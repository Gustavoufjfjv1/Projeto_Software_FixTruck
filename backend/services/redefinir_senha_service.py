import threading
import time
from collections import defaultdict, deque

from werkzeug.security import generate_password_hash

import validacoes as v
from models import Empresa
from repositories import TokenRecuperacaoRepository
from services.erros import ServiceError
from services.recuperar_senha_service import agora_utc, formatar, hash_token

MAX_FALHAS = 10
JANELA_FALHAS_SEGUNDOS = 15 * 60

# Limite simples em memória por IP (suficiente para um único processo do Flask).
_falhas = defaultdict(deque)
_trava = threading.Lock()


def _bloqueado(ip):
    agora = time.monotonic()
    with _trava:
        fila = _falhas[ip]
        while fila and agora - fila[0] > JANELA_FALHAS_SEGUNDOS:
            fila.popleft()
        return len(fila) >= MAX_FALHAS


def _registrar_falha(ip):
    with _trava:
        _falhas[ip].append(time.monotonic())


def limpar_tentativas():
    with _trava:
        _falhas.clear()


class RedefinirSenhaService:
    def executar(self, dados, ip='desconhecido'):
        if _bloqueado(ip):
            raise ServiceError('Muitas tentativas inválidas. Aguarde 15 minutos e tente novamente.', 429)
        token = dados.get('token')
        if not isinstance(token, str) or not token.strip():
            raise v.erro('Informe o código de recuperação.')
        nova_senha = v.senha(dados.get('senha'), 'A nova senha')

        empresa_id = TokenRecuperacaoRepository.consumir(hash_token(token.strip()), formatar(agora_utc()))
        empresa = Empresa.buscar_por_id(empresa_id) if empresa_id else None
        if not empresa:
            _registrar_falha(ip)
            raise ServiceError('Código inválido, expirado ou já utilizado. Solicite um novo.', 400)

        empresa.senha = generate_password_hash(nova_senha)
        empresa.atualizar()
        return {'mensagem': 'Senha redefinida com sucesso. Faça login com a nova senha.'}

import secrets

from werkzeug.security import check_password_hash, generate_password_hash

import validacoes as v
from auth import gerar_token_motorista
from models import Empresa
from repositories import MotoristaRepository, OcorrenciaRepository, VeiculoRepository
from services.erros import ServiceError

TAMANHO_MINIMO_SENHA = 6


def gerar_senha_temporaria():
    return secrets.token_urlsafe(6)[:8]


class DefinirAcessoMotoristaService:
    """A empresa define (ou gera) a credencial inicial do motorista; ele troca no primeiro acesso."""

    def executar(self, empresa_id, motorista_id, dados):
        motorista = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
        if not motorista:
            raise ServiceError('Motorista não encontrado.', 404)
        email = v.email(dados.get('email'))
        outro = MotoristaRepository.buscar_por_email(email)
        if outro and outro.id != motorista.id:
            raise ServiceError('Este e-mail já é usado por outro motorista.', 409)
        senha = dados.get('senha') or ''
        gerada = not senha
        if gerada:
            senha = gerar_senha_temporaria()
        elif len(senha) < TAMANHO_MINIMO_SENHA:
            raise v.erro(f'A senha deve ter ao menos {TAMANHO_MINIMO_SENHA} caracteres.')
        motorista.email = email
        motorista.senha = generate_password_hash(senha)
        motorista.trocar_senha = 1
        motorista.atualizar()
        resposta = {
            'mensagem': 'Acesso do motorista definido. Ele deverá trocar a senha no primeiro login.',
            'email': email,
        }
        if gerada:
            resposta['senha_temporaria'] = senha
        return resposta


class AutenticarMotoristaService:
    def executar(self, dados):
        email = (dados.get('email') or '').strip().lower()
        senha = dados.get('senha') or ''
        motorista = MotoristaRepository.buscar_por_email(email) if email else None
        if (not motorista or not motorista.tem_acesso() or not motorista.ativo
                or not check_password_hash(motorista.senha, senha)):
            raise ServiceError('E-mail ou senha incorretos.', 401)
        empresa = Empresa.buscar_por_id(motorista.empresa_id)
        return {
            'token': gerar_token_motorista(motorista),
            'motorista': motorista.to_dict_publico(),
            'empresa_nome': empresa.nome if empresa else '',
            'trocar_senha': bool(motorista.trocar_senha),
        }


class TrocarSenhaMotoristaService:
    def executar(self, motorista, dados):
        atual = dados.get('senha_atual') or ''
        nova = dados.get('nova_senha') or ''
        if not check_password_hash(motorista.senha, atual):
            raise ServiceError('Senha atual incorreta.', 401)
        if len(nova) < TAMANHO_MINIMO_SENHA:
            raise v.erro(f'A nova senha deve ter ao menos {TAMANHO_MINIMO_SENHA} caracteres.')
        if nova == atual:
            raise v.erro('A nova senha deve ser diferente da atual.')
        motorista.senha = generate_password_hash(nova)
        motorista.trocar_senha = 0
        motorista.atualizar()
        return {
            'mensagem': 'Senha alterada com sucesso.',
            'token': gerar_token_motorista(motorista),
            'motorista': motorista.to_dict_publico(),
        }


class ObterPainelMotoristaService:
    def executar(self, motorista, apenas_abertas=False):
        empresa = Empresa.buscar_por_id(motorista.empresa_id)
        return {
            'motorista': motorista.to_dict_publico(),
            'empresa_nome': empresa.nome if empresa else '',
            'veiculos': VeiculoRepository.listar_do_motorista(motorista.id, motorista.empresa_id),
            'ocorrencias': OcorrenciaRepository.listar_do_motorista(
                motorista.id, motorista.empresa_id, apenas_abertas=apenas_abertas
            ),
        }


def buscar_ocorrencia_do_motorista(motorista, ocorrencia_id):
    oc = OcorrenciaRepository.buscar_do_motorista(ocorrencia_id, motorista.id, motorista.empresa_id)
    if not oc:
        raise ServiceError('Ocorrência não encontrada.', 404)
    return oc


class ObterOcorrenciaMotoristaService:
    def executar(self, motorista, ocorrencia_id):
        oc = buscar_ocorrencia_do_motorista(motorista, ocorrencia_id)
        detalhe = OcorrenciaRepository.buscar_detalhe(oc.id, motorista.empresa_id)
        return {'ocorrencia': detalhe}

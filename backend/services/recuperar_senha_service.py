import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import email_simulado
import validacoes as v
from repositories import EmpresaRepository, TokenRecuperacaoRepository

VALIDADE_MINUTOS = 30
LIMITE_POR_JANELA = 3
JANELA_LIMITE_MINUTOS = 15

MENSAGEM_GENERICA = (
    'Se o e-mail estiver cadastrado, enviaremos um código de recuperação válido por 30 minutos. '
    'Neste projeto acadêmico o e-mail é simulado: o código aparece no terminal do backend.'
)


def agora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


def formatar(data):
    return data.strftime('%Y-%m-%d %H:%M:%S')


def hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


class RecuperarSenhaService:
    """Gera um token aleatório de uso único. A resposta é sempre a mesma (sem enumeração de e-mails)."""

    def executar(self, dados):
        email = v.email(dados.get('email'))
        empresa = EmpresaRepository.buscar_por_email(email)
        if empresa:
            self._gerar_e_enviar(empresa)
        return {'mensagem': MENSAGEM_GENERICA}

    def _gerar_e_enviar(self, empresa):
        agora = agora_utc()
        desde = formatar(agora - timedelta(minutes=JANELA_LIMITE_MINUTOS))
        if TokenRecuperacaoRepository.contar_recentes(empresa.id, desde) >= LIMITE_POR_JANELA:
            return
        token = secrets.token_urlsafe(32)
        TokenRecuperacaoRepository.invalidar_da_empresa(empresa.id, formatar(agora))
        TokenRecuperacaoRepository.criar(
            empresa.id, hash_token(token), formatar(agora + timedelta(minutes=VALIDADE_MINUTOS)), formatar(agora)
        )
        email_simulado.enviar(
            empresa.email,
            'FixTruck — recuperação de senha',
            f'Use o código abaixo em redefinir_senha.html (válido por {VALIDADE_MINUTOS} minutos, uso único):\n\n'
            f'{token}\n\nLink: redefinir_senha.html?token={token}\n'
            'Se você não pediu a recuperação, ignore esta mensagem.',
        )

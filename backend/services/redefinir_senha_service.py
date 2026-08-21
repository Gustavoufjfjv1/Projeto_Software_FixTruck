from werkzeug.security import generate_password_hash

from models import Empresa
from auth import validar_token_recuperacao
from services.erros import ServiceError


class RedefinirSenhaService:
    def executar(self, dados):
        token = dados.get('token') or ''
        nova_senha = dados.get('senha') or ''
        if len(nova_senha) < 6:
            raise ServiceError('A nova senha deve ter ao menos 6 caracteres.', 400)

        payload = validar_token_recuperacao(token)
        if not payload:
            raise ServiceError('Código inválido ou expirado. Solicite um novo.', 400)

        empresa = Empresa.buscar_por_id(payload['empresa_id'])
        if not empresa:
            raise ServiceError('Empresa não encontrada.', 404)

        empresa.senha = generate_password_hash(nova_senha)
        empresa.atualizar()
        return {'mensagem': 'Senha redefinida com sucesso. Faça login com a nova senha.'}

from werkzeug.security import check_password_hash

from models import Empresa
from auth import gerar_token
from services.erros import ServiceError


class AutenticarEmpresaService:
    def executar(self, dados):
        email = (dados.get('email') or '').strip().lower()
        senha = dados.get('senha') or ''
        empresa = Empresa.buscar_por_email(email)
        if not empresa or not check_password_hash(empresa.senha, senha):
            raise ServiceError('Email ou senha incorretos.', 401)
        return {
            'token': gerar_token(empresa.id, empresa.nome),
            'empresa': empresa.to_dict_publico(),
        }

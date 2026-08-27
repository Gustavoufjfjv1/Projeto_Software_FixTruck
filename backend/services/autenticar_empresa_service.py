from models import Empresa
from auth import gerar_token
from services.erros import ServiceError


class AutenticarEmpresaService:
    def executar(self, dados):
        email = (dados.get('email') or '').strip().lower()
        senha = dados.get('senha') or ''
        empresa = Empresa.autenticar(email, senha)
        if not empresa:
            raise ServiceError('Email ou senha incorretos.', 401)
        return {
            'token': gerar_token(empresa.id, empresa.nome),
            'empresa': empresa.to_dict_publico(),
        }

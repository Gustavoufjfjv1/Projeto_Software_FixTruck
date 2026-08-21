from models import Empresa
from services.erros import ServiceError


class CadastrarEmpresaService:
    def executar(self, dados):
        nome = (dados.get('nome') or '').strip()
        email = (dados.get('email') or '').strip().lower()
        senha = dados.get('senha') or ''
        qtd_caminhoes = dados.get('qtd_caminhoes') or 0

        if not nome or not email or not senha:
            raise ServiceError('Nome, e-mail e senha são obrigatórios.', 400)
        if Empresa.buscar_por_email(email):
            raise ServiceError('Email já cadastrado.', 409)

        empresa = Empresa(
            nome=nome, email=email, senha=senha, qtd_caminhoes=qtd_caminhoes
        )
        empresa.salvar()
        return {'mensagem': 'Cadastro realizado! Faça login.'}

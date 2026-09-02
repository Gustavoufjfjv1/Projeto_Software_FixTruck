from models import Empresa
from repositories import EmpresaRepository
from services.erros import ServiceError


class CadastrarEmpresaService:
    def executar(self, dados):
        nome = (dados.get('nome') or '').strip()
        email = (dados.get('email') or '').strip().lower()
        senha = dados.get('senha') or ''
        qtd_caminhoes = dados.get('qtd_caminhoes') or 0

        if not nome or not email or not senha:
            raise ServiceError('Nome, e-mail e senha são obrigatórios.', 400)
        if len(senha) < 6:
            raise ServiceError('A senha deve ter ao menos 6 caracteres.', 400)
        if EmpresaRepository.buscar_por_email(email):
            raise ServiceError('Email já cadastrado.', 409)

        from werkzeug.security import generate_password_hash
        empresa = Empresa(
            nome=nome, email=email, senha=generate_password_hash(senha), qtd_caminhoes=qtd_caminhoes
        )
        empresa.salvar()
        return {'mensagem': 'Cadastro realizado! Faça login.'}

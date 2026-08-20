from models import Empresa
from auth import gerar_token
from services.erros import ServiceError


class AuthService:
    @staticmethod
    def cadastrar(dados):
        nome = (dados.get('nome') or '').strip()
        email = (dados.get('email') or '').strip().lower()
        senha = dados.get('senha') or ''
        qtd_caminhoes = dados.get('qtd_caminhoes') or 0

        if not nome or not email or not senha:
            raise ServiceError('Nome, e-mail e senha são obrigatórios.', 400)

        if Empresa.buscar_por_email(email):
            raise ServiceError('Email já cadastrado.', 409)

        Empresa.cadastrar({
            'nome': nome,
            'email': email,
            'senha': senha,
            'qtd_caminhoes': qtd_caminhoes,
        })
        return {'mensagem': 'Cadastro realizado! Faça login.'}

    @staticmethod
    def login(dados):
        email = (dados.get('email') or '').strip().lower()
        senha = dados.get('senha') or ''
        empresa = Empresa.autenticar(email, senha)
        if not empresa:
            raise ServiceError('Email ou senha incorretos.', 401)

        token = gerar_token(empresa['id'], empresa['nome'])
        return {
            'token': token,
            'empresa': {
                'id': empresa['id'],
                'nome': empresa['nome'],
                'email': empresa['email'],
                'qtd_caminhoes': empresa['qtd_caminhoes'],
            },
        }

    @staticmethod
    def me(empresa_id):
        empresa = Empresa.buscar_publico(empresa_id)
        if not empresa:
            raise ServiceError('Empresa não encontrada.', 404)
        return {'empresa': empresa}

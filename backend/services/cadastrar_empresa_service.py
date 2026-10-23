from werkzeug.security import generate_password_hash

import validacoes as v
from models import Empresa
from repositories import EmpresaRepository
from services.erros import ServiceError


def validar_qtd_caminhoes(valor):
    qtd = v.numero(valor if valor not in (None, '') else 0, 'Quantidade de caminhões', minimo=0, maximo=100000)
    if qtd != int(qtd):
        raise v.erro('Quantidade de caminhões deve ser um número inteiro.')
    return int(qtd)


class CadastrarEmpresaService:
    def executar(self, dados):
        nome = v.texto(dados.get('nome'), 'Nome da empresa', max_len=120, min_len=2)
        email = v.email(dados.get('email'))
        senha = v.senha(dados.get('senha'))
        qtd_caminhoes = validar_qtd_caminhoes(dados.get('qtd_caminhoes'))
        if EmpresaRepository.buscar_por_email(email):
            raise ServiceError('Este e-mail já está cadastrado.', 409)

        empresa = Empresa(
            nome=nome, email=email, senha=generate_password_hash(senha), qtd_caminhoes=qtd_caminhoes
        )
        empresa.salvar()
        return {'mensagem': 'Cadastro realizado! Faça login.'}

from models.base import ModeloBase


class Motorista(ModeloBase):
    tabela = 'motoristas'
    campos = ('empresa_id', 'nome', 'cnh', 'telefone', 'ativo')

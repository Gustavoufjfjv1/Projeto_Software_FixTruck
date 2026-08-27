from models.base import ModeloBase


class Veiculo(ModeloBase):
    tabela = 'veiculos'
    campos = ('empresa_id', 'placa', 'modelo', 'marca', 'tipo_veiculo', 'motorista_id')

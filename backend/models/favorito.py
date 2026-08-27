from models.base import ModeloBase


class Favorito(ModeloBase):
    tabela = 'favoritos'
    campos = ('empresa_id', 'oficina_id')

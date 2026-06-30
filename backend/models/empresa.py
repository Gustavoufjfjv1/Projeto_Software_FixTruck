from . import db
from .base import ModeloBase


class Empresa(ModeloBase):
    __tablename__ = "empresas"

    razao_social = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
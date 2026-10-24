from database import db
from models.base import ModeloBase


class Motorista(ModeloBase):
    __tablename__ = 'motoristas'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    nome = db.Column(db.String, nullable=False)
    cnh = db.Column(db.String)
    telefone = db.Column(db.String)
    ativo = db.Column(db.Integer, nullable=False, default=1, server_default='1')

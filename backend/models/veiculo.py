from database import db
from models.base import ModeloBase


class Veiculo(ModeloBase):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    placa = db.Column(db.String, nullable=False)
    modelo = db.Column(db.String)
    marca = db.Column(db.String)
    tipo_veiculo = db.Column(db.String, nullable=False, default='pesado')
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'))

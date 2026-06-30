from . import db
from .base import ModeloBase


class Veiculo(ModeloBase):
    __tablename__ = "veiculos"

    placa = db.Column(db.String(7), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey("motoristas.id"), nullable=False)
    motorista = db.relationship("Motorista", back_populates="veiculos")

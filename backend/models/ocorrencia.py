from datetime import datetime
from . import db
from .base import ModeloBase


class Ocorrencia(ModeloBase):
    __tablename__ = "ocorrencias"

    data_abertura = db.Column(db.DateTime, default=datetime.now, nullable=False)
    data_fechamento = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    observacao = db.Column(db.String(200), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey("motoristas.id"), nullable=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey("veiculos.id"), nullable=True)
    motorista = db.relationship("Motorista", backref="ocorrencias")
    veiculo = db.relationship("Veiculo", backref="ocorrencias")
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    empresa = db.relationship("Empresa", backref="ocorrencias")

    def calcularDowntime(self):
        if self.data_fechamento:
            return self.data_fechamento - self.data_abertura
        return datetime.now() - self.data_abertura

    def encerrarOcorrencia(self, obs):
        self.status = "Encerrado"
        self.data_fechamento = datetime.now()
        self.observacao = obs
        db.session.commit()
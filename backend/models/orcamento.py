from . import db
from .base import ModeloBase


class Orcamento(ModeloBase):
    __tablename__ = "orcamentos"

    valor_pecas = db.Column(db.Numeric(10, 2), nullable=False)
    valor_mao_obra = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="Pendente", nullable=False)
    ocorrencia_id = db.Column(db.Integer, db.ForeignKey("ocorrencias.id"), nullable=False)
    ocorrencia = db.relationship("Ocorrencia", backref=db.backref("orcamentos", cascade="all, delete-orphan"))
    oficina_id = db.Column(db.Integer, db.ForeignKey("oficinas.id"), nullable=False)
    oficina = db.relationship("Oficina", backref="orcamentos")
    
    def calcularTotal(self):
        return self.valor_pecas + self.valor_mao_obra

    def alterarStatusAprovacao(self, novo_status):
        self.status = novo_status
        db.session.commit()

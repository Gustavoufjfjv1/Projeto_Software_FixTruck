from . import db
from .base import ModeloBase


class MensagemChat(ModeloBase):
    __tablename__ = "mensagens_chat"

    texto = db.Column(db.String(200), nullable=False)
    tipo_remetente = db.Column(db.String(20), nullable=False)
    remetente_id = db.Column(db.Integer, nullable=False)
    ocorrencia_id = db.Column(db.Integer, db.ForeignKey("ocorrencias.id"), nullable=False)
    ocorrencia = db.relationship("Ocorrencia", back_populates="mensagens")
    url_foto = db.Column(db.String(200), nullable=True)
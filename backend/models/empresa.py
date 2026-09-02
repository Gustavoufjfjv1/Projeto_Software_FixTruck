from database import db
from models.base import ModeloBase


class Empresa(ModeloBase):
    __tablename__ = 'empresas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    senha = db.Column(db.String, nullable=False)
    qtd_caminhoes = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def to_dict_publico(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'qtd_caminhoes': self.qtd_caminhoes,
        }

from . import db
from .base import ModeloBase


class Usuario(ModeloBase):
    __abstract__ = True

    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True)

    def alterarSenha(self, nova_senha_string):
        self.senha = nova_senha_string
        db.session.commit()


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
    email = db.Column(db.String, unique=True)
    senha = db.Column(db.String)
    trocar_senha = db.Column(db.Integer, nullable=False, default=0, server_default='0')

    def tem_acesso(self):
        return bool(self.email and self.senha)

    def to_dict(self, extras=None):
        data = super().to_dict(extras)
        data.pop('senha', None)
        data['tem_acesso'] = self.tem_acesso()
        return data

    def to_dict_publico(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'empresa_id': self.empresa_id,
            'trocar_senha': bool(self.trocar_senha),
        }

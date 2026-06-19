"""Modelo de Motorista"""

from app import db
from datetime import datetime


class Motorista(db.Model):
    """Representa um motorista de frota"""
    
    __tablename__ = 'motoristas'
    
    id_motorista = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False, unique=True)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('veiculos.id_veiculo'))
    numero_cnh = db.Column(db.String(15), unique=True, nullable=False, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    ocorrencias = db.relationship('Ocorrencia', backref='motorista', cascade='all, delete-orphan')
    
    def __init__(self, id_usuario, numero_cnh, id_veiculo=None):
        self.id_usuario = id_usuario
        self.numero_cnh = numero_cnh
        self.id_veiculo = id_veiculo
    
    def to_dict(self, include_usuario=False, include_veiculo=False):
        """Converte o motorista para dicionário"""
        data = {
            'id_motorista': self.id_motorista,
            'numero_cnh': self.numero_cnh,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
        if include_usuario and self.usuario:
            data['usuario'] = self.usuario.to_dict(include_tipo=False)
        if include_veiculo and self.veiculo:
            data['veiculo'] = self.veiculo.to_dict()
        return data
    
    def __repr__(self):
        return f'<Motorista {self.numero_cnh}>'

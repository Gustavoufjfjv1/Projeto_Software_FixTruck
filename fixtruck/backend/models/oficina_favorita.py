"""Modelo de Oficina Favorita"""

from app import db
from datetime import datetime


class OficinaFavorita(db.Model):
    """Representa uma oficina favoritada por um gestor"""
    
    __tablename__ = 'oficinas_favoritas'
    
    id_favorita = db.Column(db.Integer, primary_key=True)
    id_gestor = db.Column(db.Integer, db.ForeignKey('gestores.id_gestor'), nullable=False)
    id_oficina = db.Column(db.Integer, db.ForeignKey('oficinas.id_oficina'), nullable=False)
    data_adicionada = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('id_gestor', 'id_oficina', name='unique_favorita'),)
    
    def __init__(self, id_gestor, id_oficina):
        self.id_gestor = id_gestor
        self.id_oficina = id_oficina
    
    def to_dict(self):
        """Converte a oficina favorita para dicionário"""
        return {
            'id_favorita': self.id_favorita,
            'id_gestor': self.id_gestor,
            'id_oficina': self.id_oficina,
            'data_adicionada': self.data_adicionada.isoformat() if self.data_adicionada else None
        }
    
    def __repr__(self):
        return f'<OficinaFavorita {self.id_gestor}-{self.id_oficina}>'

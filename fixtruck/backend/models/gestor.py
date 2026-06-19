"""Modelo de Gestor"""

from app import db


class Gestor(db.Model):
    """Representa um gestor de frota"""
    
    __tablename__ = 'gestores'
    
    id_gestor = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False, unique=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresas_transporte.id_empresa'), nullable=False, index=True)
    telefone_corporativo = db.Column(db.String(20))
    
    # Relacionamentos
    oficinas_favoritas = db.relationship('OficinaFavorita', backref='gestor', cascade='all, delete-orphan')
    
    def __init__(self, id_usuario, id_empresa, telefone_corporativo=None):
        self.id_usuario = id_usuario
        self.id_empresa = id_empresa
        self.telefone_corporativo = telefone_corporativo
    
    def to_dict(self, include_usuario=False):
        """Converte o gestor para dicionário"""
        data = {
            'id_gestor': self.id_gestor,
            'telefone_corporativo': self.telefone_corporativo,
            'empresa': self.empresa.to_dict() if self.empresa else None
        }
        if include_usuario and self.usuario:
            data['usuario'] = self.usuario.to_dict(include_tipo=False)
        return data
    
    def __repr__(self):
        return f'<Gestor {self.id_gestor}>'

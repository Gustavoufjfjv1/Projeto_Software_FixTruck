"""Modelo de Empresa de Transporte"""

from app import db
from datetime import datetime


class EmpresaTransporte(db.Model):
    """Representa uma empresa de transporte rodoviário"""
    
    __tablename__ = 'empresas_transporte'
    
    id_empresa = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    gestores = db.relationship('Gestor', backref='empresa', cascade='all, delete-orphan')
    veiculos = db.relationship('Veiculo', backref='empresa', cascade='all, delete-orphan')
    
    def __init__(self, razao_social, cnpj):
        self.razao_social = razao_social
        self.cnpj = cnpj
    
    def to_dict(self):
        """Converte a empresa para dicionário"""
        return {
            'id_empresa': self.id_empresa,
            'razao_social': self.razao_social,
            'cnpj': self.cnpj,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
    
    def __repr__(self):
        return f'<EmpresaTransporte {self.razao_social}>'

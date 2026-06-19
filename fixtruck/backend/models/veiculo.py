"""Modelo de Veículo"""

from app import db
from datetime import datetime


class Veiculo(db.Model):
    """Representa um veículo da frota"""
    
    __tablename__ = 'veiculos'
    
    id_veiculo = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False, index=True)
    modelo = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    tipo_veiculo = db.Column(db.String(50), nullable=False)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresas_transporte.id_empresa'), nullable=False, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    motoristas = db.relationship('Motorista', backref='veiculo')
    ocorrencias = db.relationship('Ocorrencia', backref='veiculo', cascade='all, delete-orphan')
    
    def __init__(self, placa, modelo, marca, tipo_veiculo, id_empresa):
        self.placa = placa
        self.modelo = modelo
        self.marca = marca
        self.tipo_veiculo = tipo_veiculo
        self.id_empresa = id_empresa
    
    def to_dict(self, include_empresa=False):
        """Converte o veículo para dicionário"""
        data = {
            'id_veiculo': self.id_veiculo,
            'placa': self.placa,
            'modelo': self.modelo,
            'marca': self.marca,
            'tipo_veiculo': self.tipo_veiculo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ativo': self.ativo
        }
        if include_empresa and self.empresa:
            data['empresa'] = self.empresa.to_dict()
        return data
    
    def obter_historico_ocorrencias(self, limite=None):
        """Retorna o histórico de ocorrências do veículo"""
        query = self.ocorrencias.order_by(db.desc(self.ocorrencias.any().data_abertura))
        if limite:
            return query.limit(limite).all()
        return query.all()
    
    def __repr__(self):
        return f'<Veiculo {self.placa}>'

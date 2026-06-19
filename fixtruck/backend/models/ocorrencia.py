"""Modelo de Ocorrência"""

from app import db
from datetime import datetime


class Ocorrencia(db.Model):
    """Representa uma ocorrência mecânica registrada por um motorista"""
    
    __tablename__ = 'ocorrencias'
    
    id_ocorrencia = db.Column(db.Integer, primary_key=True)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('veiculos.id_veiculo'), nullable=False, index=True)
    id_oficina = db.Column(db.Integer, db.ForeignKey('oficinas.id_oficina'))
    id_motorista = db.Column(db.Integer, db.ForeignKey('motoristas.id_motorista'))
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_fechamento = db.Column(db.DateTime)
    status = db.Column(
        db.Enum('aberta', 'em_atendimento', 'resolvida', 'cancelada'),
        default='aberta',
        nullable=False,
        index=True
    )
    tipo_problema = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    motivo_resolucao = db.Column(db.Text)
    observacao = db.Column(db.Text)
    
    # Relacionamentos
    orcamentos = db.relationship('Orcamento', backref='ocorrencia', cascade='all, delete-orphan')
    mensagens = db.relationship('MensagemChat', backref='ocorrencia', cascade='all, delete-orphan')
    
    def __init__(self, id_veiculo, tipo_problema, latitude, longitude, **kwargs):
        self.id_veiculo = id_veiculo
        self.tipo_problema = tipo_problema
        self.latitude = latitude
        self.longitude = longitude
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self, include_detalhes=False):
        """Converte a ocorrência para dicionário"""
        data = {
            'id_ocorrencia': self.id_ocorrencia,
            'tipo_problema': self.tipo_problema,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_fechamento': self.data_fechamento.isoformat() if self.data_fechamento else None
        }
        
        if include_detalhes:
            data['id_veiculo'] = self.id_veiculo
            data['id_oficina'] = self.id_oficina
            data['id_motorista'] = self.id_motorista
            data['motivo_resolucao'] = self.motivo_resolucao
            data['observacao'] = self.observacao
            data['downtime'] = self.calcular_downtime()
            data['veiculo'] = self.veiculo.to_dict() if self.veiculo else None
            data['oficina'] = self.oficina.to_dict() if self.oficina else None
        
        return data
    
    def calcular_downtime(self):
        """Calcula o tempo de inatividade do veículo em horas"""
        if self.data_fechamento:
            delta = self.data_fechamento - self.data_abertura
            return delta.total_seconds() / 3600
        else:
            delta = datetime.utcnow() - self.data_abertura
            return delta.total_seconds() / 3600
    
    def encerrar(self, motivo_resolucao, observacao=''):
        """Encerra a ocorrência"""
        self.data_fechamento = datetime.utcnow()
        self.status = 'resolvida'
        self.motivo_resolucao = motivo_resolucao
        self.observacao = observacao
    
    def __repr__(self):
        return f'<Ocorrencia {self.id_ocorrencia}>'

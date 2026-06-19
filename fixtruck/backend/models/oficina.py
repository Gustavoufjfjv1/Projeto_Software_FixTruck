"""Modelo de Oficina"""

from app import db
from datetime import datetime


class Oficina(db.Model):
    """Representa uma oficina mecânica (importada do shapefile)"""
    
    __tablename__ = 'oficinas'
    
    id_oficina = db.Column(db.Integer, primary_key=True)
    nome_fantasia = db.Column(db.String(255), nullable=False, index=True)
    cnpj = db.Column(db.String(18), unique=True)
    especialidades = db.Column(db.String(255))
    horario_funcionamento = db.Column(db.String(255))
    possui_guincho = db.Column(db.Boolean, default=False)
    atende_pesado = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    endereco = db.Column(db.String(500))
    bairro = db.Column(db.String(100))
    numero_imovel = db.Column(db.String(20))
    cnae_principal = db.Column(db.String(10))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    ocorrencias = db.relationship('Ocorrencia', backref='oficina')
    orcamentos = db.relationship('Orcamento', backref='oficina', cascade='all, delete-orphan')
    favoritas = db.relationship('OficinaFavorita', backref='oficina', cascade='all, delete-orphan')
    
    def __init__(self, nome_fantasia, latitude, longitude, **kwargs):
        self.nome_fantasia = nome_fantasia
        self.latitude = latitude
        self.longitude = longitude
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self, include_endereco_completo=False):
        """Converte a oficina para dicionário"""
        data = {
            'id_oficina': self.id_oficina,
            'nome_fantasia': self.nome_fantasia,
            'cnpj': self.cnpj,
            'especialidades': self.especialidades,
            'horario_funcionamento': self.horario_funcionamento,
            'possui_guincho': self.possui_guincho,
            'atende_pesado': self.atende_pesado,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'ativo': self.ativo
        }
        
        if include_endereco_completo:
            data['endereco'] = self.endereco
            data['bairro'] = self.bairro
            data['numero_imovel'] = self.numero_imovel
            data['cnae_principal'] = self.cnae_principal
        
        return data
    
    def esta_aberta(self):
        """Verifica se a oficina está aberta no horário atual"""
        # TODO: Implementar lógica de verificação de horário
        return True
    
    def __repr__(self):
        return f'<Oficina {self.nome_fantasia}>'

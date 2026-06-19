"""Modelo de Usuário"""

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model):
    """Representa um usuário do sistema (Gestor ou Motorista)"""
    
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.Enum('gestor', 'motorista'), nullable=False, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    gestor = db.relationship('Gestor', backref='usuario', uselist=False, cascade='all, delete-orphan')
    motorista = db.relationship('Motorista', backref='usuario', uselist=False, cascade='all, delete-orphan')
    mensagens = db.relationship('MensagemChat', backref='autor', cascade='all, delete-orphan')
    
    def __init__(self, nome, email, tipo_usuario, senha=None):
        self.nome = nome
        self.email = email
        self.tipo_usuario = tipo_usuario
        if senha:
            self.set_password(senha)
    
    def set_password(self, senha):
        """Criptografa e armazena a senha"""
        self.senha = generate_password_hash(senha)
    
    def check_password(self, senha):
        """Verifica se a senha fornecida está correta"""
        return check_password_hash(self.senha, senha)
    
    def to_dict(self, include_tipo=True):
        """Converte o usuário para dicionário"""
        data = {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'email': self.email,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ativo': self.ativo
        }
        if include_tipo:
            data['tipo_usuario'] = self.tipo_usuario
        return data
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

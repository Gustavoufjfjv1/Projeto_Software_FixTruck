"""Modelo de Mensagem de Chat"""

from app import db
from datetime import datetime


class MensagemChat(db.Model):
    """Representa uma mensagem de chat em uma ocorrência"""
    
    __tablename__ = 'mensagens_chat'
    
    id_mensagem = db.Column(db.Integer, primary_key=True)
    id_ocorrencia = db.Column(db.Integer, db.ForeignKey('ocorrencias.id_ocorrencia'), nullable=False, index=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    url_foto_evidencia = db.Column(db.String(500))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __init__(self, id_ocorrencia, id_usuario, texto, **kwargs):
        self.id_ocorrencia = id_ocorrencia
        self.id_usuario = id_usuario
        self.texto = texto
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self, include_autor=True):
        """Converte a mensagem para dicionário"""
        data = {
            'id_mensagem': self.id_mensagem,
            'texto': self.texto,
            'url_foto_evidencia': self.url_foto_evidencia,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None
        }
        
        if include_autor and self.autor:
            data['autor'] = {
                'id_usuario': self.autor.id_usuario,
                'nome': self.autor.nome,
                'tipo_usuario': self.autor.tipo_usuario
            }
        
        return data
    
    def __repr__(self):
        return f'<MensagemChat {self.id_mensagem}>'

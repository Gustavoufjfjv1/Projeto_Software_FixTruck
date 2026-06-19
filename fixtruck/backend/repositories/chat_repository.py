"""Repositório de Chat"""

from models.mensagem_chat import MensagemChat
from repositories.base_repository import BaseRepository


class ChatRepository(BaseRepository):
    """Repositório para operações com Mensagens de Chat"""
    
    def __init__(self):
        super().__init__(MensagemChat)
    
    def obter_por_ocorrencia(self, id_ocorrencia, limite=None):
        """Obtém mensagens de uma ocorrência"""
        query = MensagemChat.query.filter_by(id_ocorrencia=id_ocorrencia).order_by(
            MensagemChat.data_hora.asc()
        )
        
        if limite:
            query = query.limit(limite)
        
        return query.all()
    
    def contar_por_ocorrencia(self, id_ocorrencia):
        """Conta quantas mensagens tem em uma ocorrência"""
        return MensagemChat.query.filter_by(id_ocorrencia=id_ocorrencia).count()
    
    def obter_ultimas_por_ocorrencia(self, id_ocorrencia, quantidade=10):
        """Obtém as últimas N mensagens de uma ocorrência"""
        return MensagemChat.query.filter_by(id_ocorrencia=id_ocorrencia).order_by(
            MensagemChat.data_hora.desc()
        ).limit(quantidade).all()
    
    def listar_com_foto(self, id_ocorrencia):
        """Lista mensagens com foto de evidência"""
        return MensagemChat.query.filter(
            MensagemChat.id_ocorrencia == id_ocorrencia,
            MensagemChat.url_foto_evidencia.isnot(None)
        ).all()

"""Serviço de Chat"""

from models.mensagem_chat import MensagemChat
from repositories.chat_repository import ChatRepository
from repositories.ocorrencia_repository import OcorrenciaRepository


class ChatService:
    """Gerencia operações de chat em ocorrências"""
    
    def __init__(self):
        self.chat_repo = ChatRepository()
        self.ocorrencia_repo = OcorrenciaRepository()
    
    def enviar_mensagem(self, id_ocorrencia, id_usuario, texto, url_foto_evidencia=None):
        """Envia uma mensagem em uma ocorrência"""
        
        # Validar ocorrência existe
        if not self.ocorrencia_repo.obter_por_id(id_ocorrencia):
            raise ValueError('Ocorrência não encontrada')
        
        mensagem = MensagemChat(
            id_ocorrencia=id_ocorrencia,
            id_usuario=id_usuario,
            texto=texto,
            url_foto_evidencia=url_foto_evidencia
        )
        
        mensagem_criada = self.chat_repo.criar(mensagem)
        
        return mensagem_criada.to_dict(include_autor=True)
    
    def obter_mensagens(self, id_ocorrencia):
        """Obtém todas as mensagens de uma ocorrência"""
        
        # Validar ocorrência existe
        if not self.ocorrencia_repo.obter_por_id(id_ocorrencia):
            return []
        
        mensagens = self.chat_repo.obter_por_ocorrencia(id_ocorrencia)
        
        resultado = []
        for mensagem in mensagens:
            resultado.append(mensagem.to_dict(include_autor=True))
        
        return resultado
    
    def obter_historico(self, id_ocorrencia, limite=None):
        """Obtém o histórico de chat de uma ocorrência"""
        
        mensagens = self.chat_repo.obter_por_ocorrencia(id_ocorrencia, limite=limite)
        
        resultado = []
        for mensagem in mensagens:
            resultado.append(mensagem.to_dict(include_autor=True))
        
        return resultado

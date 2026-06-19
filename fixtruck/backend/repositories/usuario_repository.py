"""Repositório de Usuários"""

from models.usuario import Usuario
from repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    """Repositório para operações com Usuários"""
    
    def __init__(self):
        super().__init__(Usuario)
    
    def obter_por_email(self, email):
        """Obtém um usuário pelo email"""
        return Usuario.query.filter_by(email=email).first()
    
    def listar_todos(self, tipo_usuario=None):
        """Lista usuários com filtro opcional por tipo"""
        query = Usuario.query
        
        if tipo_usuario:
            query = query.filter_by(tipo_usuario=tipo_usuario)
        
        return query.all()
    
    def obter_ativos(self, tipo_usuario=None):
        """Obtém usuários ativos"""
        query = Usuario.query.filter_by(ativo=True)
        
        if tipo_usuario:
            query = query.filter_by(tipo_usuario=tipo_usuario)
        
        return query.all()

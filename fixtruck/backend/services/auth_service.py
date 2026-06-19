"""Serviço de Autenticação"""

from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository
import secrets
from datetime import datetime, timedelta


class AuthService:
    """Gerencia autenticação e autorização de usuários"""
    
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
    
    def registrar_usuario(self, nome, email, senha, tipo_usuario, **kwargs):
        """Registra um novo usuário"""
        
        # Validar tipo de usuário
        if tipo_usuario not in ['gestor', 'motorista']:
            raise ValueError('Tipo de usuário inválido. Deve ser "gestor" ou "motorista"')
        
        # Verificar se usuário já existe
        if self.usuario_repo.obter_por_email(email):
            raise ValueError('Email já registrado')
        
        # Criar novo usuário
        usuario = Usuario(
            nome=nome,
            email=email,
            tipo_usuario=tipo_usuario,
            senha=senha
        )
        
        # Salvar no banco
        usuario_salvo = self.usuario_repo.criar(usuario)
        
        return usuario_salvo.to_dict()
    
    def autenticar(self, email, senha):
        """Autentica um usuário com email e senha"""
        
        usuario = self.usuario_repo.obter_por_email(email)
        
        if not usuario or not usuario.check_password(senha):
            return None
        
        # Gerar token simples (em produção, usar JWT)
        token = secrets.token_urlsafe(32)
        
        return {
            'usuario': usuario.to_dict(),
            'token': token
        }
    
    def alterar_senha(self, id_usuario, senha_atual, senha_nova):
        """Altera a senha de um usuário"""
        
        usuario = self.usuario_repo.obter_por_id(id_usuario)
        
        if not usuario:
            return False
        
        # Verificar senha atual
        if not usuario.check_password(senha_atual):
            return False
        
        # Definir nova senha
        usuario.set_password(senha_nova)
        self.usuario_repo.atualizar(usuario)
        
        return True
    
    def validar_token(self, token):
        """Valida um token (implementação simplificada)"""
        # TODO: Implementar validação real com JWT
        return True

"""Serviço de Usuários"""

from repositories.usuario_repository import UsuarioRepository


class UsuarioService:
    """Gerencia operações relacionadas a usuários"""
    
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
    
    def obter_usuario(self, id_usuario):
        """Obtém um usuário específico"""
        usuario = self.usuario_repo.obter_por_id(id_usuario)
        
        if usuario:
            dados = usuario.to_dict()
            
            # Adicionar informações de tipo específico
            if usuario.tipo_usuario == 'gestor' and usuario.gestor:
                dados['gestor'] = usuario.gestor.to_dict(include_usuario=True)
            elif usuario.tipo_usuario == 'motorista' and usuario.motorista:
                dados['motorista'] = usuario.motorista.to_dict(include_usuario=True)
            
            return dados
        
        return None
    
    def listar_usuarios(self, tipo_usuario=None):
        """Lista usuários com filtros opcionais"""
        usuarios = self.usuario_repo.listar_todos(tipo_usuario=tipo_usuario)
        
        resultado = []
        for usuario in usuarios:
            resultado.append(usuario.to_dict())
        
        return resultado
    
    def atualizar_usuario(self, id_usuario, dados):
        """Atualiza informações de um usuário"""
        usuario = self.usuario_repo.obter_por_id(id_usuario)
        
        if not usuario:
            return None
        
        # Atualizar campos permitidos
        campos_permitidos = ['nome', 'email', 'ativo']
        
        for campo in campos_permitidos:
            if campo in dados:
                setattr(usuario, campo, dados[campo])
        
        self.usuario_repo.atualizar(usuario)
        
        return usuario.to_dict()
    
    def deletar_usuario(self, id_usuario):
        """Deleta um usuário"""
        return self.usuario_repo.deletar(id_usuario)

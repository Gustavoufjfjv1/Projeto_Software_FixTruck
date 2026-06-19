"""Repositório Base"""

from app import db


class BaseRepository:
    """Classe base para todos os repositórios"""
    
    def __init__(self, model):
        self.model = model
    
    def criar(self, entidade):
        """Cria uma nova entidade"""
        db.session.add(entidade)
        db.session.commit()
        return entidade
    
    def obter_por_id(self, id):
        """Obtém uma entidade por ID"""
        return self.model.query.get(id)
    
    def atualizar(self, entidade):
        """Atualiza uma entidade"""
        db.session.merge(entidade)
        db.session.commit()
        return entidade
    
    def deletar(self, id):
        """Deleta uma entidade por ID"""
        entidade = self.obter_por_id(id)
        
        if entidade:
            db.session.delete(entidade)
            db.session.commit()
            return True
        
        return False
    
    def listar_todos(self):
        """Lista todas as entidades"""
        return self.model.query.all()

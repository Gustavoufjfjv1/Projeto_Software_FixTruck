"""Repositório de Oficinas"""

from models.oficina import Oficina
from repositories.base_repository import BaseRepository


class OficinaRepository(BaseRepository):
    """Repositório para operações com Oficinas"""
    
    def __init__(self):
        super().__init__(Oficina)
    
    def obter_por_cnpj(self, cnpj):
        """Obtém uma oficina pelo CNPJ"""
        return Oficina.query.filter_by(cnpj=cnpj).first()
    
    def listar_todos(self, ativo=True):
        """Lista oficinas com filtro opcional"""
        query = Oficina.query
        
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        return query.all()
    
    def listar_ativas(self):
        """Lista apenas oficinas ativas"""
        return Oficina.query.filter_by(ativo=True).all()
    
    def buscar_por_nome(self, nome):
        """Busca oficinas pelo nome (parcial)"""
        return Oficina.query.filter(
            Oficina.nome_fantasia.ilike(f'%{nome}%')
        ).all()
    
    def listar_por_especialidade(self, especialidade):
        """Lista oficinas por especialidade"""
        return Oficina.query.filter(
            Oficina.especialidades.ilike(f'%{especialidade}%')
        ).all()
    
    def listar_com_guincho(self):
        """Lista oficinas que possuem guincho"""
        return Oficina.query.filter_by(possui_guincho=True, ativo=True).all()
    
    def listar_atende_pesado(self):
        """Lista oficinas que atendem veículos pesados"""
        return Oficina.query.filter_by(atende_pesado=True, ativo=True).all()

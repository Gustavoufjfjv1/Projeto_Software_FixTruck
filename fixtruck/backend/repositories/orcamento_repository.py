"""Repositório de Orçamentos"""

from models.orcamento import Orcamento
from repositories.base_repository import BaseRepository


class OrcamentoRepository(BaseRepository):
    """Repositório para operações com Orçamentos"""
    
    def __init__(self):
        super().__init__(Orcamento)
    
    def listar_com_filtros(self, id_ocorrencia=None, status=None):
        """Lista orçamentos com múltiplos filtros"""
        query = Orcamento.query
        
        if id_ocorrencia:
            query = query.filter_by(id_ocorrencia=id_ocorrencia)
        
        if status:
            query = query.filter_by(status_aprovacao=status)
        
        return query.order_by(Orcamento.data_criacao.desc()).all()
    
    def listar_por_ocorrencia(self, id_ocorrencia):
        """Lista todos os orçamentos de uma ocorrência"""
        return Orcamento.query.filter_by(id_ocorrencia=id_ocorrencia).all()
    
    def listar_pendentes(self):
        """Lista orçamentos com status pendente"""
        return Orcamento.query.filter_by(status_aprovacao='pendente').all()
    
    def listar_por_oficina(self, id_oficina):
        """Lista todos os orçamentos enviados por uma oficina"""
        return Orcamento.query.filter_by(id_oficina=id_oficina).all()

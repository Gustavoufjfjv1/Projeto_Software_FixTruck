"""Repositório de Veículos"""

from models.veiculo import Veiculo
from repositories.base_repository import BaseRepository


class VeiculoRepository(BaseRepository):
    """Repositório para operações com Veículos"""
    
    def __init__(self):
        super().__init__(Veiculo)
    
    def obter_por_placa(self, placa):
        """Obtém um veículo pela placa"""
        return Veiculo.query.filter_by(placa=placa).first()
    
    def listar_todos(self, id_empresa=None, ativo=True):
        """Lista veículos com filtros opcionais"""
        query = Veiculo.query
        
        if id_empresa:
            query = query.filter_by(id_empresa=id_empresa)
        
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        return query.all()
    
    def listar_por_empresa(self, id_empresa):
        """Lista todos os veículos de uma empresa"""
        return Veiculo.query.filter_by(id_empresa=id_empresa, ativo=True).all()

"""Repositório de Ocorrências"""

from models.ocorrencia import Ocorrencia
from repositories.base_repository import BaseRepository
from datetime import datetime, timedelta


class OcorrenciaRepository(BaseRepository):
    """Repositório para operações com Ocorrências"""
    
    def __init__(self):
        super().__init__(Ocorrencia)
    
    def listar_com_filtros(self, status=None, id_veiculo=None, id_oficina=None):
        """Lista ocorrências com múltiplos filtros"""
        query = Ocorrencia.query
        
        if status:
            query = query.filter_by(status=status)
        
        if id_veiculo:
            query = query.filter_by(id_veiculo=id_veiculo)
        
        if id_oficina:
            query = query.filter_by(id_oficina=id_oficina)
        
        return query.order_by(Ocorrencia.data_abertura.desc()).all()
    
    def listar_abertas(self):
        """Lista todas as ocorrências abertas"""
        return Ocorrencia.query.filter_by(status='aberta').all()
    
    def listar_em_atendimento(self):
        """Lista todas as ocorrências em atendimento"""
        return Ocorrencia.query.filter_by(status='em_atendimento').all()
    
    def listar_por_veiculo(self, id_veiculo):
        """Lista todas as ocorrências de um veículo"""
        return Ocorrencia.query.filter_by(id_veiculo=id_veiculo).order_by(
            Ocorrencia.data_abertura.desc()
        ).all()
    
    def listar_por_periodo(self, data_inicio, data_fim):
        """Lista ocorrências em um período específico"""
        return Ocorrencia.query.filter(
            Ocorrencia.data_abertura >= data_inicio,
            Ocorrencia.data_abertura <= data_fim
        ).all()
    
    def listar_recentes(self, dias=7):
        """Lista ocorrências dos últimos N dias"""
        data_limite = datetime.utcnow() - timedelta(days=dias)
        return Ocorrencia.query.filter(
            Ocorrencia.data_abertura >= data_limite
        ).order_by(Ocorrencia.data_abertura.desc()).all()

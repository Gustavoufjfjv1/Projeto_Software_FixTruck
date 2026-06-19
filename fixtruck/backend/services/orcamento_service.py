"""Serviço de Orçamentos"""

from models.orcamento import Orcamento
from repositories.orcamento_repository import OrcamentoRepository
from repositories.ocorrencia_repository import OcorrenciaRepository


class OrcamentoService:
    """Gerencia operações relacionadas a orçamentos"""
    
    def __init__(self):
        self.orcamento_repo = OrcamentoRepository()
        self.ocorrencia_repo = OcorrenciaRepository()
    
    def criar_orcamento(self, dados):
        """Cria um novo orçamento"""
        
        # Validar ocorrência existe
        if not self.ocorrencia_repo.obter_por_id(dados['id_ocorrencia']):
            raise ValueError('Ocorrência não encontrada')
        
        orcamento = Orcamento(
            id_ocorrencia=dados['id_ocorrencia'],
            id_oficina=dados['id_oficina'],
            valor_pecas=dados['valor_pecas'],
            valor_mao_obra=dados['valor_mao_obra'],
            observacoes=dados.get('observacoes', '')
        )
        
        orcamento_criado = self.orcamento_repo.criar(orcamento)
        
        return orcamento_criado.to_dict(include_detalhes=True)
    
    def obter_orcamento(self, id_orcamento):
        """Obtém detalhes de um orçamento"""
        orcamento = self.orcamento_repo.obter_por_id(id_orcamento)
        
        if orcamento:
            return orcamento.to_dict(include_detalhes=True)
        
        return None
    
    def listar_orcamentos(self, id_ocorrencia=None, status=None):
        """Lista orçamentos com filtros opcionais"""
        orcamentos = self.orcamento_repo.listar_com_filtros(
            id_ocorrencia=id_ocorrencia,
            status=status
        )
        
        resultado = []
        for orcamento in orcamentos:
            resultado.append(orcamento.to_dict())
        
        return resultado
    
    def aprovar_orcamento(self, id_orcamento):
        """Aprova um orçamento"""
        orcamento = self.orcamento_repo.obter_por_id(id_orcamento)
        
        if not orcamento:
            return None
        
        orcamento.alterar_status_aprovacao('aprovado')
        self.orcamento_repo.atualizar(orcamento)
        
        return orcamento.to_dict(include_detalhes=True)
    
    def rejeitar_orcamento(self, id_orcamento, observacoes=''):
        """Rejeita um orçamento"""
        orcamento = self.orcamento_repo.obter_por_id(id_orcamento)
        
        if not orcamento:
            return None
        
        orcamento.alterar_status_aprovacao('rejeitado')
        if observacoes:
            orcamento.observacoes = observacoes
        
        self.orcamento_repo.atualizar(orcamento)
        
        return orcamento.to_dict(include_detalhes=True)

"""Serviço de Ocorrências"""

from models.ocorrencia import Ocorrencia
from repositories.ocorrencia_repository import OcorrenciaRepository
from repositories.veiculo_repository import VeiculoRepository
from repositories.oficina_repository import OficinaRepository


class OcorrenciaService:
    """Gerencia operações relacionadas a ocorrências"""
    
    def __init__(self):
        self.ocorrencia_repo = OcorrenciaRepository()
        self.veiculo_repo = VeiculoRepository()
        self.oficina_repo = OficinaRepository()
    
    def criar_ocorrencia(self, dados):
        """Cria uma nova ocorrência"""
        
        # Validar veículo existe
        if not self.veiculo_repo.obter_por_id(dados['id_veiculo']):
            raise ValueError('Veículo não encontrado')
        
        ocorrencia = Ocorrencia(
            id_veiculo=dados['id_veiculo'],
            tipo_problema=dados['tipo_problema'],
            latitude=dados['latitude'],
            longitude=dados['longitude'],
            id_oficina=dados.get('id_oficina'),
            id_motorista=dados.get('id_motorista'),
            observacao=dados.get('observacao', '')
        )
        
        ocorrencia_criada = self.ocorrencia_repo.criar(ocorrencia)
        
        return ocorrencia_criada.to_dict(include_detalhes=True)
    
    def obter_ocorrencia(self, id_ocorrencia):
        """Obtém detalhes de uma ocorrência"""
        ocorrencia = self.ocorrencia_repo.obter_por_id(id_ocorrencia)
        
        if ocorrencia:
            return ocorrencia.to_dict(include_detalhes=True)
        
        return None
    
    def listar_ocorrencias(self, status=None, id_veiculo=None, id_oficina=None):
        """Lista ocorrências com filtros opcionais"""
        ocorrencias = self.ocorrencia_repo.listar_com_filtros(
            status=status,
            id_veiculo=id_veiculo,
            id_oficina=id_oficina
        )
        
        resultado = []
        for ocorrencia in ocorrencias:
            resultado.append(ocorrencia.to_dict())
        
        return resultado
    
    def vincular_oficina(self, id_ocorrencia, id_oficina):
        """Vincula uma oficina a uma ocorrência"""
        ocorrencia = self.ocorrencia_repo.obter_por_id(id_ocorrencia)
        
        if not ocorrencia:
            return None
        
        # Validar oficina existe
        if not self.oficina_repo.obter_por_id(id_oficina):
            return None
        
        ocorrencia.id_oficina = id_oficina
        ocorrencia.status = 'em_atendimento'
        
        self.ocorrencia_repo.atualizar(ocorrencia)
        
        return ocorrencia.to_dict(include_detalhes=True)
    
    def encerrar_ocorrencia(self, id_ocorrencia, motivo_resolucao, observacao=''):
        """Encerra uma ocorrência"""
        ocorrencia = self.ocorrencia_repo.obter_por_id(id_ocorrencia)
        
        if not ocorrencia:
            return None
        
        ocorrencia.encerrar(motivo_resolucao, observacao)
        self.ocorrencia_repo.atualizar(ocorrencia)
        
        return ocorrencia.to_dict(include_detalhes=True)
    
    def obter_downtime(self, id_ocorrencia):
        """Obtém o tempo de inatividade de uma ocorrência"""
        ocorrencia = self.ocorrencia_repo.obter_por_id(id_ocorrencia)
        
        if ocorrencia:
            return ocorrencia.calcular_downtime()
        
        return None

"""Serviço de Veículos"""

from models.veiculo import Veiculo
from repositories.veiculo_repository import VeiculoRepository


class VeiculoService:
    """Gerencia operações relacionadas a veículos"""
    
    def __init__(self):
        self.veiculo_repo = VeiculoRepository()
    
    def criar_veiculo(self, dados):
        """Cria um novo veículo"""
        
        # Validar placa única
        if self.veiculo_repo.obter_por_placa(dados['placa']):
            raise ValueError('Placa já registrada')
        
        veiculo = Veiculo(
            placa=dados['placa'],
            modelo=dados['modelo'],
            marca=dados['marca'],
            tipo_veiculo=dados['tipo_veiculo'],
            id_empresa=dados['id_empresa']
        )
        
        veiculo_criado = self.veiculo_repo.criar(veiculo)
        
        return veiculo_criado.to_dict(include_empresa=True)
    
    def obter_veiculo(self, id_veiculo):
        """Obtém um veículo específico"""
        veiculo = self.veiculo_repo.obter_por_id(id_veiculo)
        
        if veiculo:
            return veiculo.to_dict(include_empresa=True)
        
        return None
    
    def listar_veiculos(self, id_empresa=None):
        """Lista veículos com filtros opcionais"""
        veiculos = self.veiculo_repo.listar_todos(id_empresa=id_empresa, ativo=True)
        
        resultado = []
        for veiculo in veiculos:
            resultado.append(veiculo.to_dict(include_empresa=True))
        
        return resultado
    
    def obter_historico_ocorrencias(self, id_veiculo, limite=None):
        """Obtém histórico de ocorrências de um veículo"""
        veiculo = self.veiculo_repo.obter_por_id(id_veiculo)
        
        if not veiculo:
            return None
        
        ocorrencias = veiculo.obter_historico_ocorrencias(limite)
        
        resultado = []
        for ocorrencia in ocorrencias:
            resultado.append(ocorrencia.to_dict())
        
        return resultado
    
    def atualizar_veiculo(self, id_veiculo, dados):
        """Atualiza informações de um veículo"""
        veiculo = self.veiculo_repo.obter_por_id(id_veiculo)
        
        if not veiculo:
            return None
        
        campos_permitidos = ['modelo', 'marca', 'tipo_veiculo', 'ativo']
        
        for campo in campos_permitidos:
            if campo in dados:
                setattr(veiculo, campo, dados[campo])
        
        self.veiculo_repo.atualizar(veiculo)
        
        return veiculo.to_dict(include_empresa=True)

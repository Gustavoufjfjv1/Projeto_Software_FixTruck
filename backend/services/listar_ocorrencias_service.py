import validacoes as v
from constantes import TIPOS_PROBLEMA
from repositories import OcorrenciaRepository, VeiculoRepository

PERIODOS = ['7d', '30d', '90d']
STATUS_FILTRO = ['abertas', 'aberta', 'em_atendimento', 'resolvido']


def validar_filtros(filtros):
    return {
        'periodo': v.opcao(filtros.get('periodo'), PERIODOS, 'Período', obrigatorio=False) or '',
        'tipo': v.opcao(filtros.get('tipo'), TIPOS_PROBLEMA, 'Tipo de problema', obrigatorio=False) or '',
        'veiculo': v.identificador(filtros.get('veiculo'), 'Veículo') or '',
        'status': v.opcao(filtros.get('status'), STATUS_FILTRO, 'Status', obrigatorio=False) or '',
    }


class ListarOcorrenciasService:
    def executar(self, empresa_id, filtros):
        return {
            'ocorrencias': OcorrenciaRepository.listar_por_empresa(empresa_id, validar_filtros(filtros)),
            'veiculos': VeiculoRepository.listar_simples(empresa_id),
        }

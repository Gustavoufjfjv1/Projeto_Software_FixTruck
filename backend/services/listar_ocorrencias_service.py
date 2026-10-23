import validacoes as v
from constantes import TIPOS_PROBLEMA
from repositories import OcorrenciaRepository, VeiculoRepository

PERIODOS = ['7d', '30d', '90d']
STATUS_FILTRO = ['abertas', 'aberta', 'em_atendimento', 'resolvido']


def validar_periodo(filtros):
    """Atalho 7d/30d/90d ou intervalo personalizado (data_inicio/data_fim, que tem prioridade)."""
    inicio, fim = v.intervalo_datas(filtros.get('data_inicio'), filtros.get('data_fim'))
    periodo = v.opcao(filtros.get('periodo'), PERIODOS, 'Período', obrigatorio=False) or ''
    return {'periodo': '' if (inicio or fim) else periodo, 'data_inicio': inicio or '', 'data_fim': fim or ''}


def validar_filtros(filtros):
    return {
        **validar_periodo(filtros),
        'tipo': v.opcao(filtros.get('tipo'), TIPOS_PROBLEMA, 'Tipo de problema', obrigatorio=False) or '',
        'veiculo': v.identificador(filtros.get('veiculo'), 'Veículo') or '',
        'status': v.opcao(filtros.get('status'), STATUS_FILTRO, 'Status', obrigatorio=False) or '',
    }


class ListarOcorrenciasService:
    def executar(self, empresa_id, filtros):
        filtros = validar_filtros(filtros)
        return {
            'ocorrencias': OcorrenciaRepository.listar_por_empresa(empresa_id, filtros),
            'veiculos': VeiculoRepository.listar_simples(empresa_id),
            'filtros': filtros,
        }

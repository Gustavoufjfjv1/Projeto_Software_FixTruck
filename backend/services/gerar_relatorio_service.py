from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository
from services.listar_ocorrencias_service import validar_periodo


class GerarRelatorioService:
    def executar(self, empresa_id, filtros=None):
        filtros = validar_periodo(filtros or {})
        tempo_medio = OcorrenciaRepository.tempo_medio_resolucao(empresa_id, filtros)
        tempo_medio_oficina = OcorrenciaRepository.tempo_medio_ate_oficina(empresa_id, filtros)
        agregados = OcorrenciaRepository.agregados_relatorio(empresa_id, filtros)
        return {
            'filtros': filtros,
            'total': OcorrenciaRepository.contar_total(empresa_id, filtros),
            'abertas': OcorrenciaRepository.contar_por_status(empresa_id, 'aberta', filtros),
            'em_atendimento': OcorrenciaRepository.contar_por_status(empresa_id, 'em_atendimento', filtros),
            'encerradas': OcorrenciaRepository.contar_por_status(empresa_id, STATUS_RESOLVIDO, filtros),
            'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
            'tempo_medio_oficina': round(tempo_medio_oficina, 0) if tempo_medio_oficina else 0,
            'por_tipo': agregados['por_tipo'],
            'por_veiculo': agregados['por_veiculo'],
            'por_mes': agregados['por_mes'],
            'ranking_oficinas': agregados['ranking_oficinas'],
        }

from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository


class GerarRelatorioService:
    def executar(self, empresa_id, periodo='', status=''):
        tempo_medio = OcorrenciaRepository.tempo_medio_resolucao(
            empresa_id, periodo, status
        )
        tempo_medio_oficina = OcorrenciaRepository.tempo_medio_ate_oficina(
            empresa_id, periodo, status
        )
        agregados = OcorrenciaRepository.agregados_relatorio(
            empresa_id, periodo, status
        )
        return {
            'total': OcorrenciaRepository.contar_total(empresa_id, periodo, status),
            'abertas': OcorrenciaRepository.contar_por_status(
                empresa_id, 'aberta', periodo, status
            ),
            'em_atendimento': OcorrenciaRepository.contar_por_status(
                empresa_id, 'em_atendimento', periodo, status
            ),
            'encerradas': OcorrenciaRepository.contar_por_status(
                empresa_id, STATUS_RESOLVIDO, periodo, status
            ),
            'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
            'tempo_medio_oficina': round(tempo_medio_oficina, 0) if tempo_medio_oficina else 0,
            'por_tipo': agregados['por_tipo'],
            'por_veiculo': agregados['por_veiculo'],
            'por_mes': agregados['por_mes'],
            'ranking_oficinas': agregados['ranking_oficinas'],
        }

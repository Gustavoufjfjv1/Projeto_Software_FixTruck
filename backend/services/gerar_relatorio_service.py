from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository


class GerarRelatorioService:
    def executar(self, empresa_id):
        tempo_medio = OcorrenciaRepository.tempo_medio_resolucao(empresa_id)
        agregados = OcorrenciaRepository.agregados_relatorio(empresa_id)
        return {
            'total': OcorrenciaRepository.contar_total(empresa_id),
            'abertas': OcorrenciaRepository.contar_por_status(empresa_id, 'aberta'),
            'em_atendimento': OcorrenciaRepository.contar_por_status(empresa_id, 'em_atendimento'),
            'encerradas': OcorrenciaRepository.contar_por_status(empresa_id, STATUS_RESOLVIDO),
            'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
            'por_tipo': agregados['por_tipo'],
            'por_veiculo': agregados['por_veiculo'],
            'por_mes': agregados['por_mes'],
        }

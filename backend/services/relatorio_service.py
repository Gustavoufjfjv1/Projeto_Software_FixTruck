from models import Ocorrencia
from utils import STATUS_RESOLVIDO


class RelatorioService:
    @staticmethod
    def obter(empresa_id):
        tempo_medio = Ocorrencia.tempo_medio_resolucao(empresa_id)
        agregados = Ocorrencia.agregados_relatorio(empresa_id)
        return {
            'total': Ocorrencia.contar_total(empresa_id),
            'abertas': Ocorrencia.contar_por_status(empresa_id, 'aberta'),
            'em_atendimento': Ocorrencia.contar_por_status(empresa_id, 'em_atendimento'),
            'encerradas': Ocorrencia.contar_por_status(empresa_id, STATUS_RESOLVIDO),
            'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
            'por_tipo': agregados['por_tipo'],
            'por_veiculo': agregados['por_veiculo'],
            'por_mes': agregados['por_mes'],
        }

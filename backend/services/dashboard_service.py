from models import Ocorrencia, Orcamento


class DashboardService:
    @staticmethod
    def obter(empresa_id):
        tempo_medio = Ocorrencia.tempo_medio_resolucao(empresa_id)
        return {
            'ocorrencias_abertas': Ocorrencia.contar_abertas(empresa_id),
            'total_ocorrencias': Ocorrencia.contar_total(empresa_id),
            'orcamentos_pendentes': Orcamento.contar_pendentes(empresa_id),
            'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
            'problema_comum': Ocorrencia.problema_mais_comum(empresa_id),
            'recentes': Ocorrencia.listar_recentes(empresa_id, 5),
            'abertas_list': Ocorrencia.listar_abertas(empresa_id, 5),
        }

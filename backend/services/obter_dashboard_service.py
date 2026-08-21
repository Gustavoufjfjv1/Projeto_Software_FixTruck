from repositories import OcorrenciaRepository


class ObterDashboardService:
    def executar(self, empresa_id):
        tempo_medio = OcorrenciaRepository.tempo_medio_resolucao(empresa_id)
        tempo_medio_oficina = OcorrenciaRepository.tempo_medio_ate_oficina(empresa_id)
        return {
            'ocorrencias_abertas': OcorrenciaRepository.contar_abertas(empresa_id),
            'total_ocorrencias': OcorrenciaRepository.contar_total(empresa_id),
            'veiculos_atendidos': OcorrenciaRepository.contar_veiculos_atendidos(empresa_id),
            'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
            'tempo_medio_oficina': round(tempo_medio_oficina, 0) if tempo_medio_oficina else 0,
            'problema_comum': OcorrenciaRepository.problema_mais_comum(empresa_id),
            'recentes': OcorrenciaRepository.listar_recentes(empresa_id, 5),
            'abertas_list': OcorrenciaRepository.listar_abertas(empresa_id, 5),
        }

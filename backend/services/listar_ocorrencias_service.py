from repositories import OcorrenciaRepository, VeiculoRepository


class ListarOcorrenciasService:
    def executar(self, empresa_id, filtros):
        return {
            'ocorrencias': OcorrenciaRepository.listar_por_empresa(empresa_id, filtros),
            'veiculos': VeiculoRepository.listar_simples(empresa_id),
        }

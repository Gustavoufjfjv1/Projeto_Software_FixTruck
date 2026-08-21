from repositories import VeiculoRepository, MotoristaRepository


class ObterDadosFormularioOcorrenciaService:
    def executar(self, empresa_id):
        return {
            'veiculos': VeiculoRepository.listar_por_empresa(empresa_id),
            'motoristas': MotoristaRepository.listar_por_empresa(empresa_id, apenas_ativos=True),
        }

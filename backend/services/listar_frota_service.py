from repositories import VeiculoRepository, MotoristaRepository


class ListarFrotaService:
    def executar(self, empresa_id):
        return {
            'veiculos': VeiculoRepository.listar_por_empresa(empresa_id),
            'motoristas': MotoristaRepository.listar_com_veiculo(empresa_id),
        }

from repositories import OrcamentoRepository


class ListarOrcamentosService:
    def executar(self, empresa_id, status=''):
        return {'orcamentos': OrcamentoRepository.listar_por_empresa(empresa_id, status)}

from models import Oficina
from repositories import OcorrenciaRepository, OrcamentoRepository
from services.erros import ServiceError


class ObterDetalheOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id):
        oc = OcorrenciaRepository.buscar_detalhe(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        return {
            'ocorrencia': oc,
            'orcamentos': OrcamentoRepository.listar_por_ocorrencia(ocorrencia_id),
            'oficinas': [o.to_dict() for o in Oficina.query.filter_by(ativa=1).order_by(Oficina.nome).all()],
        }

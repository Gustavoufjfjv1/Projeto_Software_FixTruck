from repositories import OcorrenciaRepository, OficinaRepository
from services.erros import ServiceError


class BuscarOficinasParaOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, raio=None):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        return {
            'ocorrencia': oc.to_dict(),
            'oficinas': OficinaRepository.buscar_para_ocorrencia(empresa_id, oc, raio),
            'raio': raio,
        }

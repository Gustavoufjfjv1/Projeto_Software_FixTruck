from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository
from services.dados_ocorrencia import extrair_dados_ocorrencia
from services.erros import ServiceError


class AtualizarOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if oc.status == STATUS_RESOLVIDO:
            raise ServiceError('Uma ocorrência já resolvida não pode ser editada.', 409)

        for campo, valor in extrair_dados_ocorrencia(empresa_id, dados).items():
            setattr(oc, campo, valor)
        oc.atualizar()
        return {'mensagem': 'Ocorrência atualizada.'}

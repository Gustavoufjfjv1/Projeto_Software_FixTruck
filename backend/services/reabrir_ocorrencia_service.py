from repositories import OcorrenciaRepository
from services.erros import ServiceError, agora_local
from utils import STATUS_RESOLVIDO


class ReabrirOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id):
        ocorrencia = OcorrenciaRepository.buscar_da_empresa(
            ocorrencia_id, empresa_id
        )
        if not ocorrencia:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if ocorrencia.status != STATUS_RESOLVIDO:
            raise ServiceError('Somente ocorrências resolvidas podem ser reabertas.', 400)

        ocorrencia.status = 'aberta'
        ocorrencia.data_encerramento = None
        ocorrencia.motivo_resolucao = None
        ocorrencia.data_reabertura = agora_local()
        ocorrencia.atualizar()
        return {'mensagem': 'Ocorrência reaberta.'}

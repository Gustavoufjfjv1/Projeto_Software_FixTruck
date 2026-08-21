from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository
from services.erros import ServiceError, agora_local


class EncerrarOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if oc.status == STATUS_RESOLVIDO:
            raise ServiceError('Esta ocorrência já está resolvida.', 400)

        oficina_id = dados.get('oficina_id')
        if not oficina_id:
            raise ServiceError('Selecione uma oficina para encerrar a ocorrência.', 400)

        oc.status = STATUS_RESOLVIDO
        oc.oficina_id = oficina_id
        oc.motivo_resolucao = dados.get('motivo', '')
        oc.observacoes = dados.get('observacoes', '')
        oc.data_encerramento = agora_local()
        oc.atualizar()
        return {'mensagem': 'Ocorrência encerrada com status resolvido.'}

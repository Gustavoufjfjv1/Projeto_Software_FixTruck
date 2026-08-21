from repositories import OcorrenciaRepository
from services.erros import ServiceError


class AtualizarStatusOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        novo_status = dados.get('status')
        if novo_status not in ['aberta', 'em_atendimento']:
            raise ServiceError('Status inválido.', 400)
        oc.status = novo_status
        oc.atualizar()
        return {'mensagem': 'Status atualizado.'}

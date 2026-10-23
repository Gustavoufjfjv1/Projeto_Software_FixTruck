import validacoes as v
from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository
from services.erros import ServiceError


class AtualizarStatusOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if oc.status == STATUS_RESOLVIDO:
            raise ServiceError('Esta ocorrência já está resolvida.', 409)
        novo_status = v.opcao(dados.get('status'), ['aberta', 'em_atendimento'], 'Status')
        oc.status = novo_status
        oc.atualizar()
        return {'mensagem': 'Status atualizado.'}

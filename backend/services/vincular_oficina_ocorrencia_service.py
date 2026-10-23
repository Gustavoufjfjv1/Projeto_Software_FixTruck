from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository
from services import posse
from services.erros import ServiceError, agora_local


class VincularOficinaOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if oc.status == STATUS_RESOLVIDO:
            raise ServiceError('Esta ocorrência já está resolvida.', 409)
        oficina = posse.oficina_disponivel(dados.get('oficina_id'), permitir_id=oc.oficina_id)
        oc.oficina_id = oficina.id
        oc.status = 'em_atendimento'
        if not oc.data_vinculacao:
            oc.data_vinculacao = agora_local()
        oc.atualizar()
        return {'mensagem': 'Oficina vinculada à ocorrência.'}

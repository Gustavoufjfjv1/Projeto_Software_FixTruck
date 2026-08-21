from repositories import OcorrenciaRepository
from services.erros import ServiceError


class VincularOficinaOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        oficina_id = dados.get('oficina_id')
        if not oficina_id:
            raise ServiceError('Oficina é obrigatória.', 400)
        oc.oficina_id = oficina_id
        oc.status = 'em_atendimento'
        oc.atualizar()
        return {'mensagem': 'Oficina vinculada à ocorrência.'}

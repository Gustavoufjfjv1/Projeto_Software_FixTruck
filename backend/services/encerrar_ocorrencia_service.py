import validacoes as v
from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository
from services import posse
from services.erros import ServiceError, agora_local


class EncerrarOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if oc.status == STATUS_RESOLVIDO:
            raise ServiceError('Esta ocorrência já está resolvida.', 409)

        if not dados.get('oficina_id'):
            raise v.erro('Selecione uma oficina para encerrar a ocorrência.')
        oficina = posse.oficina_disponivel(dados.get('oficina_id'), permitir_id=oc.oficina_id)
        motivo = v.texto(dados.get('motivo'), 'Motivo', obrigatorio=False, max_len=200)
        observacoes = v.texto(dados.get('observacoes'), 'Observações', obrigatorio=False, max_len=1000)

        if not oc.data_vinculacao:
            oc.data_vinculacao = agora_local()
        oc.status = STATUS_RESOLVIDO
        oc.oficina_id = oficina.id
        oc.motivo_resolucao = motivo or ''
        oc.observacoes = observacoes or ''
        oc.data_encerramento = agora_local()
        oc.atualizar()
        return {'mensagem': 'Ocorrência encerrada com status resolvido.'}

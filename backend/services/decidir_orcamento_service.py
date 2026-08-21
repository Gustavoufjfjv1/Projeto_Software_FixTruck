from repositories import OrcamentoRepository, OcorrenciaRepository
from services.erros import ServiceError, agora_local


class DecidirOrcamentoService:
    def executar(self, empresa_id, orcamento_id, dados):
        orc = OrcamentoRepository.buscar_da_empresa(orcamento_id, empresa_id)
        if not orc:
            raise ServiceError('Orçamento não encontrado.', 404)
        if orc.status != 'pendente':
            raise ServiceError('Este orçamento já foi decidido.', 400)

        decisao = dados.get('decisao')
        agora = agora_local()
        if decisao == 'aprovar':
            orc.status = 'aprovado'
            orc.data_resposta = agora
            orc.atualizar()
            oc = OcorrenciaRepository.buscar_da_empresa(orc.ocorrencia_id, empresa_id)
            if oc:
                oc.oficina_id = orc.oficina_id
                oc.status = 'em_atendimento'
                oc.atualizar()
            mensagem = 'Orçamento aprovado digitalmente.'
        elif decisao == 'rejeitar':
            orc.status = 'rejeitado'
            orc.data_resposta = agora
            orc.atualizar()
            mensagem = 'Orçamento rejeitado.'
        else:
            raise ServiceError('Decisão inválida.', 400)

        return {'mensagem': mensagem, 'ocorrencia_id': orc.ocorrencia_id}

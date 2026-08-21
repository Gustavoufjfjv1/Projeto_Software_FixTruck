from models import Orcamento
from repositories import OcorrenciaRepository
from services.erros import ServiceError, agora_local


class EnviarOrcamentoService:
    def executar(self, empresa_id, dados):
        ocorrencia_id = dados.get('ocorrencia_id')
        oficina_id = dados.get('oficina_id')
        valor_pecas = float(dados.get('valor_pecas') or 0)
        valor_mao_obra = float(dados.get('valor_mao_obra') or 0)
        descricao = dados.get('descricao', '')

        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)

        orcamento = Orcamento(
            ocorrencia_id=ocorrencia_id,
            oficina_id=oficina_id,
            valor_pecas=valor_pecas,
            valor_mao_obra=valor_mao_obra,
            descricao=descricao,
            status='pendente',
            data_envio=agora_local(),
        )
        orcamento.salvar()

        if oc.status == 'aberta':
            oc.oficina_id = oficina_id
            oc.status = 'em_atendimento'
            oc.atualizar()

        return {'mensagem': 'Orçamento registrado. Aguardando aprovação do gestor.'}

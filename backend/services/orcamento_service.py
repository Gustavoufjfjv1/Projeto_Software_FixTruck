from models import Ocorrencia, Orcamento
from services.erros import ServiceError, agora_local


class OrcamentoService:
    @staticmethod
    def listar(empresa_id, status=''):
        return {'orcamentos': Orcamento.listar_por_empresa(empresa_id, status)}

    @staticmethod
    def enviar(empresa_id, dados):
        ocorrencia_id = dados.get('ocorrencia_id')
        oficina_id = dados.get('oficina_id')
        valor_pecas = float(dados.get('valor_pecas') or 0)
        valor_mao_obra = float(dados.get('valor_mao_obra') or 0)
        descricao = dados.get('descricao', '')

        oc = Ocorrencia.buscar_simples_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)

        Orcamento.cadastrar({
            'ocorrencia_id': ocorrencia_id,
            'oficina_id': oficina_id,
            'valor_pecas': valor_pecas,
            'valor_mao_obra': valor_mao_obra,
            'descricao': descricao,
            'status': 'pendente',
            'data_envio': agora_local(),
        })
        if oc['status'] == 'aberta':
            Ocorrencia.editar(ocorrencia_id, {
                'oficina_id': oficina_id,
                'status': 'em_atendimento',
            })
        return {'mensagem': 'Orçamento registrado. Aguardando aprovação do gestor.'}

    @staticmethod
    def decidir(empresa_id, orcamento_id, dados):
        orc = Orcamento.buscar_da_empresa(orcamento_id, empresa_id)
        if not orc:
            raise ServiceError('Orçamento não encontrado.', 404)
        if orc['status'] != 'pendente':
            raise ServiceError('Este orçamento já foi decidido.', 400)

        decisao = dados.get('decisao')
        agora = agora_local()
        if decisao == 'aprovar':
            Orcamento.editar(orcamento_id, {
                'status': 'aprovado',
                'data_resposta': agora,
            })
            Ocorrencia.editar(orc['ocorrencia_id'], {
                'oficina_id': orc['oficina_id'],
                'status': 'em_atendimento',
            })
            mensagem = 'Orçamento aprovado digitalmente.'
        elif decisao == 'rejeitar':
            Orcamento.editar(orcamento_id, {
                'status': 'rejeitado',
                'data_resposta': agora,
            })
            mensagem = 'Orçamento rejeitado.'
        else:
            raise ServiceError('Decisão inválida.', 400)

        return {
            'mensagem': mensagem,
            'ocorrencia_id': orc['ocorrencia_id'],
        }

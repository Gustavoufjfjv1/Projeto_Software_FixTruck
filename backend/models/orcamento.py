from models.base import ModeloBase


class Orcamento(ModeloBase):
    tabela = 'orcamentos'
    campos = (
        'ocorrencia_id', 'oficina_id', 'valor_pecas', 'valor_mao_obra',
        'descricao', 'status', 'data_envio', 'data_resposta',
    )

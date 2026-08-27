from models.base import ModeloBase


class Ocorrencia(ModeloBase):
    tabela = 'ocorrencias'
    campos = (
        'empresa_id', 'motorista_id', 'veiculo_id', 'tipo_veiculo', 'tipo_problema',
        'pane_total', 'lat', 'lon', 'endereco', 'status', 'oficina_id',
        'motivo_resolucao', 'observacoes', 'data_abertura', 'data_encerramento',
        'data_vinculacao',
    )

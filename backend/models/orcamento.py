from .base import ModeloBase


class Orcamento(ModeloBase):
    tabela = 'orcamentos'
    campos = (
        'ocorrencia_id', 'oficina_id', 'valor_pecas', 'valor_mao_obra',
        'descricao', 'status', 'data_envio', 'data_resposta',
    )

    @classmethod
    def listar_por_empresa(cls, empresa_id, status=''):
        query = """SELECT o.*, of.nome as oficina_nome, oc.tipo_problema, oc.status as oc_status,
                          (o.valor_pecas + o.valor_mao_obra) as total, v.placa as veiculo_placa
                   FROM orcamentos o
                   JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
                   JOIN oficinas of ON o.oficina_id = of.id
                   LEFT JOIN veiculos v ON oc.veiculo_id = v.id
                   WHERE oc.empresa_id=?"""
        params = [empresa_id]
        if status:
            query += ' AND o.status=?'
            params.append(status)
        query += ' ORDER BY o.data_envio DESC'
        rows = cls._db().execute(query, params).fetchall()
        return cls._to_list(rows)

    @classmethod
    def listar_por_ocorrencia(cls, ocorrencia_id):
        rows = cls._db().execute(
            """SELECT o.*, of.nome as oficina_nome,
                      (o.valor_pecas + o.valor_mao_obra) as total
               FROM orcamentos o
               JOIN oficinas of ON o.oficina_id = of.id
               WHERE o.ocorrencia_id=? ORDER BY o.data_envio DESC""",
            (ocorrencia_id,),
        ).fetchall()
        return cls._to_list(rows)

    @classmethod
    def contar_pendentes(cls, empresa_id):
        return cls._db().execute(
            """SELECT COUNT(*) as c FROM orcamentos o
               JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
               WHERE oc.empresa_id=? AND o.status='pendente'""",
            (empresa_id,),
        ).fetchone()['c']

    @classmethod
    def buscar_da_empresa(cls, id_, empresa_id):
        row = cls._db().execute(
            """SELECT o.* FROM orcamentos o
               JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
               WHERE o.id=? AND oc.empresa_id=?""",
            (id_, empresa_id),
        ).fetchone()
        return cls._to_dict(row)

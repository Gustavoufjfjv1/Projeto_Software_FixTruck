from database import get_db
from models import Orcamento
from utils import rows_to_list


class OrcamentoRepository:
    """Consultas complexas de orçamentos (SQL puro)."""

    @staticmethod
    def listar_por_empresa(empresa_id, status=''):
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
        return rows_to_list(get_db().execute(query, params).fetchall())

    @staticmethod
    def listar_por_ocorrencia(ocorrencia_id):
        rows = get_db().execute(
            """SELECT o.*, of.nome as oficina_nome,
                      (o.valor_pecas + o.valor_mao_obra) as total
               FROM orcamentos o
               JOIN oficinas of ON o.oficina_id = of.id
               WHERE o.ocorrencia_id=? ORDER BY o.data_envio DESC""",
            (ocorrencia_id,),
        ).fetchall()
        return rows_to_list(rows)

    @staticmethod
    def contar_pendentes(empresa_id):
        return get_db().execute(
            """SELECT COUNT(*) as c FROM orcamentos o
               JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
               WHERE oc.empresa_id=? AND o.status='pendente'""",
            (empresa_id,),
        ).fetchone()['c']

    @staticmethod
    def buscar_da_empresa(orcamento_id, empresa_id):
        row = get_db().execute(
            """SELECT o.* FROM orcamentos o
               JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
               WHERE o.id=? AND oc.empresa_id=?""",
            (orcamento_id, empresa_id),
        ).fetchone()
        return Orcamento.from_row(row)

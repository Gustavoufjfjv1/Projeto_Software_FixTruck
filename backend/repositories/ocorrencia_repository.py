from database import get_db
from models import Ocorrencia
from utils import row_to_dict, rows_to_list


class OcorrenciaRepository:
    """Consultas complexas de ocorrências (SQL puro)."""

    @staticmethod
    def listar_por_empresa(empresa_id, filtros=None):
        filtros = filtros or {}
        query = """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa, m.nome as motorista_nome
                   FROM ocorrencias o
                   LEFT JOIN oficinas of ON o.oficina_id = of.id
                   LEFT JOIN veiculos v ON o.veiculo_id = v.id
                   LEFT JOIN motoristas m ON o.motorista_id = m.id
                   WHERE o.empresa_id=?"""
        params = [empresa_id]
        if filtros.get('tipo'):
            query += ' AND o.tipo_problema=?'
            params.append(filtros['tipo'])
        if filtros.get('veiculo'):
            query += ' AND o.veiculo_id=?'
            params.append(filtros['veiculo'])
        status = filtros.get('status', '')
        if status == 'abertas':
            query += " AND o.status IN ('aberta','em_atendimento')"
        elif status:
            query += ' AND o.status=?'
            params.append(status)
        periodo = filtros.get('periodo', '')
        if periodo == '7d':
            query += " AND o.data_abertura >= datetime('now', '-7 days')"
        elif periodo == '30d':
            query += " AND o.data_abertura >= datetime('now', '-30 days')"
        elif periodo == '90d':
            query += " AND o.data_abertura >= datetime('now', '-90 days')"
        query += ' ORDER BY o.data_abertura DESC'
        return rows_to_list(get_db().execute(query, params).fetchall())

    @staticmethod
    def buscar_detalhe(ocorrencia_id, empresa_id):
        row = get_db().execute(
            """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa, v.modelo as veiculo_modelo,
                      m.nome as motorista_nome
               FROM ocorrencias o
               LEFT JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               LEFT JOIN motoristas m ON o.motorista_id = m.id
               WHERE o.id=? AND o.empresa_id=?""",
            (ocorrencia_id, empresa_id),
        ).fetchone()
        return row_to_dict(row)

    @staticmethod
    def buscar_da_empresa(ocorrencia_id, empresa_id):
        row = get_db().execute(
            'SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?',
            (ocorrencia_id, empresa_id),
        ).fetchone()
        return Ocorrencia.from_row(row)

    @staticmethod
    def contar_abertas(empresa_id):
        return get_db().execute(
            "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status IN ('aberta','em_atendimento')",
            (empresa_id,),
        ).fetchone()['c']

    @staticmethod
    def contar_total(empresa_id):
        return get_db().execute(
            'SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=?',
            (empresa_id,),
        ).fetchone()['c']

    @staticmethod
    def contar_por_status(empresa_id, status):
        return get_db().execute(
            'SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status=?',
            (empresa_id, status),
        ).fetchone()['c']

    @staticmethod
    def tempo_medio_resolucao(empresa_id):
        return get_db().execute(
            """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
               FROM ocorrencias WHERE empresa_id=? AND status='resolvido' AND data_encerramento IS NOT NULL""",
            (empresa_id,),
        ).fetchone()['avg']

    @staticmethod
    def problema_mais_comum(empresa_id):
        row = get_db().execute(
            """SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=?
               GROUP BY tipo_problema ORDER BY c DESC LIMIT 1""",
            (empresa_id,),
        ).fetchone()
        return row['tipo_problema'] if row else '-'

    @staticmethod
    def listar_recentes(empresa_id, limite=5):
        rows = get_db().execute(
            """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa
               FROM ocorrencias o
               LEFT JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               WHERE o.empresa_id=? ORDER BY o.data_abertura DESC LIMIT ?""",
            (empresa_id, limite),
        ).fetchall()
        return rows_to_list(rows)

    @staticmethod
    def listar_abertas(empresa_id, limite=5):
        rows = get_db().execute(
            """SELECT o.*, v.placa as veiculo_placa FROM ocorrencias o
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               WHERE o.empresa_id=? AND o.status IN ('aberta','em_atendimento')
               ORDER BY o.data_abertura DESC LIMIT ?""",
            (empresa_id, limite),
        ).fetchall()
        return rows_to_list(rows)

    @staticmethod
    def agregados_relatorio(empresa_id):
        db = get_db()
        por_tipo = db.execute(
            'SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=? GROUP BY tipo_problema',
            (empresa_id,),
        ).fetchall()
        por_veiculo = db.execute(
            """SELECT COALESCE(v.placa, o.tipo_veiculo) as veiculo, COUNT(*) as c
               FROM ocorrencias o LEFT JOIN veiculos v ON o.veiculo_id = v.id
               WHERE o.empresa_id=? GROUP BY veiculo""",
            (empresa_id,),
        ).fetchall()
        por_mes = db.execute(
            """SELECT strftime('%m/%Y', data_abertura) as mes, COUNT(*) as c
               FROM ocorrencias WHERE empresa_id=?
               GROUP BY mes ORDER BY data_abertura DESC LIMIT 6""",
            (empresa_id,),
        ).fetchall()
        return {
            'por_tipo': rows_to_list(por_tipo),
            'por_veiculo': rows_to_list(por_veiculo),
            'por_mes': rows_to_list(por_mes),
        }

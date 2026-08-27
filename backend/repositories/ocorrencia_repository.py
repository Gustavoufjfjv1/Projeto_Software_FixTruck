from database import get_db
from models import Ocorrencia
from utils import row_to_dict, rows_to_list


def _sql_periodo(periodo, coluna='o.data_abertura'):
    if periodo == '7d':
        return f" AND {coluna} >= datetime('now', '-7 days')"
    if periodo == '30d':
        return f" AND {coluna} >= datetime('now', '-30 days')"
    if periodo == '90d':
        return f" AND {coluna} >= datetime('now', '-90 days')"
    return ''


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
        query += _sql_periodo(filtros.get('periodo', ''))
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
    def contar_total(empresa_id, periodo=''):
        sql = 'SELECT COUNT(*) as c FROM ocorrencias o WHERE o.empresa_id=?' + _sql_periodo(periodo)
        return get_db().execute(sql, (empresa_id,)).fetchone()['c']

    @staticmethod
    def contar_por_status(empresa_id, status, periodo=''):
        sql = 'SELECT COUNT(*) as c FROM ocorrencias o WHERE o.empresa_id=? AND o.status=?' + _sql_periodo(periodo)
        return get_db().execute(sql, (empresa_id, status)).fetchone()['c']

    @staticmethod
    def contar_veiculos_atendidos(empresa_id):
        return get_db().execute(
            """SELECT COUNT(DISTINCT veiculo_id) as c FROM ocorrencias
               WHERE empresa_id=? AND veiculo_id IS NOT NULL""",
            (empresa_id,),
        ).fetchone()['c']

    @staticmethod
    def tempo_medio_resolucao(empresa_id, periodo=''):
        sql = """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
                 FROM ocorrencias o
                 WHERE o.empresa_id=? AND o.status='resolvido' AND o.data_encerramento IS NOT NULL"""
        sql += _sql_periodo(periodo)
        return get_db().execute(sql, (empresa_id,)).fetchone()['avg']

    @staticmethod
    def tempo_medio_ate_oficina(empresa_id, periodo=''):
        sql = """SELECT AVG((julianday(data_vinculacao) - julianday(data_abertura)) * 24 * 60) as avg
                 FROM ocorrencias o
                 WHERE o.empresa_id=? AND o.data_vinculacao IS NOT NULL"""
        sql += _sql_periodo(periodo)
        return get_db().execute(sql, (empresa_id,)).fetchone()['avg']

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
    def agregados_relatorio(empresa_id, periodo=''):
        db = get_db()
        where = 'WHERE o.empresa_id=?' + _sql_periodo(periodo)
        params = (empresa_id,)
        por_tipo = db.execute(
            f'SELECT o.tipo_problema, COUNT(*) as c FROM ocorrencias o {where} GROUP BY o.tipo_problema',
            params,
        ).fetchall()
        por_veiculo = db.execute(
            f"""SELECT COALESCE(v.placa, o.tipo_veiculo) as veiculo, COUNT(*) as c
                FROM ocorrencias o LEFT JOIN veiculos v ON o.veiculo_id = v.id
                {where} GROUP BY veiculo""",
            params,
        ).fetchall()
        por_mes = db.execute(
            f"""SELECT strftime('%m/%Y', o.data_abertura) as mes, COUNT(*) as c
                FROM ocorrencias o {where}
                GROUP BY mes ORDER BY o.data_abertura DESC LIMIT 6""",
            params,
        ).fetchall()
        ranking_oficinas = db.execute(
            f"""SELECT of.nome, COUNT(*) as c FROM ocorrencias o
                JOIN oficinas of ON o.oficina_id = of.id
                {where} AND o.oficina_id IS NOT NULL
                GROUP BY of.nome ORDER BY c DESC LIMIT 5""",
            params,
        ).fetchall()
        return {
            'por_tipo': rows_to_list(por_tipo),
            'por_veiculo': rows_to_list(por_veiculo),
            'por_mes': rows_to_list(por_mes),
            'ranking_oficinas': rows_to_list(ranking_oficinas),
        }

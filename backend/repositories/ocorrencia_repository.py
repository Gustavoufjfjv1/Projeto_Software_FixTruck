from datetime import date, timedelta

from database import get_db
from horarios import agora_sao_paulo
from models import Ocorrencia
from utils import row_to_dict, rows_to_list

DIAS_PERIODO = {'7d': 7, '30d': 30, '90d': 90}
_FORMATO = '%Y-%m-%d %H:%M:%S'


def filtro_datas(filtros, coluna='o.data_abertura'):
    """(sql, params) do período. Datas gravadas como texto no horário de São Paulo.

    Intervalo personalizado (data_inicio/data_fim, YYYY-MM-DD) tem prioridade sobre o atalho 7d/30d/90d;
    o dia final é incluído por inteiro (< dia seguinte 00:00).
    """
    filtros = filtros if isinstance(filtros, dict) else {'periodo': filtros or ''}
    inicio, fim = filtros.get('data_inicio'), filtros.get('data_fim')
    sql, params = '', []
    if inicio or fim:
        if inicio:
            sql += f' AND {coluna} >= ?'
            params.append(f'{inicio} 00:00:00')
        if fim:
            sql += f' AND {coluna} < ?'
            params.append(f'{date.fromisoformat(fim) + timedelta(days=1)} 00:00:00')
    elif filtros.get('periodo') in DIAS_PERIODO:
        limite = agora_sao_paulo().replace(tzinfo=None) - timedelta(days=DIAS_PERIODO[filtros['periodo']])
        sql += f' AND {coluna} >= ?'
        params.append(limite.strftime(_FORMATO))
    return sql, params


# Ocorrências visíveis ao motorista: da própria empresa e (registradas por ele OU do veículo vinculado a ele).
_FILTRO_MOTORISTA = """o.empresa_id = ? AND (o.motorista_id = ? OR o.veiculo_id IN (
    SELECT id FROM veiculos WHERE motorista_id = ? AND empresa_id = ?))"""


class OcorrenciaRepository:
    """Consultas complexas de ocorrências (SQL puro)."""

    @staticmethod
    def listar_do_motorista(motorista_id, empresa_id, apenas_abertas=False):
        query = f"""SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa
                    FROM ocorrencias o
                    LEFT JOIN oficinas of ON o.oficina_id = of.id
                    LEFT JOIN veiculos v ON o.veiculo_id = v.id
                    WHERE {_FILTRO_MOTORISTA}"""
        if apenas_abertas:
            query += " AND o.status IN ('aberta','em_atendimento')"
        query += ' ORDER BY o.data_abertura DESC'
        params = (empresa_id, motorista_id, motorista_id, empresa_id)
        return rows_to_list(get_db().execute(query, params).fetchall())

    @staticmethod
    def buscar_do_motorista(ocorrencia_id, motorista_id, empresa_id):
        row = get_db().execute(
            f'SELECT o.id FROM ocorrencias o WHERE o.id = ? AND {_FILTRO_MOTORISTA}',
            (ocorrencia_id, empresa_id, motorista_id, motorista_id, empresa_id),
        ).fetchone()
        if not row:
            return None
        return Ocorrencia.buscar_por_id(row['id'])

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
        sql_datas, params_datas = filtro_datas(filtros)
        query += sql_datas
        params.extend(params_datas)
        query += ' ORDER BY o.data_abertura DESC'
        return rows_to_list(get_db().execute(query, params).fetchall())

    @staticmethod
    def buscar_detalhe(ocorrencia_id, empresa_id):
        row = get_db().execute(
            """SELECT o.*, of.nome as oficina_nome, of.telefone as oficina_telefone,
                      v.placa as veiculo_placa, v.modelo as veiculo_modelo, m.nome as motorista_nome
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
            'SELECT id FROM ocorrencias WHERE id=? AND empresa_id=?',
            (ocorrencia_id, empresa_id),
        ).fetchone()
        if not row:
            return None
        return Ocorrencia.buscar_por_id(row['id'])

    @staticmethod
    def contar_abertas(empresa_id):
        return get_db().execute(
            "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status IN ('aberta','em_atendimento')",
            (empresa_id,),
        ).fetchone()['c']

    @staticmethod
    def contar_total(empresa_id, filtros=None):
        sql_datas, params = filtro_datas(filtros)
        sql = 'SELECT COUNT(*) as c FROM ocorrencias o WHERE o.empresa_id=?' + sql_datas
        return get_db().execute(sql, (empresa_id, *params)).fetchone()['c']

    @staticmethod
    def contar_por_status(empresa_id, status, filtros=None):
        sql_datas, params = filtro_datas(filtros)
        sql = 'SELECT COUNT(*) as c FROM ocorrencias o WHERE o.empresa_id=? AND o.status=?' + sql_datas
        return get_db().execute(sql, (empresa_id, status, *params)).fetchone()['c']

    @staticmethod
    def contar_veiculos_atendidos(empresa_id):
        return get_db().execute(
            """SELECT COUNT(DISTINCT veiculo_id) as c FROM ocorrencias
               WHERE empresa_id=? AND veiculo_id IS NOT NULL""",
            (empresa_id,),
        ).fetchone()['c']

    @staticmethod
    def tempo_medio_resolucao(empresa_id, filtros=None):
        sql_datas, params = filtro_datas(filtros)
        sql = """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
                 FROM ocorrencias o
                 WHERE o.empresa_id=? AND o.status='resolvido' AND o.data_encerramento IS NOT NULL"""
        return get_db().execute(sql + sql_datas, (empresa_id, *params)).fetchone()['avg']

    @staticmethod
    def tempo_medio_ate_oficina(empresa_id, filtros=None):
        sql_datas, params = filtro_datas(filtros)
        sql = """SELECT AVG((julianday(data_vinculacao) - julianday(data_abertura)) * 24 * 60) as avg
                 FROM ocorrencias o
                 WHERE o.empresa_id=? AND o.data_vinculacao IS NOT NULL"""
        return get_db().execute(sql + sql_datas, (empresa_id, *params)).fetchone()['avg']

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
    def agregados_relatorio(empresa_id, filtros=None):
        db = get_db()
        sql_datas, params_datas = filtro_datas(filtros)
        where = 'WHERE o.empresa_id=?' + sql_datas
        params = (empresa_id, *params_datas)
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
                GROUP BY mes ORDER BY MAX(o.data_abertura) DESC LIMIT 6""",
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

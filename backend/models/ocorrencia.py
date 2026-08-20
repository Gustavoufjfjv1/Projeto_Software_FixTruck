from .base import ModeloBase


class Ocorrencia(ModeloBase):
    tabela = 'ocorrencias'
    campos = (
        'empresa_id', 'motorista_id', 'veiculo_id', 'tipo_veiculo', 'tipo_problema',
        'pane_total', 'lat', 'lon', 'endereco', 'status', 'oficina_id',
        'motivo_resolucao', 'observacoes', 'data_abertura', 'data_encerramento',
    )

    @classmethod
    def listar_por_empresa(cls, empresa_id, filtros=None):
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
        rows = cls._db().execute(query, params).fetchall()
        return cls._to_list(rows)

    @classmethod
    def buscar_da_empresa(cls, id_, empresa_id):
        row = cls._db().execute(
            """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa, v.modelo as veiculo_modelo,
                      m.nome as motorista_nome
               FROM ocorrencias o
               LEFT JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               LEFT JOIN motoristas m ON o.motorista_id = m.id
               WHERE o.id=? AND o.empresa_id=?""",
            (id_, empresa_id),
        ).fetchone()
        return cls._to_dict(row)

    @classmethod
    def buscar_simples_da_empresa(cls, id_, empresa_id):
        row = cls._db().execute(
            'SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?',
            (id_, empresa_id),
        ).fetchone()
        return cls._to_dict(row)

    @classmethod
    def contar_abertas(cls, empresa_id):
        return cls._db().execute(
            "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status IN ('aberta','em_atendimento')",
            (empresa_id,),
        ).fetchone()['c']

    @classmethod
    def contar_total(cls, empresa_id):
        return cls._db().execute(
            'SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=?',
            (empresa_id,),
        ).fetchone()['c']

    @classmethod
    def contar_por_status(cls, empresa_id, status):
        return cls._db().execute(
            'SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status=?',
            (empresa_id, status),
        ).fetchone()['c']

    @classmethod
    def tempo_medio_resolucao(cls, empresa_id):
        return cls._db().execute(
            """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
               FROM ocorrencias WHERE empresa_id=? AND status='resolvido' AND data_encerramento IS NOT NULL""",
            (empresa_id,),
        ).fetchone()['avg']

    @classmethod
    def problema_mais_comum(cls, empresa_id):
        row = cls._db().execute(
            """SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=?
               GROUP BY tipo_problema ORDER BY c DESC LIMIT 1""",
            (empresa_id,),
        ).fetchone()
        return row['tipo_problema'] if row else '-'

    @classmethod
    def listar_recentes(cls, empresa_id, limite=5):
        rows = cls._db().execute(
            """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa
               FROM ocorrencias o
               LEFT JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               WHERE o.empresa_id=? ORDER BY o.data_abertura DESC LIMIT ?""",
            (empresa_id, limite),
        ).fetchall()
        return cls._to_list(rows)

    @classmethod
    def listar_abertas(cls, empresa_id, limite=5):
        rows = cls._db().execute(
            """SELECT o.*, v.placa as veiculo_placa FROM ocorrencias o
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               WHERE o.empresa_id=? AND o.status IN ('aberta','em_atendimento')
               ORDER BY o.data_abertura DESC LIMIT ?""",
            (empresa_id, limite),
        ).fetchall()
        return cls._to_list(rows)

    @classmethod
    def agregados_relatorio(cls, empresa_id):
        db = cls._db()
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
            'por_tipo': cls._to_list(por_tipo),
            'por_veiculo': cls._to_list(por_veiculo),
            'por_mes': cls._to_list(por_mes),
        }

from flask import Blueprint, jsonify, g
from database import get_db
from auth import login_required
from utils import STATUS_RESOLVIDO, rows_to_list

relatorio_bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')


@relatorio_bp.route('', methods=['GET'])
@login_required
def relatorios():
    db = get_db()
    empresa_id = g.empresa_id

    total = db.execute(
        'SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=?', (empresa_id,)
    ).fetchone()['c']
    abertas = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status='aberta'",
        (empresa_id,),
    ).fetchone()['c']
    em_atendimento = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status='em_atendimento'",
        (empresa_id,),
    ).fetchone()['c']
    resolvidas = db.execute(
        'SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status=?',
        (empresa_id, STATUS_RESOLVIDO),
    ).fetchone()['c']
    tempo_medio = db.execute(
        """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
           FROM ocorrencias WHERE empresa_id=? AND status=?""",
        (empresa_id, STATUS_RESOLVIDO),
    ).fetchone()['avg']
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

    return jsonify({
        'total': total,
        'abertas': abertas,
        'em_atendimento': em_atendimento,
        'encerradas': resolvidas,
        'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
        'por_tipo': rows_to_list(por_tipo),
        'por_veiculo': rows_to_list(por_veiculo),
        'por_mes': rows_to_list(por_mes),
    })

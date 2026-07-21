from flask import Blueprint, jsonify, g
from database import get_db
from auth import login_required
from utils import STATUS_RESOLVIDO, rows_to_list

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('', methods=['GET'])
@login_required
def dashboard():
    db = get_db()
    empresa_id = g.empresa_id

    ocorrencias_abertas = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status IN ('aberta','em_atendimento')",
        (empresa_id,),
    ).fetchone()['c']
    total_ocorrencias = db.execute(
        'SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=?', (empresa_id,)
    ).fetchone()['c']
    orcamentos_pendentes = db.execute(
        """SELECT COUNT(*) as c FROM orcamentos o
           JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
           WHERE oc.empresa_id=? AND o.status='pendente'""",
        (empresa_id,),
    ).fetchone()['c']
    tempo_medio = db.execute(
        """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
           FROM ocorrencias WHERE empresa_id=? AND status=? AND data_encerramento IS NOT NULL""",
        (empresa_id, STATUS_RESOLVIDO),
    ).fetchone()['avg']
    problema_comum = db.execute(
        """SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=?
           GROUP BY tipo_problema ORDER BY c DESC LIMIT 1""",
        (empresa_id,),
    ).fetchone()
    recentes = db.execute(
        """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa
           FROM ocorrencias o
           LEFT JOIN oficinas of ON o.oficina_id = of.id
           LEFT JOIN veiculos v ON o.veiculo_id = v.id
           WHERE o.empresa_id=? ORDER BY o.data_abertura DESC LIMIT 5""",
        (empresa_id,),
    ).fetchall()
    abertas_list = db.execute(
        """SELECT o.*, v.placa as veiculo_placa FROM ocorrencias o
           LEFT JOIN veiculos v ON o.veiculo_id = v.id
           WHERE o.empresa_id=? AND o.status IN ('aberta','em_atendimento')
           ORDER BY o.data_abertura DESC LIMIT 5""",
        (empresa_id,),
    ).fetchall()

    return jsonify({
        'ocorrencias_abertas': ocorrencias_abertas,
        'total_ocorrencias': total_ocorrencias,
        'orcamentos_pendentes': orcamentos_pendentes,
        'tempo_medio': round(tempo_medio, 0) if tempo_medio else 0,
        'problema_comum': problema_comum['tipo_problema'] if problema_comum else '-',
        'recentes': rows_to_list(recentes),
        'abertas_list': rows_to_list(abertas_list),
    })

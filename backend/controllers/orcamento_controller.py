from flask import Blueprint, request, jsonify, g
from database import get_db
from auth import login_required
from utils import rows_to_list

orcamento_bp = Blueprint('orcamentos', __name__, url_prefix='/api/orcamentos')


@orcamento_bp.route('', methods=['GET'])
@login_required
def listar():
    db = get_db()
    empresa_id = g.empresa_id
    filtro = request.args.get('status', '')
    query = """SELECT o.*, of.nome as oficina_nome, oc.tipo_problema, oc.status as oc_status,
                      (o.valor_pecas + o.valor_mao_obra) as total, v.placa as veiculo_placa
               FROM orcamentos o
               JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
               JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON oc.veiculo_id = v.id
               WHERE oc.empresa_id=?"""
    params = [empresa_id]
    if filtro:
        query += ' AND o.status=?'
        params.append(filtro)
    query += ' ORDER BY o.data_envio DESC'
    lista = db.execute(query, params).fetchall()
    return jsonify({'orcamentos': rows_to_list(lista)})


@orcamento_bp.route('', methods=['POST'])
@login_required
def enviar():
    db = get_db()
    data = request.get_json(silent=True) or {}
    ocorrencia_id = data.get('ocorrencia_id')
    oficina_id = data.get('oficina_id')
    valor_pecas = float(data.get('valor_pecas') or 0)
    valor_mao_obra = float(data.get('valor_mao_obra') or 0)
    descricao = data.get('descricao', '')

    oc = db.execute(
        'SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?',
        (ocorrencia_id, g.empresa_id),
    ).fetchone()
    if not oc:
        return jsonify({'erro': 'Ocorrência não encontrada.'}), 404

    db.execute(
        """INSERT INTO orcamentos (ocorrencia_id, oficina_id, valor_pecas, valor_mao_obra,
           descricao, status, data_envio)
           VALUES (?,?,?,?,?,'pendente',datetime('now','localtime'))""",
        (ocorrencia_id, oficina_id, valor_pecas, valor_mao_obra, descricao),
    )
    if oc['status'] == 'aberta':
        db.execute(
            "UPDATE ocorrencias SET oficina_id=?, status='em_atendimento' WHERE id=?",
            (oficina_id, ocorrencia_id),
        )
    db.commit()
    return jsonify({'mensagem': 'Orçamento registrado. Aguardando aprovação do gestor.'}), 201


@orcamento_bp.route('/<int:orcamento_id>/decidir', methods=['POST'])
@login_required
def decidir(orcamento_id):
    db = get_db()
    data = request.get_json(silent=True) or {}
    decisao = data.get('decisao')

    orc = db.execute(
        """SELECT o.* FROM orcamentos o
           JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
           WHERE o.id=? AND oc.empresa_id=?""",
        (orcamento_id, g.empresa_id),
    ).fetchone()
    if not orc:
        return jsonify({'erro': 'Orçamento não encontrado.'}), 404
    if orc['status'] != 'pendente':
        return jsonify({'erro': 'Este orçamento já foi decidido.'}), 400

    if decisao == 'aprovar':
        db.execute(
            """UPDATE orcamentos SET status='aprovado', data_resposta=datetime('now','localtime')
               WHERE id=?""",
            (orcamento_id,),
        )
        db.execute(
            """UPDATE ocorrencias SET oficina_id=?, status='em_atendimento' WHERE id=?""",
            (orc['oficina_id'], orc['ocorrencia_id']),
        )
        mensagem = 'Orçamento aprovado digitalmente.'
    elif decisao == 'rejeitar':
        db.execute(
            """UPDATE orcamentos SET status='rejeitado', data_resposta=datetime('now','localtime')
               WHERE id=?""",
            (orcamento_id,),
        )
        mensagem = 'Orçamento rejeitado.'
    else:
        return jsonify({'erro': 'Decisão inválida.'}), 400

    db.commit()
    return jsonify({
        'mensagem': mensagem,
        'ocorrencia_id': orc['ocorrencia_id'],
    })

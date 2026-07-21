from flask import Blueprint, request, jsonify, g
from database import get_db
from auth import login_required
from utils import rows_to_list

frota_bp = Blueprint('frota', __name__, url_prefix='/api/frota')


@frota_bp.route('', methods=['GET'])
@login_required
def listar():
    db = get_db()
    empresa_id = g.empresa_id
    veiculos = db.execute(
        """SELECT v.*, m.nome as motorista_nome FROM veiculos v
           LEFT JOIN motoristas m ON v.motorista_id = m.id
           WHERE v.empresa_id=? ORDER BY v.placa""",
        (empresa_id,),
    ).fetchall()
    motoristas = db.execute(
        """SELECT m.*,
                  (SELECT placa FROM veiculos WHERE motorista_id=m.id LIMIT 1) as veiculo_placa
           FROM motoristas m WHERE m.empresa_id=? ORDER BY m.nome""",
        (empresa_id,),
    ).fetchall()
    return jsonify({
        'veiculos': rows_to_list(veiculos),
        'motoristas': rows_to_list(motoristas),
    })


@frota_bp.route('/motoristas', methods=['POST'])
@login_required
def novo_motorista():
    db = get_db()
    data = request.get_json(silent=True) or {}
    nome = (data.get('nome') or '').strip()
    if not nome:
        return jsonify({'erro': 'Nome do motorista é obrigatório.'}), 400
    db.execute(
        'INSERT INTO motoristas (empresa_id, nome, cnh, telefone) VALUES (?,?,?,?)',
        (g.empresa_id, nome, data.get('cnh', ''), data.get('telefone', '')),
    )
    db.commit()
    return jsonify({'mensagem': 'Motorista cadastrado.'}), 201


@frota_bp.route('/veiculos', methods=['POST'])
@login_required
def novo_veiculo():
    db = get_db()
    data = request.get_json(silent=True) or {}
    placa = (data.get('placa') or '').strip().upper()
    if not placa:
        return jsonify({'erro': 'Placa é obrigatória.'}), 400
    motorista_id = data.get('motorista_id') or None
    db.execute(
        """INSERT INTO veiculos (empresa_id, placa, modelo, marca, tipo_veiculo, motorista_id)
           VALUES (?,?,?,?,?,?)""",
        (
            g.empresa_id,
            placa,
            data.get('modelo', ''),
            data.get('marca', ''),
            data.get('tipo_veiculo', 'pesado'),
            motorista_id,
        ),
    )
    db.commit()
    return jsonify({'mensagem': 'Veículo cadastrado na frota.'}), 201


@frota_bp.route('/veiculos/<int:veiculo_id>/vincular', methods=['POST'])
@login_required
def vincular_motorista(veiculo_id):
    db = get_db()
    data = request.get_json(silent=True) or {}
    motorista_id = data.get('motorista_id') or None

    veiculo = db.execute(
        'SELECT * FROM veiculos WHERE id=? AND empresa_id=?',
        (veiculo_id, g.empresa_id),
    ).fetchone()
    if not veiculo:
        return jsonify({'erro': 'Veículo não encontrado.'}), 404

    if motorista_id:
        mot = db.execute(
            'SELECT id FROM motoristas WHERE id=? AND empresa_id=?',
            (motorista_id, g.empresa_id),
        ).fetchone()
        if not mot:
            return jsonify({'erro': 'Motorista inválido.'}), 400

    db.execute('UPDATE veiculos SET motorista_id=? WHERE id=?', (motorista_id, veiculo_id))
    db.commit()
    return jsonify({'mensagem': 'Motorista vinculado ao veículo da frota.'})

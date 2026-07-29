from flask import Blueprint, request, jsonify, g
from database import get_db
from auth import login_required
from utils import (
    STATUS_RESOLVIDO,
    haversine,
    oficina_aberta_agora,
    row_to_dict,
    rows_to_list,
)

ocorrencia_bp = Blueprint('ocorrencias', __name__, url_prefix='/api/ocorrencias')


@ocorrencia_bp.route('', methods=['GET'])
@login_required
def listar():
    db = get_db()
    empresa_id = g.empresa_id
    filtro_periodo = request.args.get('periodo', '')
    filtro_tipo = request.args.get('tipo', '')
    filtro_veiculo = request.args.get('veiculo', '')
    filtro_status = request.args.get('status', '')

    query = """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa, m.nome as motorista_nome
               FROM ocorrencias o
               LEFT JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               LEFT JOIN motoristas m ON o.motorista_id = m.id
               WHERE o.empresa_id=?"""
    params = [empresa_id]
    if filtro_tipo:
        query += ' AND o.tipo_problema=?'
        params.append(filtro_tipo)
    if filtro_veiculo:
        query += ' AND o.veiculo_id=?'
        params.append(filtro_veiculo)
    if filtro_status == 'abertas':
        query += " AND o.status IN ('aberta','em_atendimento')"
    elif filtro_status:
        query += ' AND o.status=?'
        params.append(filtro_status)
    if filtro_periodo == '7d':
        query += " AND o.data_abertura >= datetime('now', '-7 days')"
    elif filtro_periodo == '30d':
        query += " AND o.data_abertura >= datetime('now', '-30 days')"
    elif filtro_periodo == '90d':
        query += " AND o.data_abertura >= datetime('now', '-90 days')"
    query += ' ORDER BY o.data_abertura DESC'

    ocorrencias_list = db.execute(query, params).fetchall()
    veiculos = db.execute(
        'SELECT id, placa, modelo FROM veiculos WHERE empresa_id=? ORDER BY placa',
        (empresa_id,),
    ).fetchall()
    return jsonify({
        'ocorrencias': rows_to_list(ocorrencias_list),
        'veiculos': rows_to_list(veiculos),
    })


@ocorrencia_bp.route('/form-data', methods=['GET'])
@login_required
def form_data():
    db = get_db()
    empresa_id = g.empresa_id
    veiculos = db.execute(
        """SELECT v.*, m.nome as motorista_nome FROM veiculos v
           LEFT JOIN motoristas m ON v.motorista_id = m.id
           WHERE v.empresa_id=? ORDER BY v.placa""",
        (empresa_id,),
    ).fetchall()
    motoristas = db.execute(
        'SELECT * FROM motoristas WHERE empresa_id=? AND ativo=1 ORDER BY nome',
        (empresa_id,),
    ).fetchall()
    return jsonify({
        'veiculos': rows_to_list(veiculos),
        'motoristas': rows_to_list(motoristas),
    })


@ocorrencia_bp.route('', methods=['POST'])
@login_required
def criar():
    db = get_db()
    empresa_id = g.empresa_id
    data = request.get_json(silent=True) or {}

    veiculo_id = data.get('veiculo_id') or None
    motorista_id = data.get('motorista_id') or None
    tipo_problema = data.get('tipo_problema')
    pane_total = 1 if data.get('pane_total') else 0
    lat = data.get('lat')
    lon = data.get('lon')
    via = (data.get('via') or '').strip()
    km = (data.get('km') or '').strip()
    cidade = (data.get('cidade') or '').strip()
    endereco = (data.get('endereco') or '').strip()

    if not endereco:
        partes = []
        if via:
            partes.append(via)
        if km:
            partes.append(f'KM {km}')
        if cidade:
            partes.append(cidade)
        endereco = ' — '.join(partes)

    if not tipo_problema:
        return jsonify({'erro': 'Tipo de problema é obrigatório.'}), 400
    if not lat or not lon:
        return jsonify({'erro': 'Informe a localização via GPS para registrar a ocorrência.'}), 400

    tipo_veiculo = data.get('tipo_veiculo', 'pesado')
    if veiculo_id:
        veiculo = db.execute(
            'SELECT * FROM veiculos WHERE id=? AND empresa_id=?',
            (veiculo_id, empresa_id),
        ).fetchone()
        if veiculo:
            tipo_veiculo = veiculo['tipo_veiculo']
            if not motorista_id and veiculo['motorista_id']:
                motorista_id = veiculo['motorista_id']

    db.execute(
        """INSERT INTO ocorrencias (empresa_id, motorista_id, veiculo_id, tipo_veiculo, tipo_problema,
           pane_total, lat, lon, endereco, status, data_abertura)
           VALUES (?,?,?,?,?,?,?,?,?,'aberta',datetime('now','localtime'))""",
        (empresa_id, motorista_id, veiculo_id, tipo_veiculo, tipo_problema,
         pane_total, lat, lon, endereco or f'GPS: {lat}, {lon}'),
    )
    db.commit()
    oc_id = db.execute('SELECT last_insert_rowid() as id').fetchone()['id']
    return jsonify({
        'mensagem': 'Ocorrência registrada com localização GPS.',
        'id': oc_id,
    }), 201


@ocorrencia_bp.route('/<int:ocorrencia_id>', methods=['GET'])
@login_required
def detalhe(ocorrencia_id):
    db = get_db()
    oc = db.execute(
        """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa, v.modelo as veiculo_modelo,
                  m.nome as motorista_nome
           FROM ocorrencias o
           LEFT JOIN oficinas of ON o.oficina_id = of.id
           LEFT JOIN veiculos v ON o.veiculo_id = v.id
           LEFT JOIN motoristas m ON o.motorista_id = m.id
           WHERE o.id=? AND o.empresa_id=?""",
        (ocorrencia_id, g.empresa_id),
    ).fetchone()
    if not oc:
        return jsonify({'erro': 'Ocorrência não encontrada.'}), 404

    orcamentos = db.execute(
        """SELECT o.*, of.nome as oficina_nome,
                  (o.valor_pecas + o.valor_mao_obra) as total
           FROM orcamentos o
           JOIN oficinas of ON o.oficina_id = of.id
           WHERE o.ocorrencia_id=? ORDER BY o.data_envio DESC""",
        (ocorrencia_id,),
    ).fetchall()
    oficinas = db.execute(
        'SELECT * FROM oficinas WHERE ativa=1 ORDER BY nome'
    ).fetchall()
    return jsonify({
        'ocorrencia': row_to_dict(oc),
        'orcamentos': rows_to_list(orcamentos),
        'oficinas': rows_to_list(oficinas),
    })


@ocorrencia_bp.route('/<int:ocorrencia_id>/buscar-oficinas', methods=['GET'])
@login_required
def buscar_oficinas(ocorrencia_id):
    db = get_db()
    oc = db.execute(
        'SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?',
        (ocorrencia_id, g.empresa_id),
    ).fetchone()
    if not oc:
        return jsonify({'erro': 'Ocorrência não encontrada.'}), 404

    raio = request.args.get('raio', type=float)
    oficinas_raw = db.execute('SELECT * FROM oficinas WHERE ativa=1').fetchall()
    oficinas = []
    for of in oficinas_raw:
        of_dict = dict(of)
        if oc['lat'] and oc['lon']:
            try:
                dist = haversine(float(oc['lat']), float(oc['lon']), of['lat'], of['lon'])
                of_dict['distancia'] = round(dist, 1)
            except (TypeError, ValueError):
                of_dict['distancia'] = None
        else:
            of_dict['distancia'] = None
        if raio is not None and of_dict['distancia'] is not None and of_dict['distancia'] > raio:
            continue
        of_dict['aberta_agora'] = oficina_aberta_agora(of['hora_abertura'], of['hora_fechamento'])
        of_dict['atende_tipo'] = oc['tipo_problema'].lower() in (of['especialidades'] or '').lower()
        of_dict['atende_veiculo'] = oc['tipo_veiculo'].lower() in (of['tipos_veiculo'] or '').lower()
        fav = db.execute(
            'SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?',
            (g.empresa_id, of['id']),
        ).fetchone()
        of_dict['favoritada'] = fav is not None
        oficinas.append(of_dict)

    if oc['pane_total']:
        oficinas.sort(key=lambda x: (not x.get('tem_guincho', False), x['distancia'] or 9999))
    else:
        oficinas.sort(key=lambda x: (x['distancia'] or 9999))

    return jsonify({
        'ocorrencia': row_to_dict(oc),
        'oficinas': oficinas,
        'raio': raio,
    })


@ocorrencia_bp.route('/<int:ocorrencia_id>/encerrar', methods=['POST'])
@login_required
def encerrar(ocorrencia_id):
    db = get_db()
    oc = db.execute(
        'SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?',
        (ocorrencia_id, g.empresa_id),
    ).fetchone()
    if not oc:
        return jsonify({'erro': 'Ocorrência não encontrada.'}), 404
    if oc['status'] == STATUS_RESOLVIDO:
        return jsonify({'erro': 'Esta ocorrência já está resolvida.'}), 400

    data = request.get_json(silent=True) or {}
    oficina_id = data.get('oficina_id')
    motivo = data.get('motivo', '')
    observacoes = data.get('observacoes', '')
    if not oficina_id:
        return jsonify({'erro': 'Selecione uma oficina para encerrar a ocorrência.'}), 400

    db.execute(
        """UPDATE ocorrencias SET status=?, oficina_id=?, motivo_resolucao=?,
           observacoes=?, data_encerramento=datetime('now','localtime') WHERE id=?""",
        (STATUS_RESOLVIDO, oficina_id, motivo, observacoes, ocorrencia_id),
    )
    db.commit()
    return jsonify({'mensagem': 'Ocorrência encerrada com status resolvido.'})


@ocorrencia_bp.route('/<int:ocorrencia_id>/status', methods=['PATCH'])
@login_required
def atualizar_status(ocorrencia_id):
    db = get_db()
    data = request.get_json(silent=True) or {}
    novo_status = data.get('status')
    if novo_status not in ['aberta', 'em_atendimento']:
        return jsonify({'erro': 'Status inválido.'}), 400
    db.execute(
        'UPDATE ocorrencias SET status=? WHERE id=? AND empresa_id=?',
        (novo_status, ocorrencia_id, g.empresa_id),
    )
    db.commit()
    return jsonify({'mensagem': 'Status atualizado.'})


@ocorrencia_bp.route('/<int:ocorrencia_id>/vincular-oficina', methods=['POST'])
@login_required
def vincular_oficina(ocorrencia_id):
    db = get_db()
    data = request.get_json(silent=True) or {}
    oficina_id = data.get('oficina_id')
    oc = db.execute(
        'SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?',
        (ocorrencia_id, g.empresa_id),
    ).fetchone()
    if not oc:
        return jsonify({'erro': 'Ocorrência não encontrada.'}), 404
    if not oficina_id:
        return jsonify({'erro': 'Oficina é obrigatória.'}), 400

    db.execute(
        "UPDATE ocorrencias SET oficina_id=?, status='em_atendimento' WHERE id=?",
        (oficina_id, ocorrencia_id),
    )
    db.commit()
    return jsonify({'mensagem': 'Oficina vinculada à ocorrência.'})

from flask import Blueprint, request, jsonify, g
from database import get_db
from auth import login_required
from utils import haversine, oficina_aberta_agora, row_to_dict

oficina_bp = Blueprint('oficinas', __name__, url_prefix='/api/oficinas')


@oficina_bp.route('', methods=['GET'])
@login_required
def listar():
    db = get_db()
    busca = request.args.get('busca', '')
    raio = request.args.get('raio', type=float)
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    query = 'SELECT * FROM oficinas WHERE ativa=1'
    params = []
    if busca:
        query += ' AND (nome LIKE ? OR especialidades LIKE ?)'
        params.extend([f'%{busca}%', f'%{busca}%'])
    query += ' ORDER BY nome'
    oficinas_list = db.execute(query, params).fetchall()

    oficinas_com_fav = []
    for of in oficinas_list:
        of_dict = dict(of)
        fav = db.execute(
            'SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?',
            (g.empresa_id, of['id']),
        ).fetchone()
        of_dict['favoritada'] = fav is not None
        of_dict['aberta_agora'] = oficina_aberta_agora(of['hora_abertura'], of['hora_fechamento'])
        of_dict['distancia'] = None
        if lat is not None and lon is not None and of['lat'] and of['lon']:
            of_dict['distancia'] = round(haversine(lat, lon, of['lat'], of['lon']), 1)
            if raio is not None and of_dict['distancia'] > raio:
                continue
        oficinas_com_fav.append(of_dict)

    if lat is not None and lon is not None:
        oficinas_com_fav.sort(
            key=lambda x: x['distancia'] if x['distancia'] is not None else 9999
        )

    return jsonify({'oficinas': oficinas_com_fav})


@oficina_bp.route('/<int:oficina_id>', methods=['GET'])
@login_required
def detalhe(oficina_id):
    db = get_db()
    of = db.execute('SELECT * FROM oficinas WHERE id=?', (oficina_id,)).fetchone()
    if not of:
        return jsonify({'erro': 'Oficina não encontrada.'}), 404
    fav = db.execute(
        'SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?',
        (g.empresa_id, oficina_id),
    ).fetchone()
    return jsonify({
        'oficina': row_to_dict(of),
        'favoritada': fav is not None,
        'aberta_agora': oficina_aberta_agora(of['hora_abertura'], of['hora_fechamento']),
    })


@oficina_bp.route('/<int:oficina_id>/favoritar', methods=['POST'])
@login_required
def favoritar(oficina_id):
    db = get_db()
    empresa_id = g.empresa_id
    fav = db.execute(
        'SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?',
        (empresa_id, oficina_id),
    ).fetchone()
    if fav:
        db.execute(
            'DELETE FROM favoritos WHERE empresa_id=? AND oficina_id=?',
            (empresa_id, oficina_id),
        )
        favoritada = False
        mensagem = 'Oficina removida dos favoritos.'
    else:
        db.execute(
            'INSERT INTO favoritos (empresa_id, oficina_id) VALUES (?,?)',
            (empresa_id, oficina_id),
        )
        favoritada = True
        mensagem = 'Oficina favoritada.'
    db.commit()
    return jsonify({'mensagem': mensagem, 'favoritada': favoritada})

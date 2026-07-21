from flask import Blueprint, request, jsonify, g
from database import get_db
from auth import login_required, gerar_token
from utils import row_to_dict

perfil_bp = Blueprint('perfil', __name__, url_prefix='/api/perfil')


@perfil_bp.route('', methods=['GET'])
@login_required
def obter():
    db = get_db()
    empresa = db.execute(
        'SELECT id, nome, email, qtd_caminhoes FROM empresas WHERE id=?',
        (g.empresa_id,),
    ).fetchone()
    if not empresa:
        return jsonify({'erro': 'Empresa não encontrada.'}), 404
    return jsonify({'empresa': row_to_dict(empresa)})


@perfil_bp.route('', methods=['PUT'])
@login_required
def atualizar():
    db = get_db()
    data = request.get_json(silent=True) or {}
    empresa = db.execute(
        'SELECT * FROM empresas WHERE id=?', (g.empresa_id,)
    ).fetchone()
    if not empresa:
        return jsonify({'erro': 'Empresa não encontrada.'}), 404

    nome = (data.get('nome') or empresa['nome']).strip()
    qtd_caminhoes = data.get('qtd_caminhoes', empresa['qtd_caminhoes'])
    db.execute(
        'UPDATE empresas SET nome=?, qtd_caminhoes=? WHERE id=?',
        (nome, qtd_caminhoes, g.empresa_id),
    )
    db.commit()
    token = gerar_token(g.empresa_id, nome)
    return jsonify({
        'mensagem': 'Dados atualizados com sucesso.',
        'token': token,
        'empresa': {
            'id': g.empresa_id,
            'nome': nome,
            'email': empresa['email'],
            'qtd_caminhoes': qtd_caminhoes,
        },
    })

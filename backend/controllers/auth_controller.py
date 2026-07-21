from flask import Blueprint, request, jsonify
from database import get_db
from auth import gerar_token, login_required
from utils import row_to_dict

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    data = request.get_json(silent=True) or {}
    nome = (data.get('nome') or '').strip()
    email = (data.get('email') or '').strip().lower()
    senha = data.get('senha') or ''
    qtd_caminhoes = data.get('qtd_caminhoes') or 0

    if not nome or not email or not senha:
        return jsonify({'erro': 'Nome, e-mail e senha são obrigatórios.'}), 400

    db = get_db()
    existing = db.execute('SELECT id FROM empresas WHERE email = ?', (email,)).fetchone()
    if existing:
        return jsonify({'erro': 'Email já cadastrado.'}), 409

    db.execute(
        'INSERT INTO empresas (nome, email, senha, qtd_caminhoes) VALUES (?,?,?,?)',
        (nome, email, senha, qtd_caminhoes),
    )
    db.commit()
    return jsonify({'mensagem': 'Cadastro realizado! Faça login.'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    senha = data.get('senha') or ''

    db = get_db()
    empresa = db.execute(
        'SELECT * FROM empresas WHERE email=? AND senha=?', (email, senha)
    ).fetchone()
    if not empresa:
        return jsonify({'erro': 'Email ou senha incorretos.'}), 401

    token = gerar_token(empresa['id'], empresa['nome'])
    return jsonify({
        'token': token,
        'empresa': {
            'id': empresa['id'],
            'nome': empresa['nome'],
            'email': empresa['email'],
            'qtd_caminhoes': empresa['qtd_caminhoes'],
        },
    })


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    from flask import g
    db = get_db()
    empresa = db.execute(
        'SELECT id, nome, email, qtd_caminhoes FROM empresas WHERE id=?',
        (g.empresa_id,),
    ).fetchone()
    if not empresa:
        return jsonify({'erro': 'Empresa não encontrada.'}), 404
    return jsonify({'empresa': row_to_dict(empresa)})

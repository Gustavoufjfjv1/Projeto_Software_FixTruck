from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import AuthService, ServiceError

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    try:
        resultado = AuthService.cadastrar(request.get_json(silent=True) or {})
        return jsonify(resultado), 201
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        return jsonify(AuthService.login(request.get_json(silent=True) or {}))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    try:
        return jsonify(AuthService.me(g.empresa_id))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status

from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import (
    CadastrarEmpresaService,
    AutenticarEmpresaService,
    ObterEmpresaAutenticadaService,
    RecuperarSenhaService,
    RedefinirSenhaService,
    ServiceError,
)


class AuthController:
    """Controller do recurso Empresa (autenticação e cadastro)."""

    def __init__(self):
        self.bp = Blueprint('auth', __name__, url_prefix='/api/auth')
        self.bp.add_url_rule('/cadastro', view_func=self.cadastrar, methods=['POST'])
        self.bp.add_url_rule('/login', view_func=self.login, methods=['POST'])
        self.bp.add_url_rule('/me', view_func=login_required(self.me), methods=['GET'])
        self.bp.add_url_rule('/recuperar-senha', view_func=self.recuperar_senha, methods=['POST'])
        self.bp.add_url_rule('/redefinir-senha', view_func=self.redefinir_senha, methods=['POST'])

    def cadastrar(self):
        try:
            resultado = CadastrarEmpresaService().executar(request.get_json(silent=True) or {})
            return jsonify(resultado), 201
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def login(self):
        try:
            return jsonify(AutenticarEmpresaService().executar(request.get_json(silent=True) or {}))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def me(self):
        try:
            return jsonify(ObterEmpresaAutenticadaService().executar(g.empresa_id))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def recuperar_senha(self):
        try:
            return jsonify(RecuperarSenhaService().executar(request.get_json(silent=True) or {}))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def redefinir_senha(self):
        try:
            return jsonify(RedefinirSenhaService().executar(request.get_json(silent=True) or {}))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


auth_controller = AuthController()
auth_bp = auth_controller.bp

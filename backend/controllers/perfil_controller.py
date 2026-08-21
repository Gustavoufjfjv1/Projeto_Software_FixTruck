from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import ObterPerfilService, AtualizarPerfilService, ServiceError


class PerfilController:
    """Controller do perfil da Empresa."""

    def __init__(self):
        self.bp = Blueprint('perfil', __name__, url_prefix='/api/perfil')
        self.bp.add_url_rule('', view_func=login_required(self.obter), methods=['GET'])
        self.bp.add_url_rule('', view_func=login_required(self.atualizar), methods=['PUT'])

    def obter(self):
        try:
            return jsonify(ObterPerfilService().executar(g.empresa_id))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def atualizar(self):
        try:
            return jsonify(AtualizarPerfilService().executar(
                g.empresa_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


perfil_controller = PerfilController()
perfil_bp = perfil_controller.bp

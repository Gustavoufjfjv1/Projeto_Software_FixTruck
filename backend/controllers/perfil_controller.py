from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import PerfilService, ServiceError

perfil_bp = Blueprint('perfil', __name__, url_prefix='/api/perfil')


@perfil_bp.route('', methods=['GET'])
@login_required
def obter():
    try:
        return jsonify(PerfilService.obter(g.empresa_id))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@perfil_bp.route('', methods=['PUT'])
@login_required
def atualizar():
    try:
        return jsonify(PerfilService.atualizar(
            g.empresa_id, request.get_json(silent=True) or {}
        ))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status

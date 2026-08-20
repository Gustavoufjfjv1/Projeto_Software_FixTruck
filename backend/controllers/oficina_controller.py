from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import OficinaService, ServiceError

oficina_bp = Blueprint('oficinas', __name__, url_prefix='/api/oficinas')


@oficina_bp.route('', methods=['GET'])
@login_required
def listar():
    return jsonify(OficinaService.listar(
        g.empresa_id,
        busca=request.args.get('busca', ''),
        raio=request.args.get('raio', type=float),
        lat=request.args.get('lat', type=float),
        lon=request.args.get('lon', type=float),
    ))


@oficina_bp.route('/<int:oficina_id>', methods=['GET'])
@login_required
def detalhe(oficina_id):
    try:
        return jsonify(OficinaService.detalhe(g.empresa_id, oficina_id))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@oficina_bp.route('/<int:oficina_id>/favoritar', methods=['POST'])
@login_required
def favoritar(oficina_id):
    return jsonify(OficinaService.favoritar(g.empresa_id, oficina_id))

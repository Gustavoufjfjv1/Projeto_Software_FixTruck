from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import FrotaService, ServiceError

frota_bp = Blueprint('frota', __name__, url_prefix='/api/frota')


@frota_bp.route('', methods=['GET'])
@login_required
def listar():
    return jsonify(FrotaService.listar(g.empresa_id))


@frota_bp.route('/motoristas', methods=['POST'])
@login_required
def novo_motorista():
    try:
        resultado = FrotaService.cadastrar_motorista(
            g.empresa_id, request.get_json(silent=True) or {}
        )
        return jsonify(resultado), 201
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@frota_bp.route('/veiculos', methods=['POST'])
@login_required
def novo_veiculo():
    try:
        resultado = FrotaService.cadastrar_veiculo(
            g.empresa_id, request.get_json(silent=True) or {}
        )
        return jsonify(resultado), 201
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@frota_bp.route('/veiculos/<int:veiculo_id>/vincular', methods=['POST'])
@login_required
def vincular_motorista(veiculo_id):
    try:
        return jsonify(FrotaService.vincular_motorista(
            g.empresa_id, veiculo_id, request.get_json(silent=True) or {}
        ))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status

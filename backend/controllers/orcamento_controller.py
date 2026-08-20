from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import OrcamentoService, ServiceError

orcamento_bp = Blueprint('orcamentos', __name__, url_prefix='/api/orcamentos')


@orcamento_bp.route('', methods=['GET'])
@login_required
def listar():
    return jsonify(OrcamentoService.listar(
        g.empresa_id, request.args.get('status', '')
    ))


@orcamento_bp.route('', methods=['POST'])
@login_required
def enviar():
    try:
        resultado = OrcamentoService.enviar(
            g.empresa_id, request.get_json(silent=True) or {}
        )
        return jsonify(resultado), 201
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@orcamento_bp.route('/<int:orcamento_id>/decidir', methods=['POST'])
@login_required
def decidir(orcamento_id):
    try:
        return jsonify(OrcamentoService.decidir(
            g.empresa_id, orcamento_id, request.get_json(silent=True) or {}
        ))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status

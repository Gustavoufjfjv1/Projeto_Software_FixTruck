from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import OcorrenciaService, ServiceError

ocorrencia_bp = Blueprint('ocorrencias', __name__, url_prefix='/api/ocorrencias')


@ocorrencia_bp.route('', methods=['GET'])
@login_required
def listar():
    filtros = {
        'periodo': request.args.get('periodo', ''),
        'tipo': request.args.get('tipo', ''),
        'veiculo': request.args.get('veiculo', ''),
        'status': request.args.get('status', ''),
    }
    return jsonify(OcorrenciaService.listar(g.empresa_id, filtros))


@ocorrencia_bp.route('/form-data', methods=['GET'])
@login_required
def form_data():
    return jsonify(OcorrenciaService.form_data(g.empresa_id))


@ocorrencia_bp.route('', methods=['POST'])
@login_required
def criar():
    try:
        resultado = OcorrenciaService.criar(
            g.empresa_id, request.get_json(silent=True) or {}
        )
        return jsonify(resultado), 201
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@ocorrencia_bp.route('/<int:ocorrencia_id>', methods=['GET'])
@login_required
def detalhe(ocorrencia_id):
    try:
        return jsonify(OcorrenciaService.detalhe(g.empresa_id, ocorrencia_id))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@ocorrencia_bp.route('/<int:ocorrencia_id>/buscar-oficinas', methods=['GET'])
@login_required
def buscar_oficinas(ocorrencia_id):
    try:
        return jsonify(OcorrenciaService.buscar_oficinas(
            g.empresa_id,
            ocorrencia_id,
            raio=request.args.get('raio', type=float),
        ))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@ocorrencia_bp.route('/<int:ocorrencia_id>/encerrar', methods=['POST'])
@login_required
def encerrar(ocorrencia_id):
    try:
        return jsonify(OcorrenciaService.encerrar(
            g.empresa_id, ocorrencia_id, request.get_json(silent=True) or {}
        ))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@ocorrencia_bp.route('/<int:ocorrencia_id>/status', methods=['PATCH'])
@login_required
def atualizar_status(ocorrencia_id):
    try:
        return jsonify(OcorrenciaService.atualizar_status(
            g.empresa_id, ocorrencia_id, request.get_json(silent=True) or {}
        ))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status


@ocorrencia_bp.route('/<int:ocorrencia_id>/vincular-oficina', methods=['POST'])
@login_required
def vincular_oficina(ocorrencia_id):
    try:
        return jsonify(OcorrenciaService.vincular_oficina(
            g.empresa_id, ocorrencia_id, request.get_json(silent=True) or {}
        ))
    except ServiceError as e:
        return jsonify({'erro': e.mensagem}), e.status

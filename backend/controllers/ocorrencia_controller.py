from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import (
    ListarOcorrenciasService,
    ObterDadosFormularioOcorrenciaService,
    RegistrarOcorrenciaService,
    ObterDetalheOcorrenciaService,
    BuscarOficinasParaOcorrenciaService,
    EncerrarOcorrenciaService,
    AtualizarStatusOcorrenciaService,
    VincularOficinaOcorrenciaService,
    ServiceError,
)


class OcorrenciaController:
    """Controller do recurso Ocorrencia."""

    def __init__(self):
        self.bp = Blueprint('ocorrencias', __name__, url_prefix='/api/ocorrencias')
        self.bp.add_url_rule('', view_func=login_required(self.listar), methods=['GET'])
        self.bp.add_url_rule(
            '/form-data', view_func=login_required(self.form_data), methods=['GET']
        )
        self.bp.add_url_rule('', view_func=login_required(self.criar), methods=['POST'])
        self.bp.add_url_rule(
            '/<int:ocorrencia_id>', view_func=login_required(self.detalhe), methods=['GET']
        )
        self.bp.add_url_rule(
            '/<int:ocorrencia_id>/buscar-oficinas',
            view_func=login_required(self.buscar_oficinas),
            methods=['GET'],
        )
        self.bp.add_url_rule(
            '/<int:ocorrencia_id>/encerrar',
            view_func=login_required(self.encerrar),
            methods=['POST'],
        )
        self.bp.add_url_rule(
            '/<int:ocorrencia_id>/status',
            view_func=login_required(self.atualizar_status),
            methods=['PATCH'],
        )
        self.bp.add_url_rule(
            '/<int:ocorrencia_id>/vincular-oficina',
            view_func=login_required(self.vincular_oficina),
            methods=['POST'],
        )

    def listar(self):
        filtros = {
            'periodo': request.args.get('periodo', ''),
            'tipo': request.args.get('tipo', ''),
            'veiculo': request.args.get('veiculo', ''),
            'status': request.args.get('status', ''),
        }
        return jsonify(ListarOcorrenciasService().executar(g.empresa_id, filtros))

    def form_data(self):
        return jsonify(ObterDadosFormularioOcorrenciaService().executar(g.empresa_id))

    def criar(self):
        try:
            resultado = RegistrarOcorrenciaService().executar(
                g.empresa_id, request.get_json(silent=True) or {}
            )
            return jsonify(resultado), 201
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def detalhe(self, ocorrencia_id):
        try:
            return jsonify(ObterDetalheOcorrenciaService().executar(g.empresa_id, ocorrencia_id))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def buscar_oficinas(self, ocorrencia_id):
        try:
            return jsonify(BuscarOficinasParaOcorrenciaService().executar(
                g.empresa_id,
                ocorrencia_id,
                raio=request.args.get('raio', type=float),
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def encerrar(self, ocorrencia_id):
        try:
            return jsonify(EncerrarOcorrenciaService().executar(
                g.empresa_id, ocorrencia_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def atualizar_status(self, ocorrencia_id):
        try:
            return jsonify(AtualizarStatusOcorrenciaService().executar(
                g.empresa_id, ocorrencia_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def vincular_oficina(self, ocorrencia_id):
        try:
            return jsonify(VincularOficinaOcorrenciaService().executar(
                g.empresa_id, ocorrencia_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


ocorrencia_controller = OcorrenciaController()
ocorrencia_bp = ocorrencia_controller.bp

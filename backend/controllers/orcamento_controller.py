from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import (
    ListarOrcamentosService,
    EnviarOrcamentoService,
    DecidirOrcamentoService,
    ServiceError,
)


class OrcamentoController:
    """Controller do recurso Orcamento."""

    def __init__(self):
        self.bp = Blueprint('orcamentos', __name__, url_prefix='/api/orcamentos')
        self.bp.add_url_rule('', view_func=login_required(self.listar), methods=['GET'])
        self.bp.add_url_rule('', view_func=login_required(self.enviar), methods=['POST'])
        self.bp.add_url_rule(
            '/<int:orcamento_id>/decidir',
            view_func=login_required(self.decidir),
            methods=['POST'],
        )

    def listar(self):
        return jsonify(ListarOrcamentosService().executar(
            g.empresa_id, request.args.get('status', '')
        ))

    def enviar(self):
        try:
            resultado = EnviarOrcamentoService().executar(
                g.empresa_id, request.get_json(silent=True) or {}
            )
            return jsonify(resultado), 201
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def decidir(self, orcamento_id):
        try:
            return jsonify(DecidirOrcamentoService().executar(
                g.empresa_id, orcamento_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


orcamento_controller = OrcamentoController()
orcamento_bp = orcamento_controller.bp

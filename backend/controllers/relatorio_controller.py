from flask import Blueprint, jsonify, g, request
from auth import login_required
from services import GerarRelatorioService, ServiceError


class RelatorioController:
    """Controller de relatórios gerenciais."""

    def __init__(self):
        self.bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')
        self.bp.add_url_rule('', view_func=login_required(self.obter), methods=['GET'])

    def obter(self):
        filtros = {
            'periodo': request.args.get('periodo', ''),
            'data_inicio': request.args.get('data_inicio', ''),
            'data_fim': request.args.get('data_fim', ''),
        }
        try:
            return jsonify(GerarRelatorioService().executar(g.empresa_id, filtros))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


relatorio_controller = RelatorioController()
relatorio_bp = relatorio_controller.bp

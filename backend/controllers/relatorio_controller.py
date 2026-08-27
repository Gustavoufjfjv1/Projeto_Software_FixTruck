from flask import Blueprint, jsonify, g, request
from auth import login_required
from services import GerarRelatorioService


class RelatorioController:
    """Controller de relatórios gerenciais."""

    def __init__(self):
        self.bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')
        self.bp.add_url_rule('', view_func=login_required(self.obter), methods=['GET'])

    def obter(self):
        periodo = request.args.get('periodo', '')
        return jsonify(GerarRelatorioService().executar(g.empresa_id, periodo))


relatorio_controller = RelatorioController()
relatorio_bp = relatorio_controller.bp

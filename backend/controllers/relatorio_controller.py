from flask import Blueprint, jsonify, g, request, make_response
from auth import login_required
from services import FiltrarRelatorioService, GerarRelatorioCsvService, ServiceError


class RelatorioController:
    """Controller de relatórios gerenciais."""

    def __init__(self):
        self.bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')
        self.bp.add_url_rule('', view_func=login_required(self.obter), methods=['GET'])
        self.bp.add_url_rule(
            '/exportar', view_func=login_required(self.exportar_csv), methods=['GET']
        )

    def obter(self):
        periodo = request.args.get('periodo', '')
        status = request.args.get('status', '')
        try:
            return jsonify(
                FiltrarRelatorioService().executar(g.empresa_id, periodo, status)
            )
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def exportar_csv(self):
        try:
            csv_texto = GerarRelatorioCsvService().executar(
                g.empresa_id,
                request.args.get('periodo', ''),
                request.args.get('status', ''),
            )
            response = make_response(csv_texto)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = (
                'attachment; filename="relatorio-fixtruck.csv"'
            )
            return response
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


relatorio_controller = RelatorioController()
relatorio_bp = relatorio_controller.bp

from flask import Blueprint, jsonify, g
from auth import login_required
from services import ObterDashboardService


class DashboardController:
    """Controller do dashboard gerencial."""

    def __init__(self):
        self.bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
        self.bp.add_url_rule('', view_func=login_required(self.obter), methods=['GET'])

    def obter(self):
        return jsonify(ObterDashboardService().executar(g.empresa_id))


dashboard_controller = DashboardController()
dashboard_bp = dashboard_controller.bp

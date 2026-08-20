from flask import Blueprint, jsonify, g
from auth import login_required
from services import DashboardService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('', methods=['GET'])
@login_required
def dashboard():
    return jsonify(DashboardService.obter(g.empresa_id))

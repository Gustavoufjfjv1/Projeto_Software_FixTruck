from flask import Blueprint, jsonify, g
from auth import login_required
from services import RelatorioService

relatorio_bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')


@relatorio_bp.route('', methods=['GET'])
@login_required
def relatorios():
    return jsonify(RelatorioService.obter(g.empresa_id))

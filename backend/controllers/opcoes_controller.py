from flask import Blueprint, jsonify
from constantes import opcoes_publicas


class OpcoesController:
    """Listas de valores aceitos (tipos de problema, veículo, dias, UFs) para os formulários."""

    def __init__(self):
        self.bp = Blueprint('opcoes', __name__, url_prefix='/api/opcoes')
        self.bp.add_url_rule('', view_func=self.listar, methods=['GET'])

    def listar(self):
        return jsonify(opcoes_publicas())


opcoes_controller = OpcoesController()
opcoes_bp = opcoes_controller.bp

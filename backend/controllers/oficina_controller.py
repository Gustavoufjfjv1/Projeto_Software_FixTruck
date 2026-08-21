from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import (
    ListarOficinasService,
    ObterDetalheOficinaService,
    FavoritarOficinaService,
    ServiceError,
)


class OficinaController:
    """Controller do recurso Oficina."""

    def __init__(self):
        self.bp = Blueprint('oficinas', __name__, url_prefix='/api/oficinas')
        self.bp.add_url_rule('', view_func=login_required(self.listar), methods=['GET'])
        self.bp.add_url_rule(
            '/<int:oficina_id>', view_func=login_required(self.detalhe), methods=['GET']
        )
        self.bp.add_url_rule(
            '/<int:oficina_id>/favoritar',
            view_func=login_required(self.favoritar),
            methods=['POST'],
        )

    def listar(self):
        return jsonify(ListarOficinasService().executar(
            g.empresa_id,
            busca=request.args.get('busca', ''),
            raio=request.args.get('raio', type=float),
            lat=request.args.get('lat', type=float),
            lon=request.args.get('lon', type=float),
        ))

    def detalhe(self, oficina_id):
        try:
            return jsonify(ObterDetalheOficinaService().executar(g.empresa_id, oficina_id))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def favoritar(self, oficina_id):
        return jsonify(FavoritarOficinaService().executar(g.empresa_id, oficina_id))


oficina_controller = OficinaController()
oficina_bp = oficina_controller.bp

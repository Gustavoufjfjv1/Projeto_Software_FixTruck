from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import (
    ListarFrotaService,
    CadastrarMotoristaService,
    CadastrarVeiculoService,
    VincularMotoristaVeiculoService,
    DefinirAcessoMotoristaService,
    ServiceError,
)


class FrotaController:
    """Controller dos recursos Motorista e Veículo (frota)."""

    def __init__(self):
        self.bp = Blueprint('frota', __name__, url_prefix='/api/frota')
        self.bp.add_url_rule('', view_func=login_required(self.listar), methods=['GET'])
        self.bp.add_url_rule(
            '/motoristas', view_func=login_required(self.cadastrar_motorista), methods=['POST']
        )
        self.bp.add_url_rule(
            '/veiculos', view_func=login_required(self.cadastrar_veiculo), methods=['POST']
        )
        self.bp.add_url_rule(
            '/veiculos/<int:veiculo_id>/vincular',
            view_func=login_required(self.vincular_motorista),
            methods=['POST'],
        )
        self.bp.add_url_rule(
            '/motoristas/<int:motorista_id>/acesso',
            view_func=login_required(self.definir_acesso),
            methods=['POST'],
        )

    def listar(self):
        return jsonify(ListarFrotaService().executar(g.empresa_id))

    def cadastrar_motorista(self):
        try:
            resultado = CadastrarMotoristaService().executar(
                g.empresa_id, request.get_json(silent=True) or {}
            )
            return jsonify(resultado), 201
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def cadastrar_veiculo(self):
        try:
            resultado = CadastrarVeiculoService().executar(
                g.empresa_id, request.get_json(silent=True) or {}
            )
            return jsonify(resultado), 201
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def definir_acesso(self, motorista_id):
        try:
            return jsonify(DefinirAcessoMotoristaService().executar(
                g.empresa_id, motorista_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def vincular_motorista(self, veiculo_id):
        try:
            return jsonify(VincularMotoristaVeiculoService().executar(
                g.empresa_id, veiculo_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


frota_controller = FrotaController()
frota_bp = frota_controller.bp

from flask import Blueprint, request, jsonify, g
from auth import login_required
from services import (
    ListarFrotaService,
    BuscarMotoristasService,
    CadastrarMotoristaService,
    AtualizarMotoristaService,
    InativarMotoristaService,
    ReativarMotoristaService,
    ExcluirMotoristaService,
    CadastrarVeiculoService,
    AtualizarVeiculoService,
    ExcluirVeiculoService,
    VincularMotoristaVeiculoService,
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
            '/motoristas', view_func=login_required(self.buscar_motoristas), methods=['GET']
        )
        self.bp.add_url_rule(
            '/motoristas/<int:motorista_id>',
            view_func=login_required(self.atualizar_motorista),
            methods=['PUT'],
        )
        self.bp.add_url_rule(
            '/motoristas/<int:motorista_id>/inativar',
            view_func=login_required(self.inativar_motorista),
            methods=['PATCH'],
        )
        self.bp.add_url_rule(
            '/motoristas/<int:motorista_id>/reativar',
            view_func=login_required(self.reativar_motorista),
            methods=['PATCH'],
        )
        self.bp.add_url_rule(
            '/motoristas/<int:motorista_id>',
            view_func=login_required(self.excluir_motorista),
            methods=['DELETE'],
        )
        self.bp.add_url_rule(
            '/veiculos', view_func=login_required(self.cadastrar_veiculo), methods=['POST']
        )
        self.bp.add_url_rule(
            '/veiculos/<int:veiculo_id>',
            view_func=login_required(self.atualizar_veiculo),
            methods=['PUT'],
        )
        self.bp.add_url_rule(
            '/veiculos/<int:veiculo_id>',
            view_func=login_required(self.excluir_veiculo),
            methods=['DELETE'],
        )
        self.bp.add_url_rule(
            '/veiculos/<int:veiculo_id>/vincular',
            view_func=login_required(self.vincular_motorista),
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

    def buscar_motoristas(self):
        try:
            return jsonify({'motoristas': BuscarMotoristasService().executar(
                g.empresa_id, request.args.get('busca', '')
            )})
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def atualizar_motorista(self, motorista_id):
        try:
            return jsonify(AtualizarMotoristaService().executar(
                g.empresa_id, motorista_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def inativar_motorista(self, motorista_id):
        try:
            return jsonify(InativarMotoristaService().executar(g.empresa_id, motorista_id))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def reativar_motorista(self, motorista_id):
        try:
            return jsonify(ReativarMotoristaService().executar(g.empresa_id, motorista_id))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def excluir_motorista(self, motorista_id):
        try:
            return jsonify(ExcluirMotoristaService().executar(g.empresa_id, motorista_id))
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

    def atualizar_veiculo(self, veiculo_id):
        try:
            return jsonify(AtualizarVeiculoService().executar(
                g.empresa_id, veiculo_id, request.get_json(silent=True) or {}
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def excluir_veiculo(self, veiculo_id):
        try:
            return jsonify(ExcluirVeiculoService().executar(g.empresa_id, veiculo_id))
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

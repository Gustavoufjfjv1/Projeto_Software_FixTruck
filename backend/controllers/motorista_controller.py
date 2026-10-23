from flask import Blueprint, request, jsonify, g
from auth import motorista_required
from services import (
    AutenticarMotoristaService,
    TrocarSenhaMotoristaService,
    ObterPainelMotoristaService,
    ObterOcorrenciaMotoristaService,
    RegistrarOcorrenciaService,
    buscar_ocorrencia_do_motorista,
    buscar_oficinas_compativeis,
    ServiceError,
)
from constantes import opcoes_publicas
from repositories import VeiculoRepository


class MotoristaController:
    """Área do motorista: login próprio, registro e acompanhamento das suas ocorrências."""

    def __init__(self):
        self.bp = Blueprint('motorista', __name__, url_prefix='/api/motorista')
        self.bp.add_url_rule('/login', view_func=self.login, methods=['POST'])
        self.bp.add_url_rule(
            '/me', view_func=motorista_required(self.me, permitir_troca_pendente=True), methods=['GET']
        )
        self.bp.add_url_rule(
            '/trocar-senha',
            view_func=motorista_required(self.trocar_senha, permitir_troca_pendente=True),
            methods=['POST'],
        )
        self.bp.add_url_rule('/form-data', view_func=motorista_required(self.form_data), methods=['GET'])
        self.bp.add_url_rule('/ocorrencias', view_func=motorista_required(self.listar), methods=['GET'])
        self.bp.add_url_rule('/ocorrencias', view_func=motorista_required(self.criar), methods=['POST'])
        self.bp.add_url_rule(
            '/ocorrencias/<int:ocorrencia_id>', view_func=motorista_required(self.detalhe), methods=['GET']
        )
        self.bp.add_url_rule(
            '/ocorrencias/<int:ocorrencia_id>/buscar-oficinas',
            view_func=motorista_required(self.buscar_oficinas),
            methods=['GET'],
        )

    def login(self):
        try:
            return jsonify(AutenticarMotoristaService().executar(request.get_json(silent=True) or {}))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def me(self):
        return jsonify({'motorista': g.motorista.to_dict_publico()})

    def trocar_senha(self):
        try:
            return jsonify(TrocarSenhaMotoristaService().executar(g.motorista, request.get_json(silent=True) or {}))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def form_data(self):
        dados = opcoes_publicas()
        dados['veiculos'] = VeiculoRepository.listar_do_motorista(g.motorista_id, g.empresa_id)
        return jsonify(dados)

    def listar(self):
        apenas_abertas = request.args.get('status') == 'abertas'
        return jsonify(ObterPainelMotoristaService().executar(g.motorista, apenas_abertas=apenas_abertas))

    def criar(self):
        try:
            resultado = RegistrarOcorrenciaService().executar(
                g.empresa_id, request.get_json(silent=True) or {}, motorista=g.motorista
            )
            return jsonify(resultado), 201
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def detalhe(self, ocorrencia_id):
        try:
            return jsonify(ObterOcorrenciaMotoristaService().executar(g.motorista, ocorrencia_id))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status

    def buscar_oficinas(self, ocorrencia_id):
        try:
            oc = buscar_ocorrencia_do_motorista(g.motorista, ocorrencia_id)
            return jsonify(buscar_oficinas_compativeis(
                g.empresa_id, oc,
                raio=request.args.get('raio', type=float),
                janela=request.args.get('janela', type=int),
            ))
        except ServiceError as e:
            return jsonify({'erro': e.mensagem}), e.status


motorista_controller = MotoristaController()
motorista_bp = motorista_controller.bp

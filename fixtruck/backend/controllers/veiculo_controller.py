"""Controller de Veículos"""

from flask import Blueprint, request, jsonify
from services.veiculo_service import VeiculoService

veiculo_bp = Blueprint('veiculos', __name__)
veiculo_service = VeiculoService()


@veiculo_bp.route('/', methods=['POST'])
def criar_veiculo():
    """Cria um novo veículo"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['placa', 'modelo', 'marca', 'tipo_veiculo', 'id_empresa']):
            return jsonify({'erro': 'Dados obrigatórios faltando'}), 400
        
        veiculo = veiculo_service.criar_veiculo(dados)
        
        return jsonify({'mensagem': 'Veículo criado com sucesso', 'veiculo': veiculo}), 201
    
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro ao criar veículo'}), 500


@veiculo_bp.route('/<int:id_veiculo>', methods=['GET'])
def obter_veiculo(id_veiculo):
    """Obtém informações de um veículo específico"""
    try:
        veiculo = veiculo_service.obter_veiculo(id_veiculo)
        
        if veiculo:
            return jsonify(veiculo), 200
        else:
            return jsonify({'erro': 'Veículo não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter veículo'}), 500


@veiculo_bp.route('/', methods=['GET'])
def listar_veiculos():
    """Lista veículos com filtros opcionais"""
    try:
        id_empresa = request.args.get('id_empresa')
        veiculos = veiculo_service.listar_veiculos(id_empresa=id_empresa)
        
        return jsonify(veiculos), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao listar veículos'}), 500


@veiculo_bp.route('/<int:id_veiculo>/historico-ocorrencias', methods=['GET'])
def obter_historico_ocorrencias(id_veiculo):
    """Obtém o histórico de ocorrências de um veículo"""
    try:
        limite = request.args.get('limite', type=int)
        ocorrencias = veiculo_service.obter_historico_ocorrencias(id_veiculo, limite)
        
        if ocorrencias is not None:
            return jsonify(ocorrencias), 200
        else:
            return jsonify({'erro': 'Veículo não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter histórico'}), 500


@veiculo_bp.route('/<int:id_veiculo>', methods=['PUT'])
def atualizar_veiculo(id_veiculo):
    """Atualiza informações de um veículo"""
    try:
        dados = request.get_json()
        
        veiculo = veiculo_service.atualizar_veiculo(id_veiculo, dados)
        
        if veiculo:
            return jsonify({'mensagem': 'Veículo atualizado com sucesso', 'veiculo': veiculo}), 200
        else:
            return jsonify({'erro': 'Veículo não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao atualizar veículo'}), 500

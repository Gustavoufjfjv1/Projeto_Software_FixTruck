"""Controller de Orçamentos"""

from flask import Blueprint, request, jsonify
from services.orcamento_service import OrcamentoService

orcamento_bp = Blueprint('orcamentos', __name__)
orcamento_service = OrcamentoService()


@orcamento_bp.route('/', methods=['POST'])
def criar_orcamento():
    """Cria um novo orçamento"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['id_ocorrencia', 'id_oficina', 'valor_pecas', 'valor_mao_obra']):
            return jsonify({'erro': 'Dados obrigatórios faltando'}), 400
        
        orcamento = orcamento_service.criar_orcamento(dados)
        
        return jsonify({'mensagem': 'Orçamento criado com sucesso', 'orcamento': orcamento}), 201
    
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro ao criar orçamento'}), 500


@orcamento_bp.route('/<int:id_orcamento>', methods=['GET'])
def obter_orcamento(id_orcamento):
    """Obtém detalhes de um orçamento específico"""
    try:
        orcamento = orcamento_service.obter_orcamento(id_orcamento)
        
        if orcamento:
            return jsonify(orcamento), 200
        else:
            return jsonify({'erro': 'Orçamento não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter orçamento'}), 500


@orcamento_bp.route('/ocorrencia/<int:id_ocorrencia>', methods=['GET'])
def listar_orcamentos_ocorrencia(id_ocorrencia):
    """Lista todos os orçamentos de uma ocorrência"""
    try:
        orcamentos = orcamento_service.listar_orcamentos(id_ocorrencia=id_ocorrencia)
        
        return jsonify(orcamentos), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao listar orçamentos'}), 500


@orcamento_bp.route('/<int:id_orcamento>/aprovar', methods=['PUT'])
def aprovar_orcamento(id_orcamento):
    """Aprova um orçamento"""
    try:
        orcamento = orcamento_service.aprovar_orcamento(id_orcamento)
        
        if orcamento:
            return jsonify({'mensagem': 'Orçamento aprovado com sucesso', 'orcamento': orcamento}), 200
        else:
            return jsonify({'erro': 'Orçamento não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao aprovar orçamento'}), 500


@orcamento_bp.route('/<int:id_orcamento>/rejeitar', methods=['PUT'])
def rejeitar_orcamento(id_orcamento):
    """Rejeita um orçamento"""
    try:
        dados = request.get_json() or {}
        
        orcamento = orcamento_service.rejeitar_orcamento(
            id_orcamento,
            observacoes=dados.get('observacoes')
        )
        
        if orcamento:
            return jsonify({'mensagem': 'Orçamento rejeitado com sucesso', 'orcamento': orcamento}), 200
        else:
            return jsonify({'erro': 'Orçamento não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao rejeitar orçamento'}), 500

"""Controller de Chat"""

from flask import Blueprint, request, jsonify
from services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()


@chat_bp.route('/<int:id_ocorrencia>/mensagens', methods=['POST'])
def enviar_mensagem(id_ocorrencia):
    """Envia uma mensagem em uma ocorrência"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['id_usuario', 'texto']):
            return jsonify({'erro': 'ID do usuário e texto são obrigatórios'}), 400
        
        mensagem = chat_service.enviar_mensagem(
            id_ocorrencia,
            dados['id_usuario'],
            dados['texto'],
            url_foto_evidencia=dados.get('url_foto_evidencia')
        )
        
        return jsonify({'mensagem': 'Mensagem enviada com sucesso', 'dados': mensagem}), 201
    
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro ao enviar mensagem'}), 500


@chat_bp.route('/<int:id_ocorrencia>/mensagens', methods=['GET'])
def obter_mensagens(id_ocorrencia):
    """Obtém todas as mensagens de uma ocorrência"""
    try:
        mensagens = chat_service.obter_mensagens(id_ocorrencia)
        
        return jsonify(mensagens), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter mensagens'}), 500


@chat_bp.route('/<int:id_ocorrencia>/historico', methods=['GET'])
def obter_historico_chat(id_ocorrencia):
    """Obtém o histórico completo de chat de uma ocorrência"""
    try:
        limite = request.args.get('limite', type=int)
        historico = chat_service.obter_historico(id_ocorrencia, limite)
        
        return jsonify(historico), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter histórico'}), 500

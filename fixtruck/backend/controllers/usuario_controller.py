"""Controller de Usuários"""

from flask import Blueprint, request, jsonify
from services.usuario_service import UsuarioService

usuario_bp = Blueprint('usuarios', __name__)
usuario_service = UsuarioService()


@usuario_bp.route('/<int:id_usuario>', methods=['GET'])
def obter_usuario(id_usuario):
    """Obtém informações de um usuário específico"""
    try:
        usuario = usuario_service.obter_usuario(id_usuario)
        
        if usuario:
            return jsonify(usuario), 200
        else:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter usuário'}), 500


@usuario_bp.route('/', methods=['GET'])
def listar_usuarios():
    """Lista todos os usuários (com filtros opcionais)"""
    try:
        tipo_usuario = request.args.get('tipo_usuario')
        usuarios = usuario_service.listar_usuarios(tipo_usuario=tipo_usuario)
        
        return jsonify(usuarios), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao listar usuários'}), 500


@usuario_bp.route('/<int:id_usuario>', methods=['PUT'])
def atualizar_usuario(id_usuario):
    """Atualiza informações de um usuário"""
    try:
        dados = request.get_json()
        
        usuario = usuario_service.atualizar_usuario(id_usuario, dados)
        
        if usuario:
            return jsonify({'mensagem': 'Usuário atualizado com sucesso', 'usuario': usuario}), 200
        else:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao atualizar usuário'}), 500


@usuario_bp.route('/<int:id_usuario>', methods=['DELETE'])
def deletar_usuario(id_usuario):
    """Deleta um usuário"""
    try:
        sucesso = usuario_service.deletar_usuario(id_usuario)
        
        if sucesso:
            return jsonify({'mensagem': 'Usuário deletado com sucesso'}), 200
        else:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao deletar usuário'}), 500

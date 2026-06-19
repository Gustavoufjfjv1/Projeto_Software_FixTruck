"""Controller de Autenticação"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/registrar', methods=['POST'])
def registrar():
    """Registra um novo usuário (gestor ou motorista)"""
    try:
        dados = request.get_json()
        
        # Validar dados obrigatórios
        if not dados or not all(k in dados for k in ['nome', 'email', 'senha', 'tipo_usuario']):
            return jsonify({'erro': 'Dados obrigatórios faltando'}), 400
        
        usuario = auth_service.registrar_usuario(
            nome=dados['nome'],
            email=dados['email'],
            senha=dados['senha'],
            tipo_usuario=dados['tipo_usuario'],
            **dados.get('dados_adicionais', {})
        )
        
        return jsonify({'mensagem': 'Usuário registrado com sucesso', 'usuario': usuario.to_dict()}), 201
    
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro ao registrar usuário'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['email', 'senha']):
            return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
        
        resultado = auth_service.autenticar(dados['email'], dados['senha'])
        
        if resultado:
            return jsonify({
                'mensagem': 'Login realizado com sucesso',
                'usuario': resultado['usuario'],
                'token': resultado['token']
            }), 200
        else:
            return jsonify({'erro': 'Email ou senha inválidos'}), 401
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao realizar login'}), 500


@auth_bp.route('/alterar-senha', methods=['POST'])
def alterar_senha():
    """Altera a senha do usuário autenticado"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['id_usuario', 'senha_atual', 'senha_nova']):
            return jsonify({'erro': 'Dados obrigatórios faltando'}), 400
        
        sucesso = auth_service.alterar_senha(
            dados['id_usuario'],
            dados['senha_atual'],
            dados['senha_nova']
        )
        
        if sucesso:
            return jsonify({'mensagem': 'Senha alterada com sucesso'}), 200
        else:
            return jsonify({'erro': 'Não foi possível alterar a senha'}), 400
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao alterar senha'}), 500

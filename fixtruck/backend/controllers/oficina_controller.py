"""Controller de Oficinas"""

from flask import Blueprint, request, jsonify
from services.oficina_service import OficinaService

oficina_bp = Blueprint('oficinas', __name__)
oficina_service = OficinaService()


@oficina_bp.route('/', methods=['POST'])
def criar_oficina():
    """Cria uma nova oficina"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['nome_fantasia', 'latitude', 'longitude']):
            return jsonify({'erro': 'Dados obrigatórios faltando'}), 400
        
        oficina = oficina_service.criar_oficina(dados)
        
        return jsonify({'mensagem': 'Oficina criada com sucesso', 'oficina': oficina}), 201
    
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro ao criar oficina'}), 500


@oficina_bp.route('/<int:id_oficina>', methods=['GET'])
def obter_oficina(id_oficina):
    """Obtém informações de uma oficina específica"""
    try:
        oficina = oficina_service.obter_oficina(id_oficina)
        
        if oficina:
            return jsonify(oficina), 200
        else:
            return jsonify({'erro': 'Oficina não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter oficina'}), 500


@oficina_bp.route('/buscar-por-raio', methods=['POST'])
def buscar_por_raio():
    """Busca oficinas em um raio de distância"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['latitude', 'longitude', 'raio_km']):
            return jsonify({'erro': 'Latitude, longitude e raio são obrigatórios'}), 400
        
        oficinas = oficina_service.buscar_por_raio(
            dados['latitude'],
            dados['longitude'],
            dados['raio_km'],
            especialidade=dados.get('especialidade'),
            possui_guincho=dados.get('possui_guincho', False)
        )
        
        return jsonify(oficinas), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao buscar oficinas'}), 500


@oficina_bp.route('/', methods=['GET'])
def listar_oficinas():
    """Lista todas as oficinas com filtros opcionais"""
    try:
        ativo = request.args.get('ativo', type=lambda x: x.lower() in ['true', '1', 'yes'])
        especialidade = request.args.get('especialidade')
        
        oficinas = oficina_service.listar_oficinas(ativo=ativo, especialidade=especialidade)
        
        return jsonify(oficinas), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao listar oficinas'}), 500


@oficina_bp.route('/<int:id_oficina>', methods=['PUT'])
def atualizar_oficina(id_oficina):
    """Atualiza informações de uma oficina"""
    try:
        dados = request.get_json()
        
        oficina = oficina_service.atualizar_oficina(id_oficina, dados)
        
        if oficina:
            return jsonify({'mensagem': 'Oficina atualizada com sucesso', 'oficina': oficina}), 200
        else:
            return jsonify({'erro': 'Oficina não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao atualizar oficina'}), 500


@oficina_bp.route('/<int:id_oficina>/status', methods=['PUT'])
def atualizar_status_atendimento(id_oficina):
    """Atualiza o status de atendimento de uma oficina"""
    try:
        dados = request.get_json()
        
        if not dados or 'status' not in dados:
            return jsonify({'erro': 'Status é obrigatório'}), 400
        
        sucesso = oficina_service.atualizar_status_atendimento(id_oficina, dados['status'])
        
        if sucesso:
            return jsonify({'mensagem': 'Status atualizado com sucesso'}), 200
        else:
            return jsonify({'erro': 'Oficina não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao atualizar status'}), 500

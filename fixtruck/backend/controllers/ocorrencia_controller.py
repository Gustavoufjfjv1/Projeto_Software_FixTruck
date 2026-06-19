"""Controller de Ocorrências"""

from flask import Blueprint, request, jsonify
from services.ocorrencia_service import OcorrenciaService

ocorrencia_bp = Blueprint('ocorrencias', __name__)
ocorrencia_service = OcorrenciaService()


@ocorrencia_bp.route('/', methods=['POST'])
def criar_ocorrencia():
    """Cria uma nova ocorrência"""
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ['id_veiculo', 'tipo_problema', 'latitude', 'longitude']):
            return jsonify({'erro': 'Dados obrigatórios faltando'}), 400
        
        ocorrencia = ocorrencia_service.criar_ocorrencia(dados)
        
        return jsonify({'mensagem': 'Ocorrência registrada com sucesso', 'ocorrencia': ocorrencia}), 201
    
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro ao criar ocorrência'}), 500


@ocorrencia_bp.route('/<int:id_ocorrencia>', methods=['GET'])
def obter_ocorrencia(id_ocorrencia):
    """Obtém detalhes de uma ocorrência específica"""
    try:
        ocorrencia = ocorrencia_service.obter_ocorrencia(id_ocorrencia)
        
        if ocorrencia:
            return jsonify(ocorrencia), 200
        else:
            return jsonify({'erro': 'Ocorrência não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao obter ocorrência'}), 500


@ocorrencia_bp.route('/', methods=['GET'])
def listar_ocorrencias():
    """Lista ocorrências com filtros opcionais"""
    try:
        status = request.args.get('status')
        id_veiculo = request.args.get('id_veiculo', type=int)
        id_oficina = request.args.get('id_oficina', type=int)
        
        ocorrencias = ocorrencia_service.listar_ocorrencias(
            status=status,
            id_veiculo=id_veiculo,
            id_oficina=id_oficina
        )
        
        return jsonify(ocorrencias), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao listar ocorrências'}), 500


@ocorrencia_bp.route('/<int:id_ocorrencia>/vincular-oficina', methods=['PUT'])
def vincular_oficina(id_ocorrencia):
    """Vincula uma oficina a uma ocorrência"""
    try:
        dados = request.get_json()
        
        if not dados or 'id_oficina' not in dados:
            return jsonify({'erro': 'ID da oficina é obrigatório'}), 400
        
        ocorrencia = ocorrencia_service.vincular_oficina(id_ocorrencia, dados['id_oficina'])
        
        if ocorrencia:
            return jsonify({'mensagem': 'Oficina vinculada com sucesso', 'ocorrencia': ocorrencia}), 200
        else:
            return jsonify({'erro': 'Ocorrência ou oficina não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao vincular oficina'}), 500


@ocorrencia_bp.route('/<int:id_ocorrencia>/encerrar', methods=['PUT'])
def encerrar_ocorrencia(id_ocorrencia):
    """Encerra uma ocorrência"""
    try:
        dados = request.get_json()
        
        if not dados or 'motivo_resolucao' not in dados:
            return jsonify({'erro': 'Motivo da resolução é obrigatório'}), 400
        
        ocorrencia = ocorrencia_service.encerrar_ocorrencia(
            id_ocorrencia,
            dados['motivo_resolucao'],
            dados.get('observacao', '')
        )
        
        if ocorrencia:
            return jsonify({'mensagem': 'Ocorrência encerrada com sucesso', 'ocorrencia': ocorrencia}), 200
        else:
            return jsonify({'erro': 'Ocorrência não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao encerrar ocorrência'}), 500


@ocorrencia_bp.route('/<int:id_ocorrencia>/downtime', methods=['GET'])
def obter_downtime(id_ocorrencia):
    """Obtém o tempo de inatividade de uma ocorrência"""
    try:
        downtime = ocorrencia_service.obter_downtime(id_ocorrencia)
        
        if downtime is not None:
            return jsonify({'id_ocorrencia': id_ocorrencia, 'downtime_horas': downtime}), 200
        else:
            return jsonify({'erro': 'Ocorrência não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao calcular downtime'}), 500

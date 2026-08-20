from models import Motorista, Veiculo
from services.erros import ServiceError


class FrotaService:
    @staticmethod
    def listar(empresa_id):
        return {
            'veiculos': Veiculo.listar_por_empresa(empresa_id),
            'motoristas': Motorista.listar_com_veiculo(empresa_id),
        }

    @staticmethod
    def cadastrar_motorista(empresa_id, dados):
        nome = (dados.get('nome') or '').strip()
        if not nome:
            raise ServiceError('Nome do motorista é obrigatório.', 400)
        Motorista.cadastrar({
            'empresa_id': empresa_id,
            'nome': nome,
            'cnh': dados.get('cnh', ''),
            'telefone': dados.get('telefone', ''),
        })
        return {'mensagem': 'Motorista cadastrado.'}

    @staticmethod
    def cadastrar_veiculo(empresa_id, dados):
        placa = (dados.get('placa') or '').strip().upper()
        if not placa:
            raise ServiceError('Placa é obrigatória.', 400)
        Veiculo.cadastrar({
            'empresa_id': empresa_id,
            'placa': placa,
            'modelo': dados.get('modelo', ''),
            'marca': dados.get('marca', ''),
            'tipo_veiculo': dados.get('tipo_veiculo', 'pesado'),
            'motorista_id': dados.get('motorista_id') or None,
        })
        return {'mensagem': 'Veículo cadastrado na frota.'}

    @staticmethod
    def vincular_motorista(empresa_id, veiculo_id, dados):
        veiculo = Veiculo.buscar_da_empresa(veiculo_id, empresa_id)
        if not veiculo:
            raise ServiceError('Veículo não encontrado.', 404)

        motorista_id = dados.get('motorista_id') or None
        if motorista_id:
            mot = Motorista.buscar_da_empresa(motorista_id, empresa_id)
            if not mot:
                raise ServiceError('Motorista inválido.', 400)

        Veiculo.vincular_motorista(veiculo_id, motorista_id)
        return {'mensagem': 'Motorista vinculado ao veículo da frota.'}

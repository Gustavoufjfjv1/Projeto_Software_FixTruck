from repositories import VeiculoRepository, MotoristaRepository
from services.erros import ServiceError


class VincularMotoristaVeiculoService:
    def executar(self, empresa_id, veiculo_id, dados):
        veiculo = VeiculoRepository.buscar_da_empresa(veiculo_id, empresa_id)
        if not veiculo:
            raise ServiceError('Veículo não encontrado.', 404)

        motorista_id = dados.get('motorista_id') or None
        if motorista_id:
            mot = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
            if not mot:
                raise ServiceError('Motorista inválido.', 400)

        veiculo.motorista_id = motorista_id
        veiculo.atualizar()
        return {'mensagem': 'Motorista vinculado ao veículo da frota.'}

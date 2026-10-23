from repositories import VeiculoRepository
from services import posse
from services.erros import ServiceError


class VincularMotoristaVeiculoService:
    def executar(self, empresa_id, veiculo_id, dados):
        veiculo = VeiculoRepository.buscar_da_empresa(veiculo_id, empresa_id)
        if not veiculo:
            raise ServiceError('Veículo não encontrado.', 404)
        motorista = posse.motorista_da_empresa(dados.get('motorista_id'), empresa_id)
        veiculo.motorista_id = motorista.id if motorista else None
        veiculo.atualizar()
        return {'mensagem': 'Motorista vinculado ao veículo da frota.'}

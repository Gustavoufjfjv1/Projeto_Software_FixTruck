from repositories import MotoristaRepository
from services.erros import ServiceError


class ReativarMotoristaService:
    def executar(self, empresa_id, motorista_id):
        motorista = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
        if not motorista:
            raise ServiceError('Motorista não encontrado.', 404)
        if motorista.ativo != 0:
            raise ServiceError('Este motorista já está ativo.', 400)
        motorista.ativo = 1
        motorista.atualizar()
        return {'mensagem': 'Motorista reativado.'}

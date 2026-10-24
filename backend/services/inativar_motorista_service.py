from models import Veiculo
from repositories import MotoristaRepository
from services.erros import ServiceError


class InativarMotoristaService:
    def executar(self, empresa_id, motorista_id):
        motorista = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
        if not motorista:
            raise ServiceError('Motorista não encontrado.', 404)
        if motorista.ativo == 0:
            raise ServiceError('Este motorista já está inativo.', 400)
        vinculo = Veiculo.query.filter_by(
            empresa_id=empresa_id, motorista_id=motorista_id
        ).first()
        if vinculo:
            raise ServiceError(
                'Desvincule o motorista do veículo antes de inativá-lo.', 409
            )
        motorista.ativo = 0
        motorista.atualizar()
        return {'mensagem': 'Motorista inativado.'}

from models import Ocorrencia, Veiculo
from repositories import MotoristaRepository
from services.erros import ServiceError


class ExcluirMotoristaService:
    def executar(self, empresa_id, motorista_id):
        motorista = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
        if not motorista:
            raise ServiceError('Motorista não encontrado.', 404)

        possui_veiculo = Veiculo.query.filter_by(
            empresa_id=empresa_id, motorista_id=motorista_id
        ).first()
        possui_ocorrencia = Ocorrencia.query.filter_by(
            empresa_id=empresa_id, motorista_id=motorista_id
        ).first()
        if possui_veiculo or possui_ocorrencia:
            raise ServiceError(
                'Não é possível excluir um motorista vinculado a veículo ou ocorrência.',
                409,
            )

        motorista.deletar()
        return {'mensagem': 'Motorista excluído.'}

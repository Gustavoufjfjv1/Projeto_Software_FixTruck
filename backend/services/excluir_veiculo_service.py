from models import Ocorrencia
from repositories import VeiculoRepository
from services.erros import ServiceError


class ExcluirVeiculoService:
    def executar(self, empresa_id, veiculo_id):
        veiculo = VeiculoRepository.buscar_da_empresa(veiculo_id, empresa_id)
        if not veiculo:
            raise ServiceError('Veículo não encontrado.', 404)
        possui_ocorrencia = Ocorrencia.query.filter_by(
            empresa_id=empresa_id, veiculo_id=veiculo_id
        ).first()
        if possui_ocorrencia:
            raise ServiceError(
                'Não é possível excluir um veículo com ocorrências registradas.',
                409,
            )
        veiculo.deletar()
        return {'mensagem': 'Veículo excluído.'}

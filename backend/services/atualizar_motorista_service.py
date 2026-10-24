from repositories import MotoristaRepository
from services.erros import ServiceError


class AtualizarMotoristaService:
    def executar(self, empresa_id, motorista_id, dados):
        motorista = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
        if not motorista:
            raise ServiceError('Motorista não encontrado.', 404)

        nome = (dados.get('nome') or '').strip()
        if not nome:
            raise ServiceError('Nome do motorista é obrigatório.', 400)

        motorista.nome = nome
        motorista.cnh = (dados.get('cnh') or '').strip()
        motorista.telefone = (dados.get('telefone') or '').strip()
        motorista.atualizar()
        return {'mensagem': 'Cadastro do motorista atualizado.'}

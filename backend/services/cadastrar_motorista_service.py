from models import Motorista
from services.erros import ServiceError


class CadastrarMotoristaService:
    def executar(self, empresa_id, dados):
        nome = (dados.get('nome') or '').strip()
        if not nome:
            raise ServiceError('Nome do motorista é obrigatório.', 400)
        motorista = Motorista(
            empresa_id=empresa_id,
            nome=nome,
            cnh=dados.get('cnh', ''),
            telefone=dados.get('telefone', ''),
        )
        motorista.salvar()
        return {'mensagem': 'Motorista cadastrado.'}

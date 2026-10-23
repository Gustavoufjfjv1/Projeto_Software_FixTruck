from models import Motorista
from services.acesso_motorista_service import DefinirAcessoMotoristaService
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
        resposta = {'mensagem': 'Motorista cadastrado.', 'id': motorista.id}
        if dados.get('email'):
            try:
                acesso = DefinirAcessoMotoristaService().executar(empresa_id, motorista.id, dados)
            except ServiceError:
                motorista.deletar()
                raise
            resposta.update({k: acesso[k] for k in ('email', 'senha_temporaria') if k in acesso})
            resposta['mensagem'] = 'Motorista cadastrado com acesso ao sistema.'
        return resposta

import validacoes as v
from models import Motorista
from services.acesso_motorista_service import DefinirAcessoMotoristaService
from services.erros import ServiceError


class CadastrarMotoristaService:
    def executar(self, empresa_id, dados):
        motorista = Motorista(
            empresa_id=empresa_id,
            nome=v.texto(dados.get('nome'), 'Nome do motorista', max_len=120, min_len=3),
            cnh=v.cnh(dados.get('cnh')),
            telefone=v.telefone(dados.get('telefone')),
        )
        email = v.email(dados.get('email'), obrigatorio=False)
        motorista.salvar()
        resposta = {'mensagem': 'Motorista cadastrado.', 'id': motorista.id}
        if email:
            try:
                acesso = DefinirAcessoMotoristaService().executar(empresa_id, motorista.id, dados)
            except ServiceError:
                motorista.deletar()
                raise
            resposta.update({k: acesso[k] for k in ('email', 'senha_temporaria') if k in acesso})
            resposta['mensagem'] = 'Motorista cadastrado com acesso ao sistema.'
        return resposta

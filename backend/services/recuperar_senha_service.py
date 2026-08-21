from models import Empresa
from auth import gerar_token_recuperacao
from services.erros import ServiceError


class RecuperarSenhaService:
    def executar(self, dados):
        email = (dados.get('email') or '').strip().lower()
        empresa = Empresa.buscar_por_email(email)
        if not empresa:
            raise ServiceError('Não existe conta cadastrada com este e-mail.', 404)

        token = gerar_token_recuperacao(empresa.id)
        return {
            'mensagem': (
                'Código gerado. Em um sistema em produção ele seria enviado por e-mail; '
                'aqui, para fins acadêmicos, ele é exibido diretamente na tela.'
            ),
            'token': token,
        }

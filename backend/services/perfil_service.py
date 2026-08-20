from models import Empresa
from auth import gerar_token
from services.erros import ServiceError


class PerfilService:
    @staticmethod
    def obter(empresa_id):
        empresa = Empresa.buscar_publico(empresa_id)
        if not empresa:
            raise ServiceError('Empresa não encontrada.', 404)
        return {'empresa': empresa}

    @staticmethod
    def atualizar(empresa_id, dados):
        empresa = Empresa.buscar(empresa_id)
        if not empresa:
            raise ServiceError('Empresa não encontrada.', 404)

        nome = (dados.get('nome') or empresa['nome']).strip()
        qtd_caminhoes = dados.get('qtd_caminhoes', empresa['qtd_caminhoes'])
        Empresa.editar(empresa_id, {
            'nome': nome,
            'qtd_caminhoes': qtd_caminhoes,
        })
        token = gerar_token(empresa_id, nome)
        return {
            'mensagem': 'Dados atualizados com sucesso.',
            'token': token,
            'empresa': {
                'id': empresa_id,
                'nome': nome,
                'email': empresa['email'],
                'qtd_caminhoes': qtd_caminhoes,
            },
        }

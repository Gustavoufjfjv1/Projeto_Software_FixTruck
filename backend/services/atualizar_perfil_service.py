from models import Empresa
from auth import gerar_token
from services.erros import ServiceError


class AtualizarPerfilService:
    def executar(self, empresa_id, dados):
        empresa = Empresa.buscar_por_id(empresa_id)
        if not empresa:
            raise ServiceError('Empresa não encontrada.', 404)

        nome = (dados.get('nome') or empresa.nome).strip()
        qtd_caminhoes = dados.get('qtd_caminhoes', empresa.qtd_caminhoes)
        empresa.nome = nome
        empresa.qtd_caminhoes = qtd_caminhoes
        empresa.atualizar()

        return {
            'mensagem': 'Dados atualizados com sucesso.',
            'token': gerar_token(empresa_id, nome),
            'empresa': empresa.to_dict_publico(),
        }

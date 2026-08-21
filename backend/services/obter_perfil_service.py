from models import Empresa
from services.erros import ServiceError


class ObterPerfilService:
    def executar(self, empresa_id):
        empresa = Empresa.buscar_por_id(empresa_id)
        if not empresa:
            raise ServiceError('Empresa não encontrada.', 404)
        return {'empresa': empresa.to_dict_publico()}

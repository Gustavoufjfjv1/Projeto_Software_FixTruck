from repositories import MotoristaRepository
from services.erros import ServiceError


class BuscarMotoristasService:
    def executar(self, empresa_id, termo):
        termo = (termo or '').strip()
        if len(termo) < 2:
            raise ServiceError('Informe pelo menos 2 caracteres para pesquisar.', 400)
        return MotoristaRepository.buscar_por_termo(empresa_id, termo)

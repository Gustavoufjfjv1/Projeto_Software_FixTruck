from models import Oficina
from repositories import FavoritoRepository
from utils import oficina_aberta_agora
from services.erros import ServiceError


class ObterDetalheOficinaService:
    def executar(self, empresa_id, oficina_id):
        of = Oficina.buscar_por_id(oficina_id)
        if not of:
            raise ServiceError('Oficina não encontrada.', 404)
        fav = FavoritoRepository.buscar_par(empresa_id, oficina_id)
        return {
            'oficina': of.to_dict(),
            'favoritada': fav is not None,
            'aberta_agora': oficina_aberta_agora(of.hora_abertura, of.hora_fechamento),
        }

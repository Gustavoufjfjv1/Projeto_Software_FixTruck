from models import Oficina
from repositories import FavoritoRepository
from horarios import esta_aberta
from services.erros import ServiceError


class ObterDetalheOficinaService:
    def executar(self, empresa_id, oficina_id):
        of = Oficina.buscar_por_id(oficina_id)
        if not of or (not of.ativa and of.empresa_id != empresa_id):
            raise ServiceError('Oficina não encontrada.', 404)
        fav = FavoritoRepository.buscar_par(empresa_id, oficina_id)
        return {
            'oficina': of.to_dict(),
            'favoritada': fav is not None,
            'aberta_agora': esta_aberta(of.horarios, of.aberta_24h),
            'editavel': of.empresa_id == empresa_id,
        }

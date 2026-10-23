from models import Favorito, Oficina
from repositories import FavoritoRepository
from services.erros import ServiceError


class FavoritarOficinaService:
    def executar(self, empresa_id, oficina_id):
        fav = FavoritoRepository.buscar_par(empresa_id, oficina_id)
        if fav:
            fav.deletar()
            return {'mensagem': 'Oficina removida dos favoritos.', 'favoritada': False}
        oficina = Oficina.buscar_por_id(oficina_id)
        if not oficina or not oficina.ativa:
            raise ServiceError('Oficina não encontrada.', 404)
        Favorito(empresa_id=empresa_id, oficina_id=oficina_id).salvar()
        return {'mensagem': 'Oficina favoritada.', 'favoritada': True}

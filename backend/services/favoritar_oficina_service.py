from models import Favorito
from repositories import FavoritoRepository


class FavoritarOficinaService:
    def executar(self, empresa_id, oficina_id):
        fav = FavoritoRepository.buscar_par(empresa_id, oficina_id)
        if fav:
            fav.deletar()
            return {'mensagem': 'Oficina removida dos favoritos.', 'favoritada': False}
        Favorito(empresa_id=empresa_id, oficina_id=oficina_id).salvar()
        return {'mensagem': 'Oficina favoritada.', 'favoritada': True}

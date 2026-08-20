from models import Oficina, Favorito
from utils import haversine, oficina_aberta_agora
from services.erros import ServiceError


class OficinaService:
    @staticmethod
    def listar(empresa_id, busca='', raio=None, lat=None, lon=None):
        oficinas_list = Oficina.listar_ativas(busca)
        resultado = []
        for of in oficinas_list:
            of_dict = dict(of)
            fav = Favorito.buscar_par(empresa_id, of['id'])
            of_dict['favoritada'] = fav is not None
            of_dict['aberta_agora'] = oficina_aberta_agora(
                of.get('hora_abertura'), of.get('hora_fechamento')
            )
            of_dict['distancia'] = None
            if lat is not None and lon is not None and of.get('lat') and of.get('lon'):
                of_dict['distancia'] = round(haversine(lat, lon, of['lat'], of['lon']), 1)
                if raio is not None and of_dict['distancia'] > raio:
                    continue
            resultado.append(of_dict)

        if lat is not None and lon is not None:
            resultado.sort(
                key=lambda x: x['distancia'] if x['distancia'] is not None else 9999
            )
        return {'oficinas': resultado}

    @staticmethod
    def detalhe(empresa_id, oficina_id):
        of = Oficina.buscar(oficina_id)
        if not of:
            raise ServiceError('Oficina não encontrada.', 404)
        fav = Favorito.buscar_par(empresa_id, oficina_id)
        return {
            'oficina': of,
            'favoritada': fav is not None,
            'aberta_agora': oficina_aberta_agora(
                of.get('hora_abertura'), of.get('hora_fechamento')
            ),
        }

    @staticmethod
    def favoritar(empresa_id, oficina_id):
        fav = Favorito.buscar_par(empresa_id, oficina_id)
        if fav:
            Favorito.remover_par(empresa_id, oficina_id)
            return {'mensagem': 'Oficina removida dos favoritos.', 'favoritada': False}
        Favorito.cadastrar({'empresa_id': empresa_id, 'oficina_id': oficina_id})
        return {'mensagem': 'Oficina favoritada.', 'favoritada': True}

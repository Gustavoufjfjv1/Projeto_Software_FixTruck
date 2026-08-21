from repositories import OficinaRepository


class ListarOficinasService:
    def executar(self, empresa_id, busca='', raio=None, lat=None, lon=None):
        return {
            'oficinas': OficinaRepository.listar_com_contexto(
                empresa_id, busca=busca, raio=raio, lat=lat, lon=lon
            )
        }

from repositories import OficinaRepository


class ListarOficinasService:
    def executar(
        self, empresa_id, busca='', raio=None, lat=None, lon=None, limite=None, somente_nome=False
    ):
        return {
            'oficinas': OficinaRepository.listar_com_contexto(
                empresa_id, busca=busca, raio=raio, lat=lat, lon=lon, limite=limite,
                somente_nome=somente_nome,
            )
        }

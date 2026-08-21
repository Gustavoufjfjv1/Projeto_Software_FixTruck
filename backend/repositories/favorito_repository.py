from models import Favorito


class FavoritoRepository:
    """Consultas específicas de favoritos."""

    @staticmethod
    def buscar_par(empresa_id, oficina_id):
        return Favorito.query.filter_by(empresa_id=empresa_id, oficina_id=oficina_id).first()

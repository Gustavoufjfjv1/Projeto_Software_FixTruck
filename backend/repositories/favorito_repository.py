from database import get_db
from models import Favorito


class FavoritoRepository:
    """Consultas específicas de favoritos (SQL puro)."""

    @staticmethod
    def buscar_par(empresa_id, oficina_id):
        row = get_db().execute(
            'SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?',
            (empresa_id, oficina_id),
        ).fetchone()
        if not row:
            return None
        return Favorito.buscar_por_id(row['id'])

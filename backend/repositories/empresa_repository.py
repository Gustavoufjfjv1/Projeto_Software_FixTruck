from database import get_db
from models import Empresa


class EmpresaRepository:
    """Consultas específicas de empresa (SQL puro)."""

    @staticmethod
    def buscar_por_email(email):
        row = get_db().execute(
            'SELECT id FROM empresas WHERE email=?', (email,)
        ).fetchone()
        if not row:
            return None
        return Empresa.buscar_por_id(row['id'])

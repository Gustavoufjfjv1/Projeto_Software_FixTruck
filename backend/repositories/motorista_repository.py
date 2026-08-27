from database import get_db
from models import Motorista
from utils import rows_to_list


class MotoristaRepository:
    """Consultas de motoristas com joins (SQL puro)."""

    @staticmethod
    def listar_por_empresa(empresa_id, apenas_ativos=False):
        query = 'SELECT * FROM motoristas WHERE empresa_id=?'
        params = [empresa_id]
        if apenas_ativos:
            query += ' AND ativo=1'
        query += ' ORDER BY nome'
        return rows_to_list(get_db().execute(query, params).fetchall())

    @staticmethod
    def listar_com_veiculo(empresa_id):
        rows = get_db().execute(
            """SELECT m.*,
                      (SELECT placa FROM veiculos WHERE motorista_id=m.id LIMIT 1) as veiculo_placa
               FROM motoristas m WHERE m.empresa_id=? ORDER BY m.nome""",
            (empresa_id,),
        ).fetchall()
        return rows_to_list(rows)

    @staticmethod
    def buscar_da_empresa(motorista_id, empresa_id):
        row = get_db().execute(
            'SELECT * FROM motoristas WHERE id=? AND empresa_id=?',
            (motorista_id, empresa_id),
        ).fetchone()
        return Motorista.from_row(row)

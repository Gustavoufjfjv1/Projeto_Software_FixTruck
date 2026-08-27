from database import get_db
from models import Veiculo
from utils import rows_to_list


class VeiculoRepository:
    """Consultas de veículos com joins (SQL puro)."""

    @staticmethod
    def listar_por_empresa(empresa_id):
        rows = get_db().execute(
            """SELECT v.*, m.nome as motorista_nome FROM veiculos v
               LEFT JOIN motoristas m ON v.motorista_id = m.id
               WHERE v.empresa_id=? ORDER BY v.placa""",
            (empresa_id,),
        ).fetchall()
        return rows_to_list(rows)

    @staticmethod
    def listar_simples(empresa_id):
        rows = get_db().execute(
            'SELECT id, placa, modelo FROM veiculos WHERE empresa_id=? ORDER BY placa',
            (empresa_id,),
        ).fetchall()
        return rows_to_list(rows)

    @staticmethod
    def buscar_da_empresa(veiculo_id, empresa_id):
        row = get_db().execute(
            'SELECT * FROM veiculos WHERE id=? AND empresa_id=?',
            (veiculo_id, empresa_id),
        ).fetchone()
        return Veiculo.from_row(row)

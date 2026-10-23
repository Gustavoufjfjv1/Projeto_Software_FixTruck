from database import get_db
from models import Motorista
from utils import rows_to_list

# Nunca selecionar a coluna senha em listagens enviadas ao front-end.
COLUNAS_PUBLICAS = 'm.id, m.empresa_id, m.nome, m.cnh, m.telefone, m.ativo, m.email, m.trocar_senha, ' \
                   '(m.email IS NOT NULL AND m.senha IS NOT NULL) AS tem_acesso'


class MotoristaRepository:
    """Consultas de motoristas com joins (SQL puro)."""

    @staticmethod
    def listar_por_empresa(empresa_id, apenas_ativos=False):
        query = f'SELECT {COLUNAS_PUBLICAS} FROM motoristas m WHERE m.empresa_id=?'
        params = [empresa_id]
        if apenas_ativos:
            query += ' AND m.ativo=1'
        query += ' ORDER BY m.nome'
        return rows_to_list(get_db().execute(query, params).fetchall())

    @staticmethod
    def listar_com_veiculo(empresa_id):
        rows = get_db().execute(
            f"""SELECT {COLUNAS_PUBLICAS},
                      (SELECT placa FROM veiculos WHERE motorista_id=m.id LIMIT 1) as veiculo_placa
               FROM motoristas m WHERE m.empresa_id=? ORDER BY m.nome""",
            (empresa_id,),
        ).fetchall()
        return rows_to_list(rows)

    @staticmethod
    def buscar_da_empresa(motorista_id, empresa_id):
        row = get_db().execute(
            'SELECT id FROM motoristas WHERE id=? AND empresa_id=?',
            (motorista_id, empresa_id),
        ).fetchone()
        if not row:
            return None
        return Motorista.buscar_por_id(row['id'])

    @staticmethod
    def buscar_por_email(email):
        row = get_db().execute('SELECT id FROM motoristas WHERE email=?', (email,)).fetchone()
        if not row:
            return None
        return Motorista.buscar_por_id(row['id'])

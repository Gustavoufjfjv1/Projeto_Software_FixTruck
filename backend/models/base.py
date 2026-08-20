from database import get_db
from utils import row_to_dict, rows_to_list


class ModeloBase:
    """Base com operações CRUD sobre SQLite."""

    tabela = None
    campos = ()

    @classmethod
    def _db(cls):
        return get_db()

    @classmethod
    def _to_dict(cls, row):
        return row_to_dict(row)

    @classmethod
    def _to_list(cls, rows):
        return rows_to_list(rows)

    @classmethod
    def cadastrar(cls, dados):
        if not cls.tabela or not cls.campos:
            raise NotImplementedError(f'{cls.__name__} sem tabela/campos definidos')
        cols = [c for c in cls.campos if c in dados and dados[c] is not None]
        if not cols:
            raise ValueError('Nenhum campo válido para cadastro')
        placeholders = ','.join('?' * len(cols))
        sql = f"INSERT INTO {cls.tabela} ({','.join(cols)}) VALUES ({placeholders})"
        db = cls._db()
        db.execute(sql, [dados[c] for c in cols])
        db.commit()
        return db.execute('SELECT last_insert_rowid() as id').fetchone()['id']

    @classmethod
    def listar(cls, where=None, params=None, order_by='id'):
        sql = f'SELECT * FROM {cls.tabela}'
        if where:
            sql += f' WHERE {where}'
        if order_by:
            sql += f' ORDER BY {order_by}'
        rows = cls._db().execute(sql, params or []).fetchall()
        return cls._to_list(rows)

    @classmethod
    def buscar(cls, id_):
        row = cls._db().execute(
            f'SELECT * FROM {cls.tabela} WHERE id=?', (id_,)
        ).fetchone()
        return cls._to_dict(row)

    @classmethod
    def editar(cls, id_, dados):
        cols = [c for c in cls.campos if c in dados]
        if not cols:
            return False
        sets = ', '.join(f'{c}=?' for c in cols)
        values = [dados[c] for c in cols] + [id_]
        db = cls._db()
        db.execute(f'UPDATE {cls.tabela} SET {sets} WHERE id=?', values)
        db.commit()
        return True

    @classmethod
    def excluir(cls, id_):
        db = cls._db()
        db.execute(f'DELETE FROM {cls.tabela} WHERE id=?', (id_,))
        db.commit()
        return True

from database import get_db


class ModeloBase:
    """Base com CRUD em SQL puro (sqlite3)."""

    tabela = None
    campos = ()

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)
        for campo in self.campos:
            setattr(self, campo, kwargs.get(campo))
        for chave, valor in kwargs.items():
            setattr(self, chave, valor)

    @classmethod
    def _db(cls):
        return get_db()

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(**dict(row))

    def to_dict(self, extras=None):
        data = {'id': self.id}
        for campo in self.campos:
            data[campo] = getattr(self, campo, None)
        if extras:
            data.update(extras)
        return data

    def salvar(self):
        cols = [c for c in self.campos if getattr(self, c, None) is not None]
        if not cols:
            raise ValueError('Nenhum campo para salvar')
        valores = [getattr(self, c) for c in cols]
        placeholders = ','.join('?' * len(cols))
        sql = f"INSERT INTO {self.tabela} ({','.join(cols)}) VALUES ({placeholders})"
        db = self._db()
        db.execute(sql, valores)
        db.commit()
        self.id = db.execute('SELECT last_insert_rowid() as id').fetchone()['id']
        return self

    def atualizar(self):
        if not self.id:
            raise ValueError('Não é possível atualizar sem id')
        cols = list(self.campos)
        sets = ', '.join(f'{c}=?' for c in cols)
        valores = [getattr(self, c, None) for c in cols] + [self.id]
        db = self._db()
        db.execute(f'UPDATE {self.tabela} SET {sets} WHERE id=?', valores)
        db.commit()
        return self

    def deletar(self):
        if not self.id:
            raise ValueError('Não é possível deletar sem id')
        db = self._db()
        db.execute(f'DELETE FROM {self.tabela} WHERE id=?', (self.id,))
        db.commit()

    @classmethod
    def listar_todos(cls):
        rows = cls._db().execute(f'SELECT * FROM {cls.tabela}').fetchall()
        return [cls.from_row(r) for r in rows]

    @classmethod
    def buscar_por_id(cls, id_):
        row = cls._db().execute(
            f'SELECT * FROM {cls.tabela} WHERE id=?', (id_,)
        ).fetchone()
        return cls.from_row(row)

from .base import ModeloBase


class Favorito(ModeloBase):
    tabela = 'favoritos'
    campos = ('empresa_id', 'oficina_id')

    @classmethod
    def buscar_par(cls, empresa_id, oficina_id):
        row = cls._db().execute(
            'SELECT * FROM favoritos WHERE empresa_id=? AND oficina_id=?',
            (empresa_id, oficina_id),
        ).fetchone()
        return cls._to_dict(row)

    @classmethod
    def remover_par(cls, empresa_id, oficina_id):
        db = cls._db()
        db.execute(
            'DELETE FROM favoritos WHERE empresa_id=? AND oficina_id=?',
            (empresa_id, oficina_id),
        )
        db.commit()
        return True

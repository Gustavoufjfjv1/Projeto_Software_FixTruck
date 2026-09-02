from datetime import datetime
from database import db


class ModeloBase(db.Model):
    """Base com CRUD via SQLAlchemy (disciplina)."""

    __abstract__ = True

    def salvar(self):
        db.session.add(self)
        db.session.commit()
        return self

    def atualizar(self):
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def listar_todos(cls):
        return cls.query.all()

    @classmethod
    def buscar_por_id(cls, id_):
        return db.session.get(cls, id_)

    def to_dict(self, extras=None):
        data = {}
        for col in self.__table__.columns:
            valor = getattr(self, col.name)
            if isinstance(valor, datetime):
                valor = valor.strftime('%Y-%m-%d %H:%M:%S')
            data[col.name] = valor
        if extras:
            data.update(extras)
        return data

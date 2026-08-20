from .base import ModeloBase


class Empresa(ModeloBase):
    tabela = 'empresas'
    campos = ('nome', 'email', 'senha', 'qtd_caminhoes')

    @classmethod
    def buscar_por_email(cls, email):
        row = cls._db().execute(
            'SELECT * FROM empresas WHERE email=?', (email,)
        ).fetchone()
        return cls._to_dict(row)

    @classmethod
    def autenticar(cls, email, senha):
        row = cls._db().execute(
            'SELECT * FROM empresas WHERE email=? AND senha=?',
            (email, senha),
        ).fetchone()
        return cls._to_dict(row)

    @classmethod
    def buscar_publico(cls, id_):
        row = cls._db().execute(
            'SELECT id, nome, email, qtd_caminhoes FROM empresas WHERE id=?',
            (id_,),
        ).fetchone()
        return cls._to_dict(row)

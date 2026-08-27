from models.base import ModeloBase


class Empresa(ModeloBase):
    tabela = 'empresas'
    campos = ('nome', 'email', 'senha', 'qtd_caminhoes')

    def to_dict_publico(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'qtd_caminhoes': self.qtd_caminhoes,
        }

    @classmethod
    def buscar_por_email(cls, email):
        row = cls._db().execute(
            'SELECT * FROM empresas WHERE email=?', (email,)
        ).fetchone()
        return cls.from_row(row)

    @classmethod
    def autenticar(cls, email, senha):
        row = cls._db().execute(
            'SELECT * FROM empresas WHERE email=? AND senha=?',
            (email, senha),
        ).fetchone()
        return cls.from_row(row)

from .base import ModeloBase


class Motorista(ModeloBase):
    tabela = 'motoristas'
    campos = ('empresa_id', 'nome', 'cnh', 'telefone', 'ativo')

    @classmethod
    def listar_por_empresa(cls, empresa_id, apenas_ativos=False):
        where = 'empresa_id=?'
        params = [empresa_id]
        if apenas_ativos:
            where += ' AND ativo=1'
        return cls.listar(where=where, params=params, order_by='nome')

    @classmethod
    def listar_com_veiculo(cls, empresa_id):
        rows = cls._db().execute(
            """SELECT m.*,
                      (SELECT placa FROM veiculos WHERE motorista_id=m.id LIMIT 1) as veiculo_placa
               FROM motoristas m WHERE m.empresa_id=? ORDER BY m.nome""",
            (empresa_id,),
        ).fetchall()
        return cls._to_list(rows)

    @classmethod
    def buscar_da_empresa(cls, id_, empresa_id):
        row = cls._db().execute(
            'SELECT * FROM motoristas WHERE id=? AND empresa_id=?',
            (id_, empresa_id),
        ).fetchone()
        return cls._to_dict(row)

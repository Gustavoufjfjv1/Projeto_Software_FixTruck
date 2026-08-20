from .base import ModeloBase


class Veiculo(ModeloBase):
    tabela = 'veiculos'
    campos = ('empresa_id', 'placa', 'modelo', 'marca', 'tipo_veiculo', 'motorista_id')

    @classmethod
    def listar_por_empresa(cls, empresa_id):
        rows = cls._db().execute(
            """SELECT v.*, m.nome as motorista_nome FROM veiculos v
               LEFT JOIN motoristas m ON v.motorista_id = m.id
               WHERE v.empresa_id=? ORDER BY v.placa""",
            (empresa_id,),
        ).fetchall()
        return cls._to_list(rows)

    @classmethod
    def listar_simples(cls, empresa_id):
        rows = cls._db().execute(
            'SELECT id, placa, modelo FROM veiculos WHERE empresa_id=? ORDER BY placa',
            (empresa_id,),
        ).fetchall()
        return cls._to_list(rows)

    @classmethod
    def buscar_da_empresa(cls, id_, empresa_id):
        row = cls._db().execute(
            'SELECT * FROM veiculos WHERE id=? AND empresa_id=?',
            (id_, empresa_id),
        ).fetchone()
        return cls._to_dict(row)

    @classmethod
    def vincular_motorista(cls, veiculo_id, motorista_id):
        return cls.editar(veiculo_id, {'motorista_id': motorista_id})

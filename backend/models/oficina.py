from models.base import ModeloBase


class Oficina(ModeloBase):
    tabela = 'oficinas'
    campos = (
        'nome', 'endereco', 'telefone', 'lat', 'lon', 'especialidades',
        'tipos_veiculo', 'tem_guincho', 'hora_abertura', 'hora_fechamento', 'ativa',
    )

    @classmethod
    def listar_ativas(cls):
        rows = cls._db().execute(
            'SELECT * FROM oficinas WHERE ativa=1 ORDER BY nome'
        ).fetchall()
        return [cls.from_row(r) for r in rows]

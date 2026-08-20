from .base import ModeloBase


class Oficina(ModeloBase):
    tabela = 'oficinas'
    campos = (
        'nome', 'endereco', 'telefone', 'lat', 'lon', 'especialidades',
        'tipos_veiculo', 'tem_guincho', 'hora_abertura', 'hora_fechamento', 'ativa',
    )

    @classmethod
    def listar_ativas(cls, busca=''):
        query = 'SELECT * FROM oficinas WHERE ativa=1'
        params = []
        if busca:
            query += ' AND (nome LIKE ? OR especialidades LIKE ?)'
            params.extend([f'%{busca}%', f'%{busca}%'])
        query += ' ORDER BY nome'
        rows = cls._db().execute(query, params).fetchall()
        return cls._to_list(rows)

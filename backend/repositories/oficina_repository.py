from database import get_db
from models import Oficina
from horarios import esta_aberta
from utils import haversine


class OficinaRepository:
    """Consultas e enriquecimento de oficinas (SQL puro)."""

    @staticmethod
    def _carregar(rows):
        oficinas = []
        for r in rows:
            of = Oficina.buscar_por_id(r['id'])
            if of:
                oficinas.append(of)
        return oficinas

    @staticmethod
    def listar_ativas(busca=''):
        query = 'SELECT id FROM oficinas WHERE ativa = 1'
        params = []
        if busca:
            query += ' AND (nome LIKE ? OR especialidades LIKE ? OR cidade LIKE ?)'
            params.extend([f'%{busca}%'] * 3)
        query += ' ORDER BY nome'
        return OficinaRepository._carregar(get_db().execute(query, params).fetchall())

    @staticmethod
    def listar_da_empresa(empresa_id):
        rows = get_db().execute(
            'SELECT id FROM oficinas WHERE empresa_id = ? ORDER BY ativa DESC, nome', (empresa_id,)
        ).fetchall()
        return OficinaRepository._carregar(rows)

    @staticmethod
    def contar_ativas():
        return get_db().execute('SELECT COUNT(*) AS c FROM oficinas WHERE ativa = 1').fetchone()['c']

    @staticmethod
    def buscar_duplicada(nome, endereco, ignorar_id=None):
        query = 'SELECT id FROM oficinas WHERE lower(nome) = lower(?) AND lower(COALESCE(endereco, \'\')) = lower(?)'
        params = [nome, endereco or '']
        if ignorar_id:
            query += ' AND id <> ?'
            params.append(ignorar_id)
        return get_db().execute(query, params).fetchone() is not None

    @staticmethod
    def ids_favoritos(empresa_id):
        rows = get_db().execute(
            'SELECT oficina_id FROM favoritos WHERE empresa_id = ?', (empresa_id,)
        ).fetchall()
        return {r['oficina_id'] for r in rows}

    @staticmethod
    def listar_com_contexto(empresa_id, busca='', raio=None, lat=None, lon=None):
        favoritos = OficinaRepository.ids_favoritos(empresa_id)
        resultado = []
        for of in OficinaRepository.listar_ativas(busca):
            of_dict = of.to_dict()
            of_dict['favoritada'] = of.id in favoritos
            of_dict['aberta_agora'] = esta_aberta(of.horarios, of.aberta_24h)
            of_dict['distancia'] = None
            if lat is not None and lon is not None and of.lat is not None and of.lon is not None:
                of_dict['distancia'] = round(haversine(lat, lon, of.lat, of.lon), 1)
                if raio is not None and of_dict['distancia'] > raio:
                    continue
            resultado.append(of_dict)
        if lat is not None and lon is not None:
            resultado.sort(
                key=lambda x: (
                    0 if x['aberta_agora'] else 1,
                    x['distancia'] if x['distancia'] is not None else 9999,
                )
            )
        return resultado

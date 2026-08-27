from database import get_db
from models import Oficina
from utils import haversine, oficina_aberta_agora


class OficinaRepository:
    """Consultas e enriquecimento de oficinas (SQL puro)."""

    @staticmethod
    def listar_ativas(busca=''):
        query = 'SELECT * FROM oficinas WHERE ativa=1'
        params = []
        if busca:
            query += ' AND (nome LIKE ? OR especialidades LIKE ?)'
            params.extend([f'%{busca}%', f'%{busca}%'])
        query += ' ORDER BY nome'
        rows = get_db().execute(query, params).fetchall()
        return [Oficina.from_row(r) for r in rows]

    @staticmethod
    def listar_com_contexto(empresa_id, busca='', raio=None, lat=None, lon=None):
        oficinas = OficinaRepository.listar_ativas(busca)
        resultado = []
        for of in oficinas:
            of_dict = of.to_dict()
            fav = get_db().execute(
                'SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?',
                (empresa_id, of.id),
            ).fetchone()
            of_dict['favoritada'] = fav is not None
            of_dict['aberta_agora'] = oficina_aberta_agora(of.hora_abertura, of.hora_fechamento)
            of_dict['distancia'] = None
            if lat is not None and lon is not None and of.lat is not None and of.lon is not None:
                of_dict['distancia'] = round(haversine(lat, lon, of.lat, of.lon), 1)
                if raio is not None and of_dict['distancia'] > raio:
                    continue
            resultado.append(of_dict)
        if lat is not None and lon is not None:
            resultado.sort(key=lambda x: x['distancia'] if x['distancia'] is not None else 9999)
        return resultado

    @staticmethod
    def buscar_para_ocorrencia(empresa_id, ocorrencia, raio=None):
        oficinas = []
        for of in OficinaRepository.listar_ativas():
            of_dict = of.to_dict()
            if ocorrencia.lat and ocorrencia.lon:
                try:
                    dist = haversine(
                        float(ocorrencia.lat), float(ocorrencia.lon), of.lat, of.lon
                    )
                    of_dict['distancia'] = round(dist, 1)
                except (TypeError, ValueError):
                    of_dict['distancia'] = None
            else:
                of_dict['distancia'] = None

            if raio is not None and of_dict['distancia'] is not None and of_dict['distancia'] > raio:
                continue

            of_dict['aberta_agora'] = oficina_aberta_agora(of.hora_abertura, of.hora_fechamento)
            of_dict['atende_tipo'] = ocorrencia.tipo_problema.lower() in (of.especialidades or '').lower()
            of_dict['atende_veiculo'] = ocorrencia.tipo_veiculo.lower() in (of.tipos_veiculo or '').lower()
            fav = get_db().execute(
                'SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?',
                (empresa_id, of.id),
            ).fetchone()
            of_dict['favoritada'] = fav is not None
            oficinas.append(of_dict)

        if ocorrencia.pane_total:
            oficinas.sort(key=lambda x: (not x.get('tem_guincho', False), x['distancia'] or 9999))
        else:
            oficinas.sort(key=lambda x: (x['distancia'] or 9999))
        return oficinas

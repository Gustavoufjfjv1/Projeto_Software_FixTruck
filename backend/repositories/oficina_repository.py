import math

from sqlalchemy import or_

from database import get_db
from models import Oficina
from utils import haversine, oficina_aberta_agora


class OficinaRepository:
    """Consultas e enriquecimento de oficinas (SQL puro)."""

    @staticmethod
    def listar_ativas(busca='', limite=None, somente_nome=False):
        query = Oficina.query.filter_by(ativa=1)
        if busca:
            termo = f'%{busca}%'
            filtro = Oficina.nome.ilike(termo)
            if not somente_nome:
                filtro = or_(filtro, Oficina.especialidades.ilike(termo))
            query = query.filter(filtro)
        query = query.order_by(Oficina.nome)
        if limite is not None:
            query = query.limit(max(1, min(limite, 100)))
        return query.all()

    @staticmethod
    def listar_com_contexto(
        empresa_id, busca='', raio=None, lat=None, lon=None, limite=None, somente_nome=False
    ):
        oficinas = OficinaRepository.listar_ativas(busca, limite, somente_nome)
        favoritas = {
            row['oficina_id']
            for row in get_db().execute(
                'SELECT oficina_id FROM favoritos WHERE empresa_id=?',
                (empresa_id,),
            ).fetchall()
        }
        resultado = []
        for of in oficinas:
            of_dict = of.to_dict()
            of_dict['favoritada'] = of.id in favoritas
            of_dict['aberta_agora'] = oficina_aberta_agora(of.hora_abertura, of.hora_fechamento)
            of_dict['distancia'] = None
            if lat is not None and lon is not None and of.lat is not None and of.lon is not None:
                of_dict['distancia'] = round(haversine(lat, lon, of.lat, of.lon), 1)
                if raio is not None and of_dict['distancia'] > raio:
                    continue
            resultado.append(of_dict)
        if lat is not None and lon is not None:
            resultado.sort(
                key=lambda x: (
                    0 if x['aberta_agora'] is True else 1 if x['aberta_agora'] is None else 2,
                    x['distancia'] if x['distancia'] is not None else 9999,
                )
            )
        return resultado

    @staticmethod
    def buscar_para_ocorrencia(empresa_id, ocorrencia, raio=None):
        oficinas = []
        favoritas = {
            row['oficina_id']
            for row in get_db().execute(
                'SELECT oficina_id FROM favoritos WHERE empresa_id=?',
                (empresa_id,),
            ).fetchall()
        }
        for of in Oficina.query.filter_by(ativa=1).all():
            of_dict = of.to_dict()
            if ocorrencia.lat is not None and ocorrencia.lon is not None:
                try:
                    lat, lon = float(ocorrencia.lat), float(ocorrencia.lon)
                    if (
                        of.lat is not None and of.lon is not None
                        and all(map(math.isfinite, (lat, lon, of.lat, of.lon)))
                        and -90 <= lat <= 90 and -180 <= lon <= 180
                        and -90 <= of.lat <= 90 and -180 <= of.lon <= 180
                    ):
                        dist = haversine(lat, lon, of.lat, of.lon)
                        of_dict['distancia'] = round(dist, 1)
                    else:
                        of_dict['distancia'] = None
                except (TypeError, ValueError):
                    of_dict['distancia'] = None
            else:
                of_dict['distancia'] = None

            if raio is not None and of_dict['distancia'] is not None and of_dict['distancia'] > raio:
                continue

            of_dict['aberta_agora'] = oficina_aberta_agora(of.hora_abertura, of.hora_fechamento)
            of_dict['atende_tipo'] = ocorrencia.tipo_problema.lower() in (of.especialidades or '').lower()
            of_dict['atende_veiculo'] = bool(of.tipos_veiculo) and (
                ocorrencia.tipo_veiculo.lower() in of.tipos_veiculo.lower()
            )
            of_dict['favoritada'] = of.id in favoritas
            of_dict['compatibilidade'] = int(of_dict['atende_tipo']) + int(of_dict['atende_veiculo'])
            of_dict['recomendada'] = bool(
                of_dict['atende_tipo'] and of_dict['atende_veiculo'] and of_dict['aberta_agora']
                and (bool(of_dict.get('tem_guincho')) if ocorrencia.pane_total else True)
            )
            oficinas.append(of_dict)

        def chave_ordenacao(of):
            sem_guincho_penaliza = 1 if (ocorrencia.pane_total and not of.get('tem_guincho')) else 0
            return (
                sem_guincho_penaliza,
                -of['compatibilidade'],
                0 if of['aberta_agora'] is True else 1 if of['aberta_agora'] is None else 2,
                of['distancia'] if of['distancia'] is not None else 9999,
            )

        oficinas.sort(key=chave_ordenacao)
        return oficinas

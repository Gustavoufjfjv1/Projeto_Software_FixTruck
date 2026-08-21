from models import Oficina, Favorito
from utils import haversine, oficina_aberta_agora


class OficinaRepository:
    """Consultas e enriquecimento de oficinas (busca, distância, favoritos)."""

    @staticmethod
    def listar_ativas(busca=''):
        query = Oficina.query.filter_by(ativa=1)
        if busca:
            like = f'%{busca}%'
            query = query.filter(
                db_or_nome_especialidade(like)
            )
        return query.order_by(Oficina.nome).all()

    @staticmethod
    def listar_com_contexto(empresa_id, busca='', raio=None, lat=None, lon=None):
        oficinas = OficinaRepository.listar_ativas(busca)
        resultado = []
        for of in oficinas:
            of_dict = of.to_dict()
            fav = Favorito.query.filter_by(empresa_id=empresa_id, oficina_id=of.id).first()
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
            of_dict['favoritada'] = Favorito.query.filter_by(
                empresa_id=empresa_id, oficina_id=of.id
            ).first() is not None
            oficinas.append(of_dict)

        if ocorrencia.pane_total:
            oficinas.sort(key=lambda x: (not x.get('tem_guincho', False), x['distancia'] or 9999))
        else:
            oficinas.sort(key=lambda x: (x['distancia'] or 9999))
        return oficinas


def db_or_nome_especialidade(like):
    from sqlalchemy import or_
    return or_(Oficina.nome.like(like), Oficina.especialidades.like(like))

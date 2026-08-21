from sqlalchemy import or_
from models import Oficina, Favorito
from utils import haversine, oficina_aberta_agora


class OficinaRepository:
    """Consultas e enriquecimento de oficinas (busca, distância, favoritos)."""

    @staticmethod
    def listar_ativas(busca=''):
        query = Oficina.query.filter_by(ativa=1)
        if busca:
            like = f'%{busca}%'
            query = query.filter(or_(Oficina.nome.like(like), Oficina.especialidades.like(like)))
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
            resultado.sort(
                key=lambda x: (
                    0 if x['aberta_agora'] else 1,
                    x['distancia'] if x['distancia'] is not None else 9999,
                )
            )
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
            of_dict['compatibilidade'] = int(of_dict['atende_tipo']) + int(of_dict['atende_veiculo'])
            of_dict['recomendada'] = bool(
                of_dict['atende_tipo'] and of_dict['atende_veiculo'] and of_dict['aberta_agora']
                and (of_dict.get('tem_guincho') if ocorrencia.pane_total else True)
            )
            oficinas.append(of_dict)

        def chave_ordenacao(of):
            # 1) Se pane total, oficina sem guincho fica sempre depois das que têm guincho.
            # 2) Depois, quem atende melhor o problema e o tipo de veículo.
            # 3) Depois, quem está aberta agora.
            # 4) Por fim, a mais próxima.
            sem_guincho_penaliza = 1 if (ocorrencia.pane_total and not of.get('tem_guincho')) else 0
            return (
                sem_guincho_penaliza,
                -of['compatibilidade'],
                0 if of['aberta_agora'] else 1,
                of['distancia'] if of['distancia'] is not None else 9999,
            )

        oficinas.sort(key=chave_ordenacao)
        return oficinas

from datetime import datetime
import math


STATUS_ABERTOS = ('aberta', 'em_atendimento')
STATUS_RESOLVIDO = 'resolvido'


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def oficina_aberta_agora(hora_abertura, hora_fechamento):
    if not hora_abertura or not hora_fechamento:
        return None
    agora = datetime.now()
    try:
        h_ab, m_ab = map(int, hora_abertura.split(':')[:2])
        h_fe, m_fe = map(int, hora_fechamento.split(':')[:2])
    except (ValueError, AttributeError):
        return None
    minutos_agora = agora.hour * 60 + agora.minute
    minutos_ab = h_ab * 60 + m_ab
    minutos_fe = h_fe * 60 + m_fe
    if minutos_ab == minutos_fe:
        return True
    if minutos_ab < minutos_fe:
        return minutos_ab <= minutos_agora < minutos_fe
    return minutos_agora >= minutos_ab or minutos_agora < minutos_fe


def minutos_entre(inicio, fim):
    if not inicio or not fim:
        return None
    fmt = '%Y-%m-%d %H:%M:%S'
    try:
        dt_inicio = datetime.strptime(str(inicio)[:19], fmt)
        dt_fim = datetime.strptime(str(fim)[:19], fmt)
    except ValueError:
        return None
    return round((dt_fim - dt_inicio).total_seconds() / 60)


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows):
    return [dict(r) for r in rows]

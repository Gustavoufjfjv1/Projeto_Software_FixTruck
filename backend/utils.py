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
    agora = datetime.now()
    try:
        h_ab, m_ab = map(int, (hora_abertura or '08:00').split(':')[:2])
        h_fe, m_fe = map(int, (hora_fechamento or '18:00').split(':')[:2])
    except (ValueError, AttributeError):
        h_ab, m_ab, h_fe, m_fe = 8, 0, 18, 0
    minutos_agora = agora.hour * 60 + agora.minute
    minutos_ab = h_ab * 60 + m_ab
    minutos_fe = h_fe * 60 + m_fe
    if minutos_ab == minutos_fe:
        return True
    if minutos_ab < minutos_fe:
        return minutos_ab <= minutos_agora < minutos_fe
    return minutos_agora >= minutos_ab or minutos_agora < minutos_fe


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows):
    return [dict(r) for r in rows]

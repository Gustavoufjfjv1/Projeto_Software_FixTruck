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

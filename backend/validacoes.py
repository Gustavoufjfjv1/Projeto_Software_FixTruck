"""Validações de entrada reutilizadas pelos Services. Erros viram ServiceError 422."""
import re

from services.erros import ServiceError

STATUS_INVALIDO = 422

_RE_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$')
_RE_CONTROLE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


def erro(mensagem):
    return ServiceError(mensagem, STATUS_INVALIDO)


def texto(valor, rotulo, obrigatorio=True, max_len=120, min_len=1):
    """Remove espaços/caracteres de controle e valida tamanho."""
    if valor is None:
        valor = ''
    if not isinstance(valor, (str, int, float)):
        raise erro(f'{rotulo} inválido.')
    valor = _RE_CONTROLE.sub('', str(valor)).strip()
    valor = re.sub(r'\s+', ' ', valor)
    if not valor:
        if obrigatorio:
            raise erro(f'{rotulo} é obrigatório.')
        return None
    if len(valor) < min_len:
        raise erro(f'{rotulo} deve ter ao menos {min_len} caracteres.')
    if len(valor) > max_len:
        raise erro(f'{rotulo} deve ter no máximo {max_len} caracteres.')
    return valor


def apenas_digitos(valor):
    return re.sub(r'\D', '', str(valor or ''))


def telefone(valor, obrigatorio=False):
    digitos = apenas_digitos(valor)
    if not digitos:
        if obrigatorio:
            raise erro('Telefone é obrigatório.')
        return None
    if len(digitos) not in (10, 11) or digitos[:2].startswith('0'):
        raise erro('Telefone inválido. Informe DDD + número, ex.: (11) 99999-9999.')
    if len(digitos) == 11:
        return f'({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}'
    return f'({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}'


def email(valor, obrigatorio=True):
    valor = (texto(valor, 'E-mail', obrigatorio=obrigatorio, max_len=120) or '').lower()
    if not valor:
        return None
    if not _RE_EMAIL.match(valor):
        raise erro('E-mail inválido.')
    return valor


def numero(valor, rotulo, obrigatorio=True, minimo=None, maximo=None):
    if valor in (None, ''):
        if obrigatorio:
            raise erro(f'{rotulo} é obrigatório.')
        return None
    if isinstance(valor, bool):
        raise erro(f'{rotulo} inválido.')
    try:
        valor = float(str(valor).replace(',', '.'))
    except (TypeError, ValueError):
        raise erro(f'{rotulo} inválido.')
    if valor != valor or (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
        raise erro(f'{rotulo} fora da faixa permitida.')
    return valor


def coordenadas(lat, lon, obrigatorio=True):
    if lat in (None, '') and lon in (None, ''):
        if obrigatorio:
            raise erro('Latitude e longitude são obrigatórias.')
        return None, None
    lat = numero(lat, 'Latitude', minimo=-90, maximo=90)
    lon = numero(lon, 'Longitude', minimo=-180, maximo=180)
    return lat, lon


def booleano(valor):
    if isinstance(valor, str):
        return valor.strip().lower() in ('1', 'true', 'sim', 'on', 'yes')
    return bool(valor)


def opcoes(valores, permitidas, rotulo, obrigatorio=True):
    """Aceita lista ou string separada por vírgula; devolve lista sem repetição na ordem oficial."""
    if isinstance(valores, str):
        valores = valores.split(',')
    if valores is None:
        valores = []
    if not isinstance(valores, (list, tuple)):
        raise erro(f'{rotulo} inválido.')
    normalizados = {str(v).strip().lower() for v in valores if str(v).strip()}
    invalidos = normalizados - set(permitidas)
    if invalidos:
        raise erro(f'{rotulo} inválido: {", ".join(sorted(invalidos))}. Aceitos: {", ".join(permitidas)}.')
    if obrigatorio and not normalizados:
        raise erro(f'Selecione ao menos um item em {rotulo}.')
    return [p for p in permitidas if p in normalizados]


def opcao(valor, permitidas, rotulo, obrigatorio=True):
    valor = str(valor or '').strip().lower()
    if not valor:
        if obrigatorio:
            raise erro(f'{rotulo} é obrigatório.')
        return None
    if valor not in permitidas:
        raise erro(f'{rotulo} inválido: "{valor}". Aceitos: {", ".join(permitidas)}.')
    return valor


def identificador(valor, rotulo, obrigatorio=False):
    if valor in (None, '', 0, '0'):
        if obrigatorio:
            raise erro(f'{rotulo} é obrigatório.')
        return None
    if isinstance(valor, bool):
        raise erro(f'{rotulo} inválido.')
    try:
        valor_int = int(str(valor).strip())
    except (TypeError, ValueError):
        raise erro(f'{rotulo} inválido.')
    if valor_int <= 0:
        raise erro(f'{rotulo} inválido.')
    return valor_int

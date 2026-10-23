"""Horário de funcionamento das oficinas por dia da semana, no fuso America/Sao_Paulo.

Formato armazenado (coluna oficinas.horarios, JSON):
    {"seg": "08:00-18:00", ..., "sab": "08:00-12:00", "dom": null}
Um intervalo cujo fechamento é menor ou igual à abertura atravessa a meia-noite
(ex.: "22:00-06:00"). Oficinas 24h usam a coluna aberta_24h.
"""
import json
import re
from datetime import datetime, timedelta, timezone

from constantes import DIAS_SEMANA, ROTULOS_DIA_SEMANA

try:
    from zoneinfo import ZoneInfo
    FUSO_SAO_PAULO = ZoneInfo('America/Sao_Paulo')
except Exception:  # Windows sem a base tzdata: Brasil não tem horário de verão desde 2019.
    FUSO_SAO_PAULO = timezone(timedelta(hours=-3), 'America/Sao_Paulo')

_RE_INTERVALO = re.compile(r'^([01]\d|2[0-4]):([0-5]\d)-([01]\d|2[0-4]):([0-5]\d)$')
MINUTOS_DIA = 24 * 60


def agora_sao_paulo():
    return datetime.now(FUSO_SAO_PAULO)


def _para_sao_paulo(quando):
    if quando is None:
        return agora_sao_paulo()
    if quando.tzinfo is None:
        return quando.replace(tzinfo=FUSO_SAO_PAULO)
    return quando.astimezone(FUSO_SAO_PAULO)


def parse_intervalo(texto):
    """'08:00-18:00' -> (480, 1080). Lança ValueError se inválido."""
    m = _RE_INTERVALO.match(str(texto or '').strip())
    if not m:
        raise ValueError(f'Horário inválido: "{texto}". Use o formato HH:MM-HH:MM.')
    h1, m1, h2, m2 = (int(x) for x in m.groups())
    inicio, fim = h1 * 60 + m1, h2 * 60 + m2
    if inicio > MINUTOS_DIA or fim > MINUTOS_DIA or (h1 == 24 and m1) or (h2 == 24 and m2):
        raise ValueError(f'Horário inválido: "{texto}".')
    if inicio == MINUTOS_DIA:
        raise ValueError(f'Horário inválido: "{texto}". A abertura deve ser até 23:59.')
    if inicio == fim:
        raise ValueError(f'Horário inválido: "{texto}". Abertura e fechamento não podem ser iguais.')
    return inicio, fim


def normalizar_horarios(dados):
    """Valida um dict {dia: 'HH:MM-HH:MM' | None} e devolve o dict normalizado com os 7 dias."""
    if isinstance(dados, str):
        try:
            dados = json.loads(dados)
        except ValueError:
            raise ValueError('Horários em formato inválido.')
    if not isinstance(dados, dict):
        raise ValueError('Horários em formato inválido.')
    desconhecidos = set(dados) - set(DIAS_SEMANA)
    if desconhecidos:
        raise ValueError(f'Dia da semana inválido: {", ".join(sorted(desconhecidos))}.')
    resultado = {}
    for dia in DIAS_SEMANA:
        valor = dados.get(dia)
        if valor in (None, '', False):
            resultado[dia] = None
            continue
        try:
            parse_intervalo(valor)
        except ValueError as e:
            raise ValueError(f'{ROTULOS_DIA_SEMANA[dia]}: {e}')
        resultado[dia] = str(valor).strip()
    return resultado


def carregar_horarios(valor):
    """Lê a coluna JSON; valores corrompidos são tratados como 'sem horário cadastrado'."""
    if isinstance(valor, dict):
        return valor
    if not valor:
        return {dia: None for dia in DIAS_SEMANA}
    try:
        return normalizar_horarios(valor)
    except ValueError:
        return {dia: None for dia in DIAS_SEMANA}


def horarios_uniformes(abertura, fechamento, dias=DIAS_SEMANA):
    intervalo = f'{abertura}-{fechamento}'
    return {dia: (intervalo if dia in dias else None) for dia in DIAS_SEMANA}


def _intervalos_do_dia(horarios, indice_dia):
    valor = horarios.get(DIAS_SEMANA[indice_dia % 7])
    if not valor:
        return None
    try:
        return parse_intervalo(valor)
    except ValueError:
        return None


def esta_aberta(horarios, aberta_24h=False, quando=None):
    if aberta_24h:
        return True
    quando = _para_sao_paulo(quando)
    horarios = carregar_horarios(horarios)
    dia = quando.weekday()
    minuto = quando.hour * 60 + quando.minute

    hoje = _intervalos_do_dia(horarios, dia)
    if hoje:
        inicio, fim = hoje
        if inicio < fim and inicio <= minuto < fim:
            return True
        if fim <= inicio and minuto >= inicio:
            return True

    ontem = _intervalos_do_dia(horarios, dia - 1)
    if ontem:
        inicio, fim = ontem
        if fim <= inicio and minuto < fim:
            return True
    return False


def minutos_para_abrir(horarios, aberta_24h=False, quando=None, limite_minutos=24 * 60):
    """0 se aberta agora; minutos até a próxima abertura se <= limite; senão None."""
    if esta_aberta(horarios, aberta_24h, quando):
        return 0
    quando = _para_sao_paulo(quando)
    horarios = carregar_horarios(horarios)
    dia = quando.weekday()
    minuto = quando.hour * 60 + quando.minute
    candidatos = []
    for deslocamento in (0, 1):
        intervalo = _intervalos_do_dia(horarios, dia + deslocamento)
        if not intervalo:
            continue
        espera = intervalo[0] + deslocamento * MINUTOS_DIA - minuto
        if espera > 0:
            candidatos.append(espera)
    if not candidatos:
        return None
    espera = min(candidatos)
    return espera if espera <= limite_minutos else None


def resumo_horarios(horarios, aberta_24h=False):
    if aberta_24h:
        return 'Aberta 24 horas, todos os dias'
    horarios = carregar_horarios(horarios)
    grupos = []
    for dia in DIAS_SEMANA:
        valor = horarios.get(dia) or 'fechado'
        if grupos and grupos[-1][2] == valor:
            grupos[-1][1] = dia
        else:
            grupos.append([dia, dia, valor])
    partes = []
    for inicio, fim, valor in grupos:
        rotulo = ROTULOS_DIA_SEMANA[inicio][:3]
        if fim != inicio:
            rotulo += '–' + ROTULOS_DIA_SEMANA[fim][:3]
        partes.append(f'{rotulo} {valor.replace("-", "–")}')
    return '; '.join(partes)

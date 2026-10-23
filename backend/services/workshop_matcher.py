"""Recomendação de oficinas por compatibilidade (módulo puro, sem acesso a banco).

1. Filtro eliminatório: ativa, atende o problema, atende o veículo, guincho em pane total,
   aberta agora (ou abrindo dentro da janela) no fuso America/Sao_Paulo e dentro do raio.
2. Ordenação das compatíveis: distância (0,1 km) e desempate por aberta agora, guincho, favorita e nome.
3. Sem compatíveis: motivo principal + alternativas parciais rotuladas como NÃO compatíveis.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from constantes import ESPECIALIDADE_PARA_NAO_IDENTIFICADO
from horarios import minutos_para_abrir
from utils import haversine

ORDEM_CRITERIOS = ['inativa', 'problema', 'veiculo', 'guincho', 'horario', 'raio']

ROTULOS_INCOMPATIBILIDADE = {
    'inativa': 'Oficina inativa',
    'problema': 'Não atende este tipo de problema',
    'veiculo': 'Não atende este tipo de veículo',
    'guincho': 'Sem guincho (exigido em pane total)',
    'horario': 'Fechada no momento',
    'raio': 'Fora do raio de busca',
}

MAX_ALTERNATIVAS = 5


@dataclass
class CriteriosBusca:
    tipo_problema: str
    tipo_veiculo: str
    pane_total: bool = False
    lat: Optional[float] = None
    lon: Optional[float] = None
    raio_km: Optional[float] = None
    quando: Optional[datetime] = None
    janela_minutos: int = 0
    favoritos: set = field(default_factory=set)

    @property
    def tem_localizacao(self):
        return self.lat is not None and self.lon is not None


def _lista(valor):
    if isinstance(valor, (list, tuple, set)):
        return [str(v).strip().lower() for v in valor if str(v).strip()]
    return [v.strip().lower() for v in str(valor or '').split(',') if v.strip()]


def atende_problema(oficina, tipo_problema):
    tipo = (tipo_problema or '').strip().lower()
    especialidades = _lista(oficina.get('especialidades'))
    if tipo == 'não identificado':
        return ESPECIALIDADE_PARA_NAO_IDENTIFICADO in especialidades
    return tipo in especialidades


def atende_veiculo(oficina, tipo_veiculo):
    return (tipo_veiculo or '').strip().lower() in _lista(oficina.get('tipos_veiculo'))


class WorkshopMatcher:

    def avaliar(self, oficina, criterios):
        """Devolve a oficina enriquecida com distância, horário e lista de incompatibilidades."""
        motivos = []
        if not oficina.get('ativa'):
            motivos.append('inativa')
        if not atende_problema(oficina, criterios.tipo_problema):
            motivos.append('problema')
        if not atende_veiculo(oficina, criterios.tipo_veiculo):
            motivos.append('veiculo')
        if criterios.pane_total and not oficina.get('tem_guincho'):
            motivos.append('guincho')

        abre_em = minutos_para_abrir(
            oficina.get('horarios'), bool(oficina.get('aberta_24h')), criterios.quando,
            limite_minutos=max(0, int(criterios.janela_minutos or 0)),
        )
        if abre_em is None:
            motivos.append('horario')

        distancia = None
        if criterios.tem_localizacao and oficina.get('lat') is not None and oficina.get('lon') is not None:
            distancia = round(haversine(
                float(criterios.lat), float(criterios.lon), float(oficina['lat']), float(oficina['lon'])
            ), 1)
        if criterios.raio_km is not None and criterios.tem_localizacao:
            if distancia is None or distancia > criterios.raio_km:
                motivos.append('raio')

        avaliada = dict(oficina)
        avaliada.update({
            'distancia': distancia,
            'aberta_agora': abre_em == 0,
            'abre_em_minutos': abre_em if abre_em else None,
            'favoritada': oficina.get('id') in criterios.favoritos,
            'atende_tipo': 'problema' not in motivos,
            'atende_veiculo': 'veiculo' not in motivos,
            'compativel': not motivos,
            'motivos_incompatibilidade': [ROTULOS_INCOMPATIBILIDADE[m] for m in motivos],
            '_codigos': motivos,
        })
        return avaliada

    @staticmethod
    def chave_ordenacao(of):
        return (
            of['distancia'] if of['distancia'] is not None else float('inf'),
            0 if of['aberta_agora'] else 1,
            0 if of.get('tem_guincho') else 1,
            0 if of['favoritada'] else 1,
            (of.get('nome') or '').lower(),
        )

    @staticmethod
    def motivo_principal(avaliadas):
        """Primeiro critério (na ordem oficial) que zera a lista de candidatas."""
        restantes = avaliadas
        if not restantes:
            return 'nenhuma_ativa'
        for criterio in ORDEM_CRITERIOS:
            restantes = [o for o in restantes if criterio not in o['_codigos']]
            if not restantes:
                return 'nenhuma_ativa' if criterio == 'inativa' else criterio
        return None

    @staticmethod
    def detalhe(motivo, criterios):
        if motivo is None:
            return None
        textos = {
            'nenhuma_ativa': 'Não há oficinas ativas cadastradas.',
            'problema': f'Nenhuma oficina atende o problema "{criterios.tipo_problema}".',
            'veiculo': (f'Nenhuma oficina que atende o problema "{criterios.tipo_problema}" '
                        f'atende veículo {criterios.tipo_veiculo}.'),
            'guincho': 'Nenhuma oficina compatível possui guincho, exigido para pane total.',
            'horario': ('Nenhuma oficina compatível está aberta agora'
                        + (f' nem abre nos próximos {criterios.janela_minutos} min.'
                           if criterios.janela_minutos else '.')),
            'raio': f'Nenhuma oficina compatível dentro do raio de {criterios.raio_km:g} km.'
                    if criterios.raio_km is not None else 'Nenhuma oficina compatível no raio informado.',
        }
        return textos[motivo]

    @classmethod
    def mensagem(cls, motivo, criterios):
        if motivo is None:
            return None
        return 'Nenhuma oficina compatível encontrada. ' + cls.detalhe(motivo, criterios)

    def recomendar(self, oficinas, criterios):
        avaliadas = [self.avaliar(of, criterios) for of in oficinas]
        compativeis = sorted((o for o in avaliadas if o['compativel']), key=self.chave_ordenacao)
        motivo = None
        alternativas = []
        if not compativeis:
            ativas = [o for o in avaliadas if 'inativa' not in o['_codigos']]
            motivo = self.motivo_principal(ativas)
            alternativas = sorted(
                ativas, key=lambda o: (len(o['_codigos']),) + self.chave_ordenacao(o)
            )[:MAX_ALTERNATIVAS]
        for o in avaliadas:
            o.pop('_codigos', None)
        return {
            'oficinas': compativeis,
            'alternativas': alternativas,
            'motivo': motivo,
            'mensagem': self.mensagem(motivo, criterios),
            'detalhe': self.detalhe(motivo, criterios),
            'total_avaliadas': len(avaliadas),
        }

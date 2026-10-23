"""Fase 2: testes unitários do WorkshopMatcher (sem banco) e da API de busca."""
import unittest
from datetime import datetime

from tests.base import FixTruckTestCase
from horarios import FUSO_SAO_PAULO, esta_aberta, minutos_para_abrir
from services.workshop_matcher import CriteriosBusca, WorkshopMatcher

# Quarta-feira, 10:00 em São Paulo.
QUARTA_10H = datetime(2026, 10, 21, 10, 0, tzinfo=FUSO_SAO_PAULO)
COMERCIAL = {'seg': '08:00-18:00', 'ter': '08:00-18:00', 'qua': '08:00-18:00', 'qui': '08:00-18:00',
             'sex': '08:00-18:00', 'sab': None, 'dom': None}

# Ponto de referência (ocorrência) e deslocamentos aproximados em longitude (~1 km = 0,0098° nesta latitude).
LAT, LON = -21.76, -43.35


def oficina(id_, km=1.0, **extra):
    dados = {
        'id': id_, 'nome': f'Oficina {id_}', 'ativa': True,
        'lat': LAT, 'lon': LON + km * 0.00966,
        'especialidades': 'mecânica,elétrica', 'tipos_veiculo': 'leve,médio,pesado',
        'tem_guincho': False, 'aberta_24h': False, 'horarios': COMERCIAL,
    }
    dados.update(extra)
    return dados


def criterios(**extra):
    dados = dict(tipo_problema='mecânica', tipo_veiculo='pesado', pane_total=False,
                 lat=LAT, lon=LON, raio_km=None, quando=QUARTA_10H, janela_minutos=0)
    dados.update(extra)
    return CriteriosBusca(**dados)


class WorkshopMatcherTest(unittest.TestCase):

    def setUp(self):
        self.m = WorkshopMatcher()

    def ids(self, resultado, chave='oficinas'):
        return [o['id'] for o in resultado[chave]]

    def test_problema_incompativel_e_eliminado(self):
        r = self.m.recomendar([oficina(1, especialidades='borracharia'), oficina(2)], criterios())
        self.assertEqual(self.ids(r), [2])

    def test_veiculo_incompativel_e_eliminado(self):
        r = self.m.recomendar([oficina(1, tipos_veiculo='leve'), oficina(2)], criterios())
        self.assertEqual(self.ids(r), [2])

    def test_pane_total_exige_guincho(self):
        r = self.m.recomendar([oficina(1, km=0.5), oficina(2, km=5, tem_guincho=True)],
                              criterios(pane_total=True))
        self.assertEqual(self.ids(r), [2])
        sem_pane = self.m.recomendar([oficina(1, km=0.5), oficina(2, km=5, tem_guincho=True)], criterios())
        self.assertEqual(self.ids(sem_pane), [1, 2])

    def test_fechada_e_eliminada(self):
        domingo = datetime(2026, 10, 25, 10, 0, tzinfo=FUSO_SAO_PAULO)
        r = self.m.recomendar([oficina(1), oficina(2, aberta_24h=True, horarios=None)], criterios(quando=domingo))
        self.assertEqual(self.ids(r), [2])

    def test_janela_de_abertura_aceita_oficina_que_abre_em_breve(self):
        as_7h30 = datetime(2026, 10, 21, 7, 30, tzinfo=FUSO_SAO_PAULO)
        self.assertEqual(self.ids(self.m.recomendar([oficina(1)], criterios(quando=as_7h30))), [])
        r = self.m.recomendar([oficina(1)], criterios(quando=as_7h30, janela_minutos=60))
        self.assertEqual(self.ids(r), [1])
        self.assertFalse(r['oficinas'][0]['aberta_agora'])
        self.assertEqual(r['oficinas'][0]['abre_em_minutos'], 30)

    def test_fora_do_raio_e_eliminada(self):
        r = self.m.recomendar([oficina(1, km=3), oficina(2, km=30)], criterios(raio_km=10))
        self.assertEqual(self.ids(r), [1])

    def test_oficina_inativa_e_eliminada(self):
        r = self.m.recomendar([oficina(1, ativa=False), oficina(2, km=9)], criterios())
        self.assertEqual(self.ids(r), [2])

    def test_ordena_por_distancia(self):
        r = self.m.recomendar([oficina(1, km=20), oficina(2, km=2), oficina(3, km=8)], criterios())
        self.assertEqual(self.ids(r), [2, 3, 1])
        self.assertLess(r['oficinas'][0]['distancia'], r['oficinas'][1]['distancia'])

    def test_compativel_distante_vence_incompativel_proxima(self):
        """Regressão: oficina que não resolve o problema nunca aparece antes (nem na lista principal)."""
        r = self.m.recomendar([oficina(1, km=0.2, especialidades='borracharia'), oficina(2, km=40)], criterios())
        self.assertEqual(self.ids(r), [2])

    def test_desempate_aberta_agora_guincho_favorita(self):
        as_7h30 = datetime(2026, 10, 21, 7, 30, tzinfo=FUSO_SAO_PAULO)
        mesma_distancia = [
            oficina(1, km=5),                                           # abre às 08:00
            oficina(2, km=5, aberta_24h=True, horarios=None),           # aberta agora
            oficina(3, km=5, aberta_24h=True, horarios=None, tem_guincho=True),
            oficina(4, km=5, aberta_24h=True, horarios=None, tem_guincho=True),  # favorita
        ]
        r = self.m.recomendar(mesma_distancia, criterios(quando=as_7h30, janela_minutos=60, favoritos={4}))
        self.assertEqual(self.ids(r), [4, 3, 2, 1])

    def test_sem_resultados_motivo_problema(self):
        r = self.m.recomendar([oficina(1, especialidades='borracharia')], criterios())
        self.assertEqual(r['oficinas'], [])
        self.assertEqual(r['motivo'], 'problema')
        self.assertTrue(r['mensagem'].startswith('Nenhuma oficina compatível encontrada'))

    def test_sem_resultados_motivo_guincho(self):
        r = self.m.recomendar([oficina(1)], criterios(pane_total=True))
        self.assertEqual(r['motivo'], 'guincho')

    def test_sem_resultados_motivo_horario(self):
        r = self.m.recomendar([oficina(1)], criterios(quando=datetime(2026, 10, 21, 22, 0, tzinfo=FUSO_SAO_PAULO)))
        self.assertEqual(r['motivo'], 'horario')

    def test_sem_resultados_motivo_raio(self):
        r = self.m.recomendar([oficina(1, km=50)], criterios(raio_km=10))
        self.assertEqual(r['motivo'], 'raio')

    def test_sem_oficinas_ativas(self):
        r = self.m.recomendar([oficina(1, ativa=False)], criterios())
        self.assertEqual(r['motivo'], 'nenhuma_ativa')
        self.assertEqual(r['alternativas'], [])

    def test_alternativas_separadas_e_rotuladas(self):
        r = self.m.recomendar([oficina(1, especialidades='borracharia'), oficina(2, tipos_veiculo='leve')],
                              criterios())
        self.assertEqual(r['oficinas'], [])
        self.assertEqual(len(r['alternativas']), 2)
        for alt in r['alternativas']:
            self.assertFalse(alt['compativel'])
            self.assertTrue(alt['motivos_incompatibilidade'])

    def test_nao_identificado_atendido_por_mecanica_geral(self):
        r = self.m.recomendar([oficina(1), oficina(2, especialidades='elétrica')],
                              criterios(tipo_problema='não identificado'))
        self.assertEqual(self.ids(r), [1])

    def test_sem_localizacao_nao_aplica_raio(self):
        r = self.m.recomendar([oficina(1, km=500)], criterios(lat=None, lon=None, raio_km=10))
        self.assertEqual(self.ids(r), [1])
        self.assertIsNone(r['oficinas'][0]['distancia'])


class HorariosTest(unittest.TestCase):

    def test_intervalo_que_atravessa_meia_noite(self):
        noturno = {d: '22:00-06:00' for d in ('seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom')}
        self.assertTrue(esta_aberta(noturno, quando=datetime(2026, 10, 21, 23, 0, tzinfo=FUSO_SAO_PAULO)))
        self.assertTrue(esta_aberta(noturno, quando=datetime(2026, 10, 21, 3, 0, tzinfo=FUSO_SAO_PAULO)))
        self.assertFalse(esta_aberta(noturno, quando=datetime(2026, 10, 21, 12, 0, tzinfo=FUSO_SAO_PAULO)))

    def test_madrugada_de_sabado_usa_intervalo_de_sexta(self):
        so_sexta = {'sex': '20:00-04:00'}
        sabado_2h = datetime(2026, 10, 24, 2, 0, tzinfo=FUSO_SAO_PAULO)
        self.assertTrue(esta_aberta(so_sexta, quando=sabado_2h))

    def test_24h(self):
        self.assertTrue(esta_aberta(None, aberta_24h=True, quando=QUARTA_10H))

    def test_fuso_sao_paulo_aplicado_a_horario_utc(self):
        from datetime import timezone
        # 12:00 UTC = 09:00 em São Paulo (aberta); 22:00 UTC = 19:00 (fechada).
        self.assertTrue(esta_aberta(COMERCIAL, quando=datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)))
        self.assertFalse(esta_aberta(COMERCIAL, quando=datetime(2026, 10, 21, 22, 0, tzinfo=timezone.utc)))

    def test_minutos_para_abrir_no_dia_seguinte(self):
        terca_23h = datetime(2026, 10, 20, 23, 0, tzinfo=FUSO_SAO_PAULO)
        self.assertEqual(minutos_para_abrir(COMERCIAL, quando=terca_23h, limite_minutos=600), 540)
        self.assertIsNone(minutos_para_abrir(COMERCIAL, quando=terca_23h, limite_minutos=60))


class BuscaOficinasApiTest(FixTruckTestCase):

    def setUp(self):
        super().setUp()
        self.h = self.login_empresa()

    def criar_ocorrencia(self, **extra):
        veiculo = self.sql("SELECT id FROM veiculos WHERE placa='ABC1D23'")[0]['id']
        corpo = {'veiculo_id': veiculo, 'tipo_problema': 'mecânica', 'pane_total': False,
                 'lat': '-23.5613', 'lon': '-46.6558', 'endereco': 'Av. Paulista — São Paulo/SP'}
        corpo.update(extra)
        r = self.post('/api/ocorrencias', corpo, self.h)
        self.assertEqual(r.status_code, 201, r.get_json())
        return r.get_json()['id']

    def test_lista_principal_so_tem_compativeis(self):
        oc = self.criar_ocorrencia(pane_total=True)
        r = self.get(f'/api/ocorrencias/{oc}/buscar-oficinas?janela=720', self.h).get_json()
        self.assertTrue(r['oficinas'])
        for of in r['oficinas']:
            self.assertTrue(of['compativel'])
            self.assertIn('mecânica', of['especialidades'])
            self.assertIn('pesado', of['tipos_veiculo'])
            self.assertTrue(of['tem_guincho'])
        distancias = [of['distancia'] for of in r['oficinas']]
        self.assertEqual(distancias, sorted(distancias))

    def test_resposta_explicita_sem_compativeis(self):
        oc = self.criar_ocorrencia(lat='-3.10', lon='-60.02', endereco='Manaus/AM')
        r = self.get(f'/api/ocorrencias/{oc}/buscar-oficinas?raio=50&janela=720', self.h).get_json()
        self.assertEqual(r['oficinas'], [])
        self.assertEqual(r['motivo'], 'raio')
        self.assertIn('Nenhuma oficina compatível encontrada', r['mensagem'])

    def test_raio_invalido(self):
        oc = self.criar_ocorrencia()
        self.assertEqual(self.get(f'/api/ocorrencias/{oc}/buscar-oficinas?raio=-5', self.h).status_code, 422)
        self.assertEqual(self.get(f'/api/ocorrencias/{oc}/buscar-oficinas?janela=9999', self.h).status_code, 422)


if __name__ == '__main__':
    unittest.main()

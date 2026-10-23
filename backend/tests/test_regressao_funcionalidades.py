"""Regressão: caminho feliz das funcionalidades que já existiam antes das fases 1–5."""
from tests.base import FixTruckTestCase


class RegressaoTestCase(FixTruckTestCase):
    def setUp(self):
        super().setUp()
        self.h = self.login_empresa()

    def id_de(self, query, params=()):
        return self.sql(query, params)[0][0]

    def nova_ocorrencia(self, **extra):
        dados = {'veiculo_id': self.id_de("SELECT id FROM veiculos WHERE placa='ABC1D23'"),
                 'tipo_problema': 'mecânica', 'lat': -23.55, 'lon': -46.63,
                 'endereco': 'Av. Paulista, 1000 — São Paulo'}
        dados.update(extra)
        r = self.post('/api/ocorrencias', dados, self.h)
        self.assertEqual(r.status_code, 201, r.get_json())
        return r.get_json()['id']

    def ocorrencia(self, oc_id):
        r = self.get(f'/api/ocorrencias/{oc_id}', self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        return r.get_json()['ocorrencia']


class TestEmpresa(RegressaoTestCase):
    def test_cadastro_login_e_me(self):
        h = self.criar_empresa('Nova Transportes', 'nova@fixtruck.com', 'segredo1')
        me = self.get('/api/auth/me', h).get_json()
        self.assertEqual(me['empresa']['email'], 'nova@fixtruck.com')

    def test_login_com_senha_errada(self):
        r = self.post('/api/auth/login', {'email': 'demo@fixtruck.com', 'senha': 'errada'})
        self.assertEqual(r.status_code, 401)

    def test_perfil_le_e_atualiza(self):
        self.assertEqual(self.get('/api/perfil', self.h).status_code, 200)
        r = self.put('/api/perfil', {'nome': 'Demo Atualizada', 'qtd_caminhoes': 20}, self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(self.id_de("SELECT nome FROM empresas WHERE email='demo@fixtruck.com'"), 'Demo Atualizada')


class TestFrota(RegressaoTestCase):
    def test_cadastra_motorista_e_veiculo_e_vincula(self):
        r = self.post('/api/frota/motoristas', {'nome': 'Pedro Lima', 'cnh': '11122233344'}, self.h)
        self.assertEqual(r.status_code, 201, r.get_json())
        motorista_id = self.id_de("SELECT id FROM motoristas WHERE nome='Pedro Lima'")
        r = self.post('/api/frota/veiculos', {'placa': 'xyz-9a87', 'modelo': 'Atego', 'tipo_veiculo': 'médio'}, self.h)
        self.assertEqual(r.status_code, 201, r.get_json())
        veiculo_id = r.get_json()['id']
        r = self.post(f'/api/frota/veiculos/{veiculo_id}/vincular', {'motorista_id': motorista_id}, self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        frota = self.get('/api/frota', self.h).get_json()
        veiculo = next(v for v in frota['veiculos'] if v['id'] == veiculo_id)
        self.assertEqual(veiculo['placa'], 'XYZ9A87')
        self.assertEqual(veiculo['motorista_id'], motorista_id)


class TestCicloDaOcorrencia(RegressaoTestCase):
    def test_registra_edita_vincula_oficina_e_encerra(self):
        oc_id = self.nova_ocorrencia()
        self.assertEqual(self.ocorrencia(oc_id)['status'], 'aberta')

        r = self.put(f'/api/ocorrencias/{oc_id}', {
            'veiculo_id': self.id_de("SELECT id FROM veiculos WHERE placa='ABC1D23'"),
            'tipo_problema': 'elétrica', 'lat': -23.55, 'lon': -46.63,
            'endereco': 'Av. Paulista, 1000 — São Paulo'}, self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(self.ocorrencia(oc_id)['tipo_problema'], 'elétrica')

        oficina_id = self.id_de('SELECT id FROM oficinas WHERE ativa=1 ORDER BY id LIMIT 1')
        r = self.post(f'/api/ocorrencias/{oc_id}/vincular-oficina', {'oficina_id': oficina_id}, self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        oc = self.ocorrencia(oc_id)
        self.assertEqual((oc['status'], oc['oficina_id']), ('em_atendimento', oficina_id))
        self.assertTrue(oc['data_vinculacao'])

        r = self.post(f'/api/ocorrencias/{oc_id}/encerrar', {
            'oficina_id': oficina_id, 'motivo_resolucao': 'Troca de peça', 'observacoes': 'Alternador'}, self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        oc = self.ocorrencia(oc_id)
        self.assertEqual(oc['status'], 'resolvido')
        self.assertTrue(oc['data_encerramento'])

    def test_atualiza_status_manualmente(self):
        oc_id = self.nova_ocorrencia()
        r = self.patch(f'/api/ocorrencias/{oc_id}/status', {'status': 'em_atendimento'}, self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(self.ocorrencia(oc_id)['status'], 'em_atendimento')

    def test_lista_com_filtro_de_status(self):
        oc_id = self.nova_ocorrencia()
        dados = self.get('/api/ocorrencias?status=aberta', self.h).get_json()
        ids = [o['id'] for o in dados['ocorrencias']]
        self.assertIn(oc_id, ids)
        self.assertTrue(all(o['status'] == 'aberta' for o in dados['ocorrencias']))


class TestFavoritosDashboardRelatorio(RegressaoTestCase):
    def test_favoritar_e_desfavoritar(self):
        oficina_id = self.id_de('SELECT id FROM oficinas WHERE ativa=1 ORDER BY id LIMIT 1')
        r = self.post(f'/api/oficinas/{oficina_id}/favoritar', headers=self.h)
        self.assertTrue(r.get_json()['favoritada'])
        favoritas = [o['id'] for o in self.get('/api/oficinas', self.h).get_json()['oficinas'] if o['favoritada']]
        self.assertEqual(favoritas, [oficina_id])
        r = self.post(f'/api/oficinas/{oficina_id}/favoritar', headers=self.h)
        self.assertFalse(r.get_json()['favoritada'])

    def test_dashboard_reflete_nova_ocorrencia(self):
        antes = self.get('/api/dashboard', self.h).get_json()
        self.nova_ocorrencia()
        depois = self.get('/api/dashboard', self.h).get_json()
        self.assertEqual(depois['ocorrencias_abertas'], antes['ocorrencias_abertas'] + 1)
        self.assertEqual(depois['total_ocorrencias'], antes['total_ocorrencias'] + 1)

    def test_relatorio_conta_por_tipo(self):
        self.nova_ocorrencia(tipo_problema='borracharia')
        dados = self.get('/api/relatorios', self.h).get_json()
        tipos = {linha['tipo_problema']: linha['c'] for linha in dados['por_tipo']}
        self.assertGreaterEqual(tipos.get('borracharia', 0), 1)

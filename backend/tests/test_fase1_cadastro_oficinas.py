"""Fase 1: CRUD mínimo de oficinas (criar, listar, editar, ativar/desativar) com validação."""
import unittest

from tests.base import FixTruckTestCase, oficina_valida


class CadastroOficinasTest(FixTruckTestCase):

    def setUp(self):
        super().setUp()
        self.h = self.login_empresa()

    def criar(self, **extra):
        r = self.post('/api/oficinas', oficina_valida(**extra), self.h)
        self.assertEqual(r.status_code, 201, r.get_json())
        return r.get_json()['oficina']

    def test_exige_autenticacao(self):
        self.assertEqual(self.post('/api/oficinas', oficina_valida()).status_code, 401)
        self.assertEqual(self.get('/api/oficinas/minhas').status_code, 401)

    def test_criar_e_listar(self):
        of = self.criar()
        self.assertTrue(of['ativa'])
        self.assertEqual(of['especialidades'], 'mecânica,elétrica')
        minhas = self.get('/api/oficinas/minhas', self.h).get_json()['oficinas']
        self.assertEqual([o['id'] for o in minhas], [of['id']])
        busca = self.get('/api/oficinas?busca=Teste Estrada', self.h).get_json()['oficinas']
        self.assertEqual(len(busca), 1)

    def test_criar_oficina_24h_dispensa_horarios(self):
        of = self.criar(aberta_24h=True, horarios=None)
        self.assertTrue(of['aberta_24h'])
        self.assertIn('24 horas', of['horario_resumo'])

    def test_validacoes(self):
        casos = {
            'nome vazio': {'nome': ''},
            'nome curto': {'nome': 'AB'},
            'nome longo': {'nome': 'x' * 101},
            'telefone': {'telefone': '1234'},
            'uf': {'uf': 'XX'},
            'latitude': {'lat': 95},
            'longitude': {'lon': 'abc'},
            'sem coordenadas': {'lat': None, 'lon': None},
            'especialidade inválida': {'especialidades': ['funilaria']},
            'sem especialidade': {'especialidades': []},
            'veículo inválido': {'tipos_veiculo': ['moto']},
            'horário inválido': {'horarios': {'seg': '25:00-18:00'}},
            'horário igual': {'horarios': {'seg': '08:00-08:00'}},
            'dia inválido': {'horarios': {'feriado': '08:00-12:00'}},
            'nenhum dia aberto': {'horarios': {}},
        }
        for nome, extra in casos.items():
            with self.subTest(nome):
                r = self.post('/api/oficinas', oficina_valida(**extra), self.h)
                self.assertEqual(r.status_code, 422, (nome, r.get_json()))
                self.assertIn('erro', r.get_json())

    def test_duplicada_retorna_409(self):
        self.criar()
        r = self.post('/api/oficinas', oficina_valida(), self.h)
        self.assertEqual(r.status_code, 409)

    def test_editar(self):
        of = self.criar()
        r = self.put(f"/api/oficinas/{of['id']}", oficina_valida(nome='Oficina Renomeada', tem_guincho=False), self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()['oficina']['nome'], 'Oficina Renomeada')
        self.assertFalse(r.get_json()['oficina']['tem_guincho'])

    def test_desativar_remove_da_busca_e_ativar_volta(self):
        of = self.criar()
        r = self.patch(f"/api/oficinas/{of['id']}/ativa", {'ativa': False}, self.h)
        self.assertEqual(r.status_code, 200)
        ids = [o['id'] for o in self.get('/api/oficinas', self.h).get_json()['oficinas']]
        self.assertNotIn(of['id'], ids)
        self.patch(f"/api/oficinas/{of['id']}/ativa", {'ativa': True}, self.h)
        ids = [o['id'] for o in self.get('/api/oficinas', self.h).get_json()['oficinas']]
        self.assertIn(of['id'], ids)

    def test_status_invalido(self):
        of = self.criar()
        self.assertEqual(self.patch(f"/api/oficinas/{of['id']}/ativa", {}, self.h).status_code, 422)

    def test_outra_empresa_nao_edita(self):
        of = self.criar()
        outra = self.criar_empresa()
        self.assertEqual(self.put(f"/api/oficinas/{of['id']}", oficina_valida(), outra).status_code, 403)
        self.assertEqual(self.patch(f"/api/oficinas/{of['id']}/ativa", {'ativa': False}, outra).status_code, 403)
        self.assertEqual(self.get('/api/oficinas/minhas', outra).get_json()['oficinas'], [])

    def test_oficina_do_seed_e_somente_leitura(self):
        seed_id = self.sql('SELECT id FROM oficinas WHERE empresa_id IS NULL LIMIT 1')[0]['id']
        self.assertEqual(self.patch(f'/api/oficinas/{seed_id}/ativa', {'ativa': False}, self.h).status_code, 403)

    def test_oficina_inexistente(self):
        self.assertEqual(self.put('/api/oficinas/99999', oficina_valida(), self.h).status_code, 404)

    def test_favoritar_oficina_inexistente_retorna_404(self):
        self.assertEqual(self.post('/api/oficinas/99999/favoritar', headers=self.h).status_code, 404)


if __name__ == '__main__':
    unittest.main()

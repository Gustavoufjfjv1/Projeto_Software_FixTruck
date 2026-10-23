import unittest

from tests.base import FixTruckTestCase

CARLOS = {'email': 'carlos@fixtruck.com', 'senha': 'motorista123'}
JOSE = {'email': 'jose@fixtruck.com', 'senha': 'trocar123'}


def ocorrencia_motorista(veiculo_id, **extra):
    dados = {
        'veiculo_id': veiculo_id,
        'tipo_problema': 'mecânica',
        'descricao': 'Motor perdendo força na subida',
        'pane_total': False,
        'lat': -21.76,
        'lon': -43.35,
        'endereco': 'BR-040 — KM 790 — Juiz de Fora',
    }
    dados.update(extra)
    return dados


class MotoristaTestCase(FixTruckTestCase):
    def login_motorista(self, credenciais=CARLOS):
        r = self.post('/api/motorista/login', credenciais)
        self.assertEqual(r.status_code, 200, r.get_json())
        return {'Authorization': 'Bearer ' + r.get_json()['token']}, r.get_json()

    def veiculo_id(self, placa):
        return self.sql('SELECT id FROM veiculos WHERE placa=?', (placa,))[0]['id']


class TestLoginMotorista(MotoristaTestCase):
    def test_login_valido(self):
        _, dados = self.login_motorista()
        self.assertEqual(dados['motorista']['nome'], 'Carlos Mendes')
        self.assertFalse(dados['trocar_senha'])
        self.assertNotIn('senha', dados['motorista'])

    def test_login_aceita_email_com_maiusculas_e_espacos(self):
        r = self.post('/api/motorista/login', {'email': '  Carlos@FixTruck.com ', 'senha': 'motorista123'})
        self.assertEqual(r.status_code, 200)

    def test_login_senha_errada_401(self):
        r = self.post('/api/motorista/login', {'email': CARLOS['email'], 'senha': 'errada'})
        self.assertEqual(r.status_code, 401)

    def test_login_email_inexistente_mesma_mensagem(self):
        r1 = self.post('/api/motorista/login', {'email': 'ninguem@x.com', 'senha': 'abc123'})
        r2 = self.post('/api/motorista/login', {'email': CARLOS['email'], 'senha': 'abc123'})
        self.assertEqual(r1.status_code, 401)
        self.assertEqual(r1.get_json(), r2.get_json())

    def test_motorista_sem_acesso_nao_loga(self):
        rows = self.sql("SELECT email, senha FROM motoristas WHERE nome='Ana Paula Souza'")
        self.assertIsNone(rows[0]['email'])
        self.assertIsNone(rows[0]['senha'])

    def test_senha_guardada_com_hash(self):
        senha = self.sql('SELECT senha FROM motoristas WHERE email=?', (CARLOS['email'],))[0]['senha']
        self.assertNotEqual(senha, CARLOS['senha'])
        self.assertTrue(senha.startswith(('pbkdf2:', 'scrypt:')))

    def test_motorista_inativo_nao_loga(self):
        self.sql('UPDATE motoristas SET ativo=0 WHERE email=?', (CARLOS['email'],))
        r = self.post('/api/motorista/login', CARLOS)
        self.assertEqual(r.status_code, 401)

    def test_sem_token_401(self):
        self.assertEqual(self.get('/api/motorista/ocorrencias').status_code, 401)
        self.assertEqual(self.get('/api/motorista/me').status_code, 401)

    def test_token_invalido_401(self):
        r = self.get('/api/motorista/ocorrencias', {'Authorization': 'Bearer lixo'})
        self.assertEqual(r.status_code, 401)


class TestTrocaDeSenha(MotoristaTestCase):
    def test_primeiro_acesso_exige_troca(self):
        h, dados = self.login_motorista(JOSE)
        self.assertTrue(dados['trocar_senha'])
        r = self.get('/api/motorista/ocorrencias', h)
        self.assertEqual(r.status_code, 403)
        self.assertTrue(r.get_json()['trocar_senha'])
        self.assertEqual(self.get('/api/motorista/me', h).status_code, 200)

    def test_troca_libera_acesso_e_invalida_token_antigo(self):
        h, _ = self.login_motorista(JOSE)
        r = self.post('/api/motorista/trocar-senha', {'senha_atual': JOSE['senha'], 'nova_senha': 'novaSenha9'}, h)
        self.assertEqual(r.status_code, 200, r.get_json())
        novo = {'Authorization': 'Bearer ' + r.get_json()['token']}
        self.assertEqual(self.get('/api/motorista/ocorrencias', novo).status_code, 200)
        self.assertEqual(self.get('/api/motorista/me', h).status_code, 401)
        self.assertEqual(self.post('/api/motorista/login', JOSE).status_code, 401)
        self.assertEqual(self.post('/api/motorista/login', {'email': JOSE['email'], 'senha': 'novaSenha9'}).status_code, 200)

    def test_troca_com_senha_atual_errada(self):
        h, _ = self.login_motorista(JOSE)
        r = self.post('/api/motorista/trocar-senha', {'senha_atual': 'xxx', 'nova_senha': 'novaSenha9'}, h)
        self.assertEqual(r.status_code, 401)

    def test_troca_nova_senha_curta_ou_igual(self):
        h, _ = self.login_motorista(JOSE)
        r = self.post('/api/motorista/trocar-senha', {'senha_atual': JOSE['senha'], 'nova_senha': '123'}, h)
        self.assertEqual(r.status_code, 422)
        r = self.post('/api/motorista/trocar-senha', {'senha_atual': JOSE['senha'], 'nova_senha': JOSE['senha']}, h)
        self.assertEqual(r.status_code, 422)


class TestAcessoDefinidoPelaEmpresa(MotoristaTestCase):
    def test_empresa_gera_senha_temporaria(self):
        h = self.login_empresa()
        ana = self.sql("SELECT id FROM motoristas WHERE nome='Ana Paula Souza'")[0]['id']
        r = self.post(f'/api/frota/motoristas/{ana}/acesso', {'email': 'ana@fixtruck.com'}, h)
        self.assertEqual(r.status_code, 200, r.get_json())
        temp = r.get_json()['senha_temporaria']
        self.assertGreaterEqual(len(temp), 6)
        r = self.post('/api/motorista/login', {'email': 'ana@fixtruck.com', 'senha': temp})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()['trocar_senha'])

    def test_cadastro_com_email_cria_acesso(self):
        h = self.login_empresa()
        r = self.post('/api/frota/motoristas', {'nome': 'Pedro Lima', 'email': 'pedro@fixtruck.com'}, h)
        self.assertEqual(r.status_code, 201, r.get_json())
        self.assertIn('senha_temporaria', r.get_json())

    def test_email_duplicado_409_e_nao_cria_motorista(self):
        h = self.login_empresa()
        antes = self.sql('SELECT COUNT(*) c FROM motoristas')[0]['c']
        r = self.post('/api/frota/motoristas', {'nome': 'Clone', 'email': CARLOS['email']}, h)
        self.assertEqual(r.status_code, 409)
        self.assertEqual(self.sql('SELECT COUNT(*) c FROM motoristas')[0]['c'], antes)

    def test_email_invalido_422(self):
        h = self.login_empresa()
        ana = self.sql("SELECT id FROM motoristas WHERE nome='Ana Paula Souza'")[0]['id']
        r = self.post(f'/api/frota/motoristas/{ana}/acesso', {'email': 'nao-e-email'}, h)
        self.assertEqual(r.status_code, 422)

    def test_empresa_nao_define_acesso_de_motorista_alheio(self):
        outra = self.criar_empresa()
        carlos = self.sql('SELECT id FROM motoristas WHERE email=?', (CARLOS['email'],))[0]['id']
        r = self.post(f'/api/frota/motoristas/{carlos}/acesso', {'email': 'hack@x.com'}, outra)
        self.assertEqual(r.status_code, 404)

    def test_lista_de_motoristas_nao_expoe_senha(self):
        h = self.login_empresa()
        for m in self.get('/api/frota', h).get_json()['motoristas']:
            self.assertNotIn('senha', m)


class TestOcorrenciasDoMotorista(MotoristaTestCase):
    def test_lista_so_ocorrencias_do_seu_veiculo(self):
        h, _ = self.login_motorista()
        dados = self.get('/api/motorista/ocorrencias', h).get_json()
        placas = {oc['veiculo_placa'] for oc in dados['ocorrencias']}
        self.assertEqual(placas, {'ABC1D23'})
        self.assertEqual(len(dados['ocorrencias']), 2)
        self.assertEqual([v['placa'] for v in dados['veiculos']], ['ABC1D23'])

    def test_filtro_abertas(self):
        h, _ = self.login_motorista()
        ocs = self.get('/api/motorista/ocorrencias?status=abertas', h).get_json()['ocorrencias']
        self.assertTrue(ocs)
        self.assertTrue(all(oc['status'] != 'resolvido' for oc in ocs))

    def test_registra_ocorrencia_do_veiculo_vinculado(self):
        h, _ = self.login_motorista()
        r = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(self.veiculo_id('ABC1D23')), h)
        self.assertEqual(r.status_code, 201, r.get_json())
        row = self.sql('SELECT * FROM ocorrencias WHERE id=?', (r.get_json()['id'],))[0]
        self.assertEqual(row['registrada_por'], 'motorista')
        carlos = self.sql('SELECT id FROM motoristas WHERE email=?', (CARLOS['email'],))[0]['id']
        self.assertEqual(row['motorista_id'], carlos)
        self.assertEqual(row['tipo_veiculo'], 'pesado')
        self.assertEqual(row['descricao'], 'Motor perdendo força na subida')

    def test_motorista_id_do_corpo_e_ignorado(self):
        h, _ = self.login_motorista()
        jose = self.sql('SELECT id FROM motoristas WHERE email=?', (JOSE['email'],))[0]['id']
        r = self.post('/api/motorista/ocorrencias',
                      ocorrencia_motorista(self.veiculo_id('ABC1D23'), motorista_id=jose), h)
        row = self.sql('SELECT motorista_id FROM ocorrencias WHERE id=?', (r.get_json()['id'],))[0]
        self.assertNotEqual(row['motorista_id'], jose)

    def test_nao_registra_para_veiculo_de_outro_motorista(self):
        h, _ = self.login_motorista()
        r = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(self.veiculo_id('DEF4G56')), h)
        self.assertEqual(r.status_code, 403)

    def test_nao_registra_sem_veiculo_ou_descricao(self):
        h, _ = self.login_motorista()
        r = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(None), h)
        self.assertEqual(r.status_code, 422)
        r = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(self.veiculo_id('ABC1D23'), descricao=''), h)
        self.assertEqual(r.status_code, 422)

    def test_nao_ve_ocorrencia_de_outro_motorista(self):
        h, _ = self.login_motorista()
        alheia = self.sql(
            "SELECT o.id FROM ocorrencias o JOIN veiculos v ON v.id=o.veiculo_id WHERE v.placa='DEF4G56'"
        )[0]['id']
        self.assertEqual(self.get(f'/api/motorista/ocorrencias/{alheia}', h).status_code, 404)
        self.assertEqual(self.get(f'/api/motorista/ocorrencias/{alheia}/buscar-oficinas', h).status_code, 404)

    def test_busca_oficinas_compativeis_da_propria_ocorrencia(self):
        h, _ = self.login_motorista()
        r = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(self.veiculo_id('ABC1D23')), h)
        oc_id = r.get_json()['id']
        r = self.get(f'/api/motorista/ocorrencias/{oc_id}/buscar-oficinas?janela=720', h)
        self.assertEqual(r.status_code, 200, r.get_json())
        dados = r.get_json()
        self.assertIn('oficinas', dados)
        for of in dados['oficinas']:
            self.assertIn('mecânica', of['especialidades'])
            self.assertIn('pesado', of['tipos_veiculo'])

    def test_form_data_lista_apenas_veiculos_vinculados(self):
        h, _ = self.login_motorista()
        dados = self.get('/api/motorista/form-data', h).get_json()
        self.assertEqual([v['placa'] for v in dados['veiculos']], ['ABC1D23'])
        self.assertTrue(dados['tipos_problema'])

    def test_desvincular_veiculo_tira_acesso_a_novas_ocorrencias(self):
        h, _ = self.login_motorista()
        self.sql("UPDATE veiculos SET motorista_id=NULL WHERE placa='ABC1D23'")
        r = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(self.veiculo_id('ABC1D23')), h)
        self.assertEqual(r.status_code, 403)

    def test_empresa_ve_ocorrencia_registrada_pelo_motorista(self):
        h, _ = self.login_motorista()
        oc_id = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(self.veiculo_id('ABC1D23')), h).get_json()['id']
        emp = self.login_empresa()
        r = self.get(f'/api/ocorrencias/{oc_id}', emp)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['ocorrencia']['registrada_por'], 'motorista')
        self.assertEqual(r.get_json()['ocorrencia']['descricao'], 'Motor perdendo força na subida')


class TestPapeisEIsolamento(MotoristaTestCase):
    ROTAS_EMPRESA = ['/api/dashboard', '/api/ocorrencias', '/api/frota', '/api/relatorios',
                     '/api/oficinas/minhas', '/api/oficinas', '/api/perfil', '/api/auth/me',
                     '/api/ocorrencias/form-data']

    def test_token_motorista_bloqueado_em_rotas_da_empresa(self):
        h, _ = self.login_motorista()
        for rota in self.ROTAS_EMPRESA:
            r = self.get(rota, h)
            self.assertEqual(r.status_code, 403, rota)
        r = self.post('/api/frota/motoristas', {'nome': 'X'}, h)
        self.assertEqual(r.status_code, 403)

    def test_token_empresa_bloqueado_em_rotas_do_motorista(self):
        h = self.login_empresa()
        self.assertEqual(self.get('/api/motorista/ocorrencias', h).status_code, 403)
        self.assertEqual(self.get('/api/motorista/me', h).status_code, 403)

    def test_motorista_de_outra_empresa_nao_ve_dados(self):
        outra = self.criar_empresa()
        r = self.post('/api/frota/motoristas', {'nome': 'Rui', 'email': 'rui@outra.com'}, outra)
        temp = r.get_json()['senha_temporaria']
        h, _ = self.login_motorista({'email': 'rui@outra.com', 'senha': temp})
        h = {'Authorization': 'Bearer ' + self.post(
            '/api/motorista/trocar-senha', {'senha_atual': temp, 'nova_senha': 'ruiSenha1'}, h).get_json()['token']}

        dados = self.get('/api/motorista/ocorrencias', h).get_json()
        self.assertEqual(dados['ocorrencias'], [])
        self.assertEqual(dados['veiculos'], [])
        demo_oc = self.sql("SELECT id FROM ocorrencias LIMIT 1")[0]['id']
        self.assertEqual(self.get(f'/api/motorista/ocorrencias/{demo_oc}', h).status_code, 404)
        r = self.post('/api/motorista/ocorrencias', ocorrencia_motorista(self.veiculo_id('ABC1D23')), h)
        self.assertEqual(r.status_code, 403)

    def test_empresa_nao_ve_ocorrencia_de_outra_empresa(self):
        outra = self.criar_empresa()
        demo_oc = self.sql("SELECT id FROM ocorrencias LIMIT 1")[0]['id']
        self.assertEqual(self.get(f'/api/ocorrencias/{demo_oc}', outra).status_code, 404)

    def test_motorista_desativado_perde_sessao(self):
        h, _ = self.login_motorista()
        self.sql('UPDATE motoristas SET ativo=0 WHERE email=?', (CARLOS['email'],))
        self.assertEqual(self.get('/api/motorista/ocorrencias', h).status_code, 401)


if __name__ == '__main__':
    unittest.main()

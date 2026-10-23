import os
import shutil
import sqlite3
import tempfile
import unittest

from tests.base import FixTruckTestCase
from app import create_app
from database import init_db
import email_simulado
import migracoes
from services.redefinir_senha_service import limpar_tentativas


class Fase4TestCase(FixTruckTestCase):
    def setUp(self):
        super().setUp()
        self.h = self.login_empresa()

    def id_de(self, query, params=()):
        return self.sql(query, params)[0][0]

    def veiculo(self, placa):
        return self.id_de('SELECT id FROM veiculos WHERE placa=?', (placa,))

    def ocorrencia_aberta(self):
        return self.id_de("SELECT id FROM ocorrencias WHERE status='aberta' ORDER BY id LIMIT 1")

    def oficina_ativa(self):
        return self.id_de('SELECT id FROM oficinas WHERE ativa=1 ORDER BY id LIMIT 1')

    def nova_ocorrencia(self, **extra):
        dados = {'veiculo_id': self.veiculo('ABC1D23'), 'tipo_problema': 'elétrica',
                 'lat': -23.55, 'lon': -46.63, 'endereco': 'Av. Paulista, 1000 — São Paulo'}
        dados.update(extra)
        return self.post('/api/ocorrencias', dados, self.h)


class TestEnumTipoProblema(Fase4TestCase):
    def test_opcoes_publicas_tem_lista_unica(self):
        tipos = [o['valor'] for o in self.get('/api/opcoes').get_json()['tipos_problema']]
        self.assertEqual(tipos, ['mecânica', 'elétrica', 'hidráulica', 'borracharia', 'não identificado'])

    def test_registrar_aceita_todos_os_tipos_oficiais(self):
        for tipo in ['mecânica', 'elétrica', 'hidráulica', 'borracharia', 'não identificado', 'MECÂNICA']:
            self.assertEqual(self.nova_ocorrencia(tipo_problema=tipo).status_code, 201, tipo)

    def test_registrar_rejeita_tipo_fora_do_enum(self):
        for tipo in ['pneu', 'freios', '', None, 123]:
            r = self.nova_ocorrencia(tipo_problema=tipo)
            self.assertEqual(r.status_code, 422, tipo)

    def test_editar_rejeita_tipo_fora_do_enum(self):
        oc = self.ocorrencia_aberta()
        r = self.put(f'/api/ocorrencias/{oc}', {'veiculo_id': self.veiculo('ABC1D23'), 'tipo_problema': 'pneu',
                                                'endereco': 'X'}, self.h)
        self.assertEqual(r.status_code, 422)

    def test_filtro_rejeita_tipo_invalido(self):
        self.assertEqual(self.get('/api/ocorrencias?tipo=pneu', self.h).status_code, 422)
        self.assertEqual(self.get('/api/ocorrencias?tipo=borracharia', self.h).status_code, 200)
        self.assertEqual(self.get('/api/ocorrencias?status=xyz', self.h).status_code, 422)
        self.assertEqual(self.get('/api/ocorrencias?veiculo=abc', self.h).status_code, 422)

    def test_banco_recusa_tipo_fora_do_enum(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("INSERT INTO ocorrencias (empresa_id, tipo_veiculo, tipo_problema) VALUES (1, 'pesado', 'pneu')")


class TestPlaca(Fase4TestCase):
    def cadastrar(self, placa, h=None, **extra):
        return self.post('/api/frota/veiculos', {'placa': placa, 'tipo_veiculo': 'pesado', **extra}, h or self.h)

    def test_placa_antiga_e_mercosul_normalizadas(self):
        r = self.cadastrar('abc-1234')
        self.assertEqual(r.status_code, 201, r.get_json())
        self.assertEqual(r.get_json()['placa'], 'ABC1234')
        r = self.cadastrar(' bra 2e19 ')
        self.assertEqual(r.get_json()['placa'], 'BRA2E19')
        placas = {row['placa'] for row in self.sql('SELECT placa FROM veiculos')}
        self.assertTrue({'ABC1234', 'BRA2E19'} <= placas)

    def test_placa_invalida_422(self):
        for placa in ['', '1234ABC', 'AB12345', 'ABCD123', 'ABC12345', 'ABC1DD3']:
            self.assertEqual(self.cadastrar(placa).status_code, 422, placa)

    def test_placa_duplicada_mensagem_amigavel(self):
        r = self.cadastrar('abc1d23')
        self.assertEqual(r.status_code, 409)
        self.assertIn('placa já está cadastrada', r.get_json()['erro'])

    def test_placa_unica_entre_empresas(self):
        outra = self.criar_empresa()
        self.assertEqual(self.cadastrar('ABC-1D23', outra).status_code, 409)

    def test_banco_tem_unique_na_placa(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("INSERT INTO veiculos (empresa_id, placa, tipo_veiculo) VALUES (1, 'ABC1D23', 'pesado')")

    def test_tipo_veiculo_invalido(self):
        self.assertEqual(self.cadastrar('XYZ9A99', tipo_veiculo='gigante').status_code, 422)


class TestPosse(Fase4TestCase):
    def test_registrar_com_veiculo_de_outra_empresa_403(self):
        outra = self.criar_empresa()
        r = self.post('/api/ocorrencias', {'veiculo_id': self.veiculo('ABC1D23'), 'tipo_problema': 'mecânica',
                                           'endereco': 'X'}, outra)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.sql("SELECT COUNT(*) FROM ocorrencias WHERE empresa_id <> 1")[0][0], 0)

    def test_registrar_com_veiculo_inexistente_ou_invalido_422(self):
        for vid in [99999, 'abc', -1, None, {'a': 1}, True]:
            self.assertEqual(self.nova_ocorrencia(veiculo_id=vid).status_code, 422, vid)

    def test_registrar_com_motorista_de_outra_empresa_403(self):
        outra = self.criar_empresa()
        mid = self.post('/api/frota/motoristas', {'nome': 'Fulano Alheio'}, outra).get_json()['id']
        self.assertEqual(self.nova_ocorrencia(motorista_id=mid).status_code, 403)

    def test_editar_ocorrencia_de_outra_empresa_404(self):
        outra = self.criar_empresa()
        oc = self.ocorrencia_aberta()
        r = self.put(f'/api/ocorrencias/{oc}', {'tipo_problema': 'mecânica'}, outra)
        self.assertEqual(r.status_code, 404)

    def test_editar_trocando_para_veiculo_alheio_403(self):
        outra = self.criar_empresa()
        vid = self.post('/api/frota/veiculos', {'placa': 'OUT1A11'}, outra).get_json()['id']
        oc = self.ocorrencia_aberta()
        r = self.put(f'/api/ocorrencias/{oc}', {'veiculo_id': vid, 'tipo_problema': 'mecânica', 'endereco': 'X'}, self.h)
        self.assertEqual(r.status_code, 403)

    def test_encerrar_valida_oficina_e_posse(self):
        oc = self.ocorrencia_aberta()
        outra = self.criar_empresa()
        self.assertEqual(self.post(f'/api/ocorrencias/{oc}/encerrar', {'oficina_id': self.oficina_ativa()}, outra).status_code, 404)
        self.assertEqual(self.post(f'/api/ocorrencias/{oc}/encerrar', {'oficina_id': 99999}, self.h).status_code, 422)
        self.assertEqual(self.post(f'/api/ocorrencias/{oc}/encerrar', {}, self.h).status_code, 422)
        r = self.post(f'/api/ocorrencias/{oc}/encerrar', {'oficina_id': self.oficina_ativa(), 'motivo': 'Reparo'}, self.h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.post(f'/api/ocorrencias/{oc}/encerrar', {'oficina_id': self.oficina_ativa()}, self.h).status_code, 409)

    def test_vincular_oficina_inativa_422(self):
        oc = self.ocorrencia_aberta()
        of = self.oficina_ativa()
        self.sql('UPDATE oficinas SET ativa=0 WHERE id=?', (of,))
        self.assertEqual(self.post(f'/api/ocorrencias/{oc}/vincular-oficina', {'oficina_id': of}, self.h).status_code, 422)

    def test_status_invalido_422_e_de_outra_empresa_404(self):
        oc = self.ocorrencia_aberta()
        self.assertEqual(self.patch(f'/api/ocorrencias/{oc}/status', {'status': 'resolvido'}, self.h).status_code, 422)
        outra = self.criar_empresa()
        self.assertEqual(self.patch(f'/api/ocorrencias/{oc}/status', {'status': 'aberta'}, outra).status_code, 404)

    def test_vincular_motorista_posse(self):
        outra = self.criar_empresa()
        mid = self.post('/api/frota/motoristas', {'nome': 'Fulano Alheio'}, outra).get_json()['id']
        vid = self.veiculo('ABC1D23')
        self.assertEqual(self.post(f'/api/frota/veiculos/{vid}/vincular', {'motorista_id': mid}, self.h).status_code, 403)
        self.assertEqual(self.post(f'/api/frota/veiculos/{vid}/vincular', {'motorista_id': 99999}, self.h).status_code, 422)
        self.assertEqual(self.post(f'/api/frota/veiculos/{vid}/vincular', {'motorista_id': None}, outra).status_code, 404)

    def test_cadastrar_veiculo_com_motorista_alheio_403(self):
        outra = self.criar_empresa()
        mid = self.post('/api/frota/motoristas', {'nome': 'Fulano Alheio'}, outra).get_json()['id']
        r = self.post('/api/frota/veiculos', {'placa': 'NEW1A23', 'motorista_id': mid}, self.h)
        self.assertEqual(r.status_code, 403)

    def test_rotas_inexistentes_e_json_invalido_nunca_500(self):
        self.assertEqual(self.get('/api/nao-existe', self.h).status_code, 404)
        r = self.client.post('/api/ocorrencias', data='{nao e json', headers={**self.h, 'Content-Type': 'application/json'})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self.get('/api/ocorrencias/99999', self.h).status_code, 404)


class TestChavesEstrangeiras(Fase4TestCase):
    def test_pragma_ligado_nas_duas_conexoes(self):
        from database import db, get_db
        with self.app.app_context():
            self.assertEqual(get_db().execute('PRAGMA foreign_keys').fetchone()[0], 1)
            self.assertEqual(db.session.execute(db.text('PRAGMA foreign_keys')).scalar(), 1)

    def test_schema_declara_on_delete_e_on_update(self):
        conn = sqlite3.connect(self.db_path)
        esperado = {
            ('motoristas', 'empresas'): 'CASCADE',
            ('veiculos', 'motoristas'): 'SET NULL',
            ('ocorrencias', 'veiculos'): 'SET NULL',
            ('ocorrencias', 'oficinas'): 'SET NULL',
            ('ocorrencias', 'empresas'): 'CASCADE',
            ('favoritos', 'oficinas'): 'CASCADE',
            ('oficinas', 'empresas'): 'SET NULL',
        }
        for (tabela, alvo), on_delete in esperado.items():
            fks = {r[2]: (r[5], r[6]) for r in conn.execute(f'PRAGMA foreign_key_list({tabela})')}
            self.assertEqual(fks[alvo], ('CASCADE', on_delete), (tabela, alvo))
        conn.close()

    def _conn_fk(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def test_apagar_motorista_desvincula_veiculo_e_ocorrencias(self):
        conn = self._conn_fk()
        mid = conn.execute("SELECT id FROM motoristas WHERE nome='Carlos Mendes'").fetchone()[0]
        conn.execute('DELETE FROM motoristas WHERE id=?', (mid,))
        conn.commit()
        self.assertIsNone(conn.execute("SELECT motorista_id FROM veiculos WHERE placa='ABC1D23'").fetchone()[0])
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM ocorrencias WHERE motorista_id=?', (mid,)).fetchone()[0], 0)
        conn.close()

    def test_referencia_inexistente_recusada(self):
        conn = self._conn_fk()
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO ocorrencias (empresa_id, tipo_veiculo, tipo_problema) VALUES (999, 'pesado', 'mecânica')")
        conn.close()

    def test_banco_sem_violacoes_apos_seed(self):
        conn = sqlite3.connect(self.db_path)
        self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(), [])
        conn.close()


class TestFormularios(Fase4TestCase):
    def test_cadastro_empresa(self):
        base = {'nome': 'Nova Transp', 'email': 'nova@x.com', 'senha': 'segredo1'}
        casos = [
            {'email': 'sem-arroba'}, {'email': ''}, {'senha': '123'}, {'nome': ''}, {'nome': 'A'},
            {'qtd_caminhoes': -1}, {'qtd_caminhoes': 'muitos'}, {'qtd_caminhoes': 2.5}, {'nome': 'x' * 121},
        ]
        for caso in casos:
            r = self.post('/api/auth/cadastro', {**base, **caso})
            self.assertEqual(r.status_code, 422, caso)
        self.assertEqual(self.post('/api/auth/cadastro', base).status_code, 201)
        self.assertEqual(self.post('/api/auth/cadastro', {**base, 'email': 'NOVA@x.com'}).status_code, 409)

    def test_perfil(self):
        self.assertEqual(self.put('/api/perfil', {'nome': '', 'qtd_caminhoes': 3}, self.h).status_code, 422)
        self.assertEqual(self.put('/api/perfil', {'nome': 'Demo', 'qtd_caminhoes': -3}, self.h).status_code, 422)
        self.assertEqual(self.put('/api/perfil', {'nome': 'Demo Transportes', 'qtd_caminhoes': 3}, self.h).status_code, 200)

    def test_cadastro_motorista(self):
        for caso in [{'nome': ''}, {'nome': 'Jo'}, {'nome': 'João Silva', 'cnh': '123'},
                     {'nome': 'João Silva', 'telefone': '1234'}, {'nome': 'João Silva', 'email': 'x@'}]:
            self.assertEqual(self.post('/api/frota/motoristas', caso, self.h).status_code, 422, caso)
        r = self.post('/api/frota/motoristas', {'nome': '  João   Silva ', 'cnh': '123.456.789-01',
                                                 'telefone': '32999990000'}, self.h)
        self.assertEqual(r.status_code, 201)
        row = self.sql('SELECT nome, cnh, telefone FROM motoristas WHERE id=?', (r.get_json()['id'],))[0]
        self.assertEqual((row['nome'], row['cnh'], row['telefone']), ('João Silva', '12345678901', '(32) 99999-0000'))

    def test_ocorrencia_coordenadas_e_tamanhos(self):
        self.assertEqual(self.nova_ocorrencia(lat=-91).status_code, 422)
        self.assertEqual(self.nova_ocorrencia(lon=181).status_code, 422)
        self.assertEqual(self.nova_ocorrencia(lat='abc').status_code, 422)
        self.assertEqual(self.nova_ocorrencia(lat=-23.5, lon=None, endereco='').status_code, 422)
        self.assertEqual(self.nova_ocorrencia(lat=None, lon=None, endereco='').status_code, 422)
        self.assertEqual(self.nova_ocorrencia(descricao='x' * 501).status_code, 422)
        self.assertEqual(self.nova_ocorrencia(lat=None, lon=None, endereco='', via='BR-040', km='12',
                                              cidade='Juiz de Fora').status_code, 201)

    def test_sanitiza_caracteres_de_controle(self):
        r = self.nova_ocorrencia(descricao='Motor\x00 fundido\x07   agora')
        row = self.sql('SELECT descricao FROM ocorrencias WHERE id=?', (r.get_json()['id'],))[0]
        self.assertEqual(row['descricao'], 'Motor fundido agora')


class TestRecuperacaoSenha(FixTruckTestCase):
    def setUp(self):
        super().setUp()
        email_simulado.CAIXA_DE_SAIDA.clear()
        limpar_tentativas()

    def pedir(self, email='demo@fixtruck.com'):
        return self.post('/api/auth/recuperar-senha', {'email': email})

    def ultimo_token(self):
        corpo = email_simulado.CAIXA_DE_SAIDA[-1]['corpo']
        return corpo.split('\n\n')[1].strip()

    def test_resposta_igual_para_email_existente_e_inexistente(self):
        r1, r2 = self.pedir(), self.pedir('ninguem@nada.com')
        self.assertEqual((r1.status_code, r1.get_json()), (r2.status_code, r2.get_json()))
        self.assertNotIn('token', r1.get_json())
        self.assertEqual(len(email_simulado.CAIXA_DE_SAIDA), 1)

    def test_email_invalido_422(self):
        self.assertEqual(self.pedir('nao-e-email').status_code, 422)

    def test_banco_guarda_so_o_hash(self):
        self.pedir()
        token = self.ultimo_token()
        self.assertGreaterEqual(len(token), 40)
        hashes = [r['token_hash'] for r in self.sql('SELECT token_hash FROM tokens_recuperacao')]
        self.assertNotIn(token, hashes)
        self.assertEqual(len(hashes[0]), 64)

    def test_fluxo_completo_e_uso_unico(self):
        self.pedir()
        token = self.ultimo_token()
        r = self.post('/api/auth/redefinir-senha', {'token': token, 'senha': 'novaSenha1'})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.login_empresa('demo@fixtruck.com', 'novaSenha1')
        r = self.post('/api/auth/redefinir-senha', {'token': token, 'senha': 'outraSenha2'})
        self.assertEqual(r.status_code, 400)

    def test_token_expirado(self):
        self.pedir()
        token = self.ultimo_token()
        self.sql("UPDATE tokens_recuperacao SET expira_em='2000-01-01 00:00:00'")
        self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': token, 'senha': 'novaSenha1'}).status_code, 400)

    def test_novo_pedido_invalida_o_anterior(self):
        self.pedir()
        antigo = self.ultimo_token()
        self.pedir()
        novo = self.ultimo_token()
        self.assertNotEqual(antigo, novo)
        self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': antigo, 'senha': 'novaSenha1'}).status_code, 400)
        self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': novo, 'senha': 'novaSenha1'}).status_code, 200)

    def test_limite_de_pedidos(self):
        for _ in range(5):
            self.assertEqual(self.pedir().status_code, 200)
        self.assertEqual(len(email_simulado.CAIXA_DE_SAIDA), 3)

    def test_limite_de_tentativas_invalidas(self):
        for _ in range(10):
            self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': 'chute', 'senha': 'novaSenha1'}).status_code, 400)
        self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': 'chute', 'senha': 'novaSenha1'}).status_code, 429)

    def test_senha_curta_e_token_vazio(self):
        self.pedir()
        token = self.ultimo_token()
        self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': token, 'senha': '123'}).status_code, 422)
        self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': '', 'senha': 'novaSenha1'}).status_code, 422)
        self.assertEqual(self.post('/api/auth/redefinir-senha', {'token': token, 'senha': 'novaSenha1'}).status_code, 200)


class TestMigracaoFase4(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='fixtruck-mig4-')
        self.db_path = os.path.join(self.tmpdir, 'legado.db')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def criar_legado(self, placas):
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE empresas (id INTEGER PRIMARY KEY, nome TEXT, email TEXT, senha TEXT, qtd_caminhoes INTEGER);
            CREATE TABLE veiculos (id INTEGER PRIMARY KEY, empresa_id INTEGER, placa TEXT, modelo TEXT, marca TEXT,
                tipo_veiculo TEXT, motorista_id INTEGER);
            CREATE TABLE ocorrencias (id INTEGER PRIMARY KEY, empresa_id INTEGER, motorista_id INTEGER, veiculo_id INTEGER,
                tipo_veiculo TEXT, tipo_problema TEXT, pane_total INTEGER, status TEXT, oficina_id INTEGER);
            INSERT INTO empresas VALUES (1, 'Antiga', 'antiga@x.com', 'texto', 1);
            INSERT INTO ocorrencias VALUES (1, 1, 77, 1, 'pesado', 'pneu', 0, 'encerrada', NULL);
        """)
        for i, placa in enumerate(placas, start=1):
            conn.execute("INSERT INTO veiculos VALUES (?, 1, ?, 'M', 'X', 'pesado', NULL)", (i, placa))
        conn.commit()
        conn.close()

    def test_normaliza_placa_tipo_e_referencias(self):
        self.criar_legado(['abc-1234', 'BRA2E19'])
        app = create_app({'DATABASE_PATH': self.db_path})
        with app.app_context():
            init_db(popular=False)
        conn = sqlite3.connect(self.db_path)
        self.assertEqual(sorted(r[0] for r in conn.execute('SELECT placa FROM veiculos')), ['ABC1234', 'BRA2E19'])
        row = conn.execute('SELECT tipo_problema, status, motorista_id FROM ocorrencias WHERE id=1').fetchone()
        self.assertEqual(row, ('borracharia', 'resolvido', None))
        conn.close()

    def test_placas_duplicadas_abortam_sem_alterar_nada(self):
        self.criar_legado(['ABC-1234', 'abc1234'])
        app = create_app({'DATABASE_PATH': self.db_path})
        with app.app_context():
            with self.assertRaises(migracoes.MigracaoError) as ctx:
                init_db(popular=False)
        self.assertIn('ABC1234', str(ctx.exception))
        conn = sqlite3.connect(self.db_path)
        self.assertEqual(sorted(r[0] for r in conn.execute('SELECT placa FROM veiculos')), ['ABC-1234', 'abc1234'])
        self.assertEqual(conn.execute('SELECT tipo_problema FROM ocorrencias').fetchone()[0], 'pneu')
        conn.close()


if __name__ == '__main__':
    unittest.main()

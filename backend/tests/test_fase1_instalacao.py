"""Fase 1: instalação do zero, bug do campo `ativa`, seed idempotente e base ampliada."""
import os
import shutil
import sqlite3
import tempfile
import unittest

from tests.base import FixTruckTestCase
from app import create_app
from database import init_db
import migracoes
import seed_dados


class InstalacaoDoZeroTest(FixTruckTestCase):

    def test_busca_retorna_oficinas_apos_instalacao_limpa(self):
        h = self.login_empresa()
        r = self.get('/api/oficinas', h)
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.get_json()['oficinas']), 40)

    def test_ativa_gravada_como_inteiro_1_e_nunca_nulo(self):
        rows = self.sql('SELECT ativa, typeof(ativa) AS tipo FROM oficinas')
        self.assertTrue(rows)
        self.assertTrue(all(r['ativa'] == 1 and r['tipo'] == 'integer' for r in rows))

    def test_coluna_ativa_tem_default_e_not_null_no_banco(self):
        info = {r['name']: r for r in self.sql('PRAGMA table_info(oficinas)')}
        self.assertEqual(info['ativa']['notnull'], 1)
        self.assertEqual(str(info['ativa']['dflt_value']), '1')

    def test_insert_sem_ativa_assume_ativa(self):
        """Regressão do bug: INSERT que omite `ativa` não pode deixar a oficina invisível."""
        self.sql("INSERT INTO oficinas (nome, lat, lon, especialidades, tipos_veiculo) "
                 "VALUES ('Sem ativa', -23.5, -46.6, 'mecânica', 'pesado')")
        row = self.sql("SELECT ativa FROM oficinas WHERE nome='Sem ativa'")[0]
        self.assertEqual(row['ativa'], 1)

    def test_seed_idempotente(self):
        antes = {t: self.sql(f'SELECT COUNT(*) AS c FROM {t}')[0]['c']
                 for t in ('oficinas', 'empresas', 'motoristas', 'veiculos', 'ocorrencias')}
        with self.app.app_context():
            resumo = init_db()
            init_db()
        depois = {t: self.sql(f'SELECT COUNT(*) AS c FROM {t}')[0]['c'] for t in antes}
        self.assertEqual(antes, depois)
        self.assertEqual(resumo['oficinas_inseridas'], 0)
        self.assertEqual(resumo['tabelas_migradas'], [])

    def test_seed_tem_40_ou_mais_oficinas_em_varias_regioes(self):
        self.assertGreaterEqual(len(seed_dados.OFICINAS), 48)
        ufs = {r['uf'] for r in self.sql('SELECT DISTINCT uf FROM oficinas')}
        for uf in ('MG', 'RJ', 'SP', 'PR', 'SC', 'RS', 'BA', 'PE', 'CE', 'GO', 'DF', 'MT', 'MS'):
            self.assertIn(uf, ufs)

    def test_seed_tem_oficinas_24h_com_guincho_e_horarios(self):
        self.assertGreater(self.sql('SELECT COUNT(*) AS c FROM oficinas WHERE aberta_24h=1')[0]['c'], 3)
        self.assertGreater(self.sql('SELECT COUNT(*) AS c FROM oficinas WHERE tem_guincho=0')[0]['c'], 3)
        sem_horario = self.sql('SELECT COUNT(*) AS c FROM oficinas WHERE aberta_24h=0 AND horarios IS NULL')
        self.assertEqual(sem_horario[0]['c'], 0)

    def test_coordenadas_do_seed_dentro_do_brasil(self):
        for of in seed_dados.OFICINAS:
            self.assertTrue(-34 < of['lat'] < 6 and -74 < of['lon'] < -34, of['nome'])

    def test_schema_do_banco_igual_ao_script_oficial(self):
        existentes = {r['name']: r['sql'] for r in self.sql("SELECT name, sql FROM sqlite_master WHERE type='table'")}
        for tabela, create_sql in migracoes.tabelas_do_script().items():
            self.assertEqual(
                migracoes.normalizar_sql(existentes[tabela]), migracoes.normalizar_sql(create_sql), tabela
            )


class MigracaoBancoLegadoTest(unittest.TestCase):
    """Banco no formato antigo (criado por db.create_all, sem DEFAULT) é migrado sem perder dados."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='fixtruck-mig-')
        self.db_path = os.path.join(self.tmpdir, 'legado.db')
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE empresas (id INTEGER NOT NULL, nome VARCHAR NOT NULL, email VARCHAR NOT NULL,
                senha VARCHAR NOT NULL, qtd_caminhoes INTEGER, criado_em DATETIME, PRIMARY KEY (id), UNIQUE (email));
            CREATE TABLE oficinas (id INTEGER NOT NULL, nome VARCHAR NOT NULL, endereco VARCHAR, telefone VARCHAR,
                lat FLOAT, lon FLOAT, especialidades VARCHAR, tipos_veiculo VARCHAR, tem_guincho INTEGER,
                hora_abertura VARCHAR, hora_fechamento VARCHAR, ativa INTEGER, PRIMARY KEY (id));
            INSERT INTO oficinas (nome, endereco, lat, lon, especialidades, tipos_veiculo, tem_guincho,
                hora_abertura, hora_fechamento) VALUES
                ('Legada Comum', 'Rua A, 1', -23.5, -46.6, 'mecânica', 'pesado', 1, '07:00', '19:00'),
                ('Legada 24h', 'Rua B, 2', -23.5, -46.6, 'mecânica', 'pesado', NULL, '00:00', '23:59');
            INSERT INTO empresas (nome, email, senha) VALUES ('Antiga', 'antiga@x.com', 'texto-puro');
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_migra_corrige_ativa_nula_e_preserva_dados(self):
        app = create_app({'DATABASE_PATH': self.db_path})
        with app.app_context():
            resumo = init_db()
        self.assertIn('oficinas', resumo['tabelas_migradas'])
        self.assertTrue(os.path.exists(resumo['backup']))
        conn = sqlite3.connect(self.db_path)
        rows = dict(conn.execute(
            "SELECT nome, ativa FROM oficinas WHERE nome LIKE 'Legada%'").fetchall())
        self.assertEqual(rows, {'Legada Comum': 1, 'Legada 24h': 1})
        self.assertEqual(conn.execute("SELECT aberta_24h FROM oficinas WHERE nome='Legada 24h'").fetchone()[0], 1)
        self.assertIn('07:00-19:00', conn.execute(
            "SELECT horarios FROM oficinas WHERE nome='Legada Comum'").fetchone()[0])
        senha = conn.execute("SELECT senha FROM empresas WHERE email='antiga@x.com'").fetchone()[0]
        self.assertFalse(senha == 'texto-puro')
        conn.close()


if __name__ == '__main__':
    unittest.main()

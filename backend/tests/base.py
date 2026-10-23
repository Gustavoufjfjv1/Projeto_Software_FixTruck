import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from database import init_db  # noqa: E402


class FixTruckTestCase(unittest.TestCase):
    """Cada teste roda num banco SQLite novo, criado do zero pelo script oficial + seed."""

    popular = True

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='fixtruck-test-')
        self.db_path = os.path.join(self.tmpdir, 'test.db')
        self.app = create_app({'DATABASE_PATH': self.db_path, 'TESTING': True})
        with self.app.app_context():
            self.resumo_init = init_db(popular=self.popular)
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # --- utilitários ---
    def sql(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(query, params).fetchall()
            conn.commit()
            return rows
        finally:
            conn.close()

    def login_empresa(self, email='demo@fixtruck.com', senha='123456'):
        r = self.client.post('/api/auth/login', json={'email': email, 'senha': senha})
        self.assertEqual(r.status_code, 200, r.get_json())
        return {'Authorization': 'Bearer ' + r.get_json()['token']}

    def criar_empresa(self, nome='Outra Transportadora', email='outra@fixtruck.com', senha='segredo1'):
        r = self.client.post('/api/auth/cadastro', json={'nome': nome, 'email': email, 'senha': senha})
        self.assertEqual(r.status_code, 201, r.get_json())
        return self.login_empresa(email, senha)

    def get(self, url, headers=None):
        return self.client.get(url, headers=headers or {})

    def post(self, url, json=None, headers=None):
        return self.client.post(url, json=json or {}, headers=headers or {})

    def put(self, url, json=None, headers=None):
        return self.client.put(url, json=json or {}, headers=headers or {})

    def patch(self, url, json=None, headers=None):
        return self.client.patch(url, json=json or {}, headers=headers or {})


def oficina_valida(**extra):
    dados = {
        'nome': 'Oficina Teste Estrada',
        'telefone': '(32) 99999-0000',
        'endereco': 'BR-040, Km 800 - Centro',
        'cidade': 'Juiz de Fora',
        'uf': 'MG',
        'lat': -21.76,
        'lon': -43.35,
        'especialidades': ['mecânica', 'elétrica'],
        'tipos_veiculo': ['pesado'],
        'tem_guincho': True,
        'aberta_24h': False,
        'horarios': {'seg': '08:00-18:00', 'ter': '08:00-18:00', 'qua': '08:00-18:00',
                     'qui': '08:00-18:00', 'sex': '08:00-18:00', 'sab': None, 'dom': None},
    }
    dados.update(extra)
    return dados

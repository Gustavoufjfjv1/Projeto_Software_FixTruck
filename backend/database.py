import os
import sqlite3
from flask import g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'fixtruck.db')
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

db = SQLAlchemy()


def get_db():
    """Conexão sqlite3 para consultas SQL puro nos Repositories."""
    if 'sqlite_db' not in g:
        g.sqlite_db = sqlite3.connect(DATABASE_PATH)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def _ensure_column(conn, table, column, definition):
    cols = [r[1] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()]
    if column not in cols:
        conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')


def init_db():
    """Cria tabelas (SQLAlchemy) e popula dados demo se necessário."""
    from models import Empresa, Motorista, Veiculo, Oficina, Ocorrencia, Favorito  # noqa: F401

    db.create_all()

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    _ensure_column(conn, 'ocorrencias', 'motorista_id', 'INTEGER')
    _ensure_column(conn, 'ocorrencias', 'veiculo_id', 'INTEGER')
    _ensure_column(conn, 'ocorrencias', 'data_vinculacao', 'DATETIME')

    try:
        conn.execute("UPDATE ocorrencias SET status='resolvido' WHERE status='encerrada'")
        conn.commit()
    except Exception:
        pass

    for row in conn.execute('SELECT id, senha FROM empresas').fetchall():
        senha = row['senha'] or ''
        if not (senha.startswith('pbkdf2:') or senha.startswith('scrypt:')):
            conn.execute(
                'UPDATE empresas SET senha=? WHERE id=?',
                (generate_password_hash(senha), row['id']),
            )
    conn.commit()

    if conn.execute('SELECT COUNT(*) as c FROM oficinas').fetchone()['c'] == 0:
        oficinas = [
            ('Auto Mecânica Silva', 'Av. Paulista, 1000 - SP', '(11) 99001-1111', -23.5613, -46.6558,
             'mecânica,elétrica', 'leve,médio,pesado', 1, '07:00', '18:00'),
            ('Borracharia Rápida BR', 'Rod. Anhanguera KM 45', '(11) 98002-2222', -23.5200, -46.6300,
             'borracharia', 'leve,médio,pesado', 1, '06:00', '22:00'),
            ('Elétrica Diesel Master', 'Av. dos Caminhoneiros, 500', '(11) 97003-3333', -23.5900, -46.6100,
             'elétrica,mecânica', 'médio,pesado', 0, '08:00', '17:00'),
            ('Hidráulica & Freios SP', 'Rua das Indústrias, 200', '(11) 96004-4444', -23.5500, -46.6800,
             'hidráulica,freios', 'pesado', 1, '08:00', '18:00'),
            ('Oficina do Zé Mecânico', 'Estrada Velha, KM 12', '(11) 95005-5555', -23.5750, -46.6400,
             'mecânica', 'leve,médio', 0, '08:00', '17:00'),
            ('Truck Center Premium', 'Av. Industrial, 1500', '(11) 94006-6666', -23.5450, -46.6650,
             'mecânica,elétrica,hidráulica,borracharia', 'leve,médio,pesado', 1, '00:00', '23:59'),
            ('Mecânica Rodo Sul', 'Rod. Castelo Branco KM 30', '(11) 93007-7777', -23.6000, -46.6200,
             'mecânica,elétrica', 'pesado', 1, '07:00', '19:00'),
            ('Auto Peças & Serviços', 'Rua das Oficinas, 88', '(11) 92008-8888', -23.5350, -46.6900,
             'mecânica,borracharia', 'leve,médio', 0, '08:00', '18:00'),
        ]
        conn.executemany(
            """INSERT INTO oficinas (nome, endereco, telefone, lat, lon, especialidades,
               tipos_veiculo, tem_guincho, hora_abertura, hora_fechamento) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            oficinas,
        )
        conn.execute(
            'INSERT OR IGNORE INTO empresas (nome, email, senha, qtd_caminhoes) VALUES (?,?,?,?)',
            ('Transportadora Demo', 'demo@fixtruck.com', generate_password_hash('123456'), 12),
        )
        demo = conn.execute("SELECT id FROM empresas WHERE email='demo@fixtruck.com'").fetchone()
        if demo:
            eid = demo['id']
            conn.executemany(
                'INSERT INTO motoristas (empresa_id, nome, cnh, telefone) VALUES (?,?,?,?)',
                [
                    (eid, 'Carlos Mendes', '12345678901', '(11) 99111-1111'),
                    (eid, 'José Ferreira', '98765432100', '(11) 99222-2222'),
                    (eid, 'Ana Paula Souza', '45678912300', '(11) 99333-3333'),
                ],
            )
            mids = [r['id'] for r in conn.execute(
                'SELECT id FROM motoristas WHERE empresa_id=? ORDER BY id', (eid,)
            ).fetchall()]
            conn.executemany(
                """INSERT INTO veiculos (empresa_id, placa, modelo, marca, tipo_veiculo, motorista_id)
                   VALUES (?,?,?,?,?,?)""",
                [
                    (eid, 'ABC1D23', 'Actros 2651', 'Mercedes', 'pesado', mids[0]),
                    (eid, 'DEF4G56', 'FH 540', 'Volvo', 'pesado', mids[1]),
                    (eid, 'GHI7J89', 'Delivery 9.170', 'VW', 'médio', mids[2]),
                    (eid, 'JKL0M12', 'Daily 35S14', 'Iveco', 'leve', None),
                ],
            )
            vids = [r['id'] for r in conn.execute(
                'SELECT id FROM veiculos WHERE empresa_id=? ORDER BY id', (eid,)
            ).fetchall()]
            conn.executemany(
                """INSERT INTO ocorrencias (empresa_id, motorista_id, veiculo_id, tipo_veiculo, tipo_problema,
                   pane_total, lat, lon, endereco, status, oficina_id, data_abertura, data_encerramento, data_vinculacao)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    (eid, mids[0], vids[0], 'pesado', 'mecânica', 1, '-23.5613', '-46.6558',
                     'Rodovia Anhanguera KM 45', 'resolvido', 1, '2024-05-01 09:00', '2024-05-01 13:30', '2024-05-01 09:40'),
                    (eid, mids[1], vids[1], 'pesado', 'borracharia', 0, '-23.5200', '-46.6300',
                     'Av. Brasil, 500', 'resolvido', 2, '2024-05-10 14:00', '2024-05-10 15:45', '2024-05-10 14:20'),
                    (eid, mids[2], vids[2], 'médio', 'elétrica', 0, '-23.5900', '-46.6100',
                     'Rod. Dutra KM 180', 'em_atendimento', None, '2024-05-20 08:30', None, None),
                    (eid, mids[0], vids[0], 'pesado', 'mecânica', 0, '-23.5500', '-46.6800',
                     'Centro, São Paulo', 'aberta', None, '2024-05-22 07:15', None, None),
                ],
            )
        conn.commit()

    demo = conn.execute("SELECT id FROM empresas WHERE email='demo@fixtruck.com'").fetchone()
    if demo:
        eid = demo['id']
        if conn.execute('SELECT COUNT(*) as c FROM motoristas WHERE empresa_id=?', (eid,)).fetchone()['c'] == 0:
            conn.executemany(
                'INSERT INTO motoristas (empresa_id, nome, cnh, telefone) VALUES (?,?,?,?)',
                [
                    (eid, 'Carlos Mendes', '12345678901', '(11) 99111-1111'),
                    (eid, 'José Ferreira', '98765432100', '(11) 99222-2222'),
                    (eid, 'Ana Paula Souza', '45678912300', '(11) 99333-3333'),
                ],
            )
        if conn.execute('SELECT COUNT(*) as c FROM veiculos WHERE empresa_id=?', (eid,)).fetchone()['c'] == 0:
            mids = [r['id'] for r in conn.execute(
                'SELECT id FROM motoristas WHERE empresa_id=? ORDER BY id', (eid,)
            ).fetchall()]
            conn.executemany(
                """INSERT INTO veiculos (empresa_id, placa, modelo, marca, tipo_veiculo, motorista_id)
                   VALUES (?,?,?,?,?,?)""",
                [
                    (eid, 'ABC1D23', 'Actros 2651', 'Mercedes', 'pesado', mids[0] if mids else None),
                    (eid, 'DEF4G56', 'FH 540', 'Volvo', 'pesado', mids[1] if len(mids) > 1 else None),
                    (eid, 'GHI7J89', 'Delivery 9.170', 'VW', 'médio', mids[2] if len(mids) > 2 else None),
                    (eid, 'JKL0M12', 'Daily 35S14', 'Iveco', 'leve', None),
                ],
            )
        conn.commit()
    conn.close()

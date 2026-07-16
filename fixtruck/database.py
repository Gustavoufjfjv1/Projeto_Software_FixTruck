import sqlite3
from flask import g
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'fixtruck.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.executescript('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            qtd_caminhoes INTEGER DEFAULT 0,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS motoristas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            cnh TEXT,
            telefone TEXT,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        );

        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            placa TEXT NOT NULL,
            modelo TEXT,
            marca TEXT,
            tipo_veiculo TEXT NOT NULL DEFAULT 'pesado',
            motorista_id INTEGER,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (motorista_id) REFERENCES motoristas(id)
        );

        CREATE TABLE IF NOT EXISTS oficinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT,
            telefone TEXT,
            lat REAL,
            lon REAL,
            especialidades TEXT,
            tipos_veiculo TEXT,
            tem_guincho INTEGER DEFAULT 0,
            hora_abertura TEXT DEFAULT '08:00',
            hora_fechamento TEXT DEFAULT '18:00',
            ativa INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS ocorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            motorista_id INTEGER,
            veiculo_id INTEGER,
            tipo_veiculo TEXT NOT NULL,
            tipo_problema TEXT NOT NULL,
            pane_total INTEGER DEFAULT 0,
            lat TEXT,
            lon TEXT,
            endereco TEXT,
            status TEXT DEFAULT 'aberta',
            oficina_id INTEGER,
            motivo_resolucao TEXT,
            observacoes TEXT,
            data_abertura DATETIME,
            data_encerramento DATETIME,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (motorista_id) REFERENCES motoristas(id),
            FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
            FOREIGN KEY (oficina_id) REFERENCES oficinas(id)
        );

        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ocorrencia_id INTEGER NOT NULL,
            oficina_id INTEGER NOT NULL,
            valor_pecas REAL NOT NULL DEFAULT 0,
            valor_mao_obra REAL NOT NULL DEFAULT 0,
            descricao TEXT,
            status TEXT DEFAULT 'pendente',
            data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_resposta DATETIME,
            FOREIGN KEY (ocorrencia_id) REFERENCES ocorrencias(id),
            FOREIGN KEY (oficina_id) REFERENCES oficinas(id)
        );

        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            oficina_id INTEGER NOT NULL,
            UNIQUE(empresa_id, oficina_id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (oficina_id) REFERENCES oficinas(id)
        );
    ''')

    def _ensure_column(table, column, definition):
        cols = [r[1] for r in db.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in cols:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    _ensure_column('ocorrencias', 'motorista_id', 'INTEGER')
    _ensure_column('ocorrencias', 'veiculo_id', 'INTEGER')

    try:
        db.execute("UPDATE ocorrencias SET status='resolvido' WHERE status='encerrada'")
        db.commit()
    except Exception:
        pass

    # Seed demo data
    count = db.execute("SELECT COUNT(*) as c FROM oficinas").fetchone()['c']
    if count == 0:
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
        db.executemany(
            """INSERT INTO oficinas (nome, endereco, telefone, lat, lon, especialidades,
               tipos_veiculo, tem_guincho, hora_abertura, hora_fechamento) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            oficinas)

        db.execute("INSERT OR IGNORE INTO empresas (nome, email, senha, qtd_caminhoes) VALUES (?,?,?,?)",
                   ('Transportadora Demo', 'demo@fixtruck.com', '123456', 12))

        demo_empresa = db.execute("SELECT id FROM empresas WHERE email='demo@fixtruck.com'").fetchone()
        if demo_empresa:
            eid = demo_empresa['id']
            db.executemany(
                "INSERT INTO motoristas (empresa_id, nome, cnh, telefone) VALUES (?,?,?,?)",
                [
                    (eid, 'Carlos Mendes', '12345678901', '(11) 99111-1111'),
                    (eid, 'José Ferreira', '98765432100', '(11) 99222-2222'),
                    (eid, 'Ana Paula Souza', '45678912300', '(11) 99333-3333'),
                ])
            mids = [r['id'] for r in db.execute(
                "SELECT id FROM motoristas WHERE empresa_id=? ORDER BY id", (eid,)).fetchall()]
            db.executemany(
                """INSERT INTO veiculos (empresa_id, placa, modelo, marca, tipo_veiculo, motorista_id)
                   VALUES (?,?,?,?,?,?)""",
                [
                    (eid, 'ABC1D23', 'Actros 2651', 'Mercedes', 'pesado', mids[0]),
                    (eid, 'DEF4G56', 'FH 540', 'Volvo', 'pesado', mids[1]),
                    (eid, 'GHI7J89', 'Delivery 9.170', 'VW', 'médio', mids[2]),
                    (eid, 'JKL0M12', 'Daily 35S14', 'Iveco', 'leve', None),
                ])
            vids = [r['id'] for r in db.execute(
                "SELECT id FROM veiculos WHERE empresa_id=? ORDER BY id", (eid,)).fetchall()]
            db.executemany(
                """INSERT INTO ocorrencias (empresa_id, motorista_id, veiculo_id, tipo_veiculo, tipo_problema,
                   pane_total, lat, lon, endereco, status, oficina_id, data_abertura, data_encerramento)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    (eid, mids[0], vids[0], 'pesado', 'mecânica', 1, '-23.5613', '-46.6558',
                     'Rodovia Anhanguera KM 45', 'resolvido', 1, '2024-05-01 09:00', '2024-05-01 13:30'),
                    (eid, mids[1], vids[1], 'pesado', 'borracharia', 0, '-23.5200', '-46.6300',
                     'Av. Brasil, 500', 'resolvido', 2, '2024-05-10 14:00', '2024-05-10 15:45'),
                    (eid, mids[2], vids[2], 'médio', 'elétrica', 0, '-23.5900', '-46.6100',
                     'Rod. Dutra KM 180', 'em_atendimento', None, '2024-05-20 08:30', None),
                    (eid, mids[0], vids[0], 'pesado', 'mecânica', 0, '-23.5500', '-46.6800',
                     'Centro, São Paulo', 'aberta', None, '2024-05-22 07:15', None),
                ])
            # Orçamento pendente na ocorrência em atendimento
            oc_atend = db.execute(
                "SELECT id FROM ocorrencias WHERE empresa_id=? AND status='em_atendimento' LIMIT 1",
                (eid,)).fetchone()
            if oc_atend:
                db.execute(
                    """INSERT INTO orcamentos (ocorrencia_id, oficina_id, valor_pecas, valor_mao_obra,
                       descricao, status, data_envio)
                       VALUES (?,?,?,?,?,'pendente',datetime('now','localtime'))""",
                    (oc_atend['id'], 3, 850.00, 320.00, 'Troca de alternador e revisão elétrica'))
        db.commit()

    # Seed frota/orçamentos se o banco antigo já tinha oficinas
    demo_empresa = db.execute("SELECT id FROM empresas WHERE email='demo@fixtruck.com'").fetchone()
    if demo_empresa:
        eid = demo_empresa['id']
        if db.execute("SELECT COUNT(*) as c FROM motoristas WHERE empresa_id=?", (eid,)).fetchone()['c'] == 0:
            db.executemany(
                "INSERT INTO motoristas (empresa_id, nome, cnh, telefone) VALUES (?,?,?,?)",
                [
                    (eid, 'Carlos Mendes', '12345678901', '(11) 99111-1111'),
                    (eid, 'José Ferreira', '98765432100', '(11) 99222-2222'),
                    (eid, 'Ana Paula Souza', '45678912300', '(11) 99333-3333'),
                ])
        if db.execute("SELECT COUNT(*) as c FROM veiculos WHERE empresa_id=?", (eid,)).fetchone()['c'] == 0:
            mids = [r['id'] for r in db.execute(
                "SELECT id FROM motoristas WHERE empresa_id=? ORDER BY id", (eid,)).fetchall()]
            db.executemany(
                """INSERT INTO veiculos (empresa_id, placa, modelo, marca, tipo_veiculo, motorista_id)
                   VALUES (?,?,?,?,?,?)""",
                [
                    (eid, 'ABC1D23', 'Actros 2651', 'Mercedes', 'pesado', mids[0] if mids else None),
                    (eid, 'DEF4G56', 'FH 540', 'Volvo', 'pesado', mids[1] if len(mids) > 1 else None),
                    (eid, 'GHI7J89', 'Delivery 9.170', 'VW', 'médio', mids[2] if len(mids) > 2 else None),
                    (eid, 'JKL0M12', 'Daily 35S14', 'Iveco', 'leve', None),
                ])
        if db.execute("SELECT COUNT(*) as c FROM orcamentos").fetchone()['c'] == 0:
            oc_atend = db.execute(
                "SELECT id FROM ocorrencias WHERE empresa_id=? AND status IN ('em_atendimento','aberta') LIMIT 1",
                (eid,)).fetchone()
            if oc_atend:
                db.execute(
                    """INSERT INTO orcamentos (ocorrencia_id, oficina_id, valor_pecas, valor_mao_obra,
                       descricao, status, data_envio)
                       VALUES (?,?,?,?,?,'pendente',datetime('now','localtime'))""",
                    (oc_atend['id'], 3, 850.00, 320.00, 'Troca de alternador e revisão elétrica'))
        db.commit()
    db.close()

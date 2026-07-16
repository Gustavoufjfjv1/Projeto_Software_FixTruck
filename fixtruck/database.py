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

        # Demo company
        db.execute("INSERT OR IGNORE INTO empresas (nome, email, senha, qtd_caminhoes) VALUES (?,?,?,?)",
                   ('Transportadora Demo', 'demo@fixtruck.com', '123456', 12))

        # Demo occurrences
        demo_empresa = db.execute("SELECT id FROM empresas WHERE email='demo@fixtruck.com'").fetchone()
        if demo_empresa:
            eid = demo_empresa['id']
            db.executemany(
                """INSERT INTO ocorrencias (empresa_id, tipo_veiculo, tipo_problema, pane_total,
                   lat, lon, endereco, status, oficina_id, data_abertura, data_encerramento)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    (eid, 'pesado', 'mecânica', 1, '-23.5613', '-46.6558', 'Rodovia Anhanguera KM 45',
                     'encerrada', 1, '2024-05-01 09:00', '2024-05-01 13:30'),
                    (eid, 'médio', 'borracharia', 0, '-23.5200', '-46.6300', 'Av. Brasil, 500',
                     'encerrada', 2, '2024-05-10 14:00', '2024-05-10 15:45'),
                    (eid, 'pesado', 'elétrica', 0, '-23.5900', '-46.6100', 'Rod. Dutra KM 180',
                     'em_atendimento', None, '2024-05-20 08:30', None),
                    (eid, 'leve', 'mecânica', 0, '-23.5500', '-46.6800', 'Centro, São Paulo',
                     'aberta', None, '2024-05-22 07:15', None),
                ])
        db.commit()
    db.close()

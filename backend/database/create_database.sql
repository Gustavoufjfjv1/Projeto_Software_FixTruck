-- FixTruck — script oficial do banco de dados (SQLite).
-- Este arquivo é a fonte da verdade do schema: o backend o executa em init_db()
-- e a migração (backend/migracoes.py) reconstrói qualquer tabela antiga que divirja dele.

CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    qtd_caminhoes INTEGER NOT NULL DEFAULT 0,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS motoristas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    cnh TEXT,
    telefone TEXT,
    ativo INTEGER NOT NULL DEFAULT 1,
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
    cidade TEXT,
    uf TEXT,
    telefone TEXT,
    lat REAL,
    lon REAL,
    especialidades TEXT NOT NULL DEFAULT '',
    tipos_veiculo TEXT NOT NULL DEFAULT '',
    tem_guincho INTEGER NOT NULL DEFAULT 0 CHECK (tem_guincho IN (0, 1)),
    aberta_24h INTEGER NOT NULL DEFAULT 0 CHECK (aberta_24h IN (0, 1)),
    horarios TEXT,
    ativa INTEGER NOT NULL DEFAULT 1 CHECK (ativa IN (0, 1)),
    empresa_id INTEGER,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

CREATE TABLE IF NOT EXISTS ocorrencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    motorista_id INTEGER,
    veiculo_id INTEGER,
    tipo_veiculo TEXT NOT NULL,
    tipo_problema TEXT NOT NULL,
    pane_total INTEGER NOT NULL DEFAULT 0,
    lat TEXT,
    lon TEXT,
    endereco TEXT,
    status TEXT NOT NULL DEFAULT 'aberta',
    oficina_id INTEGER,
    motivo_resolucao TEXT,
    observacoes TEXT,
    data_abertura DATETIME,
    data_encerramento DATETIME,
    data_vinculacao DATETIME,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (oficina_id) REFERENCES oficinas(id)
);

CREATE TABLE IF NOT EXISTS favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    oficina_id INTEGER NOT NULL,
    UNIQUE (empresa_id, oficina_id),
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (oficina_id) REFERENCES oficinas(id)
);

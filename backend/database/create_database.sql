-- FixTruck — script oficial do banco de dados (SQLite).
-- Este arquivo é a fonte da verdade do schema: o backend o executa em init_db()
-- e a migração (backend/migracoes.py) reconstrói qualquer tabela antiga que divirja dele.
-- Chaves estrangeiras só valem com PRAGMA foreign_keys = ON (ligado em toda conexão do backend).
-- Enums (mesmos valores de backend/constantes.py):
--   tipo_problema: mecânica, elétrica, hidráulica, borracharia, não identificado
--   tipo_veiculo:  leve, médio, pesado
--   status:        aberta, em_atendimento, resolvido

CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    qtd_caminhoes INTEGER NOT NULL DEFAULT 0 CHECK (qtd_caminhoes >= 0),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS motoristas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    cnh TEXT,
    telefone TEXT,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    email TEXT UNIQUE,
    senha TEXT,
    trocar_senha INTEGER NOT NULL DEFAULT 0 CHECK (trocar_senha IN (0, 1)),
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    placa TEXT NOT NULL UNIQUE,
    modelo TEXT,
    marca TEXT,
    tipo_veiculo TEXT NOT NULL DEFAULT 'pesado' CHECK (tipo_veiculo IN ('leve', 'médio', 'pesado')),
    motorista_id INTEGER,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE SET NULL ON UPDATE CASCADE
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
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ocorrencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    motorista_id INTEGER,
    veiculo_id INTEGER,
    tipo_veiculo TEXT NOT NULL CHECK (tipo_veiculo IN ('leve', 'médio', 'pesado')),
    tipo_problema TEXT NOT NULL CHECK (tipo_problema IN ('mecânica', 'elétrica', 'hidráulica', 'borracharia', 'não identificado')),
    pane_total INTEGER NOT NULL DEFAULT 0 CHECK (pane_total IN (0, 1)),
    descricao TEXT,
    lat TEXT,
    lon TEXT,
    endereco TEXT,
    status TEXT NOT NULL DEFAULT 'aberta' CHECK (status IN ('aberta', 'em_atendimento', 'resolvido')),
    oficina_id INTEGER,
    motivo_resolucao TEXT,
    observacoes TEXT,
    data_abertura DATETIME,
    data_reabertura DATETIME,
    data_encerramento DATETIME,
    data_vinculacao DATETIME,
    registrada_por TEXT NOT NULL DEFAULT 'empresa' CHECK (registrada_por IN ('empresa', 'motorista')),
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    oficina_id INTEGER NOT NULL,
    UNIQUE (empresa_id, oficina_id),
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Recuperação de senha: guarda apenas o hash SHA-256 do token; uso único e com expiração.
CREATE TABLE IF NOT EXISTS tokens_recuperacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expira_em DATETIME NOT NULL,
    usado_em DATETIME,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE ON UPDATE CASCADE
);

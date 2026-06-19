-- Criação do banco de dados FixTruck
-- Script para criar as tabelas e estrutura base

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo_usuario ENUM('gestor', 'motorista') NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Tabela de Empresa Transporte
CREATE TABLE IF NOT EXISTS empresas_transporte (
    id_empresa INT PRIMARY KEY AUTO_INCREMENT,
    razao_social VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Gestores
CREATE TABLE IF NOT EXISTS gestores (
    id_gestor INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL UNIQUE,
    id_empresa INT NOT NULL,
    telefone_corporativo VARCHAR(20),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_empresa) REFERENCES empresas_transporte(id_empresa) ON DELETE CASCADE
);

-- Tabela de Veículos
CREATE TABLE IF NOT EXISTS veiculos (
    id_veiculo INT PRIMARY KEY AUTO_INCREMENT,
    placa VARCHAR(10) UNIQUE NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    marca VARCHAR(100) NOT NULL,
    tipo_veiculo VARCHAR(50) NOT NULL,
    id_empresa INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_empresa) REFERENCES empresas_transporte(id_empresa) ON DELETE CASCADE
);

-- Tabela de Motoristas
CREATE TABLE IF NOT EXISTS motoristas (
    id_motorista INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL UNIQUE,
    id_veiculo INT,
    numero_cnh VARCHAR(15) UNIQUE NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE SET NULL
);

-- Tabela de Oficinas (importadas do shapefile)
CREATE TABLE IF NOT EXISTS oficinas (
    id_oficina INT PRIMARY KEY AUTO_INCREMENT,
    nome_fantasia VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    especialidades VARCHAR(255),
    horario_funcionamento VARCHAR(255),
    possui_guincho BOOLEAN DEFAULT FALSE,
    atende_pesado BOOLEAN DEFAULT FALSE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    endereco VARCHAR(500),
    bairro VARCHAR(100),
    numero_imovel VARCHAR(20),
    cnae_principal VARCHAR(10),
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Ocorrências
CREATE TABLE IF NOT EXISTS ocorrencias (
    id_ocorrencia INT PRIMARY KEY AUTO_INCREMENT,
    id_veiculo INT NOT NULL,
    id_oficina INT,
    id_motorista INT,
    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fechamento TIMESTAMP NULL,
    status ENUM('aberta', 'em_atendimento', 'resolvida', 'cancelada') DEFAULT 'aberta',
    tipo_problema VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    motivo_resolucao TEXT,
    observacao TEXT,
    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE CASCADE,
    FOREIGN KEY (id_oficina) REFERENCES oficinas(id_oficina) ON DELETE SET NULL,
    FOREIGN KEY (id_motorista) REFERENCES motoristas(id_motorista) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_data_abertura (data_abertura)
);

-- Tabela de Orçamentos
CREATE TABLE IF NOT EXISTS orcamentos (
    id_orcamento INT PRIMARY KEY AUTO_INCREMENT,
    id_ocorrencia INT NOT NULL,
    id_oficina INT NOT NULL,
    valor_pecas DECIMAL(10, 2) NOT NULL DEFAULT 0,
    valor_mao_obra DECIMAL(10, 2) NOT NULL DEFAULT 0,
    status_aprovacao ENUM('pendente', 'aprovado', 'rejeitado') DEFAULT 'pendente',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_resposta TIMESTAMP NULL,
    observacoes TEXT,
    FOREIGN KEY (id_ocorrencia) REFERENCES ocorrencias(id_ocorrencia) ON DELETE CASCADE,
    FOREIGN KEY (id_oficina) REFERENCES oficinas(id_oficina) ON DELETE CASCADE,
    INDEX idx_status_aprovacao (status_aprovacao)
);

-- Tabela de Mensagens de Chat
CREATE TABLE IF NOT EXISTS mensagens_chat (
    id_mensagem INT PRIMARY KEY AUTO_INCREMENT,
    id_ocorrencia INT NOT NULL,
    id_usuario INT NOT NULL,
    texto TEXT NOT NULL,
    url_foto_evidencia VARCHAR(500),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ocorrencia) REFERENCES ocorrencias(id_ocorrencia) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_ocorrencia (id_ocorrencia),
    INDEX idx_data_hora (data_hora)
);

-- Tabela de Oficinas Favoritas (Gestores)
CREATE TABLE IF NOT EXISTS oficinas_favoritas (
    id_favorita INT PRIMARY KEY AUTO_INCREMENT,
    id_gestor INT NOT NULL,
    id_oficina INT NOT NULL,
    data_adicionada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_gestor) REFERENCES gestores(id_gestor) ON DELETE CASCADE,
    FOREIGN KEY (id_oficina) REFERENCES oficinas(id_oficina) ON DELETE CASCADE,
    UNIQUE KEY unique_favorita (id_gestor, id_oficina)
);

-- Índices para melhorar performance
CREATE INDEX idx_usuarios_tipo ON usuarios(tipo_usuario);
CREATE INDEX idx_ocorrencias_veiculo ON ocorrencias(id_veiculo);
CREATE INDEX idx_ocorrencias_oficina ON ocorrencias(id_oficina);
CREATE INDEX idx_motoristas_veiculo ON motoristas(id_veiculo);
CREATE INDEX idx_gestores_empresa ON gestores(id_empresa);
CREATE INDEX idx_veiculos_empresa ON veiculos(id_empresa);

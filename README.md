# Projeto_Software_FixTruck

## Integrantes

- Arthur Cezar
- Caio Luis
- Gustavo Henrique
- João Otávio
- Mateus Torres
- Pedro Lima

## Stack utilizada

### Front-end
- HTML
- CSS
- JavaScript

### Back-end
- Python (Flask) — API REST JSON
- Flask-SQLAlchemy

### Banco de dados
- SQLite

## Descrição

O FixTruck é um sistema de gestão de ocorrências mecânicas projetado especificamente para transportadoras e frotas de transporte rodoviário. O objetivo principal da solução é reduzir o downtime quando ocorre uma pane em rota. A plataforma conecta motoristas e gestores a oficinas mecânicas próximas através de geolocalização e filtros baseados na especialidade técnica.

## Funcionalidades Implementadas

1. Cadastrar empresa
2. Autenticar empresa (login)
3. Cadastrar motorista
4. Cadastrar veículo
5. Registrar ocorrência
6. Listar ocorrências (com filtros)
7. Buscar oficinas para ocorrência
8. Favoritar oficina
9. Enviar e decidir orçamento
10. Gerar relatório de ocorrências

Cada funcionalidade está disponível de ponta a ponta: Interface → API Flask → Controller (classe) → Service (um por caso de uso) → Model/`Repository` → Banco de Dados.

Também estão implementados no mesmo padrão: vincular motorista ao veículo, encerrar ocorrência, dashboard e atualizar perfil.

## Estrutura do projeto

```text
fixtruck/
├── backend/              # API Flask (JSON)
│   ├── app.py
│   ├── database.py       # SQLAlchemy (db)
│   ├── controllers/      # Classes Controller por recurso
│   ├── services/         # Um Service por caso de uso
│   ├── models/           # Entidades (db.Model) com CRUD
│   ├── repositories/     # Consultas complexas / filtros / relatórios
│   └── fixtruck.db
└── frontend/             # Interface que consome a API
    ├── *.html
    ├── css/
    ├── js/
    └── img/
```

O frontend e o backend rodam em processos separados. O frontend chama os endpoints em `http://127.0.0.1:5000/api/...`.

## Como utilizar

### 1. Pré-requisitos

- Python 3 instalado ([python.org/downloads](https://www.python.org/downloads/))
- Marque a opção **"Add Python to PATH"** no instalador do Windows

### 2. Baixar o projeto

```powershell
git clone https://github.com/Gustavoufjfjv1/Projeto_Software_FixTruck
cd Projeto_Software_FixTruck
```

### 3. Ambiente virtual e dependências

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Subir a API (backend)

Em um terminal, na pasta do projeto:

```powershell
cd backend
python app.py
```

A API ficará em: `http://127.0.0.1:5000`

### 5. Subir o frontend

Em **outro** terminal:

```powershell
cd frontend
python -m http.server 8080
```

Abra no navegador: `http://127.0.0.1:8080`

### Conta demo

- E-mail: `demo@fixtruck.com`
- Senha: `123456`

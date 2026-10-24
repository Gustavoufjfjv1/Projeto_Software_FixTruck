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
- Flask-SQLAlchemy (CRUD nas Models)
- SQL puro nos Repositories (`sqlite3`)

### Banco de dados
- SQLite

## Descrição

O FixTruck é um sistema de gestão de ocorrências mecânicas projetado especificamente para transportadoras e frotas de transporte rodoviário. O objetivo principal da solução é reduzir o downtime quando ocorre uma pane em rota. A plataforma conecta motoristas e gestores a oficinas mecânicas próximas através de geolocalização e filtros baseados na especialidade técnica.

## Funcionalidades Implementadas

As funcionalidades abaixo estão conectadas à interface, API Flask, Controller, Service e persistência no SQLite, conforme aplicável:

1. Cadastrar empresa
2. Autenticar empresa
3. Solicitar recuperação de senha
4. Redefinir senha com token
5. Consultar dashboard operacional
6. Consultar e atualizar perfil da empresa
7. Cadastrar motorista
8. Listar frota e motoristas
9. Cadastrar veículo
10. Vincular ou desvincular motorista de veículo
11. Registrar ocorrência
12. Listar e filtrar ocorrências por período, status, tipo e veículo
13. Consultar detalhes da ocorrência
14. Atualizar ocorrência
15. Atualizar status da ocorrência
16. Buscar oficinas compatíveis para uma ocorrência
17. Vincular oficina à ocorrência
18. Encerrar ocorrência como resolvida
19. Listar oficinas por busca e localização
20. Consultar detalhes da oficina
21. Favoritar ou desfavoritar oficina
22. Consultar oficinas favoritas
23. Gerar relatório operacional por período
24. Buscar motoristas por nome, CNH ou telefone
25. Atualizar cadastro de motorista
26. Inativar motorista (com validação de vínculo com veículo)
27. Reativar motorista
28. Excluir motorista sem vínculos ou ocorrências históricas
29. Atualizar dados de veículo
30. Excluir veículo sem ocorrências históricas
31. Reabrir ocorrência resolvida
32. Filtrar relatórios por status da ocorrência
33. Exportar relatório filtrado em CSV

As funcionalidades 24 a 33 foram acrescentadas nesta etapa. As exclusões preservam o histórico e são recusadas quando há ocorrências ou vínculos que dependem do registro. O relatório CSV respeita os mesmos filtros de período e status da tela.

O diagrama de classes do domínio está em [docs/diagrama_classes.md](./docs/diagrama_classes.md).

### Base de oficinas

`backend/data/oficinas_bh.json` contém estabelecimentos de Belo Horizonte filtrados pelos CNAEs de serviços automotivos 4520001 a 4520008. As coordenadas do shapefile municipal foram convertidas de SIRGAS 2000 / UTM 23S para latitude e longitude. A fonte não informa atendimento a caminhões, telefone, horário de funcionamento ou disponibilidade de guincho; esses dados permanecem como não informados.

## Estrutura do projeto

```text
fixtruck/
├── backend/              # API Flask (JSON)
│   ├── app.py
│   ├── database.py       # SQLAlchemy (Models) + sqlite3 (Repositories)
│   ├── controllers/      # Classes Controller por recurso
│   ├── services/         # Um Service por caso de uso
│   ├── models/           # Entidades db.Model com CRUD (SQLAlchemy)
│   ├── repositories/     # Consultas SQL puro / filtros / relatórios
│   ├── data/             # Base pública filtrada de oficinas de Belo Horizonte
│   └── fixtruck.db
├── docs/
│   └── diagrama_classes.md
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

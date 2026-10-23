# Projeto_Software_FixTruck

## Integrantes

- Arthur Cezar
- Caio Luis
- Gustavo Henrique
- João Otávio
- Mateus Torres
- Pedro Lima

## Descrição

O FixTruck é um sistema de gestão de ocorrências mecânicas para transportadoras e frotas
de transporte rodoviário. O objetivo é reduzir o tempo de caminhão parado quando ocorre
uma pane em rota: o gestor (empresa) ou o próprio motorista registra a ocorrência com a
localização, e o sistema recomenda oficinas **compatíveis** com o problema, o tipo de
veículo, a necessidade de guincho, o horário de funcionamento e a distância.

## Status das funcionalidades

Regra usada: **Concluída** = implementada **e** testada (teste automatizado em
`backend/tests/` ou teste manual no navegador registrado). Na dúvida, não se marca.

| # | Funcionalidade | Status | Como foi testada |
|---|---|---|---|
| 1 | Cadastrar empresa | Concluída | `test_regressao_funcionalidades` (`TestEmpresa`), `test_fase4_validacoes` (`TestFormularios`) |
| 2 | Login da empresa | Concluída | `test_regressao_funcionalidades` (`TestEmpresa`) |
| 3 | Recuperar e redefinir senha (token seguro, e-mail simulado) | Concluída | `test_fase4_validacoes` (`TestRecuperacaoSenha`) |
| 4 | Ver e atualizar perfil da empresa | Concluída | `test_regressao_funcionalidades` (`test_perfil_le_e_atualiza`) |
| 5 | Cadastrar motorista | Concluída | `test_regressao_funcionalidades` (`TestFrota`), `test_fase4_validacoes` (`TestFormularios`) |
| 6 | Cadastrar veículo (placa normalizada e única) | Concluída | `test_regressao_funcionalidades` (`TestFrota`), `test_fase4_validacoes` (`TestPlaca`) |
| 7 | Vincular motorista a veículo | Concluída | `test_regressao_funcionalidades` (`TestFrota`), `test_fase4_validacoes` (`test_vincular_motorista_posse`) |
| 8 | Cadastro de oficinas pela empresa (criar, editar, ativar/desativar) | Concluída | `test_fase1_cadastro_oficinas` |
| 9 | Registrar ocorrência com GPS e alternativa manual | Concluída | `test_fase4_validacoes`, `test_regressao_funcionalidades` e teste manual no navegador (GPS negado, indisponível, timeout e sucesso) |
| 10 | Editar ocorrência | Concluída | `test_regressao_funcionalidades` (`TestCicloDaOcorrencia`), `test_fase4_validacoes` (`TestPosse`) |
| 11 | Listar ocorrências com filtros (status, tipo, veículo, 7/30/90 dias) | Concluída | `test_regressao_funcionalidades` (`test_lista_com_filtro_de_status`), `test_fase5_filtros_consistencia` |
| 12 | Filtro por intervalo de datas (ocorrências e relatórios) | Concluída | `test_fase5_filtros_consistencia` (`TestIntervaloDeDatas`, `TestRelatorioComDatas`) e teste manual no navegador |
| 13 | Buscar oficinas compatíveis (WorkshopMatcher), com mapa e distância | Concluída | `test_fase2_workshop_matcher` e teste manual no navegador |
| 14 | Explicar quando não há oficina compatível (motivo e alternativas) | Concluída | `test_fase2_workshop_matcher` (`test_sem_resultados_*`) e teste manual no navegador |
| 15 | Vincular oficina à ocorrência e atualizar status | Concluída | `test_regressao_funcionalidades` (`TestCicloDaOcorrencia`) |
| 16 | Encerrar ocorrência | Concluída | `test_regressao_funcionalidades` (`TestCicloDaOcorrencia`), `test_fase4_validacoes` e teste manual no navegador |
| 17 | Favoritar oficinas | Concluída | `test_regressao_funcionalidades` (`test_favoritar_e_desfavoritar`) |
| 18 | Dashboard e relatórios | Concluída | `test_regressao_funcionalidades` (`TestFavoritosDashboardRelatorio`), `test_fase5_filtros_consistencia` |
| 19 | Login do motorista (acesso criado pela empresa, troca de senha no 1º acesso) | Concluída | `test_fase3_motorista` (`TestLoginMotorista`, `TestTrocaDeSenha`, `TestAcessoDefinidoPelaEmpresa`) |
| 20 | Motorista registra e acompanha ocorrências do seu veículo e busca oficinas | Concluída | `test_fase3_motorista` (`TestOcorrenciasDoMotorista`, `TestPapeisEIsolamento`) e teste manual no navegador |

**Fora do escopo:** envio, aprovação ou rejeição de orçamentos. Não há tela, rota nem
service para isso. Bancos antigos podem ter uma tabela `orcamentos` herdada de versões
anteriores; ela é preservada pela migração, mas não é usada pelo sistema.

### Funcionalidades novas (resumo)

Desde a versão anterior, entraram 11 funcionalidades novas, todas testadas: cadastro de
oficinas pela empresa, catálogo inicial com 54 oficinas, atualização automática e segura
do banco, recomendação por compatibilidade, explicação quando não há oficina compatível,
horários por dia da semana, login do motorista, acesso do motorista criado pela empresa,
ocorrências registradas pelo motorista, alternativa manual quando o GPS falha e filtro por
intervalo de datas. Detalhes, arquivos e testes em
[docs/funcionalidades-novas.md](docs/funcionalidades-novas.md).

## Stack

- **Front-end:** HTML, CSS e JavaScript puro; mapa com Leaflet e geocodificação com
  OpenStreetMap/Nominatim (sem chave de API).
- **Back-end:** Python com Flask (API REST JSON), Flask-SQLAlchemy nos Models e SQL puro
  (`sqlite3`) nos Repositories.
- **Banco de dados:** SQLite. O schema oficial está em `backend/database/create_database.sql`.

Arquitetura em camadas: Interface → API Flask → Controller → Service (um por caso de uso)
→ Model / Repository → Banco. Diagrama de classes em
[docs/diagrama-de-classes.md](docs/diagrama-de-classes.md).

## Pré-requisitos

- Python 3.10 ou mais novo ([python.org/downloads](https://www.python.org/downloads/)).
  No Windows, marque **"Add Python to PATH"** no instalador.
- Git.
- Navegador moderno (Chrome, Firefox ou Edge). O GPS só funciona em `localhost`/`127.0.0.1`
  ou HTTPS; sem GPS, a tela permite informar o local manualmente.
- Internet no navegador para carregar o mapa (Leaflet) e buscar endereços (Nominatim).
  A API e os testes funcionam sem internet.

## Instalação do zero

### 1. Baixar o projeto

```bash
git clone https://github.com/Gustavoufjfjv1/Projeto_Software_FixTruck
cd Projeto_Software_FixTruck
```

### 2. Ambiente virtual e dependências

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Subir o sistema

```bash
cd backend
python app.py
```

Na primeira execução o backend cria o banco a partir do script SQL oficial, aplica a
migração (se o banco for antigo) e carrega os dados de demonstração. A saída mostra:

```text
Banco pronto em .../backend/fixtruck.db — 54 oficinas ativas.
```

Abra **http://127.0.0.1:5000** no navegador. O Flask serve a API e as telas no mesmo
endereço; não é preciso subir o front-end separadamente.

### Banco de dados e seed

- O seed (`backend/seed.py` e `backend/seed_dados.py`) é **idempotente**: roda a cada
  inicialização e só insere o que falta (oficinas do catálogo, empresa e motoristas demo).
  Dados cadastrados pelos usuários nunca são apagados.
- Se o banco for de uma versão antiga, a migração (`backend/migracoes.py`) faz uma cópia
  `fixtruck.db.bak-AAAAMMDDHHMMSS` antes de alterar qualquer tabela.
- Para usar um banco novo sem mexer no atual, aponte outro arquivo:

```bash
FIXTRUCK_DB=/tmp/fixtruck-novo.db python app.py
```

No PowerShell: `$env:FIXTRUCK_DB="$env:TEMP\fixtruck-novo.db"; python app.py`.

Variáveis de ambiente opcionais:

| Variável | Uso | Padrão |
|---|---|---|
| `FIXTRUCK_DB` | Caminho do arquivo SQLite | `backend/fixtruck.db` |
| `FIXTRUCK_SECRET` | Chave para assinar os tokens de login | valor fixo de desenvolvimento |

### Recuperação de senha (e-mail simulado)

Não há servidor de e-mail. Ao pedir a recuperação em "Esqueceu a senha?", o código e o
link `redefinir_senha.html?token=...` são impressos **no terminal onde o backend está
rodando** (bloco "E-MAIL SIMULADO"). O código vale 30 minutos e só pode ser usado uma vez.

## Testes

```bash
cd backend
python -m unittest discover -s tests -t .
```

Cada teste cria um banco SQLite temporário do zero (script oficial + seed); o banco real
não é usado. Arquivos por fase:

| Arquivo | O que cobre |
|---|---|
| `test_fase1_instalacao.py` | Instalação limpa, campo `ativa`, seed, migração de banco antigo |
| `test_fase1_cadastro_oficinas.py` | Cadastro de oficinas |
| `test_fase2_workshop_matcher.py` | Recomendação de oficinas e horários |
| `test_fase3_motorista.py` | Login do motorista, papéis e ocorrências do motorista |
| `test_fase4_validacoes.py` | Enum, placa, posse (404/403/422), FKs, formulários, recuperação de senha |
| `test_fase5_filtros_consistencia.py` | Intervalo de datas e consistência SQL/banco/código |
| `test_regressao_funcionalidades.py` | Caminho feliz das funcionalidades que já existiam |

## Credenciais de demonstração

Criadas pelo seed:

| Papel | Tela de login | E-mail | Senha | Observação |
|---|---|---|---|---|
| Empresa | `login.html` | `demo@fixtruck.com` | `123456` | Transportadora Demo |
| Motorista | `motorista_login.html` | `carlos@fixtruck.com` | `motorista123` | Vinculado ao veículo ABC1D23 |
| Motorista | `motorista_login.html` | `jose@fixtruck.com` | `trocar123` | Precisa trocar a senha no primeiro acesso |

São credenciais de demonstração; troque-as em qualquer ambiente que não seja local.

## Estrutura de pastas

```text
Projeto_Software_FixTruck/
├── backend/
│   ├── app.py                    # create_app(), tratamento de erros, serve o front-end
│   ├── auth.py                   # tokens de empresa e de motorista, decorators de acesso
│   ├── constantes.py             # enums (tipo de problema, tipo de veículo, status)
│   ├── database.py               # SQLAlchemy + sqlite3, PRAGMA foreign_keys, init_db()
│   ├── database/create_database.sql  # schema oficial (fonte da verdade)
│   ├── migracoes.py              # migração segura de bancos antigos
│   ├── seed.py, seed_dados.py    # dados de demonstração (idempotente)
│   ├── horarios.py               # horários por dia, fuso de São Paulo
│   ├── validacoes.py             # validação de formulários (422)
│   ├── email_simulado.py         # "envio" de e-mail no console
│   ├── controllers/              # um Controller (Blueprint) por recurso
│   ├── services/                 # um Service por caso de uso, WorkshopMatcher, posse
│   ├── models/                   # entidades SQLAlchemy com CRUD (ModeloBase)
│   ├── repositories/             # consultas em SQL puro, filtros e relatórios
│   └── tests/                    # testes automatizados (unittest)
├── frontend/
│   ├── *.html                    # telas da empresa e do motorista (motorista_*.html)
│   ├── css/
│   ├── js/                       # api.js, localizacao.js, busca_oficinas.js, filtro_datas.js...
│   └── img/
├── docs/
│   ├── diagrama-de-classes.md
│   ├── funcionalidades-novas.md
│   ├── inconsistencias-sql-codigo.md
│   └── roteiro-video.md
└── requirements.txt
```

## Documentação

- [Diagrama de classes (Mermaid)](docs/diagrama-de-classes.md)
- [Funcionalidades novas](docs/funcionalidades-novas.md)
- [Inconsistências entre SQL, banco e código](docs/inconsistencias-sql-codigo.md)
- [Roteiro do vídeo de demonstração](docs/roteiro-video.md)

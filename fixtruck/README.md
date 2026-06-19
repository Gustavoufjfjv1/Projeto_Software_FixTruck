# FixTruck - Sistema de Gestão de Ocorrências Mecânicas

Bem-vindo ao FixTruck! Uma plataforma moderna para otimizar a gestão de ocorrências mecânicas em frotas rodoviárias.

## 📋 Estrutura do Projeto

```
fixtruck/
├── frontend/                 # Interface do usuário
│   ├── index.html           # Arquivo principal
│   ├── css/
│   │   ├── styles.css       # Estilos principais
│   │   └── responsive.css   # Estilos responsivos
│   ├── js/
│   │   ├── api.js           # Cliente API
│   │   ├── auth.js          # Gerenciamento de autenticação
│   │   ├── router.js        # Sistema de roteamento
│   │   ├── motorista.js     # Interface do motorista
│   │   ├── gestor.js        # Interface do gestor
│   │   └── app.js           # Inicialização
│   ├── pages/               # Páginas adicionais
│   └── assets/              # Imagens e recursos
│
└── backend/                 # API Flask
    ├── app.py              # Aplicação principal
    ├── config.py           # Configurações
    ├── requirements.txt    # Dependências Python
    │
    ├── models/             # Modelos de dados (ORM)
    │   ├── usuario.py
    │   ├── empresa_transporte.py
    │   ├── gestor.py
    │   ├── motorista.py
    │   ├── veiculo.py
    │   ├── oficina.py
    │   ├── ocorrencia.py
    │   ├── orcamento.py
    │   ├── mensagem_chat.py
    │   └── oficina_favorita.py
    │
    ├── controllers/        # Controladores de requisições
    │   ├── auth_controller.py
    │   ├── usuario_controller.py
    │   ├── veiculo_controller.py
    │   ├── ocorrencia_controller.py
    │   ├── oficina_controller.py
    │   ├── orcamento_controller.py
    │   └── chat_controller.py
    │
    ├── services/           # Lógica de negócio
    │   ├── auth_service.py
    │   ├── usuario_service.py
    │   ├── veiculo_service.py
    │   ├── ocorrencia_service.py
    │   ├── oficina_service.py
    │   ├── orcamento_service.py
    │   └── chat_service.py
    │
    ├── repositories/       # Acesso a dados
    │   ├── base_repository.py
    │   ├── usuario_repository.py
    │   ├── veiculo_repository.py
    │   ├── ocorrencia_repository.py
    │   ├── oficina_repository.py
    │   ├── orcamento_repository.py
    │   └── chat_repository.py
    │
    └── database/
        └── create_database.sql  # Script de criação do BD
```

## 🚀 Como Iniciar

### 1. Configurar Backend (Python/Flask)

```bash
# Navegar para a pasta backend
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados (MySQL)
# 1. Abrir MySQL e executar:
# mysql -u root -p
# source database/create_database.sql

# Configurar variáveis de ambiente
# Criar arquivo backend/.env com:
# FLASK_ENV=development
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/fixtruck
# SECRET_KEY=sua-chave-secreta

# Executar aplicação
python app.py
```

### 2. Configurar Frontend

```bash
# Navegar para a pasta frontend
cd frontend

# Abrir em servidor local (Python 3)
python -m http.server 8000

# Ou usar outro servidor web (nginx, Apache, etc.)
```

Acesso: `http://localhost:8000`

## 📚 Tecnologias

- **Backend**: Python, Flask, Flask-SQLAlchemy
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Maps**: Leaflet.js
- **API**: RESTful com JSON

## 🔐 Autenticação

Dois tipos de usuário:
- **Gestor**: Aprova orçamentos, gerencia frota
- **Motorista**: Registra ocorrências, busca oficinas

## 📝 Funcionalidades Principais

### Módulo Motorista
- ✅ Registrar ocorrência com GPS
- ✅ Buscar oficinas próximas em mapa
- ✅ Chat com oficina/gestor
- ✅ Histórico de ocorrências

### Módulo Gestor
- ✅ Dashboard com métricas
- ✅ Aprovar/rejeitar orçamentos
- ✅ Encerrar ocorrências
- ✅ Relatórios de downtime
- ✅ Histórico de ocorrências

## 🗺️ Integração de Dados Geográficos

O sistema integra dados do shapefile BHMap para exibir oficinas:
- Localização geográfica
- Especialidades (CNAE)
- Informações de contato
- Distância em raio configurável

## 🔗 API Endpoints

### Autenticação
- `POST /api/auth/registrar` - Registrar novo usuário
- `POST /api/auth/login` - Fazer login
- `POST /api/auth/alterar-senha` - Alterar senha

### Ocorrências
- `GET /api/ocorrencias` - Listar ocorrências
- `POST /api/ocorrencias` - Criar ocorrência
- `PUT /api/ocorrencias/{id}/encerrar` - Encerrar ocorrência

### Oficinas
- `GET /api/oficinas` - Listar oficinas
- `POST /api/oficinas/buscar-por-raio` - Buscar por distância

### Orçamentos
- `POST /api/orcamentos` - Criar orçamento
- `PUT /api/orcamentos/{id}/aprovar` - Aprovar orçamento
- `PUT /api/orcamentos/{id}/rejeitar` - Rejeitar orçamento

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se o backend está rodando em `http://localhost:5000`
2. Se o banco de dados está configurado corretamente
3. Verifique os logs do console do navegador (F12)

## 📄 Licença

Projeto educacional - Ensino Médio

# 🚀 GUIA RÁPIDO DE INICIALIZAÇÃO - FixTruck

## ⚡ Iniciar em 5 Minutos

### Pré-requisitos
- Python 3.10+
- MySQL Server
- Navegador moderno

### Windows PowerShell

#### 1️⃣ Preparar Backend

```powershell
# Navegue para a pasta do projeto
cd C:\projetos\teseta a\fixtruck\backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
Copy-Item .env.example .env

# Editar .env com suas credenciais MySQL
notepad .env

# Inicializar banco de dados (execute no MySQL)
mysql -u root -p < database\create_database.sql

# Rodar servidor Flask
python app.py
```

Será exibido:
```
Running on http://127.0.0.1:5000
```

#### 2️⃣ Preparar Frontend

Abra outro terminal PowerShell:

```powershell
# Navegue para frontend
cd C:\projetos\teseta a\fixtruck\frontend

# Iniciar servidor HTTP simples (Python 3)
python -m http.server 8000
```

Acesse: `http://localhost:8000`

## 📱 Testar a Aplicação

### 1. Registrar Novo Usuário
- Click em "Registrar"
- Preencher formulário (ex: gestor@test.com)
- Selecionar tipo: **Gestor** ou **Motorista**

### 2. Fazer Login
- Email: gestor@test.com
- Senha: (conforme registrou)

### 3. Testar Funcionalidades
**Para Motorista:**
- Nova Ocorrência → Preencher problema
- Mapa vai mostrar oficinas próximas

**Para Gestor:**
- Dashboard → Ver ocorrências abertas
- Approve/Reject orçamentos

## 🔧 Troubleshooting

### ❌ "API não está respondendo"
```powershell
# Verificar se Flask está rodando
# Terminal 1: Backend
python app.py

# Deve exibir: Running on http://127.0.0.1:5000
```

### ❌ "Erro de conexão MySQL"
```powershell
# Verificar credenciais em .env
# Padrão:
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/fixtruck

# Testar conexão MySQL:
mysql -u root -p
```

### ❌ "Module not found"
```powershell
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

## 📚 Estrutura de Pastas

```
fixtruck/
├── frontend/        ← Abrir no navegador
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── ...
│
├── backend/         ← Rodar em Terminal 1
│   ├── app.py
│   ├── models/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── database/
│   └── requirements.txt
│
├── README.md        ← Documentação completa
└── .gitignore
```

## 🎯 Próximos Passos

1. **Importar Shapefile**
   - Lugar dados geográficos em `backend/data/`
   - Implementar script de ingestão em `backend/services/`

2. **Customizar CSS**
   - Editar `frontend/css/styles.css`
   - Ajustar cores e layout

3. **Testar API**
   - Usar Postman ou Insomnia
   - Base URL: `http://localhost:5000/api`

## 📖 Documentação Completa

Veja `README.md` para:
- Endpoints da API
- Estrutura de dados
- Fluxo de autenticação
- Integração de mapas

## 💡 Dicas

- **Browser DevTools (F12)** → Console mostra logs da API
- **Flask Debug** → Erros com stack trace automático
- **SQLAlchemy ORM** → Modelos já criados em `backend/models/`

---

✅ **Status**: MVP funcional com funcionalidades críticas implementadas!

Para dúvidas, verifique:
1. README.md
2. Logs do terminal
3. Console do navegador (F12)

# Projeto_Software_FixTruck

## Integrantes:

- Arthur Cezar
- Caio Luis
- Gustavo Henrique
- João Otávio
- Mateus Torres
- Pedro Lima

## Stack utilizada:
### Front-end:
- HTML
- CSS
- Javascript

### Back-end:
- Python

### Banco de dados:
- Flask SQLAlchemy

## Descrição:
O FixTruck é um sistema de gestão de ocorrências mecânicas projetado especificamente para transportadoras e frotas de transporte rodoviário. O objetivo principal da solução é reduzir o downtime quando ocorre uma pane em rota. A plataforma conecta motoristas e gestores a oficinas mecânicas próximas através de geolocalização e filtros baseados na especialidade técnica.

## Como Utilizar:

Para o projeto funcionar, você precisa do Python no seu computador:
1. Baixe a versão mais recente em [python.org/downloads](https://www.python.org/downloads/).
2. Abra o instalador e **MARQUE** a caixinha escrito **"Add Python.exe to PATH"** (isso é muito importante!).
3. Clique em **"Install Now"** e avance até o final.

### 1. Baixar o projeto
Abra o seu terminal (PowerShell) e clone o repositório:
```powershell
git clone https://github.com/Gustavoufjfjv1/Projeto_Software_FixTruck
```

Agora, entre na pasta do projeto:
```powershell
cd Projeto_Software_FixTruck
```

### 2. Iniciar o Ambiente Virtual (venv)
Crie e ative o ambiente virtual para isolar as ferramentas:
```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

### 3. Baixar os Requirements
Instale todas as ferramentas e pacotes necessários para o projeto:
```powershell
pip install -r requirements.txt
```

### 4. Executar o Projeto
Ligue o servidor do Flask com o comando:
```powershell
flask run
```

### 5. Acessar o Site
Após o comando acima, o terminal vai carregar o projeto. Abra o seu navegador de internet (como Chrome ou Edge) e pesquise pelo link abaixo na barra de endereços:
```text
http://127.0.0.1:5000
```
Deixe a janela do terminal aberta enquanto estiver usando o site.

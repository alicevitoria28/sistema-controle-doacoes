# 📦 Sistema de Controle de Doações

Sistema desktop desenvolvido em Python para gerenciamento e organização de doações.

## 🎯 Sobre o projeto

O **Sistema de Controle de Doações** é uma aplicação desktop desenvolvida em Python com o objetivo de facilitar o cadastro, organização, consulta e gerenciamento de doações.

O projeto foi desenvolvido aplicando conceitos de desenvolvimento de software, criação de interfaces gráficas, autenticação de usuários, persistência de dados e manipulação de arquivos.

## ✨ Funcionalidades

- 🔐 Sistema de login
- 👤 Autenticação de usuários
- 📦 Cadastro de doações
- 🔎 Consulta e pesquisa de registros
- ✏️ Edição de informações
- 🗑️ Exclusão de registros
- 💾 Persistência de dados utilizando SQLite
- 📊 Exportação de informações para Excel
- 🎨 Interface gráfica
- 🌓 Alternância de tema
- 🔒 Armazenamento de senhas utilizando bcrypt

## 🖥️ Demonstração

### 🔐 Tela de Login

![Tela de Login](screenshots/login.png)

### 📝 Cadastro de Doação

![Cadastro de Doação](screenshots/cadastro-doacao.png)

### 👤 Cadastro/Login

![Cadastro/Login](screenshots/cadastro-login.png)

## 🛠️ Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| 🐍 Python | Linguagem principal |
| 🎨 Tkinter | Interface gráfica |
| 🎨 ttkbootstrap | Estilização da interface |
| 🔐 bcrypt | Hash de senhas |
| 🗄️ SQLite | Banco de dados |
| 📊 OpenPyXL | Exportação para Excel |
| 🔧 Git | Controle de versão |
| 🌐 GitHub | Hospedagem e versionamento do projeto |

## 📁 Estrutura do projeto

```text
sistema-controle-doacoes/
│
├── main.py                  # Inicialização da aplicação
├── interface.py             # Interface principal
├── banco_dados.py           # Operações relacionadas ao banco de dados
├── login.py                 # Sistema de autenticação
├── migrar_schema.py         # Migração/atualização do banco
│
├── config.json              # Configurações do sistema
├── config.txt               # Configuração de tema
├── login_ilustracao.png     # Ilustração da tela de login
│
├── requirements.txt         # Dependências do projeto
├── .gitignore               # Arquivos ignorados pelo Git
├── screenshots/             # Capturas de tela da aplicação
└── README.md                # Documentação do projeto
```

## ⚙️ Como Executar

### 📋 Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado em sua máquina:

- 🐍 Python 3.x
- 🔧 Git

### 🚀 Passo a Passo

**1️⃣ Clone o repositório**

```bash
git clone https://github.com/alicevitoria28/sistema-controle-doacoes.git
```

**2️⃣ Acesse a pasta do projeto**

```bash
cd sistema-controle-doacoes
```

**3️⃣ Crie um ambiente virtual**

```powershell
py -m venv .venv
```

**4️⃣ Ative o ambiente virtual**

No Windows PowerShell:

```powershell
.venv\Scripts\activate
```

Após a ativação, o terminal deverá apresentar `(.venv)` no início da linha.

**5️⃣ Instale as dependências**

```powershell
pip install -r requirements.txt
```

Principais dependências utilizadas:

- `ttkbootstrap`
- `bcrypt`
- `openpyxl`

**6️⃣ Execute a aplicação**

```powershell
py main.py
```

## 🗄️ Detalhes Arquiteturais

### 💾 Banco de Dados

A aplicação utiliza **SQLite** para armazenamento local das informações relacionadas às doações.

Os arquivos do banco de dados são ignorados pelo Git por meio do `.gitignore`, evitando que dados locais sejam enviados ao repositório público.

### 🔐 Segurança

O projeto utiliza a biblioteca **bcrypt** para realizar o hash das senhas dos usuários, evitando o armazenamento de senhas em texto puro.

### 📊 Exportação de Dados

O sistema possui funcionalidade de exportação de informações para planilhas em formato Excel, utilizando a biblioteca **OpenPyXL**.

### 🎨 Interface Gráfica

A interface foi desenvolvida utilizando **Tkinter** em conjunto com **ttkbootstrap**, oferecendo componentes visuais personalizados e suporte à alternância entre temas.

## 🎓 Objetivos de Aprendizado

Este projeto foi desenvolvido com o objetivo de praticar e consolidar conhecimentos relacionados a:

- 🐍 Programação em Python
- 💻 Desenvolvimento de aplicações desktop
- 🎨 Criação e estilização de interfaces gráficas
- 🏗️ Organização e estruturação de código
- 🗄️ Integração e manipulação de banco de dados SQLite
- 🔐 Autenticação de usuários e hash de senhas
- 📊 Manipulação de arquivos e exportação de dados
- 📦 Gerenciamento de dependências e ambientes virtuais
- 🔧 Controle de versão com Git e GitHub

## 🚧 Próximas Melhorias

- [ ] Implementação de testes automatizados
- [ ] Melhorias na validação de campos e formulários
- [ ] Sistema com diferentes níveis de acesso
- [ ] Relatórios e gráficos analíticos mais completos
- [ ] Aprimoramentos na experiência do usuário (UX)
- [ ] Ampliação das funcionalidades de gerenciamento e filtros

## 👩‍💻 Desenvolvedora

**Alice Vitória**

Estudante de Sistemas de Informação, com interesse em desenvolvimento de software, programação e tecnologia.

Este projeto faz parte da minha jornada de aprendizado e desenvolvimento na área de tecnologia.

---

⭐ *Se você gostou deste projeto, considere deixar uma estrela no repositório!*
# 📦 Sistema de Controle de Doações

Sistema desktop desenvolvido em Python para gerenciamento e organização de doações.

## 🎯 Sobre o projeto

O Sistema de Controle de Doações é uma aplicação desktop desenvolvida em Python com o objetivo de facilitar o cadastro, organização, consulta e gerenciamento de doações.

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
- 🔒 Armazenamento seguro de senhas utilizando bcrypt

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
└── README.md                # Documentação do projeto
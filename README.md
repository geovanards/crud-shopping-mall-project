# 🛍️ Sistema de Gerenciamento de Loja de Roupas

Um **mini-sistema completo em Python** para gerenciar o inventário de uma loja de roupas, com interface gráfica, banco de dados local e API RESTful integrada.

---

## 🧩 Funcionalidades Principais

### 1. Banco de Dados (SQLite)
- Armazena os dados em um arquivo local `loja.db`.
- Utiliza duas tabelas relacionadas: `categorias` e `produtos`.
- A tabela `produtos` possui uma **chave estrangeira (`categoria_id`)** que se relaciona com a tabela `categorias`.

---

### 2. Interface Gráfica (Tkinter)
- Realiza operações de **CRUD (Criar, Ler, Atualizar e Excluir)** de produtos.  
- Exibe os produtos em uma lista (`Treeview`).  
- Possui campos de formulário para **Nome**, **Tamanho**, **Preço** e um **Combobox** para selecionar a Categoria (carregada do banco de dados).  
- Exibe **mensagens de sucesso/erro** em uma barra de status.

---

### 3. API Local (FastAPI)
- Expõe os dados do **mesmo banco de dados** via uma **API RESTful**.  
- Permite operações de CRUD (GET, POST, PUT, DELETE) para **Categorias** e **Produtos**.  
- Inclui **documentação automática (Swagger UI)** para testes.

---
### Colaboradores:
- Geovana Rodrigues
- Taís Döring

---

### 📦 Instalação das Dependências

Abra o terminal na pasta do projeto e execute:

```bash
pip install -r requirements.txt

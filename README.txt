Nome da Aplicação:
Sistema de Gerenciamento de Loja de Roupas

Descrição das Funcionalidades:
Este é um mini-sistema completo em Python que gerencia um inventário de uma
loja de roupas. Ele permite o cadastro de Categorias (ex: Camisetas, Calças)
e Produtos (ex: Camiseta Gola V, Calça Jeans Skinny).

O sistema é composto por três partes integradas:

1.  Banco de Dados (SQLite):
    * Armazena os dados em um arquivo local 'loja.db'.
    * Utiliza duas tabelas relacionadas: 'categorias' e 'produtos'.
    * A tabela 'produtos' tem uma chave estrangeira (categoria_id)
        que se relaciona com a 'categorias'.

2.  Interface Gráfica (Tkinter):
    * Permite ao usuário realizar operações de CRUD (Criar, Ler,
        Atualizar, Excluir) nos produtos.
    * Exibe os produtos em uma lista (Treeview).
    * Possui campos de formulário para Nome, Tamanho, Preço e um
        Combobox para selecionar a Categoria (carregada do DB).
    * Fornece feedback ao usuário (sucesso/erro) em uma barra de status.

3.  API Local (FastAPI):
    * Expõe os dados do *mesmo* banco de dados através de uma API RESTful.
    * Permite operações de CRUD (GET, POST, PUT, DELETE) para
        Categorias e Produtos.
    * Inclui documentação automática (Swagger UI) para testes.

Como Executar o Projeto:

1.  Pré-requisitos:
    * Ter o Python 3.7+ instalado.

2.  Instalação das Dependências:
    * Abra um terminal na pasta do projeto.
    * Execute o comando:
        pip install -r requirements.txt
    * (Se o 'requirements.txt' não for usado, instale manualmente:
        pip install fastapi uvicorn)

3.  Executando a Interface Gráfica (GUI):
    * No terminal, na pasta do projeto, execute:
        python main.py
    * Isso iniciará o banco de dados (criando 'loja.db') e abrirá a
        janela do programa.
    * (Recomendado) Adicione algumas categorias primeiro (pela API ou
        modificando db.py) para que o Combobox da GUI funcione melhor.
        *O script db.py já adiciona 4 categorias padrão na primeira execução.*

4.  Executando a API Local (em paralelo):
    * Abra um *segundo* terminal na mesma pasta do projeto.
    * Execute o comando:
        uvicorn api:app --reload
    * A API estará rodando em http://127.0.0.1:8000

5.  Verificando a Integração:
    * Abra http://127.0.0.1:8000/docs no seu navegador para ver
        a documentação da API e testar as rotas.
    * Adicione um produto usando a Interface Gráfica (GUI).
    * Acesse a rota GET /produtos/ na API (pelo navegador ou
        pela documentação /docs).
    * Você verá que o produto adicionado pela GUI aparece na
        resposta da API, provando que ambos acessam o mesmo banco de dados.
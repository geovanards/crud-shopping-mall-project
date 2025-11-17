# api.py
from flask import Flask, request, jsonify
# Importa as estruturas de dados e funções auxiliares do db.py
from db import CATEGORIES_DATA, PRODUCTS_DATA, _get_next_id, _find_item_by_id, _find_category_name, Database

app = Flask(__name__)

def format_product_api(product):
    """Adiciona o nome da categoria ao produto para a resposta da API."""
    product_copy = product.copy()
    category_id = product_copy.get('categoria_id')
    product_copy['categoria_nome'] = _find_category_name(category_id)
    return product_copy

# --- Rotas Base ---

@app.route('/', methods=['GET'])
def home():
    return "Bem-vindo à API de Loja de Roupas (Flask - In-Memory)"

# -----------------------------
# --- ROTAS DE PRODUTOS (CRUD) ---
# -----------------------------

@app.route('/produtos', methods=['GET'])
def get_produtos():
    formatted_products = sorted([format_product_api(p) for p in PRODUCTS_DATA], key=lambda x: x['nome'])
    return jsonify(formatted_products)

@app.route('/produtos/<int:id>', methods=['GET'])
def get_produto(id):
    produto = _find_item_by_id(PRODUCTS_DATA, id)
    if produto:
        return jsonify(format_product_api(produto))
    return jsonify({"erro": "Produto não encontrado"}), 404

@app.route('/produtos', methods=['POST'])
def adicionar_produto():
    novo = request.get_json()
    
    required_fields = ["nome", "preco", "categoria_id"]
    if not all(k in novo for k in required_fields):
        return jsonify({"erro": f"Campos obrigatórios ausentes: {', '.join(required_fields)}"}), 400

    categoria_id = novo.get('categoria_id')
    if not _find_item_by_id(CATEGORIES_DATA, categoria_id):
         return jsonify({"erro": f"Categoria com ID {categoria_id} não existe."}), 400
         
    novo["id"] = _get_next_id('produtos')
    PRODUCTS_DATA.append(novo)
    return jsonify(format_product_api(novo)), 201

@app.route('/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    dados = request.get_json()
    produto = _find_item_by_id(PRODUCTS_DATA, id)
    
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
        
    if 'categoria_id' in dados:
        if not _find_item_by_id(CATEGORIES_DATA, dados['categoria_id']):
             return jsonify({"erro": f"Categoria com ID {dados['categoria_id']} não existe."}), 400
             
    produto.update(dados)
    return jsonify(format_product_api(produto))

@app.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    produto = _find_item_by_id(PRODUCTS_DATA, id)
    if produto:
        PRODUCTS_DATA.remove(produto)
        return jsonify({"mensagem": f"Produto ID {id} removido com sucesso."})
    return jsonify({"erro": "Produto não encontrado"}), 404

# ------------------------------------
# --- ROTAS DE CATEGORIAS (CRUD) ---
# ------------------------------------

@app.route('/categorias', methods=['GET'])
def get_categorias():
    return jsonify(sorted(CATEGORIES_DATA, key=lambda x: x['nome']))

@app.route('/categorias/<int:id>', methods=['GET'])
def get_categoria(id):
    categoria = _find_item_by_id(CATEGORIES_DATA, id)
    if categoria:
        return jsonify(categoria)
    return jsonify({"erro": "Categoria não encontrada"}), 404

@app.route('/categorias', methods=['POST'])
def adicionar_categoria():
    novo = request.get_json()
    
    if 'nome' not in novo:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400

    if any(c['nome'].lower() == novo['nome'].lower() for c in CATEGORIES_DATA):
        return jsonify({"erro": f"Categoria '{novo['nome']}' já existe."}), 400
        
    novo["id"] = _get_next_id('categorias')
    CATEGORIES_DATA.append(novo)
    return jsonify(novo), 201

@app.route('/categorias/<int:id>', methods=['PUT'])
def atualizar_categoria(id):
    dados = request.get_json()
    categoria = _find_item_by_id(CATEGORIES_DATA, id)
    
    if not categoria:
        return jsonify({"erro": "Categoria não encontrada"}), 404
        
    if 'nome' in dados:
        if any(c['nome'].lower() == dados['nome'].lower() and c['id'] != id for c in CATEGORIES_DATA):
            return jsonify({"erro": f"Categoria '{dados['nome']}' já existe."}), 400
        categoria['nome'] = dados['nome']
        
    return jsonify(categoria)

@app.route('/categorias/<int:id>', methods=['DELETE'])
def deletar_categoria(id):
    categoria = _find_item_by_id(CATEGORIES_DATA, id)
    if not categoria:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    
    if any(p.get('categoria_id') == id for p in PRODUCTS_DATA):
        return jsonify({"erro": "Não é possível excluir. Existem produtos usando esta categoria."}), 400
        
    CATEGORIES_DATA.remove(categoria)
    return jsonify({"mensagem": f"Categoria ID {id} removida com sucesso."})

if __name__ == '__main__':
    # Inicializa os dados (garante que as listas CATEGORIES_DATA e PRODUCTS_DATA sejam populadas)
    Database() 
    
    app.run(debug=True)
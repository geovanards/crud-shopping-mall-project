# api.py
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db import Database

# --- Modelos de Dados (Pydantic) ---
# Usados pelo FastAPI para validação, documentação e resposta.

class CategoriaBase(BaseModel):
    nome: str

class Categoria(CategoriaBase):
    id: int

    class Config:
        orm_mode = True # Permite mapear de/para objetos do DB (ex: sqlite3.Row)

class ProdutoBase(BaseModel):
    nome: str
    tamanho: Optional[str] = None
    preco: float
    categoria_id: int

class ProdutoCreate(ProdutoBase):
    # Modelo para criar um produto (não tem ID ainda)
    pass

class Produto(ProdutoBase):
    id: int
    categoria_nome: Optional[str] = None # Incluindo nome da categoria (do JOIN)

    class Config:
        orm_mode = True

# --- Inicialização ---
app = FastAPI(
    title="API Loja de Roupas", 
    description="API para gerenciar produtos e categorias."
)

# Instancia o banco de dados
db = Database("loja.db") # Conecta ao mesmo banco de dados!

# --- Rotas da API ---

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API da Loja de Roupas. Acesse /docs para a documentação."}

# --- Rotas de Categorias (CRUD Completo) ---

@app.post("/categorias/", response_model=Categoria, status_code=201)
def create_category(categoria: CategoriaBase):
    """Cria uma nova categoria."""
    cat_id = db.add_category(categoria.nome)
    if cat_id is None:
        raise HTTPException(status_code=400, detail="Categoria já existe ou erro ao criar.")
    return Categoria(id=cat_id, nome=categoria.nome)

@app.get("/categorias/", response_model=List[Categoria])
def read_categories():
    """Lista todas as categorias."""
    categories_db = db.get_categories()
    # Converte o resultado (sqlite3.Row) para o modelo Pydantic
    return [Categoria.from_orm(cat) for cat in categories_db]

@app.put("/categorias/{categoria_id}", response_model=Categoria)
def update_category(categoria_id: int, categoria: CategoriaBase):
    """Atualiza o nome de uma categoria."""
    result = db.update_category(categoria_id, categoria.nome)
    
    if result == "UNIQUE_VIOLATION":
        raise HTTPException(status_code=400, detail=f"O nome '{categoria.nome}' já está em uso.")
    if not result:
        raise HTTPException(status_code=404, detail=f"Categoria com ID {categoria_id} não encontrada.")
        
    return Categoria(id=categoria_id, nome=categoria.nome)

@app.delete("/categorias/{categoria_id}", response_model=dict)
def delete_category(categoria_id: int):
    """Exclui uma categoria (se não estiver em uso)."""
    result = db.delete_category(categoria_id)
    
    if result == "IN_USE":
        raise HTTPException(status_code=400, detail="Categoria está em uso por produtos. Não pode ser excluída.")
    if result == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=f"Categoria com ID {categoria_id} não encontrada.")
    if result == "ERROR":
         raise HTTPException(status_code=500, detail="Erro interno ao excluir categoria.")

    return {"message": f"Categoria ID {categoria_id} excluída com sucesso."}


# --- Rotas de Produtos (CRUD Completo) ---

def _get_produto_or_404(produto_id: int):
    """Função helper para buscar um produto pelo ID e formatá-lo."""
    # (Ineficiente, mas simples para este projeto)
    produtos = db.get_products() 
    produto_db = next((p for p in produtos if p['id'] == produto_id), None)
    
    if produto_db is None:
        return None
    
    # Converte sqlite3.Row para um objeto Pydantic
    return Produto.from_orm(produto_db)


@app.post("/produtos/", response_model=Produto, status_code=201)
def create_product(produto: ProdutoCreate):
    """Cria um novo produto."""
    try:
        produto_id = db.add_product(
            produto.nome,
            produto.tamanho,
            produto.preco,
            produto.categoria_id
        )
        if produto_id is None:
            raise HTTPException(status_code=400, detail="Erro ao criar produto (verifique se a categoria_id existe).")
        
        # Para a resposta, buscamos o produto recém-criado para ter todos os dados
        novo_produto = _get_produto_or_404(produto_id)
        if novo_produto:
             return novo_produto
        else:
             raise HTTPException(status_code=404, detail="Produto criado mas não encontrado.")
             
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@app.get("/produtos/", response_model=List[Produto])
def read_products():
    """Lista todos os produtos (com detalhes da categoria)."""
    products_db = db.get_products()
    return [Produto.from_orm(p) for p in products_db]

@app.put("/produtos/{produto_id}", response_model=Produto)
def update_product(produto_id: int, produto: ProdutoCreate):
    """Atualiza um produto existente."""
    success = db.update_product(
        produto_id,
        produto.nome,
        produto.tamanho,
        produto.preco,
        produto.categoria_id
    )
    if not success:
        raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado ou erro ao atualizar.")

    # Busca o produto atualizado para retornar
    produto_atualizado = _get_produto_or_404(produto_id)
    if produto_atualizado:
         return produto_atualizado
    else:
         raise HTTPException(status_code=404, detail="Produto atualizado mas não encontrado.")

@app.delete("/produtos/{produto_id}", response_model=dict)
def delete_product(produto_id: int):
    """Exclui um produto."""
    success = db.delete_product(produto_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado.")
    
    return {"message": f"Produto ID {produto_id} excluído com sucesso."}

# --- Comando para rodar a API (no terminal) ---
# uvicorn api:app --reload
import copy
from typing import List, Dict, Any, Optional

# --- Simulação de Dados em Memória ---
CATEGORIES_DATA = []
PRODUCTS_DATA = []

_next_category_id = 1
_next_product_id = 1

def _get_next_id(data_list_name: str) -> int:
    """Gera o próximo ID sequencial."""
    global _next_category_id, _next_product_id
    if data_list_name == 'categorias':
        id_val = _next_category_id
        _next_category_id += 1
        return id_val
    else:
        id_val = _next_product_id
        _next_product_id += 1
        return id_val

def _find_item_by_id(data_list: List[Dict[str, Any]], item_id: int) -> Optional[Dict[str, Any]]:
    """Função auxiliar para encontrar um item pelo ID."""
    return next((item for item in data_list if item.get("id") == item_id), None)

def _find_category_name(category_id: int) -> Optional[str]:
    """Função auxiliar para encontrar o nome da categoria."""
    cat = _find_item_by_id(CATEGORIES_DATA, category_id)
    return cat['nome'] if cat else None

class Row:
    """Simula o objeto sqlite3.Row para compatibilidade com o código GUI."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
    def __getitem__(self, key: str) -> Any:
        return self._data.get(key)
        
    def keys(self):
        return self._data.keys()
        
    def __iter__(self):
        return iter(self._data.values())
        
    def __len__(self):
        return len(self._data)
        
    def __repr__(self):
        return f"Row({self._data})"
        
    def __eq__(self, other):
        return self._data == other._data if isinstance(other, Row) else False
        
    def __hash__(self):
        return hash(tuple(sorted(self._data.items())))

class Database:
    """Simula o Banco de Dados para a GUI."""
    
    def __init__(self, db_file="loja.db"):
        self.create_tables() 
        self._seed_data()

    def create_tables(self):
        pass 
        
    def _seed_data(self):
        """Adiciona dados padrão se as listas estiverem vazias."""
        if not CATEGORIES_DATA:
            self.add_category("Camisetas")
            self.add_category("Calças")
            self.add_category("Calçados")
            self.add_product("Camiseta Básica", "G", 49.90, 1)
            self.add_product("Calça Cargo", "42", 189.90, 2)
            self.add_product("Sapatênis", "40", 129.50, 3)

    # CRUD CATEGORIAS 
    def add_category(self, nome: str) -> Optional[int]:
        if any(c['nome'].lower() == nome.lower() for c in CATEGORIES_DATA):
            return None
            
        new_id = _get_next_id('categorias')
        new_category = {"id": new_id, "nome": nome}
        CATEGORIES_DATA.append(new_category)
        return new_id

    def get_categories(self) -> List[Row]:
        sorted_data = sorted(CATEGORIES_DATA, key=lambda x: x['nome'])
        return [Row(copy.deepcopy(c)) for c in sorted_data]

    def update_category(self, id: int, nome: str) -> Any:
        if any(c['nome'].lower() == nome.lower() and c['id'] != id for c in CATEGORIES_DATA):
            return "UNIQUE_VIOLATION"
            
        category = _find_item_by_id(CATEGORIES_DATA, id)
        if category:
            category['nome'] = nome
            return True
        return False

    def delete_category(self, id: int) -> str:
        category = _find_item_by_id(CATEGORIES_DATA, id)
        if not category:
            return "NOT_FOUND"
        
        if any(p.get('categoria_id') == id for p in PRODUCTS_DATA):
            return "IN_USE"
            
        CATEGORIES_DATA.remove(category)
        return "SUCCESS"

    # CRUD PRODUTOS 
    def add_product(self, nome: str, tamanho: str, preco: float, categoria_id: int) -> Optional[int]:
        if not _find_category_name(categoria_id):
            return None 

        new_id = _get_next_id('produtos')
        new_product = {
            "id": new_id, "nome": nome, "tamanho": tamanho, 
            "preco": preco, "categoria_id": categoria_id
        }
        PRODUCTS_DATA.append(new_product)
        return new_id

    def get_products(self) -> List[Row]:
        result = []
        for p in PRODUCTS_DATA:
            product_dict = copy.deepcopy(p)
            product_dict['categoria_nome'] = _find_category_name(p.get('categoria_id'))
            result.append(Row(product_dict))
            
        return sorted(result, key=lambda r: r['nome'])

    def update_product(self, id: int, nome: str, tamanho: str, preco: float, categoria_id: int) -> bool:
        product = _find_item_by_id(PRODUCTS_DATA, id)
        if not product or not _find_category_name(categoria_id):
            return False
            
        product.update({
            "nome": nome, "tamanho": tamanho, "preco": preco, "categoria_id": categoria_id
        })
        return True

    def delete_product(self, id: int) -> bool:
        product = _find_item_by_id(PRODUCTS_DATA, id)
        if product:
            PRODUCTS_DATA.remove(product)
            return True
        return False
# db.py
import sqlite3
import os

class Database:
    """Classe para gerenciar o banco de dados SQLite da loja."""
    
    def __init__(self, db_file="loja.db"):
        self.db_file = db_file
        # tabelas criadas na inicialização
        self.create_tables()

    def get_connection(self):
        """Retorna uma conexão com o banco de dados."""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row  # colunas por nome
            return conn
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def create_tables(self):
        """Cria as tabelas 'categorias' e 'produtos' se não existirem."""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Tabela de Categorias
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE
                )
                """)
                
                # Tabela de Produtos
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    tamanho TEXT,
                    preco REAL NOT NULL,
                    categoria_id INTEGER,
                    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
                        ON DELETE SET NULL -- Se categoria for deletada, seta para NULL
                )
                """)
                
                conn.commit()
            except sqlite3.Error as e:
                print(f"Erro ao criar tabelas: {e}")
            finally:
                conn.close()

    # crud categorias ------------------------------------------------------------------------------------

    def add_category(self, nome):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar categoria: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_categories(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias ORDER BY nome")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar categorias: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_category(self, id, nome):
        """Atualiza o nome de uma categoria existente."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE categorias SET nome = ? WHERE id = ?", (nome, id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar categoria: {e}")
            # retorna uma string de erro se for violação de chave única (nome repetido)
            if "UNIQUE" in str(e).upper():
                return "UNIQUE_VIOLATION"
            return False
        finally:
            if conn:
                conn.close()

    def delete_category(self, id):
        """Exclui uma categoria, se não estiver em uso por produtos."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # 1. Verifica se a categoria está em uso
            cursor.execute("SELECT 1 FROM produtos WHERE categoria_id = ?", (id,))
            if cursor.fetchone():
                # Se encontrou (fetchone() não é None), a categoria está em uso
                return "IN_USE"
            
            # 2. Se não estiver em uso, exclui
            cursor.execute("DELETE FROM categorias WHERE id = ?", (id,))
            conn.commit()
            
            # Retorna sucesso se uma linha foi afetada
            return "SUCCESS" if cursor.rowcount > 0 else "NOT_FOUND"
            
        except sqlite3.Error as e:
            print(f"Erro ao deletar categoria: {e}")
            return "ERROR"
        finally:
            if conn:
                conn.close()

    #  crud produtos ---------------------------------------------------------------------------------------------------

    def add_product(self, nome, tamanho, preco, categoria_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO produtos (nome, tamanho, preco, categoria_id) VALUES (?, ?, ?, ?)",
                (nome, tamanho, preco, categoria_id)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar produto: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_products(self):
        """Retorna todos os produtos com o nome da categoria."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # JOIN para o nome da categoria----------------------------------
            cursor.execute("""
                SELECT 
                    p.id, 
                    p.nome, 
                    p.tamanho, 
                    p.preco, 
                    c.nome as categoria_nome,
                    p.categoria_id
                FROM produtos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                ORDER BY p.nome
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_product(self, id, nome, tamanho, preco, categoria_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE produtos 
                SET nome = ?, tamanho = ?, preco = ?, categoria_id = ?
                WHERE id = ?
                """,
                (nome, tamanho, preco, categoria_id, id)
            )
            conn.commit()
            return cursor.rowcount > 0  #retorna true
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def delete_product(self, id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0 #retorna valor true
        except sqlite3.Error as e:
            print(f"Erro ao deletar produto: {e}")
            return False
        finally:
            if conn:
                conn.close()

#  iniciar o db: adicionar categorias
if __name__ == "__main__":
    db = Database()
    print("Banco de dados e tabelas verificados/criados.")
    
    # adicionando categorias padrão se não existirem
    if not db.get_categories():
        print("Adicionando categorias padrão...")
        db.add_category("Camisetas")
        db.add_category("Calças")
        db.add_category("Calçados")
        db.add_category("Acessórios")
    
    print("Categorias existentes:")
    for cat in db.get_categories():
        print(f"- ID: {cat['id']}, Nome: {cat['nome']}")
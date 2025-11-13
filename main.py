# main.py
import tkinter as tk
from db import Database
from gui import App

if __name__ == "__main__":
    # 1. Inicializa o banco de dados (cria o arquivo .db e as tabelas)
    db = Database(db_file="loja.db")
    
    # 2. Cria a janela principal do Tkinter
    root = tk.Tk()
    
    # 3. Inicializa a aplicação da GUI, passando a janela e o banco de dados
    app = App(root, db)
    
    # 4. Inicia o loop principal da interface gráfica
    root.mainloop()
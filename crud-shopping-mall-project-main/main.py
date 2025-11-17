import tkinter as tk
from db import Database
from gui import App

if __name__ == "__main__":
    db = Database(db_file="loja.db")
    root = tk.Tk()
    app = App(root, db)

    root.mainloop()
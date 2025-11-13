# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import Database

#
# pop up janelas-
#
class CategoryWindow(tk.Toplevel):
    """Janela para gerenciar (CRUD) as Categorias."""
    
    def __init__(self, master, db, main_app_ref):
        """
        Inicializa a janela.
        master: A janela pai (root).
        db: A instância do banco de dados.
        main_app_ref: A referência à aplicação principal (App) para 
                      podermos atualizar o combobox dela.
        """
        super().__init__(master)
        self.title("Gerenciador de Categorias")
        self.geometry("450x400")
        
        # transient() faz a janela aparecer sobre a janela mestre.
        self.transient(master)
        # grab_set() torna a janela "modal", bloqueando a janela principal
        # até que esta seja fechada.
        self.grab_set()
        
        self.db = db
        self.main_app_ref = main_app_ref # Referência à 'App' principal
        self.selected_category_id = None

        # wdgets --------------------------------------------------------------------
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.X)

        ttk.Label(form_frame, text="Nome:").pack(side=tk.LEFT, padx=5)
        self.entry_nome_cat = ttk.Entry(form_frame, width=30)
        self.entry_nome_cat.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)

        self.btn_add_cat = ttk.Button(button_frame, text="Adicionar", command=self.add_category_gui)
        self.btn_add_cat.pack(side=tk.LEFT, padx=5)

        self.btn_update_cat = ttk.Button(button_frame, text="Atualizar", command=self.update_category_gui, state=tk.DISABLED)
        self.btn_update_cat.pack(side=tk.LEFT, padx=5)

        self.btn_delete_cat = ttk.Button(button_frame, text="Excluir", command=self.delete_category_gui, state=tk.DISABLED)
        self.btn_delete_cat.pack(side=tk.LEFT, padx=5)

        self.btn_clear_cat = ttk.Button(button_frame, text="Limpar", command=self.clear_category_fields)
        self.btn_clear_cat.pack(side=tk.LEFT, padx=5)

        # --- Treeview para Categorias ---
        tree_frame = ttk.Frame(self, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_cat = ttk.Treeview(tree_frame, columns=("id", "nome"), show="headings", height=10)
        self.tree_cat.heading("id", text="ID")
        self.tree_cat.heading("nome", text="Nome")
        self.tree_cat.column("id", width=50, anchor=tk.CENTER)
        self.tree_cat.column("nome", width=300)
        
        scrollbar_cat = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_cat.yview)
        self.tree_cat.configure(yscroll=scrollbar_cat.set)
        scrollbar_cat.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_cat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree_cat.bind("<<TreeviewSelect>>", self.on_category_select)

        # carregamento inicial
        self.load_categories_list()

    def load_categories_list(self):
        """Carrega as categorias do DB para a Treeview desta janela."""
        # limpa a lista
        for i in self.tree_cat.get_children():
            self.tree_cat.delete(i)
        
        # busca e insere
        categories = self.db.get_categories()
        for cat in categories:
            self.tree_cat.insert("", tk.END, values=(cat['id'], cat['nome']))
    
    def on_category_select(self, event):
        """Chamado quando um item é selecionado na Treeview."""
        selected_items = self.tree_cat.selection()
        if not selected_items:
            return
        
        # pega os dados do item selecionado
        item = self.tree_cat.item(selected_items[0])
        values = item['values']
        
        self.selected_category_id = values[0] # Armazena o ID
        
        # preenche o campo de entrada
        self.entry_nome_cat.delete(0, tk.END)
        self.entry_nome_cat.insert(0, values[1]) # Nome

        # atualiza botões
        self.btn_add_cat.config(state=tk.DISABLED)
        self.btn_update_cat.config(state=tk.NORMAL)
        self.btn_delete_cat.config(state=tk.NORMAL)

    def clear_category_fields(self):
        """Limpa o campo de entrada e a seleção."""
        self.entry_nome_cat.delete(0, tk.END)
        self.tree_cat.selection_remove(self.tree_cat.selection()) # Limpa seleção
        self.selected_category_id = None
        
        # reseta botões
        self.btn_add_cat.config(state=tk.NORMAL)
        self.btn_update_cat.config(state=tk.DISABLED)
        self.btn_delete_cat.config(state=tk.DISABLED)

    def refresh_main_app_combobox(self):
        """Chama a função de recarregar da janela principal."""
        if self.main_app_ref:
            # chama a função load_categories() da classe App
            self.main_app_ref.load_categories()

    def add_category_gui(self):
        """Botão Adicionar: Adiciona nova categoria."""
        nome = self.entry_nome_cat.get().strip()
        if not nome:
            messagebox.showwarning("Campo Vazio", "O nome da categoria não pode estar vazio.", parent=self)
            return
        
        new_id = self.db.add_category(nome)
        
        if new_id:
            messagebox.showinfo("Sucesso", f"Categoria '{nome}' adicionada.", parent=self)
            self.load_categories_list() # Att a lista nesta janela
            self.clear_category_fields()
            self.refresh_main_app_combobox() # att combobox principal
        else:
            messagebox.showerror("Erro", f"A categoria '{nome}' já existe ou ocorreu um erro.", parent=self)

    def update_category_gui(self):
        """Botão Atualizar: Atualiza categoria selecionada."""
        nome = self.entry_nome_cat.get().strip()
        if not nome or self.selected_category_id is None:
            messagebox.showwarning("Dados Inválidos", "Selecione uma categoria e insira um novo nome.", parent=self)
            return

        result = self.db.update_category(self.selected_category_id, nome)
        
        if result == "UNIQUE_VIOLATION":
            messagebox.showerror("Erro", f"A categoria '{nome}' já existe.", parent=self)
        elif result:
            messagebox.showinfo("Sucesso", "Categoria atualizada.", parent=self)
            self.load_categories_list() # Att a lista nesta janela
            self.clear_category_fields()
            self.refresh_main_app_combobox() # att combobox principal
        else:
            messagebox.showerror("Erro", "Não foi possível atualizar a categoria.", parent=self)

    def delete_category_gui(self):
        """Botão Excluir: Exclui categoria selecionada."""
        if self.selected_category_id is None:
            messagebox.showwarning("Seleção Vazia", "Selecione uma categoria para excluir.", parent=self)
            return
        
        # Pede confirmação
        if not messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a categoria ID {self.selected_category_id}?\n\n(Isso só funcionará se não houver produtos nela.)", parent=self):
            return

        result = self.db.delete_category(self.selected_category_id)
        
        if result == "SUCCESS":
            messagebox.showinfo("Sucesso", "Categoria excluída.", parent=self)
            self.load_categories_list() # Att a lista nesta janela
            self.clear_category_fields()
            self.refresh_main_app_combobox() # Attt combobox principal
        elif result == "IN_USE":
            messagebox.showerror("Erro", "Não é possível excluir. Esta categoria está sendo usada por produtos.", parent=self)
        else: # NOT_FOUND ou ERROR
            messagebox.showerror("Erro", "Não foi possível excluir a categoria.", parent=self)


#
# --- JANELA PRINCIPAL DA APLICAÇÃO ---
#
class App:
    """Classe principal da aplicação de interface gráfica (Tkinter)."""
    
    def __init__(self, root, db):
        self.db = db
        self.root = root
        self.root.title("Gerenciador de Loja de Roupas")
        self.root.geometry("800x600")

        # Variáveis para armazenar o ID do item selecionado e as categorias
        self.selected_item_id = None
        self.categories = {}  # Dicionário {nome_categoria: id_categoria}
        
        # Referência para a janela de categorias (para evitar duplicação)
        self.category_win = None

        # --- Widgets ---
        self.create_widgets()
        
        # --- Carregamento Inicial ---
        self.load_categories()
        self.load_products()

    def create_widgets(self):
        """Cria e organiza os widgets na janela principal."""
        
        # --- Frame de Formulário (Entradas e Botões) ---
        form_frame = ttk.Frame(self.root, padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Nome
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_nome = ttk.Entry(form_frame, width=40)
        self.entry_nome.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)

        # Tamanho
        ttk.Label(form_frame, text="Tamanho:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=5)
        self.entry_tamanho = ttk.Entry(form_frame, width=10)
        self.entry_tamanho.grid(row=0, column=3, sticky=tk.W, pady=2, padx=5)

        # Preço
        ttk.Label(form_frame, text="Preço (R$):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_preco = ttk.Entry(form_frame, width=15)
        self.entry_preco.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)

        # Categoria (Combobox)
        ttk.Label(form_frame, text="Categoria:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=5)
        self.combo_categoria = ttk.Combobox(form_frame, state="readonly", width=20)
        self.combo_categoria.grid(row=1, column=3, sticky=tk.W, pady=2, padx=5)

        # --- Frame de Botões (Ações) ---
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_add = ttk.Button(button_frame, text="Adicionar", command=self.add_product)
        self.btn_add.pack(side=tk.LEFT, padx=5)
        
        self.btn_update = ttk.Button(button_frame, text="Atualizar", command=self.update_product, state=tk.DISABLED)
        self.btn_update.pack(side=tk.LEFT, padx=5)
        
        self.btn_delete = ttk.Button(button_frame, text="Excluir", command=self.delete_product, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = ttk.Button(button_frame, text="Limpar Campos", command=self.clear_entries)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # Botão para gerenciar categorias (alinhado à direita)
        self.btn_manage_categories = ttk.Button(button_frame, text="Gerenciar Categorias", command=self.open_category_window)
        self.btn_manage_categories.pack(side=tk.RIGHT, padx=10)


        # --- Frame da Lista (Treeview) ---
        tree_frame = ttk.Frame(self.root, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Colunas
        columns = ("id", "nome", "tamanho", "preco", "categoria")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Definindo Cabeçalhos
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("tamanho", text="Tamanho")
        self.tree.heading("preco", text="Preço (R$)")
        self.tree.heading("categoria", text="Categoria")

        # Definindo Largura das Colunas
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nome", width=250)
        self.tree.column("tamanho", width=80, anchor=tk.CENTER)
        self.tree.column("preco", width=100, anchor=tk.E) # Alinhado à direita (East)
        self.tree.column("categoria", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Evento de seleção na Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # --- Label de Feedback ---
        self.status_label = ttk.Label(self.root, text="Bem-vindo!", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=5)

    # --- Funções de Evento e Lógica ---

    def open_category_window(self):
        """Abre a janela modal de gerenciamento de categorias."""
        # Verifica se a janela já está aberta, para não criar múltiplas
        if not self.category_win or not self.category_win.winfo_exists():
            # Passa a janela root (mestre), o db, e 'self' (a própria classe App)
            self.category_win = CategoryWindow(self.root, self.db, self)
        else:
            self.category_win.lift() # Traz a janela para frente se já estiver aberta


    def load_categories(self):
        """Carrega as categorias do DB para o Combobox."""
        try:
            self.categories = {} # Limpa o dicionário
            categories_data = self.db.get_categories()
            category_names = []
            
            for cat in categories_data:
                self.categories[cat['nome']] = cat['id']
                category_names.append(cat['nome'])
                
            self.combo_categoria['values'] = category_names
            if category_names:
                self.combo_categoria.current(0) # Seleciona o primeiro item
            else:
                self.combo_categoria.set('') # Limpa se não houver categorias
                
        except Exception as e:
            self.show_feedback(f"Erro ao carregar categorias: {e}", "error")

    def load_products(self):
        """Carrega os produtos do DB para a Treeview."""
        try:
            # Limpa a lista atual
            for i in self.tree.get_children():
                self.tree.delete(i)
                
            # Busca novos dados
            products = self.db.get_products()
            
            # Insere dados na lista
            for product in products:
                # Formata o preço
                preco_formatado = f"{product['preco']:.2f}"
                categoria_nome = product['categoria_nome'] if product['categoria_nome'] else "Sem Categoria"
                
                self.tree.insert("", tk.END, values=(
                    product['id'],
                    product['nome'],
                    product['tamanho'],
                    preco_formatado,
                    categoria_nome
                ))
            
            self.show_feedback(f"{len(products)} produtos carregados.", "success")
        except Exception as e:
            self.show_feedback(f"Erro ao carregar produtos: {e}", "error")

    def get_form_data(self):
        """Valida e retorna os dados do formulário."""
        nome = self.entry_nome.get().strip()
        tamanho = self.entry_tamanho.get().strip()
        preco_str = self.entry_preco.get().strip()
        categoria_nome = self.combo_categoria.get()

        # Validação
        if not nome or not preco_str:
            self.show_feedback("Nome e Preço são obrigatórios.", "error")
            return None
        
        if not categoria_nome:
            self.show_feedback("Nenhuma categoria selecionada. Cadastre uma categoria primeiro.", "error")
            return None

        try:
            preco = float(preco_str.replace(",", ".")) # Aceita 10,50 ou 10.50
        except ValueError:
            self.show_feedback("Preço inválido. Use números (ex: 19.99).", "error")
            return None
        
        if preco < 0:
            self.show_feedback("Preço não pode ser negativo.", "error")
            return None

        categoria_id = self.categories.get(categoria_nome)
        if categoria_id is None:
            self.show_feedback("Categoria selecionada inválida.", "error")
            return None

        return nome, tamanho, preco, categoria_id

    def add_product(self):
        """Adiciona um novo produto ao banco de dados."""
        data = self.get_form_data()
        if data:
            nome, tamanho, preco, categoria_id = data
            try:
                self.db.add_product(nome, tamanho, preco, categoria_id)
                self.show_feedback(f"Produto '{nome}' adicionado com sucesso!", "success")
                self.load_products()
                self.clear_entries()
            except Exception as e:
                self.show_feedback(f"Erro ao adicionar produto: {e}", "error")

    def update_product(self):
        """Atualiza um produto existente."""
        if self.selected_item_id is None:
            self.show_feedback("Nenhum produto selecionado para atualizar.", "info")
            return

        data = self.get_form_data()
        if data:
            nome, tamanho, preco, categoria_id = data
            try:
                self.db.update_product(self.selected_item_id, nome, tamanho, preco, categoria_id)
                self.show_feedback(f"Produto ID {self.selected_item_id} atualizado!", "success")
                self.load_products()
                self.clear_entries()
            except Exception as e:
                self.show_feedback(f"Erro ao atualizar produto: {e}", "error")

    def delete_product(self):
        """Exclui um produto selecionado."""
        if self.selected_item_id is None:
            self.show_feedback("Nenhum produto selecionado para excluir.", "info")
            return
        
        # Confirmação
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto ID {self.selected_item_id}?"):
            try:
                self.db.delete_product(self.selected_item_id)
                self.show_feedback(f"Produto ID {self.selected_item_id} excluído.", "success")
                self.load_products()
                self.clear_entries()
            except Exception as e:
                self.show_feedback(f"Erro ao excluir produto: {e}", "error")

    def clear_entries(self):
        """Limpa os campos de entrada e a seleção."""
        self.entry_nome.delete(0, tk.END)
        self.entry_tamanho.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        
        # Reseta o combobox para o primeiro item, se houver
        if self.combo_categoria['values']:
             self.combo_categoria.current(0)
        else:
             self.combo_categoria.set('')

        self.tree.selection_remove(self.tree.selection()) # Limpa seleção da árvore
        self.selected_item_id = None
        
        # Reseta os botões
        self.btn_add.config(state=tk.NORMAL)
        self.btn_update.config(state=tk.DISABLED)
        self.btn_delete.config(state=tk.DISABLED)
        self.show_feedback("Campos limpos. Pronto para adicionar.", "info")

    def on_item_select(self, event):
        """Chamado quando um item é selecionado na Treeview."""
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                return
            
            item = self.tree.item(selected_items[0])
            values = item['values']
            
            # Pega o ID (primeira coluna)
            self.selected_item_id = values[0]

            # Preenche os campos de entrada
            self.clear_entries() # Limpa antes de preencher
            self.entry_nome.insert(0, values[1])      # Nome
            self.entry_tamanho.insert(0, values[2])   # Tamanho
            self.entry_preco.insert(0, values[3])     # Preço
            
            # Define o combobox para a categoria correta
            categoria_nome = values[4]
            if categoria_nome in self.categories:
                self.combo_categoria.set(categoria_nome)
            elif categoria_nome == "Sem Categoria" and self.combo_categoria['values']:
                self.combo_categoria.current(0) # Default
            else:
                 self.combo_categoria.set('') # Limpa se a categoria não for encontrada
            
            # Habilita/Desabilita botões
            self.btn_add.config(state=tk.DISABLED)
            self.btn_update.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
            self.show_feedback(f"Produto ID {self.selected_item_id} selecionado.", "info")

        except Exception as e:
            self.show_feedback(f"Erro ao selecionar item: {e}", "error")
            self.clear_entries()

    def show_feedback(self, message, msg_type="info"):
        """Exibe feedback ao usuário na barra de status."""
        self.status_label.config(text=f" {message}")
        if msg_type == "success":
            self.status_label.config(foreground="green")
        elif msg_type == "error":
            self.status_label.config(foreground="red")
        else:
            self.status_label.config(foreground="black")
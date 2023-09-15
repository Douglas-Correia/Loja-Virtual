import tkinter as tk
from tkinter import ttk, messagebox, Tk
import sqlite3
from datetime import datetime
import re

class CondominioApp:
    def __init__(self, root, funcionario_nome, funcionario_cargo):
        self.root = root
        self.funcionario_nome = funcionario_nome  # Armazena o nome do funcionário logado
        self.cargo_funcionario = funcionario_cargo
        
        self.root.title("Sistema de Controle de Chaves e Itens")
        
        self.conn = sqlite3.connect('condominio.db')
        self.create_tables()
        
        # Guia para cadastro de moradores
        self.tab_control = ttk.Notebook(root)
        self.tab_moradores = self.create_moradores_tab()
        self.tab_control.add(self.tab_moradores, text="Moradores")
        
        # Guia para cadastro de chaves e Itens
        self.tab_chaves_itens = self.create_chaves_itens_tab()
        self.tab_control.add(self.tab_chaves_itens, text="Chaves e Itens")
        
        # Guia para rastreamento de empréstimos
        self.tab_emprestimos = self.create_emprestimos_tab()
        self.tab_control.add(self.tab_emprestimos, text="Empréstimos")
        
        # Guia para controle de lavanderia
        self.tab_lavanderia = self.create_lavanderia_tab()
        self.tab_control.add(self.tab_lavanderia, text="Controle de Lavanderia")

        if self.cargo_funcionario != "Porteiro":
            # Guia para cadastro de funcionários
            self.tab_funcionarios = self.create_funcionarios_tab()
            self.tab_control.add(self.tab_funcionarios, text="Funcionários")
        else:
            pass
        
        self.tab_control.pack()
    
    def start(self):
        self.root.mainloop()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS moradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                apartamento INTEGER)
        ''')
        
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS chave_acesso(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_chave TEXT)''')
        
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                morador TEXT,
                item TEXT,
                data_hora_pego TEXT,
                data_hora_devolvido TEXT,
                acao TEXT,
                funcionario TEXT)
''')
        
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS registros_lavanderia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                morador TEXT NOT NULL,
                maquina INTEGER NOT NULL,
                inicio DATETIME NOT NULL,
                termino DATETIME,
                horas_uso REAL,
                FOREIGN KEY (morador) REFERENCES moradores(nome),
                FOREIGN KEY (maquina) REFERENCES maquinas(numero_maquina)
)''')
        
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS maquinas (
                numero_maquina INTEGER PRIMARY KEY,
                nome_maquina TEXT NOT NULL,
                disponivel BOOLEAN NOT NULL
)''')
        self.conn.commit()
        # Insira as quatro máquinas se elas não existirem
        for numero_maquina in range(1, 5):
            cursor.execute("INSERT OR IGNORE INTO maquinas (numero_maquina, nome_maquina, disponivel) VALUES (?,?,?)", (numero_maquina, f"Maquina {numero_maquina}", 1))
            self.conn.commit()

    def create_moradores_tab(self):
        tab = ttk.Frame(self.root)
        tab.grid_columnconfigure(0, weight=1)

        # Crie um estilo personalizado para os Entry e os Buttons
        estilo = ttk.Style()
        estilo.configure('Estilo.TEntry', padding=(5, 5, 5, 5), relief="solid")
        estilo.map('Estilo.TEntry',
                fieldbackground=[('active', 'blue'), ('!active', 'white')],
                foreground=[('focus', 'black'), ('!focus', 'black')])

        estilo.configure('Estilo.TButton', padding=(10, 5, 10, 5), relief="raised")
        estilo.map('Estilo.TButton',
                background=[('active', 'blue'), ('!active', 'gray')],
                foreground=[('focus', 'white'), ('!focus', 'black')])

        # Frame para campos e botões
        input_frame = ttk.Frame(tab)
        input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        morador_label = ttk.Label(input_frame, text="Nome do Morador:", font=('Arial', 14))
        morador_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.morador_entry = ttk.Entry(input_frame, style='Estilo.TEntry')
        self.morador_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew", columnspan=2)

        ap_morador_label = ttk.Label(input_frame, text="Apartamento:", font=('Arial', 14))
        ap_morador_label.grid(row=1, column=0, padx=10, pady=10)

        self.ap_morador_entry = ttk.Entry(input_frame, style='Estilo.TEntry')
        self.ap_morador_entry.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew", columnspan=2)

        adicionar_morador_button = ttk.Button(input_frame, text="Adicionar Morador", command=self.adicionar_morador, style='Estilo.TButton')
        adicionar_morador_button.grid(row=0, column=3, padx=(10, 5), pady=10, sticky="w")

        excluir_morador_button = ttk.Button(input_frame, text="Excluir Morador", command=self.excluir_morador, style='Estilo.TButton')
        excluir_morador_button.grid(row=1, column=3, padx=(5, 10), pady=10, sticky="w")

        # Frame para a Treeview
        treeview_frame = ttk.Frame(tab)
        treeview_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        treeview_frame.grid_rowconfigure(0, weight=1)
        treeview_frame.grid_columnconfigure(0, weight=1)

        self.moradores_tree = ttk.Treeview(treeview_frame, columns=("Apartamento", "Nome"))
        self.moradores_tree.heading("#1", text="Apartamento")
        self.moradores_tree.heading("#2", text="Nome")
        self.moradores_tree.column("#0", width=0, stretch=tk.NO)
        self.moradores_tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tab.grid_rowconfigure(1, weight=1)
        tab.pack(fill="both", expand=True)

        self.atualizar_lista_moradores()

        return tab
    
    def adicionar_morador(self):
        nome = self.morador_entry.get()
        apartamento = self.ap_morador_entry.get()  # Obtém o número do apartamento
        if nome and apartamento:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO moradores (nome, apartamento) VALUES (?, ?)", (nome, apartamento))  # Insere o nome e o número do apartamento
            self.conn.commit()
            self.morador_entry.delete(0, tk.END)
            self.ap_morador_entry.delete(0, tk.END)  # Limpa o campo do número do apartamento
            
            self.preencher_dropdown_moradores()
            self.load_moradores()
            self.atualizar_lista_moradores()
            
    def excluir_morador(self):
        # Obtém o morador selecionado
        morador_selecionado = self.moradores_tree.selection()
        
        if morador_selecionado:
            id_morador = morador_selecionado[0] # Obtém o id do morador
            
            nome_morador = self.moradores_tree.item(id_morador, "values")[1] # Pegando o nome do morador através do id
            
            # Excluir o morador 
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM moradores WHERE nome = ?", (nome_morador,))
            self.conn.commit()
            
            self.moradores_tree.delete(id_morador)
        else:
            messagebox.showerror("Erro", "Selecione um morador para excluir.")

    def atualizar_lista_moradores(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT apartamento, nome FROM moradores")  # Seleciona o número do apartamento e o nome
        moradores = cursor.fetchall()

        for record in self.moradores_tree.get_children():
            self.moradores_tree.delete(record)

        for morador in moradores:
            self.moradores_tree.insert("", "end", values=morador)


    def create_chaves_itens_tab(self):
        tab = ttk.Frame(self.root)

        # Criar um estilo personalizado para campos e botões
        estilo = ttk.Style()
        estilo.configure('Estilo.TEntry', padding=(5, 5, 5, 5), relief="solid")
        estilo.configure('Estilo.TButton', padding=(10, 5, 10, 5), relief="raised")

        # Frame para campos e botões
        input_frame = ttk.Frame(tab)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        nome_chave_label = ttk.Label(input_frame, text="Nome da chave ou Item:", font=('Arial', 14))
        nome_chave_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.nome_chave_entry = ttk.Entry(input_frame, style='Estilo.TEntry')
        self.nome_chave_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")  # Alterações feitas aqui

        adicionar_chave = ttk.Button(input_frame, text="Adicionar", command=self.adicionar_chave, style='Estilo.TButton')
        adicionar_chave.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="e")  # Alterações feitas aqui

        excluir_chave = ttk.Button(input_frame, text="Excluir", command=self.excluir_chave, style='Estilo.TButton')
        excluir_chave.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="w")  # Alterações feitas aqui

        # Frame para a Treeview
        treeview_frame = ttk.Frame(tab)
        treeview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")  # Alterações feitas aqui

        self.chaves_tree = ttk.Treeview(treeview_frame, columns=("Id", "Nome da chave"))
        self.chaves_tree.heading("#1", text="Id")
        self.chaves_tree.heading("#2", text="Nome da chave/Item")
        self.chaves_tree.column("#0", width=0, stretch=tk.NO)
        self.chaves_tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")  # Alterações feitas aqui

        # Configurar a expansão da Treeview
        treeview_frame.grid_rowconfigure(0, weight=1)
        treeview_frame.grid_columnconfigure(0, weight=1)

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        tab.pack(fill="both", expand=True)
        self.atualizar_lista_chaves()
        return tab

    def adicionar_chave(self):
        nome_chave = self.nome_chave_entry.get()
        
        if nome_chave:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO chave_acesso (nome_chave) VALUES (?)", (nome_chave,))
            self.conn.commit()
            self.nome_chave_entry.delete(0, tk.END)
            
            self.preencher_dropdown_itens()
            self.atualizar_lista_chaves()
            
    def excluir_chave(self):
        # Obtém o item selecionado na Treeview
        item_selecionado = self.chaves_tree.selection()
        
        # Verifica se um item está selecionado
        if item_selecionado:
            chave_id = item_selecionado[0]  # Pega o ID do item selecionado
            
            # Obtém o valor da chave (nome da chave) a partir do item selecionado
            chave_nome = self.chaves_tree.item(chave_id, "values")[1]  # Supondo que o nome da chave é a segunda coluna (índice 1)
            
            # Exclui a chave do banco de dados
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM chave_acesso WHERE nome_chave = ?", (chave_nome,))
            self.conn.commit()
            
            # Remove o item selecionado da Treeview
            self.chaves_tree.delete(chave_id)
        else:
            # Exibe uma mensagem de erro se nenhum item estiver selecionado
            messagebox.showerror("Erro", "Selecione uma chave para excluir.")

            
    def atualizar_lista_chaves(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chave_acesso")
        chaves = cursor.fetchall()
        
        for record in self.chaves_tree.get_children():
            self.chaves_tree.delete(record)
            
        for chave in chaves:
            self.chaves_tree.insert("", "end" ,values=chave)
    
    def create_emprestimos_tab(self):
        tab = ttk.Frame(self.root)

        # Frame para campos e botões
        input_frame = ttk.Frame(tab)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Dropdown para selecionar um morador
        morador_label = ttk.Label(input_frame, text="Selecione um Morador:", font=('Arial', 14))
        morador_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.morador_var = tk.StringVar()
        self.morador_dropdown = ttk.Combobox(input_frame, textvariable=self.morador_var)
        self.morador_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Dropdown para selecionar uma chave ou item
        item_label = ttk.Label(input_frame, text="Selecione uma Chave ou Item:", font=('Arial', 14))
        item_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.item_var = tk.StringVar()
        self.item_dropdown = ttk.Combobox(input_frame, textvariable=self.item_var)
        self.item_dropdown.grid(row=1, column=1, padx=10, pady=10)

        # Botões para registrar empréstimo e devolução
        emprestar_button = ttk.Button(input_frame, text="Emprestar", command=self.registrar_emprestimo, style='Estilo.TButton')
        emprestar_button.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="w")

        devolver_button = ttk.Button(input_frame, text="Devolver", command=self.registrar_devolucao, style='Estilo.TButton')
        devolver_button.grid(row=2, column=1, padx=(5, 10), pady=10, sticky="w")

        # Frame para a Treeview
        treeview_frame = ttk.Frame(tab)
        treeview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.emprestimos_tree = ttk.Treeview(treeview_frame, columns=("Morador", "Item", "Data e Hora", "Ação", "Data"))
        self.emprestimos_tree.heading("#1", text="Morador")
        self.emprestimos_tree.heading("#2", text="Item")
        self.emprestimos_tree.heading("#3", text="Data e Hora")
        self.emprestimos_tree.heading("#4", text="Ação")
        self.emprestimos_tree.heading("#5", text="Data")
        self.emprestimos_tree.column("#0", width=0, stretch=tk.NO)
        self.emprestimos_tree.column("#5", width=0, stretch=tk.NO)
        self.emprestimos_tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configurar a expansão da Treeview
        treeview_frame.grid_rowconfigure(0, weight=1)
        treeview_frame.grid_columnconfigure(0, weight=1)

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        tab.pack(fill="both", expand=True)

        self.preencher_dropdown_itens()
        self.preencher_dropdown_moradores()
        # Atualize a Treeview apenas com registros do dia atual
        self.atualizar_treeview_emprestimo()
        return tab

    def preencher_dropdown_moradores(self):
        # Consulta o banco de dados para obter os nomes dos moradores
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome FROM moradores")
        moradores = cursor.fetchall()

        # Preenche o dropdown de moradores
        self.morador_dropdown['values'] = [morador[0] for morador in moradores]

    def preencher_dropdown_itens(self):
        # Consulta o banco de dados para obter os nomes dos itens (chaves ou objetos)
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome_chave FROM chave_acesso")
        itens = cursor.fetchall()

        # Preenche o dropdown de itens
        self.item_dropdown['values'] = [item[0] for item in itens]

    def registrar_emprestimo(self):
        morador = self.morador_var.get()
        item = self.item_var.get()

        if morador and item:
            # Obtém a data e hora atual
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Registra o empréstimo na Treeview sem a data e hora
            self.emprestimos_tree.insert("", "end", values=(morador, item, data_hora_atual, "Pegou", self.funcionario_nome))

            # Registra o empréstimo no banco de dados com data, hora e nome do funcionário
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO emprestimos (morador, item, data_hora_pego, acao, funcionario) VALUES (?, ?, ?, ?, ?)", (morador, item, data_hora_atual, "Pegou", self.funcionario_nome))
            self.conn.commit()

            # Limpa os campos
            self.morador_var.set("")
            self.item_var.set("")

    def registrar_devolucao(self):
        # Obtém o item selecionado na Treeview
        item_selecionado = self.emprestimos_tree.selection()

        if item_selecionado:
            # Obtém a data e hora atual para armazenamento
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Obtém os valores do registro selecionado na Treeview
            valores_registro = self.emprestimos_tree.item(item_selecionado[0], "values")

            # Obtém informações do registro selecionado na Treeview
            morador = valores_registro[0]
            item = valores_registro[1]
            data_hora = valores_registro[2]

            try:
                cursor = self.conn.cursor()

                # Consulta o banco de dados para obter o ID correto com base nas informações da Treeview
                cursor.execute("SELECT id FROM emprestimos WHERE morador = ? AND item = ? AND data_hora_pego = ?",
                                (morador, item, data_hora))
                resultado = cursor.fetchone()

                if resultado:
                    registro_id = resultado[0]  # Obtém o ID correto do banco de dados

                    # Obtém a ação atual (Pegou ou Devolveu)
                    acao_atual = valores_registro[3]

                    # Verifica se a ação atual é "Pegou" para permitir a devolução
                    if acao_atual == "Pegou":
                        # Atualiza a ação para "Devolvido" na Treeview, mantendo os outros valores
                        valores_atualizados = (*valores_registro[:3], "Devolvido", self.funcionario_nome)
                        self.emprestimos_tree.item(item_selecionado[0], values=valores_atualizados)

                        # Atualiza a ação no banco de dados com o ID correto
                        cursor.execute("UPDATE emprestimos SET acao = ?, data_hora_devolvido = ?, funcionario = ? WHERE id = ?",("Devolvido", data_hora_atual, self.funcionario_nome, registro_id))
                        self.conn.commit()
                    else:
                        messagebox.showerror("Erro", "Selecione um empréstimo para devolver.")
                else:
                    messagebox.showerror("Erro", "Registro não encontrado no banco de dados.")
            except Exception as e:
                print("Erro ao atualizar ação:", str(e))
        else:
            messagebox.showerror("Erro", "Selecione um registro para devolver.")
        
    def atualizar_treeview_emprestimo(self):
        # Obtém a data atual no formato "YYYY-MM-DD"
        data_atual = datetime.now().strftime("%Y-%m-%d")
        
        # Limpa a Treeview
        for record in self.emprestimos_tree.get_children():
            self.emprestimos_tree.delete(record)
        
        # Consulta o banco de dados para obter os registros do dia atual
        cursor = self.conn.cursor()
        cursor.execute("SELECT morador, item, data_hora_pego, acao FROM emprestimos WHERE acao LIKE \"Pegou\"")
        registros = cursor.fetchall()
        
        # Preenche a Treeview com os registros do dia atual
        for registro in registros:
            self.emprestimos_tree.insert("", "end", values=registro)

        # Agende a próxima atualização periódica (a cada 1 minuto)
        self.root.after(60000, self.atualizar_treeview_emprestimo)
        
    # Criação da aba de controle de lavanderia
    def create_lavanderia_tab(self):
        tab_lavanderia = ttk.Frame(self.root)

        moradores_var = tk.StringVar()
        maquinas_disponiveis = self.load_maquinas_disponiveis()

        # Crie um ComboBox para selecionar o morador
        self.morador_label = ttk.Label(tab_lavanderia, text="Selecione o Morador:")
        self.morador_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.morador_combobox = ttk.Combobox(tab_lavanderia, textvariable=moradores_var)
        self.morador_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Crie um ComboBox para selecionar a máquina
        self.maquina_label = ttk.Label(tab_lavanderia, text="Selecione a Máquina:")
        self.maquina_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.maquina_combobox = ttk.Combobox(tab_lavanderia, values=maquinas_disponiveis)
        self.maquina_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.maquina_combobox.set(maquinas_disponiveis[0])

        # Crie botões de ação
        self.iniciar_uso_button = ttk.Button(tab_lavanderia, text="Iniciar Uso", command=self.iniciar_uso_lavanderia)
        self.iniciar_uso_button.grid(row=2, column=0, padx=10, pady=10)

        self.encerrar_uso_button = ttk.Button(tab_lavanderia, text="Encerrar Uso", command=self.encerrar_uso_lavanderia)
        self.encerrar_uso_button.grid(row=2, column=1, padx=10, pady=10)

        # Crie um Treeview para exibir registros
        self.registros_tree = ttk.Treeview(tab_lavanderia, columns=("Morador", "Máquinas", "Início", "Término", "Horas de Uso"))
        self.registros_tree.heading("#1", text="Morador")
        self.registros_tree.heading("#2", text="Máquinas")
        self.registros_tree.heading("#3", text="Início")
        self.registros_tree.heading("#4", text="Término")
        self.registros_tree.heading("#5", text="Horas de Uso")
        self.registros_tree.column("#0", width=0, stretch=tk.NO)
        self.registros_tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configure a expansão do Treeview e da aba
        tab_lavanderia.grid_rowconfigure(3, weight=1)
        tab_lavanderia.grid_columnconfigure(0, weight=1)
        
        self.load_moradores()
        self.atualizar_registros_lavanderia()
        return tab_lavanderia
    
    def iniciar_uso_lavanderia(self):
        # Obtenha o morador selecionado no ComboBox
        morador_selecionado = self.morador_combobox.get()

        # Obtenha a máquina selecionada no ComboBox
        maquina_selecionada = self.maquina_combobox.get()

        # Se nenhum morador ou máquina for selecionado, não faça nada
        if not morador_selecionado or not maquina_selecionada:
            return

        # Verifique se a máquina já está em uso (se já existe um registro "Em andamento" para essa máquina)
        conn = sqlite3.connect('condominio.db')
        cursor = conn.cursor()

        cursor.execute("SELECT maquina FROM registros_lavanderia WHERE maquina = ? AND termino IS NULL", (maquina_selecionada,))
        registro_em_andamento = cursor.fetchone()

        if registro_em_andamento:
            messagebox.showerror("Máquina Ocupada", "A máquina selecionada já está em uso.")
            return

        try:
            # Registre o início do uso no banco de dados
            hora_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Conecte-se ao banco de dados
            conn = sqlite3.connect('condominio.db')
            cursor = conn.cursor()

            # Insira um novo registro na tabela 'registros_lavanderia'
            cursor.execute("INSERT INTO registros_lavanderia (morador, maquina, inicio) VALUES (?, ?, ?)",
                        (morador_selecionado, maquina_selecionada, hora_inicio))

            # Faça o commit para salvar as alterações
            conn.commit()

            # Formate o tempo para exibi-lo corretamente na Treeview
            tempo_formatado = self.formatar_tempo(0)  # Início tem 0 minutos de uso

            # Após inserir os dados, atualize a Treeview com os novos registros
            self.atualizar_registros_lavanderia()

        except sqlite3.Error as e:
            print(f"Erro ao inserir dados no banco de dados: {e}")

    def calcular_horas_uso(self, inicio_str, termino_str):
        if inicio_str is None:
            # Uso ainda em andamento, não calcule as horas de uso
            return "Em andamento"

        try:
            inicio = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
            termino = datetime.strptime(termino_str, "%Y-%m-%d %H:%M:%S")
            horas_uso = (termino - inicio).total_seconds() / 3600.0
            return f"{horas_uso:.2f} horas"
        except ValueError:
            return "Erro no formato da data/hora"

    def formatar_tempo(self, tempo_minutos):
        if tempo_minutos < 60:
            return f"{tempo_minutos} M"
        else:
            horas = tempo_minutos // 60
            minutos = tempo_minutos % 60
            return f"{horas} H {minutos} M"

    def encerrar_uso_lavanderia(self):
        maquina_selecionada = self.maquina_combobox.get()  # Obtenha a máquina selecionada no ComboBox
        item_selecionado = self.registros_tree.selection()

        if not maquina_selecionada or not item_selecionado:
            return

        # Conecte-se ao banco de dados
        conn = sqlite3.connect('condominio.db')
        cursor = conn.cursor()

        for item in item_selecionado:
            # Obtenha o valor da coluna "Início" para o item selecionado
            inicio_str = self.registros_tree.item(item, "values")[2]

            # Verifique se o uso está em andamento (valor 'Em andamento')
            if inicio_str == 'Em andamento':
                continue  # Não faz nada para usos em andamento

            try:
                # Obtenha o nome do morador da linha selecionada
                morador_selecionado = self.registros_tree.item(item, "values")[0]
                
                # Obtenha a máquina da linha selecionada
                maquina_atual = self.registros_tree.item(item, "values")[1]

                # Converta a data/hora de início em datetime
                inicio = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
                termino = datetime.now()
                minutos_uso = int((termino - inicio).total_seconds() / 60)  # Duração em minutos

                # Formate o tempo de uso
                tempo_formatado = self.formatar_tempo(minutos_uso)

                # Atualize a coluna "Término" e "Horas de Uso" na Treeview
                self.registros_tree.item(item, values=(morador_selecionado, maquina_atual, inicio_str, termino.strftime("%Y-%m-%d %H:%M:%S"), tempo_formatado))

                # Atualize o registro no banco de dados
                cursor.execute("UPDATE registros_lavanderia SET termino = ?, horas_uso = ? WHERE morador = ? AND inicio = ?",
                            (termino.strftime("%Y-%m-%d %H:%M:%S"), minutos_uso, morador_selecionado, inicio_str))
                conn.commit()

            except ValueError:
                print("Erro no formato da data/hora")

    def load_moradores(self):
        # Conecte-se ao banco de dados 
        conn = sqlite3.connect('condominio.db')
        cursor = conn.cursor()

        # Consulte o banco de dados para obter a lista de moradores
        cursor.execute("SELECT nome FROM moradores")
        moradores = cursor.fetchall()
        self.morador_combobox['values'] = [morador[0] for morador in moradores]

    def load_maquinas_disponiveis(self):
        # Conecte-se ao banco de dados 
        conn = sqlite3.connect('condominio.db')
        cursor = conn.cursor()

        # Consulte o banco de dados para obter a lista de máquinas disponíveis
        cursor.execute("SELECT numero_maquina FROM maquinas WHERE disponivel = 1")
        maquinas_disponiveis = [row[0] for row in cursor.fetchall()]

        # Feche a conexão com o banco de dados
        conn.close()

        return maquinas_disponiveis

    def atualizar_registros_lavanderia(self):
        # Conecte-se ao banco de dados 
        conn = sqlite3.connect('condominio.db')
        cursor = conn.cursor()

        # Obtenha a data atual no formato 'YYYY-MM-DD'
        data_atual = datetime.now().strftime('%Y-%m-%d')

        # Consulte o banco de dados para obter os registros do dia atual, incluindo aqueles com valor NULL ou "Em andamento"
        cursor.execute("SELECT morador, maquina, inicio, termino, horas_uso FROM registros_lavanderia WHERE strftime('%Y-%m-%d', inicio) = ? OR termino IS NULL", (data_atual,))
        registros_do_banco = cursor.fetchall()

        # Limpe o Treeview
        for item in self.registros_tree.get_children():
            self.registros_tree.delete(item)

        # Preencha o Treeview com os registros do banco de dados e formate as datas e horas
        for registro in registros_do_banco:
            morador, maquina, inicio, termino, horas_uso = registro

            # Verifique se a data de início é None ou se já está no formato correto
            if inicio:
                if not isinstance(inicio, datetime):
                    inicio = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
                inicio_formatado = inicio.strftime("%Y-%m-%d %H:%M:%S")
            else:
                inicio_formatado = "Em andamento"
            
            if termino:
                if not isinstance(termino, datetime):
                    termino = datetime.strptime(termino, "%Y-%m-%d %H:%M:%S")
                termino_formatado = termino.strftime("%Y-%m-%d %H:%M:%S")
                horas_uso_formatadas = self.formatar_tempo(int(horas_uso))
            else:
                termino_formatado = "Em andamento"
                horas_uso_formatadas = "Em andamento"

            self.registros_tree.insert("", "end", values=(morador, maquina, inicio_formatado, termino_formatado, horas_uso_formatadas))
    
    def create_funcionarios_tab(self):
        tab = ttk.Frame(self.root)

        # Criar um estilo personalizado para campos e botões
        estilo = ttk.Style()
        estilo.configure('Estilo.TEntry', padding=(5, 5, 5, 5), relief="solid")
        estilo.configure('Estilo.TButton', padding=(10, 5, 10, 5), relief="raised")

        # Frame para campos e botões
        input_frame = ttk.Frame(tab)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Campos para cadastro de funcionário
        nome_label = ttk.Label(input_frame, text="Nome do Funcionário:")
        nome_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.nome_funcionario_entry = ttk.Entry(input_frame, style='Estilo.TEntry')
        self.nome_funcionario_entry.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        cargo_label = ttk.Label(input_frame, text="Cargo:")
        cargo_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.cargo_funcionario_entry = ttk.Entry(input_frame, style='Estilo.TEntry')
        self.cargo_funcionario_entry.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        login_label = ttk.Label(input_frame, text="Login:")
        login_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.login_funcionario_entry = ttk.Entry(input_frame, style='Estilo.TEntry')
        self.login_funcionario_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        senha_label = ttk.Label(input_frame, text="Senha:")
        senha_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        self.senha_funcionario_entry = ttk.Entry(input_frame, style='Estilo.TEntry', show="*")
        self.senha_funcionario_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Botão para cadastrar funcionário
        cadastrar_funcionario_button = ttk.Button(input_frame, text="Cadastrar Funcionário", command=self.cadastrar_funcionario, style='Estilo.TButton')
        cadastrar_funcionario_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Frame para a Treeview
        treeview_frame = ttk.Frame(tab)
        treeview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Tabela para mostrar a lista de funcionários
        self.funcionarios_tree = ttk.Treeview(treeview_frame, columns=("ID", "Nome", "Cargo"))
        self.funcionarios_tree.heading("#1", text="ID")
        self.funcionarios_tree.heading("#2", text="Nome")
        self.funcionarios_tree.heading("#3", text="Cargo")
        self.funcionarios_tree.column("#0", width=0, stretch=tk.NO)
        self.funcionarios_tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configurar a expansão da Treeview
        treeview_frame.grid_rowconfigure(0, weight=1)
        treeview_frame.grid_columnconfigure(0, weight=1)

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        tab.pack(fill="both", expand=True)

        # Preencha a Treeview com a lista de funcionários
        self.atualizar_lista_funcionarios()

        return tab

    def cadastrar_funcionario(self):
        nome = self.nome_funcionario_entry.get()
        cargo = self.cargo_funcionario_entry.get()
        login = self.login_funcionario_entry.get()
        senha = self.senha_funcionario_entry.get()

        if nome and cargo and login and senha:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO funcionarios (nome, cargo, login, senha) VALUES (?, ?, ?, ?)", (nome, cargo, login, senha))
            self.conn.commit()
            self.nome_funcionario_entry.delete(0, tk.END)
            self.cargo_funcionario_entry.delete(0, tk.END)
            self.login_funcionario_entry.delete(0, tk.END)
            self.senha_funcionario_entry.delete(0, tk.END)
            self.atualizar_lista_funcionarios()

    def atualizar_lista_funcionarios(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, cargo FROM funcionarios")
        funcionarios = cursor.fetchall()

        for record in self.funcionarios_tree.get_children():
            self.funcionarios_tree.delete(record)

        for funcionario in funcionarios:
            self.funcionarios_tree.insert("", "end", values=funcionario)

def main():
    root = Tk()
    app = CondominioApp(root)
    app.start()

if __name__ == "__main__":
    main()
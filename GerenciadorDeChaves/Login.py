from tkinter import Tk, PhotoImage, messagebox, Label
import customtkinter as ctk
import sqlite3
from Gerenciador import CondominioApp

class Login:
    def __init__(self, root):
        self.root = root  # Armazena a instância root
        self.janela = Tk()
        self.Conectar_Banco()
        self.Tema()
        self.Tela()
        self.Tela_Login()
        self.Campo_Entrys()
        # Bind the <Return> event to the entry fields and button
        self.entry_username.bind("<Return>", self.enter)
        self.entry_password.bind("<Return>", self.enter)
        self.janela.mainloop()

    def Conectar_Banco(self):
        self.conn = sqlite3.connect("condominio.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS funcionarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                cargo TEXT,
                login TEXT UNIQUE,
                senha TEXT)
        ''')

        # Verificando se o usuário admin123 já existe
        select_query = "SELECT * FROM funcionarios WHERE login = ? AND senha = ?"
        self.cursor.execute(select_query, ("admin123", "admin123"))
        result = self.cursor.fetchone()

        if result is None:
            # Inserindo novo registro com usuário e senha admin123
            insert_query = "INSERT INTO funcionarios (nome, cargo, login, senha) VALUES (?, ?, ?, ?)"
            self.cursor.execute(insert_query, ("Adiministrador", "Adiministrador","admin123", "admin123"))
            self.conn.commit()

    # DEFININDO O TEMA
    def Tema(self):
        self.janela.configure(bg="#252525")

    # CONFIGURANDO A JANELA
    def Tela(self):
        self.janela.geometry("700x400+500+200")
        self.janela.title("Area de login")
        #self.janela.iconbitmap("img/icons/Logo-caixa.ico")
        self.janela.resizable(False, False)

    # CAMPO DE LOGIN
    def Tela_Login(self):
        #self.img = PhotoImage(file="img/icons/Logo-login.png")
        #self.label_img = Label(master=self.janela, image=self.img, background="#252525")
        #self.label_img.place(x=5, y=50)

        # FRAME DA JANELA DE LOGIN
        self.frame_login = ctk.CTkFrame(master=self.janela, width=360, height=400, fg_color="#252525", corner_radius=0)
        self.frame_login.pack(side="right")

        # CAMPO DE LABELS
        self.label_ = ctk.CTkLabel(master=self.janela, text="SISTEMA DE CONTROLE DE CONDOMINIO",
                                   font=ctk.CTkFont(family="Roboto", size=22), text_color="white", bg_color="#252525",
                                   corner_radius=None)
        self.label_.place(x=70, y=5)

    def Campo_Entrys(self):
        # CAMPO DE ENTRY PARA RECEBER VARIÁVEIS DE LOGIN E SENHA
        self.entry_username = ctk.CTkEntry(master=self.frame_login, placeholder_text="Entre com Usuario", width=300,
                                           height=45, font=ctk.CTkFont(family="Roboto", size=14), text_color="black",
                                           bg_color="#252525", corner_radius=None)
        self.entry_username.place(x=30, y=60)

        self.lb_alert_obg = ctk.CTkLabel(master=self.frame_login, text="*O campo de usuario é de carater obrigatório",
                                         text_color="green", bg_color="#252525", corner_radius=None)
        self.lb_alert_obg.place(x=30, y=109)

        self.entry_password = ctk.CTkEntry(master=self.frame_login, placeholder_text="Entre com a Senha", width=300,
                                           height=45, font=ctk.CTkFont(family="Roboto", size=14), show="*",
                                           text_color="black", bg_color="#252525", corner_radius=None)
        self.entry_password.place(x=30, y=150)
        self.lb_alert_obg = ctk.CTkLabel(master=self.frame_login, text="*O campo de senha é de carater obrigatório",
                                         text_color="green", bg_color="#252525", corner_radius=None)
        self.lb_alert_obg.place(x=30, y=200)

        # CAMPO DE CHECKBOX
        self.check_box = ctk.CTkCheckBox(master=self.frame_login, text="Lembrar senha", hover_color="blue",
                                         text_color="white", bg_color="#252525", corner_radius=None)
        self.check_box.place(x=30, y=240)

        # CAMPO DE BOTÕES
        self.button = ctk.CTkButton(master=self.frame_login, text="Entrar", command=self.Verificar_Login, width=300,
                                    height=45, hover_color="blue", font=ctk.CTkFont(family="Roboto", size=20),
                                    text_color="white", bg_color="#252525", corner_radius=None)
        self.button.place(x=30, y=280)

    def Receber_Variaveis_Login(self):
        self.username = str(self.entry_username.get())
        self.userpassword = str(self.entry_password.get())

    def enter(self, event=None):
        self.Verificar_Login()

    def Verificar_Login(self):
        self.Receber_Variaveis_Login()
        veri_login = "SELECT * FROM funcionarios WHERE login like '" + self.username + "'AND senha like '" + self.userpassword + "'"
        self.cursor.execute(veri_login)
        validado = self.cursor.fetchall()
        if len(validado) > 0:
            messagebox.showinfo(title="Login bem-sucedido", message="Login realizado com sucesso!")
            self.root.deiconify()  # Exibe a janela principal novamente
            self.janela.destroy()  # Destrua a janela de login
            # Execute a consulta SQL para obter o nome do funcionário logado
            self.cursor.execute("SELECT nome, cargo FROM funcionarios WHERE login = ?", (self.username,))
            resultado = self.cursor.fetchone()
            if resultado:
                funcionario_nome = resultado[0]  # Obtém o nome do funcionário a partir do resultado
                funcionario_cargo = resultado[1] # Obtém o cargo do funcionário para verificar se for administrador, irá conter o campo de cadastro
            else:
                funcionario_nome = "adiministrador"  # Substitua pelo nome padrão desejado

            condominioApp = CondominioApp(root=self.root, funcionario_nome=funcionario_nome, funcionario_cargo=funcionario_cargo)  # Abre a tela do gerenciador
        elif validado == "":
            messagebox.showinfo(title="Erro", message="Preencha todos os campos!!")
            self.Verificar_Login()
        else:
            messagebox.showerror(title="Erro de Login", message="Verifique usuário e senha!!")

def main():
    root = Tk()  # Crie a instância root antes de criar a instância Login
    root.withdraw()  # Oculta a janela principal temporariamente
    app = Login(root)

if __name__ == "__main__":
    main()

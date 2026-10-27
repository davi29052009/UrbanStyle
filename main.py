
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import sqlite3

BASE = Path(__file__).resolve().parent
BANCO = BASE / "urbanstyle.db"

PRETO = "#111111"
BRANCO = "#FFFFFF"
FUNDO = "#F5F5F5"
CINZA = "#737373"
BORDA = "#E5E5E5"
VERMELHO = "#C0392B"


def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class UrbanStyle:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("URBANSTYLE | Streetwear Store")
        self.janela.geometry("1200x760")
        self.janela.minsize(950, 620)
        self.janela.configure(bg=FUNDO)

        self.db = sqlite3.connect(BANCO)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                categoria TEXT NOT NULL,
                imagem TEXT
            )
        """)
        self.db.commit()

        self.carrinho = {}
        self.cupom = None
        self.fotos = []
        self.tela_atual = ""

        self.configurar_estilo()
        self.criar_layout()
        self.inicio()

        self.janela.protocol("WM_DELETE_WINDOW", self.fechar)

    def configurar_estilo(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Urban.Treeview",
            font=("Arial", 11),
            rowheight=42,
            background=BRANCO,
            fieldbackground=BRANCO,
            foreground=PRETO,
            borderwidth=0
        )
        estilo.configure(
            "Urban.Treeview.Heading",
            font=("Arial", 11, "bold"),
            background="#EEEEEE",
            foreground=PRETO,
            padding=10
        )
        estilo.map(
            "Urban.Treeview",
            background=[("selected", "#DDDDDD")],
            foreground=[("selected", PRETO)]
        )

    def criar_layout(self):
        self.sidebar = tk.Frame(
            self.janela, bg=PRETO, width=225
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="URBANSTYLE.",
            font=("Arial", 22, "bold"),
            fg=BRANCO, bg=PRETO
        ).pack(anchor="w", padx=24, pady=(35, 4))

        tk.Label(
            self.sidebar,
            text="STREETWEAR STORE",
            font=("Arial", 9, "bold"),
            fg="#999999", bg=PRETO
        ).pack(anchor="w", padx=25, pady=(0, 50))

        self.menu_botoes = {}

        opcoes = [
            ("Início", self.inicio),
            ("Catálogo", self.catalogo),
            ("Carrinho", self.mostrar_carrinho),
            ("Administração", self.administracao)
        ]

        for nome, comando in opcoes:
            botao = tk.Button(
                self.sidebar,
                text="   " + nome,
                command=comando,
                font=("Arial", 12),
                fg="#BBBBBB",
                bg=PRETO,
                activebackground="#292929",
                activeforeground=BRANCO,
                anchor="w",
                relief="flat",
                bd=0,
                padx=20,
                pady=16,
                cursor="hand2"
            )
            botao.pack(fill="x", padx=10, pady=3)
            self.menu_botoes[nome] = botao

        tk.Label(
            self.sidebar,
            text="URBANSTYLE © 2026",
            bg=PRETO, fg="#777777",
            font=("Arial", 9)
        ).pack(side="bottom", pady=25)

        self.conteudo = tk.Frame(self.janela, bg=FUNDO)
        self.conteudo.pack(
            side="right", fill="both", expand=True
        )

    def ativar_menu(self, nome):
        for titulo, botao in self.menu_botoes.items():
            ativo = titulo == nome
            botao.configure(
                bg="#303030" if ativo else PRETO,
                fg=BRANCO if ativo else "#BBBBBB"
            )

    def limpar(self, nome):
        for widget in self.conteudo.winfo_children():
            widget.destroy()
        self.fotos.clear()
        self.tela_atual = nome
        self.ativar_menu(nome)

    def botao(self, pai, texto, comando, escuro=True):
        return tk.Button(
            pai, text=texto, command=comando,
            bg=PRETO if escuro else BRANCO,
            fg=BRANCO if escuro else PRETO,
            activebackground="#383838" if escuro else "#EEEEEE",
            activeforeground=BRANCO if escuro else PRETO,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=18, pady=11,
            cursor="hand2"
        )

    def cabecalho(self, titulo, descricao):
        topo = tk.Frame(self.conteudo, bg=FUNDO)
        topo.pack(fill="x", padx=35, pady=(30, 15))

        tk.Label(
            topo, text=titulo,
            bg=FUNDO, fg=PRETO,
            font=("Arial", 26, "bold")
        ).pack(anchor="w")

        tk.Label(
            topo, text=descricao,
            bg=FUNDO, fg=CINZA,
            font=("Arial", 11)
        ).pack(anchor="w", pady=5)

    def produtos(self, busca="", categoria="Todos"):
        sql = """
            SELECT id, nome, preco, categoria, imagem
            FROM produtos WHERE 1=1
        """
        parametros = []

        if busca:
            sql += " AND nome LIKE ?"
            parametros.append(f"%{busca}%")

        if categoria != "Todos":
            sql += " AND categoria = ?"
            parametros.append(categoria)

        sql += " ORDER BY id"
        return self.db.execute(sql, parametros).fetchall()

    def carregar_foto(self, pai, caminho):
        quadro = tk.Frame(
            pai, bg="#F0F0F0",
            width=185, height=150
        )
        quadro.pack(padx=12, pady=(12, 8))
        quadro.pack_propagate(False)

        if caminho:
            try:
                arquivo = Path(caminho)
                if not arquivo.is_absolute():
                    arquivo = BASE / arquivo

                imagem = tk.PhotoImage(file=str(arquivo))
                fator = max(
                    1,
                    (max(imagem.width(), imagem.height()) + 149) // 150
                )
                imagem = imagem.subsample(fator, fator)
                self.fotos.append(imagem)

                tk.Label(
                    quadro, image=imagem,
                    bg="#F0F0F0"
                ).pack(expand=True)
                return
            except (tk.TclError, OSError):
                pass

        tk.Label(
            quadro,
            text="URBANSTYLE",
            font=("Arial", 11, "bold"),
            fg=CINZA, bg="#F0F0F0"
        ).pack(expand=True)

    def card(self, pai, produto):
        codigo, nome, preco, categoria, imagem = produto

        card = tk.Frame(
            pai, bg=BRANCO,
            width=210, height=280,
            highlightbackground=BORDA,
            highlightthickness=1
        )
        card.pack(side="left", padx=(0, 15), pady=10)
        card.pack_propagate(False)

        self.carregar_foto(card, imagem)

        tk.Label(
            card, text=categoria.upper(),
            bg=BRANCO, fg=CINZA,
            font=("Arial", 8, "bold")
        ).pack()

        tk.Label(
            card, text=nome,
            bg=BRANCO, fg=PRETO,
            font=("Arial", 11, "bold"),
            wraplength=190
        ).pack(pady=(4, 2))

        tk.Label(
            card, text=moeda(preco),
            bg=BRANCO, fg=PRETO,
            font=("Arial", 12)
        ).pack()

        self.botao(
            card, "ADICIONAR +",
            lambda p=produto: self.adicionar(p)
        ).pack(pady=8)

    def criar_rolagem(self, pai):
        canvas = tk.Canvas(
            pai, bg=FUNDO, highlightthickness=0
        )
        barra = ttk.Scrollbar(
            pai, orient="vertical", command=canvas.yview
        )
        interior = tk.Frame(canvas, bg=FUNDO)

        janela_canvas = canvas.create_window(
            (0, 0), window=interior, anchor="nw"
        )

        def atualizar_area(evento=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def ajustar_largura(evento):
            canvas.itemconfigure(
                janela_canvas, width=evento.width
            )

        interior.bind("<Configure>", atualizar_area)
        canvas.bind("<Configure>", ajustar_largura)
        canvas.configure(yscrollcommand=barra.set)

        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def rolar(evento):
            canvas.yview_scroll(
                int(-evento.delta / 120), "units"
            )

        canvas.bind("<MouseWheel>", rolar)
        interior.bind("<MouseWheel>", rolar)

        return interior

    # INÍCIO
    def inicio(self):
        self.limpar("Início")

        self.cabecalho(
            "Bem-vindo à UrbanStyle",
            "Moda urbana para todos os estilos."
        )

        banner = tk.Frame(
            self.conteudo, bg="#202020", height=220
        )
        banner.pack(fill="x", padx=35, pady=10)
        banner.pack_propagate(False)

        tk.Label(
            banner, text="NEW COLLECTION / 2026",
            bg="#202020", fg="#AAAAAA",
            font=("Arial", 10, "bold")
        ).pack(pady=(25, 8))

        tk.Label(
            banner, text="SEU ESTILO.\nSUAS REGRAS.",
            bg="#202020", fg=BRANCO,
            font=("Arial", 29, "bold"),
            justify="center"
        ).pack()

        self.botao(
            banner, "EXPLORAR COLEÇÃO",
            self.catalogo, escuro=False
        ).pack(pady=12)

        tk.Label(
            self.conteudo,
            text="DESTAQUES DA SEMANA",
            bg=FUNDO, fg=PRETO,
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=35, pady=(22, 5))

        area = tk.Frame(self.conteudo, bg=FUNDO)
        area.pack(fill="x", padx=35)

        for produto in self.produtos()[:3]:
            self.card(area, produto)

    # CATÁLOGO
    def catalogo(self):
        self.limpar("Catálogo")

        self.cabecalho(
            "Explore nossa coleção",
            "Encontre peças que combinam com você."
        )

        filtros = tk.Frame(self.conteudo, bg=FUNDO)
        filtros.pack(fill="x", padx=35, pady=(5, 15))

        busca = tk.Entry(
            filtros, font=("Arial", 12),
            relief="flat", bg=BRANCO,
            width=25
        )
        busca.pack(side="left", ipady=11, padx=(0, 12))

        categoria = ttk.Combobox(
            filtros,
            values=[
                "Todos", "Roupas",
                "Calçados", "Acessórios"
            ],
            state="readonly",
            width=15
        )
        categoria.set("Todos")
        categoria.pack(side="left", padx=5)

        area = tk.Frame(self.conteudo, bg=FUNDO)
        area.pack(
            fill="both", expand=True,
            padx=35, pady=(0, 20)
        )

        interior = self.criar_rolagem(area)

        def atualizar():
            for widget in interior.winfo_children():
                widget.destroy()
            self.fotos.clear()

            lista = self.produtos(
                busca.get().strip(), categoria.get()
            )

            if not lista:
                tk.Label(
                    interior,
                    text="Nenhum produto encontrado.",
                    bg=FUNDO, fg=CINZA,
                    font=("Arial", 13)
                ).pack(pady=30)
                return

            for inicio in range(0, len(lista), 3):
                linha = tk.Frame(interior, bg=FUNDO)
                linha.pack(anchor="w")

                for produto in lista[inicio:inicio + 3]:
                    self.card(linha, produto)

        self.botao(
            filtros, "BUSCAR", atualizar
        ).pack(side="left", padx=10)

        busca.bind("<Return>", lambda e: atualizar())
        categoria.bind(
            "<<ComboboxSelected>>",
            lambda e: atualizar()
        )

        atualizar()

    # CARRINHO
    def adicionar(self, produto):
        codigo, nome, preco, categoria, imagem = produto
        self.carrinho[codigo] = (
            self.carrinho.get(codigo, 0) + 1
        )
        messagebox.showinfo(
            "UrbanStyle",
            f"{nome} adicionado ao carrinho!"
        )

    def total(self):
        total = 0

        for codigo, quantidade in self.carrinho.items():
            registro = self.db.execute(
                "SELECT preco FROM produtos WHERE id=?",
                (codigo,)
            ).fetchone()

            if registro:
                total += registro[0] * quantidade

        if self.cupom == "URBAN10":
            total *= 0.90

        return total

    def mostrar_carrinho(self):
        self.limpar("Carrinho")
        self.cabecalho(
            "Seu carrinho",
            f"{sum(self.carrinho.values())} itens selecionados"
        )

        colunas = ("nome", "preco", "qtd", "subtotal")
        tabela = ttk.Treeview(
            self.conteudo,
            columns=colunas,
            show="headings",
            style="Urban.Treeview",
            height=9
        )

        for coluna, titulo in zip(
            colunas,
            ["Produto", "Preço", "Qtd.", "Subtotal"]
        ):
            tabela.heading(coluna, text=titulo)

        tabela.column("nome", width=250)
        tabela.column("preco", width=120, anchor="center")
        tabela.column("qtd", width=80, anchor="center")
        tabela.column("subtotal", width=120, anchor="center")
        tabela.pack(fill="x", padx=35, pady=15)

        total_texto = tk.Label(
            self.conteudo,
            text="",
            bg=FUNDO, fg=PRETO,
            font=("Arial", 23, "bold")
        )
        total_texto.pack(anchor="e", padx=35, pady=15)

        def atualizar():
            for item in tabela.get_children():
                tabela.delete(item)

            for codigo, qtd in self.carrinho.items():
                registro = self.db.execute(
                    "SELECT nome, preco FROM produtos WHERE id=?",
                    (codigo,)
                ).fetchone()

                if registro:
                    nome, preco = registro
                    tabela.insert(
                        "", "end",
                        iid=str(codigo),
                        values=(
                            nome, moeda(preco),
                            qtd, moeda(preco * qtd)
                        )
                    )

            total_texto.config(
                text="TOTAL: " + moeda(self.total())
            )

        def mudar_qtd(diferenca):
            selecionado = tabela.selection()
            if not selecionado:
                messagebox.showwarning(
                    "Atenção", "Selecione um produto."
                )
                return

            codigo = int(selecionado[0])
            quantidade = self.carrinho[codigo] + diferenca

            if quantidade <= 0:
                self.carrinho.pop(codigo)
            else:
                self.carrinho[codigo] = quantidade

            atualizar()

        controles = tk.Frame(self.conteudo, bg=FUNDO)
        controles.pack(anchor="w", padx=35)

        self.botao(
            controles, "+", lambda: mudar_qtd(1)
        ).pack(side="left", padx=3)

        self.botao(
            controles, "-", lambda: mudar_qtd(-1)
        ).pack(side="left", padx=3)

        cupom_area = tk.Frame(self.conteudo, bg=FUNDO)
        cupom_area.pack(fill="x", padx=35, pady=25)

        tk.Label(
            cupom_area, text="CUPOM DE DESCONTO",
            bg=FUNDO, fg=PRETO,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=5)

        entrada = tk.Entry(
            cupom_area, font=("Arial", 12),
            relief="flat", width=20
        )
        entrada.pack(side="left", ipady=10)

        def aplicar():
            codigo = entrada.get().strip().upper()

            if codigo == "URBAN10":
                self.cupom = codigo
                messagebox.showinfo(
                    "Cupom", "10% de desconto aplicado!"
                )
            else:
                self.cupom = None
                messagebox.showwarning(
                    "Cupom", "Cupom inválido."
                )

            atualizar()

        self.botao(
            cupom_area, "APLICAR", aplicar
        ).pack(side="left", padx=10)

        def finalizar():
            if not self.carrinho:
                messagebox.showwarning(
                    "Carrinho vazio",
                    "Adicione produtos primeiro."
                )
                return

            if messagebox.askyesno(
                "Confirmar pedido",
                f"Total: {moeda(self.total())}\n\n"
                "Confirmar compra de demonstração?"
            ):
                self.carrinho.clear()
                self.cupom = None
                messagebox.showinfo(
                    "UrbanStyle",
                    "Pedido de demonstração realizado!"
                )
                self.inicio()

        self.botao(
            self.conteudo,
            "FINALIZAR COMPRA",
            finalizar
        ).pack(anchor="e", padx=35, pady=5)

        atualizar()

    # ADMINISTRAÇÃO
    def administracao(self):
        self.limpar("Administração")
        self.cabecalho(
            "Gerenciar produtos",
            "Adicione novas peças ao catálogo."
        )

        form = tk.Frame(
            self.conteudo, bg=BRANCO,
            padx=25, pady=20
        )
        form.pack(fill="x", padx=35, pady=10)

        entradas = {}

        for campo in ["Nome", "Preço", "Categoria"]:
            tk.Label(
                form, text=campo.upper(),
                bg=BRANCO, fg=PRETO,
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(10, 4))

            if campo == "Categoria":
                entrada = ttk.Combobox(
                    form,
                    values=[
                        "Roupas", "Calçados", "Acessórios"
                    ],
                    state="readonly"
                )
                entrada.set("Roupas")
            else:
                entrada = tk.Entry(
                    form, font=("Arial", 12),
                    bg="#F5F5F5", relief="flat"
                )

            entrada.pack(fill="x", ipady=7)
            entradas[campo] = entrada

        imagem = tk.StringVar()

        def selecionar():
            arquivo = filedialog.askopenfilename(
                filetypes=[("PNG", "*.png")]
            )
            if arquivo:
                imagem.set(arquivo)

        self.botao(
            form, "SELECIONAR IMAGEM PNG",
            selecionar
        ).pack(anchor="w", pady=12)

        tk.Label(
            form, textvariable=imagem,
            bg=BRANCO, fg=CINZA,
            wraplength=500
        ).pack(anchor="w")

        def salvar():
            nome = entradas["Nome"].get().strip()
            texto_preco = entradas["Preço"].get().strip()

            try:
                preco = float(
                    texto_preco.replace(",", ".")
                )
            except ValueError:
                messagebox.showwarning(
                    "Erro", "Digite um preço válido."
                )
                return

            if not nome or preco <= 0:
                messagebox.showwarning(
                    "Erro", "Preencha nome e preço."
                )
                return

            self.db.execute("""
                INSERT INTO produtos
                (nome, preco, categoria, imagem)
                VALUES (?, ?, ?, ?)
            """, (
                nome, preco,
                entradas["Categoria"].get(),
                imagem.get()
            ))
            self.db.commit()

            messagebox.showinfo(
                "UrbanStyle", "Produto cadastrado!"
            )
            self.administracao()

        self.botao(
            form, "CADASTRAR PRODUTO",
            salvar
        ).pack(anchor="w", pady=15)

    def fechar(self):
        self.db.close()
        self.janela.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    UrbanStyle(janela)
    janela.mainloop()

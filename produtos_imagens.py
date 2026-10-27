
from PIL import Image, ImageDraw
from pathlib import Path

PASTA = Path(__file__).resolve().parent / "imagens"
PASTA.mkdir(exist_ok=True)

PRODUTOS = [
    ("Camiseta Oversized", 79.90, "Roupas", "camiseta", "#202020"),
    ("Tênis Casual", 199.90, "Calçados", "tenis", "#EAEAEA"),
    ("Boné Streetwear", 49.90, "Acessórios", "bone", "#242424"),
    ("Moletom Urban", 149.90, "Roupas", "moletom", "#555555"),
    ("Calça Cargo", 129.90, "Roupas", "calca", "#686B5A"),
    ("Jaqueta Street", 219.90, "Roupas", "jaqueta", "#252525"),
    ("Camiseta Branca", 69.90, "Roupas", "camiseta", "#F8F8F8"),
    ("Tênis Street", 249.90, "Calçados", "tenis", "#333333"),
    ("Boné Branco", 59.90, "Acessórios", "bone", "#F5F5F5"),
    ("Moletom Preto", 159.90, "Roupas", "moletom", "#171717"),
    ("Calça Jeans", 139.90, "Roupas", "calca", "#385574"),
    ("Bolsa Casual", 89.90, "Acessórios", "bolsa", "#393939"),
]


def criar_imagem(tipo, cor, caminho):
    img = Image.new("RGB", (320, 320), "#F0F0F0")
    d = ImageDraw.Draw(img)

    # Sombra
    d.ellipse((65, 275, 255, 295), fill="#D7D7D7")

    if tipo in ("camiseta", "moletom", "jaqueta"):
        pontos = [
            (115, 65), (85, 80), (35, 135),
            (70, 160), (95, 130), (95, 260),
            (225, 260), (225, 130), (250, 160),
            (285, 135), (235, 80), (205, 65)
        ]
        d.polygon(pontos, fill=cor, outline="#777777", width=3)
        d.arc((125, 58, 195, 100), 0, 180,
              fill="#888888", width=4)

        if tipo == "moletom":
            d.arc((115, 35, 205, 125), 180, 360,
                  fill="#777777", width=8)
            d.rounded_rectangle(
                (120, 195, 200, 225), radius=10,
                outline="#888888", width=3
            )

        if tipo == "jaqueta":
            d.line((160, 95, 160, 260),
                   fill="#AAAAAA", width=5)

    elif tipo == "calca":
        pontos = [
            (105, 50), (215, 50),
            (230, 270), (175, 270),
            (160, 140), (145, 270),
            (90, 270)
        ]
        d.polygon(pontos, fill=cor, outline="#777777", width=3)
        d.line((105, 85, 215, 85), fill="#999999", width=3)
        d.line((160, 85, 160, 140), fill="#999999", width=2)

    elif tipo == "tenis":
        d.polygon([
            (45, 180), (95, 145), (150, 165),
            (190, 195), (255, 205), (280, 235),
            (275, 255), (45, 255)
        ], fill=cor, outline="#777777", width=3)
        d.rounded_rectangle(
            (42, 238, 280, 263), radius=8,
            fill="white", outline="#777777", width=3
        )
        for x in range(125, 190, 18):
            d.line((x, 183, x + 18, 195),
                   fill="#AAAAAA", width=4)

    elif tipo == "bone":
        d.pieslice((65, 75, 255, 255), 180, 360,
                   fill=cor, outline="#777777", width=3)
        d.ellipse((135, 70, 185, 90), fill=cor)
        d.polygon([
            (75, 170), (250, 170),
            (285, 195), (240, 215), (90, 205)
        ], fill=cor, outline="#777777", width=3)

    elif tipo == "bolsa":
        d.rounded_rectangle(
            (65, 115, 255, 260), radius=20,
            fill=cor, outline="#777777", width=3
        )
        d.arc((110, 55, 210, 165), 180, 360,
              fill="#555555", width=12)
        d.line((65, 170, 255, 170),
               fill="#777777", width=3)

    img.save(caminho)


def preparar_produtos():
    import sqlite3

    banco = Path(__file__).resolve().parent / "urbanstyle.db"
    conexao = sqlite3.connect(banco)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            categoria TEXT NOT NULL,
            imagem TEXT
        )
    """)

    for nome, preco, categoria, tipo, cor in PRODUTOS:
        arquivo = PASTA / (
            nome.lower()
            .replace(" ", "_")
            .replace("ç", "c") + ".png"
        )

        if not arquivo.exists():
            criar_imagem(tipo, cor, arquivo)

        registro = cursor.execute(
            "SELECT id, imagem FROM produtos WHERE nome = ?",
            (nome,)
        ).fetchone()

        if registro:
            # Preserva imagens personalizadas já cadastradas
            if not registro[1]:
                cursor.execute(
                    "UPDATE produtos SET imagem = ? WHERE id = ?",
                    (str(arquivo), registro[0])
                )
        else:
            cursor.execute("""
                INSERT INTO produtos
                (nome, preco, categoria, imagem)
                VALUES (?, ?, ?, ?)
            """, (nome, preco, categoria, str(arquivo)))

    conexao.commit()
    conexao.close()


if __name__ == "__main__":
    preparar_produtos()
    print("Produtos e imagens preparados com sucesso!")

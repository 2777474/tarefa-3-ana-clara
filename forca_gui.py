import json
import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


BASE_DIR = Path(__file__).resolve().parent
PALAVRAS_ARQUIVO = BASE_DIR / "palavras.txt"
ESTATISTICAS_ARQUIVO = BASE_DIR / "estatisticas.json"
MAX_ERROS = 6
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def carregar_palavras(arquivo):
    caminho = Path(arquivo)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de palavras nao encontrado: {caminho}")

    palavras = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        palavra = linha.strip().upper()
        if palavra:
            palavras.append(palavra)
    if not palavras:
        raise ValueError("O arquivo de palavras esta vazio.")
    return palavras


def normalizar(texto):
    replacements = str.maketrans(
        "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ",
        "AAAAAEEEEIIIIOOOOOUUUUC",
    )
    return texto.upper().translate(replacements)


def escolher_palavra(lista):
    if not lista:
        raise ValueError("A lista de palavras esta vazia.")
    return random.choice(lista).upper()


def atualizar_display(palavra, letras_tentadas):
    if not letras_tentadas:
        tentadas = set()
    else:
        tentadas = {normalizar(letra) for letra in letras_tentadas}

    exibicao = []
    for letra in palavra:
        if normalizar(letra) in tentadas or not letra.isalpha():
        #espaco or punctuation
            exibicao.append(letra)
        else:
            exibicao.append("_")
    return " ".join(exibicao)


def verificar_vitoria(palavra, letras_tentadas):
    normalizada = normalizar(palavra)
    tentadas = {normalizar(letra) for letra in letras_tentadas}
    return all(normalizar(letra) in tentadas for letra in normalizada)


def carregar_estatisticas():
    if not ESTATISTICAS_ARQUIVO.exists():
        return {"vitorias": 0, "derrotas": 0}
    try:
        dados = json.loads(ESTATISTICAS_ARQUIVO.read_text(encoding="utf-8"))
        return {
            "vitorias": int(dados.get("vitorias", 0)),
            "derrotas": int(dados.get("derrotas", 0)),
        }
    except (json.JSONDecodeError, OSError, ValueError):
        return {"vitorias": 0, "derrotas": 0}


def salvar_estatisticas(vitorias, derrotas):
    dados = {"vitorias": int(vitorias), "derrotas": int(derrotas)}
    ESTATISTICAS_ARQUIVO.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class JogoDaForca:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Forca")
        self.root.geometry("760x650")
        self.root.minsize(680, 600)
        self.root.configure(bg="#f4f7fb")

        try:
            self.palavras = carregar_palavras(PALAVRAS_ARQUIVO)
        except (FileNotFoundError, ValueError) as exc:
            messagebox.showerror("Erro", str(exc))
            self.palavras = []

        stats = carregar_estatisticas()
        self.vitorias = stats["vitorias"]
        self.derrotas = stats["derrotas"]
        self.palavra = ""
        self.letras_tentadas = set()
        self.erros = 0
        self.jogo_encerrado = False
        self.hints_usados = 0

        self.criar_interface()
        self.novo_jogo()

    def criar_interface(self):
        titulo = tk.Label(
            self.root,
            text="JOGO DA FORCA",
            font=("Arial", 24, "bold"),
            fg="#1f3a5f",
            bg="#f4f7fb",
        )
        titulo.pack(pady=(12, 4))

        topo = tk.Frame(self.root, bg="#f4f7fb")
        topo.pack(fill="x", padx=20)

        self.canvas = tk.Canvas(topo, width=240, height=260, bg="white", highlightthickness=1,
                                highlightbackground="#cbd5e1")
        self.canvas.pack(side="left", padx=(0, 20))

        painel = tk.Frame(topo, bg="#f4f7fb")
        painel.pack(side="left", fill="both", expand=True)

        self.display = tk.Label(
            painel,
            text="_",
            font=("Courier", 28, "bold"),
            fg="#1f3a5f",
            bg="#f4f7fb",
        )
        self.display.pack(pady=(35, 10))

        self.tentativas_label = tk.Label(
            painel,
            text="",
            font=("Arial", 15, "bold"),
            fg="#b91c1c",
            bg="#f4f7fb",
        )
        self.tentativas_label.pack(pady=8)

        self.status_label = tk.Label(
            painel,
            text="",
            font=("Arial", 13),
            fg="#334155",
            bg="#f4f7fb",
        )
        self.status_label.pack(pady=8)

        self.stats_label = tk.Label(
            painel,
            text="",
            font=("Arial", 12),
            fg="#475569",
            bg="#f4f7fb",
        )
        self.stats_label.pack(pady=8)

        botoes = tk.Frame(self.root, bg="#f4f7fb")
        botoes.pack(pady=8)
        self.botao_novo = tk.Button(botoes, text="Novo Jogo", command=self.novo_jogo,
                                    width=12, font=("Arial", 11, "bold"), bg="#2563eb", fg="white")
        self.botao_novo.pack(side="left", padx=5)
        self.botao_desistir = tk.Button(botoes, text="Desistir", command=self.desistir,
                                        width=12, font=("Arial", 11, "bold"), bg="#dc2626", fg="white")
        self.botao_desistir.pack(side="left", padx=5)
        self.botao_dica = tk.Button(botoes, text="Dicas", command=self.dar_dica,
                                    width=12, font=("Arial", 11, "bold"), bg="#7c3aed", fg="white")
        self.botao_dica.pack(side="left", padx=5)

        teclado = tk.Frame(self.root, bg="#f4f7fb")
        teclado.pack(pady=8)
        self.botoes_letras = {}
        for indice, letra in enumerate(LETRAS):
            linha = indice // 9
            coluna = indice % 9
            botao = tk.Button(
                teclado,
                text=letra,
                width=5,
                height=2,
                font=("Arial", 10, "bold"),
                bg="#e2e8f0",
                command=lambda l=letra: self.tentar_letra(l),
            )
            botao.grid(row=linha, column=coluna, padx=3, pady=3)
            self.botoes_letras[letra] = botao

        self.root.bind("<Key>", self.teclado_fisico)

    def desenhar_boneco(self):
        self.canvas.delete("all")
        self.canvas.create_line(30, 230, 210, 230, width=3)
        self.canvas.create_line(70, 230, 70, 30, width=3)
        self.canvas.create_line(70, 30, 165, 30, width=3)
        self.canvas.create_line(165, 30, 165, 55, width=3)

        if self.erros >= 1:
            self.canvas.create_oval(145, 55, 185, 95, width=3)
        if self.erros >= 2:
            self.canvas.create_line(165, 95, 165, 150, width=3)
        if self.erros >= 3:
            self.canvas.create_line(165, 110, 125, 135, width=3)
        if self.erros >= 4:
            self.canvas.create_line(165, 110, 205, 135, width=3)
        if self.erros >= 5:
            self.canvas.create_line(165, 150, 135, 195, width=3)
        if self.erros >= 6:
            self.canvas.create_line(165, 150, 195, 195, width=3)

    def novo_jogo(self):
        if not self.palavras:
            return
        self.palavra = escolher_palavra(self.palavras)
        self.letras_tentadas = set()
        self.erros = 0
        self.jogo_encerrado = False
        self.hints_usados = 0
        self.status_label.config(text="Escolha uma letra", fg="#334155")
        self.botao_desistir.config(state="normal")
        self.botao_dica.config(state="normal")
        for botao in self.botoes_letras.values():
            botao.config(state="normal", bg="#e2e8f0")
        self.atualizar_interface()

    def atualizar_interface(self):
        self.display.config(text=atualizar_display(self.palavra, self.letras_tentadas))
        restantes = MAX_ERROS - self.erros
        self.tentativas_label.config(text=f"Tentativas restantes: {restantes}")
        self.stats_label.config(
            text=f"Vitorias: {self.vitorias}  |  Derrotas: {self.derrotas}"
        )
        self.desenhar_boneco()

    def teclado_fisico(self, evento):
        letra = evento.char.upper()
        if letra in LETRAS:
            self.tentar_letra(letra)

    def tentar_letra(self, letra):
        if self.jogo_encerrado:
            return
        letra = normalizar(letra)
        if letra in self.letras_tentadas:
            self.status_label.config(text=f"A letra {letra} ja foi tentada.", fg="#d97706")
            return

        self.letras_tentadas.add(letra)
        botao = self.botoes_letras.get(letra)
        if normalizar(letra) not in normalizar(self.palavra):
            self.erros += 1
            if botao:
                botao.config(state="disabled", bg="#fecaca")
            self.status_label.config(text=f"A letra {letra} nao existe na palavra.", fg="#dc2626")
        else:
            if botao:
                botao.config(state="disabled", bg="#bbf7d0")
            self.status_label.config(text=f"Boa! A letra {letra} existe.", fg="#15803d")

        self.atualizar_interface()
        self.verificar_fim()

    def dar_dica(self):
        if self.jogo_encerrado:
            return
        ocultas = []
        for letra in normalizar(self.palavra):
            if letra not in self.letras_tentadas:
                ocultas.append(letra)
        if not ocultas:
            self.status_label.config(text="Nao ha letras ocultas para revelar.", fg="#334155")
            return

        letra = random.choice(sorted(set(ocultas)))
        self.letras_tentadas.add(letra)
        botao = self.botoes_letras.get(letra)
        if botao:
            botao.config(state="disabled", bg="#ddd6fe")
        self.hints_usados += 1
        self.status_label.config(
            text=f"Dica: a letra {letra} foi revelada.",
            fg="#7c3aed",
        )
        self.atualizar_interface()
        self.verificar_fim()

    def verificar_fim(self):
        if verificar_vitoria(self.palavra, self.letras_tentadas):
            self.finalizar(True)
        elif self.erros >= MAX_ERROS:
            self.finalizar(False)

    def finalizar(self, venceu):
        self.jogo_encerrado = True
        self.botao_desistir.config(state="disabled")
        self.botao_dica.config(state="disabled")
        for botao in self.botoes_letras.values():
            botao.config(state="disabled")

        if venceu:
            self.vitorias += 1
            self.status_label.config(
                text=f"Vitoria! A palavra era {self.palavra}.",
                fg="#15803d",
            )
            mensagem = "Parabens! Voce venceu!"
        else:
            self.derrotas += 1
            self.status_label.config(
                text=f"Derrota! A palavra era {self.palavra}.",
                fg="#dc2626",
            )
            mensagem = f"Voce perdeu! A palavra era {self.palavra}."

        salvar_estatisticas(self.vitorias, self.derrotas)
        self.atualizar_interface()
        messagebox.showinfo("Fim de jogo", mensagem)

    def desistir(self):
        if self.jogo_encerrado:
            return
        if messagebox.askyesno("Desistir", "Deseja desistir desta partida?"):
            self.finalizar(False)


def main():
    root = tk.Tk()
    JogoDaForca(root)
    root.mainloop()


if __name__ == "__main__":
    main()

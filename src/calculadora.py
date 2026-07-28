import tkinter as tk
import tkinter.font as tkfont

from expressao import apagar_ultimo, avaliar, deve_reiniciar, pode_digitar

resultado_mostrado = False

# Os botões mostram o símbolo tipográfico, mas o avaliador só entende o operador
# de verdade. A tradução é da camada de UI e acontece em `clicar`, antes de
# qualquer regra — nenhum "×" ou "−" (U+2212, não o hífen) chega a `expressao.py`.
TRADUCAO = {"÷": "/", "×": "*", "−": "-"}

# Paleta num lugar só: trocar o tema é mexer aqui, não caçar cor solta no arquivo.
CORES = {
    "fundo": "#14161c",
    "visor_texto": "#f2f5fa",
    "linha": "#2b3040",
    "numero": "#262a34",
    "numero_hover": "#313745",
    "numero_texto": "#eef1f6",
    "operador": "#2d323e",
    "operador_hover": "#3a4150",
    "operador_texto": "#f0a83c",
    "igual": "#f0a83c",
    "igual_hover": "#f7b957",
    "igual_texto": "#14161c",
    "limpar": "#262a34",
    "limpar_hover": "#3b2a2f",
    "limpar_texto": "#ff7b72",
    "apagar_texto": "#aeb6c4",  # cinza: apagar um toque não é destrutivo como o C
}

def clicar(valor):
    tecla = TRADUCAO.get(valor, valor)
    resetar_se_resultado(tecla)
    entrada.insert(tk.END, tecla)

def resetar_se_resultado(tecla):
    global resultado_mostrado
    if not resultado_mostrado:
        return
    # Dígito recomeça a conta; operador continua a partir do resultado.
    if deve_reiniciar(entrada.get(), tecla):
        entrada.delete(0, tk.END)
    resultado_mostrado = False

def limpar():
    global resultado_mostrado
    escrever_no_visor("")
    resultado_mostrado = False

def apagar():
    global resultado_mostrado
    escrever_no_visor(apagar_ultimo(entrada.get()))
    # O que sobrou virou expressão em edição, não resultado — sem isto, o
    # próximo dígito limparia o campo em vez de continuar de onde parou.
    resultado_mostrado = False

def calcular(_evento=None):
    global resultado_mostrado
    escrever_no_visor(avaliar(entrada.get()))
    resultado_mostrado = True
    return "break"  # o Enter não deve fazer mais nada além de calcular

def teclou_no_visor(evento):
    """Digitação direta no visor segue a MESMA regra dos botões.

    Sem isto, o teclado e os botões discordam: com `96` no visor, o botão `5`
    começa uma conta nova (mostra `5`), mas a tecla `5` cairia no campo por
    baixo do pano e viraria `965`.

    Roda antes da inserção do Tk (é binding do widget, que vem antes do da
    classe): decide o que fazer com o visor, e o caractere entra depois.
    """
    global resultado_mostrado
    if not resultado_mostrado:
        return None
    if evento.keysym in ("BackSpace", "Delete"):
        # Apagou: o que sobrar é expressão em edição, não mais um resultado.
        resultado_mostrado = False
        return None
    # Só tecla que REALMENTE entra no campo mexe no estado do visor. Sem este
    # filtro, o `\r` do Enter era tratado como dígito: apertar Enter duas vezes
    # limpava o visor antes de calcular e devolvia "Erro".
    if not evento.char or not pode_digitar(evento.char):
        return None  # Enter, Shift, Ctrl, setas — não é digitação
    if deve_reiniciar(entrada.get(), evento.char):
        escrever_no_visor("")
    resultado_mostrado = False
    return None

def escrever_no_visor(texto):
    """Troca o conteúdo do visor SEM passar pelo filtro de digitação.

    O filtro (`pode_digitar`) existe para o que vem de fora — tecla e Ctrl+V.
    O que a própria calculadora devolve é resultado, não digitação, e precisa
    aparecer mesmo tendo letra: sem desligar a validação aqui, o Tk recusaria a
    própria mensagem `"Erro"` e o visor ficaria vazio no lugar dela.
    """
    entrada.configure(validate="none")
    entrada.delete(0, tk.END)
    entrada.insert(tk.END, texto)
    entrada.configure(validate="key")

def escolher_fonte(*familias):
    """Primeira família instalada, para o app não depender de uma fonte só.

    Sem isso o Tk cai numa fonte padrão feia quando a família não existe — e o
    que está instalado muda bastante entre Linux, Windows e macOS.
    """
    disponiveis = set(tkfont.families())
    for familia in familias:
        if familia in disponiveis:
            return familia
    return "Helvetica"  # o Tk sempre resolve esta

def realcar_no_hover(botao, cor, cor_hover):
    """Clareia o botão sob o cursor — o Tk não tem estado de hover pronto."""
    # O Tk passa o evento para o callback; aqui ele não é usado, daí o `_`.
    botao.bind("<Enter>", lambda _evento: botao.configure(bg=cor_hover))
    botao.bind("<Leave>", lambda _evento: botao.configure(bg=cor))

# Interface Gráfica
janela = tk.Tk()
janela.title("Calculadora")
janela.geometry("340x500")
janela.resizable(False, False)
janela.configure(bg=CORES["fundo"])

fonte = escolher_fonte("Inter", "Segoe UI", "Roboto", "Noto Sans", "DejaVu Sans")

# Visor — sem moldura: o campo se funde ao fundo e só o texto aparece.
area_visor = tk.Frame(janela, bg=CORES["fundo"])
area_visor.pack(fill="x", padx=22, pady=(30, 0))

entrada = tk.Entry(
    area_visor,
    font=(fonte, 34),
    justify="right",
    bg=CORES["fundo"],
    fg=CORES["visor_texto"],
    insertbackground=CORES["operador_texto"],  # cursor visível no fundo escuro
    bd=0,
    highlightthickness=0,
)
entrada.pack(fill="x", ipady=6)
entrada.focus_set()

# Filtro de digitação: `%P` é o texto que o campo TERIA depois da tecla — se
# `pode_digitar` recusar, o Tk descarta a edição e a letra nunca aparece. Vale
# para tecla e para Ctrl+V, que chega como uma inserção só.
entrada.configure(
    validate="key",
    validatecommand=(janela.register(pode_digitar), "%P"),
)

# Enter calcula, de qualquer lugar da janela (por isso o bind é na `janela`, e
# não no campo: depois de clicar num botão, o foco está nele, não no visor).
# `<KP_Enter>` é o Enter do teclado numérico, que é uma tecla diferente.
janela.bind("<Return>", calcular)
janela.bind("<KP_Enter>", calcular)

# Já o ajuste do estado do visor é do campo: precisa rodar ANTES de o Tk
# inserir o caractere, e binding de widget vem antes do binding de classe.
entrada.bind("<Key>", teclou_no_visor)

# Filete no lugar da borda do Entry — marca o visor sem enquadrá-lo.
tk.Frame(area_visor, bg=CORES["linha"], height=1).pack(fill="x", pady=(10, 0))

# Grade dos botões
grade = tk.Frame(janela, bg=CORES["fundo"])
grade.pack(fill="both", expand=True, padx=16, pady=16)

for coluna in range(4):
    grade.grid_columnconfigure(coluna, weight=1, uniform="botao")
for linha_grade in range(5):
    grade.grid_rowconfigure(linha_grade, weight=1)

# Posição explícita porque a grade não é uniforme: o `0` ocupa duas colunas, e
# `C` e `=` dividem a linha de baixo. (texto, tipo, linha, coluna, colunas)
botoes = [
    ("7", "num", 0, 0, 1), ("8", "num", 0, 1, 1), ("9", "num", 0, 2, 1), ("÷", "op", 0, 3, 1),
    ("4", "num", 1, 0, 1), ("5", "num", 1, 1, 1), ("6", "num", 1, 2, 1), ("×", "op", 1, 3, 1),
    ("1", "num", 2, 0, 1), ("2", "num", 2, 1, 1), ("3", "num", 2, 2, 1), ("−", "op", 2, 3, 1),
    ("0", "num", 3, 0, 2), (".", "num", 3, 2, 1), ("+", "op", 3, 3, 1),
    ("C", "limpar", 4, 0, 1), ("⌫", "apagar", 4, 1, 1), ("=", "eq", 4, 2, 2),
]

# tipo -> (cor, cor no hover, cor do texto, corpo da fonte)
estilo_por_tipo = {
    "num": (CORES["numero"], CORES["numero_hover"], CORES["numero_texto"], "normal"),
    "op": (CORES["operador"], CORES["operador_hover"], CORES["operador_texto"], "bold"),
    "eq": (CORES["igual"], CORES["igual_hover"], CORES["igual_texto"], "bold"),
    "limpar": (CORES["limpar"], CORES["limpar_hover"], CORES["limpar_texto"], "bold"),
    "apagar": (CORES["numero"], CORES["numero_hover"], CORES["apagar_texto"], "normal"),
}

acoes_por_tipo = {"eq": calcular, "limpar": limpar, "apagar": apagar}

for texto, tipo, linha, coluna, colunas in botoes:
    cor, cor_hover, cor_texto, corpo = estilo_por_tipo[tipo]
    # `t=texto` captura o valor DESTA iteração — sem ele todos os botões
    # chamariam `clicar` com o texto do último.
    comando = acoes_por_tipo.get(tipo) or (lambda t=texto: clicar(t))

    botao = tk.Button(
        grade,
        text=texto,
        font=(fonte, 18 if tipo in ("op", "apagar") else 16, corpo),
        bg=cor,
        fg=cor_texto,
        activebackground=cor_hover,
        activeforeground=cor_texto,
        command=comando,
        bd=0,
        highlightthickness=0,
        relief="flat",
        cursor="hand2",
    )

    botao.grid(row=linha, column=coluna, columnspan=colunas, padx=5, pady=5, sticky="nsew")
    realcar_no_hover(botao, cor, cor_hover)

janela.mainloop()

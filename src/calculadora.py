import tkinter as tk

def clicar(valor):
    if valor == "X":
        entrada.insert(tk.END, "*")
    else:
        entrada.insert(tk.END, valor)

def limpar():
    entrada.delete(0, tk.END)

def calcular():
    try:
        resultado = eval(entrada.get())
        entrada.delete(0, tk.END)
        entrada.insert(tk.END, resultado)
    except:
        entrada.delete(0, tk.END)
        entrada.insert(tk.END, "Erro")

# Interface Gráfica
janela = tk.Tk()
janela.title("Calculadora")
janela.geometry("300x420") 
janela.resizable(False, False)
janela.configure(bg="#f2f2f2")

# Campo de entrada
entrada = tk.Entry(
    janela,
    font=("Arial", 20),
    justify="right",
    bg="white",
    fg="black",
    bd=0,       
    highlightthickness=1 
)
entrada.pack(fill="x", padx=15, pady=15) 

# Frame para os botões
frame = tk.Frame(janela, bg="#f2f2f2")
frame.pack(padx=10, pady=5)

for i in range(4):
    frame.grid_columnconfigure(i, weight=1)

# Definições de botões
numeros_cor = "#2c3e50"      
operacoes_cor = "#8e44ad"   
fundo_botao = "#ecf0f1"

botoes = [
    ("7", "num"), ("8", "num"), ("9", "num"), ("/", "op"),
    ("4", "num"), ("5", "num"), ("6", "num"), ("X", "op"),
    ("1", "num"), ("2", "num"), ("3", "num"), ("-", "op"),
    ("0", "num"), (".", "num"), ("=", "eq"), ("+", "op"),
]

linha = 0
coluna = 0

for texto, tipo in botoes:
    if tipo == "num":
        cor = numeros_cor
        comando = lambda t=texto: clicar(t)
    elif tipo == "op":
        cor = operacoes_cor
        comando = lambda t=texto: clicar(t)
    else:  # "="
        cor = "#27ae60"
        comando = calcular

    botao = tk.Button(
        frame,
        text=texto,
        width=5,
        height=2,
        font=("Arial", 12, "bold"),
        bg=fundo_botao,
        fg=cor,
        activebackground="#dcdde1",
        command=comando,
        bd=1,
        relief="raised"
    )

    botao.grid(row=linha, column=coluna, padx=3, pady=3, sticky="nsew")

    coluna += 1
    if coluna > 3:
        coluna = 0
        linha += 1

# Botão limpar
btn_limpar = tk.Button(
    frame,
    text="C",
    height=2,
    font=("Arial", 11, "bold"),
    bg="#f8d7da",
    fg="#721c24",
    activebackground="#f5c6cb",
    command=limpar,
    bd=1
)
btn_limpar.grid(row=linha, column=0, columnspan=4, padx=3, pady=3, sticky="nsew")

janela.mainloop()
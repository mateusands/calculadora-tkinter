# Calculadora em Python (Tkinter)

Calculadora simples desenvolvida em **Python** utilizando a biblioteca **Tkinter**, com interface gráfica e botões funcionais.  
Projeto com foco em aprendizado de GUI, organização de código e versionamento com Git/GitHub.

---

## Funcionalidades

- Interface gráfica simples e intuitiva
- Operações básicas:
  - Soma (+)
  - Subtração (-)
  - Multiplicação (X)
  - Divisão (/)
- Botões numéricos e operadores
- Botão **C (Limpar)**
- Tratamento básico de erros (expressões inválidas)

---

## Tecnologias utilizadas

- Python 3
- Tkinter (biblioteca padrão do Python)
- Git & GitHub

---

## Requisitos

- Python 3.10+
- Tk instalado no sistema — o `tkinter` é da biblioteca padrão, mas depende da
  lib Tk do SO. No Windows e no macOS ela já vem com o instalador do Python.
  No Linux é um pacote à parte:

  ```bash
  sudo pacman -S tk        # Arch / CachyOS
  sudo apt install python3-tk   # Debian / Ubuntu
  ```

Não há dependências externas, então não é preciso criar um ambiente virtual.

## Como usar

```bash
python src/calculadora.py
```
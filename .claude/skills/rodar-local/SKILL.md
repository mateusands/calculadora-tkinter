---
name: rodar-local
description: Rodar a calculadora Tkinter localmente e as pegadinhas do ambiente (Tk do sistema no Linux, venv só para desenvolver) mais o roteiro de teste manual da UI, que a suíte não cobre. Use ao rodar, testar manualmente ou debugar o ambiente.
---

# Rodar a calculadora localmente

## Para rodar não precisa de venv

O app usa **só a biblioteca padrão**. Para desenvolver (rodar a suíte) é preciso `pytest`, que fica em
`requirements-dev.txt` — separado justamente para o app continuar sem dependências.

```bash
python src/calculadora.py
```

## Pré-requisito real: o Tk do sistema

`tkinter` é stdlib, mas é um *binding* para a biblioteca **Tk do sistema operacional**. Se ela não estiver
instalada:

```
ImportError: libtk8.6.so: cannot open shared object file: No such file or directory
```

| Sistema | Como instalar |
|---|---|
| Arch / CachyOS | `sudo pacman -S tk` |
| Debian / Ubuntu | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| Windows / macOS | já vem com o instalador oficial do Python |

Verificar:

```bash
python -c "import tkinter; print('Tk', tkinter.TkVersion)"
```

## Pegadinhas

- **`import calculadora` abre a janela.** O `mainloop()` está em nível de módulo, na última linha. Não dá
  para importar o arquivo num REPL ou em teste sem a GUI subir e bloquear. Por isso a suíte importa
  `expressao`, nunca `calculadora`.

- **A janela é de tamanho fixo** (`300x420`, `resizable(False, False)`). Se você adicionar widget e ele
  não aparecer, provavelmente ficou fora da área — ajuste a geometria junto.

- **Sem servidor gráfico, não roda.** Em sessão SSH ou container sem display: `no display name and no
  $DISPLAY environment variable`. Precisa de X11 ou Wayland ativo.

- **A janela abre atrás de outras** em alguns gerenciadores. Se "não abriu", confira a barra de tarefas
  antes de investigar erro.

---

## Roteiro de teste manual

A suíte (`pytest`) cobre `avaliar()`; ela não abre janela. **Este roteiro cobre a UI** — o estado do
visor, que nenhum teste alcança. Rode os dois:

```bash
pip install -r requirements-dev.txt && pytest
```

### Operações básicas
- `2 + 3 =` → `5`
- `9 - 4 =` → `5`
- `6 X 7 =` → `42` (o botão mostra `X`, insere `*`)
- `8 / 2 =` → `4.0` ⚠️ com `.0` — comportamento atual, não regressão

### Erros
- `5 / 0 =` → `Erro`
- `1 . 2 . 3 =` → `Erro` (ponto decimal duplicado)
- `7 + =` → `Erro` (operador sem operando)
- Depois de qualquer `Erro`, o próximo dígito deve **limpar** o visor, não concatenar

### Fluxo de estado (a flag `resultado_mostrado`)
- `2 + 2 =` → `4`; digitar `5` → visor mostra `5` (limpou), **não** `45`
- `2 + 2 =` → `4`; apertar `+` → continua a conta a partir do resultado
- `C` limpa o visor em qualquer estado

### Layout
- Os 16 botões estão na grade 4×4, na ordem esperada
- O `C` ocupa a largura toda, na linha de baixo
- O texto do visor fica alinhado à direita e não estoura com número grande

---

## Empacotar (opcional)

Se um dia for gerar executável, o padrão para Tkinter é o PyInstaller:

```bash
pyinstaller --onefile --windowed src/calculadora.py
```

`--windowed` evita o terminal aparecer junto no Windows. Isso **adiciona uma dependência de build** —
como o `CLAUDE.md` diz que o projeto é stdlib-only, trate como decisão a ser pedida, não assumida.

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
- `6 × 7 =` → `42` (o botão mostra `×`, insere `*` — o visor exibe o operador ASCII)
- `8 / 2 =` → `4.0` ⚠️ com `.0` — comportamento atual, não regressão

### Erros
- `5 / 0 =` → `Erro`
- `1 . 2 . 3 =` → `Erro` (ponto decimal duplicado)
- `7 + =` → `Erro` (operador sem operando)
- Depois de qualquer `Erro`, o próximo dígito deve **limpar** o visor, não concatenar

### Fluxo de estado (a flag `resultado_mostrado` + `deve_reiniciar`)
- `2 + 2 =` → `4`; digitar `5` → visor mostra `5` (limpou), **não** `45`
- `2 + 2 =` → `4`; apertar `+` → visor mostra `4+` (encadeou); seguir com `3 =` → `7`
- `5 / 0 =` → `Erro`; apertar `+` → visor mostra `+` (erro não encadeia)
- `2 + 2 =` → `4`; apertar `C` e depois `+` → visor mostra `+` (o `C` zera a flag)

### Apagar (⌫ e C)
- `1 2 3` e `⌫` → `12` (some só o último)
- `1 2 + 3` e `⌫` → `12+` (o operador continua lá)
- `5 ÷ 0 =` → `Erro`; `⌫` → visor **vazio** (não pode sobrar `Err`)
- `1 2 × 8 =` → `96`; `⌫` e depois `5` → `95` (o que sobrou virou expressão em edição)
- `⌫` com o visor já vazio → não acontece nada, e nada quebra
- `C` continua zerando tudo de uma vez

### Teclado
- Digitar `12+7` e apertar **Enter** → `19` (e o Enter do teclado numérico também)
- Apertar **Enter de novo** → continua `19`. ⚠️ Se virar `Erro`, o handler de tecla voltou a tratar o
  `\r` do Enter como dígito e limpou o visor antes de calcular
- `2*3` Enter → `6`; teclar `5` → visor mostra `5` (conta nova, igual ao botão), **não** `65`
- `2*3` Enter → `6`; teclar `+ 4` Enter → `10` (encadeou)
- `96` no visor, **BackSpace**, teclar `5` → `95`
- `Esc` **não** limpa: não há atalho para o `C` nem para o `⌫`

### O visor é editável — teste digitando nele
- Clicar no campo e digitar `2+3` no teclado físico, depois clicar em `=` → `5`
- Digitar `q`, `abc`, espaço → **nada aparece no visor**; o campo recusa a tecla
- Colar `__import__('os').system('echo oi')` → **não entra**; e mesmo que entrasse, o `=` daria `Erro`
- Digitar `(2+3)*4` e `=` → `20` (parêntese é digitável, apesar de não ter botão)
- Digitar `9**9**9` e apertar `=` → `Erro` na hora; a janela **não** pode congelar
- ⚠️ Regressão a conferir sempre: `5 ÷ 0 =` ainda mostra `Erro`. A palavra tem letra — se o filtro de
  digitação for ligado errado, ele barra a própria mensagem e o visor fica vazio.

### Layout
- Os 18 botões estão na grade: 4×4 em cima, `0` ocupando duas colunas, e `C` + `⌫` + `=` na base
- O `=` é o único botão preenchido de âmbar; o `C` é o único com texto vermelho
- Passar o cursor sobre qualquer botão clareia o fundo (hover) e volta ao sair
- O texto do visor fica alinhado à direita e não estoura com número grande
- Com o tema escuro, o cursor do visor (âmbar) fica visível ao clicar no campo

---

## Empacotar (opcional)

Se um dia for gerar executável, o padrão para Tkinter é o PyInstaller:

```bash
pyinstaller --onefile --windowed src/calculadora.py
```

`--windowed` evita o terminal aparecer junto no Windows. Isso **adiciona uma dependência de build** —
como o `CLAUDE.md` diz que o projeto é stdlib-only, trate como decisão a ser pedida, não assumida.

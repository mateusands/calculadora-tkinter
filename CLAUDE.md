# CLAUDE.md — Calculadora (Python + Tkinter)

## Propósito do projeto

Calculadora de desktop com interface gráfica em Tkinter: operações básicas (+, −, ×, ÷), botão de limpar
e tratamento de expressão inválida. Projeto de portfólio com foco em **aprendizado de GUI, organização de
código e versionamento** — não em completude de funcionalidades.

---

## Fonte da verdade

**O estado real do sistema é o código.** São dois arquivos pequenos — `src/expressao.py` (a regra) e
`src/calculadora.py` (a UI). Leia os dois inteiros antes de mudar qualquer coisa.

---

## Stack

- **Python 3.10+**
- **Tkinter** — biblioteca padrão, sem `ttk`, sem CustomTkinter
- **Zero dependências externas para rodar.** O `requirements.txt` documenta isso
- **pytest** — só para desenvolver (`requirements-dev.txt`)

### Estrutura

```
calculadora-tkinter/
├── .github/workflows/
│   └── testes.yml        # CI: roda pytest no push/PR (sem Tk — a suíte não importa tkinter)
├── requirements.txt      # sem deps — só documenta que não há
├── requirements-dev.txt  # pytest
├── pytest.ini            # pythonpath=src, testpaths=tests
├── docs/
│   └── calculadora.png   # screenshot usado no README
├── src/
│   ├── calculadora.py    # UI em nível de módulo (importar ABRE a janela)
│   └── expressao.py      # avaliação da expressão — lógica PURA, testável
└── tests/
    └── test_expressao.py
```

⚠️ **Tkinter é da stdlib, mas depende da lib Tk do sistema.** No Windows e no macOS vem com o instalador
do Python; no Linux é pacote à parte (`sudo pacman -S tk` / `sudo apt install python3-tk`). Sem ele o
`import tkinter` falha com `libtk8.6.so: cannot open shared object file`.

---

## Como o código está organizado hoje

**Duas camadas**, separadas justamente para permitir teste:

- **`src/expressao.py`** — Lógica **pura**, sem Tkinter, importável e testável. Duas funções:
  - `avaliar(expressao) -> str`. Nunca levanta exceção: expressão inválida vira a string `"Erro"`.
    Não usa `eval` — percorre a árvore do `ast.parse` com allowlist (ver "Como o cálculo é avaliado").
  - `deve_reiniciar(visor, tecla) -> bool`. Com um resultado no visor, dígito recomeça a conta e
    operador encadeia a partir do resultado. `"Erro"` nunca encadeia.
  - `apagar_ultimo(visor) -> str`. Regra do botão `⌫`: tira só o último caractere. `"Erro"` é o caso
    especial — apagar limpa o visor inteiro, porque `"Err"` não é nada.
  - `pode_digitar(texto) -> bool`. Filtro do que o usuário pode digitar ou colar no visor
    (`CARACTERES_DIGITAVEIS`). É a segunda camada de defesa, não a única.
- **`src/calculadora.py`** — a UI. Não há classes nem `main()`; o arquivo é lido de cima para baixo:
  1. `resultado_mostrado` — flag global: o visor exibe um resultado?
  2. `TRADUCAO` (rótulo `÷ × −` → operador `/ * -`) e `CORES` (paleta do tema, num lugar só)
  3. Funções `clicar`, `resetar_se_resultado`, `limpar`, `apagar`, `calcular` (delegam para
     `expressao.py`) e `escrever_no_visor`; mais `escolher_fonte` e `realcar_no_hover`, só apresentação
  4. Criação de `janela` e `entrada` **em nível de módulo**, com o filtro de digitação ligado no campo
  5. Laço que gera os 18 botões a partir da lista `botoes`, que carrega a posição na grade —
     ela não é uniforme: `0` ocupa duas colunas, e `C`, `⌫` e `=` dividem a linha de baixo
  6. `janela.mainloop()` na última linha

### Teclado

O visor é editável, então **teclado e botões precisam concordar** — e o que faz isso são dois bindings
com papéis diferentes:

| Binding | Onde | Por quê ali |
|---|---|---|
| `<Return>` / `<KP_Enter>` → `calcular` | na **`janela`** | vale de qualquer foco; depois de clicar num botão o foco está nele, não no visor |
| `<Key>` → `teclou_no_visor` | no **`entrada`** | binding de widget roda ANTES do da classe, então dá para limpar o visor antes de o caractere ser inserido |

`teclou_no_visor` aplica ao teclado a mesma `deve_reiniciar` dos botões: com `96` no visor, teclar `5`
começa conta nova e teclar `+` encadeia — igual ao clique. Sem ele o campo concatenava por baixo do
pano e virava `965`.

⚠️ **Tecla que não digita nada não pode mexer no estado.** O `Enter` tem `evento.char == "\r"`; sem o
`pode_digitar(evento.char)` na entrada da função, ele era tratado como dígito e **apertar Enter duas
vezes limpava o visor antes de calcular, devolvendo `"Erro"`**. Mesma armadilha vale para qualquer
tecla nova com `char` preenchido (Tab, Esc).

### Aparência

Tema escuro, todo declarado no dicionário `CORES` e na fonte escolhida por `escolher_fonte` (primeira
família instalada da lista — o que existe muda entre Linux, Windows e macOS). **Mudar o tema é mexer
nesses dois lugares**, não caçar literal no meio do arquivo.

Detalhes que não são acidente:

- `tk.Button` **não tem canto arredondado nem estado de hover** — não existe opção para isso no Tk puro.
  O hover é feito à mão em `realcar_no_hover` (`<Enter>`/`<Leave>`), e canto redondo só desenhando em
  `Canvas`, o que seria reescrever a UI inteira. Não vale.
- O visor não tem moldura (`bd=0`, `highlightthickness=0`): quem marca a área é um `Frame` de 1px.
- `insertbackground` deixa o cursor visível no fundo escuro — sem isso ele some.

⚠️ **`import calculadora` ainda ABRE a janela** e bloqueia no `mainloop()`. É por isso que a regra vive
em `expressao.py`: os testes importam só esse módulo. Se um dia a UI precisar ser testada, o passo é
envolvê-la em `main()` + `if __name__ == "__main__":` — mudança estrutural, peça antes.

---

## Como o cálculo é avaliado (não mexa sem ler isto)

**`avaliar()` não usa `eval`.** A expressão é lida com `ast.parse(..., mode="eval")` e a árvore é
percorrida à mão em `_calcular`, com **allowlist de nós**: `Constant` numérico (`bool` recusado de
propósito — é subclasse de `int`), `BinOp` com `+ - * /` e `UnaryOp` com sinal. Nada é executado; os
operadores vêm do módulo `operator`. Qualquer outro nó levanta `ValueError` e vira `"Erro"`.

⚠️ **O motivo é que o visor é um `tk.Entry` comum, editável.** Dá para clicar nele, digitar e colar
(Ctrl+V) — não são só os botões que alimentam o campo. Com `eval`, colar
`__import__('os').system(...)` e apertar `=` executava o comando de verdade. A allowlist é o que
sustenta a promessa de que o campo é seguro para digitar.

**São duas camadas, e cada uma pega o que a outra não pega:**

| Camada | Onde | O que decide | Exemplo do que só ela barra |
|---|---|---|---|
| Filtro de digitação | `pode_digitar`, ligado no `Entry` com `validate="key"` | o que **entra** no visor | `q` — a letra nem aparece no campo |
| Allowlist do `ast` | `_calcular`, dentro de `avaliar` | o que é **calculável** | `2**3` — os caracteres são válidos, a operação não |

⚠️ **Armadilha do `validate="key"`: o Tk valida também o que o PROGRAMA escreve no campo.** Como
`"Erro"` tem letra, um `entrada.insert` direto seria recusado e o visor ficaria vazio no lugar da
mensagem. É por isso que todo write da calculadora passa por `escrever_no_visor`, que desliga a
validação, escreve e religa. **Nunca use `entrada.insert`/`delete` direto para resultado.**

Consequências que valem como regra:

- **Operador novo entra na allowlist, não em `eval`.** Adicionar `%` ou `**` é acrescentar a entrada em
  `_OPERACOES_BINARIAS` e o teste correspondente — nunca afrouxar o parser.
- **`**` está fora de propósito:** `9**9**9` roda por tempo indefinido na thread do `mainloop`, congela
  a janela e não há como cancelar. Travado por `test_deve_devolver_erro_sem_travar_em_calculo_explosivo`.
- **`avaliar()` nunca levanta exceção.** Cuidado com `except Exception:` se algum dia o avaliador puder
  produzir `BaseException` — foi exatamente assim que `exit()` escapava na versão com `eval`
  (`SystemExit` não é `Exception`). Travado por `test_nunca_deve_levantar_excecao`.

---

## Armadilhas ativas (conhecidas, ainda no código)

1. **Divisão inteira vs. float:** `avaliar("1/2")` devolve `"0.5"`, mas `avaliar("4/2")` devolve `"2.0"`
   — o visor mostra `2.0`, não `2`. Formatação de resultado nunca foi tratada. Está travado por teste
   (`test_deve_devolver_float_na_divisao_exata`): se você formatar, o teste falha de propósito, para
   forçar a decisão consciente.

2. **Estado por variável global** (`resultado_mostrado`, `entrada`, `janela`). Qualquer função nova que
   precise do visor depende do global — não há injeção.

3. **Só o `Enter` tem atalho.** `<Return>` e `<KP_Enter>` calculam (equivalem ao `=`). `Esc` **não**
   limpa e não há atalho para o `⌫` — quem quiser apagar pelo teclado usa o BackSpace nativo do campo.

4. **A validação da digitação é por caractere, não por estrutura.** Letra não entra mais no visor
   (`pode_digitar`), mas `1..2` e `2++` são digitáveis e só falham no `=`, virando `Erro` sem dizer
   onde. O feedback continua sendo o mínimo: a palavra `Erro` no visor.

---

## Como trabalhar neste repositório

### Rodar

```bash
python src/calculadora.py       # o app não precisa de venv nem de instalação
```

### Testar

```bash
pip install -r requirements-dev.txt
pytest
```

### Regras de desenvolvimento

- **Não introduza dependência externa para RODAR** sem pedido explícito. O app ser stdlib-only é
  característica, não limitação acidental. `pytest` é dependência de desenvolvimento e fica separada em
  `requirements-dev.txt` justamente para preservar isso.
- **Não reescreva para classes/MVC de repente.** É um projeto de aprendizado; refatoração estrutural só
  quando pedida.
- **Regra nova vai para `expressao.py`, não para `calculadora.py`.** É o que a mantém testável. Se você
  precisou pôr um `if` de regra dentro de um callback de botão, provavelmente ele pertence a `expressao.py`.
- Nomes e comentários em **português**, seguindo o que já está no arquivo.

---

## Regra inegociável: SDD + BDD + TDD

Nenhum código de produção é escrito sem spec (SDD) → comportamento (BDD) → teste vermelho (TDD).
Sem exceções, mesmo em mudança pequena.

### 1. SDD — a spec mora no topo do arquivo de teste

Cabeçalho explicando **qual é o contrato**, **por que existe** e **o que é regra de negócio**.
Modelo: `tests/test_expressao.py`.

### 2. BDD — comportamento, não implementação

`class Test<CenárioDeNegócio>` → `def test_deve_<resultado>_quando_<condição>`, em português, na
linguagem da calculadora (visor, resultado, expressão inválida).

### 3. TDD — Red → Green → Refactor

Escreva o teste, rode e **veja falhar**; só então escreva o mínimo para passar.

### O que testar

| Prioridade | Alvo |
|---|---|
| 🔴 Alta | `avaliar()` — toda operação, todo caso de erro, todo encadeamento |
| 🟡 Média | Regra nova extraída da UI (formatação de resultado, suporte a teclado) |
| 🟢 Nenhuma | Widget — `calculadora.py` não é importável sem abrir a janela |

**Não há mock neste projeto** e não deveria haver: `avaliar()` é pura. Se você sentir necessidade de
mockar algo, é sinal de que a regra foi para o lugar errado.

**Verde não basta.** A suíte cobre o cálculo, não a interface. Depois de passar, abra o app e passe pelo
roteiro de `/rodar-local` — principalmente o comportamento de digitar logo após um resultado, que é
estado da UI e nenhum teste cobre.

### Convenção de commits

Conventional Commits, descrição no imperativo: `feat: adiciona suporte a teclado`,
`fix: trata divisão por zero sem quebrar o visor`, `test: cobre encadeamento de resultado`,
`refactor: extrai avaliação de expressão`.

---

## Regras gerais

- **O código é a fonte da verdade.** Se algo aqui parecer inconsistente com o código, o código vence —
  e atualize este arquivo.
- Decisão técnica não-óbvia deve ser documentada (no commit e/ou aqui).
- **Não commite nem faça push sem ordem explícita.**

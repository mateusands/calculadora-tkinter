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
├── requirements.txt      # sem deps — só documenta que não há
├── requirements-dev.txt  # pytest
├── pytest.ini            # pythonpath=src, testpaths=tests
├── src/
│   ├── calculadora.py    # UI em nível de módulo (importar ABRE a janela)
│   ├── expressao.py      # avaliação da expressão — lógica PURA, testável
│   └── *.png             # screenshots do README
└── tests/
    └── test_expressao.py
```

⚠️ **Tkinter é da stdlib, mas depende da lib Tk do sistema.** No Windows e no macOS vem com o instalador
do Python; no Linux é pacote à parte (`sudo pacman -S tk` / `sudo apt install python3-tk`). Sem ele o
`import tkinter` falha com `libtk8.6.so: cannot open shared object file`.

---

## Como o código está organizado hoje

**Duas camadas**, separadas justamente para permitir teste:

- **`src/expressao.py`** — `avaliar(expressao) -> str`. Lógica **pura**, sem Tkinter, importável e
  testável. Nunca levanta exceção: expressão inválida vira a string `"Erro"`.
- **`src/calculadora.py`** — a UI. Não há classes nem `main()`; o arquivo é lido de cima para baixo:
  1. `resultado_mostrado` — flag global: o visor exibe um resultado? (o próximo dígito limpa o campo)
  2. Funções `clicar`, `resetar_se_resultado`, `limpar`, `calcular` (esta delega para `avaliar`)
  3. Criação de `janela` e `entrada` **em nível de módulo**
  4. Laço que gera os 16 botões a partir da lista `botoes`
  5. `janela.mainloop()` na última linha

⚠️ **`import calculadora` ainda ABRE a janela** e bloqueia no `mainloop()`. É por isso que a regra vive
em `expressao.py`: os testes importam só esse módulo. Se um dia a UI precisar ser testada, o passo é
envolvê-la em `main()` + `if __name__ == "__main__":` — mudança estrutural, peça antes.

---

## Armadilhas ativas (conhecidas, ainda no código)

1. **`avaliar()` usa `eval()` na string do visor.** Funciona, mas `eval` executa **Python arbitrário**,
   não só aritmética. Como o teclado da UI só produz dígitos e operadores, a exposição prática é baixa —
   mas se algum dia o campo aceitar digitação livre ou colar do clipboard, vira execução de código. A
   substituição correta é um parser de expressão (`ast.literal_eval` não resolve operadores; o caminho é
   `ast.parse` com allowlist de nós, ou um avaliador próprio). **Troque o avaliador ANTES de liberar a
   entrada, não depois.**

2. **Divisão inteira vs. float:** `eval("1/2")` devolve `0.5`, mas `eval("4/2")` devolve `2.0` — o visor
   mostra `2.0`, não `2`. Formatação de resultado nunca foi tratada. Está travado por teste
   (`test_deve_devolver_float_na_divisao_exata`): se você formatar, o teste falha de propósito, para
   forçar a decisão consciente.

3. **Estado por variável global** (`resultado_mostrado`, `entrada`, `janela`). Qualquer função nova que
   precise do visor depende do global — não há injeção.

4. **Sem suporte a teclado.** Só clique; digitar números no teclado físico não faz nada.

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

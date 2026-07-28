---
name: python-gui
description: Desenvolvimento da calculadora Tkinter — convenções do repo (separação expressao.py/calculadora.py, estado global do visor, closure de laço em botão), o que muda ao mexer na lógica de cálculo e o ciclo TDD obrigatório. Use ao mexer em src/calculadora.py ou src/expressao.py.
---

# Python GUI — calculadora Tkinter

Guia para qualquer mexida no app. Segue o `CLAUDE.md`: **stdlib pura**, **não refatore o que não foi
pedido**, **sem commit/push sem ordem**.

## O que este projeto é

Dois arquivos pequenos, Tkinter puro, sem classes e sem `main()`. Projeto de **aprendizado de GUI**.
Toda proposta de reescrever em MVC, adicionar CustomTkinter ou trocar por PyQt muda a natureza dele —
só com pedido explícito.

- **`src/expressao.py`** — a regra (`avaliar`). Pura, importável, **coberta por teste**.
- **`src/calculadora.py`** — a UI. Widgets e `mainloop()` em nível de módulo.

---

## Convenções do código (siga, não invente outro padrão)

### Widgets são criados em nível de módulo

`janela` e `entrada` existem no escopo global e as funções os acessam diretamente. Não há injeção de
dependência. Ao adicionar uma função que mexe no visor, ela vai usar `entrada` global igual às outras —
seja consistente com o arquivo, não introduza um segundo padrão no meio.

**Efeito colateral que você precisa conhecer:** como o `mainloop()` está na última linha do módulo,
`import calculadora` **abre a janela** e bloqueia. É por isso que a regra vive em `expressao.py` — os
testes importam só aquele módulo.

### Closure em laço: o `t=texto` não é decorativo

```python
comando = lambda t=texto: clicar(t)
```

O argumento default **captura o valor da iteração atual**. Sem ele, todos os 18 botões chamariam
`clicar` com o valor da **última** iteração — bug clássico de Python em laço. Ao criar botão dentro de
laço, repita esse padrão.

### O visor é a única fonte de estado da expressão

Não há variável guardando a expressão — ela vive no texto do `Entry`. A flag `resultado_mostrado` diz se
o conteúdo atual é um resultado. O que fazer com ele **não** é decidido no callback: `resetar_se_resultado`
pergunta a `deve_reiniciar(visor, tecla)`, em `expressao.py` — dígito recomeça a conta, operador encadeia
a partir do resultado, `"Erro"` nunca encadeia.

Toda função nova que escreve no visor precisa decidir o que fazer com essa flag, senão o comportamento
"digitar depois do igual" quebra de forma sutil. `limpar()` e `apagar()` zeram a flag: visor vazio não é
resultado, e resultado com um dígito a menos virou expressão em edição.

### Binding de tecla: o lugar do `bind` é decisão, não detalhe

- **Ação global** (`<Return>`/`<KP_Enter>` → `calcular`) vai na **`janela`**: depois de clicar num botão
  o foco está nele, e um bind no `entrada` não pegaria.
- **Ajuste do visor antes da digitação** (`<Key>` → `teclou_no_visor`) vai no **`entrada`**: binding de
  widget roda antes do da classe, então dá para limpar o campo antes de o caractere entrar.

⚠️ **Filtre a tecla antes de mexer no estado.** `evento.char` do Enter é `"\r"` — sem
`pode_digitar(evento.char)`, ele passa por dígito e apertar Enter duas vezes limpa o visor antes de
calcular, devolvendo `"Erro"`. Já aconteceu; o smoke test da UI cobre.

### Escrever no visor é sempre por `escrever_no_visor`

O `Entry` tem filtro de digitação (`validate="key"` + `pode_digitar`), e **o Tk valida também o que o
programa escreve**. Como `"Erro"` tem letra, um `entrada.insert` direto seria recusado e o visor
ficaria vazio no lugar da mensagem. `escrever_no_visor` desliga a validação, escreve e religa.

Regra prática: **texto que vem da calculadora** (resultado, erro) usa `escrever_no_visor`; **texto que
vem do usuário** (a tecla em `clicar`) entra pelo `insert` normal e passa pelo filtro de propósito.

### O rótulo é tipográfico, o operador é ASCII

Os botões mostram `÷ × −`, mas o avaliador só entende `/ * -`. A tradução vive no dicionário `TRADUCAO`,
aplicado na **primeira linha** de `clicar()` — antes de `resetar_se_resultado`, senão `deve_reiniciar`
receberia `"×"`, não o reconheceria como operador e o encadeamento quebraria de forma silenciosa.

Operador novo com símbolo bonito entra em `TRADUCAO`. Cuidado: o `−` dos botões é U+2212, **não** o
hífen do teclado — os dois precisam funcionar, porque o visor também aceita digitação.

---

## Ao mexer na lógica de cálculo

`avaliar()`, em `src/expressao.py`, é a função mais delicada do projeto. `calcular()` na UI só delega
para ela e escreve o resultado no visor.

- **Não há `eval` aqui, e não pode voltar a haver.** A expressão é lida com `ast.parse` e percorrida em
  `_calcular` com allowlist de nós (`Constant` numérico, `BinOp` com `+ - * /`, `UnaryOp` de sinal).
  O motivo é concreto: o visor é um `Entry` editável, o usuário digita e cola nele: com `eval`, colar
  `__import__('os').system(...)` e apertar `=` executava o comando. `TestApenasAritmetica` trava isso.
- **Operador novo = entrada nova na allowlist + teste.** Acrescente em `_OPERACOES_BINARIAS` (ou
  `_OPERACOES_UNARIAS`) e cubra com teste. Nunca "abra" o parser para resolver um caso.
- **`**` fica de fora de propósito:** `9**9**9` roda indefinidamente na thread do `mainloop` e congela a
  janela sem cancelamento possível.
- **`bool` é subclasse de `int`** — a guarda contra `True+1` em `_calcular` não é decorativa.
- **`avaliar()` nunca levanta exceção** — expressão inválida vira a string `"Erro"`, porque o visor é o
  único canal de erro da calculadora. Está travado por `test_nunca_deve_levantar_excecao`.
- **O resultado não é formatado:** `avaliar("4/2")` → `"4.0"` no visor. Se for formatar, cuide dos casos
  `float` grande, notação científica e precisão de ponto flutuante (`0.1 + 0.2`) — e saiba que
  `test_deve_devolver_float_na_divisao_exata` vai falhar de propósito, para forçar a decisão consciente.

---

## Não travar a interface

Regra geral de Tkinter, ainda que hoje nada aqui seja lento: **tudo roda na thread do `mainloop`**. Se
algum dia entrar operação demorada (histórico em arquivo, cálculo pesado), ela **não** pode rodar no
handler do botão — a janela congela. O padrão é `threading.Thread(daemon=True)` para o trabalho e
`janela.after(0, callback)` para voltar à UI. **Nunca chame método de widget da thread de trabalho.**

---

## SDD + BDD + TDD (obrigatório) + validar verde

**Ordem: spec → comportamento → teste falhando → código.** Detalhe completo no `CLAUDE.md`.

- **SDD:** cabeçalho do teste explica contrato e porquê. Modelo: `tests/test_expressao.py`.
- **BDD:** `class Test<Cenário>` → `def test_deve_<resultado>_quando_<condição>`, em português.
- **TDD:** Red (roda e **falha**) → Green → Refactor.

### Onde a regra mora

`src/expressao.py` é a camada pura e **é onde regra nova entra**. `src/calculadora.py` é só UI e não é
importável sem abrir a janela — nada testável deve ir para lá.

```python
# ❌ regra dentro do callback → intestável
def calcular():
    if entrada.get().endswith("+"):        # a regra está presa na UI
        ...

# ✅ regra em expressao.py → testável direto
def avaliar(expressao: str) -> str:
    ...
```

Se você precisou escrever um `if` de regra dentro de um callback de botão, ele pertence a `expressao.py`.

**Não há mock neste projeto** e não deveria haver: `avaliar()` é pura, recebe string e devolve string.
Sentir necessidade de mockar é sinal de que a regra foi para o lugar errado.

```bash
pip install -r requirements-dev.txt
pytest
```

**Verde não basta.** A suíte cobre o cálculo, não a interface. Depois de passar, abra o app e passe pelo
roteiro de `/rodar-local` — em especial o comportamento de digitar logo após um resultado (a flag
`resultado_mostrado`), que é estado da UI e nenhum teste cobre.

Se for mexer no avaliador, `TestTratamentoDeErro` e `TestApenasAritmetica` já travam o contrato:
qualquer versão nova tem que devolver `"Erro"` nos mesmos casos, sem levantar exceção e sem executar
nada além das quatro operações.

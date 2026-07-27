---
name: codereview
description: Code review sênior das últimas mudanças da calculadora Tkinter, focado em correção do cálculo, robustez da UI e manutenibilidade. Apenas reporta problemas com arquivo/linha e a refatoração sugerida — não aplica correções.
---

# Code Review Sênior — calculadora Tkinter

Atue como Engenheiro Sênior e revise criticamente as **últimas mudanças deste repositório**.

## Como identificar o que revisar (nesta ordem)

1. Working tree: `git status` + `git diff` + arquivos novos relevantes.
2. Se limpo, os últimos commits da branch (`git log` + `git show`).
3. O projeto são dois arquivos pequenos (`src/expressao.py` + `src/calculadora.py`) — **leia os dois
   inteiros**, sempre.

## Pilar 1 — Correção do cálculo (o que mais importa aqui)

- **Avaliação da expressão:** o diff mexeu em `avaliar()` (`src/expressao.py`)? Toda mudança ali precisa
  vir com teste e ser conferida contra os casos-limite: divisão por zero, ponto decimal duplicado,
  operador solto no fim, expressão vazia, número muito grande, precisão de ponto flutuante.
- **`avaliar()` continua sem levantar exceção?** O contrato é devolver `"Erro"`, nunca propagar — o visor
  é o único canal de erro. Exceção escapando derruba o callback e deixa a janela viva porém inerte.
- **Regra de negócio que foi parar em `calculadora.py`** em vez de `expressao.py`: fica intestável, porque
  aquele módulo abre a janela ao ser importado. Aponte a realocação.
- **`eval()` com entrada mais ampla:** o diff permite que algo além dos botões chegue ao campo — digitação
  por teclado físico, colar do clipboard, histórico editável, arquivo de configuração? Se sim, `eval`
  deixou de ser "só aritmética" e virou **execução de código Python arbitrário**. Reporte no topo, com a
  alternativa (`ast.parse` + allowlist de nós).
- **Formatação do resultado:** mudança que passe a formatar precisa cobrir `float` grande, notação
  científica e o caso `0.1 + 0.2`.
- **Flag `resultado_mostrado`:** toda função nova que escreve no visor decide o que fazer com ela? Se
  esquecer, o comportamento "digitar depois do igual" quebra de forma sutil.

## Pilar 2 — Robustez

- **`except:` pelado** — o diff introduziu um? Captura `KeyboardInterrupt` e `SystemExit` junto com os
  erros reais. Aponte `except Exception:` ou os tipos específicos.
- **Exceção não tratada em handler de botão** derruba o callback e deixa a janela viva mas inerte, sem
  feedback nenhum ao usuário. Todo `command=` novo precisa de tratamento.
- **Trabalho demorado no handler** trava a janela inteira (Tkinter é single-threaded). Se o diff
  introduziu I/O, rede ou cálculo pesado no callback, aponte o padrão correto:
  `threading.Thread(daemon=True)` + `janela.after(0, callback)` para voltar à UI.
- **Chamada de widget fora da thread da UI** é erro silencioso e intermitente no Tkinter. Se apareceu
  `threading` no diff, verifique que nenhum `entrada.insert`/`configure` acontece na thread de trabalho.

## Pilar 3 — TDD (obrigatório neste repo)

- **Código de produção novo sem teste correspondente?** Viola a regra inegociável do `CLAUDE.md`.
  Reporte — é achado de review, não detalhe de estilo.
- **O teste tem cabeçalho SDD** explicando contrato e porquê, ou é assert solto?
- **O nome descreve comportamento** (`test_deve_<resultado>_quando_<condição>`) ou detalhe interno?
- **Mock apareceu?** Não deveria: `avaliar()` é pura. Mock aqui é sinal de que a regra foi para o lugar
  errado — provavelmente para dentro da UI.
- **Teste que não falharia** se a implementação fosse removida.

## Pilar 4 — Manutenibilidade

- **Closure em laço:** botão criado dentro de `for` usa o argumento default (`lambda t=texto:`)? Sem ele,
  todos os botões chamam com o valor da última iteração — bug clássico e difícil de ver.
- **Global novo:** o diff acrescentou variável global? Já há três (`resultado_mostrado`, `entrada`,
  `janela`). Cada nova aumenta o acoplamento; questione se não cabe parâmetro.
- **Duplicação de literal:** cores (`#2c3e50`, `#8e44ad`…) e fontes estão repetidas inline. Se o diff
  adiciona mais uma cópia, sugira a constante — mas sem transformar isso em refatoração geral não pedida.
- **Consistência com o arquivo:** o projeto é procedural, em português, sem classes. Código novo em outro
  paradigma no meio do arquivo é pior que código consistente e imperfeito.

## Pilar 5 — Dependências e escopo

- **Dependência externa nova para RODAR** (`import` fora da stdlib, entrada no `requirements.txt`)? O
  `CLAUDE.md` define o app como **stdlib-only**. Dependência de desenvolvimento vai em
  `requirements-dev.txt` — confundir os dois quebra a característica do projeto.
- **Reescrita estrutural não pedida** (virar classe, MVC, trocar por CustomTkinter/PyQt)? É projeto de
  aprendizado — mudança de arquitetura precisa ser pedida, não sugerida no meio de um fix.

## Pilar 6 — Usabilidade

- Feedback de erro chega ao usuário (hoje: a palavra `Erro` no visor) ou o diff introduziu falha silenciosa?
- Widget novo cabe na janela fixa de `300x420`? Ela é `resizable(False, False)` — o que não coube, sumiu.
- Contraste do texto sobre o fundo do botão continua legível?

## Formato da resposta

- Nada de micro-otimização irrelevante.
- Para cada problema: **arquivo e linha**, impacto, e o código refatorado. Ordene por severidade —
  correção do cálculo e ampliação da superfície do `eval` vêm primeiro.
- **Apenas revise e reporte. Não aplique as correções** sem ordem explícita.

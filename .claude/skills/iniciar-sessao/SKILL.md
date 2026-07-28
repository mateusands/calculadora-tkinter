---
name: iniciar-sessao
description: Inicializa a sessão de trabalho na calculadora Tkinter — lê o CLAUDE.md, o estado do git e as pendências da última sessão, em modo somente leitura, e confirma o alinhamento de escopo antes de qualquer código. Use no começo de cada sessão.
---

# Inicialização de Sessão — calculadora Tkinter

App de desktop em **Python + Tkinter puro**, sem dependências para rodar, com suíte `pytest` da lógica
de cálculo (`src/expressao.py`).
A fonte da verdade é **o código**.

Antes de qualquer ação, execute os passos de leitura abaixo:

1. **Leia o `CLAUDE.md` da raiz** — propósito, stack, como o código está organizado e, principalmente,
   as seções **"Como o cálculo é avaliado"** (allowlist do `ast`, visor editável) e **"Armadilhas
   ativas"** (formatação do resultado, estado global, sem atalho de teclado, sem validação na digitação).

2. **Leia a última sessão**, se houver: `.claude/sessions/` (arquivo mais recente).

3. **Levante o estado real do git** (somente leitura):
   ```bash
   git status --short && git branch --show-current && git log --oneline -10
   ```

4. **Leia os dois arquivos inteiros.** `src/expressao.py` (a regra, pura) e `src/calculadora.py` (a UI).
   São pequenos e cabem no contexto sem esforço.

5. **MODO SOMENTE LEITURA:** é proibido alterar código, criar ou apagar arquivo nesta etapa.

## Gates que valem nesta sessão

Confirme explicitamente que estão ativos:

- **Stdlib pura para RODAR.** Nada de dependência externa no `requirements.txt` sem pedido explícito —
  é característica do projeto. `pytest` fica em `requirements-dev.txt`, separado justamente por isso.
- **Sem reescrita estrutural não pedida.** É projeto de aprendizado de GUI; virar classes, MVC ou trocar
  o toolkit é decisão do dono, não melhoria a ser aplicada de passagem.
- **SDD + BDD + TDD obrigatório** — spec no topo do teste → `test_deve_<resultado>_quando_<condição>` →
  teste vermelho → código. A suíte roda com `pytest`.
- **Regra nova vai para `expressao.py`.** `calculadora.py` não é importável sem abrir a janela, então
  nada testável deve ir para lá.
- **Verde não basta** — a suíte cobre o cálculo, não a UI. Não anuncie "testado" sem ter aberto o app.
- **Tk do sistema é pré-requisito.** No Linux, `import tkinter` falha sem o pacote `tk` instalado.
- **Sem commit/push sem ordem explícita.**

## O que responder ao usuário

Retorno **curto**: branch atual, se o working tree está limpo, o que vamos mexer, e se havia pendência da
sessão anterior. Confirme numa frase que os gates acima estão ativos.

---
name: finalizar-sessao
description: Encerra a sessão de trabalho na calculadora Tkinter — gera o relatório da sessão em .claude/sessions/ e atualiza o CLAUDE.md se algo que ele afirma mudou. Use ao final de cada sessão.
---

# Encerramento de Sessão — calculadora Tkinter

O objetivo agora **não é codar**, e sim consolidar o que a sessão mudou.

## 1. Relatório da sessão

- Crie `.claude/sessions/YYYY-MM-DD.md` (data de hoje). Se já existir arquivo com a data de hoje,
  **acrescente** uma seção em vez de sobrescrever.
- Conteúdo exigido:
  - **O que foi feito** — o que mudou em `src/calculadora.py`.
  - **Decisões técnicas não-óbvias** — e o porquê.
  - **Validação manual** — quais casos do roteiro de `/rodar-local` você realmente executou. Se rodou 4
    dos 12, escreva 4. Não arredonde para cima.
  - **Pendências** — explícitas o bastante para retomar sem contexto.
  - **Estado do git** — branch, se ficou coisa não commitada.

> `.claude/sessions/` é **gitignorado** — caderno de bordo local, não documentação do repo.

## 2. Atualização do CLAUDE.md

Avalie se a sessão mudou algo que o `CLAUDE.md` afirma. Gatilhos:

- **Armadilha resolvida** — trocou o `eval` por um avaliador seguro? Corrigiu o `except:` pelado? Passou
  a formatar o resultado? **Remova o item da seção "Armadilhas ativas"**. Documento que descreve bug já
  corrigido induz o próximo leitor ao erro.
- **Armadilha nova descoberta** — acrescente. É o conteúdo mais valioso do arquivo.
- **Dependência introduzida** — o `CLAUDE.md` afirma "zero dependências externas" em três lugares
  (stack, estrutura, regras). Se isso mudou, atualize todos.
- **Módulo virou importável** (`if __name__ == "__main__":` + `main()`) — isso destrava teste
  automatizado; o arquivo afirma o contrário hoje. Atualize e registre que a suíte passou a ser possível.
- Mudança na estrutura de arquivos.

## 3. Validação final

**Primeiro a suíte** — e relate o resultado real:

```bash
pytest
```

Se houve código de produção nesta sessão, houve teste vermelho antes? Se não, a regra do `CLAUDE.md`
foi quebrada — registre no relatório em vez de esconder.

**Depois o app**, porque a suíte não cobre a UI:

```bash
python src/calculadora.py
```

No mínimo: operações básicas, divisão por zero, ponto duplicado, operador solto, e o comportamento de
digitar logo após um resultado. **Relate o que de fato testou** — e o que não deu para testar.

## O que responder ao usuário

1. Caminho do relatório gerado.
2. Se o `CLAUDE.md` foi atualizado, e o que mudou (ou que nada foi necessário).
3. O que foi validado manualmente e o que ficou de fora.
4. **Não commite nem faça push** — só quando o dono mandar.

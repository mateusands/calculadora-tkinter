"""Avaliação da expressão do visor — lógica pura, sem Tkinter.

Separado de `calculadora.py` porque aquele módulo cria a janela em nível de
módulo: importá-lo abre a UI e bloqueia no `mainloop()`. Aqui a regra fica
testável isolada, sem abrir janela.

A avaliação NÃO usa `eval`. O visor é um `Entry` comum, editável: o usuário
pode clicar nele, digitar e colar (Ctrl+V) o que quiser — não são só os botões
que alimentam o campo. Com `eval`, qualquer texto colado ali seria executado
como Python. Por isso a expressão é lida com `ast.parse` e percorrida com uma
allowlist de nós: só número, as quatro operações e sinal unário. Nada é
executado — os operadores são aplicados por `operator`, um a um.

Recusar `**` também fecha o congelamento da janela: `9**9**9` roda por tempo
indefinido na thread do `mainloop`, sem cancelamento possível.
"""

import ast
import operator

RESULTADO_ERRO = "Erro"

OPERADORES = ("+", "-", "*", "/")

# Allowlist: fora daqui, nada é aceito.
_OPERACOES_BINARIAS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

_OPERACOES_UNARIAS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def avaliar(expressao: str) -> str:
    """Avalia a expressão do visor e devolve o texto a exibir.

    Devolve `RESULTADO_ERRO` para qualquer expressão inválida — a calculadora
    nunca propaga exceção para a UI, porque o visor é o único canal de erro.
    Expressão que não seja aritmética das quatro operações também é inválida.
    """
    try:
        arvore = ast.parse(expressao, mode="eval")
        return str(_calcular(arvore.body))
    except Exception:
        return RESULTADO_ERRO


def deve_reiniciar(visor: str, tecla: str) -> bool:
    """Com um resultado no visor, decide se a próxima tecla começa expressão nova.

    Dígito e ponto reiniciam (quem digita `5` depois de `4` quer `5`, não `45`).
    Operador continua a conta a partir do resultado — é o encadeamento. Resultado
    que não é número ("Erro") nunca é encadeável: reiniciar sempre.
    """
    if tecla not in OPERADORES:
        return True
    return not _e_numero(visor)


def apagar_ultimo(visor: str) -> str:
    """Devolve o visor sem o último caractere — é a regra do botão ⌫.

    Diferente do "C", que zera tudo: aqui só o último toque é desfeito, para
    corrigir um dígito sem refazer a conta inteira.

    "Erro" é o caso especial: não é expressão, é mensagem. Apagar uma letra
    deixaria "Err" no visor, que não é nada — então o visor inteiro é limpo.
    """
    if visor == RESULTADO_ERRO:
        return ""
    return visor[:-1]


def _calcular(no: ast.AST) -> float:
    """Percorre a árvore recusando tudo que não seja aritmética.

    Nada de `eval`/`exec`: cada nó é conferido contra a allowlist antes de o
    operador correspondente ser aplicado.
    """
    if isinstance(no, ast.Constant):
        # `bool` é subclasse de `int` — `True+1` seria aceito sem esta guarda.
        if isinstance(no.value, bool) or not isinstance(no.value, (int, float)):
            raise ValueError(f"constante não numérica: {no.value!r}")
        return no.value

    if isinstance(no, ast.BinOp) and type(no.op) in _OPERACOES_BINARIAS:
        operacao = _OPERACOES_BINARIAS[type(no.op)]
        return operacao(_calcular(no.left), _calcular(no.right))

    if isinstance(no, ast.UnaryOp) and type(no.op) in _OPERACOES_UNARIAS:
        operacao = _OPERACOES_UNARIAS[type(no.op)]
        return operacao(_calcular(no.operand))

    raise ValueError(f"expressão não é aritmética: {type(no).__name__}")


def _e_numero(texto: str) -> bool:
    try:
        float(texto)
        return True
    except ValueError:
        return False

"""Avaliação da expressão do visor — lógica pura, sem Tkinter.

Separado de `calculadora.py` porque aquele módulo cria a janela em nível de
módulo: importá-lo abre a UI e bloqueia no `mainloop()`. Aqui a regra fica
testável isolada, sem abrir janela.

⚠️ A avaliação continua usando `eval`, que executa Python arbitrário e não só
aritmética. Hoje a exposição é baixa porque só os botões alimentam o visor. Se
a entrada passar a ser livre (teclado físico, colar do clipboard, histórico
editável), troque por um avaliador com allowlist (`ast.parse`) ANTES de liberar
a entrada.
"""

RESULTADO_ERRO = "Erro"


def avaliar(expressao: str) -> str:
    """Avalia a expressão do visor e devolve o texto a exibir.

    Devolve `RESULTADO_ERRO` para qualquer expressão inválida — a calculadora
    nunca propaga exceção para a UI, porque o visor é o único canal de erro.
    """
    try:
        return str(eval(expressao))
    except Exception:
        return RESULTADO_ERRO

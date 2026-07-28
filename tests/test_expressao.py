"""
SDD — Especificação: avaliação da expressão do visor

CONTRATO
  `avaliar(expressao)` recebe o texto do visor e devolve o texto a exibir.
  NUNCA levanta exceção: expressão inválida vira a string `"Erro"`, porque o
  visor é o único canal de erro da calculadora (não há messagebox nem log).

POR QUE EXISTE
  A regra vivia dentro de `calcular()`, em `calculadora.py`, junto do código de
  UI — e aquele módulo cria a janela em nível de módulo, então importá-lo abre a
  interface e bloqueia no `mainloop()`. Era impossível testar. A extração para
  este módulo é o que destrava o TDD no projeto.

REGRA DE NEGÓCIO
  - O botão rotulado "X" já chega aqui como "*" (a tradução é da camada de UI).
  - Divisão devolve float: "4/2" resulta em "2.0", não "2". É o comportamento
    atual, herdado do `eval`, e está documentado como pendência no CLAUDE.md.
  - Qualquer erro (sintaxe, divisão por zero, nome desconhecido) vira "Erro".
  - SÓ ARITMÉTICA das quatro operações (+ - * /), com sinal unário. Qualquer
    outra construção Python — chamada de função, comparação, potência, texto,
    nome — é expressão inválida e vira "Erro". A calculadora não é um
    interpretador: o visor é um campo de texto editável, então tudo o que o
    usuário digitar ou colar chega até aqui.
"""

import pytest

from expressao import RESULTADO_ERRO, avaliar


class TestOperacoesBasicas:
    @pytest.mark.parametrize(
        "expressao, esperado",
        [
            ("2+3", "5"),
            ("9-4", "5"),
            ("6*7", "42"),
            ("10-20", "-10"),
            ("2+3*4", "14"),  # precedência preservada
            ("1.5+2.5", "4.0"),
        ],
    )
    def test_deve_calcular_quando_a_expressao_e_valida(self, expressao, esperado):
        assert avaliar(expressao) == esperado

    def test_deve_devolver_float_na_divisao_exata(self):
        # Comportamento atual conhecido: o visor mostra "2.0", não "2".
        assert avaliar("8/2") == "4.0"


class TestTratamentoDeErro:
    @pytest.mark.parametrize(
        "expressao, motivo",
        [
            ("5/0", "divisão por zero"),
            ("1.2.3", "ponto decimal duplicado"),
            ("7+", "operador sem operando"),
            ("", "expressão vazia"),
            ("*5", "começa com operador"),
            ("2++", "operadores soltos no fim"),
            ("abc", "nome desconhecido"),
        ],
    )
    def test_deve_devolver_erro_quando_a_expressao_e_invalida(self, expressao, motivo):
        assert avaliar(expressao) == RESULTADO_ERRO, f"deveria falhar: {motivo}"

    def test_nunca_deve_levantar_excecao(self):
        # O visor é o único canal de erro — exceção aqui derrubaria o callback
        # do botão e deixaria a janela viva porém inerte, sem feedback nenhum.
        # `exit()` está na lista de propósito: ele levanta SystemExit, que NÃO é
        # subclasse de Exception e por isso escapa de um `except Exception:`.
        for entrada in ["", "((((", "1/0", "None+1", "]" * 50, "9" * 500, "exit()"]:
            resultado = avaliar(entrada)
            assert isinstance(resultado, str)


class TestApenasAritmetica:
    """O visor é editável: o usuário pode digitar e colar texto livre nele.

    Tudo o que não for as quatro operações precisa virar "Erro" ANTES de ser
    executado — senão a calculadora vira um interpretador Python.
    """

    @pytest.mark.parametrize(
        "expressao, motivo",
        [
            ("__import__('os').getcwd()", "chamada de função embutida"),
            ("exit()", "encerra o processo (SystemExit)"),
            ("open('/etc/passwd').read()", "acesso a arquivo"),
            ("1==1", "comparação — a calculadora não tem booleano"),
            ("2**32", "potência não é operação da calculadora"),
            ("7//2", "divisão inteira não é operação da calculadora"),
            ("7%2", "resto não é operação da calculadora"),
            ("'ab'*3", "texto, não número"),
            ("True", "booleano, não número"),
            ("None", "nome embutido"),
            ("[1,2][0]", "lista e indexação"),
            ("(lambda: 1)()", "função anônima"),
        ],
    )
    def test_deve_devolver_erro_quando_a_expressao_nao_e_aritmetica(self, expressao, motivo):
        assert avaliar(expressao) == RESULTADO_ERRO, f"deveria recusar: {motivo}"

    def test_nao_deve_executar_efeito_colateral(self, tmp_path):
        # Se a expressão for executada de fato, o arquivo aparece — e aí o visor
        # deixou de ser uma calculadora e virou execução de código arbitrário.
        alvo = tmp_path / "invadido.txt"
        avaliar(f"open({str(alvo)!r}, 'w').write('x')")
        assert not alvo.exists(), "a expressão foi executada de verdade"

    def test_deve_devolver_erro_sem_travar_em_calculo_explosivo(self):
        # `9**9**9` com `eval` congela a janela inteira (Tkinter é single-thread)
        # e não há como cancelar. Recusar a potência resolve na origem.
        assert avaliar("9**9**9") == RESULTADO_ERRO


class TestContinuidadeDoResultado:
    def test_deve_permitir_encadear_o_resultado_anterior(self):
        # Fluxo real: 2+2 = 4, depois o usuário aperta "+3" e "=".
        primeiro = avaliar("2+2")
        assert avaliar(f"{primeiro}+3") == "7"

    def test_deve_devolver_erro_ao_encadear_a_partir_de_um_erro(self):
        # Se o visor mostra "Erro" e o usuário insiste no "=", continua "Erro"
        # (a UI limpa o visor no próximo dígito, mas o "=" repetido cai aqui).
        assert avaliar(RESULTADO_ERRO) == RESULTADO_ERRO
"""§5.12 — MarcadorDecisaoAberta.

"Tornar visivel que um valor ainda nao foi decidido, em vez de deixar um chute
virar verdade."

Anatomia: o glifo ⚠️ seguido do texto em --tinta-secundaria, SEM cor de alerta
e SEM caixa. Na faixa de premissas: `rampa e sazonalidade ⚠️ nao aplicadas`.

REGRAS:
  - um valor em aberto NUNCA e substituido por um numero plausivel no codigo.
    Ele vive num unico modulo parametros.py com o valor marcado como
    provisorio, e a tela mostra o marcador
  - o marcador e discreto o bastante para nao alarmar o cliente, e explicito
    o bastante para o vendedor saber que aquele item esta pendente
  - quando a decisao for tomada, o marcador SOME junto com a substituicao do
    valor em parametros.py. Nao ha outro lugar para mexer

O glifo ⚠️ e a unica excecao a regra "sem emoji" (D2), porque o §5.12 o
especifica literalmente.
"""

from __future__ import annotations

from src import parametros as P

GLIFO = "⚠️"


def inline(texto: str) -> str:
    """'⚠️ nao aplicadas' — para dentro de uma frase corrida."""
    return f'<span class="st-proc">{GLIFO} {texto}</span>'


def chip(texto: str) -> str:
    """Chip com borda TRACEJADA, sem cor de alerta e sem caixa colorida."""
    return f'<span class="st-chip st-chip--aberto">{GLIFO} {texto}</span>'


def decisoes_abertas_ativas() -> list[tuple[str, str]]:
    """Quais decisoes da §10 estao abertas AGORA, lidas de parametros.py.

    Nao ha lista fixa: a funcao consulta os parametros, de modo que preencher
    um valor em parametros.py faz o marcador desaparecer sozinho — sem
    ninguem precisar lembrar de apagar o marcador em outro arquivo.
    """
    abertas: list[tuple[str, str]] = []

    if P.PISO_PRECO is None:
        abertas.append(("F", "piso de preço não definido — sem validação de piso"))
    if P.CODIGOS_COBERTURA_97 is None:
        abertas.append(
            ("G", "número de códigos não definido — bloco de investimento ausente")
        )
    if not P.rampa_aplicada():
        abertas.append(("I", "rampa dos 3 primeiros meses não parametrizada"))
    if not P.sazonalidade_aplicada():
        abertas.append(("J", "curva de sazonalidade não parametrizada"))
    if P.LIMIAR_IDADE_DIAS is None:
        abertas.append(("L", "idade de recoleta não definida — idade exibida em dias"))

    return abertas


def texto_premissas_rampa() -> str | None:
    """O item da faixa de premissas para as decisoes I e J.

    §5.6: "Quando um coeficiente e placeholder, o item carrega ⚠️ e o marcador
    da §5.12." A ausencia e DECLARADA — curva plana nao e aplicada em silencio.
    """
    if P.rampa_aplicada() and P.sazonalidade_aplicada():
        return None
    if not P.rampa_aplicada() and not P.sazonalidade_aplicada():
        return f"rampa e sazonalidade {GLIFO} não aplicadas"
    if not P.rampa_aplicada():
        return f"rampa {GLIFO} não aplicada"
    return f"sazonalidade {GLIFO} não aplicada"

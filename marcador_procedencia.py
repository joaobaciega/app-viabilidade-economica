"""§5.7 — Marcador de procedencia. Todo numero declara de onde veio (P5).

"A tela mistura naturezas muito diferentes de numero, e o cliente nao tem como
distinguir. Quando o gerente aponta um numero e pergunta 'de onde saiu isso?',
a resposta JA TEM QUE ESTAR NA TELA."

    ◆ carteira    Catalogo — dado proprio da Suicatech
    ▪ premissa    Digitado — informado na hora
    ƒ calculado   Derivado por formula
    ≈ derivado    Calculado, subclasse — derivacao por proporcao, NAO medicao
    ⬡ coletado    Coletado de fonte externa — NAO OCORRE na Tela 1

REGRAS:
  - os marcadores sao glifos MONOCROMATICOS em --tinta-secundaria, NUNCA cor.
    Cor esta gasta (§3.1.2), e o cliente le em angulo
  - o marcador NUNCA e o unico canal: cada um vem acompanhado da palavra

A distincao `◆ carteira` x `≈ derivado` no traseiro e OBRIGATORIA e nao e
preciosismo. Ela ataca o risco n. 1 do plano: se o 7% e o 13% do traseiro
forem apresentados com a mesma autoridade do 30% do dianteiro, o app esta
vendendo derivacao como medicao, e o erro so aparece no mes 3 do cliente.
"""

from __future__ import annotations

from typing import Literal

Natureza = Literal["carteira", "premissa", "calculado", "derivado", "coletado"]

_GLIFOS: dict[str, tuple[str, str]] = {
    "carteira": ("◆", "carteira"),
    "premissa": ("▪", "premissa"),
    "calculado": ("ƒ", "calculado"),
    "derivado": ("≈", "derivado"),
    "coletado": ("⬡", "coletado"),  # nao ocorre na Tela 1
}


def marcador(natureza: Natureza) -> str:
    """'◆ carteira' — glifo E palavra, sempre os dois."""
    glifo, palavra = _GLIFOS[natureza]
    return f'<span class="st-proc">{glifo} {palavra}</span>'


def de_origem(origem: str) -> str:
    """Traduz `parametros.Origem` no marcador correspondente.

    `carteira_medida` -> `◆ carteira`      (medido em 15+ concessionarias)
    `derivado`        -> `≈ derivado`      (proporcao, nao medicao)

    E aqui que a mitigacao do risco n. 1 vira pixel: o valor do traseiro
    pessimista e otimista NUNCA pode sair como `◆ carteira`.
    """
    return marcador("derivado" if origem == "derivado" else "carteira")


LEGENDA_DERIVADO = (
    "derivado do dianteiro na mesma proporção — não medido"
)

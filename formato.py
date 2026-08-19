"""Formatacao de numero e a traducao em escala humana (DESIGN.md §6.1.5).

Aritmetica pura. Nao importa streamlit.

Regra de centavos, que depende da NATUREZA do numero:
    agregado / projetado  ->  SEM centavos    R$ 141.480
    unitario / digitado   ->  COM centavos    R$ 197,90

Milhar sempre com ponto, decimal com virgula, prefixo "R$ " com espaco.

A traducao e o elemento mais importante da tela (§5.5, P2). Ela e verificada
pela intuicao do gerente em dois segundos, enquanto "R$ 1,2 milhao por ano" e
rejeitado pelo cerebro antes de ser avaliado.
"""

from __future__ import annotations

import math

# Sinal de menos tipografico (U+2212). Le melhor que hifen a 36px, e o
# resultado negativo e exibido COM o sinal, em tinta primaria, nunca em
# vermelho (DESIGN §5.5, §3.1.2).
MENOS = "−"


def _milhar(inteiro: int) -> str:
    """3000 -> '3.000'. Separador de milhar por ponto."""
    return f"{inteiro:,}".replace(",", ".")


def _arredonda_meio_para_cima(x: float) -> int:
    """Arredonda 0,5 para cima.

    round() do Python usa arredondamento bancario (round-half-even):
    round(2.5) == 2, o que produziria '2 a cada 10' para 25% de
    aproveitamento. Aqui meio arredonda para cima, como um leitor humano
    espera.
    """
    return math.floor(x + 0.5)


def inteiro(valor: float) -> str:
    """Quantidade sem casas: 3000.0 -> '3.000'."""
    return _milhar(int(_arredonda_meio_para_cima(valor)))


def moeda_agregada(valor: float) -> str:
    """Valor projetado ou agregado, SEM centavos: 141480.0 -> 'R$ 141.480'.

    DESIGN §6.1.5: sem centavos nos valores agregados. Centavos numa projecao
    de 12 meses fingem precisao que nao existe.
    """
    negativo = valor < 0
    n = int(_arredonda_meio_para_cima(abs(valor)))
    texto = f"R$ {_milhar(n)}"
    return f"{MENOS}{texto}" if negativo else texto


def moeda_unitaria(valor: float) -> str:
    """Valor unitario ou digitado, COM centavos: 197.9 -> 'R$ 197,90'."""
    negativo = valor < 0
    reais, centavos = divmod(round(abs(valor) * 100), 100)
    texto = f"R$ {_milhar(int(reais))},{int(centavos):02d}"
    return f"{MENOS}{texto}" if negativo else texto


def percentual(fracao: float, casas: int = 0) -> str:
    """0.30 -> '30%'. Inteiro por default; casas decimais com virgula."""
    valor = fracao * 100
    if casas == 0:
        return f"{int(_arredonda_meio_para_cima(valor))}%"
    return f"{valor:.{casas}f}".replace(".", ",") + "%"


def decimal(valor: float, casas: int = 1) -> str:
    """34.09 -> '34,1'. Usado na faixa do vendedor (carga por consultor)."""
    return f"{valor:.{casas}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# A traducao em escala humana (DESIGN §6.1.5, §5.5, plano §3.6)
# ---------------------------------------------------------------------------

SUFIXO_TRADUCAO = "carros que entram na oficina"


def traducao_por_passagem(fracao_dianteiro: float) -> str:
    """'3 a cada 10 carros que entram na oficina'.

    DESIGN §6.1.5: "A traducao arredonda para o inteiro mais proximo em base
    10: 30% -> '3 a cada 10'; 27% -> 'quase 3 a cada 10'; 34% -> '3 a cada
    10'. NUNCA '3,4 a cada 10' — o ganho de precisao e nulo e o custo de
    credibilidade e alto."

    A traducao e sempre POR PASSAGEM, nunca por consultor/dia: a traducao por
    consultor herda a ambiguidade da §1.3 do plano e pode errar por 10x.

    SUPOSICAO (docs/DIVERGENCIAS.md): o DESIGN da os tres exemplos acima mas
    nao define o limiar do "quase". Regra adotada: n = arredonda(fracao x 10);
    se fracao x 10 < n, prefixo "quase". Reproduz os tres exemplos. Meio
    arredonda para cima, logo 25% -> "quase 3 a cada 10".

    SUPOSICAO: o DESIGN nao diz o que exibir em 0%. Usado "nenhum a cada 10",
    porque "0 a cada 10" e lido em voz alta como "zero" e soa como
    impossibilidade, quando 0% e apenas o cenario de nao fazer nada (E2).
    """
    escala = fracao_dianteiro * 10
    n = _arredonda_meio_para_cima(escala)

    if n <= 0:
        return f"nenhum a cada 10 {SUFIXO_TRADUCAO}"

    quase = "quase " if escala < n else ""
    return f"{quase}{n} a cada 10 {SUFIXO_TRADUCAO}"


def traducao_curta(fracao_dianteiro: float) -> str:
    """Versao sem o sufixo, para a faixa de premissas e o PDF."""
    escala = fracao_dianteiro * 10
    n = _arredonda_meio_para_cima(escala)
    if n <= 0:
        return "nenhum a cada 10"
    quase = "quase " if escala < n else ""
    return f"{quase}{n} a cada 10"


# ---------------------------------------------------------------------------
# Totais derivados (DESIGN §5.1, §4 padrao de rotulo)
# ---------------------------------------------------------------------------


def total_derivado_passagens(passagens_por_ponto: float, pontos: int) -> str:
    """'-> 3.000 passagens por mes no total'.

    DESIGN §5.1: "Quando o multiplicador vale 1 (um ponto de venda), o
    derivado CONTINUA aparecendo. Sumir com ele quando o valor e trivial
    ensina o cliente a nao procura-lo quando deixa de ser."
    """
    total = passagens_por_ponto * pontos
    return f"→ {inteiro(total)} passagens por mês no total"


def total_derivado_consultores(consultores_por_ponto: float, pontos: int) -> str:
    """'-> 30 consultores no total'."""
    total = consultores_por_ponto * pontos
    return f"→ {inteiro(total)} consultores no total"


def total_derivado_palhetas(por_ponto: float, pontos: int) -> str:
    """'-> 200 palhetas por mes no total'."""
    total = por_ponto * pontos
    return f"→ {inteiro(total)} palhetas por mês no total"

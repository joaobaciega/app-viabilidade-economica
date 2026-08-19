"""T13 e T14 — traducao e formatacao (DESIGN §6.1.5).

Casos meus, nao da §11.3: a v5 especifica as duas regras mas nao as
transformou em caso-teste. Registrado em docs/DIVERGENCIAS.md.
"""

from __future__ import annotations

from testes.conftest import esperado
from src import formato


def test_T13_traducao_por_passagem() -> None:
    """30% -> "3 a cada 10"; 27% -> "quase 3"; 34% -> "3". NUNCA "3,4 a cada 10"."""
    e = esperado("T13")
    for fracao_texto, texto_esperado in e.items():
        fracao = float(fracao_texto)
        assert formato.traducao_por_passagem(fracao) == texto_esperado, (
            f"{fracao:.0%} deveria traduzir para {texto_esperado!r}"
        )


def test_T13_nunca_fracao_na_traducao() -> None:
    """"O ganho de precisao e nulo e o custo de credibilidade e alto.\""""
    for pp in range(0, 61):
        texto = formato.traducao_por_passagem(pp / 100)
        assert "," not in texto, f"{pp}% produziu fracao: {texto!r}"
        assert "." not in texto.split("a cada")[0], f"{pp}%: {texto!r}"


def test_T13_zero_nao_le_como_impossibilidade() -> None:
    """"0 a cada 10" e lido em voz alta como "zero"."""
    assert formato.traducao_por_passagem(0.0).startswith("nenhum a cada 10")
    assert not formato.traducao_por_passagem(0.0).startswith("0 ")


def test_T13_traducao_e_por_passagem_nunca_por_consultor() -> None:
    """§6.1.5 / plano §3.6: a traducao por consultor herda a ambiguidade da
    §1.3 e pode errar por 10x. Ela nao existe no codigo."""
    assert "consultor" not in formato.SUFIXO_TRADUCAO
    assert formato.SUFIXO_TRADUCAO == "carros que entram na oficina"


def test_T14_formatacao_de_moeda() -> None:
    e = esperado("T14")
    assert formato.moeda_agregada(141480.0) == e["agregado_141480"]
    assert formato.moeda_agregada(-38520.0) == e["agregado_negativo"]
    assert formato.moeda_unitaria(197.90) == e["unitario_197_9"]
    assert formato.moeda_unitaria(113.0) == e["unitario_113"]
    assert formato.inteiro(3000) == e["inteiro_3000"]


def test_T14_agregado_sem_centavos_unitario_com_centavos() -> None:
    """A regra depende da NATUREZA do numero, nao do tamanho da fonte."""
    assert "," not in formato.moeda_agregada(11790.0)
    assert formato.moeda_unitaria(11790.0).endswith(",00")


def test_T14_milhar_com_ponto() -> None:
    assert formato.moeda_agregada(1234567.0) == "R$ 1.234.567"
    assert formato.inteiro(1000) == "1.000"


def test_T14_nunca_abrevia_moeda() -> None:
    """Abreviar um numero que o cliente vai conferir e convite a desconfianca."""
    for valor in (1_200_000.0, 141_480.0, 999.0):
        texto = formato.moeda_agregada(valor)
        for abreviacao in ("mi", "mil", "k", "M"):
            assert abreviacao not in texto, f"{valor} abreviou: {texto!r}"


def test_T14_arredondamento_meio_para_cima() -> None:
    """round() do Python e bancario: round(2.5) == 2. Aqui meio sobe."""
    assert formato.inteiro(2.5) == "3"
    assert formato.inteiro(3.5) == "4"
    assert formato.percentual(0.255, casas=0) == "26%"


def test_percentual() -> None:
    assert formato.percentual(0.30) == "30%"
    assert formato.percentual(0.0) == "0%"
    assert formato.percentual(0.105, casas=1) == "10,5%"


def test_decimal_usa_virgula() -> None:
    assert formato.decimal(34.09) == "34,1"
    assert formato.decimal(4.545) == "4,5"

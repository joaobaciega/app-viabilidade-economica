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


def test_markup_percentual_e_o_acrescimo_sobre_o_custo() -> None:
    """D27 — o exemplo que o cliente deu: "ao invés de 2x colocar 100%".

    O mark up é o **acréscimo** sobre o custo, não a razão. Vender a duas vezes
    o custo é 100%, e trocar uma leitura pela outra **dobra o número** — é a
    diferença do próprio custo.
    """
    assert formato.markup_percentual(2.0) == "100%"
    assert formato.markup_percentual(1.0) == "0%"  # vende ao preço de custo
    assert formato.markup_percentual(3.0) == "200%"
    assert formato.markup_percentual(1.5) == "50%"

    # T1: faturamento 29.961 ÷ custo 14.391 = 2,082 -> 108%
    assert formato.markup_percentual(29961 / 14391) == "108%"


def test_markup_percentual_nao_e_margem_percentual() -> None:
    """As duas contas dão números diferentes, e a troca é o erro provável.

    mark up  = (faturamento − custo) ÷ **custo**
    margem % = (faturamento − custo) ÷ **faturamento**

    No mesmo cenário do T1 uma dá 108% e a outra 52%. É por isso que o cartão
    que mostra este número declara a conta embaixo dele (§4) — sem essa linha,
    "108%" ao lado de duas colunas de reais lê como margem.
    """
    faturamento, custo = 29961.0, 14391.0
    markup = formato.markup_percentual(faturamento / custo)
    margem = formato.percentual((faturamento - custo) / faturamento)

    assert markup == "108%"
    assert margem == "52%"
    assert markup != margem


def test_markup_percentual_abaixo_do_custo_sai_negativo() -> None:
    """Vender abaixo do custo é possível (plano §1.1) e não é escondido."""
    assert formato.markup_percentual(0.9) == "-10%"


def test_T14_moeda_curta_espelha_o_eixo_da_tela() -> None:
    """D24: `moeda_curta` e o gemeo do `labelExpr` do eixo Y do gráfico.

    Os DOIS limiares são os mesmos, e é isso que impede o PDF e a tela de
    rotularem o mesmo tick de dois jeitos na frente do cliente:

        >= 1.000.000  ->  'R$ X,X mi'   (uma casa)
        >= 1.000      ->  'R$ X mil'    (sem casa)
        abaixo disso  ->  'R$ X'

    Mexer aqui obriga a mexer em `grafico_sensibilidade._eixo_y`.
    """
    assert formato.moeda_curta(141_480) == "R$ 141 mil"
    assert formato.moeda_curta(1_241_000) == "R$ 1,2 mi"
    assert formato.moeda_curta(999) == "R$ 999"
    assert formato.moeda_curta(1_000) == "R$ 1 mil"
    assert formato.moeda_curta(1_000_000) == "R$ 1,0 mi"
    assert formato.moeda_curta(-50_000) == "−R$ 50 mil"

    # E o `labelExpr` da tela precisa continuar com os mesmos dois limiares.
    from pathlib import Path

    fonte = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "componentes"
        / "grafico_sensibilidade.py"
    ).read_text(encoding="utf-8")
    assert "1000000" in fonte and "' mi'" in fonte
    assert "' mil'" in fonte


def test_T14_abreviacao_de_moeda_e_so_para_eixo() -> None:
    """§6.1.5: abreviar moeda continua PROIBIDO em texto.

    `moeda_curta` existe para o tick do eixo, que concorre por espaço com o
    desenho. Nenhum rótulo, cartão, linha de resultado ou célula de tabela
    pode chamá-la — e este teste é onde isso está travado.
    """
    import ast
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[1]
    permitidos = {
        # `rotulos_do_eixo` é o único chamador: ele monta os ticks do eixo Y da
        # curva — os mesmos na tela e no PDF desde D28 — e cai para o número
        # inteiro quando a forma curta repete.
        "apresentacao.py",
        "formato.py",
    }

    culpados: list[str] = []
    for caminho in (raiz / "src").rglob("*.py"):
        if caminho.name in permitidos:
            continue
        arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Attribute) and no.attr == "moeda_curta":
                culpados.append(f"{caminho.name}:{no.lineno}")
            elif isinstance(no, ast.Name) and no.id == "moeda_curta":
                culpados.append(f"{caminho.name}:{no.lineno}")

    assert not culpados, (
        "moeda_curta abrevia, e abreviar moeda em texto é proibido "
        f"(§6.1.5): {culpados}"
    )


def test_venda_da_unidade_concorda_com_a_unidade_declarada() -> None:
    """D23: "por par vendido" e "por unidade vendida" concordam em genero.

    A frase e escrita nos DOIS lugares do bloco de cashback — o titulo do grupo
    e o subtotal —, e escreve-la a mao nos dois e como um deles vira "por
    unidade vendido".
    """
    from src import parametros as P

    assert formato.venda_da_unidade("par") == "por par vendido"
    assert formato.venda_da_unidade("unitario") == "por unidade vendida"

    # E vale para toda unidade DECLARADA no catalogo (§5.13 / V3), nao so para
    # as duas escritas acima.
    for categoria in P.CATEGORIAS:
        frase = formato.venda_da_unidade(categoria.unidade)
        assert frase.startswith("por ")
        assert "vendido" in frase or "vendida" in frase


def test_total_derivado_de_cashback_usa_a_seta_dos_outros_derivados() -> None:
    """§5.1: o chip de total derivado tem uma forma so na tela inteira."""
    texto = formato.total_derivado_cashback(15.0, "par")
    assert texto == "→ R$ 15,00 no total, por par vendido"
    assert texto.startswith("→ ")

    # Centavos aparecem: e valor UNITARIO, por venda (§6.1.5).
    assert formato.total_derivado_cashback(5.5, "unitario") == (
        "→ R$ 5,50 no total, por unidade vendida"
    )

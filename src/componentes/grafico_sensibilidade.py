"""§5.11 — Grafico de sensibilidade, e o gemeo em tabela.

"Recuperar parte do efeito perdido do arraste. Como o servidor calcula tudo de
uma vez, A CURVA INTEIRA APARECE com marcador na posicao atual — o cliente ve o
intervalo completo SEM INTERAGIR."

Forma: serie unica, curva de resposta. SEM LEGENDA — serie unica, o titulo ja
diz o que esta plotado.

Especificacao de marcas (§5.11):
  curva            mark_line, 2px, ponta e juncao arredondadas, --tinta-primaria
  area             NENHUMA. Um wash a 10% desaparece a um metro em angulo sob
                   luz de showroom e nao acrescenta leitura
  marcador atual   mark_point, r = 8 (16px de diametro), --marca-vermelho,
                   com anel de 2px na cor da superficie
  rotulo direto    EXATAMENTE UM, junto ao marcador, com o valor anual.
                   A menos de 80px da borda direita, vira para a esquerda
  marcas de preset tres mark_rule verticais em 20/30/40%, 1px SOLIDA --traco.
                   NUNCA tracejadas
  linha do zero    horizontal em y=0, 1px solida --tinta-secundaria, rotulada
                   R$ 0. DESENHADA APENAS quando o dominio de y cruza o zero
  grade            horizontal, 1px solida --grade. SEM GRADE VERTICAL — as
                   marcas dos presets ja ocupam esse canal
  eixos            --tinta-secundaria 15px. Y com no maximo 4 ticks, compactados
  altura           300px = 260 de plot + ~40 de faixa de eixo

REGRAS:
  - UM EIXO Y SO. Nunca dois
  - o dominio de X e IDENTICO ao do slider, lido do mesmo
    parametros.SLIDER_DOMINIO, para que o marcador nunca saia do plot
  - a curva plota EXATAMENTE A MESMA GRANDEZA DA MANCHETE (margem incremental
    anual). Se divergirem, a tela se contradiz na frente do cliente
  - so o traseiro fica congelado; ao variar o dianteiro, o traseiro NAO
    acompanha. O subtitulo diz isso literalmente
  - SEM HOVER, SEM TOOLTIP. Nao existe hover em tablet, e o marcador e
    permanente. Nenhuma camada abaixo declara `tooltip`
  - GEMEO EM TABELA, OBRIGATORIO — o canal de reserva que substitui o tooltip

Vermelho: o marcador e o UNICO uso de --marca-vermelho aqui, e e um dos dois
lugares que a §3.1 autoriza no app inteiro. A CURVA E PRETA.
"""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src import formato
from src import parametros as P
from src.calculo import (
    Entradas,
    Resultado,
    curva_sensibilidade,
    curvas_comparadas,
    traseiro_entra_na_conta,
)
from src.css import (
    GRADE,
    MARCA_VERMELHO,
    SUPERFICIE,
    T_DERIVADO,
    T_PREMISSAS,
    T_ROTULO,
    TINTA_PRIMARIA,
    TINTA_SECUNDARIA,
    TRACO,
)

ALTURA_PLOT = 260  # + faixa de eixo = 300px de conteiner (css.py garante o resto)

# `size` no Altair e AREA em px². r = 8 -> pi * 8² ~= 201.
AREA_MARCADOR = 201

# Fracao do eixo a partir da qual o rotulo direto vira para a esquerda,
# equivalente aos 80px da borda direita da §5.11.
LIMIAR_VIRA_ROTULO = 0.82


def _texto_do_titulo(e: Entradas, duas_linhas: bool) -> tuple[str, str]:
    """O subtitulo DECLARA o que esta congelado e em que valor."""
    if duas_linhas:
        titulo = "Margem de contribuição anual: com refil × só com a palheta original"
    else:
        titulo = "Margem incremental anual por aproveitamento dianteiro"

    if traseiro_entra_na_conta(e):
        congelado = (
            f"traseiro fixo em {formato.percentual(e.aproveitamento_traseiro)}"
        )
    else:
        congelado = "traseiro fora da conta"

    subtitulo = f"{congelado} · demais premissas conforme a faixa acima"
    if duas_linhas:
        subtitulo = "a distância entre as duas linhas é o incremental · " + subtitulo
    return titulo, subtitulo


def _eixo_x(lo: int, hi: int) -> alt.X:
    return alt.X(
        "aproveitamento:Q",
        scale=alt.Scale(domain=[lo, hi], nice=False),
        axis=alt.Axis(
            title=None,
            labelExpr="datum.value + '%'",
            values=list(range(lo, hi + 1, 10)),
            labelColor=TINTA_SECUNDARIA,
            labelFontSize=T_PREMISSAS,
            tickColor=TRACO,
            domainColor=TRACO,
            grid=False,
        ),
    )


def _eixo_y() -> alt.Y:
    return alt.Y(
        "anual:Q",
        axis=alt.Axis(
            title=None,
            tickCount=4,
            labelExpr=(
                "abs(datum.value) >= 1000000"
                " ? 'R$ ' + format(datum.value/1000000, '.1f') + ' mi'"
                " : abs(datum.value) >= 1000"
                " ? 'R$ ' + format(datum.value/1000, '.0f') + ' mil'"
                " : 'R$ ' + format(datum.value, '.0f')"
            ),
            labelColor=TINTA_SECUNDARIA,
            labelFontSize=T_PREMISSAS,
            gridColor=GRADE,
            gridDash=[],
            gridWidth=1,
            domainColor=TRACO,
            tickColor=TRACO,
        ),
    )


def grafico(e: Entradas, r: Resultado) -> None:
    """Desenha as curvas. NADA e desenhado no estado E1 (§6.1.6).

    DUAS LINHAS quando ha margem da palheta original (pedido do cliente,
    11/08/2026):

      1. margem anual TOTAL adotando o refil (preta, cheia)
      2. margem anual se ele continuar SO com a original (cinza, tracejada) —
         constante, porque nao depende do aproveitamento do refil

    A distancia entre elas e o incremental, que e a manchete. O cruzamento
    responde "a partir de quanto de aproveitamento eu ganho trocando?".

    Sem o custo da original volta a ser UMA linha, plotando o incremental — o
    app nao inventa margem para a original.
    """
    if r.anual is None:
        return

    lo, hi = P.SLIDER_DOMINIO
    atual_x = e.aproveitamento_dianteiro * 100
    com_refil, base = curvas_comparadas(e)
    duas = base is not None

    if duas:
        pontos, valor_atual = com_refil, base + r.anual
    else:
        pontos = curva_sensibilidade(e)
        valor_atual = r.anual
    if not pontos:
        return

    dados = pd.DataFrame(pontos, columns=["aproveitamento", "anual"])
    eixo_x, eixo_y = _eixo_x(lo, hi), _eixo_y()
    camadas: list[alt.Chart] = []

    # --- marcas dos presets: verticais, 1px SOLIDA ------------------------
    marcas = pd.DataFrame(
        {"aproveitamento": [round(p.dianteiro * 100) for p in P.PRESETS]}
    )
    camadas.append(
        alt.Chart(marcas).mark_rule(color=TRACO, strokeWidth=1).encode(x=eixo_x)
    )

    # --- linha do zero: SO se o dominio de y cruzar o zero ---------------
    minimo = min(dados["anual"].min(), base if duas else 0.0)
    maximo = max(dados["anual"].max(), base if duas else 0.0)
    if bool(minimo < 0 < maximo):
        zero = pd.DataFrame({"anual": [0], "rotulo": ["R$ 0"]})
        camadas.append(
            alt.Chart(zero)
            .mark_rule(color=TINTA_SECUNDARIA, strokeWidth=1)
            .encode(y=eixo_y)
        )
        camadas.append(
            alt.Chart(zero)
            .mark_text(
                align="left", dx=4, dy=-6,
                color=TINTA_SECUNDARIA, fontSize=T_DERIVADO,
            )
            .encode(y=eixo_y, text="rotulo:N")
        )

    # --- linha 2: so com a palheta original ------------------------------
    #
    # Cinza e TRACEJADA. A distincao entre as duas linhas nao depende de cor
    # (§3.1.3 / §9.4): sao tinta diferente, tracejado diferente e cada uma tem
    # rotulo direto proprio. Sobrevive a impressao e a daltonismo.
    if duas:
        linha_base = pd.DataFrame({"anual": [base]})
        camadas.append(
            alt.Chart(linha_base)
            .mark_rule(color=TINTA_SECUNDARIA, strokeWidth=2, strokeDash=[6, 3])
            .encode(y=eixo_y)
        )
        camadas.append(
            alt.Chart(
                pd.DataFrame(
                    {
                        "aproveitamento": [lo],
                        "anual": [base],
                        "rotulo": ["só com a palheta original"],
                    }
                )
            )
            .mark_text(
                align="left", dx=6, dy=-11, baseline="bottom",
                color=TINTA_SECUNDARIA, fontSize=T_DERIVADO, fontWeight=600,
            )
            .encode(x=eixo_x, y=eixo_y, text="rotulo:N")
        )

    # --- linha 1: adotando o refil. 2px, PRETA, sem area -----------------
    camadas.append(
        alt.Chart(dados)
        .mark_line(
            color=TINTA_PRIMARIA, strokeWidth=2,
            strokeCap="round", strokeJoin="round",
        )
        .encode(x=eixo_x, y=eixo_y)
    )
    if duas:
        camadas.append(
            alt.Chart(
                pd.DataFrame(
                    {
                        "aproveitamento": [hi],
                        "anual": [dados["anual"].iloc[-1]],
                        "rotulo": ["com refil"],
                    }
                )
            )
            .mark_text(
                align="right", dx=-6, dy=-12,
                color=TINTA_PRIMARIA, fontSize=T_DERIVADO, fontWeight=700,
            )
            .encode(x=eixo_x, y=eixo_y, text="rotulo:N")
        )

    # --- o VAO entre as duas linhas, medido no ponto atual ----------------
    #
    # Esta camada existe para o grafico nao contradizer a manchete (§5.11). Com
    # duas linhas de TOTAL, o marcador mostra o total — e um gerente que le
    # R$ 186.840 no grafico e R$ 141.480 na manchete tropeca. O vao anotado
    # mostra que o segundo numero E a distancia entre as linhas.
    if duas:
        vao = pd.DataFrame(
            {
                "aproveitamento": [atual_x],
                "anual": [base],
                "anual2": [valor_atual],
                "rotulo": [f"+ {formato.moeda_agregada(r.anual)}"],
                "meio": [(base + valor_atual) / 2],
            }
        )
        camadas.append(
            alt.Chart(vao)
            .mark_rule(color=MARCA_VERMELHO, strokeWidth=2, opacity=0.55)
            .encode(x=eixo_x, y=eixo_y, y2="anual2:Q")
        )
        camadas.append(
            alt.Chart(vao)
            .mark_text(
                align="left", dx=9,
                color=MARCA_VERMELHO, fontSize=T_DERIVADO, fontWeight=700,
            )
            .encode(
                x=eixo_x,
                y=alt.Y("meio:Q", axis=None, scale=alt.Scale(zero=False)),
                text="rotulo:N",
            )
        )

    # --- marcador da posicao atual: o unico vermelho do grafico ----------
    atual = pd.DataFrame(
        {
            "aproveitamento": [atual_x],
            "anual": [valor_atual],
            "rotulo": [formato.moeda_agregada(valor_atual)],
        }
    )
    camadas.append(
        alt.Chart(atual)
        .mark_point(
            size=AREA_MARCADOR, filled=True,
            color=MARCA_VERMELHO, stroke=SUPERFICIE, strokeWidth=2,
        )
        .encode(x=eixo_x, y=eixo_y)
    )

    # --- rotulo direto do marcador --------------------------------------
    #
    # §5.11 pede "exatamente um" rotulo direto, o do marcador. Com duas series
    # cada linha ganha o seu, porque a alternativa seria uma caixa de legenda —
    # e a §5.11 dispensa legenda justamente para nao gastar espaco. Rotulo
    # direto identifica melhor e nao pede ida de olho ao canto.
    vira = (atual_x - lo) / (hi - lo) > LIMIAR_VIRA_ROTULO
    camadas.append(
        alt.Chart(atual)
        .mark_text(
            align="right" if vira else "left",
            dx=-14 if vira else 14,
            dy=-18,
            color=TINTA_PRIMARIA, fontSize=T_DERIVADO, fontWeight=700,
        )
        .encode(x=eixo_x, y=eixo_y, text="rotulo:N")
    )

    titulo, subtitulo = _texto_do_titulo(e, duas)
    figura = (
        alt.layer(*camadas)
        .properties(
            height=ALTURA_PLOT,
            title=alt.TitleParams(
                titulo,
                subtitle=subtitulo,
                anchor="start",
                color=TINTA_PRIMARIA,
                fontSize=T_ROTULO,
                fontWeight=600,
                subtitleColor=TINTA_SECUNDARIA,
                subtitleFontSize=T_PREMISSAS,
            ),
        )
        .configure_view(stroke=None)
    )

    st.altair_chart(figura, width="stretch")
    _frase_do_cruzamento(e, base)


def _frase_do_cruzamento(e: Entradas, base: float | None) -> None:
    """"a partir de X% o refil supera o que ele tem hoje" — se houver um X.

    Procura o primeiro aproveitamento em que a linha do refil passa da linha da
    original. Se nao houver cruzamento no dominio, DIZ isso em vez de sugerir
    que existe: o app nao promete um ponto de virada que a conta nao tem.
    """
    if base is None:
        return

    pontos, _ = curvas_comparadas(e)
    if not pontos:
        return

    cruzamento = next((pp for pp, total in pontos if total > base), None)
    if cruzamento is None:
        st.markdown(
            '<p class="st-legenda-bloco">O refil <b>não supera</b> a palheta '
            "original em nenhum ponto da faixa — confira preço e custo das duas "
            "categorias.</p>",
            unsafe_allow_html=True,
        )
        return

    if cruzamento <= P.SLIDER_DOMINIO[0]:
        st.markdown(
            '<p class="st-legenda-bloco">O refil supera a palheta original em '
            "<b>toda a faixa</b> de aproveitamento.</p>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<p class="st-legenda-bloco">A partir de <b>{int(cruzamento)}% de '
        f"aproveitamento</b> o refil passa a render mais que continuar só com "
        f"a palheta original.</p>",
        unsafe_allow_html=True,
    )


def tabela_da_curva(e: Entradas, r: Resultado) -> None:
    """Gemeo em tabela — OBRIGATORIO (§5.11, §9).

    "E o canal de reserva que substitui o tooltip que a stack nao tem." Mostra
    as MESMAS series do grafico: se o grafico tem duas linhas, a tabela tem as
    duas colunas, mais o incremental entre elas. Um gemeo que mostra menos que
    o grafico deixa de ser gemeo.
    """
    if r.anual is None:
        return

    com_refil, base = curvas_comparadas(e, passo_pp=5)
    if not com_refil:
        return

    colunas: dict[str, list[str]] = {
        "Aproveitamento dianteiro": [f"{int(x)}%" for x, _ in com_refil],
    }

    if base is not None:
        colunas["Com refil (ano)"] = [
            formato.moeda_agregada(y) for _, y in com_refil
        ]
        colunas["Só com a original (ano)"] = [
            formato.moeda_agregada(base) for _ in com_refil
        ]
        colunas["Diferença (incremental)"] = [
            formato.moeda_agregada(y - base) for _, y in com_refil
        ]
    else:
        colunas["Margem do refil (ano)"] = [
            formato.moeda_agregada(y) for _, y in com_refil
        ]

    with st.expander("Ver os números da curva", expanded=False):
        st.dataframe(pd.DataFrame(colunas), hide_index=True, width="stretch")

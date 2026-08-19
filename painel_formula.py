"""§5.8 — Painel de formula. Prova em um toque para todo numero `ƒ calculado`.

    Pares dianteiros por mes
      passagens totais x aproveitamento dianteiro
      3.000 x 30% = 900

    Margem mensal do dianteiro
      pares x (preco - custo)
      900 x (R$ 197,90 - R$ 84,90) = R$ 101.700,00

REGRA (§5.8): fechado por padrao — abrir custa um round-trip e ocupa a tela.
Mas EXISTE, e o vendedor sabe onde esta. "E a diferenca entre parecer honesto e
SER VERIFICAVEL."

Quando o gerente aponta um numero e pergunta "de onde saiu isso?", a resposta
ja esta na tela.
"""

from __future__ import annotations

import streamlit as st

from src import formato
from src import parametros as P
from src.calculo import Entradas, Resultado


def painel(e: Entradas, r: Resultado) -> None:
    if r.anual is None:
        return

    with st.expander("De onde vêm esses números", expanded=False):
        for titulo, formula, conta in _linhas(e, r):
            st.markdown(
                f"**{titulo}**  \n"
                f"<span class='st-legenda-bloco'>{formula}</span>  \n"
                f"`{conta}`",
                unsafe_allow_html=True,
            )


def _linhas(e: Entradas, r: Resultado) -> list[tuple[str, str, str]]:
    pct_d = formato.percentual(e.aproveitamento_dianteiro)
    linhas: list[tuple[str, str, str]] = [
        (
            "Passagens totais por mês",
            "pontos de venda × passagens por ponto",
            f"{e.pontos_de_venda} × {formato.inteiro(e.passagens_por_ponto)}"
            f" = {formato.inteiro(r.passagens_totais)}",
        ),
        (
            "Pares dianteiros por mês",
            "passagens totais × aproveitamento dianteiro",
            f"{formato.inteiro(r.passagens_totais)} × {pct_d}"
            f" = {formato.inteiro(r.pares_dianteiros)}",
        ),
        (
            "Margem mensal do dianteiro",
            "pares × (preço − custo)",
            f"{formato.inteiro(r.pares_dianteiros)} × "
            f"({formato.moeda_unitaria(e.preco_dianteiro)} − "
            f"{formato.moeda_unitaria(e.custo_dianteiro)})"
            f" = {formato.moeda_unitaria(r.margem_dianteiro)}",
        ),
    ]

    if r.traseiro_na_conta:
        # Repare: o traseiro tem preco e custo PROPRIOS. Nenhuma linha aqui
        # deriva um do outro (§5.13).
        linhas.append(
            (
                "Unidades traseiras por mês",
                "passagens totais × aproveitamento traseiro",
                f"{formato.inteiro(r.passagens_totais)} × "
                f"{formato.percentual(e.aproveitamento_traseiro)}"
                f" = {formato.inteiro(r.unidades_traseiras)}",
            )
        )
        linhas.append(
            (
                "Margem mensal do traseiro",
                "unidades × (preço − custo) — preço e custo próprios do traseiro",
                f"{formato.inteiro(r.unidades_traseiras)} × "
                f"({formato.moeda_unitaria(e.preco_traseiro)} − "
                f"{formato.moeda_unitaria(e.custo_traseiro)})"
                f" = {formato.moeda_unitaria(r.margem_traseiro)}",
            )
        )
        linhas.append(
            (
                "Margem de contribuição bruta mensal",
                "margem do dianteiro + margem do traseiro",
                f"{formato.moeda_unitaria(r.margem_dianteiro)} + "
                f"{formato.moeda_unitaria(r.margem_traseiro)}"
                f" = {formato.moeda_unitaria(r.margem_refil)}",
            )
        )

    if r.tem_margem_da_original:
        linhas.append(
            (
                "Margem unitária da palheta original",
                "preço cobrado hoje − custo de aquisição",
                f"{formato.moeda_unitaria(e.preco_original)} − "
                f"{formato.moeda_unitaria(e.custo_original)}"
                f" = {formato.moeda_unitaria(r.margem_unitaria_original)}",
            )
        )
        linhas.append(
            (
                "Margem mensal atual com palhetas",
                "palhetas vendidas por mês × margem unitária da original",
                f"{formato.inteiro(r.originais_por_mes)} × "
                f"{formato.moeda_unitaria(r.margem_unitaria_original)}"
                f" = {formato.moeda_unitaria(r.margem_atual)}",
            )
        )
        linhas.append(
            (
                "Margem de contribuição incremental mensal",
                "a margem do refil inteira — nada é descontado dela. "
                "A canibalização não é modelada: assume-se que nenhuma venda de "
                "refil tira venda da palheta original",
                f"{formato.moeda_unitaria(r.incremental_mensal)}",
            )
        )
    else:
        linhas.append(
            (
                "Margem de contribuição do refil, por mês",
                "sem o custo da palheta original não existe margem dela para "
                "comparar — o resultado NÃO é chamado de incremental",
                f"{formato.moeda_unitaria(r.incremental_mensal)}",
            )
        )
    linhas.append(
        (
            f"Valor anual — {P.rotulo_do_anual()}",
            "incremental mensal × 12"
            + (
                "  ·  rampa e sazonalidade ⚠️ não aplicadas"
                if not (P.rampa_aplicada() and P.sazonalidade_aplicada())
                else ""
            ),
            f"{formato.moeda_unitaria(r.incremental_mensal)} × 12"
            f" = {formato.moeda_unitaria(r.anual)}",
        )
    )
    linhas.append(
        (
            "Tradução por passagem",
            "aproveitamento dianteiro, arredondado em base 10",
            f"{pct_d} → {formato.traducao_curta(e.aproveitamento_dianteiro)}",
        )
    )

    if r.cashback_total:
        # Documenta explicitamente que o cashback NAO participa da conta.
        partes = []
        if r.cashback_por_par_dianteiro:
            partes.append(
                f"{formato.inteiro(r.pares_dianteiros)} pares × "
                f"{formato.moeda_unitaria(r.cashback_por_par_dianteiro)}"
            )
        if r.cashback_por_unidade_traseira and r.traseiro_na_conta:
            partes.append(
                f"{formato.inteiro(r.unidades_traseiras)} unidades × "
                f"{formato.moeda_unitaria(r.cashback_por_unidade_traseira)}"
            )
        linhas.append(
            (
                "Cashback para a equipe",
                "NÃO entra na conta — pago pela Suicatech, não sai da margem "
                "da concessionária",
                f"{' + '.join(partes)} = "
                f"{formato.moeda_unitaria(r.cashback_total)}/mês  "
                f"· efeito na margem exibida: R$ 0,00",
            )
        )
        for nome, valor in r.cashback_por_destinatario:
            linhas.append(
                (
                    f"Cashback — {nome}",
                    "soma do valor por venda das duas categorias",
                    f"{formato.moeda_unitaria(valor)}/mês",
                )
            )

    return linhas

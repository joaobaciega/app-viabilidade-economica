"""Tiles de KPI — a grade de cartoes do dashboard do cliente. Acrescimo D5.

Nao substitui nada do DESIGN: sao os numeros `ƒ calculado` que ja existiam
espalhados como legenda, reunidos numa grade legivel. O bloco de resultado
(§5.5) continua sendo a manchete, e nenhum tile compete com ele em tamanho —
26px contra os 48px da traducao.

REGRA QUE OS TILES OBEDECEM: nenhum deles e faturamento em destaque. §4 permite
faturamento apenas em linha secundaria, nunca como manchete, porque o resultado
e lido em margem (plano §3.3).
"""

from __future__ import annotations

import streamlit as st

from src import formato
from src.calculo import Entradas, Resultado

CHAVE_CONTAINER = "kpis"


def _tile(rotulo: str, valor: str, nota: str = "") -> str:
    linha_nota = f'<span class="st-kpi-nota">{nota}</span>' if nota else ""
    return (
        f'<div class="st-kpi">'
        f'<span class="st-kpi-rotulo">{rotulo}</span>'
        f'<span class="st-kpi-valor">{valor}</span>'
        f"{linha_nota}</div>"
    )


def tiles(e: Entradas, r: Resultado) -> None:
    """Quatro tiles com o que o vendedor confere de relance."""
    if r.passagens_totais is None:
        return

    dados: list[tuple[str, str, str]] = [
        (
            "Passagens/mês",
            formato.inteiro(r.passagens_totais),
            f"{e.pontos_de_venda} ponto(s) de venda",
        )
    ]

    if r.pares_dianteiros is not None:
        dados.append(
            (
                "Pares dianteiros/mês",
                formato.inteiro(r.pares_dianteiros),
                f"{formato.percentual(e.aproveitamento_dianteiro)} de aproveitamento",
            )
        )

    if r.traseiro_na_conta and r.unidades_traseiras:
        dados.append(
            (
                "Unidades traseiras/mês",
                formato.inteiro(r.unidades_traseiras),
                f"{formato.percentual(e.aproveitamento_traseiro)} de aproveitamento",
            )
        )
    elif r.originais_por_mes is not None:
        dados.append(
            (
                "Palhetas originais/mês",
                formato.inteiro(r.originais_por_mes),
                "vendidas hoje",
            )
        )

    if r.margem_refil is not None:
        dados.append(
            (
                "Margem do refil/mês",
                formato.moeda_agregada(r.margem_refil),
                "dianteiro + traseiro",
            )
        )

    with st.container(key=CHAVE_CONTAINER):
        colunas = st.columns(len(dados), gap="small")
        for coluna, (rotulo, valor, nota) in zip(colunas, dados):
            with coluna:
                st.markdown(_tile(rotulo, valor, nota), unsafe_allow_html=True)

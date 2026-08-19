"""Componente +17 — EstadoVazioCatalogo. ACRESCIMO DECLARADO.

O DESIGN v5 nao especifica as Telas 2 e 3 (a §6 dele cobre so a Tela 1), e a
§7.3 dele trata do vazio da Tela 1, nao do catalogo. Este componente
implementa a regra que o plano §7 Fase 2 fixa:

    "O app mostra APENAS marcas com dados completos — melhor 3 marcas solidas
    que 15 pela metade."

E a regra de nao inventar dado, do plano §2.4:

    "NUNCA preencher com preco de vendedor terceiro e chamar de original. O
    item 3 existe para ser auditavel; UMA LINHA INVENTADA DESTROI AS OUTRAS 200."

Por isso, com o catalogo sem registros, estas telas dizem honestamente que nao
ha dado publicado. Nao ha numero de exemplo, nao ha marca listada vazia, nao ha
travessao no lugar de valor.

PROVISORIO ate o DESIGN ser regerado para as Telas 2 e 3.
"""

from __future__ import annotations

import streamlit as st

from src.dados.carregar_snapshot import Snapshot
from src.icones import svg


def vazio(
    *,
    titulo: str,
    explicacao: str,
    o_que_falta: list[str],
    snapshot: Snapshot,
) -> None:
    """O estado vazio de uma tela dependente de catalogo."""
    with st.container(border=True):
        st.markdown(
            f'<p class="st-falta-ancora">{titulo}<br>'
            f"<span>{explicacao}</span></p>",
            unsafe_allow_html=True,
        )

        st.markdown("<p class='st-legenda-bloco'><b>O que falta publicar</b></p>",
                    unsafe_allow_html=True)
        for item in o_que_falta:
            st.markdown(
                f"<p class='st-legenda-bloco'>{svg('tabela')} {item}</p>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<p class='st-legenda-bloco'>Publicação: "
            "<code>python -m pipeline.publicar</code> valida a planilha e gera "
            "o snapshot. Nenhum dado chega a esta tela sem passar pelas "
            "validações S1–S13.</p>",
            unsafe_allow_html=True,
        )

    if snapshot.indisponivel:
        st.caption(f"Estado do catálogo: {snapshot.indisponivel}.")

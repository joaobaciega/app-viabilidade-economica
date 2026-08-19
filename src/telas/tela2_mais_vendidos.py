"""Tela 2 — Carros mais vendidos por marca. ESTRUTURA, dados na Fase 0.

O DESIGN v5 nao especifica esta tela (a §6 dele cobre so a Tela 1). A estrutura
segue o plano §4, e e PROVISORIA ate o DESIGN ser regerado.

Plano §4.1: seletor de marca, duas colunas — emplacamentos 2025 ("os carros
novos da sua marca") e acumulado 2022-2025 ("a base que passa pela sua oficina").

Plano §4.2: rodape fixo com fonte, periodo e link para o PDF PUBLICO da
Fenabrave. NUNCA para area logada — a secao "Mais Vendidos" do portal exige
login, os informes em PDF nao. Um link que pede senha na frente do cliente e a
auditabilidade se autodestruindo.

Plano §7 Fase 2: o app mostra APENAS marcas com dados completos. Sem registros,
exibe o estado vazio — nunca uma marca listada pela metade.
"""

from __future__ import annotations

import streamlit as st

from src.componentes.estado_vazio_catalogo import vazio
from src.dados.carregar_snapshot import carregar
from src.icones import svg


def renderizar() -> None:
    st.markdown(
        f'<div class="st-secao">{svg("veiculos")}'
        "<span>Carros mais vendidos por marca</span></div>",
        unsafe_allow_html=True,
    )

    snapshot = carregar()
    marcas = snapshot.marcas

    if not marcas:
        vazio(
            titulo="Nenhuma marca publicada ainda.",
            explicacao=(
                "Esta tela existe para dar credibilidade antes da comparação de "
                "preço, e por isso não exibe número sem fonte e data. Enquanto a "
                "curadoria da Fase 0 não publicar uma marca completa, ela não "
                "aparece no seletor."
            ),
            o_que_falta=[
                "Emplacamentos 2025 por modelo, dos informes públicos da Fenabrave",
                "Acumulado 2022–2025 (janela de garantia e revisão)",
                "Corte varejo × venda direta, quando o informe trouxer",
                "Link para o PDF público da fonte, com data de coleta",
            ],
            snapshot=snapshot,
        )
        return

    # Estrutura pronta para quando houver registros.
    marca = st.selectbox("Marca", marcas, key="tela2_marca")
    col_a, col_b = st.columns(2, gap="large")
    linhas = [m for m in snapshot.modelos if m.get("marca") == marca]

    with col_a:
        st.markdown("**Emplacamentos 2025**")
        st.caption("os carros novos da sua marca")
        for i, m in enumerate(sorted(linhas, key=lambda x: -(x.get("emplac_2025") or 0))[:5], 1):
            st.markdown(f"{i}  {m.get('modelo')}  ·  {m.get('emplac_2025'):,}".replace(",", "."))

    with col_b:
        st.markdown("**Acumulado 2022–2025**")
        st.caption("a base que passa pela sua oficina")
        for i, m in enumerate(
            sorted(linhas, key=lambda x: -(x.get("emplac_2022_2025") or 0))[:5], 1
        ):
            valor = m.get("emplac_2022_2025")
            if valor:
                st.markdown(f"{i}  {m.get('modelo')}  ·  {valor:,}".replace(",", "."))

    st.caption(snapshot.rotulo_versao())

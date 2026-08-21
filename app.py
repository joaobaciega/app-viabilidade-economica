"""Simulador de viabilidade — refil de palhetas. Suicatech / Intrace AG.

Ponto de entrada. A ORDEM DAS CHAMADAS AQUI E A ORDEM DE LEITURA DA TELA
(DESIGN.md §6.1.3) — em Streamlit a hierarquia visual e literalmente a ordem do
script, e a §6.1.2 fixa o que o cliente ve primeiro.

    st.set_page_config(...)
    injetar_css()          # 🔧 tokens da camada B
    cabecalho()
    tela ativa
    faixa_do_vendedor()

Rode com:  python -m streamlit run app.py

NAO EXISTE ESTADO OFFLINE (plano §6.2, DESIGN §1, §3 camada C, §7.1). O
Streamlit renderiza no servidor e o navegador so mantem um websocket. Este app
NAO PROMETE, em nenhum texto, funcionamento sem rede. A conectividade e
requisito de EQUIPAMENTO (plano §6.5) e esta em docs/CHECKLIST-PRE-VISITA.md.
"""

from __future__ import annotations

import streamlit as st

# O import de `src` dispara V1-V7. Parametro invalido = o app NAO SOBE, com
# erro no log do deploy, nunca uma tela quebrada na frente do cliente (§7.4).
import src  # noqa: F401
from src import css, marca
from src.componentes import estado_reconexao, faixa_vendedor

# Rotulo curto na navegacao, titulo completo no corpo da tela. Rotulo longo
# quebra em duas linhas na largura do cabecalho e rouba altura da tela.
TELAS = {
    "Simulador": ("simulador", "Simulador de viabilidade"),
    "Mais vendidos": ("mais_vendidos", "Carros mais vendidos"),
    "Preço original": ("preco_original", "Preço da palheta original"),
}


def main() -> None:
    st.set_page_config(
        page_title="Simulador de viabilidade — refil de palhetas",
        page_icon="◆",
        layout="wide",
        # §6.1.3: a lateral NAO e usada. Uma lateral permanente comeria ~250px
        # dos ~1180px do alvo, e comeria justamente da coluna que o cliente le
        # a 1 metro. A navegacao mora no cabecalho da propria pagina — ver
        # _cabecalho() e a nota sobre isso abaixo.
        initial_sidebar_state="collapsed",
        menu_items={"Get help": None, "Report a Bug": None, "About": None},
    )

    css.injetar()  # 🔧 camada B — precisa vir antes de qualquer render

    escolha = _cabecalho()
    tela, _titulo_completo = TELAS[escolha]

    # Mantem o app acordado, reduzindo a hibernacao de 12 h do Community Cloud
    # (plano §6.5, risco 6). NAO substitui o checklist pre-visita.
    estado_reconexao.manter_acordado()

    if tela == "simulador":
        from src.telas import tela1_simulador

        tela1_simulador.renderizar()
        return  # a Tela 1 desenha a propria faixa do vendedor

    if tela == "mais_vendidos":
        from src.telas import tela2_mais_vendidos

        # A Tela 2 desenha a propria faixa do vendedor, como a Tela 1. Ela nao
        # le o snapshot: a base de emplacamentos e um dado proprio, e herdar
        # aqui o rotulo do snapshot faria o rodape dizer "nenhum snapshot
        # publicado" embaixo de numeros reais na tela.
        tela2_mais_vendidos.renderizar()
        return

    from src.telas import tela3_preco_original

    linhas = tela3_preco_original.renderizar()

    from src.dados.carregar_snapshot import carregar

    faixa_vendedor.faixa(linhas, meta=[carregar().rotulo_versao()])


def _cabecalho() -> str:
    """Logo, titulo e a NAVEGACAO entre as tres telas. Devolve a tela escolhida.

    POR QUE A NAVEGACAO ESTA AQUI E NAO NA BARRA LATERAL:
    a §6.1.3 fixa `initial_sidebar_state="collapsed"` e a §6.1.9 proibe qualquer
    marca do framework. Ocultar a barra superior do Streamlit — necessario para
    cumprir a §6.1.9 — leva embora o controle que abre a lateral, e as Telas 2 e
    3 ficam INALCANCAVEIS. Isso aconteceu de fato nesta construcao e so apareceu
    na verificacao pelo navegador.

    A navegacao propria resolve os dois de uma vez: nenhuma marca do framework,
    nenhuma dependencia do chrome dele, e nada roubando largura da coluna que o
    cliente le. Ela nao e destrutiva, ao contrario de `novo cliente`, que por
    isso continua na faixa do vendedor (§5.9).
    """
    # `st.container(key="cabecalho")` gera a classe `st-key-cabecalho`, que e o
    # gancho da faixa vermelha de largura total. Sem o container o CSS nao tem
    # onde pegar (um <div> injetado por markdown fecha sozinho e nao envolve).
    with st.container(key="cabecalho"):
        col_marca, col_nav = st.columns([5, 7], gap="large")

        with col_marca:
            st.markdown(
                f'<div class="st-cabecalho">'
                f"{marca.html()}"
                # O logo ja carrega a assinatura "SWISSINT INTRACE AG"; repetir
                # aqui seria redundancia. O subtitulo diz que ferramenta e esta.
                f'<span class="st-titulo-tela">Simulador de viabilidade '
                f"· refil de palhetas</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col_nav:
            with st.container(key="navegacao"):
                escolha = st.radio(
                    "Telas",
                    list(TELAS),
                    key="tela_ativa",
                    horizontal=True,
                    label_visibility="collapsed",
                )

    return escolha


main()

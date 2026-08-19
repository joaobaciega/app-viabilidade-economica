"""Tela 3 — Preco da palheta original. ESTRUTURA, dados na Fase 0.

O DESIGN v5 nao especifica esta tela. A estrutura segue o plano §5, e e
PROVISORIA ate o DESIGN ser regerado.

E A TELA QUE PROVA. "Qualquer dado frouxo aqui contamina as outras duas telas."

O bloco "menos codigo na prateleira" fica NO TOPO, acima dos cartoes: e o
argumento mais forte do produto (plano §2.5) e nao pode virar nota de rodape.
O numero exato de codigos esta em aberto (⚠️ G) e NAO PODE SER CHUTADO — o
bloco existe com o MarcadorDecisaoAberta no lugar do numero e o texto
qualitativo. "Voce troca 40 codigos por 3" e uma frase que fecha reuniao, e ela
PRECISA DO NUMERO CERTO.

O preco do refil e UM PAR DE CAMPOS NO CABECALHO, nao um campo por cartao,
porque o refil e universal — um preco, uma linha, zero curadoria (plano §2.5).
Repetir o campo por cartao contradiria visualmente a propria tese que a tela
existe para provar, e faria o vendedor digitar o mesmo numero cinco vezes na
frente do cliente.
"""

from __future__ import annotations

import streamlit as st

from src import parametros as P
from src.componentes import marcador_decisao_aberta as aberto
from src.componentes.cartao_comparativo import cartao, idade_em_dias
from src.componentes.campo_unidade import campo_moeda
from src.componentes.estado_vazio_catalogo import vazio
from src.dados.carregar_snapshot import carregar
from src.estado import K_CUSTO_D, K_PRECO_D, K_PRECO_T
from src.icones import svg


def renderizar() -> list[str]:
    """Devolve as linhas para a faixa do vendedor (avisos de idade)."""
    st.markdown(
        f'<div class="st-secao">{svg("preco")}'
        "<span>Preço da palheta original</span></div>",
        unsafe_allow_html=True,
    )

    _bloco_menos_codigo()

    snapshot = carregar()
    if not snapshot.precos_originais:
        vazio(
            titulo="Nenhum preço de palheta original publicado ainda.",
            explicacao=(
                "Esta é a tela que prova, e por isso ela nunca exibe um preço sem "
                "fonte, sem data e sem print. Enquanto a coleta da Fase 0 não "
                "publicar um registro completo, nada aparece aqui."
            ),
            o_que_falta=[
                "Preço da original por marca, modelo e faixa de ano-modelo",
                "Print com o selo de loja oficial da montadora, sem o banner "
                '"não é compatível com seu veículo"',
                "Data de coleta e link para a fonte",
                "Tabela de aplicação: medida por posição e faixa de ano",
            ],
            snapshot=snapshot,
        )
        return []

    return _cartoes(snapshot)


def _bloco_menos_codigo() -> None:
    """O argumento mais forte do produto, com o furo da decisao G visivel."""
    with st.container(border=True):
        st.markdown("**MENOS CÓDIGO NA PRATELEIRA**")

        if P.CODIGOS_COBERTURA_97 is None:
            # ⚠️ G — o numero NAO e chutado. O marcador fica no lugar dele.
            st.markdown(
                "<p class='st-mensal'>Palheta original: dezenas de códigos.<br>"
                "Refil Suicatech: "
                + aberto.chip("nº de códigos em aberto — decisão G")
                + " cobrem 97% do mercado.</p>",
                unsafe_allow_html=True,
            )
        else:  # pragma: no cover — enquanto G estiver aberta
            st.markdown(
                f"<p class='st-mensal'>Refil Suicatech: "
                f"{P.CODIGOS_COBERTURA_97} códigos cobrem 97% do mercado.</p>",
                unsafe_allow_html=True,
            )

        st.caption(
            "Atender mais carros com muito menos código em prateleira: menos "
            "capital parado, menos ruptura, menos complexidade de compra. "
            "É verificável na hora, olhando a prateleira."
        )


def _cartoes(snapshot) -> list[str]:
    # Dois campos na tela inteira, no cabecalho — nao dois por cartao.
    with st.container(border=True):
        st.markdown("**Seu preço nesta negociação**")
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            preco_d = campo_moeda(
                chave=K_PRECO_D,
                rotulo="Dianteiro · por par",
            )
        with col_b:
            preco_t = campo_moeda(
                chave=K_PRECO_T,
                rotulo="Traseiro · por unidade",
            )
        st.caption("Preenchido nesta negociação · não fica salvo.")

    marcas = sorted(
        {str(r.get("marca")) for r in snapshot.precos_originais if r.get("marca")}
    )
    marca = st.selectbox("Marca", marcas, key="tela3_marca")
    registros = [r for r in snapshot.precos_originais if r.get("marca") == marca]

    avisos: list[str] = []
    colunas = st.columns(2, gap="large")
    for i, registro in enumerate(registros):
        unidade = registro.get("unidade", "par")
        preco_refil = preco_d if unidade == "par" else preco_t
        with colunas[i % 2]:
            cartao(registro, preco_refil, unidade)

        # ⚠️ L — idade CRUA em dias, sem limiar. So na faixa do vendedor.
        dias = idade_em_dias(registro.get("data_coleta", ""))
        if dias is not None:
            avisos.append(
                f"preço {marca} {registro.get('modelo')}: {dias} dias"
            )

    return avisos

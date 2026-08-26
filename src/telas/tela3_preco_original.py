"""Tela 3 — Preco da palheta original, sobre a base `app_precos`.

O DESIGN v5 nao especifica esta tela. A estrutura segue o plano §5, e e
PROVISORIA ate o DESIGN ser regerado.

E A TELA QUE PROVA. "Qualquer dado frouxo aqui contamina as outras duas telas."

REGRA DA TELA, pedida pelo cliente e implementada pelo `index=None` do seletor:
o menu suspenso de marca vem ANTES DE TUDO, e enquanto nenhuma marca estiver
escolhida NAO APARECE NADA ALEM DO MENU. Nem cartao, nem campo de preco, nem
lista de modelos. A conversa e com o gerente de UMA concessionaria, e 80
modelos de 18 marcas na frente dele nao e informacao, e ruido.

O bloco "menos codigo na prateleira" continua NO TOPO, acima dos cartoes: e o
argumento mais forte do produto (plano §2.5) e nao pode virar nota de rodape.
Ele passa a aparecer JUNTO com os cartoes, o que e o que reconcilia as duas
exigencias — "no topo, acima dos cartoes" e "nada alem do menu antes da
escolha". O numero exato de codigos esta em aberto (⚠️ G) e NAO PODE SER
CHUTADO: o bloco existe com o MarcadorDecisaoAberta no lugar do numero e o
texto qualitativo. "Voce troca 40 codigos por 3" e uma frase que fecha reuniao,
e ela PRECISA DO NUMERO CERTO.

O preco do refil e UM PAR DE CAMPOS NO CABECALHO, nao um campo por cartao,
porque o refil e universal — um preco, uma linha, zero curadoria (plano §2.5).
Repetir o campo por cartao contradiria visualmente a propria tese que a tela
existe para provar, e faria o vendedor digitar o mesmo numero cinco vezes na
frente do cliente.

AS 18 MARCAS APARECEM NO MENU, inclusive as 17 que ainda nao passaram pela
coleta. E uma divergencia deliberada em relacao a Tela 2, que so lista marca
com dado — ver o cabecalho de `src/dados/carregar_precos.py` e
docs/DIVERGENCIAS.md. Modelo sem coleta mostra a estrutura montada com "—" no
lugar do valor, NUNCA um preco estimado.

NOTA SOBRE AS CLASSES DE CSS USADAS AQUI: esta tela vive sobre fundo BRANCO, e
por isso usa `.st-kpi-valor`, `.st-kpi-rotulo`, `.st-legenda-bloco`, `.st-chip`,
`.st-derivado` e `.st-premissas`. A excecao e `_bloco_menos_codigo`, que usa
`.st-mensal` — herdado da versao anterior desta tela e mantido como estava.
"""

from __future__ import annotations

import html

import streamlit as st

from src import parametros as P
from src.componentes import faixa_vendedor
from src.componentes import marcador_decisao_aberta as aberto
from src.componentes.campo_unidade import campo_moeda
from src.componentes.cartao_comparativo import idade_em_dias
from src.componentes.cartao_preco_palheta import cartao
from src.dados.carregar_precos import BasePrecos, MarcaPrecos, carregar
from src.estado import K_PRECO_D, K_PRECO_T
from src.icones import svg

CHAVE_MARCA = "tela3_marca"
CHAVE_SELETOR = "seletor_marca"


def renderizar() -> None:
    """Desenha a tela inteira, inclusive a propria faixa do vendedor."""
    base = carregar()

    _titulo(base)

    if not base.nomes_de_marca:
        _estado_vazio(base)
        faixa_vendedor.faixa([], meta=[base.rotulo_versao()])
        return

    # Marca que saiu da base entre uma publicacao e outra: o Streamlit levanta
    # se a chave guardar um valor fora das opcoes. Zerar ANTES de instanciar o
    # widget e a direcao segura (§5.3 proibe escrever a chave DEPOIS), e
    # atribuir e nao apagar, como em estado.novo_cliente().
    if st.session_state.get(CHAVE_MARCA) not in (None, *base.nomes_de_marca):
        st.session_state[CHAVE_MARCA] = None

    escolhida = _seletor(base)

    # NADA ALEM DO MENU. Sem convite, sem chips, sem campo de preco.
    if escolhida is None:
        faixa_vendedor.faixa([], meta=[base.rotulo_versao()])
        return

    marca = base.marcas[escolhida]

    _bloco_menos_codigo()
    preco_d, preco_t = _campos_refil()
    avisos = _cartoes(base, marca, preco_d, preco_t)
    _procedencia(base, marca)

    faixa_vendedor.faixa(avisos, meta=[base.rotulo_versao()])


# ---------------------------------------------------------------------------
# Blocos
# ---------------------------------------------------------------------------


def _titulo(base: BasePrecos) -> None:
    nota = ""
    if base.nomes_de_marca:
        nota = (
            f"{len(base.nomes_de_marca)} marcas · "
            f"{base.total_com_preco} de {base.total_de_modelos} modelos "
            "com preço coletado"
        )
    st.markdown(
        f'<div class="st-secao">{svg("preco")}'
        f"<span>Preço da palheta original</span>"
        f'<span class="st-secao-nota">{html.escape(nota)}</span></div>',
        unsafe_allow_html=True,
    )


def _seletor(base: BasePrecos) -> str | None:
    """O menu suspenso, em evidencia. Abre VAZIO — `index=None` E O REQUISITO.

    Com o padrao do Streamlit (`index=0`) a tela escolheria uma marca sozinha e
    ja mostraria veiculos e precos antes de alguem pedir.

    `st.container(key=...)` gera a classe estavel `st-key-seletor_marca`, que e
    o gancho do CSS que da destaque ao campo. E API publica: um `<div>`
    injetado por markdown fecharia sozinho e nao envolveria o widget.
    """
    with st.container(key=CHAVE_SELETOR):
        coluna, _ = st.columns([5, 7], gap="large")
        with coluna:
            return st.selectbox(
                "Marca da concessionária",
                base.nomes_de_marca,
                index=None,
                placeholder="Escolha a marca…",
                key=CHAVE_MARCA,
            )


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


def _campos_refil() -> tuple[float | None, float | None]:
    """Dois campos na tela inteira, no cabecalho — nao dois por cartao.

    As chaves sao as MESMAS da Tela 1 (`K_PRECO_D`/`K_PRECO_T`), ja listadas em
    `estado.CAMPOS_DE_SESSAO`: o preco digitado aqui e o mesmo da simulacao, e
    o botao `novo cliente` ja o limpa de graca.
    """
    with st.container(border=True):
        st.markdown("**Seu preço nesta negociação**")
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            preco_d = campo_moeda(chave=K_PRECO_D, rotulo="Dianteiro · por par")
        with col_b:
            preco_t = campo_moeda(
                chave=K_PRECO_T, rotulo="Traseiro · por unidade"
            )
        st.caption("Preenchido nesta negociação · não fica salvo.")
    return preco_d, preco_t


def _cartoes(
    base: BasePrecos,
    marca: MarcaPrecos,
    preco_d: float | None,
    preco_t: float | None,
) -> list[str]:
    """A grade de cartoes da marca. Devolve os avisos da faixa do vendedor."""
    avisos: list[str] = []
    colunas = st.columns(2, gap="large")

    for i, modelo in enumerate(marca.modelos):
        with colunas[i % 2]:
            cartao(
                modelo,
                janela=base.janela_emplacamento,
                preco_refil_d=preco_d,
                preco_refil_t=preco_t,
            )

        # ⚠️ L — idade CRUA em dias, sem limiar. So na faixa do vendedor.
        dias = idade_em_dias(modelo.data_consulta)
        if dias is not None:
            avisos.append(f"preço {marca.nome} {modelo.modelo}: {dias} dias")

    return avisos


def _procedencia(base: BasePrecos, marca: MarcaPrecos) -> None:
    """Canal, data e cobertura da coleta. Aparece SEMPRE, mesmo sem preco."""
    if base.indisponivel:
        return

    linhas = [
        f"<b>Cobertura</b> {marca.modelos_com_preco} de "
        f"{len(marca.modelos)} modelos de {html.escape(marca.nome)} com preço "
        f"coletado · {base.total_com_preco} de {base.total_de_modelos} no total"
    ]

    if marca.canal:
        linhas.append(f"<b>Canal</b> {html.escape(marca.canal)}")
    if marca.data_consulta:
        linhas.append(f"<b>Coletado em</b> {html.escape(marca.data_consulta)}")

    if not marca.modelos_com_preco:
        linhas.append(
            f"{html.escape(marca.nome)} ainda não passou pela coleta na loja "
            "oficial da montadora. A estrutura dos campos aparece nos cartões "
            "com “—” no lugar do valor: nenhum preço é estimado, e nenhum "
            "preço de vendedor terceiro é chamado de original."
        )

    notas = [(m.modelo, m.nota) for m in marca.modelos if m.nota and m.tem_preco]
    for modelo, nota in notas:
        linhas.append(f"<b>{html.escape(modelo)}</b> {html.escape(nota)}")

    st.markdown(
        '<div class="st-premissas">' + "<br>".join(linhas) + "</div>",
        unsafe_allow_html=True,
    )


def _estado_vazio(base: BasePrecos) -> None:
    """Sem base publicada. Nunca tela branca, nunca conteudo pela metade."""
    with st.container(border=True):
        st.markdown(
            '<p class="st-kpi-valor">Nenhum preço da original publicado ainda.</p>'
            '<p class="st-legenda-bloco">Esta é a tela que prova, e por isso ela '
            "nunca exibe um preço sem fonte e sem data. Enquanto a base da "
            "coleta não for publicada, nenhuma marca aparece no seletor.</p>"
            '<p class="st-legenda-bloco">Publicação: '
            "<code>python -m pipeline.gerar_precos</code> lê a planilha da "
            "curadoria e grava <code>dados/precos.json</code>.</p>",
            unsafe_allow_html=True,
        )
    if base.indisponivel:
        st.caption(f"Estado da base: {base.indisponivel}.")

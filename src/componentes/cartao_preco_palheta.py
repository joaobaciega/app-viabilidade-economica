"""Componente +19 — CartaoPrecoPalheta. ACRESCIMO DECLARADO.

O DESIGN v5 nao especifica as Telas 2 e 3 (a §5 dele diz literalmente que os
componentes delas "nao estao aqui"). A estrutura segue o plano §5.1 e §5.3, e e
PROVISORIA ate o DESIGN ser regerado.

POR QUE NAO E O `cartao()` DE `cartao_comparativo.py`: aquele registro e
`ano_ini`/`ano_fim`/`medida_mm`/`posicao`/`unidade`, campos que a base
`app_precos` nao tem. O que aquele modulo tem de reaproveitavel — a
`RESSALVA_ARMACAO` e a `idade_em_dias` da ⚠️ L — e importado daqui, nao
duplicado.

REGRAS QUE ESTE CARTAO OBEDECE:
  - UNIDADE DECLARADA DOS DOIS LADOS (§2.7). "por par" no dianteiro, "por
    unidade" no traseiro, dos dois lados da comparacao. O refil dianteiro so e
    comparado com o dianteiro da original; nao ha conversao nem soma cruzada,
    porque errar por 2x na tela cuja unica funcao e ser auditavel destroi a
    tela inteira
  - A RESSALVA SOBRE A ARMACAO, porque comparar palheta inteira com refil e
    comparar coisas diferentes. Declarar a condicao desarma a objecao antes
    dela chegar
  - A MARGEM DA CONCESSIONARIA NAO APARECE AQUI. O custo dela e o preco de
    venda da Suicatech; esse numero so existe na Tela 1, depois de digitado
  - preco SEMPRE exibido, qualquer idade; data de coleta SEMPRE colada ao
    preco; aviso de idade APENAS na faixa do vendedor (⚠️ L, sem limiar)

O TRAVESSAO NO LUGAR DO VALOR — divergencia declarada (docs/DIVERGENCIAS.md).
A Tela 2 escreve "não publicado" por extenso e `estado_vazio_catalogo` proibe o
travessao. Aqui ele foi pedido de proposito: com 75 dos 80 modelos ainda sem
coleta, o cliente precisa ver QUAIS CAMPOS existem para a marca dele, com o
rotulo ao lado do "—". A regra que continua valendo inteira e a outra, mais
importante (plano §2.4): nenhum preco inventado, nenhum preco de terceiro
chamado de original. UMA LINHA INVENTADA DESTROI AS OUTRAS 200.

NOTA SOBRE AS CLASSES DE CSS: este cartao vive sobre fundo BRANCO, e por isso
usa `.st-kpi-valor`, `.st-kpi-rotulo`, `.st-legenda-bloco`, `.st-chip` e
`.st-derivado`. NAO use `.st-mensal`, `.st-anual`, `.st-traducao` nem
`.st-falta-ancora`: todas sao `color: var(--tinta-clara)` e so funcionam dentro
do cartao escuro `.st-key-resultado` — sobre branco elas somem.
"""

from __future__ import annotations

import html

import streamlit as st

from src import formato
from src.componentes.cartao_comparativo import RESSALVA_ARMACAO
from src.dados.carregar_precos import ModeloPreco

TRACO = "—"

SEM_COLETA = "Sem preço coletado nesta marca."


def cartao(
    modelo: ModeloPreco,
    *,
    janela: str,
    preco_refil_d: float | None,
    preco_refil_t: float | None,
) -> None:
    """Um modelo: preco da original por posicao, e a economia contra o refil."""
    with st.container(border=True):
        _identificacao(modelo, janela)
        _linha_dianteiro(modelo)
        _linha_traseiro(modelo)
        _linha_completo(modelo)
        _procedencia(modelo)

        st.divider()
        _comparacao(modelo, preco_refil_d, preco_refil_t)


# ---------------------------------------------------------------------------
# Blocos do cartao
# ---------------------------------------------------------------------------


def _identificacao(modelo: ModeloPreco, janela: str) -> None:
    st.markdown(f"**{html.escape(modelo.modelo.upper())}**")

    partes = []
    if modelo.categoria:
        partes.append(modelo.categoria)
    if modelo.emplacamentos is not None:
        contexto = f"{formato.inteiro(modelo.emplacamentos)} emplacamentos"
        partes.append(f"{contexto} em {janela}" if janela else contexto)
    if partes:
        st.caption(" · ".join(partes))


def _linha_dianteiro(modelo: ModeloPreco) -> None:
    """O dianteiro e SEMPRE por par — a original nao e vendida avulsa aqui."""
    _valor("Dianteiro · por par", modelo.preco_dianteiro_par)

    notas = []
    if modelo.pn_dianteiro:
        notas.append(f"código {modelo.pn_dianteiro}")
    if modelo.tem_faixa:
        notas.append(
            f"faixa {formato.moeda_unitaria(modelo.preco_dianteiro_min)} – "
            f"{formato.moeda_unitaria(modelo.preco_dianteiro_max)}"
        )
    if modelo.ofertas_dianteiro:
        plural = "s" if modelo.ofertas_dianteiro > 1 else ""
        notas.append(f"{modelo.ofertas_dianteiro} oferta{plural}")
    if notas:
        _nota(" · ".join(notas))

    _link(modelo.url_dianteiro, "ver o anúncio do dianteiro")


def _linha_traseiro(modelo: ModeloPreco) -> None:
    """Tres estados, nao dois — ver o cabecalho de `carregar_precos.py`.

    `tem_traseiro is None` significa que ninguem verificou se o veiculo tem
    limpador traseiro. Escrever "não tem" nesse caso seria afirmar por conta
    propria, em 29 modelos, algo que a coleta nao apurou.
    """
    _valor("Traseiro · por unidade", modelo.preco_traseiro_unid)

    if modelo.tem_traseiro is False:
        _nota("veículo sem limpador traseiro")
        return

    if modelo.tem_traseiro is None:
        _nota("limpador traseiro não verificado")
        return

    notas = []
    if modelo.pn_traseiro:
        notas.append(f"código {modelo.pn_traseiro}")
    if modelo.preco_traseiro_unid is None:
        notas.append("palheta traseira não encontrada na loja oficial")
    if notas:
        _nota(" · ".join(notas))

    _link(modelo.url_traseiro, "ver o anúncio do traseiro")


def _linha_completo(modelo: ModeloPreco) -> None:
    _valor("Veículo completo", modelo.preco_veiculo_completo)
    if modelo.preco_veiculo_completo is None and modelo.tem_preco:
        # O caso do Pulse: dianteiro coletado, traseiro nao encontrado. Somar o
        # que existe daria um "completo" que nao cobre o carro inteiro.
        _nota("em aberto enquanto faltar o preço da traseira")


def _procedencia(modelo: ModeloPreco) -> None:
    """Data e canal SEMPRE colados ao preco, na mesma classe de leitura (§5.3)."""
    if not modelo.tem_preco:
        st.caption(SEM_COLETA)
        return

    partes = []
    if modelo.data_consulta:
        partes.append(f"coletado em {modelo.data_consulta}")
    if modelo.canal:
        partes.append(modelo.canal)
    if partes:
        st.caption(" · ".join(partes))


def _comparacao(
    modelo: ModeloPreco,
    preco_refil_d: float | None,
    preco_refil_t: float | None,
) -> None:
    """A economia, por posicao. Dianteiro com dianteiro, traseiro com traseiro."""
    if preco_refil_d is None and preco_refil_t is None:
        st.caption("Informe o preço do refil no topo da tela.")
        return

    if not modelo.tem_preco and modelo.preco_traseiro_unid is None:
        st.caption(
            "Sem o preço da original não há comparação. "
            "Nunca preenchido com preço de vendedor terceiro."
        )
        return

    linhas = _economia(
        "Dianteiro", modelo.preco_dianteiro_par, preco_refil_d, "por par"
    ) + _economia(
        "Traseiro", modelo.preco_traseiro_unid, preco_refil_t, "por unidade"
    )

    if not linhas:
        st.caption("Informe o preço do refil na mesma posição para comparar.")
        return

    st.markdown("".join(linhas), unsafe_allow_html=True)
    st.caption(RESSALVA_ARMACAO)


def _economia(
    posicao: str, original: float | None, refil: float | None, unidade: str
) -> list[str]:
    """Uma linha de economia, ou nenhuma. NUNCA compara unidades diferentes."""
    if original is None or refil is None:
        return []

    economia = original - refil
    fracao = economia / original
    return [
        f'<p class="st-legenda-bloco"><b>{posicao} · seu refil '
        f"{formato.moeda_unitaria(refil)} {unidade}</b></p>"
        f'<p class="st-legenda-bloco">Cliente economiza '
        f"{formato.moeda_unitaria(economia)} · "
        f"{formato.percentual(fracao, casas=1)} sobre "
        f"{formato.moeda_unitaria(original)}</p>"
    ]


# ---------------------------------------------------------------------------
# Primitivas de exibicao
# ---------------------------------------------------------------------------


def _valor(rotulo: str, preco: float | None) -> None:
    """Rotulo SEMPRE visivel; o valor vira '—' quando nao foi coletado.

    O rotulo ficar de pe com o travessao ao lado e o ponto do componente: e o
    que mostra a estrutura do dado sem afirmar um numero que ninguem coletou.
    """
    texto = TRACO if preco is None else formato.moeda_unitaria(preco)
    st.markdown(
        f'<span class="st-kpi-rotulo">{html.escape(rotulo)}</span>'
        f'<span class="st-kpi-valor">{texto}</span>',
        unsafe_allow_html=True,
    )


def _nota(texto: str) -> None:
    st.markdown(
        f'<p class="st-legenda-bloco">{html.escape(texto)}</p>',
        unsafe_allow_html=True,
    )


def _link(url: str, rotulo: str) -> None:
    """Link para a fonte. Sempre em aba nova, sempre com `rel=noopener`."""
    if not url:
        return
    st.markdown(
        f'<p class="st-legenda-bloco">'
        f'<a href="{html.escape(url, quote=True)}" target="_blank" '
        f'rel="noopener">{html.escape(rotulo)}</a></p>',
        unsafe_allow_html=True,
    )

"""O RESULTADO NA TELA — o espelho do PDF. D28.

Pedido do cliente em 27/08/2026: *"a tela de resultados deve ser exatamente
igual o que aparece no PDF. Com todos os graficos, tabelas e KPIs."*

    ┌──────────────────────────────┬──────────────────────────────┐
    │ FATURAMENTO ADICIONAL        │ MARGEM DE CONTRIBUIÇÃO ADIC. │
    │ R$ 249.372                   │ R$ 141.480                   │  manchete
    │ R$ 20.781 por mês            │ R$ 11.790 por mês            │  (escura)
    └──────────────────────────────┴──────────────────────────────┘
    Valores anuais · margem de contribuição incremental · ano cheio em regime

    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │ MARK UP        │ │ NA OFICINA     │ │ NOVA MARGEM    │  apoio
    │ 108%           │ │ 3 a cada 10    │ │ R$ 15.570      │
    └────────────────┘ └────────────────┘ └────────────────┘

    Margem de contribuição no ano: hoje e com o refil      <- barras
    Os três cenários medidos na carteira                   <- tiras
    <cashback, quando ligado>
    Como o resultado varia com o aproveitamento            <- curva + gemeo
    As premissas desta simulação                           <- linhas
    Preço e custo de tabela  (so com custo informado)
    O que esta simulação ainda não considera

ESTE MODULO NAO DECIDE NADA. Quais blocos existem, em que ordem, com que rotulo
e que numero vem de `src/apresentacao.py`, que o PDF consome igual. Aqui so ha
HTML. Uma divergencia entre a tela e o papel deixou de ser possivel por
descuido: ela exige editar a montagem, e `test_paridade_tela_e_pdf` reprova
quem editar so um dos dois desenhos.

REGRAS QUE CONTINUAM VALENDO INTEGRALMENTE:

  - NENHUM numero em vermelho, nem quando negativo (§3.1.2, §13.1): numero
    financeiro em vermelho le como prejuizo, que e o oposto do que o pitch
    afirma. O destaque da manchete e a superficie ESCURA (D6, 17,9:1)
  - NAO USE st.metric — nao chega ao tamanho que a leitura a 1 m exige
  - o rotulo nomeia SO a conta que foi feita (§4, §6.1.7). "Mark up" nao e
    "margem" e nao e "lucro"; desde D27 o cartao dele diz
    `(faturamento − custo) ÷ custo` embaixo do numero, porque um percentual ao
    lado de duas colunas de reais convida a leitura de margem percentual
  - o cashback ACRESCENTA uma linha e nunca altera nenhum numero
  - o gemeo em TABELA da curva e obrigatorio (§5.11, §9) e continua na Tela 1,
    logo abaixo do grafico. Ele nao existe no PDF porque no papel nao ha
    tooltip para substituir — e a unica peca que a tela tem a mais
"""

from __future__ import annotations

import html

import streamlit as st

from src import apresentacao
from src.apresentacao import Apresentacao, Cartao, Secao

CHAVE_CONTAINER = "resultado"


def bloco(a: Apresentacao) -> None:
    """Desenha o resultado inteiro. Recebe a APRESENTACAO, nao o `Resultado`.

    Quem chama ja garantiu o gate (`estado.resultado_visivel()`). A guarda do
    `manchete is None` fica porque um resultado parcial desenhado pela metade e
    pior do que nenhum — e e o estado E1, que tem texto proprio.
    """
    with st.container(key=CHAVE_CONTAINER):
        if a.manchete is None:
            _incompleto(a)
            return

        _manchete(a)
        _apoio(a)
        _barras(a)
        _cenarios(a)
        _cashback(a)


def _md(bruto: str) -> None:
    st.markdown(bruto, unsafe_allow_html=True)


def _e(texto: str) -> str:
    """Escapa o que vem de dado antes de entrar no HTML.

    Nenhum destes textos vem do cliente hoje — todos nascem em `apresentacao`,
    de constantes e de numeros formatados. Escapar mesmo assim custa nada e
    fecha a porta para o dia em que um nome digitado na reuniao chegar aqui.
    """
    return html.escape(texto, quote=False)


# ---------------------------------------------------------------------------
# Manchete e apoio
# ---------------------------------------------------------------------------


def _incompleto(a: Apresentacao) -> None:
    """Estado E1: nenhum valor no lugar do que falta (P9, §6.1.6)."""
    _md(
        f'<span class="st-secao-res">O resultado</span>'
        f'<p class="st-cartao-valor">{_e(a.traducao)}</p>'
        f'<p class="st-secao-nota-res">{_e(a.incompleto)}</p>'
    )


def _manchete(a: Apresentacao) -> None:
    """Os dois numeros, lado a lado, no maior corpo da tela (D26).

    Os dois tem o MESMO corpo, e nao um maior que o outro: hierarquizar um
    sobre o outro aqui responderia uma pergunta que ninguem fez. Quem os separa
    e o rotulo, que nomeia a conta de cada um (§4).
    """
    assert a.manchete is not None
    colunas = "".join(
        f'<div class="st-manchete-col">'
        f'<span class="st-manchete-rotulo">{_e(c.rotulo)}</span>'
        f'<span class="st-manchete-valor">{_e(c.valor or "")}</span>'
        f'<span class="st-manchete-apoio">{_e(c.apoio)}</span>'
        f"</div>"
        for c in a.manchete
    )
    _md(f'<div class="st-manchete">{colunas}</div>')
    _md(f'<p class="st-nota-grupo">{_e(a.nota_do_grupo)}</p>')


def _cartao(c: Cartao) -> str:
    """Um KPI de apoio. Sem valor, o MOTIVO ocupa o lugar do numero.

    §6.1.9 proibe travessao no lugar de moeda e P9 proibe default zero: um mark
    up de 0% significaria "vende ao preco de custo", que e uma afirmacao que
    ninguem fez.
    """
    valor = (
        f'<span class="st-cartao-valor">{_e(c.valor)}</span>'
        if c.valor is not None
        else ""
    )
    return (
        f'<div class="st-cartao">'
        f'<span class="st-cartao-rotulo">{_e(c.rotulo)}</span>'
        f"{valor}"
        f'<span class="st-cartao-apoio">{_e(c.apoio)}</span>'
        f"</div>"
    )


def _apoio(a: Apresentacao) -> None:
    """Mark up, traducao em escala humana e a nova margem com refil.

    A ORDEM DESTA TUPLA VEM DA MONTAGEM, e nao daqui. `st.columns` porque os
    tres cartoes precisam de altura igual e o `.st-cartao` ja tem `height:100%`
    — o mesmo arranjo que os tres cartoes tinham antes de D28.
    """
    colunas = st.columns(len(a.apoio), gap="small")
    for coluna, dado in zip(colunas, a.apoio):
        with coluna:
            _md(_cartao(dado))


# ---------------------------------------------------------------------------
# Barras, cenarios e cashback
# ---------------------------------------------------------------------------


def _secao(titulo: str, nota: str = "") -> None:
    fim = f'<p class="st-secao-nota-res">{_e(nota)}</p>' if nota else ""
    _md(f'<span class="st-secao-res">{_e(titulo)}</span>{fim}')


def _barras(a: Apresentacao) -> None:
    """Duas barras na mesma grandeza, a segunda com a MESMA base da primeira.

    A base repetida diz, no desenho, que nada foi trocado — a premissa de
    canibalizacao NAO afirma substituicao (`P.CANIBALIZACAO_MODELADA`). Com
    incremental negativo a segunda barra e mais baixa e o vao que falta aparece
    em contorno tracejado, nunca em vermelho (§13.1).
    """
    b = a.barras
    if b is None:
        return

    _secao(a.titulo_barras)

    total = b.hoje + b.incremental
    teto = max(total, b.hoje, 1.0)
    ganho = b.incremental >= 0

    # DOIS SISTEMAS DE PORCENTAGEM, e confundi-los desalinha o desenho:
    #
    #   pct_*      fracao do PLOT (a altura fixa da coluna). Manda na altura de
    #              cada pilha e nas duas faixas da regua do vao
    #   dentro_*   fracao da PILHA. Manda nos segmentos empilhados
    #
    # A pilha existe para o rotulo poder ficar colado no topo da barra
    # (`bottom: 100%` sobre ela). Solto na coluna, ele flutuava no topo do
    # plot — com a base em 4,8%, a 300px do risco que nomeava.
    pct_hoje = max(b.hoje, 0.0) / teto * 100
    pct_total = max(total, 0.0) / teto * 100
    pct_vao = abs(pct_total - pct_hoje)

    pct_pilha = pct_total if ganho else pct_hoje
    dentro_vao = (pct_vao / pct_pilha * 100) if pct_pilha else 0.0
    dentro_base = max(100.0 - dentro_vao, 0.0)

    classe_vao = "st-barra-inc" if ganho else "st-barra-falta"
    segmentos = (
        f'<div class="st-barra-seg {classe_vao}" style="height:{dentro_vao:.2f}%"></div>'
        f'<div class="st-barra-seg st-barra-base" style="height:{dentro_base:.2f}%"></div>'
    )

    # A regua do vao fica na altura do segmento que ela mede — o mesmo lugar
    # que ela ocupa no PDF. O bloco de baixo e um espacador da altura da base.
    embaixo = pct_hoje if ganho else pct_total
    classe_delta = "st-barra-delta" + ("" if ganho else " st-barra-delta--perda")

    _md(
        f'<div class="st-barras">'
        f'<div class="st-barra">'
        f'<div class="st-barra-corpo">'
        f'<div class="st-barra-pilha" style="height:{pct_hoje:.2f}%">'
        f'<span class="st-barra-valor">{_e(b.rotulo_hoje)}</span>'
        f'<div class="st-barra-seg st-barra-base" style="height:100%"></div>'
        f"</div>"
        f"</div>"
        f'<span class="st-barra-nome">{_e(b.nome_hoje)}</span>'
        f"</div>"
        f'<div class="st-barra">'
        f'<div class="st-barra-corpo">'
        f'<div class="st-barra-pilha" style="height:{pct_pilha:.2f}%">'
        f'<span class="st-barra-valor">{_e(b.rotulo_refil)}</span>'
        f"{segmentos}"
        f"</div>"
        f"</div>"
        f'<span class="st-barra-nome">{_e(b.nome_refil)}</span>'
        f"</div>"
        f'<div class="{classe_delta}">'
        f'<div class="st-barra-delta-vao" style="height:{pct_vao:.2f}%">'
        f"<span>{_e(b.rotulo_incremental)}</span>"
        f"</div>"
        f'<div style="height:{embaixo:.2f}%"></div>'
        f"</div>"
        f"</div>"
        f'<p class="st-secao-nota-res">{_e(b.nota)}</p>'
    )


def _cenarios(a: Apresentacao) -> None:
    """As tres faixas medidas da carteira, com a simulada destacada.

    O PESSIMISTA ENTRA, e com o mesmo tamanho dos outros dois — o mesmo que o
    PDF faz. Um resultado que mostrasse so o cenario favoravel seria material
    de venda; a faixa inteira e o que permite escolher em qual acreditar.
    """
    if not a.cenarios:
        return

    _secao(a.titulo_cenarios)
    tiras = "".join(
        f'<div class="st-cenario{" st-cenario--ativo" if c.ativo else ""}">'
        f'<span class="st-cenario-rotulo">{_e(c.rotulo)}</span>'
        f'<span class="st-cenario-aprov">{_e(c.aproveitamento)}</span>'
        f'<span class="st-cenario-valor">{_e(c.valor)}</span>'
        f'<span class="st-cenario-apoio">{_e(c.apoio)}</span>'
        f"</div>"
        for c in a.cenarios
    )
    _md(
        f'<div class="st-cenarios">{tiras}</div>'
        f'<p class="st-secao-nota-res">{_e(a.nota_cenarios)}</p>'
    )


def _cashback(a: Apresentacao) -> None:
    """ACRESCENTA, NUNCA subtrai (§6.1.7, plano decisao A).

    A frase "pago pela Suicatech, nao sai da sua margem" e literal e pode ser
    dita na reuniao. A palavra "cashback" NUNCA entra no rotulo do resultado
    (§6.1.7): o rotulo nomeia so o que foi descontado, e cashback nao e
    desconto.
    """
    c = a.cashback
    if c is None:
        return

    rateio = (
        f'<span class="st-cashback-rateio">{_e(c.rateio)}</span>' if c.rateio else ""
    )
    _md(
        f'<div class="st-cashback">'
        f'<span class="st-cashback-valor">{_e(c.total)}</span>'
        f'<span class="st-cashback-nota">{_e(c.nota)}</span>'
        f"{rateio}"
        f"</div>"
    )


# ---------------------------------------------------------------------------
# As secoes de auditoria — as mesmas da pagina 2 do PDF
# ---------------------------------------------------------------------------


def secoes(a: Apresentacao) -> None:
    """Premissas, preco e custo de tabela, e o que ainda nao foi decidido.

    NA TELA TAMBEM, e nao so no papel. O argumento que as pos no PDF vale aqui
    inteiro: o gerente le o resultado sozinho depois que o vendedor sai da
    sala, e uma premissa que muda o numero sem aparecer e o que a §5.10 proibe.
    """
    for secao in (a.premissas, a.preco_custo, a.decisoes):
        _secao_de_linhas(secao)


def _secao_de_linhas(secao: Secao | None) -> None:
    if secao is None:
        return
    _secao(secao.titulo, secao.nota)
    linhas = "".join(
        f'<div class="st-linha-par">'
        f'<span class="st-linha-rotulo">{_e(rotulo)}</span>'
        f'<span class="st-linha-valor">{_e(valor)}</span>'
        f"</div>"
        for rotulo, valor in secao.linhas
    )
    _md(f'<div class="st-linhas">{linhas}</div>')


def titulo_da_curva(a: Apresentacao) -> None:
    """O titulo e o subtitulo da curva, na mesma forma das outras secoes."""
    if a.curva is None:
        return
    _secao(a.titulo_curva, a.curva.subtitulo)


def frase_da_curva(a: Apresentacao) -> None:
    """"a partir de X% o refil supera o que ha hoje" — se houver um X."""
    if a.curva is None or not a.curva.frase:
        return
    _md(f'<p class="st-secao-nota-res">{_e(a.curva.frase)}</p>')


__all__ = [
    "CHAVE_CONTAINER",
    "bloco",
    "frase_da_curva",
    "secoes",
    "titulo_da_curva",
    "apresentacao",
]

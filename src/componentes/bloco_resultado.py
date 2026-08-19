"""§5.5 — Bloco de resultado. E o que o cliente le.

"A ORDEM DE LEITURA E O REQUISITO MAIS IMPORTANTE DESTA TELA."

    ┌──────────────────────────────────────────────┐
    │  3 a cada 10 carros que entram               │  <- t-traducao 48/800
    │  na oficina                                  │     PRIMEIRO
    │                                              │
    │  R$ 141.480 por ano                          │  <- t-anual 36/700
    │  margem de contribuicao incremental          │  <- t-mensal 22
    │  R$ 11.790 por mes                           │  <- t-mensal 22
    │  ────────────────────────────────────────    │
    │  hoje R$ 3.780 -> com refil R$ 15.570        │
    └──────────────────────────────────────────────┘

REGRAS (§5.5):
  - A TRADUCAO VEM ANTES DO VALOR ANUAL. Em Streamlit isso e literalmente a
    ordem das chamadas no script. "R$ 1,2 milhao por ano" e rejeitado pelo
    cerebro antes de ser avaliado; "3 a cada 10 carros que entram na oficina" e
    verificado pela intuicao em dois segundos
  - a traducao e POR PASSAGEM, nunca por consultor/dia (erraria por 10x)
  - a traducao e MAIOR que o anual: t-traducao >= 1,25 x t-anual
  - NAO USE st.metric — nao chega aos 48px que a leitura a 1 m exige
  - resultado negativo em tinta clara COM O SINAL. Nada em vermelho: numero
    financeiro em vermelho le como prejuizo (§3.1.2, §13.1)
  - o rotulo nomeia SO o que de fato foi descontado (§6.1.7), e so diz
    "incremental" quando existe margem da original para descontar
"""

from __future__ import annotations

import streamlit as st

from src import formato
from src import parametros as P
from src.calculo import Resultado, rotulo_do_resultado

CHAVE_CONTAINER = "resultado"


def bloco(r: Resultado) -> None:
    # O container com key E o cartao (fundo escuro, regua vermelha, sombra),
    # estilizado em css.py §9. Sem `border=True`: a borda nativa brigaria com o
    # fundo escuro, e depender do wrapper interno deixou o fundo sem aplicar
    # numa versao anterior — texto branco sobre branco.
    with st.container(key=CHAVE_CONTAINER):
        if r.anual is None:
            _estado_vazio(r)
            return
        _resultado(r)


def _estado_vazio(r: Resultado) -> None:
    """§7.3: "O vazio desta tela NAO E UMA FALHA, e a abertura da conversa."

    "Trate o texto de estado vazio como roteiro de pitch, nao como mensagem de
    erro." Nenhum valor em R$ aparece aqui — nem R$ 0, nem travessao no lugar
    de moeda (§6.1.9).
    """
    if r.estado == "E1_sem_operacao":
        titulo = "Quantas passagens por mês esta oficina recebe?"
        apoio = (
            "É por aí que a conta começa. Depois: quantas palhetas são vendidas "
            "hoje e a que preço — o preço da original pode ser conferido ao vivo "
            "na aba <b>Preço original</b>."
        )
    else:
        titulo = "Falta o preço e o custo do refil."
        apoio = (
            "São os valores desta negociação. Abrem em branco de propósito: "
            "preço e custo são negociados caso a caso."
        )

    if r.traducao_fracao > 0:
        st.markdown(
            f'<p class="st-traducao">'
            f"{formato.traducao_por_passagem(r.traducao_fracao)}</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<p class="st-falta-ancora">{titulo}<span>{apoio}</span></p>',
        unsafe_allow_html=True,
    )


def _resultado(r: Resultado) -> None:
    # ------------------------------------------------------------------
    # (1) A TRADUCAO — PRIMEIRO, e o maior elemento da tela.
    #     Nao mova esta chamada para baixo do anual: a ordem das chamadas
    #     no script E a ordem de leitura (§5.5, P2, checklist §12).
    # ------------------------------------------------------------------
    st.markdown(
        f'<p class="st-traducao">'
        f"{formato.traducao_por_passagem(r.traducao_fracao)}</p>",
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # (2) O valor anual, com o rotulo que descreve a conta que foi feita
    # ------------------------------------------------------------------
    st.markdown(
        f'<p class="st-anual">{formato.moeda_agregada(r.anual)} por ano</p>'
        f'<p class="st-rotulo-resultado">{rotulo_do_resultado(r)}'
        f" · {P.rotulo_do_anual()}</p>",
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # (3) O valor mensal
    # ------------------------------------------------------------------
    st.markdown(
        f'<p class="st-mensal">{formato.moeda_agregada(r.incremental_mensal)} '
        f"por mês</p>",
        unsafe_allow_html=True,
    )

    _linhas_de_apoio(r)
    _hoje_versus_refil(r)


def _linhas_de_apoio(r: Resultado) -> None:
    """Volume e faturamento — linha de apoio, NUNCA manchete.

    §4: faturamento so em linha secundaria. NUNCA como manchete — o resultado e
    lido em margem (plano §3.3). Elevar o faturamento trocaria a metrica nativa
    do gerente de pos-venda (aproveitamento) por uma que nao e dele.
    """
    partes: list[str] = []
    if r.pares_dianteiros:
        partes.append(
            f"{formato.inteiro(r.pares_dianteiros)} pares dianteiros/mês"
        )
    if r.traseiro_na_conta and r.unidades_traseiras:
        partes.append(
            f"{formato.inteiro(r.unidades_traseiras)} unidades traseiras/mês"
        )
    if r.faturamento_refil:
        partes.append(
            f"{formato.moeda_agregada(r.faturamento_refil)} de faturamento/mês"
        )
    if partes:
        st.markdown(
            f'<p class="st-linha-apoio">{" · ".join(partes)}</p>',
            unsafe_allow_html=True,
        )

    _cashback(r)


def _cashback(r: Resultado) -> None:
    """A linha de cashback: ACRESCENTA, NUNCA subtrai (§6.1.7, plano decisao A).

    A frase "pago pela Suicatech, nao sai da sua margem" e literal e pode ser
    dita na reuniao — o plano §1.4 a identifica como uma vantagem que nao custa
    nada ao cliente.

    A palavra "cashback" NUNCA entra no rotulo do resultado (§6.1.7): o rotulo
    nomeia so o que foi descontado, e cashback nao e desconto.
    """
    if not r.cashback_total:
        return

    detalhe = " · ".join(
        f"{nome.lower()} {formato.moeda_agregada(valor)}"
        for nome, valor in r.cashback_por_destinatario
    )

    st.markdown(
        f'<div class="st-cashback">'
        f'<span class="st-cashback-valor">'
        f"{formato.moeda_agregada(r.cashback_total)}/mês de cashback"
        f"</span>"
        f'<span class="st-cashback-nota">para sua equipe — pago pela Suicatech, '
        f"não sai da sua margem</span>"
        + (f'<span class="st-cashback-rateio">{detalhe}</span>' if detalhe else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def _hoje_versus_refil(r: Resultado) -> None:
    """"hoje X -> com refil Y" — o contraste que ancora o resultado.

    So aparece quando ha margem da original para comparar. Sem o custo da
    original nao existe margem dela, e comparar margem com faturamento
    misturaria grandezas — exatamente o que a §6.1.5 proibe.
    """
    if r.margem_atual is None or r.incremental_mensal is None:
        return

    total = r.margem_atual + r.incremental_mensal
    st.markdown(
        f'<div class="st-hoje-refil">'
        f"<span>hoje <b>{formato.moeda_agregada(r.margem_atual)}/mês</b> "
        f"de margem com palhetas</span>"
        f'<span class="seta">→</span>'
        f"<span>com o refil <b>{formato.moeda_agregada(total)}/mês</b></span>"
        f"</div>",
        unsafe_allow_html=True,
    )

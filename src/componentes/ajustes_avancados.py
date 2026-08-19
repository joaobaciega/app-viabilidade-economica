"""§5.10 — Revelacao progressiva: "Ajustes avancados".

"Segurar o limite de campos editaveis visiveis. A planilha original tem ~30
celulas; num tablet, na frente do cliente, isso e morte."

REGRAS (§5.10):
  - fechado por padrao, SEMPRE, inclusive depois de aberto na simulacao
    anterior. Ele reabre fechado a cada carga da pagina
  - NENHUM campo dentro dele altera o resultado sem que a faixa de premissas
    (§5.6) reflita a mudanca. "Uma alteracao escondida atras de um acordeao que
    muda o numero da manchete sem deixar rastro e A PIOR FALHA POSSIVEL"
  - o expander conta como UM elemento na contagem de densidade

CONTEUDO, apos a revisao de 11/08/2026 (decisao do cliente):

    A operacao da concessionaria   consultores por ponto, dias uteis
    Cashback                       R$ por venda x 3 destinatarios x 2 categorias

O que SAIU, e por que:

  - SUBSTITUICAO (canibalizacao) — retirada. Consequencia declarada em
    parametros.CANIBALIZACAO_MODELADA e na faixa de premissas: o app passa a
    assumir que nenhuma venda de refil tira venda da palheta original
  - COMISSAO e IMPOSTOS — absorvidos pelo Cashback, que e o programa real. O
    valor destinado ao consultor por venda E a comissao dele, e agora vive num
    lugar so
  - INVESTIMENTO, ESTOQUE E PAYBACK — o bloco nunca existiu (⚠️ G), e a
    declaracao de que ele nao existe tambem saiu daqui. A decisao G continua
    visivel onde ela vale algo: no bloco "menos codigo na prateleira" da Tela 3
"""

from __future__ import annotations

import streamlit as st

from src import parametros as P
from src.componentes.campo_unidade import campo_moeda, campo_quantidade
from src.estado import (
    CHAVES_CASHBACK_D,
    CHAVES_CASHBACK_T,
    K_CONSULTORES,
    K_DIAS_UTEIS,
    K_PONTOS,
    contar_avancados_alterados,
)
from src.formato import total_derivado_consultores


def painel() -> None:
    alterados = contar_avancados_alterados()
    rotulo = "Ajustes avançados"
    if alterados:
        rotulo += f"  ·  {alterados} alterado{'s' if alterados != 1 else ''}"

    # expanded=False sempre: reabre fechado a cada carga da pagina.
    with st.expander(rotulo, expanded=False):
        _a_operacao()
        st.divider()
        _cashback()


def _a_operacao() -> None:
    st.markdown("**A operação da concessionária**")
    st.caption(
        "Estes dois não entram em nenhuma conta de margem — servem só à "
        "verificação de carga por consultor."
    )

    col_a, col_b = st.columns(2, gap="large")
    pontos = int(st.session_state.get(K_PONTOS) or 1)

    with col_a:
        campo_quantidade(
            chave=K_CONSULTORES,
            rotulo="Consultores por ponto de venda",
            derivado=lambda v: total_derivado_consultores(v, pontos),
        )
    with col_b:
        st.number_input(
            "Dias úteis por mês",
            min_value=1,
            max_value=31,
            step=1,
            key=K_DIAS_UTEIS,
        )


def _cashback() -> None:
    """O programa de cashback: R$ por venda, por destinatario e por categoria.

    A ARMADILHA que este bloco existe para nao cair (§6.1.7, plano decisao A):
    o cashback e pago pela SUICATECH, saindo da margem dela. Ele NAO desconta
    nada da margem da concessionaria. Preencher aqui ACRESCENTA uma linha ao
    resultado e nunca altera o valor da manchete.

    "Se a implementacao subtrair cashback da margem exibida, ela inverteu o
    principal argumento comercial do bloco."
    """
    st.markdown("**Cashback**  ·  valor por venda destinado a cada parte")
    st.caption(
        "Pago pela Suicatech, sai da margem dela. **Não desconta** da margem da "
        "concessionária — aparece como uma linha própria no resultado. Deixe em "
        "branco quem não participa."
    )

    cabecalho = st.columns([2, *([3] * len(P.DESTINATARIOS_CASHBACK))], gap="small")
    cabecalho[0].markdown(
        "<p class='st-cash-cabecalho'>&nbsp;</p>", unsafe_allow_html=True
    )
    for coluna, nome in zip(cabecalho[1:], P.DESTINATARIOS_CASHBACK):
        coluna.markdown(
            f"<p class='st-cash-cabecalho'>{nome}</p>", unsafe_allow_html=True
        )

    _linha_cashback("Dianteiro", "por par", CHAVES_CASHBACK_D)
    _linha_cashback("Traseiro", "por unidade", CHAVES_CASHBACK_T)


def _linha_cashback(categoria: str, unidade: str, chaves: tuple[str, ...]) -> None:
    """Uma linha da grade: a categoria a esquerda, um campo por destinatario.

    O rotulo de cada campo e colapsado — quem nomeia a coluna e o cabecalho da
    grade. Repetir "Consultor" em seis rotulos gastaria altura e leitura sem
    acrescentar informacao.
    """
    colunas = st.columns([2, *([3] * len(chaves))], gap="small")
    colunas[0].markdown(
        f"<p class='st-cash-linha'><b>{categoria}</b><br>{unidade}</p>",
        unsafe_allow_html=True,
    )
    for coluna, chave in zip(colunas[1:], chaves):
        with coluna:
            campo_moeda(chave=chave, rotulo=f"{categoria} {chave[-1]}", oculto=True)

"""Os dois blocos que MORAVAM em "Ajustes avancados". D21.

O expander da §5.10 DEIXOU DE EXISTIR em 27/08/2026, a pedido do cliente: o que
estava escondido atras dele subiu para a superficie primaria, junto dos outros
campos. Este modulo continua sendo a casa dos dois blocos que vinham de la —
o nome do arquivo guarda de onde eles vieram.

    operacao()   consultores por ponto, dias uteis
    cashback()   R$ por venda x 3 destinatarios x 2 categorias (grade 2x3)

O QUE A §5.10 PROTEGIA, e o que se perdeu com o fim do expander:

    "Segurar o limite de campos editaveis visiveis. A planilha original tem ~30
    celulas; num tablet, na frente do cliente, isso e morte."

Com estes oito campos na superficie, a Tela 1 passa de nove para dezessete
controles visiveis. O teto de seis da §6.1.4 ja estava rompido por D8; D21 o
abandona de vez. A contrapartida que continua de pe: cada bloco tem titulo que
diz que pergunta ele responde, e nenhum campo altera o resultado sem que a
faixa de premissas (§5.6) reflita a mudanca — essa regra da §5.10 NAO caiu com
o expander, e e a que importava.

O que continua fora, e por que:

  - SUBSTITUICAO (canibalizacao) — retirada. Consequencia declarada em
    parametros.CANIBALIZACAO_MODELADA e na faixa de premissas: o app assume que
    nenhuma venda de refil tira venda da palheta original
  - COMISSAO e IMPOSTOS — absorvidos pelo Cashback, que e o programa real. O
    valor destinado ao consultor por venda E a comissao dele
  - INVESTIMENTO, ESTOQUE E PAYBACK — o bloco nunca existiu (⚠️ G)
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
)
from src.formato import total_derivado_consultores


# A nota dos dois campos de operacao. Fica no fim da LINHA, e nao embaixo de
# cada campo: sao dois campos com a mesma ressalva, e repetir a ressalva duas
# vezes gasta altura sem acrescentar leitura.
NOTA_OPERACAO = (
    "Consultores e dias úteis não entram em nenhuma conta de margem — servem "
    "só à verificação de carga por consultor."
)


def campo_consultores() -> None:
    """Consultores por ponto de venda, com o total derivado (§5.1).

    Alimenta so a regra R1 de plausibilidade (carga por consultor por dia), que
    avisa na faixa do vendedor sem NUNCA bloquear o calculo (§6.1.8).
    """
    pontos = int(st.session_state.get(K_PONTOS) or 1)
    campo_quantidade(
        chave=K_CONSULTORES,
        rotulo="Consultores por ponto de venda",
        derivado=lambda v: total_derivado_consultores(v, pontos),
    )


def campo_dias_uteis() -> None:
    """Dias uteis por mes. Tem default (22) e quase nunca muda.

    Nao passa por `campo_quantidade` porque nao tem total derivado: um total de
    dias uteis somado entre pontos de venda nao significa nada.
    """
    st.number_input(
        "Dias úteis por mês",
        min_value=1,
        max_value=31,
        step=1,
        key=K_DIAS_UTEIS,
    )


def cashback() -> None:
    """O programa de cashback: R$ por venda, por destinatario e por categoria.

    A ARMADILHA que este bloco existe para nao cair (§6.1.7, plano decisao A):
    o cashback e pago pela SUICATECH, saindo da margem dela. Ele NAO desconta
    nada da margem da concessionaria. Preencher aqui ACRESCENTA uma linha ao
    resultado e nunca altera nenhum dos tres numeros.

    "Se a implementacao subtrair cashback da margem exibida, ela inverteu o
    principal argumento comercial do bloco."
    """
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

    O rotulo INVISIVEL, porem, nomeia o destinatario ("Dianteiro · Consultor") e
    nao o indice da chave ("Dianteiro 0"), como era antes: `label_visibility`
    esconde o rotulo da tela mas o leitor de tela continua lendo, e "Dianteiro 0"
    nao diz nada a quem depende dele (§9.6).
    """
    colunas = st.columns([2, *([3] * len(chaves))], gap="small")
    colunas[0].markdown(
        f"<p class='st-cash-linha'><b>{categoria}</b><br>{unidade}</p>",
        unsafe_allow_html=True,
    )
    for coluna, chave, nome in zip(
        colunas[1:], chaves, P.DESTINATARIOS_CASHBACK
    ):
        with coluna:
            campo_moeda(chave=chave, rotulo=f"{categoria} · {nome}", oculto=True)

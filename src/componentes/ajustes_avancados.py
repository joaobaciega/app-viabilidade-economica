"""Os dois blocos que MORAVAM em "Ajustes avancados". D21.

O expander da §5.10 DEIXOU DE EXISTIR em 27/08/2026, a pedido do cliente: o que
estava escondido atras dele subiu para a superficie primaria, junto dos outros
campos. Este modulo continua sendo a casa dos dois blocos que vinham de la —
o nome do arquivo guarda de onde eles vieram.

    operacao()   consultores por ponto, dias uteis
    cashback()   valor por venda x 3 destinatarios x 2 categorias

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
from src.formato import (
    total_derivado_cashback,
    total_derivado_consultores,
    venda_da_unidade,
)


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
    """O programa de cashback: valor por venda, por destinatario e por categoria.

    A ARMADILHA que este bloco existe para nao cair (§6.1.7, plano decisao A):
    o cashback e pago pela SUICATECH, saindo da margem dela. Ele NAO desconta
    nada da margem da concessionaria. Preencher aqui ACRESCENTA uma linha ao
    resultado e nunca altera nenhum dos tres numeros.

    "Se a implementacao subtrair cashback da margem exibida, ela inverteu o
    principal argumento comercial do bloco."

    D23 — A FORMA MUDOU, e por que: era uma GRADE 2x3 com cabecalho de coluna
    ("Consultor", "Gerente", "Marketing") e os seis campos de rotulo colapsado.
    A grade tinha quatro colunas — a da categoria mais uma por destinatario — e
    D22 travou ela em linha em QUALQUER largura, porque empilhada o cabecalho
    deixava de encabecar e os seis campos ficavam anonimos. O preco disso estava
    escrito na propria D22: "a 390px ela fica apertada — quatro colunas de ~85px
    — e isso e o compromisso escolhido".

    Nao e mais. Cada campo passou a carregar o proprio rotulo VISIVEL com o nome
    do destinatario, e com isso:

      - a coluna da categoria sumiu (o titulo dela virou uma linha por cima dos
        tres campos, como ja acontece no bloco do refil), sobrando tres colunas
        em vez de quatro
      - empilhar deixou de perder informacao. Abaixo de 768px os campos viram
        tres caixas de largura inteira, cada uma com o nome de quem recebe

    O custo assumido: "Consultor · Gerente · Marketing" aparece duas vezes, uma
    por categoria, em vez de uma vez no cabecalho. Sao ~21px por rotulo, e e o
    que compra um campo de ~360px no lugar de um de ~85px.
    """
    st.caption(
        "Pago pela Suicatech, sai da margem dela. **Não desconta** da margem da "
        "concessionária — aparece como uma linha própria no resultado. Deixe em "
        "branco quem não participa."
    )

    for nome_categoria, chaves in (
        ("dianteiro", CHAVES_CASHBACK_D),
        ("traseiro", CHAVES_CASHBACK_T),
    ):
        categoria = P.categoria_por_nome(nome_categoria)
        if categoria is not None:
            _grupo_cashback(categoria, chaves)


def _grupo_cashback(categoria: P.Categoria, chaves: tuple[str, ...]) -> None:
    """Uma categoria: o titulo por cima, um campo por destinatario embaixo.

    A CATEGORIA VEM DE `P.CATEGORIAS`, e nao de literais aqui: `unidade` e
    atributo DECLARADO por categoria (§5.13, V3) e escrever "par" a mao neste
    arquivo seria inferir a unidade fora do lugar em que ela e declarada — a
    porta dos fundos exata que a §5.13 fecha.

    O rotulo de cada campo e VISIVEL e diz "Consultor · dianteiro" — o
    destinatario mais a categoria, e nada alem. A unidade nao entra nele porque
    ja esta na linha de cima; a categoria entra porque sem ela o rotulo seria
    ambiguo entre os dois grupos para quem chega no campo por leitor de tela,
    que nao le o titulo da linha de cima ao tabular (§9.6). Nenhum dos dois
    rotulos quebra em duas linhas na largura de um terco de cartao.

    O SUBTOTAL nao aparece com a linha vazia, pela mesma razao dos outros
    derivados da §5.1: nao existe total de nada.
    """
    st.markdown(
        f'<p class="st-rotulo-categoria"><b>{categoria.rotulo}</b> — valor '
        f"{venda_da_unidade(categoria.unidade)}, por destinatário</p>",
        unsafe_allow_html=True,
    )

    colunas = st.columns(len(chaves), gap="small")
    valores: list[float | None] = []
    for coluna, chave, nome in zip(colunas, chaves, P.DESTINATARIOS_CASHBACK):
        with coluna:
            valores.append(
                campo_moeda(chave=chave, rotulo=f"{nome} · {categoria.nome}")
            )

    soma = sum(valor for valor in valores if valor)
    if soma:
        st.markdown(
            f'<p class="st-derivado">'
            f"{total_derivado_cashback(soma, categoria.unidade)}</p>",
            unsafe_allow_html=True,
        )

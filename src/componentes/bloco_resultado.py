"""§5.5 reescrita por D21 — o resultado em TRES cartoes.

    ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
    │ FATURAMENTO ADICIONAL │ │ MARGEM DE CONTRIB.    │ │ MARK UP DA OPERAÇÃO   │
    │ R$ 249.372            │ │ R$ 141.480            │ │ 108%                  │
    │ R$ 20.781 por mês     │ │ R$ 11.790 por mês     │ │ (fat. − custo)÷ custo │
    └───────────────────────┘ └───────────────────────┘ └───────────────────────┘

A ORDEM E NORMATIVA e foi pedida pelo cliente em 27/08/2026, nesta sequencia:
faturamento adicional, margem de contribuicao adicional, mark up da operacao.

O QUE MUDOU EM RELACAO A VERSAO ANTERIOR, e vale saber por que:

  - a TRADUCAO em escala humana ("3 a cada 10 carros que entram na oficina", em
    48px) SAIU DA TELA. Ela era o primeiro elemento e o maior, por exigencia da
    §5.5 e do P2 — o argumento era que "R$ 1,2 milhao por ano" e rejeitado pelo
    cerebro antes de ser avaliado, enquanto "3 a cada 10 carros" e conferido
    pela intuicao em dois segundos. Ela CONTINUA no PDF, no painel de formula e
    na faixa do vendedor; so a tela deixou de abrir por ela (D21.2)
  - o FATURAMENTO virou manchete. A §4 do DESIGN diz que faturamento entra "so
    em linha secundaria, NUNCA como manchete — o resultado e lido em margem".
    Divergencia declarada em D21.1, com a consequencia registrada: a curva do
    grafico plota MARGEM, portanto ela e o gemeo do SEGUNDO cartao, nao do
    primeiro, e o titulo do grafico diz qual grandeza esta plotada
  - o estado vazio saiu daqui. O vazio da tela agora e a propria area de campos
    com o botao desabilitado; este bloco so e desenhado quando ha resultado

REGRAS QUE CONTINUAM VALENDO INTEGRALMENTE:

  - NENHUM numero em vermelho, nem quando negativo (§3.1.2, §13.1): numero
    financeiro em vermelho le como prejuizo, que e o oposto do que o pitch
    afirma. O destaque do primeiro cartao e o cartao ESCURO (D6, 17,9:1), nao
    preenchimento vermelho
  - NAO USE st.metric — nao chega ao tamanho que a leitura a 1 m exige
  - o rotulo nomeia SO a conta que foi feita (§4, §6.1.7). "Mark up" nao e
    "margem" e nao e "lucro": o cartao diz `(faturamento − custo) ÷ custo`
    embaixo do numero para que a conta seja lida junto com ele. Desde D27 esse
    apoio vale MAIS, e nao menos: o mark up passou a sair em percentual, e um
    percentual ao lado de duas colunas de reais convida a leitura de margem
    percentual — que divide pelo faturamento e da outro numero
  - o cashback ACRESCENTA uma linha e nunca altera nenhum dos tres numeros
"""

from __future__ import annotations

import streamlit as st

from src import formato
from src import parametros as P
from src.calculo import MESES_NO_ANO, Resultado, rotulo_do_resultado

CHAVE_CONTAINER = "resultado"


def bloco(r: Resultado) -> None:
    """Desenha o resultado. Nada e desenhado sem valor anual.

    Quem chama ja garantiu o gate (`estado.resultado_visivel()`), portanto na
    pratica `r.anual` existe sempre aqui. A guarda fica porque um resultado
    parcial desenhado pela metade e pior do que nenhum.
    """
    if r.anual is None:
        return

    with st.container(key=CHAVE_CONTAINER):
        _cartoes(r)
        _nota_do_grupo(r)
        _linhas_de_apoio(r)
        _cashback(r)
        _hoje_versus_refil(r)


# ---------------------------------------------------------------------------
# Os tres cartoes
# ---------------------------------------------------------------------------


def _cartao(rotulo: str, valor: str, apoio: str, principal: bool = False) -> str:
    classe = "st-cartao st-cartao--principal" if principal else "st-cartao"
    return (
        f'<div class="{classe}">'
        f'<span class="st-cartao-rotulo">{rotulo}</span>'
        f'<span class="st-cartao-valor">{valor}</span>'
        f'<span class="st-cartao-apoio">{apoio}</span>'
        f"</div>"
    )


def _cartao_sem_numero(rotulo: str, motivo: str) -> str:
    """Cartao que declara por que nao ha numero — nunca um numero inventado.

    §6.1.9 proibe travessao no lugar de moeda e P9 proibe default zero. Um mark
    up de 1,0 significaria "vende ao preco de custo", que e uma afirmacao que
    ninguem fez.
    """
    return (
        f'<div class="st-cartao">'
        f'<span class="st-cartao-rotulo">{rotulo}</span>'
        f'<span class="st-cartao-apoio">{motivo}</span>'
        f"</div>"
    )


def _cartoes(r: Resultado) -> None:
    """A ORDEM DESTA TUPLA E A ORDEM DA TELA. Nao reordene sem trocar D21.

    `test_T1_ordem_dos_tres_cartoes_e_a_hierarquia` le esta funcao por AST e
    reprova se os tres rotulos sairem de ordem — e por isso que o cartao do
    mark up e montado por uma funcao propria, abaixo: manter o `if` aqui
    colocaria a palavra "Mark up" antes de "Faturamento" na fonte.
    """
    faturamento_mensal = r.faturamento_refil or 0.0
    faturamento_anual = faturamento_mensal * MESES_NO_ANO

    colunas = st.columns(3, gap="small")
    cartoes = (
        _cartao(
            "Faturamento adicional",
            formato.moeda_agregada(faturamento_anual),
            f"{formato.moeda_agregada(faturamento_mensal)} por mês",
            principal=True,
        ),
        _cartao(
            "Margem de contribuição adicional",
            formato.moeda_agregada(r.anual),
            f"{formato.moeda_agregada(r.incremental_mensal)} por mês",
        ),
        _cartao_markup(r),
    )

    for coluna, cartao in zip(colunas, cartoes):
        with coluna:
            st.markdown(cartao, unsafe_allow_html=True)


def _cartao_markup(r: Resultado) -> str:
    # D27: em PERCENTUAL, e nao mais como multiplo. O apoio nomeia a conta, e
    # nao e decoracao (§4): "108%" ao lado de dois valores em reais convida a
    # leitura de MARGEM percentual, que e outra conta — `(faturamento - custo) /
    # faturamento` — e daria 52% no mesmo cenario.
    if r.markup_operacao is not None:
        return _cartao(
            "Mark up da operação",
            formato.markup_percentual(r.markup_operacao),
            "(faturamento − custo) ÷ custo",
        )
    # Acontece quando o custo total da operacao e zero — nao ha por que
    # dividir. Nao existe piso de preco (decisao F em aberto), portanto custo
    # zero passa pelos campos.
    return _cartao_sem_numero(
        "Mark up da operação", "sem custo total para dividir"
    )


def _nota_do_grupo(r: Resultado) -> None:
    """Qual periodo e qual conta — os dois em uma linha, embaixo dos cartoes.

    "Valores anuais" nao e enfeite: os numeros grandes sao de 12 meses e o
    apoio de cada cartao e mensal. Sem a nota, os dois se confundem.
    """
    st.markdown(
        f'<p class="st-legenda-bloco">Valores anuais · '
        f"{rotulo_do_resultado(r)} · {P.rotulo_do_anual()}</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Linhas de apoio
# ---------------------------------------------------------------------------


def _linhas_de_apoio(r: Resultado) -> None:
    """O volume que produz os numeros acima.

    O faturamento SAIU desta linha: ele virou o primeiro cartao (D21.1), e
    repeti-lo aqui seria o mesmo numero duas vezes na mesma tela.
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
    if partes:
        st.markdown(
            f'<p class="st-linha-apoio">{" · ".join(partes)}</p>',
            unsafe_allow_html=True,
        )


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

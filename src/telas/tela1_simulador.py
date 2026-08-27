"""Tela 1 — Simulador de viabilidade. Reformada por D21 (27/08/2026).

MODELO NOVO, pedido pelo cliente com base num simulador de juros compostos:

    1. a tela abre SO COM OS CAMPOS, distribuidos pela largura toda
    2. durante o preenchimento NADA e calculado e nada aparece
    3. um botao "Mostrar Resultado" habilita quando os obrigatorios estao
       preenchidos, e revela o resultado ABAIXO dos campos
    4. o resultado sao TRES numeros — faturamento adicional, margem de
       contribuicao adicional, mark up da operacao — e depois grafico e tabela

O QUE ISSO SUBSTITUI, e o que se perdeu (registro completo em D21):

  - as DUAS COLUNAS (`st.columns([5, 7])`, §3.3) acabaram. Nao existe mais "o
    lado do vendedor" a esquerda e "o lado que o cliente le" a direita: a tela
    tem uma coluna de campos em largura total e o resultado embaixo. Com isso
    morre D3 (a reordenacao por CSS abaixo de 1024px) e enfraquece a mitigacao
    de D11, que dizia que o slider do traseiro era inofensivo porque vivia na
    coluna do vendedor
  - a TRADUCAO em escala humana saiu da tela (segue no PDF, no painel de formula
    e na faixa do vendedor)
  - o expander "Ajustes avancados" (§5.10) acabou: consultores, dias uteis e a
    grade de cashback estao na superficie primaria
  - os TILES DE KPI foram removidos
  - o teto de SEIS campos primarios (§6.1.4) foi abandonado

O QUE FOI PRESERVADO DE PROPOSITO, e nao e detalhe:

  - a FAIXA DE PREMISSAS aparece SEMPRE, antes do clique, na area de campos. Ela
    e o que declara "sem canibalizacao — todo refil e venda nova" e o traseiro
    fora da conta. Sem ela o numero passa a ser lido como promessa, e a §5.10
    proibe premissa que muda o resultado sem aparecer
  - o TRASEIRO continua OPCIONAL. Vazio significa "fora da conta" e e um estado
    legitimo (§5.13) — o botao nao o exige
  - os presets seguem com 96px e continuam sendo o protagonista do cenario (§5.3)
  - a faixa do vendedor continua no rodape, ilegivel a um metro (§5.9)
  - nenhum aviso bloqueia o calculo (§6.1.8): o botao gateia a EXIBICAO, e a
    plausibilidade continua avisando so na faixa do vendedor

A TELA 1 NAO LE PLANILHA E NAO FAZ NENHUMA REQUISICAO (P11, §7.1). Repare nos
imports: nao ha `carregar_snapshot`, `requests`, `pandas.read_*` nem `openpyxl`.
"""

from __future__ import annotations

import streamlit as st

from src import estado, formato, plausibilidade
from src import parametros as P
from src.calculo import calcular
from src.componentes import (
    ajustes_avancados,
    bloco_resultado,
    botoes_cenario,
    faixa_premissas,
    faixa_vendedor,
    grafico_sensibilidade,
    painel_formula,
    slider_ajuste_fino,
)
from src.componentes.campo_unidade import campo_moeda, campo_quantidade
from src.componentes.exportador_pdf import bloco_exportar
from src.icones import svg

# Nome curto de cada obrigatorio, para a linha "falta preencher".
#
# NAO e o rotulo do campo: o rotulo carrega a unidade e e longo de proposito
# (§5.1). Aqui o que serve e o nome mais curto que ainda identifica o campo, em
# minuscula, para caber numa linha so.
NOMES_CURTOS: dict[str, str] = {
    estado.K_PASSAGENS: "passagens por mês",
    estado.K_ORIGINAIS: "palhetas vendidas por mês",
    estado.K_PRECO_ORIG: "preço da original",
    estado.K_CUSTO_ORIG: "custo da original",
    estado.K_PRECO_D: "preço do dianteiro",
    estado.K_CUSTO_D: "custo do dianteiro",
}


def _secao(icone: str, titulo: str, nota: str = "") -> None:
    extra = f'<span class="st-secao-nota">{nota}</span>' if nota else ""
    st.markdown(
        f'<div class="st-secao">{svg(icone)}<span>{titulo}</span>{extra}</div>',
        unsafe_allow_html=True,
    )


def renderizar() -> None:
    estado.iniciar()

    _campos()

    # A faixa de premissas ANTES do botao, e portanto antes de existir qualquer
    # numero na tela: ela declara as premissas da conta, nao o resultado dela.
    entradas = estado.ler_entradas()
    resultado = calcular(entradas)
    faixa_premissas.faixa(entradas, resultado)

    _botao_de_acao()

    # ==================================================================
    # O RESULTADO — so depois do toque explicito, e so com os
    # obrigatorios preenchidos. Ver estado.resultado_visivel().
    # ==================================================================
    if estado.resultado_visivel():
        bloco_resultado.bloco(resultado)

        with st.container(key="grafico"):
            grafico_sensibilidade.grafico(entradas, resultado)
        grafico_sensibilidade.tabela_da_curva(entradas, resultado)

        painel_formula.painel(entradas, resultado)
        bloco_exportar(entradas, resultado)

    # A faixa e a ULTIMA coisa do script: precisa refletir tudo que os campos
    # acabaram de mudar.
    faixa_vendedor.faixa(
        plausibilidade.avaliar(entradas, resultado),
        meta=[
            f"aproveitamento dianteiro {formato.percentual(entradas.aproveitamento_dianteiro)}",
            P.rotulo_do_anual(),
        ],
    )
    faixa_vendedor.botao_novo_cliente()


# ---------------------------------------------------------------------------
# A AREA DE CAMPOS — largura total, um cartao por pergunta
# ---------------------------------------------------------------------------


def _campos() -> None:
    """Cinco cartoes, cada um respondendo uma pergunta do vendedor.

    Cada cartao e um `st.container(key=...)` — NAO um `<div>` injetado. Um
    markdown com `<div class="...">` abre e FECHA a propria div: os campos
    seguintes ficam fora dela, o CSS nao pega, e o "cartao" renderiza como uma
    pilula vazia. Ja aconteceu duas vezes nesta construcao (docs/DIVERGENCIAS
    §4.2 e §4.8).

    VOCABULARIO: nenhum rotulo fala do cliente em terceira pessoa (D14). O
    tablet esta inclinado NA DIRECAO dele — "palhetas que ele vende" e uma frase
    sobre alguem que esta lendo a frase.
    """
    _bloco_operacao()
    _bloco_hoje()
    _bloco_refil()
    _bloco_cashback()
    _bloco_cenario()


def _bloco_operacao() -> None:
    _secao("operacao", "A operação da concessionária", "informado na reunião")

    with st.container(key="entrada_operacao"):
        col_a, col_b, col_c, col_d = st.columns(4, gap="medium")

        with col_a:
            st.number_input(
                "Pontos de venda, no total",
                min_value=1,
                step=1,
                key=estado.K_PONTOS,
            )
        pontos = int(st.session_state.get(estado.K_PONTOS) or 1)

        with col_b:
            # §5.1: o total derivado aparece SEMPRE que ha valor, INCLUSIVE
            # quando o multiplicador vale 1. Sumir com ele quando o valor e
            # trivial ensina o cliente a nao procura-lo quando deixa de ser.
            campo_quantidade(
                chave=estado.K_PASSAGENS,
                rotulo="Passagens por mês, por ponto de venda",
                derivado=lambda v: formato.total_derivado_passagens(v, pontos),
            )

        # Os dois que vinham de Ajustes avancados, um por coluna. Ficam no fim
        # da linha porque sao os campos mais discretos da tela: nenhum dos dois
        # entra em conta de margem.
        with col_c:
            ajustes_avancados.campo_consultores()
        with col_d:
            ajustes_avancados.campo_dias_uteis()

        st.caption(ajustes_avancados.NOTA_OPERACAO)


def _bloco_hoje() -> None:
    _secao("hoje", "A venda de palhetas hoje", "a âncora do resultado")

    with st.container(key="entrada_hoje"):
        col_a, col_b, col_c = st.columns(3, gap="medium")
        pontos = int(st.session_state.get(estado.K_PONTOS) or 1)

        with col_a:
            campo_quantidade(
                chave=estado.K_ORIGINAIS,
                rotulo="Palhetas vendidas por mês, por ponto de venda",
                derivado=lambda v: formato.total_derivado_palhetas(v, pontos),
            )
        with col_b:
            campo_moeda(
                chave=estado.K_PRECO_ORIG,
                rotulo="Preço da palheta original cobrado hoje",
                legenda=(
                    "Confira o preço da original ao vivo na aba "
                    "<b>Preço original</b>."
                ),
            )
        with col_c:
            campo_moeda(
                chave=estado.K_CUSTO_ORIG,
                rotulo="Custo da palheta original",
                legenda=(
                    "Entra na margem da original e no <b>mark up da "
                    "operação</b> — por isso é obrigatório."
                ),
            )


def _bloco_refil() -> None:
    # PRECO TABELADO (D21): a versao anterior dizia que preco e custo do refil
    # eram "negociados caso a caso". O cliente corrigiu — o preco e de tabela, e
    # nenhum texto da tela pode sugerir negociacao por cliente.
    _secao("produto", "O refil Suicatech", "preço de tabela")

    with st.container(key="entrada_dianteiro"):
        st.markdown(
            '<p class="st-rotulo-categoria"><b>Dianteiro · par</b>'
            " — duas medidas, vendido em par</p>",
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            campo_moeda(
                chave=estado.K_PRECO_D,
                rotulo="Preço ao consumidor final, por par (dianteiro)",
            )
        with col_b:
            campo_moeda(
                chave=estado.K_CUSTO_D,
                rotulo="Custo de aquisição, por par (dianteiro)",
            )

    # §5.13: preco e custo PROPRIOS do traseiro — e proibido derivar do
    # dianteiro por qualquer fator, inclusive / 2.
    with st.container(key="entrada_traseiro"):
        st.markdown(
            '<p class="st-rotulo-categoria"><b>Traseiro · unidade</b>'
            " — lâmina única, preço próprio</p>",
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            campo_moeda(
                chave=estado.K_PRECO_T,
                rotulo="Preço ao consumidor final, por unidade (traseiro)",
            )
        with col_b:
            campo_moeda(
                chave=estado.K_CUSTO_T,
                rotulo="Custo de aquisição, por unidade (traseiro)",
                legenda=(
                    "Preço e custo vêm da tabela Suicatech vigente. Enquanto "
                    "estiverem vazios, o traseiro fica <b>fora da conta</b>, "
                    "nunca estimado."
                ),
            )

        # O APROVEITAMENTO DO TRASEIRO fica AQUI, junto do preco e do custo da
        # mesma categoria — e nao junto dos presets do dianteiro. Os presets sao
        # o protagonista do cenario (§5.3) e um segundo controle grande ao lado
        # deles convidaria o risco n. 1 do plano.
        campo_percentual_traseiro()


def _bloco_cashback() -> None:
    _secao("preco", "Cashback", "pago pela Suicatech")

    with st.container(key="entrada_cashback"):
        ajustes_avancados.cashback()


def _bloco_cenario() -> None:
    _secao("cenario", "O cenário de aproveitamento", "aperte um, ou ajuste no slider")

    # O protagonista (§5.3). Recebe as entradas so para derivar qual preset esta
    # ativo — o estado ativo NAO e guardado.
    botoes_cenario.botoes(estado.ler_entradas())
    slider_ajuste_fino.slider()


# ---------------------------------------------------------------------------
# O BOTAO — o gate da exibicao
# ---------------------------------------------------------------------------


def _botao_de_acao() -> None:
    """"Mostrar Resultado", habilitado so com os obrigatorios preenchidos.

    POR QUE `disabled=` AQUI, quando o projeto o evita em todo o resto: a
    §10-F argumenta que "um campo desabilitado com rotulo promete
    funcionalidade que nao existe; ausencia nao promete nada". Aqui e o
    contrario — o botao PRECISA estar visivel desde o inicio, porque ele e o
    que explica o modelo da tela ("preencha e aperte"). Um botao que aparece do
    nada quando o sexto campo e preenchido nao ensina nada.

    E o que falta e DITO, em linha discreta, sem `st.warning` (proibido, §12) e
    sem vocabulario de alerta (§4: nada de "invalido", "atencao", "erro").
    """
    with st.container(key="acao"):
        completo = estado.esta_completo()

        if estado.resultado_visivel():
            # Com o resultado na tela, "Mostrar" nao faria nada. O caminho de
            # volta para a tela de campos e util na reuniao: recomeca o pitch
            # sem apagar nada do que foi digitado.
            st.button(
                "Esconder resultado",
                key="btn_esconder",
                on_click=estado.esconder_resultado,
                width="stretch",
            )
            return

        st.button(
            "Mostrar Resultado",
            key="btn_mostrar",
            type="primary",
            disabled=not completo,
            on_click=estado.mostrar_resultado,
            width="stretch",
        )

        if not completo:
            faltam = " · ".join(
                NOMES_CURTOS.get(chave, chave) for chave in estado.faltando()
            )
            st.markdown(
                f'<p class="st-acao-falta">Falta preencher: {faltam}</p>',
                unsafe_allow_html=True,
            )


def campo_percentual_traseiro() -> None:
    """Aproveitamento traseiro: slider para arrastar + atalhos dos presets.

    Dois caminhos para trocar o valor, porque "facil de trocar" num tablet e
    diferente de "facil de trocar" no teclado: o slider resolve o ajuste
    grosso com o dedo, e os tres atalhos levam direto aos valores da carteira.

    PROCEDENCIA (mudou em D21): as tres faixas do traseiro — 5%, 10% e 18% —
    passaram a ser declaradas como medidas na carteira. Antes, so os 10% eram
    medidos e os extremos eram derivados do dianteiro na mesma proporcao, e o
    atalho dizia qual era qual. A distincao `◆ carteira` / `≈ derivado` continua
    montada no codigo (marcador_procedencia): ela volta a aparecer no dia em que
    um preset voltar a ser derivado.
    """
    lo, hi = P.SLIDER_DOMINIO
    st.slider(
        "Aproveitamento traseiro",
        min_value=lo,
        max_value=hi,
        key=estado.K_CONV_T,
        format="%d%%",
        help=(
            "Quanto das passagens converte em refil traseiro. Normalmente é "
            "menor que o dianteiro."
        ),
    )

    with st.container(key="atalhos_traseiro"):
        colunas = st.columns(len(P.PRESETS), gap="small")
        for coluna, preset in zip(colunas, P.PRESETS):
            pp = int(round(preset.traseiro * 100))
            with coluna:
                st.button(
                    f"{pp}%",
                    key=f"btn_traseiro_{preset.nome}",
                    width="stretch",
                    on_click=estado.aplicar_traseiro,
                    args=(preset.traseiro,),
                    help="medido na carteira Suicatech",
                )
    st.markdown(
        f'<p class="st-legenda-bloco">{P.LEGENDA_PRESETS_TRASEIRO}.</p>',
        unsafe_allow_html=True,
    )

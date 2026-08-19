"""Tela 1 — Simulador de viabilidade (DESIGN.md §6.1).

OBJETIVO (§6.1.1): fazer o cliente pegar o tablet. Chegar num numero anual de
margem de contribuicao que ele mesmo ajudou a montar, com uma traducao por
passagem que ele valide por intuicao, e com o controle de cenario AO ALCANCE DA
MAO DELE.

ORDEM DO SCRIPT = ORDEM DE LEITURA (§6.1.3). Em Streamlit a hierarquia visual E
a ordem das chamadas, e a §6.1.2 fixa o que o cliente ve primeiro:
  1. a traducao em escala humana — 48px
  2. os tres botoes de cenario — 96px, imediatamente acima do resultado
  3. o valor anual — 36px
  4. o mensal, a faixa de premissas e os tiles
  5. o grafico de sensibilidade
  6. a coluna de entradas, a esquerda — e o lado do VENDEDOR
  7. a faixa do vendedor, no rodape — o cliente nao le a 1 m, e assim que deve ser

A ANCORA (mudanca de 11/08/2026, decisao do cliente): em vez de pedir "margem
de contribuicao mensal atual com palhetas" — pergunta que gerente de pos-venda
nao responde de cabeca — o app pergunta o que ele sabe de cor:

    quantas palhetas voce vende por mes, e a quanto

O preco da original vem da aba "Preco original", consultado ao vivo. O custo
dela e opcional; sem ele nao existe incremental e o rotulo do resultado diz
"margem de contribuicao do refil". O app nunca ASSUME uma margem para a original.

DENSIDADE: a §6.1.4 fixa 6 campos. Com o traseiro trazido para a superficie
primaria a pedido do cliente, e com a ancora virando tres campos, o teto passa a
ser respeitado por BLOCO, nao pela tela — cada bloco tem no maximo tres campos e
um titulo que diz o que ele responde. Registrado em docs/DIVERGENCIAS.md (D8).

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
    tiles_kpi,
)
from src.componentes.campo_unidade import campo_moeda, campo_quantidade
from src.componentes.exportador_pdf import bloco_exportar
from src.icones import svg


def _secao(icone: str, titulo: str, nota: str = "") -> None:
    extra = f'<span class="st-secao-nota">{nota}</span>' if nota else ""
    st.markdown(
        f'<div class="st-secao">{svg(icone)}<span>{titulo}</span>{extra}</div>',
        unsafe_allow_html=True,
    )


def renderizar() -> None:
    estado.iniciar()

    with st.container(key="corpo"):
        col_entradas, col_resultado = st.columns([5, 7], gap="large")

        # ==============================================================
        # COLUNA ESQUERDA (5/12) — o lado do VENDEDOR, escala de 40 cm.
        # Declarada primeiro; abaixo de 1024px o CSS a manda para baixo (D3,
        # §8), porque em retrato quem le e o cliente.
        # ==============================================================
        with col_entradas:
            _entradas()

        # ==============================================================
        # COLUNA DIREITA (7/12) — o lado que o CLIENTE le, escala de 1 m.
        # E a maior porque e a que precisa dos 48px (§3.3).
        # ==============================================================
        with col_resultado:
            # Protagonista: acima do bloco de resultado, ao alcance de quem
            # esta do outro lado da mesa (§5.3). Recebe as entradas so para
            # derivar qual preset esta ativo — o estado ativo nao e guardado.
            botoes_cenario.botoes(estado.ler_entradas())
            slider_ajuste_fino.slider()

            # Reler DEPOIS dos controles: o slider acabou de escrever no
            # session_state ao ser instanciado neste mesmo rerun.
            entradas = estado.ler_entradas()
            resultado = calcular(entradas)

            bloco_resultado.bloco(resultado)
            faixa_premissas.faixa(entradas, resultado)
            tiles_kpi.tiles(entradas, resultado)

            with st.container(key="grafico"):
                grafico_sensibilidade.grafico(entradas, resultado)
            grafico_sensibilidade.tabela_da_curva(entradas, resultado)
            painel_formula.painel(entradas, resultado)
            bloco_exportar(entradas, resultado)

    # ==================================================================
    # Largura total: Ajustes avancados e a faixa do vendedor
    # ==================================================================
    ajustes_avancados.painel()

    # A faixa e a ULTIMA coisa do script: precisa refletir tudo que os
    # avancados acabaram de mudar.
    entradas = estado.ler_entradas()
    resultado = calcular(entradas)
    faixa_vendedor.faixa(
        plausibilidade.avaliar(entradas, resultado),
        meta=[
            f"aproveitamento dianteiro {formato.percentual(entradas.aproveitamento_dianteiro)}",
            P.rotulo_do_anual(),
        ],
    )
    faixa_vendedor.botao_novo_cliente()


def _entradas() -> None:
    """Quatro cartoes, cada um respondendo uma pergunta do vendedor.

    Cada cartao e um `st.container(key=...)` — NAO um `<div>` injetado. Um
    markdown com `<div class="...">` abre e FECHA a propria div: os campos
    seguintes ficam fora dela, o CSS nao pega, e o "cartao" renderiza como uma
    pilula vazia. Ja aconteceu duas vezes nesta construcao (docs/DIVERGENCIAS
    §4.2 e §4.8).
    """

    # --- Bloco A — a operacao da concessionaria ---------------------------
    #
    # VOCABULARIO: nenhum rotulo fala do cliente em terceira pessoa. O tablet
    # esta inclinado NA DIRECAO dele — "palhetas que ele vende" e uma frase
    # sobre alguem que esta lendo a frase. Os rotulos sao impessoais
    # ("palhetas vendidas por mês"), e onde o texto se dirige a alguem, ele se
    # dirige ao cliente em segunda pessoa.
    _secao("operacao", "A operação da concessionária", "informado na reunião")

    with st.container(key="entrada_operacao"):
        st.number_input(
            "Pontos de venda, no total",
            min_value=1,
            step=1,
            key=estado.K_PONTOS,
        )
        pontos = int(st.session_state.get(estado.K_PONTOS) or 1)

        # §5.1: o total derivado aparece SEMPRE que ha valor, INCLUSIVE quando o
        # multiplicador vale 1. Sumir com ele quando o valor e trivial ensina o
        # cliente a nao procura-lo quando deixa de ser.
        campo_quantidade(
            chave=estado.K_PASSAGENS,
            rotulo="Passagens por mês, por ponto de venda",
            derivado=lambda v: formato.total_derivado_passagens(v, pontos),
        )

    # --- Bloco B — a venda de palhetas hoje (a ancora) --------------------
    _secao("hoje", "A venda de palhetas hoje", "a âncora do resultado")

    with st.container(key="entrada_hoje"):
        campo_quantidade(
            chave=estado.K_ORIGINAIS,
            rotulo="Palhetas vendidas por mês, por ponto de venda",
            derivado=lambda v: formato.total_derivado_palhetas(v, pontos),
        )
        campo_moeda(
            chave=estado.K_PRECO_ORIG,
            rotulo="Preço da palheta original cobrado hoje",
        )
        campo_moeda(
            chave=estado.K_CUSTO_ORIG,
            rotulo="Custo da palheta original (opcional)",
            legenda=(
                "Confira o preço da original ao vivo na aba "
                "<b>Preço original</b>. Sem o custo dela não existe margem da "
                "original para comparar, e o resultado é rotulado como margem "
                "<b>do refil</b>, não incremental."
            ),
        )

    # --- Bloco C — o refil, dianteiro -------------------------------------
    _secao("produto", "O refil Suicatech", "preço desta negociação")

    with st.container(key="entrada_dianteiro"):
        st.markdown(
            '<p class="st-rotulo-categoria"><b>Dianteiro · par</b>'
            " — duas medidas, vendido em par</p>",
            unsafe_allow_html=True,
        )
        campo_moeda(
            chave=estado.K_PRECO_D,
            rotulo="Preço ao consumidor final, por par (dianteiro)",
        )
        campo_moeda(
            chave=estado.K_CUSTO_D,
            rotulo="Custo de aquisição, por par (dianteiro)",
        )

    # --- Bloco D — o refil, traseiro --------------------------------------
    #
    # O TRASEIRO na superficie primaria, a pedido do cliente (11/08/2026);
    # antes vivia em Ajustes avancados. §5.13: preco e custo PROPRIOS — e
    # proibido derivar do dianteiro por qualquer fator, inclusive / 2.
    with st.container(key="entrada_traseiro"):
        st.markdown(
            '<p class="st-rotulo-categoria"><b>Traseiro · unidade</b>'
            " — lâmina única, preço próprio</p>",
            unsafe_allow_html=True,
        )
        campo_moeda(
            chave=estado.K_PRECO_T,
            rotulo="Preço ao consumidor final, por unidade (traseiro)",
        )
        campo_moeda(
            chave=estado.K_CUSTO_T,
            rotulo="Custo de aquisição, por unidade (traseiro)",
            legenda=(
                "Preço e custo são negociados caso a caso — abrem em branco de "
                "propósito. Enquanto estiverem vazios, o traseiro fica "
                "<b>fora da conta</b>, nunca estimado."
            ),
        )

        # O APROVEITAMENTO DO TRASEIRO na superficie primaria, a pedido do
        # cliente (11/08/2026): "normalmente elas tem aproveitamento menor,
        # algo em torno de 10% — deixe facil de trocar o valor".
        #
        # Fica AQUI, na coluna do vendedor, e nao na coluna da direita: o
        # protagonista da tela e o controle de cenario do dianteiro (§5.3), e um
        # segundo slider do lado do cliente competiria com ele — que e
        # exatamente o convite ao risco n. 1 do plano. Aqui ele e controle de
        # operacao, ao lado do preco e do custo da mesma categoria.
        campo_percentual_traseiro()

    st.caption(f"Demais premissas em Ajustes avançados · {P.rotulo_do_anual()}")


def campo_percentual_traseiro() -> None:
    """Aproveitamento traseiro: slider para arrastar + atalhos dos presets.

    Dois caminhos para trocar o valor, porque "facil de trocar" num tablet e
    diferente de "facil de trocar" no teclado: o slider resolve o ajuste
    grosso com o dedo, e os tres atalhos levam direto aos valores da carteira.

    A procedencia continua declarada: so os 10% sao medidos; 7% e 13% sao
    DERIVADOS do dianteiro na mesma proporcao (§5.7, §10-H). O atalho nao
    apaga essa distincao — a faixa de premissas segue mostrando
    `≈ derivado` quando o valor ativo e um dos extremos.
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
            "menor que o dianteiro: 10% é a média medida na carteira."
        ),
    )

    with st.container(key="atalhos_traseiro"):
        colunas = st.columns(len(P.PRESETS), gap="small")
        for coluna, preset in zip(colunas, P.PRESETS):
            pp = int(round(preset.traseiro * 100))
            medido = preset.origem_traseiro == "carteira_medida"
            with coluna:
                st.button(
                    f"{pp}%",
                    key=f"btn_traseiro_{preset.nome}",
                    width="stretch",
                    on_click=estado.aplicar_traseiro,
                    args=(preset.traseiro,),
                    help=(
                        "medido na carteira Suicatech"
                        if medido
                        else "derivado do dianteiro na mesma proporção — não medido"
                    ),
                )
    st.markdown(
        f'<p class="st-legenda-bloco">{P.LEGENDA_PRESETS_TRASEIRO}.</p>',
        unsafe_allow_html=True,
    )

"""Componente +18 — ExportadorPDF. ACRESCIMO DECLARADO (docs/DIVERGENCIAS.md).

O DESIGN v5 nao especifica este componente porque a §5 dele cobre so a Tela 1 e
o PDF esta na Fase 3 do plano. O cliente pediu que entre nesta entrega.

GERADO NO SERVIDOR (plano §6.1: "PDF gerado no servidor (fpdf/reportlab) +
st.download_button — mais simples aqui do que seria no navegador"). Nao ha
geracao no dispositivo nesta stack: o app renderiza no servidor.

PARA QUE ELE EXISTE, alem de entregar um documento ao cliente (plano §3.8):
o PDF carrega identificacao do cliente e os parametros simulados, e e o UNICO
caminho que o plano tem para calibrar os presets com dado proprio — conferir o
realizado em 90 dias contra o simulado. Em dois trimestres isso vira um ativo
comercial, e e a mitigacao de fundo do risco n. 1.

REGRAS QUE O DOCUMENTO OBEDECE:
  - a palavra "lucro" NAO APARECE, em nenhuma flexao (§4, P12, §6.1.9)
  - o CUSTO DO CASHBACK PARA A SUICATECH nao aparece — nao existe nem como
    campo (§6.1.9)
  - o cashback, se ligado, aparece como linha de exibicao declarando quem paga,
    e NAO e descontado de nada
  - o rotulo do resultado nomeia SO o que de fato foi descontado (§6.1.7)
  - o rotulo do anual descreve a conta que foi feita: "ano cheio em regime"
    enquanto rampa e sazonalidade estiverem em aberto (§6.1.5)
  - as decisoes em aberto vao IMPRESSAS no documento. Um PDF que sai da sala
    sem dizer o que ainda nao foi decidido e pior que a tela, porque ninguem
    esta ao lado para explicar
  - MARCA-D'AGUA "documento interno" quando o custo de aquisicao entra no
    documento, porque o custo E o preco de venda da Suicatech e o PDF sai da
    sala (plano §6.3)

O nome do cliente NAO CONTA contra o teto de 6 campos: ele vive nesta area de
exportacao, nao na superficie de pitch (§6.1.4).

D24 — O DOCUMENTO VIROU VISUAL, e o que isso NAO mudou
======================================================

Pedido do cliente em 27/08/2026: *"o PDF tem que ser mais visual. Use os cards
de KPI, graficos, faca cenarios. Deve ser algo que o cliente bata o olho e fique
evidente que e um bom negocio."*

O documento era uma lista de `rotulo ... valor` em duas colunas, da primeira
linha a ultima. Passou a ter DUAS PAGINAS com papeis distintos:

    pagina 1   a leitura de relance: a traducao em escala humana, os TRES
               CARTOES da tela, o comparativo em barras "hoje x com o refil" e
               os TRES CENARIOS medidos, lado a lado
    pagina 2   a auditoria: a curva de sensibilidade inteira, as premissas, o
               preco e o custo de tabela (so em documento interno) e o que
               ainda nao foi decidido

O QUE NAO MUDOU, e e a parte que importa deste item. "Bata o olho e fique
evidente que e um bom negocio" e um pedido de PERSUASAO, e este projeto tem uma
regra dura sobre isso (§4): o app nao promete, e a §12 reprova "ROI", "retorno
garantido" e "estimativa" junto de numero medido. A leitura de relance ficou
mais forte pelo DESENHO — hierarquia, contraste, uma grandeza por elemento —, e
nao por adjetivo. Em particular:

  - o CENARIO PESSIMISTA entra na pagina 1, do mesmo tamanho dos outros dois.
    Um documento que mostrasse so o cenario favoravel seria material de venda,
    e a faixa inteira e o que deixa o gerente escolher em qual acreditar
  - a premissa mais favoravel (sem canibalizacao) continua IMPRESSA, e as
    decisoes em aberto continuam impressas, agora na pagina 2
  - nenhum numero de resultado e vermelho (§13.1). O destaque e superficie
    escura, como na tela (D6)
  - o valor negativo continua saindo com sinal, sem cor de alerta: o plano §1.1
    avisa que margem negativa e possivel, e o documento nao esconde

A TINTA MORA EM `pdf_visual.py`. Este arquivo decide O QUE entra, em que ordem e
com que texto; aquele sabe desenhar cartao, barra e curva e nada mais.
"""

from __future__ import annotations

import io
import unicodedata
from dataclasses import replace
from datetime import date

import streamlit as st
from fpdf import FPDF

from src import formato
from src import parametros as P
from src.calculo import (
    MESES_NO_ANO,
    Entradas,
    Resultado,
    calcular,
    curvas_comparadas,
    preset_ativo,
    rotulo_do_resultado,
)
from src.componentes import marcador_decisao_aberta as aberto
from src.componentes import pdf_visual as visual
from src.css import (
    MARCA_VERMELHO,
    SUPERFICIE_ESCURA,
    TINTA_CLARA,
    TINTA_CLARA_2,
    TINTA_DISCRETA,
    TINTA_PRIMARIA,
    TINTA_SECUNDARIA,
    TRACO,
)
from src.estado import K_NOME_CLIENTE
from src.icones import svg

_LARGURA = 190
_MARGEM_X = 10


def _t(bruto: str) -> str:
    """A fonte nucleo do fpdf2 e Latin-1. Uma porta so para o texto entrar.

    Delega a `pdf_visual.texto`, que TRANSCREVE o que nao cabe em Latin-1 em
    vez de apagar. Antes daquela tabela, um `NFKD` + `ignore` engolia o
    travessao do proprio titulo do documento e deixava "Simulação de
    viabilidade  refil de palhetas", com o buraco no lugar.
    """
    return visual.texto(bruto)


class _Documento(FPDF):
    def __init__(self, interno: bool, cliente: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self._interno = interno
        self._cliente = cliente
        self.set_auto_page_break(auto=True, margin=20)

    def header(self) -> None:
        """Roda em TODA pagina, inclusive nas que a quebra automatica cria.

        A marca-d'agua vem PRIMEIRO, e por isso ela fica atras do conteudo: o
        PDF nao tem camadas, so ordem de escrita. Antes de D24 o documento tinha
        uma pagina so e a marca era desenhada uma vez, em `gerar_pdf`; com duas
        paginas, um documento interno saia com a segunda pagina LIMPA — a pagina
        que carrega o preco e o custo de tabela.
        """
        self._marca_dagua()
        self.set_xy(_MARGEM_X, 8)

        # O logo, se existir em assets/. `fpdf2` aceita o caminho direto; se o
        # arquivo estiver ilegivel seguimos so com o texto — um PDF sem logo e
        # melhor que uma excecao no meio da reuniao.
        from src import marca

        caminho = marca.caminho_do_logo_completo()
        if caminho is not None and caminho.suffix.lower() != ".svg":
            try:
                self.image(str(caminho), x=_MARGEM_X, y=8, h=11)
                self.set_y(8 + 11 + 2)
            except (RuntimeError, OSError, ValueError):
                pass

        self.set_font("Helvetica", "B", 14)
        self.set_text_color(TINTA_PRIMARIA)
        self.cell(
            0,
            7,
            _t("Simulação de viabilidade — refil de palhetas"),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(TINTA_SECUNDARIA)
        linha = f"Suicatech · Intrace AG · gerado em {date.today():%d/%m/%Y}"
        if self._cliente:
            linha = f"{self._cliente} · {linha}"
        self.cell(0, 5, _t(linha), new_x="LMARGIN", new_y="NEXT")

        # Filete de marca, e nao um traco cinza: e o mesmo papel da barra
        # vermelha na borda dos cartoes de campo da tela (D5).
        self.set_draw_color(MARCA_VERMELHO)
        self.set_line_width(0.6)
        self.line(_MARGEM_X, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(TINTA_DISCRETA)
        nota = (
            "Margem de contribuição. Valores simulados a partir de premissas "
            "informadas na reunião."
        )
        if self._interno:
            nota = f"DOCUMENTO INTERNO — contém custo de aquisição. {nota}"
        self.multi_cell(_LARGURA - 12, 3.6, _t(nota), align="L")
        self.set_xy(-_MARGEM_X - 12, -15)
        self.cell(12, 3.6, _t(f"{self.page_no()}/{{nb}}"), align="R")

    def _marca_dagua(self) -> None:
        """Marca-d'agua diagonal quando o documento carrega custo."""
        if not self._interno:
            return
        with self.rotation(45, x=105, y=150):
            self.set_font("Helvetica", "B", 46)
            self.set_text_color(230, 230, 226)
            self.text(38, 150, _t("DOCUMENTO INTERNO"))
        self.set_text_color(TINTA_PRIMARIA)

    # -- helpers de conteudo ------------------------------------------------

    def secao(self, titulo: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(TINTA_PRIMARIA)
        self.cell(0, 6.5, _t(titulo), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(TRACO)
        self.set_line_width(0.3)
        self.line(_MARGEM_X, self.get_y(), 200, self.get_y())
        self.ln(2)

    def linha(self, rotulo: str, valor: str, forte: bool = False) -> None:
        """Rotulo a esquerda, valor a direita. O VALOR QUEBRA quando nao cabe.

        Era um `cell` de largura 0, que nao quebra: ele escreve ate a margem e
        o resto some. A linha da decisao G saia "bloco de investimento ausent",
        com a ultima letra cortada — e ela e uma das que a §5.12 manda imprimir
        justamente porque ninguem estara ao lado para completar a frase.
        """
        topo = self.get_y()
        coluna = 95.0

        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(TINTA_SECUNDARIA)
        self.set_xy(_MARGEM_X, topo)
        self.multi_cell(
            coluna, 5.6, _t(rotulo), align="L", new_x="RIGHT", new_y="TOP"
        )
        fim_do_rotulo = self.get_y()

        # align="L" explicito: o default do `multi_cell` do fpdf2 e JUSTIFICADO,
        # e uma linha justificada de 95 mm sai com vaos enormes entre palavras.
        self.set_font("Helvetica", "B" if forte else "", 10.5 if forte else 9.5)
        self.set_text_color(TINTA_PRIMARIA)
        self.set_xy(_MARGEM_X + coluna, topo)
        self.multi_cell(_LARGURA - coluna, 5.6, _t(valor), align="L")

        self.set_y(max(self.get_y(), fim_do_rotulo, topo + 5.6))
        self.set_x(_MARGEM_X)

    def paragrafo(self, texto: str, tamanho: float = 8.5) -> None:
        self.set_font("Helvetica", "", tamanho)
        self.set_text_color(TINTA_SECUNDARIA)
        self.set_x(_MARGEM_X)
        self.multi_cell(_LARGURA, 4.2, _t(texto), align="L")
        self.ln(1)


def gerar_pdf(e: Entradas, r: Resultado, cliente: str = "") -> bytes:
    """Monta o PDF do cenario simulado. Aritmetica ja resolvida em `r`.

    Duas paginas com papeis distintos (D24): a primeira e a leitura de relance,
    a segunda e a auditoria. Sem resultado nao existe a primeira — o documento
    abre dizendo o que falta, e nao com um cartao de R$ 0.
    """
    interno = (
        e.custo_dianteiro is not None
        or e.custo_traseiro is not None
        or e.custo_original is not None
    )
    doc = _Documento(interno=interno, cliente=cliente)
    doc.add_page()

    if r.anual is None:
        _abertura_sem_resultado(doc, r)
    else:
        _pagina_de_relance(doc, e, r)
        doc.add_page()
        _curva(doc, e, r)

    # --- as premissas ------------------------------------------------------
    doc.secao("As premissas desta simulação")
    doc.linha("Pontos de venda", str(e.pontos_de_venda))
    if e.passagens_por_ponto is not None:
        doc.linha(
            "Passagens por mês, por ponto de venda",
            formato.inteiro(e.passagens_por_ponto),
        )
        doc.linha(
            "Passagens por mês, no total", formato.inteiro(r.passagens_totais or 0)
        )
    doc.linha(
        "Aproveitamento dianteiro",
        f"{formato.percentual(e.aproveitamento_dianteiro)} "
        f"({_procedencia_dianteiro(e)})",
    )

    if r.traseiro_na_conta:
        doc.linha(
            "Aproveitamento traseiro",
            f"{formato.percentual(e.aproveitamento_traseiro)} "
            f"({_procedencia_traseiro(e)})",
        )
    else:
        doc.linha("Traseiro", "preço não informado — fora da conta")

    # A premissa favoravel vai IMPRESSA: o documento sai da sala e ninguem
    # estara ao lado para explicar (§5.12, mesmo princípio das decisões abertas).
    if not P.CANIBALIZACAO_MODELADA:
        doc.linha("Canibalização", P.TEXTO_SEM_CANIBALIZACAO)

    # A operacao de hoje — a ancora
    if r.originais_por_mes is not None:
        doc.linha(
            "Palhetas vendidas hoje, por mês",
            formato.inteiro(r.originais_por_mes),
        )
    if e.preco_original is not None:
        doc.linha(
            "Preço da palheta original cobrado hoje",
            formato.moeda_unitaria(e.preco_original),
        )
    if r.margem_unitaria_original is not None:
        doc.linha(
            "Margem unitária da palheta original",
            formato.moeda_unitaria(r.margem_unitaria_original),
        )
    elif e.preco_original is not None:
        doc.linha(
            "Margem da palheta original",
            "custo não informado — sem incremental",
        )
    if r.margem_atual is not None:
        doc.linha(
            "Margem mensal atual com palhetas",
            formato.moeda_agregada(r.margem_atual),
        )

    # --- preco e custo: so em documento interno ---------------------------
    if interno:
        doc.secao("Preço e custo de tabela")
        doc.paragrafo(
            "Preço e custo vêm da tabela Suicatech vigente. Por conterem o "
            "custo de aquisição, este documento é interno."
        )
        if e.preco_dianteiro is not None:
            doc.linha(
                "Preço ao consumidor final, por par (dianteiro)",
                formato.moeda_unitaria(e.preco_dianteiro),
            )
        if e.custo_dianteiro is not None:
            doc.linha(
                "Custo de aquisição, por par (dianteiro)",
                formato.moeda_unitaria(e.custo_dianteiro),
            )
        if e.preco_traseiro is not None:
            doc.linha(
                "Preço ao consumidor final, por unidade (traseiro)",
                formato.moeda_unitaria(e.preco_traseiro),
            )
        if e.custo_traseiro is not None:
            doc.linha(
                "Custo de aquisição, por unidade (traseiro)",
                formato.moeda_unitaria(e.custo_traseiro),
            )

    # --- o que ainda nao foi decidido -------------------------------------
    abertas = aberto.decisoes_abertas_ativas()
    if abertas:
        doc.secao("O que esta simulação ainda não considera")
        doc.paragrafo(
            "Estes pontos não têm valor definido. O comportamento adotado é "
            "sempre o mais conservador, nunca o mais favorável:"
        )
        for letra, texto in abertas:
            doc.linha(f"decisão {letra}", texto)

    saida = io.BytesIO()
    doc.output(saida)
    return saida.getvalue()


# ---------------------------------------------------------------------------
# PAGINA 1 — a leitura de relance (D24)
# ---------------------------------------------------------------------------


def _abertura_sem_resultado(doc: _Documento, r: Resultado) -> None:
    """Sem valor anual nao ha pagina de relance. Nao ha cartao de R$ 0 tambem.

    P9 / §6.1.9: um default de R$ 0 ancora no cenario mais favoravel possivel, e
    e falso. O documento diz o que falta, e a pagina de premissas logo abaixo
    mostra o que ja foi informado — que e o que serve para retomar a conversa.
    """
    doc.secao("O resultado")
    doc.set_font("Helvetica", "B", 17)
    doc.set_text_color(TINTA_PRIMARIA)
    doc.multi_cell(
        _LARGURA,
        8,
        _t(formato.traducao_por_passagem(r.traducao_fracao)),
        align="L",
    )
    doc.ln(2)
    doc.paragrafo(
        "A simulação está incompleta: faltam as passagens por mês ou o preço e "
        "o custo do refil. Nenhum valor é exibido no lugar — um default de R$ 0 "
        "ancoraria no cenário mais favorável possível, e seria falso."
    )


def _pagina_de_relance(doc: _Documento, e: Entradas, r: Resultado) -> None:
    """Manchete, apoio, barras e cenarios — nesta ordem, e ela e normativa.

    A ORDEM MUDOU EM D26, a pedido do cliente: FATURAMENTO E MARGEM ADICIONAL
    abrem o documento, lado a lado, no maior corpo da folha. A traducao em
    escala humana desceu para os cartoes de apoio.

    O que isso contraria, e que precisa ficar dito: a §5.5 e o P2 mandavam a
    traducao vir primeiro e maior, porque "R$ 141.480 por ano" e rejeitado pelo
    cerebro antes de ser avaliado enquanto "3 a cada 10 carros que entram" e
    conferido pela intuicao em dois segundos. A tela ja tinha invertido isso em
    D21; o documento era o ultimo lugar onde a ordem original sobrevivia.

    `test_pdf_faturamento_e_margem_abrem_o_documento` le a ordem no FLUXO DE
    CONTEUDO do PDF, e nao no codigo — reordenar estas chamadas reprova.
    """
    _manchete(doc, r)
    _nota_do_grupo(doc, r)
    doc.ln(4)
    _cartoes_de_apoio(doc, r)
    doc.ln(6)
    _barras(doc, r)
    _cenarios(doc, e, r)
    _cashback(doc, r)


def _manchete(doc: _Documento, r: Resultado) -> None:
    """A faixa escura de abertura: os DOIS numeros, lado a lado (D26).

    Faturamento adicional a esquerda, margem de contribuicao adicional a
    direita, no MESMO corpo — a ordem dos dois primeiros cartoes da tela (D21,
    normativa). O documento e a lembranca da tela: inverter aqui faria o cliente
    procurar no papel o numero que ficou noutro lugar.

    A GRANDEZA DE CADA UM VAI NO ROTULO, e nao so na nota de rodape do grupo:
    sao duas contas diferentes no mesmo tamanho, e a §4 exige que todo resultado
    financeiro diga qual conta ele e. "Faturamento" nao e "margem".
    """
    faturamento_mensal = r.faturamento_refil or 0.0

    y = visual.manchete_dupla(
        doc,
        _MARGEM_X,
        doc.get_y(),
        _LARGURA,
        38.0,
        visual.KPI(
            "Faturamento adicional",
            formato.moeda_agregada(faturamento_mensal * MESES_NO_ANO),
            f"{formato.moeda_agregada(faturamento_mensal)} por mês",
        ),
        visual.KPI(
            "Margem de contribuição adicional",
            formato.moeda_agregada(r.anual or 0.0),
            f"{formato.moeda_agregada(r.incremental_mensal or 0.0)} por mês",
        ),
    )
    doc.set_y(y + 1.5)


def _cartoes_de_apoio(doc: _Documento, r: Resultado) -> None:
    """Os tres que sobraram da abertura: mark up, traducao e o contraste do mes.

    A TRADUCAO MORA AQUI DESDE D26. Ela nao saiu do documento — sairia do unico
    lugar em que ainda existe, porque D21 ja a tinha tirado da tela. O que ela
    perdeu foi a posicao de abertura e o corpo de 15pt; o que ela mantem e a
    forma curta ("3 a cada 10") no lugar do numero e a frase inteira embaixo,
    que e como o cartao de KPI e construido.
    """
    cartoes = [
        _cartao_markup(r),
        visual.KPI(
            "O que isso significa na oficina",
            formato.traducao_curta(r.traducao_fracao),
            "carros que entram viram um par de refil",
        ),
        _cartao_hoje_versus_refil(r),
    ]

    y = visual.linha_de_kpis(doc, _MARGEM_X, doc.get_y(), _LARGURA, 26.0, cartoes)
    doc.set_y(y)


def _cartao_hoje_versus_refil(r: Resultado) -> visual.KPI:
    """"hoje X -> com o refil Y" — o contraste que ancora o resultado.

    So aparece com margem da original para comparar. Sem o custo dela nao existe
    margem dela, e comparar margem com faturamento misturaria grandezas
    (§6.1.5) — o cartao entao declara o motivo, e nao um numero.
    """
    if r.margem_atual is None or r.incremental_mensal is None:
        return visual.KPI(
            "Margem com palhetas, por mês",
            None,
            "custo da original não informado",
        )
    # A SETA FICA NA LINHA DE APOIO, entre os dois estados, e nao colada no
    # numero grande: "-> R$ 15.570" sozinho no lugar do valor parece um valor
    # com um simbolo perdido na frente. Embaixo ela separa o antes do depois,
    # que e a leitura de `_hoje_versus_refil` na tela.
    total = r.margem_atual + r.incremental_mensal
    return visual.KPI(
        "Margem com palhetas, por mês",
        formato.moeda_agregada(total),
        f"hoje {formato.moeda_agregada(r.margem_atual)} → adotando o refil",
    )


def _nota_do_grupo(doc: _Documento, r: Resultado) -> None:
    """Qual periodo e qual conta, logo abaixo da manchete.

    "Valores anuais" nao e enfeite: os dois numeros grandes sao de 12 meses e o
    apoio de cada um e mensal. Sem a nota, os dois se confundem — e a §4 exige
    que todo resultado financeiro diga qual conta ele e.
    """
    doc.set_x(_MARGEM_X)
    doc.set_font("Helvetica", "", 7.5)
    doc.set_text_color(TINTA_DISCRETA)
    doc.cell(
        _LARGURA,
        4,
        _t(
            f"Valores anuais · {rotulo_do_resultado(r)} · {P.rotulo_do_anual()}"
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )


def _cartao_markup(r: Resultado) -> visual.KPI:
    if r.markup_operacao is not None:
        return visual.KPI(
            "Mark up da operação",
            formato.multiplo(r.markup_operacao),
            "faturamento ÷ custo",
        )
    # Sem custo total nao ha o que dividir. Um "1,0" ali significaria "vende ao
    # preco de custo", que e uma afirmacao que ninguem fez (§6.1.9, P9).
    return visual.KPI(
        "Mark up da operação", None, "sem custo total para dividir"
    )


def _barras(doc: _Documento, r: Resultado) -> None:
    """O comparativo anual em barras. So com margem da original para comparar."""
    if r.margem_atual is None or r.anual is None:
        return

    hoje_anual = r.margem_atual * MESES_NO_ANO
    doc.secao("Margem de contribuição no ano: hoje e com o refil")

    y = visual.barras_hoje_versus_refil(
        doc,
        _MARGEM_X,
        doc.get_y(),
        _LARGURA,
        60.0,
        hoje=hoje_anual,
        incremental=r.anual,
        rotulo_hoje=formato.moeda_agregada(hoje_anual),
        rotulo_refil=formato.moeda_agregada(hoje_anual + r.anual),
        # `moeda_agregada` ja traz o sinal de menos quando o valor e negativo
        # (§5.5). O "+" so entra quando ha o que somar — senao a linha sairia
        # "+ −R$ 36.828".
        rotulo_incremental=(
            f"+ {formato.moeda_agregada(r.anual)}"
            if r.anual >= 0
            else formato.moeda_agregada(r.anual)
        ),
    )
    doc.set_y(y)
    doc.paragrafo(
        "A base das duas barras é a mesma de propósito: nenhuma venda de refil "
        f"é descontada da palheta original — {P.TEXTO_SEM_CANIBALIZACAO}. O "
        "segmento de cima é o que entra."
        if r.anual >= 0
        else "A base das duas barras é a mesma de propósito: nenhuma venda de "
        f"refil é descontada da palheta original — {P.TEXTO_SEM_CANIBALIZACAO}. "
        "Com este preço e este custo, o refil fica abaixo do que a palheta "
        "original já entrega — o vão tracejado é a diferença."
    )


def _cenarios(doc: _Documento, e: Entradas, r: Resultado) -> None:
    """As tres faixas medidas da carteira, com a simulada destacada.

    RECALCULA cada preset a partir das MESMAS entradas — mesmo preco, mesmo
    custo, mesma operacao —, trocando so o par de aproveitamento. E o mesmo
    caminho que os botoes de cenario da tela percorrem (§5.3): um preset e um
    PAR medido, e aplicar um escreve as duas grandezas.

    O pessimista entra e ocupa o mesmo espaco. Ver `pdf_visual.tiras_de_cenario`.
    """
    if r.anual is None:
        return

    ativo = preset_ativo(e)
    itens: list[visual.Cenario] = []

    for preset in P.PRESETS:
        simulado = calcular(
            replace(
                e,
                aproveitamento_dianteiro=preset.dianteiro,
                aproveitamento_traseiro=preset.traseiro,
            )
        )
        if simulado.anual is None:
            continue
        pp_d = formato.percentual(preset.dianteiro)
        pp_t = formato.percentual(preset.traseiro)
        itens.append(
            visual.Cenario(
                rotulo=preset.rotulo,
                aproveitamento=f"{pp_d} dianteiro · {pp_t} traseiro",
                valor=formato.moeda_agregada(simulado.anual),
                apoio=f"por ano · {formato.moeda_agregada(simulado.anual / MESES_NO_ANO)}/mês",
                ativo=preset.nome == ativo,
            )
        )

    if not itens:
        return

    doc.secao("Os três cenários medidos na carteira")
    y = visual.tiras_de_cenario(doc, _MARGEM_X, doc.get_y(), _LARGURA, 26.0, itens)
    doc.set_y(y + 1)

    if ativo is None:
        nota = (
            f"Esta simulação usa {formato.percentual(e.aproveitamento_dianteiro)} "
            "de aproveitamento dianteiro, ajustado na reunião — entre os "
            f"cenários acima. {P.LEGENDA_PRESETS_DIANTEIRO}."
        )
    else:
        nota = (
            f"O cenário simulado nesta reunião está destacado. "
            f"{P.LEGENDA_PRESETS_DIANTEIRO}."
        )
    doc.paragrafo(nota)


def _cashback(doc: _Documento, r: Resultado) -> None:
    """A linha do cashback: ACRESCENTA, nunca subtrai (§6.1.7, plano decisao A).

    Declara quem paga. NUNCA quanto isso custa a Suicatech — esse numero nao
    existe nem como campo (§6.1.9).
    """
    if not r.cashback_total:
        return

    x, y = _MARGEM_X, doc.get_y() + 2
    altura = 15.0
    visual.cartao(doc, x, y, _LARGURA, altura, fundo="#FDF3F5", borda="#F2CFD6")
    doc.set_draw_color(MARCA_VERMELHO)
    doc.set_line_width(1.0)
    doc.line(x + 0.5, y + 2, x + 0.5, y + altura - 2)

    doc.set_xy(x + 5, y + 2.5)
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(TINTA_PRIMARIA)
    doc.cell(
        _LARGURA - 10,
        4.5,
        _t(
            f"{formato.moeda_agregada(r.cashback_total)}/mês de cashback para "
            f"sua equipe"
        ),
    )
    doc.set_xy(x + 5, y + 7.5)
    doc.set_font("Helvetica", "", 7.5)
    doc.set_text_color(TINTA_SECUNDARIA)
    doc.cell(
        _LARGURA - 10,
        3.6,
        _t("pago pela Suicatech, não sai da sua margem"),
    )
    detalhe = " · ".join(
        f"{nome} {formato.moeda_agregada(valor)}/mês"
        for nome, valor in r.cashback_por_destinatario
    )
    if detalhe:
        doc.set_xy(x + 5, y + 11)
        doc.set_font("Helvetica", "B", 7.5)
        doc.cell(_LARGURA - 10, 3.6, _t(detalhe))
    doc.set_y(y + altura)


# ---------------------------------------------------------------------------
# PAGINA 2 — a auditoria
# ---------------------------------------------------------------------------


def _curva(doc: _Documento, e: Entradas, r: Resultado) -> None:
    """A curva inteira, com marcador na posicao simulada. Gemeo da §5.11.

    "O cliente ve o intervalo completo SEM INTERAGIR" — no papel isso vale
    ainda mais, porque nao ha slider nenhum para arrastar.

    A curva plota a MESMA GRANDEZA da manchete. Com margem da original ela
    mostra o TOTAL das duas linhas e o vao entre elas e o incremental; sem ela,
    volta a uma linha so, plotando o incremental — o app nao inventa margem
    para a original.
    """
    if r.anual is None:
        return

    lo, hi = P.SLIDER_DOMINIO
    pontos, base = curvas_comparadas(e)
    if not pontos:
        return

    atual_y = (base + r.anual) if base is not None else r.anual
    valores = [valor for _, valor in pontos] + (
        [base] if base is not None else []
    )
    ticks = _ticks_do_eixo(min(valores), max(valores))

    doc.secao("Como o resultado varia com o aproveitamento")
    congelado = (
        f"traseiro fixo em {formato.percentual(e.aproveitamento_traseiro)}"
        if r.traseiro_na_conta
        else "traseiro fora da conta"
    )
    doc.paragrafo(
        f"{congelado} · só o dianteiro varia. "
        + (
            "A distância entre as duas linhas é a margem adicional."
            if base is not None
            else "A linha é a margem de contribuição do refil."
        ),
        tamanho=8,
    )

    y = visual.curva(
        doc,
        _MARGEM_X,
        doc.get_y(),
        _LARGURA,
        58.0,
        pontos=pontos,
        dominio_x=(lo, hi),
        base=base,
        atual_x=e.aproveitamento_dianteiro * 100,
        atual_y=atual_y,
        rotulo_atual=formato.moeda_agregada(atual_y),
        rotulo_base="só com a palheta original" if base is not None else None,
        ticks_y=ticks,
        marcas_x=[preset.dianteiro * 100 for preset in P.PRESETS],
    )
    doc.set_y(y + 2)
    _frase_do_cruzamento(doc, pontos, base)


def _ticks_do_eixo(piso: float, teto: float) -> list[tuple[float, str]]:
    """Os ticks do eixo Y, com a forma ABREVIADA — mas so quando ela distingue.

    `moeda_curta` arredonda por construcao, e numa faixa estreita ela colapsa:
    R$ 1.000, R$ 1.050 e R$ 1.100 viram tres ticks lendo "R$ 1 mil". Tres
    ticks identicos em alturas diferentes nao sao uma regua — sao uma
    contradicao no desenho.

    Quando a forma curta repete, o eixo cai para o numero inteiro. Ele e mais
    largo, mas numa faixa estreita o numero tambem e curto, entao o custo de
    espaco que justifica abreviar simplesmente nao existe ali.
    """
    brutos = visual.ticks_de_eixo(piso, teto)
    curtos = [formato.moeda_curta(valor) for valor in brutos]
    if len(set(curtos)) == len(curtos):
        return list(zip(brutos, curtos))
    return [(valor, formato.moeda_agregada(valor)) for valor in brutos]


def _frase_do_cruzamento(
    doc: _Documento, pontos: list[tuple[float, float]], base: float | None
) -> None:
    """"a partir de X% o refil supera o que ha hoje" — se houver um X.

    Sem cruzamento no domínio, DIZ isso, em vez de sugerir que existe. Mesma
    regra de `grafico_sensibilidade._frase_do_cruzamento`.
    """
    if base is None:
        return

    cruzamento = next((pp for pp, total in pontos if total > base), None)
    if cruzamento is None:
        doc.paragrafo(
            "O refil não supera a palheta original em nenhum ponto da faixa — "
            "confira preço e custo das duas categorias.",
            tamanho=8,
        )
    elif cruzamento <= P.SLIDER_DOMINIO[0]:
        doc.paragrafo(
            "O refil supera a palheta original em toda a faixa de "
            "aproveitamento.",
            tamanho=8,
        )
    else:
        doc.paragrafo(
            f"A partir de {int(cruzamento)}% de aproveitamento o refil passa a "
            "render mais que continuar só com a palheta original.",
            tamanho=8,
        )


def _procedencia_dianteiro(e: Entradas) -> str:
    nome = preset_ativo(e)
    if nome is None:
        return "ajustado na reunião"
    preset = P.preset_por_nome(nome)
    if preset and preset.origem_dianteiro == "carteira_medida":
        return "medido em 15+ concessionárias da carteira Suicatech"
    return "derivado — não medido"


def _procedencia_traseiro(e: Entradas) -> str:
    nome = preset_ativo(e)
    if nome is None:
        return "ajustado na reunião"
    preset = P.preset_por_nome(nome)
    if preset and preset.origem_traseiro == "carteira_medida":
        return "medido na carteira Suicatech"
    return "derivado do dianteiro na mesma proporção — não medido"


def nome_do_arquivo(cliente: str, dia: date | None = None) -> str:
    """`simulacao-refil-<cliente>-<AAAA-MM-DD>.pdf`, seguro em qualquer sistema.

    A versao anterior fazia `c if c.isalnum() else "-"` sobre o nome em
    minusculas, e isso deixava passar duas coisas que quebram nome de arquivo:

      - ACENTO. `"á".isalnum()` e True em Python, e o nome saia com acento. O
        Windows aceita; um anexo de e-mail passando por servidor antigo, nem
        sempre — e o PDF existe justamente para sair da sala
      - TRACO REPETIDO. "Auto Center — Zona Sul" virava
        `auto-center-----zona-sul`

    Sem cliente o nome nao leva o traco solto: `simulacao-refil-2026-08-27`.
    """
    dia = dia or date.today()
    base = "simulacao-refil"

    sem_acento = (
        unicodedata.normalize("NFKD", cliente.lower())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    limpo = "".join(c if c.isalnum() else "-" for c in sem_acento)
    while "--" in limpo:
        limpo = limpo.replace("--", "-")
    limpo = limpo.strip("-")

    if limpo:
        base = f"{base}-{limpo}"
    return f"{base}-{dia:%Y-%m-%d}.pdf"


def bloco_exportar(e: Entradas, r: Resultado) -> None:
    """A area de exportacao. Fechada por padrao, como o painel de formula.

    O DOCUMENTO E MONTADO A CADA RERUN, e nao atras de um botao "gerar". Sao
    ~19 ms por PDF nesta maquina, contra um toque a mais na frente do cliente e
    um estado a mais para o botao ficar dessincronizado do que esta na tela — o
    risco real de um fluxo de dois passos e o vendedor baixar o PDF do cenario
    ANTERIOR. A conta so roda quando o resultado esta visivel: a Tela 1 nao
    chama este bloco antes do toque em "Mostrar Resultado".
    """
    with st.expander("Levar esta simulação — PDF", expanded=False):
        st.markdown(
            f'<p class="st-exportar-nota">{svg("exportar")}'
            "<span>Um documento com o cenário simulado, as premissas "
            "assumidas e o que ainda não foi decidido.</span></p>",
            unsafe_allow_html=True,
        )

        st.text_input(
            "Nome do cliente (opcional, entra no documento)",
            key=K_NOME_CLIENTE,
        )
        cliente = str(st.session_state.get(K_NOME_CLIENTE) or "").strip()

        if e.custo_dianteiro is not None or e.custo_traseiro is not None:
            st.caption(
                "O documento incluirá o custo de aquisição e sairá marcado como "
                "**documento interno** — o custo é o preço de venda da Suicatech."
            )

        with st.container(key="exportar"):
            # §7.4 — nunca uma tela quebrada na frente do cliente. O PDF passa
            # por fonte, imagem e rotacao; qualquer uma delas pode falhar num
            # ambiente que nao e este, e uma excecao aqui derrubaria o
            # RESULTADO INTEIRO, que ja esta na tela e e o que o cliente veio
            # ver. A captura e larga de proposito, e o que ela troca por isso e
            # dito em linha, sem componente de alerta (§5.9).
            try:
                documento = gerar_pdf(e, r, cliente)
            except Exception:  # noqa: BLE001 — ver o comentario acima
                documento = None

            if documento is None:
                st.caption(
                    "O documento não pôde ser montado agora. Os números da tela "
                    "continuam válidos — o painel **De onde vêm esses números** "
                    "mostra a conta inteira."
                )
                return

            # O ROTULO E TEXTO PURO, e nao pode voltar a carregar HTML: o
            # Streamlit trata rotulo de botao como markdown e ESCAPA a marcacao
            # — o `svg()` que morava aqui saia impresso como `<span class=...>`
            # em cima do botao (§4.11). O icone e a linha de markdown acima.
            st.download_button(
                "Baixar PDF do cenário",
                data=documento,
                file_name=nome_do_arquivo(cliente),
                mime="application/pdf",
                width="stretch",
            )

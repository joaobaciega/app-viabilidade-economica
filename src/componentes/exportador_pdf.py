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
from datetime import date

import streamlit as st
from fpdf import FPDF

from src import apresentacao
from src.calculo import Entradas, Resultado
from src.componentes import pdf_visual as visual
from src.css import (
    MARCA_BORDA,
    MARCA_LAVADO,
    MARCA_VERMELHO,
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

        # O NOME DO CLIENTE ABRE O DOCUMENTO (D29). Ate aqui ele entrava no meio
        # da linha de metadados, em 8,5pt cinza, entre a marca e a data — o
        # cliente digitava o nome e nao encontrava: "nao aparece em nenhum
        # lugar". Um documento personalizado e endereçado a alguem, e quem ele
        # e vem antes do que ele e.
        #
        # Sem nome, o titulo sobe para o lugar do nome e nada mais muda: o
        # documento generico continua abrindo pelo proprio titulo.
        if self._cliente:
            self.set_font("Helvetica", "B", 17)
            self.set_text_color(TINTA_PRIMARIA)
            self.cell(0, 8, _t(self._cliente), new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 10.5)
            self.set_text_color(TINTA_SECUNDARIA)
            self.cell(
                0,
                5.5,
                _t("Simulação de viabilidade — refil de palhetas"),
                new_x="LMARGIN",
                new_y="NEXT",
            )
        else:
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
        self.set_text_color(TINTA_DISCRETA)
        self.cell(
            0,
            5,
            _t(f"Suicatech · Intrace AG · gerado em {date.today():%d/%m/%Y}"),
            new_x="LMARGIN",
            new_y="NEXT",
        )

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
        coluna = 95.0
        self._reservar(self._altura_da_linha(rotulo, valor, forte, coluna))

        topo = self.get_y()
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

    def _altura_da_linha(
        self, rotulo: str, valor: str, forte: bool, coluna: float
    ) -> float:
        """Quanto o par `rotulo / valor` vai ocupar, MEDIDO antes de escrever.

        `dry_run=True, output="HEIGHT"` faz o fpdf2 quebrar o texto e devolver a
        altura sem desenhar nem mover o cursor. E a unica forma honesta de
        saber quantas linhas um texto vai ocupar — contar caracteres erra em
        qualquer fonte proporcional.
        """
        self.set_font("Helvetica", "", 9.5)
        alto_rotulo = self.multi_cell(
            coluna, 5.6, _t(rotulo), align="L", dry_run=True, output="HEIGHT"
        )
        self.set_font("Helvetica", "B" if forte else "", 10.5 if forte else 9.5)
        alto_valor = self.multi_cell(
            _LARGURA - coluna,
            5.6,
            _t(valor),
            align="L",
            dry_run=True,
            output="HEIGHT",
        )
        return max(alto_rotulo, alto_valor, 5.6)

    def _reservar(self, altura: float) -> None:
        """Quebra a pagina ANTES do bloco, se ele nao couber inteiro.

        A quebra automatica do fpdf2 age POR CELULA, e `linha()` desenha duas —
        o rotulo numa coluna e o valor noutra, ambas comecando no mesmo `y`. Sem
        esta reserva, um par no fim da pagina saia RASGADO: "decisão L" numa
        pagina e "idade de recoleta não definida" na seguinte. Um rotulo sem o
        valor dele e pior do que o par inteiro na pagina de baixo.
        """
        if self.get_y() + altura > self.page_break_trigger:
            self.add_page()

    def paragrafo(self, texto: str, tamanho: float = 8.5) -> None:
        self.set_font("Helvetica", "", tamanho)
        self.set_text_color(TINTA_SECUNDARIA)
        self.set_x(_MARGEM_X)
        self.multi_cell(_LARGURA, 4.2, _t(texto), align="L")
        self.ln(1)


def gerar_pdf(e: Entradas, r: Resultado, cliente: str = "") -> bytes:
    """Monta o PDF do cenario simulado. Aritmetica ja resolvida em `r`.

    NAO DECIDE NADA sobre o conteudo desde D28: quais blocos existem, em que
    ordem, com que rotulo e que numero vem de `apresentacao.montar()`, que a
    tela consome igual. Aqui so se decide GEOMETRIA — o que cabe em que pagina,
    quantos milimetros cada peca ocupa.

    Duas paginas com papeis distintos: a primeira e a leitura de relance, a
    segunda e a auditoria. Sem resultado nao existe a primeira — o documento
    abre dizendo o que falta, e nao com um cartao de R$ 0.
    """
    a = apresentacao.montar(e, r)
    doc = _Documento(
        interno=apresentacao.documento_interno(e), cliente=cliente
    )
    doc.add_page()

    if a.manchete is None:
        _abertura_sem_resultado(doc, a)
    else:
        _pagina_de_relance(doc, a)
        doc.add_page()
        _curva(doc, a)

    for secao in (a.premissas, a.preco_custo, a.decisoes):
        _secao(doc, secao)

    saida = io.BytesIO()
    doc.output(saida)
    return saida.getvalue()


def _secao(doc: _Documento, secao: apresentacao.Secao | None) -> None:
    """Titulo, nota opcional e as linhas `rotulo ... valor`."""
    if secao is None:
        return
    doc.secao(secao.titulo)
    if secao.nota:
        doc.paragrafo(secao.nota)
    for rotulo, valor in secao.linhas:
        doc.linha(rotulo, valor)


# ---------------------------------------------------------------------------
# PAGINA 1 — a leitura de relance (D24, reordenada por D26)
# ---------------------------------------------------------------------------


def _abertura_sem_resultado(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """Sem valor anual nao ha pagina de relance. Nao ha cartao de R$ 0 tambem.

    P9 / §6.1.9: um default de R$ 0 ancora no cenario mais favoravel possivel, e
    e falso. O documento diz o que falta, e a pagina de premissas logo abaixo
    mostra o que ja foi informado — que e o que serve para retomar a conversa.
    """
    doc.secao("O resultado")
    doc.set_font("Helvetica", "B", 17)
    doc.set_text_color(TINTA_PRIMARIA)
    doc.multi_cell(_LARGURA, 8, _t(a.traducao), align="L")
    doc.ln(2)
    doc.paragrafo(a.incompleto)


def _pagina_de_relance(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """Manchete, apoio, barras, cenarios e cashback — a ordem vem da montagem.

    `test_pdf_faturamento_e_margem_abrem_o_documento` le a ordem no FLUXO DE
    CONTEUDO do PDF, e nao no codigo — reordenar estas chamadas reprova.
    """
    _manchete(doc, a)
    _nota_do_grupo(doc, a)
    doc.ln(4)
    _cartoes_de_apoio(doc, a)
    doc.ln(6)
    _barras(doc, a)
    _cenarios(doc, a)
    _cashback(doc, a)


def _manchete(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """A faixa escura de abertura: os DOIS numeros, lado a lado (D26)."""
    if a.manchete is None:
        return
    esquerda, direita = a.manchete
    y = visual.manchete_dupla(
        doc, _MARGEM_X, doc.get_y(), _LARGURA, 38.0, esquerda, direita
    )
    doc.set_y(y + 1.5)


def _nota_do_grupo(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """Qual periodo e qual conta, logo abaixo da manchete.

    "Valores anuais" nao e enfeite: os dois numeros grandes sao de 12 meses e o
    apoio de cada um e mensal. Sem a nota, os dois se confundem — e a §4 exige
    que todo resultado financeiro diga qual conta ele e.
    """
    doc.set_x(_MARGEM_X)
    doc.set_font("Helvetica", "", 7.5)
    doc.set_text_color(TINTA_DISCRETA)
    doc.cell(
        _LARGURA, 4, _t(a.nota_do_grupo), new_x="LMARGIN", new_y="NEXT"
    )


def _cartoes_de_apoio(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """Mark up, traducao em escala humana e a nova margem com refil."""
    y = visual.linha_de_kpis(
        doc, _MARGEM_X, doc.get_y(), _LARGURA, 26.0, list(a.apoio)
    )
    doc.set_y(y)


def _barras(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """O comparativo anual em barras. So com margem da original para comparar."""
    if a.barras is None:
        return

    b = a.barras
    doc.secao(a.titulo_barras)
    y = visual.barras_hoje_versus_refil(
        doc,
        _MARGEM_X,
        doc.get_y(),
        _LARGURA,
        66.0,
        hoje=b.hoje,
        incremental=b.incremental,
        rotulo_hoje=b.rotulo_hoje,
        rotulo_refil=b.rotulo_refil,
        rotulo_incremental=b.rotulo_incremental,
        nome_hoje=b.nome_hoje,
        nome_refil=b.nome_refil,
    )
    doc.set_y(y)
    doc.paragrafo(b.nota)


def _cenarios(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """As tres faixas medidas da carteira, com a simulada destacada."""
    if not a.cenarios:
        return

    doc.secao(a.titulo_cenarios)
    y = visual.tiras_de_cenario(
        doc, _MARGEM_X, doc.get_y(), _LARGURA, 26.0, list(a.cenarios)
    )
    doc.set_y(y + 1)
    doc.paragrafo(a.nota_cenarios)


def _cashback(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """A linha do cashback: ACRESCENTA, nunca subtrai (§6.1.7, plano decisao A).

    Declara quem paga. NUNCA quanto isso custa a Suicatech — esse numero nao
    existe nem como campo (§6.1.9).
    """
    if a.cashback is None:
        return

    x, y = _MARGEM_X, doc.get_y() + 2
    altura = 15.0
    visual.cartao(doc, x, y, _LARGURA, altura, fundo=MARCA_LAVADO, borda=MARCA_BORDA)
    doc.set_draw_color(MARCA_VERMELHO)
    doc.set_line_width(1.0)
    doc.line(x + 0.5, y + 2, x + 0.5, y + altura - 2)

    doc.set_xy(x + 5, y + 2.5)
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(TINTA_PRIMARIA)
    doc.cell(_LARGURA - 10, 4.5, _t(a.cashback.total))

    doc.set_xy(x + 5, y + 7.5)
    doc.set_font("Helvetica", "", 7.5)
    doc.set_text_color(TINTA_SECUNDARIA)
    doc.cell(_LARGURA - 10, 3.6, _t(a.cashback.nota))

    if a.cashback.rateio:
        doc.set_xy(x + 5, y + 11)
        doc.set_font("Helvetica", "B", 7.5)
        doc.cell(_LARGURA - 10, 3.6, _t(a.cashback.rateio))
    doc.set_y(y + altura)


# ---------------------------------------------------------------------------
# PAGINA 2 — a auditoria
# ---------------------------------------------------------------------------


def _curva(doc: _Documento, a: apresentacao.Apresentacao) -> None:
    """A curva inteira, com marcador na posicao simulada. Gemeo da §5.11."""
    if a.curva is None:
        return

    c = a.curva
    doc.secao(a.titulo_curva)
    doc.paragrafo(c.subtitulo, tamanho=8)

    y = visual.curva(
        doc,
        _MARGEM_X,
        doc.get_y(),
        _LARGURA,
        48.0,
        pontos=list(c.pontos),
        dominio_x=c.dominio_x,
        base=c.base,
        atual_x=c.atual_x,
        atual_y=c.atual_y,
        rotulo_atual=c.rotulo_atual,
        rotulo_base=c.rotulo_base,
        ticks_y=list(c.ticks),
        marcas_x=list(c.marcas_x),
    )
    doc.set_y(y + 2)
    if c.frase:
        doc.paragrafo(c.frase, tamanho=8)


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

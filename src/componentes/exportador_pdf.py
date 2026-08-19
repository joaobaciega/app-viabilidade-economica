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
"""

from __future__ import annotations

import io
import unicodedata
from datetime import date

import streamlit as st
from fpdf import FPDF

from src import formato
from src import parametros as P
from src.calculo import Entradas, Resultado, rotulo_do_resultado
from src.componentes import marcador_decisao_aberta as aberto
from src.estado import K_NOME_CLIENTE
from src.icones import svg

# A fonte nucleo do fpdf2 e Latin-1. Normalizamos para nao quebrar em acento.
_LARGURA = 190


def _t(texto: str) -> str:
    """Normaliza para Latin-1, preservando acentos suportados."""
    try:
        texto.encode("latin-1")
        return texto
    except UnicodeEncodeError:
        return (
            unicodedata.normalize("NFKD", texto)
            .encode("latin-1", "ignore")
            .decode("latin-1")
        )


class _Documento(FPDF):
    def __init__(self, interno: bool, cliente: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self._interno = interno
        self._cliente = cliente
        self.set_auto_page_break(auto=True, margin=20)

    def header(self) -> None:
        # O logo, se existir em assets/. `fpdf2` aceita o caminho direto; se o
        # arquivo estiver ilegivel seguimos so com o texto — um PDF sem logo e
        # melhor que uma excecao no meio da reuniao.
        from src import marca

        caminho = marca.caminho_do_logo_completo()
        if caminho is not None and caminho.suffix.lower() != ".svg":
            try:
                self.image(str(caminho), x=10, y=8, h=13)
                self.set_y(8 + 13 + 3)
            except (RuntimeError, OSError, ValueError):
                pass

        self.set_font("Helvetica", "B", 15)
        self.set_text_color(11, 11, 11)
        self.cell(0, 8, _t("Simulação de viabilidade — refil de palhetas"), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(82, 81, 78)
        linha = f"Suicatech · Intrace AG · gerado em {date.today():%d/%m/%Y}"
        if self._cliente:
            linha = f"{self._cliente} · {linha}"
        self.cell(0, 6, _t(linha), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(195, 194, 183)
        self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(137, 135, 129)
        nota = "Margem de contribuição. Valores simulados a partir de premissas informadas na reunião."
        if self._interno:
            nota = f"DOCUMENTO INTERNO — contém custo de aquisição. {nota}"
        self.multi_cell(_LARGURA, 4, _t(nota))

    def marca_dagua(self) -> None:
        """Marca-d'agua diagonal quando o documento carrega custo."""
        if not self._interno:
            return
        with self.rotation(45, x=105, y=150):
            self.set_font("Helvetica", "B", 46)
            self.set_text_color(230, 230, 226)
            self.text(38, 150, _t("DOCUMENTO INTERNO"))
        self.set_text_color(11, 11, 11)

    # -- helpers de conteudo ------------------------------------------------

    def secao(self, titulo: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(11, 11, 11)
        self.cell(0, 7, _t(titulo), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(225, 224, 217)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def linha(self, rotulo: str, valor: str, forte: bool = False) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(82, 81, 78)
        self.cell(105, 6, _t(rotulo))
        self.set_font("Helvetica", "B" if forte else "", 11 if forte else 10)
        self.set_text_color(11, 11, 11)
        self.cell(0, 6, _t(valor), new_x="LMARGIN", new_y="NEXT")

    def paragrafo(self, texto: str, tamanho: int = 9) -> None:
        self.set_font("Helvetica", "", tamanho)
        self.set_text_color(82, 81, 78)
        self.multi_cell(_LARGURA, 4.6, _t(texto))
        self.ln(1)


def gerar_pdf(e: Entradas, r: Resultado, cliente: str = "") -> bytes:
    """Monta o PDF do cenario simulado. Aritmetica ja resolvida em `r`."""
    interno = (
        e.custo_dianteiro is not None
        or e.custo_traseiro is not None
        or e.custo_original is not None
    )
    doc = _Documento(interno=interno, cliente=cliente)
    doc.add_page()
    doc.marca_dagua()

    # --- o resultado, na MESMA ORDEM da tela (§5.5): traducao antes do anual
    doc.secao("O resultado")
    doc.set_font("Helvetica", "B", 20)
    doc.set_text_color(11, 11, 11)
    doc.multi_cell(
        _LARGURA, 9, _t(formato.traducao_por_passagem(r.traducao_fracao))
    )
    doc.ln(2)

    if r.anual is None:
        doc.paragrafo(
            "A simulação está incompleta: faltam as passagens por mês ou o "
            "preço e o custo do refil. Nenhum valor é exibido no lugar — um "
            "default de R$ 0 ancoraria no cenário mais favorável possível, e "
            "seria falso."
        )
    else:
        doc.linha(
            f"{rotulo_do_resultado(r)} · {P.rotulo_do_anual()}",
            f"{formato.moeda_agregada(r.anual)} por ano",
            forte=True,
        )
        doc.linha("por mês", f"{formato.moeda_agregada(r.incremental_mensal)}")
        if r.faturamento_refil:
            doc.linha(
                "faturamento mensal (linha de apoio)",
                formato.moeda_agregada(r.faturamento_refil),
            )
        if r.cashback_total:
            # Declara quem paga. NUNCA quanto isso custa a Suicatech.
            doc.linha(
                "cashback para a equipe",
                f"{formato.moeda_agregada(r.cashback_total)}/mês "
                f"— pago pela Suicatech, não sai da sua margem",
            )
            for nome, valor in r.cashback_por_destinatario:
                doc.linha(f"    {nome}", f"{formato.moeda_agregada(valor)}/mês")

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
        doc.secao("Preço e custo desta negociação")
        doc.paragrafo(
            "Estes valores são negociados caso a caso e não constam de nenhuma "
            "planilha publicada. Por conterem o custo de aquisição, este "
            "documento é interno."
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


def _procedencia_dianteiro(e: Entradas) -> str:
    from src.calculo import preset_ativo

    nome = preset_ativo(e)
    if nome is None:
        return "ajustado na reunião"
    preset = P.preset_por_nome(nome)
    if preset and preset.origem_dianteiro == "carteira_medida":
        return "medido em 15+ concessionárias da carteira Suicatech"
    return "derivado — não medido"


def _procedencia_traseiro(e: Entradas) -> str:
    from src.calculo import preset_ativo

    nome = preset_ativo(e)
    if nome is None:
        return "ajustado na reunião"
    preset = P.preset_por_nome(nome)
    if preset and preset.origem_traseiro == "carteira_medida":
        return "medido na carteira Suicatech"
    return "derivado do dianteiro na mesma proporção — não medido"


def bloco_exportar(e: Entradas, r: Resultado) -> None:
    """A area de exportacao. Fechada por padrao, como o painel de formula."""
    with st.expander("Levar esta simulação — PDF", expanded=False):
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

        nome_arquivo = "simulacao-refil"
        if cliente:
            seguro = "".join(
                c if c.isalnum() or c in "-_" else "-" for c in cliente.lower()
            )
            nome_arquivo = f"simulacao-refil-{seguro}"

        st.download_button(
            f"{svg('exportar')} Baixar PDF do cenário",
            data=gerar_pdf(e, r, cliente),
            file_name=f"{nome_arquivo}-{date.today():%Y-%m-%d}.pdf",
            mime="application/pdf",
            width="stretch",
        )

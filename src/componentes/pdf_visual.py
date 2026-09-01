"""A TINTA do PDF — cartoes, barras, tiras de cenario e curva. D24.

Este modulo nao sabe NADA sobre viabilidade de refil. Ele recebe posicao,
tamanho, rotulo e numero JA FORMATADO, e desenha. Quem decide o que entra no
documento, em que ordem e com que texto e `exportador_pdf.py` — a mesma
separacao que existe entre `css.py` (a tinta da tela) e os componentes.

POR QUE DESENHAR A MAO, em vez de gerar imagem com matplotlib:

  1. `requirements.txt` instala EXATAMENTE o que o app importa, e
     `test_runtime_nao_carrega_dependencia_de_desenvolvimento` reprova o
     contrario. matplotlib sao ~30 MB e dezenas de submodulos no Streamlit
     Community Cloud, que hiberna apos 12 h e precisa acordar antes de o
     cliente olhar a tela (plano §6.2, §9 risco 6)
  2. grafico rasterizado num PDF A4 ou fica serrilhado na impressao ou fica
     pesado. Retangulo e linha vetoriais imprimem nitido em qualquer tamanho
  3. o `fpdf2` que ja esta instalado desenha os dois

A PALETA VEM DE `src/css.py`. Nao existe uma cor definida neste arquivo: o PDF
e a tela sao a MESMA marca, e o documento sai da sala junto com a lembranca da
tela. Um vermelho ligeiramente diferente no papel e uma marca desalinhada.

AS REGRAS DE COR DO PROJETO VALEM AQUI INTEIRAS:

  - NENHUM NUMERO DE RESULTADO EM VERMELHO (§3.1.2, §13.1). "Numero financeiro
    em vermelho le como prejuizo, que e o oposto do que o pitch afirma." O
    destaque do cartao principal e a SUPERFICIE ESCURA (D6, 17,9:1), como na
    tela
  - o vermelho e MARCA DE GRAFICO: o segmento de barra do incremental, o
    marcador da curva e a anotacao do vao. Sao exatamente os usos que a §3.1
    autoriza, e os mesmos que `grafico_sensibilidade.py` faz na tela
  - nenhuma cor semantica de alerta existe neste projeto — nao ha token de
    erro, e nada aqui pisca

LATIN-1: as fontes nucleo do `fpdf2` (Helvetica) sao Latin-1. `texto()` e o
unico caminho por onde uma string entra no documento, e ele transcreve o que
nao cabe em vez de apagar — ver a tabela `_TRANSCRICAO`.
"""

from __future__ import annotations

import unicodedata

from fpdf import FPDF

# As pecas vem de `src/apresentacao.py`, que e quem decide o que o resultado
# tem. Este modulo NAO declara tipo proprio de cartao nem de cenario: dois
# dataclasses com os mesmos campos em arquivos diferentes e a forma mais
# discreta de a tela e o papel divergirem (D28).
from src.apresentacao import Cartao, Cenario
from src.css import (
    GRADE,
    MARCA_BORDA,
    MARCA_LAVADO,
    MARCA_VERMELHO,
    SUPERFICIE,
    SUPERFICIE_2,
    SUPERFICIE_3,
    SUPERFICIE_ESCURA,
    TINTA_CLARA,
    TINTA_CLARA_2,
    TINTA_DISCRETA,
    TINTA_PRIMARIA,
    TINTA_SECUNDARIA,
    TRACO,
)

# D1 na escala do papel: 14px de raio a 96 dpi sao ~3,7 mm. O cartao do PDF usa
# 2,6 mm porque ele e menor que o da tela e o mesmo raio absoluto o deixaria
# com cara de pilula.
RAIO = 2.6

# Caracteres tipograficos que o projeto usa na tela e que NAO existem em
# Latin-1. Sem esta tabela o `NFKD` + `ignore` os APAGA, e o titulo do
# documento saia "Simulacao de viabilidade  refil de palhetas", com o buraco
# onde estava o travessao. Transcrever preserva a leitura; apagar, nao.
_TRANSCRICAO = {
    "—": "-",  # travessao —
    "–": "-",  # meia-risca –
    "−": "-",  # sinal de menos tipografico − (formato.MENOS)
    # "->" e nao ">": sozinho, o ">" le como "maior que" ao lado de um numero,
    # e a faixa de manchete tem exatamente essa vizinhanca ("hoje R$ 3.780" /
    # "> R$ 15.570" seria lido como uma desigualdade).
    "→": "->",
    "≈": "~",  # aproximadamente ≈
    "◆": "*",  # losango de procedencia ◆
    "▪": "*",  # quadrado de procedencia ▪
    "≥": ">=",
    "≤": "<=",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "…": "...",
    " ": " ",
}


def texto(bruto: str) -> str:
    """Normaliza para Latin-1 TRANSCREVENDO o que nao cabe, nunca apagando.

    A ordem importa: transcreve primeiro, testa depois. Um `NFKD` direto sobre
    "—" nao produz "-" — produz nada, e o buraco passa despercebido ate o
    documento estar na mao do cliente.
    """
    convertido = bruto.translate(str.maketrans(_TRANSCRICAO))
    try:
        convertido.encode("latin-1")
        return convertido
    except UnicodeEncodeError:
        return (
            unicodedata.normalize("NFKD", convertido)
            .encode("latin-1", "ignore")
            .decode("latin-1")
        )


# ---------------------------------------------------------------------------
# Primitivas
# ---------------------------------------------------------------------------


def cartao(
    doc: FPDF,
    x: float,
    y: float,
    largura: float,
    altura: float,
    *,
    fundo: str,
    borda: str | None = None,
    raio: float = RAIO,
) -> None:
    """Retangulo de canto arredondado. A base de tudo que este modulo desenha."""
    doc.set_fill_color(fundo)
    if borda is not None:
        doc.set_draw_color(borda)
        doc.set_line_width(0.3)
        estilo = "DF"
    else:
        estilo = "F"
    doc.rect(
        x, y, largura, altura, style=estilo, round_corners=True, corner_radius=raio
    )


def _fonte_que_cabe(
    doc: FPDF,
    conteudo: str,
    largura: float,
    *,
    maximo: float,
    minimo: float,
    estilo: str = "B",
) -> float:
    """O maior corpo, entre `maximo` e `minimo`, que faz o texto caber.

    Existe por causa de um numero especifico: "R$ 1.241.000" no cartao de
    faturamento de uma rede de doze pontos de venda. Num cartao de 60 mm ele
    nao cabe em 20 pt, e um numero CORTADO num documento que sai da sala e pior
    do que um numero menor. Fixar o corpo no menor que serve para todo mundo,
    por outro lado, encolheria os numeros de todas as simulacoes por causa da
    maior — e a §3.2 e sobre ser lido, nao sobre caber.
    """
    corpo = maximo
    while corpo > minimo:
        doc.set_font("Helvetica", estilo, corpo)
        if doc.get_string_width(texto(conteudo)) <= largura:
            return corpo
        corpo -= 0.5
    doc.set_font("Helvetica", estilo, minimo)
    return minimo


def rotulo_de_secao(doc: FPDF, conteudo: str, tinta: str = TINTA_DISCRETA) -> None:
    """Versalete espacado, o mesmo papel do `.st-cartao-rotulo` da tela."""
    doc.set_font("Helvetica", "B", 7)
    doc.set_text_color(tinta)
    doc.set_char_spacing(0.6)
    doc.cell(0, 4, texto(conteudo.upper()), new_x="LMARGIN", new_y="NEXT")
    doc.set_char_spacing(0)


# ---------------------------------------------------------------------------
# Cartao de KPI — o gemeo do `.st-cartao` da tela
# ---------------------------------------------------------------------------


def kpi(
    doc: FPDF, x: float, y: float, largura: float, altura: float, dado: Cartao
) -> None:
    """Um cartao de apoio. CLARO — o escuro e a manchete, que e outra peca.

    `dado.valor is None` desenha o cartao SEM numero, e isso e estado legitimo e
    obrigatorio (§6.1.9, P9): o mark up nao existe quando o custo total e zero,
    e um "0%" ali significaria "vende ao preco de custo" — uma afirmacao que
    ninguem fez. O cartao mostra entao o MOTIVO no lugar do numero.
    """
    cartao(doc, x, y, largura, altura, fundo=SUPERFICIE, borda=TRACO)

    interno = 4.0
    util = largura - interno * 2

    doc.set_xy(x + interno, y + interno)
    doc.set_font("Helvetica", "B", 6.5)
    doc.set_text_color(TINTA_DISCRETA)
    doc.set_char_spacing(0.4)
    doc.multi_cell(util, 3.2, texto(dado.rotulo.upper()), align="L")
    doc.set_char_spacing(0)

    if dado.valor is not None:
        corpo = _fonte_que_cabe(doc, dado.valor, util, maximo=19, minimo=10)
        doc.set_text_color(TINTA_PRIMARIA)
        doc.set_xy(x + interno, y + altura - interno - 4 - corpo * 0.36)
        doc.cell(util, corpo * 0.36, texto(dado.valor))

    doc.set_font("Helvetica", "", 7.5)
    doc.set_text_color(TINTA_SECUNDARIA)
    doc.set_xy(x + interno, y + altura - interno - 3.6)
    doc.cell(util, 3.6, texto(dado.apoio))


def linha_de_kpis(
    doc: FPDF, x: float, y: float, largura: float, altura: float, dados: list[Cartao]
) -> float:
    """Os cartoes lado a lado. Devolve o y logo abaixo deles."""
    if not dados:
        return y
    folga = 3.0
    cada = (largura - folga * (len(dados) - 1)) / len(dados)
    for i, dado in enumerate(dados):
        kpi(doc, x + i * (cada + folga), y, cada, altura, dado)
    return y + altura


def manchete_dupla(
    doc: FPDF,
    x: float,
    y: float,
    largura: float,
    altura: float,
    esquerda: Cartao,
    direita: Cartao,
) -> float:
    """DOIS numeros do mesmo tamanho, lado a lado, na faixa escura de abertura.

    E a primeira coisa da pagina 1 e a maior coisa do documento (D26). Os dois
    tem o MESMO corpo de fonte, e nao um maior que o outro: o pedido foi "lado a
    lado, de forma bem grande e evidente", e hierarquizar um sobre o outro aqui
    responderia uma pergunta que ninguem fez.

    O CORPO E COMUM AOS DOIS, medido pelo que couber no MAIS LARGO. Ajustar cada
    um por conta propria faria "R$ 7.694.784" sair menor que "R$ 141.480" ao
    lado — e, em dois numeros pareados, tamanho diferente lê como importancia
    diferente, que e o contrario do que este desenho afirma.

    Escura pela mesma razao do primeiro cartao da tela (D6): branco sobre
    #141414 da 17,9:1, mais contraste do que preto sobre branco tinha, e o
    destaque nao precisa de preenchimento vermelho — que leria como alerta e
    fica a dois passos do que a §13.1 proibe.
    """
    cartao(doc, x, y, largura, altura, fundo=SUPERFICIE_ESCURA)

    interno = 7.0
    meio = x + largura / 2
    coluna = largura / 2 - interno * 1.5

    doc.set_draw_color(TINTA_SECUNDARIA)
    doc.set_line_width(0.3)
    doc.line(meio, y + 6, meio, y + altura - 6)

    corpo = min(
        _fonte_que_cabe(doc, esquerda.valor or "", coluna, maximo=32, minimo=13),
        _fonte_que_cabe(doc, direita.valor or "", coluna, maximo=32, minimo=13),
    )

    for dado, dx in ((esquerda, x + interno), (direita, meio + interno)):
        doc.set_xy(dx, y + interno - 1.5)
        doc.set_font("Helvetica", "B", 7)
        doc.set_text_color(TINTA_CLARA_2)
        doc.set_char_spacing(0.5)
        doc.multi_cell(coluna, 3.6, texto(dado.rotulo.upper()), align="L")
        doc.set_char_spacing(0)

        if dado.valor is not None:
            doc.set_font("Helvetica", "B", corpo)
            doc.set_text_color(TINTA_CLARA)
            doc.set_xy(dx, y + altura - interno - 5 - corpo * 0.36)
            doc.cell(coluna, corpo * 0.36, texto(dado.valor))

        doc.set_font("Helvetica", "", 8.5)
        doc.set_text_color(TINTA_CLARA_2)
        doc.set_xy(dx, y + altura - interno - 4)
        doc.cell(coluna, 4, texto(dado.apoio))

    return y + altura


# ---------------------------------------------------------------------------
# Barras: hoje x com o refil
# ---------------------------------------------------------------------------


def barras_hoje_versus_refil(
    doc: FPDF,
    x: float,
    y: float,
    largura: float,
    altura: float,
    *,
    hoje: float,
    incremental: float,
    rotulo_hoje: str,
    rotulo_refil: str,
    rotulo_incremental: str,
    nome_hoje: str,
    nome_refil: str,
) -> float:
    """Duas barras na MESMA grandeza: margem anual hoje e margem anual com refil.

    A segunda barra e EMPILHADA — a base e literalmente a mesma altura da
    primeira, e so o segmento de cima e novo. E o desenho que carrega o
    argumento inteiro sem uma frase: o que ja existe continua existindo, e o
    vermelho e o que entra.

    Empilhar em vez de justapor nao e estetica. Duas barras soltas convidam a
    ler "de X para Y" como substituicao, e substituicao e exatamente o que a
    premissa de canibalizacao NAO afirma (`P.CANIBALIZACAO_MODELADA`). A base
    repetida diz, no desenho, que nada foi trocado.

    O vermelho aqui e o segmento e a anotacao do vao — marca de grafico, o mesmo
    uso que `grafico_sensibilidade.py` faz na tela. Os VALORES ficam em tinta
    primaria (§13.1).
    """
    total = hoje + incremental
    teto = max(total, hoje, 1.0)

    faixa_rotulo = 9.0  # a faixa de baixo, com o nome de cada barra
    faixa_valor = 5.0  # a faixa de cima, com o valor de cada barra
    plot = altura - faixa_rotulo - faixa_valor
    base_y = y + faixa_valor + plot

    # A faixa da direita fica reservada para a anotacao do vao — por isso os
    # dois centros ficam a esquerda do meio, e nao simetricos na largura toda.
    largura_barra = min(38.0, (largura - 40) / 2)
    centro_1 = x + largura * 0.20
    centro_2 = x + largura * 0.52
    x1 = centro_1 - largura_barra / 2
    x2 = centro_2 - largura_barra / 2

    altura_hoje = plot * (hoje / teto) if hoje > 0 else 0.0
    altura_total = plot * (total / teto) if total > 0 else 0.0
    altura_incremental = max(altura_total - altura_hoje, 0.0)

    # --- barra 1: o que ha hoje -------------------------------------------
    if altura_hoje > 0:
        cartao(
            doc,
            x1,
            base_y - altura_hoje,
            largura_barra,
            altura_hoje,
            fundo=SUPERFICIE_3,
            borda=TRACO,
            raio=1.4,
        )

    # --- barra 2: a MESMA base, mais o incremental -------------------------
    #
    # Com incremental NEGATIVO a segunda barra e MAIS BAIXA que a primeira, e o
    # que aparece no lugar do segmento vermelho e o vao que falta, em contorno
    # tracejado. O plano §1.1 avisa que margem negativa e possivel — o documento
    # nao esconde, e tambem nao pinta de vermelho: numero negativo em vermelho
    # e exatamente o que a §13.1 proibe, e aqui o desenho ja diz o que houve.
    altura_base_2 = min(altura_hoje, altura_total)
    if altura_base_2 > 0:
        cartao(
            doc,
            x2,
            base_y - altura_base_2,
            largura_barra,
            altura_base_2,
            fundo=SUPERFICIE_3,
            borda=TRACO,
            raio=1.4,
        )
    if altura_incremental > 0:
        cartao(
            doc,
            x2,
            base_y - altura_total,
            largura_barra,
            altura_incremental,
            fundo=MARCA_VERMELHO,
            raio=1.4,
        )
    elif altura_total < altura_hoje - 0.5:
        doc.set_draw_color(TINTA_SECUNDARIA)
        doc.set_line_width(0.3)
        doc.set_dash_pattern(dash=1.2, gap=1.0)
        doc.rect(
            x2, base_y - altura_hoje, largura_barra, altura_hoje - altura_total
        )
        doc.set_dash_pattern()

    # --- a linha de base ---------------------------------------------------
    doc.set_draw_color(TRACO)
    doc.set_line_width(0.3)
    doc.line(x, base_y, x + largura, base_y)

    # --- valores, em tinta primaria ---------------------------------------
    doc.set_font("Helvetica", "B", 9)
    doc.set_text_color(TINTA_PRIMARIA)
    doc.set_xy(x1 - 8, base_y - altura_hoje - faixa_valor)
    doc.cell(largura_barra + 16, faixa_valor, texto(rotulo_hoje), align="C")
    doc.set_xy(x2 - 8, base_y - altura_total - faixa_valor)
    doc.cell(largura_barra + 16, faixa_valor, texto(rotulo_refil), align="C")

    # --- nome de cada barra ------------------------------------------------
    doc.set_font("Helvetica", "", 7.5)
    doc.set_text_color(TINTA_SECUNDARIA)
    doc.set_xy(x1 - 8, base_y + 1.5)
    doc.multi_cell(largura_barra + 16, 3.4, texto(nome_hoje), align="C")
    doc.set_xy(x2 - 8, base_y + 1.5)
    doc.multi_cell(largura_barra + 16, 3.4, texto(nome_refil), align="C")

    # --- a anotacao do vao: o incremental, medido no desenho ---------------
    #
    # A anotacao e VERMELHA so quando o vao e ganho — mesmo uso que a tela faz
    # em `grafico_sensibilidade` ("+ R$ 141.480" junto do vao entre as duas
    # linhas). Quando o vao e perda, a anotacao vai em tinta primaria, com o
    # sinal, pela regra da §13.1.
    topo_vao, base_vao = (
        (base_y - altura_total, base_y - altura_hoje)
        if altura_incremental > 0
        else (base_y - altura_hoje, base_y - altura_total)
    )
    if abs(base_vao - topo_vao) > 2:
        seta_x = x2 + largura_barra + 3
        tinta = MARCA_VERMELHO if altura_incremental > 0 else TINTA_PRIMARIA
        doc.set_draw_color(tinta)
        doc.set_line_width(0.5)
        doc.line(seta_x, topo_vao, seta_x, base_vao)
        doc.set_font("Helvetica", "B", 9)
        doc.set_text_color(tinta)
        doc.set_xy(seta_x + 2, (topo_vao + base_vao) / 2 - 2.5)
        doc.cell(largura - (seta_x - x) - 2, 5, texto(rotulo_incremental))

    return y + altura


# ---------------------------------------------------------------------------
# Tiras de cenario — os tres presets, lado a lado
# ---------------------------------------------------------------------------


def tiras_de_cenario(
    doc: FPDF, x: float, y: float, largura: float, altura: float, itens: list[Cenario]
) -> float:
    """Os tres cenarios medidos, um ao lado do outro, com o simulado destacado.

    O PESSIMISTA ENTRA, e entra com o mesmo tamanho dos outros dois. Um
    documento que mostrasse so o cenario favoravel seria material de venda; a
    faixa inteira e o que permite ao gerente escolher em qual acreditar — e a
    procedencia medida (§5.3, `LEGENDA_PRESETS_DIANTEIRO`) e o que sustenta os
    tres. E o cenario ATIVO e o que foi simulado nesta reuniao, marcado para o
    documento nao se contradizer com os cartoes acima.
    """
    if not itens:
        return y

    folga = 3.0
    cada = (largura - folga * (len(itens) - 1)) / len(itens)

    for i, item in enumerate(itens):
        ix = x + i * (cada + folga)
        cartao(
            doc,
            ix,
            y,
            cada,
            altura,
            fundo=MARCA_LAVADO if item.ativo else SUPERFICIE_2,
            borda=MARCA_BORDA if item.ativo else TRACO,
        )

        # A MARCA DO CENARIO ATIVO NAO PODE DEPENDER DE COR (§3.1.3 / §9.4). O
        # fundo lavado e a borda rosa somem numa impressora preto e branco — e
        # este documento vai ser impresso. A barra lateral grossa sobrevive: em
        # tons de cinza ela vira um traco escuro que nenhum outro cartao tem.
        #
        # So a margem ESQUERDA abre espaco para a barra; a vertical continua
        # igual a dos outros dois, senao o cartao ativo desalinharia a linha.
        if item.ativo:
            doc.set_draw_color(MARCA_VERMELHO)
            doc.set_line_width(1.2)
            doc.line(ix + 0.6, y + 2, ix + 0.6, y + altura - 2)

        vertical = 3.0
        esquerda = 4.6 if item.ativo else 3.0
        util = cada - esquerda - 3.0

        doc.set_xy(ix + esquerda, y + vertical)
        doc.set_font("Helvetica", "B", 6.5)
        doc.set_text_color(MARCA_VERMELHO if item.ativo else TINTA_DISCRETA)
        doc.set_char_spacing(0.5)
        doc.cell(util, 3.2, texto(item.rotulo.upper()))
        doc.set_char_spacing(0)

        doc.set_xy(ix + esquerda, y + vertical + 3.6)
        doc.set_font("Helvetica", "", 7)
        doc.set_text_color(TINTA_SECUNDARIA)
        doc.cell(util, 3.2, texto(item.aproveitamento))

        corpo = _fonte_que_cabe(doc, item.valor, util, maximo=13, minimo=8)
        doc.set_text_color(TINTA_PRIMARIA)
        doc.set_xy(ix + esquerda, y + altura - vertical - 4.2 - corpo * 0.36)
        doc.cell(util, corpo * 0.36, texto(item.valor))

        doc.set_font("Helvetica", "", 6.5)
        doc.set_text_color(TINTA_SECUNDARIA)
        doc.set_xy(ix + esquerda, y + altura - vertical - 3.2)
        doc.cell(util, 3.2, texto(item.apoio))

    return y + altura


# ---------------------------------------------------------------------------
# A curva de sensibilidade
# ---------------------------------------------------------------------------


# `ticks_de_eixo` MUDOU DE CASA em D28: onde os ticks caem e decisao de
# apresentacao, nao de tinta, e a tela precisa dela tanto quanto o papel. Vive
# agora em `src/apresentacao.py`, que e puro; `curva()` recebe os ticks prontos.


def curva(
    doc: FPDF,
    x: float,
    y: float,
    largura: float,
    altura: float,
    *,
    pontos: list[tuple[float, float]],
    dominio_x: tuple[int, int],
    base: float | None,
    atual_x: float,
    atual_y: float,
    rotulo_atual: str,
    rotulo_base: str | None,
    ticks_y: list[tuple[float, str]],
    marcas_x: list[float],
) -> float:
    """A curva inteira, com marcador na posicao simulada. Gemeo da §5.11.

    As mesmas marcas da tela, e pelas mesmas razoes:

      curva          2 linhas de espessura, TINTA PRIMARIA. Nunca vermelha
      area           NENHUMA — um wash desaparece no papel como desaparece no
                     showroom, e nao acrescenta leitura
      base           horizontal TRACEJADA em tinta secundaria: "so com a
                     palheta original". Nao depende do aproveitamento do refil,
                     por isso e reta
      marcas         verticais finas nos tres presets, SOLIDAS
      grade          horizontal, solida, so nos ticks. Sem grade vertical — as
                     marcas dos presets ja ocupam esse canal
      marcador       o UNICO vermelho da curva, com anel na cor da superficie

    A distincao entre as duas linhas nao depende de cor (§3.1.3 / §9.4): sao
    tinta diferente, tracejado diferente e rotulo direto proprio. Sobrevive a
    impressao em preto e branco, que e o destino provavel deste documento.
    """
    if not pontos:
        return y

    # A GOTEIRA DOS ROTULOS DO EIXO Y. O plot comeca DEPOIS dela, e nao na
    # margem: com `px` mapeando o dominio na largura inteira, a curva entrava
    # por baixo dos rotulos "R$ 200 mil" e o rotulo "0%" do eixo X caia fora do
    # eixo desenhado. Aparecia so no papel — nenhum teste de texto pega isso.
    goteira = 17.0
    faixa_x = 6.0
    plot = altura - faixa_x
    largura_plot = largura - goteira
    lo, hi = dominio_x

    valores = [valor for _, valor in pontos]
    if base is not None:
        valores.append(base)
    valores.extend(valor for valor, _ in ticks_y)
    piso, teto = min(valores), max(valores)
    if teto - piso < 1e-9:
        teto = piso + 1.0
    # Folga em cima e embaixo: sem ela a curva encosta na borda do plot e o
    # ultimo ponto sai lendo como se o desenho tivesse sido cortado.
    folga = (teto - piso) * 0.08
    piso, teto = piso - folga, teto + folga

    def px(pp: float) -> float:
        return x + goteira + (pp - lo) / (hi - lo) * largura_plot

    def py(valor: float) -> float:
        return y + plot - (valor - piso) / (teto - piso) * plot

    # --- grade horizontal e ticks -----------------------------------------
    doc.set_line_width(0.2)
    doc.set_font("Helvetica", "", 6.5)
    for valor, rotulo in ticks_y:
        gy = py(valor)
        doc.set_draw_color(GRADE)
        doc.line(x + goteira, gy, x + largura, gy)
        doc.set_text_color(TINTA_SECUNDARIA)
        doc.set_xy(x, gy - 2)
        doc.cell(goteira - 2, 4, texto(rotulo), align="R")

    # --- marcas verticais dos presets, SOLIDAS ----------------------------
    doc.set_draw_color(TRACO)
    doc.set_line_width(0.2)
    for pp in marcas_x:
        if lo <= pp <= hi:
            doc.line(px(pp), y, px(pp), y + plot)

    # --- eixo x ------------------------------------------------------------
    doc.set_draw_color(TRACO)
    doc.set_line_width(0.3)
    doc.line(x + goteira, y + plot, x + largura, y + plot)
    doc.set_font("Helvetica", "", 6.5)
    doc.set_text_color(TINTA_SECUNDARIA)
    for pp in range(lo, hi + 1, 10):
        doc.set_xy(px(pp) - 5, y + plot + 1)
        doc.cell(10, 4, texto(f"{pp}%"), align="C")

    # --- a base tracejada: so com a palheta original ----------------------
    if base is not None:
        doc.set_draw_color(TINTA_SECUNDARIA)
        doc.set_line_width(0.4)
        doc.set_dash_pattern(dash=1.6, gap=1.0)
        doc.line(x + goteira, py(base), x + largura, py(base))
        doc.set_dash_pattern()
        if rotulo_base:
            doc.set_font("Helvetica", "B", 6.5)
            doc.set_text_color(TINTA_SECUNDARIA)
            doc.set_xy(x + goteira + 2, py(base) - 4.4)
            doc.cell(largura - goteira - 4, 4, texto(rotulo_base))

    # --- o vao entre as duas, medido na posicao simulada ------------------
    if base is not None and abs(py(base) - py(atual_y)) > 3:
        doc.set_draw_color(MARCA_VERMELHO)
        doc.set_line_width(0.5)
        doc.line(px(atual_x), py(base), px(atual_x), py(atual_y))

    # --- a curva: 2 de espessura, TINTA PRIMARIA --------------------------
    doc.set_draw_color(TINTA_PRIMARIA)
    doc.set_line_width(0.6)
    doc.polyline([(px(pp), py(valor)) for pp, valor in pontos], style="D")

    # --- marcador: o unico vermelho -----------------------------------
    mx, my = px(atual_x), py(atual_y)
    doc.set_fill_color(SUPERFICIE)
    doc.set_draw_color(SUPERFICIE)
    doc.circle(mx, my, 2.2, style="DF")
    doc.set_fill_color(MARCA_VERMELHO)
    doc.set_draw_color(MARCA_VERMELHO)
    doc.circle(mx, my, 1.5, style="DF")

    # --- rotulo direto do marcador ----------------------------------------
    #
    # SOBRE UM RETANGULO DA COR DA SUPERFICIE: a curva sobe justamente onde o
    # marcador esta, e sem o fundo o valor sai riscado pela propria linha —
    # exatamente o que acontecia na primeira versao deste desenho. O Altair
    # resolve isso na tela porque o rotulo mora fora da curva; no papel, o
    # espaco e menor e a colisao e a regra, nao a excecao.
    doc.set_font("Helvetica", "B", 7.5)
    largura_rotulo = doc.get_string_width(texto(rotulo_atual)) + 3
    vira = (mx + 4 + largura_rotulo) > (x + largura)
    rx = mx - largura_rotulo - 3 if vira else mx + 3
    ry = my - 7.5

    doc.set_fill_color(SUPERFICIE)
    doc.rect(rx - 0.6, ry - 0.4, largura_rotulo + 1.2, 5, style="F")
    doc.set_text_color(TINTA_PRIMARIA)
    doc.set_xy(rx, ry)
    doc.cell(largura_rotulo, 4.2, texto(rotulo_atual), align="C")

    return y + altura

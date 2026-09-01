"""O RESULTADO, montado uma vez e desenhado duas. D28.

Pedido do cliente em 27/08/2026: *"a tela de resultados deve ser exatamente
igual o que aparece no PDF. Com todos os graficos, tabelas e KPIs."*

"Exatamente igual" nao se consegue escrevendo a mesma coisa em dois lugares —
se consegue TIRANDO A DECISAO dos dois lugares. Este modulo e o unico lugar que
decide QUAIS blocos o resultado tem, EM QUE ORDEM, com QUE rotulo e QUE numero
JA FORMATADO. Quem desenha nao decide nada:

    apresentacao.montar(e, r)          <- aqui, uma vez
        |
        +-- componentes/bloco_resultado.py   desenha em HTML/CSS na tela
        +-- componentes/exportador_pdf.py    desenha em vetor no papel

E a mesma separacao que ja existia entre `exportador_pdf` (o que entra) e
`pdf_visual` (a tinta) — so que agora o "o que entra" e compartilhado. Uma
divergencia entre a tela e o papel deixou de ser possivel por descuido: ela
exige editar este arquivo, e `test_paridade_tela_e_pdf` reprova quem editar so
um dos dois desenhos.

ESTE MODULO E PURO. Nao importa streamlit e nao importa fpdf — nem
indiretamente. E o que permite testar a apresentacao inteira sem subir o app e
sem gerar PDF, e e a mesma doutrina de `calculo.py`.

NUMEROS JA FORMATADOS, e nunca `float`, nos campos de texto: o arredondamento e
a virgula sao decisao de apresentacao (§6.1.5), e deixa-los para quem desenha
seria abrir a porta para a tela mostrar `R$ 141.480` e o papel `R$ 141.480,00`.
Os poucos `float` que sobrevivem aqui sao os que o DESENHO precisa como
geometria — a altura de uma barra, a coordenada de um ponto da curva.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

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


# ---------------------------------------------------------------------------
# As pecas
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Cartao:
    """Um KPI. `valor=None` desenha o cartao SEM numero.

    Cartao sem numero e estado legitimo e obrigatorio (§6.1.9, P9): o mark up
    nao existe quando o custo total e zero, e um "0%" ali significaria "vende ao
    preco de custo", que e uma afirmacao que ninguem fez. O cartao mostra entao
    o MOTIVO no lugar do numero.
    """

    rotulo: str
    valor: str | None
    apoio: str


@dataclass(frozen=True)
class Barras:
    """O comparativo anual: duas barras na mesma grandeza, a segunda EMPILHADA.

    `hoje` e `incremental` sao os unicos `float` da peca, e sao geometria: quem
    desenha precisa da proporcao entre eles para dar altura as barras. Tudo que
    e lido vem formatado.
    """

    hoje: float
    incremental: float
    rotulo_hoje: str
    rotulo_refil: str
    rotulo_incremental: str
    nome_hoje: str
    nome_refil: str
    nota: str


@dataclass(frozen=True)
class Cenario:
    rotulo: str
    aproveitamento: str
    valor: str
    apoio: str
    ativo: bool


@dataclass(frozen=True)
class Cashback:
    total: str
    nota: str
    rateio: str


@dataclass(frozen=True)
class Curva:
    """A curva de sensibilidade. `pontos` e `ticks` sao geometria + rotulo."""

    pontos: tuple[tuple[float, float], ...]
    dominio_x: tuple[int, int]
    base: float | None
    atual_x: float
    atual_y: float
    rotulo_atual: str
    rotulo_base: str | None
    ticks: tuple[tuple[float, str], ...]
    marcas_x: tuple[float, ...]
    subtitulo: str
    frase: str


@dataclass(frozen=True)
class Secao:
    """Um bloco de `rotulo ... valor`, com titulo e nota opcional."""

    titulo: str
    linhas: tuple[tuple[str, str], ...]
    nota: str = ""


@dataclass(frozen=True)
class Apresentacao:
    """O resultado inteiro, na ORDEM em que as duas superficies o desenham.

    A ordem dos campos desta classe E a ordem de leitura, e ela e normativa
    (D21, D26). Reordenar aqui reordena os dois desenhos de uma vez — que e
    exatamente o ponto deste modulo.
    """

    # 1. a abertura: os dois numeros, lado a lado, no maior corpo (D26)
    manchete: tuple[Cartao, Cartao] | None = None
    nota_do_grupo: str = ""
    # 2. os tres de apoio
    apoio: tuple[Cartao, ...] = ()
    # 3. hoje x com o refil, no ano
    titulo_barras: str = ""
    barras: Barras | None = None
    # 4. os tres cenarios medidos
    titulo_cenarios: str = ""
    cenarios: tuple[Cenario, ...] = ()
    nota_cenarios: str = ""
    # 5. o cashback — acrescenta, nunca subtrai
    cashback: Cashback | None = None
    # 6. como o resultado varia
    titulo_curva: str = ""
    curva: Curva | None = None
    # 7. a auditoria
    premissas: Secao | None = None
    preco_custo: Secao | None = None
    decisoes: Secao | None = None
    # E o estado E1: sem valor anual nao ha manchete, e o motivo vai dito.
    incompleto: str = ""
    traducao: str = ""


# ---------------------------------------------------------------------------
# Eixo
# ---------------------------------------------------------------------------

# Passos "redondos", como fracao da potencia de dez da faixa. Uma regua de
# `R$ 47.160 / R$ 94.320` ninguem usa de relance, e a regua existe justamente
# para ser lida de relance.
_PASSOS_REDONDOS = (0.1, 0.2, 0.25, 0.5, 1.0, 2.0)
_TICKS_DEMAIS = 8


def ticks_de_eixo(piso: float, teto: float, quantidade: int = 4) -> list[float]:
    """Onde os ticks caem. Nao decide como eles LEEM — isso e de quem chama.

    ESCOLHE O PASSO PELA CONTAGEM QUE ELE PRODUZ, e nao pela largura do
    intervalo. A primeira versao derivava o passo de `faixa / (quantidade - 1)`
    e arredondava para cima ate o proximo passo redondo — e o arredondamento
    para cima pode DOBRAR o passo. Numa faixa de R$ 45 mil a R$ 390 mil isso
    saltava de R$ 100 mil para R$ 200 mil e o eixo saia com UM tick so, o que
    deixa de ser regua: sem um segundo tick nao ha escala, so um numero solto ao
    lado de uma linha.

    Aqui cada passo candidato e testado, e vence o que chega mais perto de
    `quantidade` ticks dentro do intervalo.
    """
    if teto - piso < 1e-9 or quantidade < 2:
        return [piso]

    magnitude = 10 ** math.floor(math.log10(teto - piso))
    melhor: list[float] = []
    melhor_erro: int | None = None

    for escala in _PASSOS_REDONDOS:
        passo = escala * magnitude
        valores: list[float] = []
        atual = math.ceil(piso / passo) * passo
        while atual <= teto + 1e-9:
            valores.append(atual)
            if len(valores) > _TICKS_DEMAIS:
                break
            atual += passo

        if len(valores) < 2 or len(valores) > _TICKS_DEMAIS:
            continue
        erro = abs(len(valores) - quantidade)
        if melhor_erro is None or erro < melhor_erro:
            melhor, melhor_erro = valores, erro

    return melhor or [piso, teto]


def rotulos_do_eixo(piso: float, teto: float) -> tuple[tuple[float, str], ...]:
    """Os ticks com a forma ABREVIADA — mas so quando ela distingue.

    `moeda_curta` arredonda por construcao, e numa faixa estreita ela colapsa:
    R$ 1.000, R$ 1.050 e R$ 1.100 viram tres ticks lendo "R$ 1 mil". Tres ticks
    identicos em alturas diferentes nao sao uma regua — sao uma contradicao no
    desenho. Quando a forma curta repete, o eixo cai para o numero inteiro.
    """
    brutos = ticks_de_eixo(piso, teto)
    curtos = [formato.moeda_curta(valor) for valor in brutos]
    if len(set(curtos)) == len(curtos):
        return tuple(zip(brutos, curtos))
    return tuple((valor, formato.moeda_agregada(valor)) for valor in brutos)


# ---------------------------------------------------------------------------
# A montagem
# ---------------------------------------------------------------------------


def documento_interno(e: Entradas) -> bool:
    """O documento carrega custo de aquisicao — e o custo E o preco de venda da
    Suicatech (plano §6.3). Vale para as duas superficies pelo mesmo criterio."""
    return (
        e.custo_dianteiro is not None
        or e.custo_traseiro is not None
        or e.custo_original is not None
    )


def montar(e: Entradas, r: Resultado) -> Apresentacao:
    """O resultado inteiro, pronto para desenhar. A UNICA fonte da ordem."""
    traducao = formato.traducao_por_passagem(r.traducao_fracao)

    if r.anual is None:
        return Apresentacao(
            traducao=traducao,
            incompleto=(
                "A simulação está incompleta: faltam as passagens por mês ou o "
                "preço e o custo do refil. Nenhum valor é exibido no lugar — um "
                "default de R$ 0 ancoraria no cenário mais favorável possível, "
                "e seria falso."
            ),
            premissas=_premissas(e, r),
            preco_custo=_preco_custo(e),
            decisoes=_decisoes(),
        )

    return Apresentacao(
        manchete=_manchete(r),
        nota_do_grupo=(
            f"Valores anuais · {rotulo_do_resultado(r)} · {P.rotulo_do_anual()}"
        ),
        apoio=_apoio(r, traducao),
        titulo_barras="Margem de contribuição no ano: hoje e com o refil",
        barras=_barras(r),
        titulo_cenarios="Os três cenários medidos na carteira",
        cenarios=_cenarios(e, r),
        nota_cenarios=_nota_dos_cenarios(e),
        cashback=_cashback(r),
        titulo_curva="Como o resultado varia com o aproveitamento",
        curva=_curva(e, r),
        premissas=_premissas(e, r),
        preco_custo=_preco_custo(e),
        decisoes=_decisoes(),
        traducao=traducao,
    )


def _manchete(r: Resultado) -> tuple[Cartao, Cartao]:
    """Faturamento a esquerda, margem a direita — a ordem dos cartoes de D21.

    A GRANDEZA DE CADA UM VAI NO ROTULO, e nao so na nota do grupo: sao duas
    contas diferentes no mesmo corpo de fonte, e a §4 exige que todo resultado
    financeiro diga qual conta ele e. "Faturamento" nao e "margem".
    """
    mensal = r.faturamento_refil or 0.0
    return (
        Cartao(
            "Faturamento adicional",
            formato.moeda_agregada(mensal * MESES_NO_ANO),
            f"{formato.moeda_agregada(mensal)} por mês",
        ),
        Cartao(
            "Margem de contribuição adicional",
            formato.moeda_agregada(r.anual or 0.0),
            f"{formato.moeda_agregada(r.incremental_mensal or 0.0)} por mês",
        ),
    )


def _apoio(r: Resultado, traducao: str) -> tuple[Cartao, ...]:
    """Mark up, traducao em escala humana e o contraste do mes."""
    return (_cartao_markup(r), _cartao_traducao(r), _cartao_nova_margem(r))


def _cartao_markup(r: Resultado) -> Cartao:
    # O APOIO NOMEIA A CONTA, e nao e decoracao (§4). "108%" ao lado de duas
    # colunas de reais convida a leitura de MARGEM percentual, que e outra
    # conta — `(faturamento - custo) / faturamento` — e daria 52% no mesmo
    # cenario. A linha embaixo do numero e o que impede a troca (D27).
    if r.markup_operacao is not None:
        return Cartao(
            "Mark up da operação",
            formato.markup_percentual(r.markup_operacao),
            "(faturamento − custo) ÷ custo",
        )
    return Cartao("Mark up da operação", None, "sem custo total para dividir")


def _cartao_traducao(r: Resultado) -> Cartao:
    """A traducao em escala humana (§5.5, P2).

    Ela nao abre mais o resultado — D21 a tirou da tela e D26 a desceu no PDF —,
    mas continua existindo nas duas superficies, no mesmo cartao. A forma curta
    ocupa o lugar do numero e a frase inteira fica no apoio, que e como o cartao
    de KPI e construido.
    """
    return Cartao(
        "O que isso significa na oficina",
        formato.traducao_curta(r.traducao_fracao),
        "carros que entram viram um par de refil",
    )


def _cartao_nova_margem(r: Resultado) -> Cartao:
    """"Nova margem com refil" (D27).

    So aparece com margem da original para comparar. Sem o custo dela nao existe
    margem dela, e comparar margem com faturamento misturaria grandezas
    (§6.1.5) — o cartao entao declara o motivo, e nao um numero.

    O periodo vive no apoio, junto do valor de hoje: sem ele o numero grande
    perderia o periodo, e um valor mensal lido como anual erra por 12x.
    """
    if r.margem_atual is None or r.incremental_mensal is None:
        return Cartao(
            "Nova margem com refil", None, "custo da original não informado"
        )
    total = r.margem_atual + r.incremental_mensal
    return Cartao(
        "Nova margem com refil",
        formato.moeda_agregada(total),
        f"por mês · hoje {formato.moeda_agregada(r.margem_atual)}",
    )


def _barras(r: Resultado) -> Barras | None:
    """Duas barras na MESMA grandeza, a segunda com a MESMA base da primeira.

    Empilhar em vez de justapor nao e estetica. Duas barras soltas convidam a
    ler "de X para Y" como substituicao, e substituicao e exatamente o que a
    premissa de canibalizacao NAO afirma (`P.CANIBALIZACAO_MODELADA`). A base
    repetida diz, no desenho, que nada foi trocado — e a nota repete em palavras.
    """
    if r.margem_atual is None or r.anual is None:
        return None

    hoje = r.margem_atual * MESES_NO_ANO
    ganho = r.anual >= 0
    return Barras(
        hoje=hoje,
        incremental=r.anual,
        rotulo_hoje=formato.moeda_agregada(hoje),
        rotulo_refil=formato.moeda_agregada(hoje + r.anual),
        # `moeda_agregada` ja traz o sinal de menos quando o valor e negativo
        # (§5.5). O "+" so entra quando ha o que somar — senao a linha sairia
        # "+ −R$ 36.828".
        rotulo_incremental=(
            f"+ {formato.moeda_agregada(r.anual)}"
            if ganho
            else formato.moeda_agregada(r.anual)
        ),
        nome_hoje="hoje, só com a palheta original",
        nome_refil="com o refil",
        nota=(
            "A base das duas barras é a mesma de propósito: nenhuma venda de "
            f"refil é descontada da palheta original — {P.TEXTO_SEM_CANIBALIZACAO}. "
            + (
                "O segmento de cima é o que entra."
                if ganho
                else "Com este preço e este custo, o refil fica abaixo do que a "
                "palheta original já entrega — o vão tracejado é a diferença."
            )
        ),
    )


def _cenarios(e: Entradas, r: Resultado) -> tuple[Cenario, ...]:
    """As tres faixas medidas da carteira, com a simulada destacada.

    RECALCULA cada preset a partir das MESMAS entradas — mesmo preco, mesmo
    custo, mesma operacao —, trocando so o par de aproveitamento. E o mesmo
    caminho que os botoes de cenario da tela percorrem (§5.3): um preset e um
    PAR medido, e aplicar um escreve as duas grandezas.

    O PESSIMISTA ENTRA, e com o mesmo tamanho dos outros dois. Um resultado que
    mostrasse so o cenario favoravel seria material de venda; a faixa inteira e
    o que permite ao gerente escolher em qual acreditar.
    """
    if r.anual is None:
        return ()

    ativo = preset_ativo(e)
    itens: list[Cenario] = []

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
        itens.append(
            Cenario(
                rotulo=preset.rotulo,
                aproveitamento=(
                    f"{formato.percentual(preset.dianteiro)} dianteiro · "
                    f"{formato.percentual(preset.traseiro)} traseiro"
                ),
                valor=formato.moeda_agregada(simulado.anual),
                apoio=(
                    "por ano · "
                    f"{formato.moeda_agregada(simulado.anual / MESES_NO_ANO)}/mês"
                ),
                ativo=preset.nome == ativo,
            )
        )
    return tuple(itens)


def _nota_dos_cenarios(e: Entradas) -> str:
    if preset_ativo(e) is None:
        return (
            f"Esta simulação usa {formato.percentual(e.aproveitamento_dianteiro)} "
            "de aproveitamento dianteiro, ajustado na reunião — entre os "
            f"cenários acima. {P.LEGENDA_PRESETS_DIANTEIRO}."
        )
    return (
        "O cenário simulado nesta reunião está destacado. "
        f"{P.LEGENDA_PRESETS_DIANTEIRO}."
    )


def _cashback(r: Resultado) -> Cashback | None:
    """ACRESCENTA, nunca subtrai (§6.1.7, plano decisao A).

    Declara quem paga. NUNCA quanto isso custa a Suicatech — esse numero nao
    existe nem como campo (§6.1.9).
    """
    if not r.cashback_total:
        return None
    return Cashback(
        total=(
            f"{formato.moeda_agregada(r.cashback_total)}/mês de cashback "
            "para sua equipe"
        ),
        nota="pago pela Suicatech, não sai da sua margem",
        rateio=" · ".join(
            f"{nome} {formato.moeda_agregada(valor)}/mês"
            for nome, valor in r.cashback_por_destinatario
        ),
    )


def _curva(e: Entradas, r: Resultado) -> Curva | None:
    """A curva inteira, com marcador na posicao simulada (§5.11).

    "O cliente ve o intervalo completo SEM INTERAGIR." Com margem da original a
    curva mostra o TOTAL das duas linhas e o vao entre elas e o incremental; sem
    ela, volta a uma linha so, plotando o incremental — o app nao inventa margem
    para a original.
    """
    if r.anual is None:
        return None

    pontos, base = curvas_comparadas(e)
    if not pontos:
        return None

    atual_y = (base + r.anual) if base is not None else r.anual
    valores = [valor for _, valor in pontos] + (
        [base] if base is not None else []
    )
    congelado = (
        f"traseiro fixo em {formato.percentual(e.aproveitamento_traseiro)}"
        if r.traseiro_na_conta
        else "traseiro fora da conta"
    )

    return Curva(
        pontos=tuple(pontos),
        dominio_x=P.SLIDER_DOMINIO,
        base=base,
        atual_x=e.aproveitamento_dianteiro * 100,
        atual_y=atual_y,
        rotulo_atual=formato.moeda_agregada(atual_y),
        rotulo_base="só com a palheta original" if base is not None else None,
        ticks=rotulos_do_eixo(min(valores), max(valores)),
        marcas_x=tuple(preset.dianteiro * 100 for preset in P.PRESETS),
        subtitulo=(
            f"{congelado} · só o dianteiro varia. "
            + (
                "A distância entre as duas linhas é a margem adicional."
                if base is not None
                else "A linha é a margem de contribuição do refil."
            )
        ),
        frase=_frase_do_cruzamento(pontos, base),
    )


def _frase_do_cruzamento(
    pontos: list[tuple[float, float]], base: float | None
) -> str:
    """"a partir de X% o refil supera o que ha hoje" — se houver um X.

    Sem cruzamento no dominio, DIZ isso em vez de sugerir que existe: o app nao
    promete um ponto de virada que a conta nao tem.
    """
    if base is None:
        return ""

    cruzamento = next((pp for pp, total in pontos if total > base), None)
    if cruzamento is None:
        return (
            "O refil não supera a palheta original em nenhum ponto da faixa — "
            "confira preço e custo das duas categorias."
        )
    if cruzamento <= P.SLIDER_DOMINIO[0]:
        return (
            "O refil supera a palheta original em toda a faixa de "
            "aproveitamento."
        )
    return (
        f"A partir de {int(cruzamento)}% de aproveitamento o refil passa a "
        "render mais que continuar só com a palheta original."
    )


def _premissas(e: Entradas, r: Resultado) -> Secao:
    """O que a conta assumiu. Vale nas duas superficies pelo mesmo motivo.

    A PREMISSA MAIS FAVORAVEL VAI IMPRESSA (sem canibalizacao): a §5.10 proibe
    premissa que muda o resultado sem aparecer, e o documento sai da sala sem
    ninguem ao lado para explicar.
    """
    linhas: list[tuple[str, str]] = [
        ("Pontos de venda", str(e.pontos_de_venda))
    ]

    if e.passagens_por_ponto is not None:
        linhas.append(
            (
                "Passagens por mês, por ponto de venda",
                formato.inteiro(e.passagens_por_ponto),
            )
        )
        linhas.append(
            (
                "Passagens por mês, no total",
                formato.inteiro(r.passagens_totais or 0),
            )
        )

    linhas.append(
        (
            "Aproveitamento dianteiro",
            f"{formato.percentual(e.aproveitamento_dianteiro)} "
            f"({_procedencia_dianteiro(e)})",
        )
    )

    if r.traseiro_na_conta:
        linhas.append(
            (
                "Aproveitamento traseiro",
                f"{formato.percentual(e.aproveitamento_traseiro)} "
                f"({_procedencia_traseiro(e)})",
            )
        )
    else:
        linhas.append(("Traseiro", "preço não informado — fora da conta"))

    if not P.CANIBALIZACAO_MODELADA:
        linhas.append(("Canibalização", P.TEXTO_SEM_CANIBALIZACAO))

    if r.originais_por_mes is not None:
        linhas.append(
            ("Palhetas vendidas hoje, por mês", formato.inteiro(r.originais_por_mes))
        )
    if e.preco_original is not None:
        linhas.append(
            (
                "Preço da palheta original cobrado hoje",
                formato.moeda_unitaria(e.preco_original),
            )
        )
    if r.margem_unitaria_original is not None:
        linhas.append(
            (
                "Margem unitária da palheta original",
                formato.moeda_unitaria(r.margem_unitaria_original),
            )
        )
    elif e.preco_original is not None:
        linhas.append(
            ("Margem da palheta original", "custo não informado — sem incremental")
        )
    if r.margem_atual is not None:
        linhas.append(
            (
                "Margem mensal atual com palhetas",
                formato.moeda_agregada(r.margem_atual),
            )
        )

    return Secao("As premissas desta simulação", tuple(linhas))


def _preco_custo(e: Entradas) -> Secao | None:
    """Preco e custo de tabela — SO quando o custo de aquisicao entra.

    O custo E o preco de venda da Suicatech (plano §6.3), e e ele que faz o
    documento virar interno.
    """
    if not documento_interno(e):
        return None

    linhas: list[tuple[str, str]] = []
    if e.preco_dianteiro is not None:
        linhas.append(
            (
                "Preço ao consumidor final, por par (dianteiro)",
                formato.moeda_unitaria(e.preco_dianteiro),
            )
        )
    if e.custo_dianteiro is not None:
        linhas.append(
            (
                "Custo de aquisição, por par (dianteiro)",
                formato.moeda_unitaria(e.custo_dianteiro),
            )
        )
    if e.preco_traseiro is not None:
        linhas.append(
            (
                "Preço ao consumidor final, por unidade (traseiro)",
                formato.moeda_unitaria(e.preco_traseiro),
            )
        )
    if e.custo_traseiro is not None:
        linhas.append(
            (
                "Custo de aquisição, por unidade (traseiro)",
                formato.moeda_unitaria(e.custo_traseiro),
            )
        )

    return Secao(
        "Preço e custo de tabela",
        tuple(linhas),
        # "este documento" nao serve mais: o mesmo texto agora aparece NA TELA,
        # onde nao ha documento nenhum (D28). A frase diz o que vale nos dois
        # lugares — que o PDF desta simulacao sai marcado como interno.
        nota=(
            "Preço e custo vêm da tabela Suicatech vigente. Por conterem o "
            "custo de aquisição, o PDF sai marcado como documento interno."
        ),
    )


def _decisoes() -> Secao | None:
    """O que ainda nao foi decidido, IMPRESSO (§5.12).

    "Um PDF que sai da sala sem dizer o que ainda nao foi decidido e pior que a
    tela, porque ninguem esta ao lado para explicar." Na tela vale o mesmo: o
    gerente le o resultado sozinho depois que o vendedor sai da sala.
    """
    abertas = aberto.decisoes_abertas_ativas()
    if not abertas:
        return None
    return Secao(
        "O que esta simulação ainda não considera",
        tuple((f"decisão {letra}", texto) for letra, texto in abertas),
        nota=(
            "Estes pontos não têm valor definido. O comportamento adotado é "
            "sempre o mais conservador, nunca o mais favorável:"
        ),
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

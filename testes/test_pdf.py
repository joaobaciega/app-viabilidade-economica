"""O PDF do cenario — componente +18, gerado no servidor.

O documento SAI DA SALA. Por isso ele obedece as mesmas regras de vocabulario
da tela, e carrega marca-d'agua quando inclui o custo de aquisicao (que e o
preco de venda da Suicatech, plano §6.3).
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from src import parametros as P
from src.calculo import calcular
from src.componentes.exportador_pdf import gerar_pdf, nome_do_arquivo
from testes.conftest import entradas_do_caso


def _pdf(nome_do_caso: str = "T1", cliente: str = "") -> bytes:
    entradas = entradas_do_caso(nome_do_caso)
    return gerar_pdf(entradas, calcular(entradas), cliente)


def _paginas(dados: bytes) -> int:
    """Quantas paginas o documento tem, contando os objetos `/Type /Page`.

    `[^s]` no fim para nao casar com `/Type /Pages`, que e o NO DE INDICE e
    aparece uma vez por documento.
    """
    import re

    return len(re.findall(rb"/Type\s*/Page[^s]", dados))


def _texto_do_pdf(dados: bytes) -> str:
    """Extrai texto legivel do PDF sem dependencia extra.

    fpdf2 escreve os literais de texto entre parenteses nos operadores Tj/TJ.
    Isso basta para verificar presenca e ausencia de vocabulario, que e o que
    interessa aqui.
    """
    import re
    import zlib

    partes: list[str] = []
    for fluxo in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", dados, re.S):
        try:
            conteudo = zlib.decompress(fluxo)
        except zlib.error:
            conteudo = fluxo
        for literal in re.findall(rb"\((?:[^()\\]|\\.)*\)", conteudo):
            partes.append(
                literal[1:-1]
                .replace(b"\\(", b"(")
                .replace(b"\\)", b")")
                .decode("latin-1", "ignore")
            )
    return " ".join(partes)


def test_pdf_e_gerado() -> None:
    dados = _pdf()
    assert dados.startswith(b"%PDF"), "saida precisa ser um PDF valido"
    assert len(dados) > 1000


def test_pdf_traz_os_numeros_do_cenario() -> None:
    texto = _texto_do_pdf(_pdf())
    assert "141.480" in texto
    assert "3 a cada 10" in texto


def test_pdf_nunca_escreve_lucro() -> None:
    """P12 / §6.1.9 — inclusive no PDF."""
    texto = _texto_do_pdf(_pdf()).lower()
    assert "lucro" not in texto
    assert "margem de contribui" in texto


def test_pdf_marca_dagua_quando_inclui_custo() -> None:
    """O custo de aquisicao E o preco de venda da Suicatech (plano §6.3)."""
    texto = _texto_do_pdf(_pdf())
    assert "DOCUMENTO INTERNO" in texto, (
        "o PDF com custo precisa sair marcado como interno"
    )


def test_pdf_sem_custo_nao_leva_marca_dagua() -> None:
    """Sem NENHUM custo o documento pode circular — inclusive o da original,
    que tambem e informacao de negociacao."""
    entradas = replace(
        entradas_do_caso("T1"),
        custo_dianteiro=None,
        custo_traseiro=None,
        custo_original=None,
    )
    # Sem custo o calculo entra em E1b, mas o documento ainda e gerado.
    texto = _texto_do_pdf(gerar_pdf(entradas, calcular(entradas)))
    assert "DOCUMENTO INTERNO" not in texto


def test_pdf_declara_as_decisoes_em_aberto() -> None:
    """Um PDF que sai da sala sem dizer o que nao foi decidido e pior que a
    tela, porque ninguem esta ao lado para explicar."""
    texto = _texto_do_pdf(_pdf())
    assert "ainda n" in texto  # "ainda nao considera"
    assert "rampa" in texto.lower()


def test_pdf_rotulo_do_anual_descreve_a_conta() -> None:
    texto = _texto_do_pdf(_pdf())
    assert "ano cheio em regime" in texto
    assert "primeiros 12 meses" not in texto


def test_pdf_cashback_declara_quem_paga_e_nao_desconta() -> None:
    entradas = replace(
        entradas_do_caso("T1"),
        cashback_dianteiro=(10.0, 3.0, 2.0),
        cashback_traseiro=(4.0, 1.5, 1.0),
    )
    resultado = calcular(entradas)
    texto = _texto_do_pdf(gerar_pdf(entradas, resultado))

    assert "pago pela Suicatech" in texto
    # O rateio por destinatario vai impresso.
    for nome in ("Consultor", "Gerente", "Marketing"):
        assert nome in texto, nome
    # O valor do resultado NAO muda.
    assert "141.480" in texto
    assert resultado.incremental_mensal == pytest.approx(11790.0, abs=0.005)


def test_pdf_declara_que_nao_ha_canibalizacao() -> None:
    """A premissa mais favoravel vai IMPRESSA: o documento sai da sala e
    ninguem estara ao lado para explicar."""
    texto = _texto_do_pdf(_pdf())
    assert "Canibaliza" in texto
    assert "venda nova" in texto


def test_pdf_faturamento_e_margem_abrem_o_documento() -> None:
    """D26 — a ordem de leitura do documento, INVERTIDA a pedido do cliente.

    SUBSTITUI `test_pdf_traducao_vem_antes_do_anual`, que exigia o contrario:
    `texto.index("3 a cada 10") < texto.index("141.480")`, por §5.5 e P2 — "R$
    141.480 por ano" e rejeitado pelo cerebro antes de ser avaliado, enquanto
    "3 a cada 10 carros que entram" e conferido pela intuicao em dois segundos.

    O cliente pediu em 27/08/2026 que faturamento e margem adicional abrissem o
    PDF, lado a lado e no maior corpo da folha. A tela ja tinha invertido isso
    em D21; o documento era o ultimo lugar onde a ordem original sobrevivia.

    O que este teste trava no lugar:
      1. os DOIS numeros abrem o documento, e nessa ordem — faturamento antes
         de margem, a mesma dos cartoes da tela (D21, normativa)
      2. a traducao CONTINUA no documento. Ela desceu de posicao, nao saiu: o
         PDF e o unico lugar em que ela ainda existe
      3. cada um dos dois diz QUAL CONTA ele e (§4). Dois numeros do mesmo
         tamanho lado a lado sem rotulo proprio seriam intercambiaveis
    """
    texto = _texto_do_pdf(_pdf())

    fim_da_manchete = texto.index("141.480")
    assert texto.index("249.372") < fim_da_manchete, (
        "faturamento adicional abre o documento, antes da margem"
    )
    assert fim_da_manchete < texto.index("3 a cada 10"), (
        "a tradução desceu para os cartões de apoio (D26)"
    )

    # A tradução continua no documento — inteira, não só a forma curta.
    assert "3 a cada 10" in texto
    assert "carros que entram" in texto

    # E cada número da manchete nomeia a conta que ele é — em versalete, que é
    # como o rótulo é desenhado.
    assert texto.index("FATURAMENTO ADICIONAL") < texto.index("249.372")
    assert (
        texto.index("249.372")
        < texto.index("MARGEM DE CONTRIBUIÇÃO ADICIONAL")
        < fim_da_manchete
    )


def test_pdf_com_nome_do_cliente() -> None:
    texto = _texto_do_pdf(_pdf(cliente="Concessionária Exemplo"))
    assert "Concession" in texto


# ---------------------------------------------------------------------------
# D24 — o documento visual
# ---------------------------------------------------------------------------


def test_pdf_duas_paginas_com_resultado_e_uma_sem() -> None:
    """As duas paginas tem papeis distintos, e a primeira so existe com numero.

    Pagina 1 e a leitura de relance; pagina 2 e a auditoria. Sem valor anual
    nao ha o que ler de relance — o documento abre dizendo o que falta, e nao
    com uma pagina de cartoes vazios.
    """
    assert _paginas(_pdf("T1")) == 2

    entradas = entradas_do_caso("T5")  # sem passagens: estado E1
    assert _paginas(gerar_pdf(entradas, calcular(entradas))) == 1


def test_pdf_traz_os_tres_cenarios_medidos() -> None:
    """D24 — E O PESSIMISTA ENTRA.

    Um documento que mostrasse so o cenario favoravel seria material de venda.
    A faixa inteira e o que deixa o gerente escolher em qual acreditar, e a
    procedencia medida (§5.3) e o que sustenta os tres.

    Os valores sao os do MESMO preco, MESMO custo e MESMA operacao — so o par
    de aproveitamento muda, como os botoes de cenario da tela fazem.
    """
    texto = _texto_do_pdf(_pdf("T1"))

    for preset in P.PRESETS:
        assert preset.rotulo in texto, preset.rotulo

    # T1 e 300 passagens, 1 ponto: 10% -> R$ 50.400; 40% -> R$ 182.160;
    # 70% -> R$ 319.752, com o traseiro seguindo o par de cada preset.
    for valor in ("50.400", "182.160", "319.752"):
        assert valor in texto, valor

    # E a procedencia medida vai junto, com a palavra "estimativa" NEGADA —
    # nunca afirmada ao lado de um numero de carteira (§4).
    assert "não é estimativa" in texto


def test_pdf_mark_up_em_percentual_e_a_nova_margem_nomeada() -> None:
    """D27 — as duas trocas de rótulo pedidas em 27/08/2026.

    O mark up saiu de "2,1×" para "108%", e o cartão do contraste mensal saiu de
    "Margem com palhetas, por mês" para "Nova margem com refil". Os dois cartões
    vivem lado a lado na linha de apoio da página 1, e os dois têm de dizer o
    que são: um percentual sem a conta embaixo lê como margem, e um valor em R$
    sem "nova" não se distingue do valor de hoje, que está na linha abaixo dele.
    """
    texto = _texto_do_pdf(_pdf("T1"))

    assert "108%" in texto
    assert "2,1×" not in texto, "o mark up deixou de ser múltiplo em D27"
    assert "(faturamento - custo) ÷ custo" in texto, (
        "o cartão precisa nomear a conta — o travessão vira hífen em Latin-1"
    )

    assert "NOVA MARGEM COM REFIL" in texto
    assert "MARGEM COM PALHETAS" not in texto
    # E o período não se perdeu ao sair do rótulo: ele desceu para o apoio,
    # junto do valor de hoje. Um valor mensal lido como anual erra por 12×.
    assert "por mês · hoje R$ 3.780" in texto


def test_pdf_cenarios_nao_prometem() -> None:
    """§4 / §12 no documento inteiro, agora que ele tem cara de material.

    "Bata o olho e fique evidente que e um bom negocio" foi atendido pelo
    DESENHO. Nenhum adjetivo entrou junto.
    """
    texto = _texto_do_pdf(_pdf("T1")).lower()
    for proibida in ("roi", "garantid", "grátis", "imperdív", "lucro"):
        assert proibida not in texto, proibida


def test_pdf_marca_dagua_em_TODAS_as_paginas() -> None:
    """A pagina 2 e a que carrega preco e custo de tabela.

    Antes de D24 o documento tinha uma pagina so e a marca-d'agua era desenhada
    uma vez, depois do `add_page`. Com duas paginas isso deixaria a SEGUNDA
    limpa — justamente a que tem o custo de aquisicao, que e o preco de venda
    da Suicatech (plano §6.3). Ela passou para o `header`, que roda em toda
    pagina.

    Duas ocorrencias por pagina: a marca-d'agua e o rodape.
    """
    dados = _pdf("T1")
    texto = _texto_do_pdf(dados)
    assert _paginas(dados) == 2
    assert texto.count("DOCUMENTO INTERNO") == 4, (
        "a marca-d'água e o rodapé precisam aparecer nas duas páginas"
    )


def test_pdf_transcreve_o_travessao_em_vez_de_apagar() -> None:
    """O titulo do proprio documento tinha um buraco no lugar do travessao.

    Latin-1 nao tem "—", e o `NFKD` + `ignore` anterior o APAGAVA: saia
    "Simulação de viabilidade  refil de palhetas", com dois espaços. Nenhum
    teste pegava, porque a busca era por trechos curtos.
    """
    from src.componentes.pdf_visual import texto as transcrever

    assert transcrever("a — b") == "a - b"
    assert transcrever("hoje → amanhã") == "hoje -> amanhã"
    assert transcrever("−R$ 10") == "-R$ 10"
    # O que JA cabia em Latin-1 nao pode ser tocado.
    assert transcrever("Simulação · 90 pares × R$ 197,90 ÷ custo") == (
        "Simulação · 90 pares × R$ 197,90 ÷ custo"
    )

    texto = _texto_do_pdf(_pdf("T1"))
    assert "Simulação de viabilidade - refil de palhetas" in texto
    assert "viabilidade  refil" not in texto, "o travessão virou buraco"


def test_pdf_valor_longo_nao_e_cortado() -> None:
    """`linha` quebra o valor. Era um `cell` de largura 0, que corta.

    A decisao G saia "bloco de investimento ausent" — e ela e uma das que a
    §5.12 manda imprimir justamente porque ninguem estara ao lado da folha
    para completar a frase.
    """
    texto = _texto_do_pdf(_pdf("T1"))
    assert "investimento ausente" in texto


def test_pdf_eixo_da_curva_sempre_tem_escala() -> None:
    """Um tick sozinho nao e regua — e um numero solto ao lado de uma linha.

    A primeira versao do calculo de ticks derivava o passo da largura do
    intervalo e arredondava para cima, o que pode DOBRAR o passo: numa faixa de
    R$ 45 mil a R$ 390 mil ela produzia um unico tick.
    """
    from src.componentes.pdf_visual import ticks_de_eixo

    faixas = [
        (45_360, 390_240),
        (0, 141_480),
        (19_440, 344_880),
        (-36_828, 120_000),
        (1_000, 1_200),
        (362_880, 8_036_928),
    ]
    for piso, teto in faixas:
        ticks = ticks_de_eixo(piso, teto)
        assert len(ticks) >= 2, f"{piso}..{teto} produziu {ticks}"
        assert all(piso <= v <= teto for v in ticks), f"{piso}..{teto}: {ticks}"
        assert ticks == sorted(ticks)


def test_pdf_rotulos_do_eixo_nunca_se_repetem() -> None:
    """Tres ticks lendo "R$ 1 mil" em alturas diferentes se contradizem.

    `moeda_curta` arredonda por construcao; numa faixa estreita ela colapsa, e
    o eixo cai para o numero inteiro.
    """
    from src.componentes.exportador_pdf import _ticks_do_eixo

    for piso, teto in ((1_000, 1_200), (45_360, 390_240), (0, 141_480)):
        rotulos = [rotulo for _, rotulo in _ticks_do_eixo(piso, teto)]
        assert len(set(rotulos)) == len(rotulos), f"{piso}..{teto}: {rotulos}"


def test_pdf_nenhum_numero_de_resultado_em_vermelho() -> None:
    """§13.1 — "numero financeiro em vermelho le como prejuizo".

    Checagem ESTRUTURAL, e nao por texto: o vermelho da marca e legitimo neste
    modulo (o segmento de barra, o marcador da curva, a anotacao do vao), e uma
    busca no arquivo inteiro acusaria esses usos. O que nao pode e o cartao de
    KPI e a tira de cenario pintarem o VALOR de vermelho — e e isso que a
    §13.1 protege, porque ali mora o numero que o cliente le como resultado.
    """
    import ast

    from testes.checagens import RAIZ

    fonte = (RAIZ / "src" / "componentes" / "pdf_visual.py").read_text(
        encoding="utf-8"
    )
    arvore = ast.parse(fonte)

    for no in ast.walk(arvore):
        if not isinstance(no, ast.FunctionDef) or no.name != "kpi":
            continue
        corpo = ast.get_source_segment(fonte, no) or ""
        assert "MARCA_VERMELHO" not in corpo, (
            "o cartão de KPI não pode pintar nada de vermelho: é onde mora o "
            "número que o cliente lê como resultado (§13.1)"
        )
        return
    raise AssertionError("pdf_visual.kpi não encontrado")


def test_pdf_incremental_negativo_sai_com_sinal_e_sem_promessa() -> None:
    """T3 no documento: a margem pode ser negativa, e o plano §1.1 avisa disso.

    O documento nao esconde e tambem nao pinta de vermelho. O rotulo do vao nao
    leva "+" — senao sairia "+ -R$ 36.828".
    """
    entradas = replace(entradas_do_caso("T1"), custo_dianteiro=250.0)
    resultado = calcular(entradas)
    assert resultado.anual is not None and resultado.anual < 0

    texto = _texto_do_pdf(gerar_pdf(entradas, resultado))
    assert "36.828" in texto
    assert "+ -R$" not in texto and "+ −R$" not in texto
    # E o desenho explica o vao em palavras, sem vocabulario de alerta (§4).
    assert "vão tracejado" in texto
    for proibida in ("inválido", "atenção", "cuidado", "erro"):
        assert proibida not in texto.lower(), proibida


def test_pdf_nome_do_arquivo_sem_cliente() -> None:
    """Sem cliente o nome nao leva traco solto no meio."""
    from datetime import date

    assert nome_do_arquivo("", date(2026, 8, 27)) == (
        "simulacao-refil-2026-08-27.pdf"
    )
    assert nome_do_arquivo("   ", date(2026, 8, 27)) == (
        "simulacao-refil-2026-08-27.pdf"
    )


def test_pdf_nome_do_arquivo_sobrevive_a_qualquer_nome_de_cliente() -> None:
    """D23 — o PDF SAI DA SALA, e o nome dele vai junto.

    A versao anterior fazia `c if c.isalnum() else "-"` sobre o nome em
    minusculas e deixava passar duas coisas:

      - ACENTO. `"á".isalnum()` e True em Python, e o nome saia acentuado. O
        Windows aceita; um anexo passando por servidor antigo, nem sempre
      - TRACO REPETIDO. "Auto Center — Zona Sul" virava
        `auto-center-----zona-sul`
    """
    from datetime import date

    dia = date(2026, 8, 27)

    assert nome_do_arquivo("Concessionária Guaíba", dia) == (
        "simulacao-refil-concessionaria-guaiba-2026-08-27.pdf"
    )
    assert nome_do_arquivo("Auto Center — Zona Sul", dia) == (
        "simulacao-refil-auto-center-zona-sul-2026-08-27.pdf"
    )
    # Pontuacao no fim nao vira traco solto antes da data.
    assert nome_do_arquivo("Veículos Ipiranga LTDA.", dia) == (
        "simulacao-refil-veiculos-ipiranga-ltda-2026-08-27.pdf"
    )

    for cliente in (
        "Ação & Cia / Filial 2",
        "  ---  ",
        "São João",
        "R$ Motors",
        "\\..\\etc",
    ):
        nome = nome_do_arquivo(cliente, dia)
        assert nome.isascii(), f"{cliente!r} -> {nome!r}"
        assert nome.endswith("-2026-08-27.pdf"), nome
        assert "--" not in nome, nome
        # Nada que um sistema de arquivos leia como caminho.
        for proibido in ("/", "\\", ":", "..", " "):
            assert proibido not in nome, f"{cliente!r} -> {nome!r}"


def test_pdf_sem_ancora_nao_inventa_valor() -> None:
    """E1 no documento: nenhum valor anual, e a explicacao do porque."""
    entradas = entradas_do_caso("T5")
    texto = _texto_do_pdf(gerar_pdf(entradas, calcular(entradas)))
    assert "141.480" not in texto
    assert "0,00" not in texto
    assert "margem de contribui" in texto.lower()

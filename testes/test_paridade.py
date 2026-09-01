"""A TELA E O PDF MOSTRAM A MESMA COISA. D28.

Pedido do cliente em 27/08/2026: *"a tela de resultados deve ser exatamente
igual o que aparece no PDF. Com todos os graficos, tabelas e KPIs."*

"Exatamente igual" so e verificavel se houver um lugar so decidindo o que
aparece. Esse lugar e `src/apresentacao.py`, e este arquivo e a rede que pega
quem desenhar um lado sem desenhar o outro:

    montar()  ->  bloco_resultado (HTML)   <- os dois tem de mostrar
              ->  exportador_pdf (vetor)      TUDO que a montagem produziu

O que NAO e comparado, e por que:

  - a GEOMETRIA. Milimetro no papel e pixel na tela nao se comparam, e nem
    deveriam: o A4 tem 190 mm de largura fixa e a tela tem a largura que o
    navegador der
  - o GEMEO EM TABELA da curva, o painel de formula e a area de exportacao.
    Sao as tres pecas que a tela tem A MAIS. O gemeo e obrigatorio pela §5.11
    e pela §9 (substitui o tooltip, que nao existe em tablet e muito menos no
    papel); os outros dois sao ferramenta de operacao, nao resultado
  - o cabecalho, o rodape e a marca-d'agua do PDF, que sao do DOCUMENTO
"""

from __future__ import annotations

import re
from dataclasses import replace

from src import apresentacao
from src.calculo import calcular
from src.componentes.exportador_pdf import gerar_pdf
from testes.conftest import entradas_do_caso
from testes.test_pdf import _texto_do_pdf

# Os casos que exercitam os quatro caminhos do resultado.
_CASOS = {
    "completo": lambda: entradas_do_caso("T1"),
    "com cashback": lambda: replace(
        entradas_do_caso("T1"),
        cashback_dianteiro=(10.0, 3.0, 2.0),
        cashback_traseiro=(4.0, 1.5, 1.0),
    ),
    "margem negativa": lambda: replace(
        entradas_do_caso("T1"), custo_dianteiro=250.0
    ),
    "sem custo da original": lambda: replace(
        entradas_do_caso("T1"), custo_original=None
    ),
}


def _textos_da_montagem(a: apresentacao.Apresentacao) -> list[str]:
    """Todo texto que a montagem manda desenhar, em ordem.

    A traducao inteira fica de fora porque nenhuma das duas superficies a
    imprime junta: as duas mostram a forma curta no lugar do numero e a frase
    no apoio do cartao — o que ja e comparado pelo cartao.
    """
    partes: list[str] = []

    if a.manchete is not None:
        for cartao in a.manchete:
            partes += [cartao.rotulo, cartao.valor or "", cartao.apoio]
        partes.append(a.nota_do_grupo)

    for cartao in a.apoio:
        partes += [cartao.rotulo, cartao.valor or "", cartao.apoio]

    if a.barras is not None:
        partes += [
            a.titulo_barras,
            a.barras.rotulo_hoje,
            a.barras.rotulo_refil,
            a.barras.rotulo_incremental,
            a.barras.nome_hoje,
            a.barras.nome_refil,
            a.barras.nota,
        ]

    if a.cenarios:
        partes.append(a.titulo_cenarios)
        for cenario in a.cenarios:
            partes += [
                cenario.rotulo,
                cenario.aproveitamento,
                cenario.valor,
                cenario.apoio,
            ]
        partes.append(a.nota_cenarios)

    if a.cashback is not None:
        partes += [a.cashback.total, a.cashback.nota, a.cashback.rateio]

    if a.curva is not None:
        partes += [a.titulo_curva, a.curva.subtitulo, a.curva.frase]

    for secao in (a.premissas, a.preco_custo, a.decisoes):
        if secao is None:
            continue
        partes += [secao.titulo, secao.nota]
        for rotulo, valor in secao.linhas:
            partes += [rotulo, valor]

    if a.incompleto:
        partes.append(a.incompleto)

    return [p for p in partes if p]


def _normalizar(texto: str) -> str:
    """Tira o que so o MEIO decide: espaco, caixa e o que Latin-1 transcreve.

    O PDF escreve `-` onde a tela escreve `—`, porque a fonte nucleo do fpdf2 e
    Latin-1 (a tabela de transcricao vive em `pdf_visual`). Comparar sem
    normalizar acusaria uma divergencia que e do MEIO, e nao do conteudo.
    """
    for de, para in (
        ("—", "-"),
        ("–", "-"),
        ("−", "-"),
        ("→", "->"),
        (" ", " "),
    ):
        texto = texto.replace(de, para)
    return re.sub(r"\s+", " ", texto).lower()


def _texto_da_tela(a: apresentacao.Apresentacao) -> str:
    """O HTML que a tela desenha, sem as tags.

    Chama os desenhadores com um `st` de mentira — nao sobe o app. O que
    interessa aqui e o texto que sai do desenho da TELA, e nao o do modelo:
    comparar o modelo consigo mesmo nao provaria nada.
    """
    from src.componentes import bloco_resultado

    capturado: list[str] = []

    original = bloco_resultado._md
    bloco_resultado._md = capturado.append  # type: ignore[assignment]
    try:
        if a.manchete is not None:
            bloco_resultado._manchete(a)
            for cartao in a.apoio:
                capturado.append(bloco_resultado._cartao(cartao))
            bloco_resultado._barras(a)
            bloco_resultado._cenarios(a)
            bloco_resultado._cashback(a)
        else:
            bloco_resultado._incompleto(a)
        bloco_resultado.titulo_da_curva(a)
        bloco_resultado.frase_da_curva(a)
        bloco_resultado.secoes(a)
    finally:
        bloco_resultado._md = original  # type: ignore[assignment]

    return _normalizar(re.sub(r"<[^>]+>", " ", " ".join(capturado)))


def test_paridade_tela_e_pdf() -> None:
    """Tudo que a montagem produz aparece NOS DOIS desenhos.

    Este e o teste que da sentido a "exatamente igual": sem ele, acrescentar um
    bloco ao PDF e esquecer da tela (ou o contrario) passa despercebido — foi
    exatamente o que aconteceu entre D24 e D28, quando o documento ganhou
    barras, cenarios e premissas e a tela ficou com tres cartoes.
    """
    for nome, montar_entradas in _CASOS.items():
        e = montar_entradas()
        r = calcular(e)
        a = apresentacao.montar(e, r)

        na_tela = _texto_da_tela(a)
        no_papel = _normalizar(_texto_do_pdf(gerar_pdf(e, r)))

        for parte in _textos_da_montagem(a):
            alvo = _normalizar(parte)
            assert alvo in na_tela, f"[{nome}] falta na TELA: {parte!r}"
            assert alvo in no_papel, f"[{nome}] falta no PDF: {parte!r}"


def test_paridade_cobre_os_blocos_que_importam() -> None:
    """A rede so vale se o caso base exercitar todos os blocos.

    Sem esta checagem, `test_paridade_tela_e_pdf` continuaria verde se a
    montagem parasse de produzir barras, cenarios ou premissas — ele compara o
    que existe, e o que nao existe nao e comparado.
    """
    e = entradas_do_caso("T1")
    a = apresentacao.montar(e, calcular(e))

    assert a.manchete is not None and len(a.manchete) == 2
    assert len(a.apoio) == 3
    assert a.barras is not None
    assert len(a.cenarios) == 3, "os três cenários medidos, o pessimista junto"
    assert a.curva is not None and a.curva.pontos
    assert a.premissas is not None and a.premissas.linhas
    assert a.preco_custo is not None and a.preco_custo.linhas
    assert a.decisoes is not None and a.decisoes.linhas

    # E a montagem inteira tem de gerar texto suficiente para a comparacao
    # significar alguma coisa.
    assert len(_textos_da_montagem(a)) > 40


def test_paridade_no_estado_incompleto() -> None:
    """Sem valor anual as duas superficies dizem a MESMA coisa que falta.

    P9 / §6.1.6: nenhum valor e exibido no lugar, nas duas.
    """
    e = entradas_do_caso("T5")
    r = calcular(e)
    a = apresentacao.montar(e, r)

    assert a.manchete is None
    assert a.incompleto

    na_tela = _texto_da_tela(a)
    no_papel = _normalizar(_texto_do_pdf(gerar_pdf(e, r)))
    alvo = _normalizar(a.incompleto)

    assert alvo in na_tela
    assert alvo in no_papel

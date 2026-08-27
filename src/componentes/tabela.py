"""Tabela propria — o gemeo em tabela (§5.11), desenhado. Acrescimo D20.

POR QUE NAO `st.dataframe`: ele desenha numa `<canvas>`. Nenhuma regra da
camada B pega nele, e o resultado era que as duas tabelas do app (a curva na
Tela 1 e os modelos na Tela 2) eram os unicos objetos da tela fora da
linguagem visual do resto: cabecalho, tipografia, alinhamento e cantos do
framework, no meio de cartoes proprios.

O que se GANHA com uma `<table>` de verdade:

  - ela obedece a folha da camada B como qualquer outro elemento — cabecalho
    grudado, filete de 1px por linha, numero alinhado a direita com digito de
    largura fixa (§15.1 de css.py)
  - MARCADOR DA POSICAO ATUAL. A §5.11 pede que o gemeo mostre as mesmas
    series do grafico; o grafico tem um marcador vermelho na posicao corrente
    e a tabela nao tinha nada equivalente. Agora tem: `destaque`
  - e texto de verdade. Leitor de tela le celula por celula com o cabecalho
    associado (`scope="col"`), o cliente seleciona e copia, e o conteudo
    sobrevive ao print e ao PDF do navegador — nenhuma das tres coisas
    acontece com uma canvas

O que se PERDE: ordenacao por clique e redimensionamento de coluna do
`st.dataframe`. Nenhuma das duas era usada — as duas tabelas do app sao
curtas e ja saem ordenadas pela grandeza que interessa (aproveitamento
crescente, posicao no ranking).

TODO texto passa por `html.escape`. As celulas da Tela 2 vem do snapshot
publicado — nome de modelo e dado de fora, e dado de fora nunca entra em
markup sem escapar.

O VALOR ENTRA JA FORMATADO, como texto (convencao do projeto): o pt-BR nao
depende de configuracao do navegador, e o componente nao decide casas
decimais nem separador de milhar de ninguem.
"""

from __future__ import annotations

import html
from collections.abc import Collection, Sequence

import streamlit as st


def tabela(
    *,
    colunas: Sequence[str],
    linhas: Sequence[Sequence[str]],
    numericas: Collection[int] = (),
    destaque: int | None = None,
) -> None:
    """Desenha a tabela. Nada e desenhado sem coluna ou sem linha.

    colunas    titulos, na ordem
    linhas     uma sequencia de celulas JA FORMATADAS por linha
    numericas  indices das colunas alinhadas a direita (as de numero)
    destaque   indice da linha marcada como posicao atual, se houver
    """
    if not colunas or not linhas:
        return

    direita = set(numericas)

    cabecalho = "".join(
        f'<th{_alinhamento(indice in direita)} scope="col">'
        f"{html.escape(str(titulo))}</th>"
        for indice, titulo in enumerate(colunas)
    )

    corpo: list[str] = []
    for numero, linha in enumerate(linhas):
        marca = ' class="st-tabela-atual"' if numero == destaque else ""
        celulas = "".join(
            f"<td{_alinhamento(indice in direita)}>{html.escape(str(celula))}</td>"
            for indice, celula in enumerate(linha)
        )
        corpo.append(f"<tr{marca}>{celulas}</tr>")

    # Uma linha unica de HTML, sem quebra em branco no meio: o markdown do
    # Streamlit trata linha vazia como fim de bloco e cortaria a tabela ao
    # meio, transformando o resto em texto solto.
    st.markdown(
        '<div class="st-tabela"><table>'
        f"<thead><tr>{cabecalho}</tr></thead>"
        f'<tbody>{"".join(corpo)}</tbody>'
        "</table></div>",
        unsafe_allow_html=True,
    )


def _alinhamento(numerica: bool) -> str:
    return ' class="st-tabela-num"' if numerica else ""

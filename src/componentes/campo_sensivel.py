"""§5.2 — Campo sensivel (preco e custo). E §5.13 — regra de unidade.

"O custo de aquisicao da concessionaria E o preco de venda da Suicatech. Numa
tela de link aberto, um default e tabela de preco exposta (plano §6.3)."

A legenda fica SOB O BLOCO INTEIRO de preco e custo, nao sob cada campo:

    Preco ao consumidor final, por par (dianteiro)
    [                    ]        <- vazio, sempre
    Custo de aquisicao, por par (dianteiro)
    [                    ]        <- vazio, sempre
    Preco e custo sao negociados caso a caso.     <- t-derivado
    Abrem em branco de proposito.

REGRAS (§5.2):
  - value=None. NUNCA um numero, nunca um placeholder numerico que pareca valor
  - a legenda existe para o campo vazio NAO PARECER ESQUECIDO. Sem ela, um
    vendedor novo preenche com o valor da ultima reuniao, ou o cliente pergunta
    se o app esta quebrado
  - ⚠️ NAO implemente validacao de piso de preco. A decisao F esta em aberto
    (§10-F). Nao invente um piso

REGRA DE UNIDADE (§5.13) — a mais critica desta tela:
  E PROIBIDO derivar o preco ou o custo do traseiro a partir do dianteiro por
  qualquer fator, INCLUSIVE / 2. Nao e arredondamento, e erro de fato. O par
  dianteiro tem duas medidas diferentes (motorista e passageiro); o traseiro e
  lamina unica.

  Este modulo NAO contem nenhuma expressao relacionando preco_traseiro a
  preco_dianteiro. testes/test_checklist.py verifica isso por AST em todo o
  src/, nao apenas aqui.
"""

from __future__ import annotations

import streamlit as st

from src import parametros as P
from src.componentes.campo_unidade import campo_moeda

LEGENDA_BLOCO = (
    "Preço e custo são negociados caso a caso. Abrem em branco de propósito."
)


def bloco_preco_custo(
    *,
    categoria_nome: str,
    chave_preco: str,
    chave_custo: str,
) -> tuple[float | None, float | None]:
    """Renderiza preco + custo de UMA categoria, com a unidade no rotulo.

    A unidade vem de `parametros.CATEGORIAS[].rotulo_unidade` — ATRIBUTO
    DECLARADO por categoria (§5.13, V3), nunca constante global e nunca
    inferida do nome. V3 aborta o app se estiver ausente.
    """
    categoria = P.categoria_por_nome(categoria_nome)
    if categoria is None:  # pragma: no cover — V3 ja teria abortado o app
        return None, None

    unidade = categoria.rotulo_unidade

    preco = campo_moeda(
        chave=chave_preco,
        rotulo=f"Preço ao consumidor final, {unidade}",
    )
    custo = campo_moeda(
        chave=chave_custo,
        rotulo=f"Custo de aquisição, {unidade}",
    )

    st.markdown(
        f'<p class="st-legenda-bloco">{LEGENDA_BLOCO}</p>',
        unsafe_allow_html=True,
    )

    return preco, custo

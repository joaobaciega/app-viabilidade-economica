"""§5.3 — Botao de cenario. O PROTAGONISTA.

"E o momento em que o cliente age. Tres botoes grandes, uma ida ao servidor
cada, resposta decisiva, IMUNES A LATENCIA."

Isso substitui a ideia original de slider em tempo real, que nao e
reproduzivel em Streamlit (plano §3.7 e §6.2). E a substituicao e MELHOR que a
original: os presets vem de carteira real de 15+ concessionarias, e apertar
"REALISTA" e invocar um dado. Arrastar ate o mesmo numero e so mexer num
controle.

    ┌────────────┐ ┌────────────┐ ┌────────────┐
    │ PESSIMISTA │ │  REALISTA  │ │  OTIMISTA  │   <- t-preset-nome 22/700
    │    20%     │ │    30%     │ │    40%     │   <- t-preset-valor 32/700
    └────────────┘ └────────────┘ └────────────┘
       96px de altura, largura total da coluna
    Aproveitamento dianteiro medido em 15+ concessionarias
    da carteira Suicatech — nao e estimativa            <- t-derivado

REGRAS (§5.3):
  - O ESTADO ATIVO E DERIVADO, NAO GUARDADO. Um preset esta ativo se e somente
    se (conv_dianteiro, conv_traseiro) for exatamente igual ao par daquele
    preset. Isso torna IMPOSSIVEL a tela mostrar "REALISTA" aceso com o slider
    em 27%
  - cada botao escreve OS DOIS valores via on_click. Escrever a chave de um
    widget depois que ele foi instanciado levanta StreamlitAPIException
  - os tres botoes ficam ACIMA do bloco de resultado, dentro da coluna do
    cliente. O controle que muda o numero esta imediatamente acima do numero
    que ele muda, ao alcance de quem estiver do outro lado da mesa
  - a legenda de procedencia e ARGUMENTO COMERCIAL, nao nota de rodape. Fica em
    15px, sempre visivel. A palavra "estimativa" e PROIBIDA aqui (§4)

O estado ativo usa type="primary" — NATIVO, nao CSS. Se toda a camada B
quebrar, os botoes continuam funcionando e continuam mostrando o cenario
ativo. So o tamanho degrada (§3, camada A).
"""

from __future__ import annotations

import streamlit as st

from src import parametros as P
from src.calculo import Entradas, preset_ativo
from src.estado import aplicar_preset


# O CSS de 96px de altura pende deste seletor. `st.container(key=...)` gera a
# classe `st-key-cenarios` NO ELEMENTO QUE ENVOLVE os filhos — API publica.
#
# NAO troque por st.markdown('<div class="st-cenarios">'): um markdown injetado
# abre e FECHA a propria div, e as colunas seguintes nao ficam dentro dela.
# O seletor nunca casa, os botoes voltam a ~52px e o protagonista da tela deixa
# de ser o protagonista — foi exatamente o que aconteceu na primeira versao,
# e so apareceu na captura de tela.
CHAVE_CONTAINER = "cenarios"


def botoes(e: Entradas) -> None:
    ativo = preset_ativo(e)  # derivado a cada rerun, nunca lido de um flag

    with st.container(key=CHAVE_CONTAINER):
        colunas = st.columns(len(P.PRESETS), gap="small")
        for coluna, preset in zip(colunas, P.PRESETS):
            with coluna:
                st.button(
                    f"{preset.rotulo}\n\n{int(round(preset.dianteiro * 100))}%",
                    key=f"btn_preset_{preset.nome}",
                    type="primary" if preset.nome == ativo else "secondary",
                    width="stretch",
                    on_click=aplicar_preset,
                    args=(preset.nome,),
                )

    st.caption(P.LEGENDA_PRESETS_DIANTEIRO)

"""§5.9 — Faixa do vendedor. O canal de aviso discreto.

"A tela precisa poder discordar do usuario sem constranger ninguem. Se o
vendedor digitar numeros que produzem um cenario implausivel, o app avisa —
mas O CLIENTE ESTA OLHANDO, e um alerta vermelho transforma um ajuste tecnico
em VEXAME PUBLICO."

Fica no RODAPE: a borda mais proxima de quem segura o aparelho e a mais
escorcada para quem esta do outro lado da mesa. 12px, --tinta-discreta, sem
caixa, sem borda, sem icone, sem cor.

A 1 metro, 12px subtende ~4,8px de leitura normal — ABAIXO DO LIMIAR DE
LEITURA. E o mecanismo do canal privado, nao um descuido (§3.2).

REGRAS ABSOLUTAS (§5.9):
  - st.warning, st.error, st.exception, st.toast e st.balloons sao PROIBIDOS em
    qualquer ponto da area visivel ao cliente. Verificacao:
    grep -rn "st\\.warning\\|st\\.error\\|st\\.exception\\|st\\.toast\\|st\\.balloons" src/
    retorna vazio. testes/test_checklist.py garante isso
  - o texto DESCREVE, NAO ACUSA. "carga de 34 veiculos por consultor por dia",
    nunca "valor invalido"
  - varios avisos viram LINHAS SEPARADAS na mesma faixa, na ordem das regras da
    §6.1.8. Nunca um contador, nunca um badge
  - a faixa NAO EMPURRA O LAYOUT quando aparece. Ela ocupa altura reservada
    (64px em css.py), vazia quando nao ha aviso

Se o CSS quebrar, o texto volta ao tamanho padrao de st.caption — ainda
discreto, ainda sem caixa, ainda cinza. Degradacao aceitavel.

`novo cliente` mora AQUI, nao na barra superior: na barra superior seria um
botao destrutivo na regiao mais visivel ao cliente, e a justificativa
geometrica desta secao existe exatamente para isso.
"""

from __future__ import annotations

import html

import streamlit as st

from src.estado import novo_cliente


def faixa(linhas: list[str], meta: list[str] | None = None) -> None:
    """Renderiza a faixa. Sempre presente, mesmo sem nenhuma linha.

    `linhas` sao os avisos de plausibilidade (R1-R5).
    `meta` sao informacoes de estado (versao do snapshot, etc).
    """
    marcado = "".join(
        f'<p class="st-fv-linha">{html.escape(linha)}</p>' for linha in linhas
    )
    if meta:
        marcado += (
            '<p class="st-fv-linha st-fv-meta">'
            + html.escape(" · ".join(meta))
            + "</p>"
        )

    st.markdown(
        f'<div class="st-faixa-vendedor">{marcado}</div>',
        unsafe_allow_html=True,
    )


CHAVE_CONTAINER_BOTAO = "faixa_novo_cliente"


def botao_novo_cliente() -> None:
    """`novo cliente` — limpa preco, custo e ancora SEM CONFIRMACAO.

    §5.2: "Precisa ser executavel entre uma visita e outra, no elevador."

    Fica DENTRO da faixa do vendedor, no rodape — nao na barra superior, onde
    seria um botao destrutivo na regiao mais visivel ao cliente.

    NOTA DE IMPLEMENTACAO: a faixa em si e um `<div>` injetado, e HTML injetado
    nao pode conter um widget do Streamlit. A solucao e renderizar o botao num
    `st.container(key=...)` — que gera a classe estavel `st-key-<key>` — e
    posiciona-lo por CSS dentro da zona da faixa. `st.container(key=)` e API
    publica, portanto este e o unico gancho de CSS do app que NAO depende de
    seletor interno: e o menos fragil da camada B.
    """
    with st.container(key=CHAVE_CONTAINER_BOTAO):
        st.button(
            "novo cliente",
            key="btn_novo_cliente",
            on_click=novo_cliente,
            help="Limpa preço, custo, âncora e deduções desta negociação.",
        )

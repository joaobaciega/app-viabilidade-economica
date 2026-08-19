"""Componentes +15 e +16 — CartaoComparativo e SeloProcedencia.

ACRESCIMOS DECLARADOS (docs/DIVERGENCIAS.md). O DESIGN v5 nao os especifica: a
§5 dele diz literalmente que componentes das Telas 2 e 3 "nao estao aqui". A
estrutura segue o plano §5.1 e §5.3, e e PROVISORIA ate o DESIGN ser regerado.

Regras que o cartao precisa obedecer (plano §5.1):
  - UNIDADE DECLARADA DOS DOIS LADOS (§2.7). Par contra par, ou unidade contra
    unidade. Se um lado for par e o outro unidade, o resultado ERRA POR 2x na
    tela cuja unica funcao e ser auditavel — e o app BLOQUEIA a comparacao em
    vez de converter
  - MEDIDA E ANO-MODELO VISIVEIS (§2.5), senao o cartao nao e auditavel
  - A RESSALVA SOBRE A ARMACAO — comparar palheta inteira com refil e comparar
    coisas diferentes, e e o mesmo vicio que derruba o 3,49x da §1.1. Declarar
    a condicao desarma a objecao antes dela chegar
  - A MARGEM DA CONCESSIONARIA NAO APARECE NO CARTAO. O custo dela e o preco de
    venda da Suicatech; esse numero so existe na Tela 1, depois de digitado

Selo de procedencia (plano §5.3): preco SEMPRE exibido, qualquer idade; data de
coleta SEMPRE visivel, colada ao preco, na mesma classe de leitura; aviso de
idade APENAS na faixa do vendedor. "Card bloqueado na frente do cliente e pior
que preco velho. Vendedor com tela vazia perdeu a cena; vendedor com numero
datado ainda negocia."

⚠️ Decisao L em aberto (§10-L): NENHUM limiar de idade. A faixa do vendedor
exibe a idade CRUA em dias. Nao invente 60 nem 180 — esse numero decide quando
o vendedor refaz a coleta, e ninguem o decidiu.
"""

from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from src import formato
from src.componentes.regra_unidade import unidades_sao_comparaveis

RESSALVA_ARMACAO = "Requer armação em bom estado"


def selo_procedencia(*, tipo_fonte: str, marca: str, data_coleta: str) -> str:
    """'coletado em 10/03/2026 · loja oficial VW' — colado ao preco.

    O rotulo de fonte segue a regra de fallback do plano §2.4, literalmente.
    """
    rotulos = {
        "loja_oficial_ml": f"loja oficial {marca} — Mercado Livre",
        "ecommerce_montadora": f"loja oficial {marca}",
        "indisponivel": "sem preço oficial publicado",
    }
    fonte = rotulos.get(tipo_fonte, "sem preço oficial publicado")
    return f"coletado em {data_coleta} · {fonte}"


def idade_em_dias(data_coleta: str) -> int | None:
    """Idade CRUA em dias, sem faixa de severidade (⚠️ L)."""
    try:
        coletado = datetime.strptime(data_coleta, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None
    return (date.today() - coletado).days


def cartao(registro: dict, preco_refil: float | None, unidade_refil: str) -> None:
    """Um cartao comparativo. Bloqueia a economia se as unidades divergirem."""
    marca = registro.get("marca", "")
    modelo = registro.get("modelo", "")
    anos = f"{registro.get('ano_ini', '')}–{registro.get('ano_fim', '')}"
    medida = registro.get("medida_mm", "")
    posicao = registro.get("posicao", "")
    unidade_original = registro.get("unidade", "")
    preco_original = registro.get("preco")

    with st.container(border=True):
        st.markdown(f"**{marca.upper()} {modelo.upper()}**  ·  {anos}")
        st.caption(f"{posicao} — {unidade_original} ({medida} mm)")

        if preco_original:
            st.markdown(
                f'<p class="st-anual">{formato.moeda_unitaria(preco_original)}'
                f' <span class="st-rotulo-resultado">{unidade_original}</span></p>',
                unsafe_allow_html=True,
            )
            st.caption(
                selo_procedencia(
                    tipo_fonte=registro.get("tipo_fonte", "indisponivel"),
                    marca=marca,
                    data_coleta=registro.get("data_coleta", ""),
                )
            )
        else:
            st.markdown("**sem preço oficial publicado**")
            st.caption(
                "Nunca preenchido com preço de vendedor terceiro. "
                "Uma linha inventada destrói as outras 200."
            )

        st.divider()

        if preco_refil is None:
            st.caption("Informe o preço do refil no cabeçalho da tela.")
            return

        st.markdown(f"Seu refil · {formato.moeda_unitaria(preco_refil)} {unidade_refil}")

        # BLOQUEIO em vez de conversao (plano §2.7).
        categoria_original = "dianteiro" if unidade_original == "par" else "traseiro"
        categoria_refil = "dianteiro" if unidade_refil == "par" else "traseiro"

        if not unidades_sao_comparaveis(categoria_original, categoria_refil):
            _comparacao_bloqueada(unidade_original, unidade_refil)
            return

        if preco_original:
            economia = preco_original - preco_refil
            base = economia / preco_original
            st.markdown(
                f"**Cliente economiza {formato.moeda_unitaria(economia)}**  \n"
                f"{formato.percentual(base, casas=1)} sobre "
                f"{formato.moeda_unitaria(preco_original)}"
            )

        st.caption(RESSALVA_ARMACAO)


def _comparacao_bloqueada(unidade_a: str, unidade_b: str) -> None:
    """Recusa tecnica CORRETA, nao defeito. Sem vermelho, sem tom de falha.

    Nunca existe um botao "converter mesmo assim". A acao oferecida e sempre
    completar o dado que falta, nunca aproximar.
    """
    st.markdown(
        "**Comparação não disponível**  \n"
        f"<span class='st-legenda-bloco'>A palheta original está em "
        f"<b>{unidade_a}</b> e o refil em <b>{unidade_b}</b>. "
        f"Somar ou dobrar daria um número errado.</span>",
        unsafe_allow_html=True,
    )

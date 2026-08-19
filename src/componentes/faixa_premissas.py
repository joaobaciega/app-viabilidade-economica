"""§5.6 — Faixa de premissas.

"Declarar, de forma PERMANENTEMENTE VISIVEL, o que a simulacao esta assumindo.
E o que separa premissa de fato sem ninguem precisar perguntar."

    dianteiro 30% ◆ carteira · traseiro 10% ◆ carteira · substituicao 0% ▪ premissa
    · rampa e sazonalidade ⚠️ nao aplicadas · ano cheio em regime

REGRAS (§5.6):
  - aparece SEMPRE, inclusive quando todos os valores sao o default. A hipotese
    favoravel precisa estar DITA NA TELA, nao escondida no default.
    Substituicao em 0% significa "o refil nao tira nenhuma venda da original" —
    e a premissa MAIS FAVORAVEL POSSIVEL, e o cliente tem que poder ve-la
  - cada item carrega o marcador de procedencia da §5.7
  - quando o aproveitamento nao corresponde a nenhum preset, o item le
    `dianteiro 27% ▪ ajustado na reuniao` — a procedencia MUDA JUNTO com o valor
  - quando um coeficiente e placeholder, o item carrega ⚠️ e o marcador da §5.12

§5.10: nada dentro de Ajustes avancados pode alterar o resultado sem que esta
faixa reflita a mudanca. "Uma alteracao escondida atras de um acordeao que muda
o numero da manchete sem deixar rastro e A PIOR FALHA POSSIVEL nesta tela."
"""

from __future__ import annotations

import streamlit as st

from src import formato
from src import parametros as P
from src.calculo import Entradas, Resultado, preset_ativo
from src.componentes import marcador_decisao_aberta as aberto
from src.componentes.marcador_procedencia import (
    LEGENDA_DERIVADO,
    de_origem,
    marcador,
)


def faixa(e: Entradas, r: Resultado) -> None:
    itens: list[str] = []
    ativo = preset_ativo(e)
    preset = P.preset_por_nome(ativo) if ativo else None

    # --- Aproveitamento dianteiro -----------------------------------------
    pct_d = formato.percentual(e.aproveitamento_dianteiro)
    if preset is not None:
        proc_d = de_origem(preset.origem_dianteiro)
    else:
        # A procedencia muda junto com o valor: um numero ajustado na reuniao
        # nao pode sair com a autoridade da carteira.
        proc_d = '<span class="st-proc">▪ ajustado na reunião</span>'
    itens.append(f"dianteiro <b>{pct_d}</b> {proc_d}")

    # --- Aproveitamento traseiro ------------------------------------------
    #
    # A distincao `◆ carteira` x `≈ derivado` aqui e a mitigacao do risco n. 1
    # do plano. So a linha realista do traseiro foi medida.
    if r.traseiro_na_conta:
        pct_t = formato.percentual(e.aproveitamento_traseiro)
        if preset is not None:
            proc_t = de_origem(preset.origem_traseiro)
            if preset.origem_traseiro == "derivado":
                proc_t += f' <span class="st-proc">({LEGENDA_DERIVADO})</span>'
        else:
            proc_t = '<span class="st-proc">▪ ajustado na reunião</span>'
        itens.append(f"traseiro <b>{pct_t}</b> {proc_t}")
    else:
        # §5.13: "Se o preco ou o custo do traseiro estiver vazio, o traseiro
        # contribui com R$ 0 e a faixa de premissas declara. Nunca estimado,
        # nunca inferido."
        itens.append("traseiro: preço não informado — fora da conta")

    # --- A premissa mais favoravel possivel, SEMPRE declarada -------------
    #
    # §5.6: "Aparece SEMPRE, inclusive quando todos os valores sao o default. A
    # hipotese favoravel precisa estar DITA NA TELA, nao escondida no default."
    #
    # A canibalizacao deixou de ser modelada (decisao do cliente, 11/08/2026), e
    # o campo saiu da interface. A premissa que ficou no lugar dele e justamente
    # a mais favoravel: nenhuma venda de refil tira venda da original. Ela e
    # declarada aqui em toda simulacao, lida de parametros — se um dia a
    # canibalizacao voltar a ser modelada, este item sai sozinho.
    if not P.CANIBALIZACAO_MODELADA:
        itens.append(f"{P.TEXTO_SEM_CANIBALIZACAO} {marcador('premissa')}")

    # --- A margem da original: existe ou nao existe -----------------------
    if r.tem_margem_da_original:
        itens.append(
            f"margem da original "
            f"<b>{formato.moeda_unitaria(r.margem_unitaria_original)}</b>/palheta "
            f"{marcador('premissa')}"
        )
    elif e.preco_original is not None:
        itens.append("custo da original não informado — sem incremental")

    # --- Cashback: declarado, e declarado como NAO sendo deducao ----------
    if r.cashback_total:
        itens.append(
            f"cashback {formato.moeda_agregada(r.cashback_total)}/mês "
            f"— pago pela Suicatech, fora da margem"
        )

    # --- Dias uteis, se fora do padrao ------------------------------------
    if e.dias_uteis != P.DIAS_UTEIS_PADRAO:
        itens.append(f"{e.dias_uteis} dias úteis {marcador('premissa')}")

    # --- Decisoes em aberto I e J ----------------------------------------
    texto_rampa = aberto.texto_premissas_rampa()
    if texto_rampa:
        itens.append(texto_rampa)

    # --- O rotulo da conta anual ------------------------------------------
    itens.append(P.rotulo_do_anual())

    st.markdown(
        f'<div class="st-premissas">{" · ".join(itens)}</div>',
        unsafe_allow_html=True,
    )

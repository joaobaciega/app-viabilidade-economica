"""Estado de sessao — DESIGN.md §11.1 (tabela acrescentada), P3, §5.2, §6.1.9.

TABELA DE ESTADO DE SESSAO — NUNCA PERSISTIDO, NUNCA PUBLICADO:

    preco_dianteiro, custo_dianteiro    §5.2  campo sensivel
    preco_traseiro,  custo_traseiro     §5.2, §5.13
    palhetas_originais_mes, preco_original, custo_original   a ancora
    substituicao                        §6.1.4 avancados
    comissao, aliquota, cashback        §6.1.7
    nome_cliente (so para o PDF)        plano §3.8

Por que isto importa: o custo de aquisicao da concessionaria E o preco de
venda da Suicatech, e o app tem link aberto sem login. O problema NAO e o
cliente ver o numero que o vendedor acabou de digitar — ele e a concessionaria,
ele sabe o que paga. O problema e o numero VIR PREENCHIDO ou PERSISTIR, porque
ai qualquer um com o link ve a tabela, e a proxima concessionaria ve o preco
da anterior.

REGRAS VERIFICADAS POR testes/test_checklist.py (AST):
  - nada desta tabela vai para localStorage, sessionStorage, query params,
    disco, st.cache_data ou st.cache_resource
  - st.session_state vive na memoria do servidor e morre ao recarregar a
    pagina — e o que entrega a nao persistencia de graca
  - o botao `novo cliente` limpa tudo SEM CONFIRMACAO: precisa ser executavel
    entre uma visita e outra, no elevador
"""

from __future__ import annotations

import streamlit as st

from src import parametros as P
from src.calculo import Entradas

# ---------------------------------------------------------------------------
# Chaves de widget. Os nomes sao usados como key= nos widgets, portanto
# escrever nelas DEPOIS de o widget ter sido instanciado levanta
# StreamlitAPIException — e por isso que os presets usam on_click (§5.3).
# ---------------------------------------------------------------------------

K_PONTOS = "pontos_de_venda"
K_PASSAGENS = "passagens_por_ponto"
K_PRECO_D = "preco_dianteiro"
K_CUSTO_D = "custo_dianteiro"
K_PRECO_T = "preco_traseiro"
K_CUSTO_T = "custo_traseiro"
# A ancora: o que ele vende hoje. Substitui o antigo campo unico de "margem
# atual com palhetas", que era uma pergunta que gerente nenhum responde de
# cabeca. O preco da original vem da Tela 3, consultado ao vivo.
K_ORIGINAIS = "palhetas_originais_mes"
K_PRECO_ORIG = "preco_original"
K_CUSTO_ORIG = "custo_original"
K_CONV_D = "conv_dianteiro"  # em pontos percentuais (inteiro), para o slider
K_CONV_T = "conv_traseiro"  # em pontos percentuais (inteiro)
K_CONSULTORES = "consultores_por_ponto"
K_DIAS_UTEIS = "dias_uteis"
K_NOME_CLIENTE = "nome_cliente"

# Cashback: R$ por venda, por destinatario, com linha propria para cada
# categoria. `cashback_d_0` = Consultor no dianteiro, `_1` = Gerente, `_2` =
# Marketing; `cashback_t_*` idem no traseiro. Os indices seguem a ordem de
# `parametros.DESTINATARIOS_CASHBACK`, que e a fonte unica dos nomes.
CHAVES_CASHBACK_D: tuple[str, ...] = tuple(
    f"cashback_d_{i}" for i in range(len(P.DESTINATARIOS_CASHBACK))
)
CHAVES_CASHBACK_T: tuple[str, ...] = tuple(
    f"cashback_t_{i}" for i in range(len(P.DESTINATARIOS_CASHBACK))
)

# Os campos que o botao `novo cliente` limpa e que NUNCA persistem.
CAMPOS_DE_SESSAO: tuple[str, ...] = (
    K_PRECO_D,
    K_CUSTO_D,
    K_PRECO_T,
    K_CUSTO_T,
    K_ORIGINAIS,
    K_PRECO_ORIG,
    K_CUSTO_ORIG,
    K_NOME_CLIENTE,
    K_PASSAGENS,
    K_CONSULTORES,
    *CHAVES_CASHBACK_D,
    *CHAVES_CASHBACK_T,
)

# Defaults dos campos NAO sensiveis. Repare que nenhum campo de preco, custo
# ou ancora aparece aqui: eles abrem None e continuam None (P3, §5.2).
_DEFAULTS: dict[str, object] = {
    K_PONTOS: P.PONTOS_DE_VENDA_PADRAO,
    K_CONV_D: 0,  # nenhum preset ativo na primeira carga (§6.1.4)
    K_CONV_T: 0,
    K_DIAS_UTEIS: P.DIAS_UTEIS_PADRAO,
}


def iniciar() -> None:
    """Semeia apenas os campos nao sensiveis. Idempotente.

    Estado E0 (§6.1.6): campos 2-5 vazios, nenhum preset ativo. Nenhuma
    leitura de planilha, nenhuma rede alem do proprio websocket.
    """
    for chave, valor in _DEFAULTS.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def aplicar_preset(nome: str) -> None:
    """Escreve os DOIS valores — dianteiro e traseiro — via on_click.

    DESIGN §5.3: "Cada botao escreve OS DOIS valores em st.session_state, via
    on_click. Escrever a chave de um widget depois que ele foi instanciado
    levanta StreamlitAPIException; por isso e on_click, nao codigo depois do
    botao."

    Repare que o traseiro tambem e escrito: mover o SLIDER do dianteiro nao
    altera o traseiro (§5.4), mas apertar um PRESET altera os dois, porque o
    preset e um par medido.
    """
    preset = P.preset_por_nome(nome)
    if preset is None:
        return
    st.session_state[K_CONV_D] = int(round(preset.dianteiro * 100))
    st.session_state[K_CONV_T] = int(round(preset.traseiro * 100))


# Valor de limpeza por campo. `None` para numerico, False para interruptor,
# "" para texto, 0 para o slider de substituicao.
#
# POR QUE ATRIBUIR E NAO `del`: apagar a chave de um widget do session_state
# zera o estado no servidor, mas NAO empurra o reset para o navegador — o campo
# continua MOSTRANDO o numero antigo enquanto o calculo ja o considera vazio.
# Isso apareceu na verificacao: depois de `novo cliente` a tela voltava para o
# estado E1 (correto) e os campos de preco e custo seguiam preenchidos na cara
# do proximo cliente (errado, e e exatamente o vazamento que a §5.2 existe para
# impedir). Atribuir o valor de limpeza sincroniza os dois lados.
_LIMPEZA: dict[str, object] = {
    K_PRECO_D: None,
    K_CUSTO_D: None,
    K_PRECO_T: None,
    K_CUSTO_T: None,
    K_ORIGINAIS: None,
    K_PRECO_ORIG: None,
    K_CUSTO_ORIG: None,
    K_PASSAGENS: None,
    K_CONSULTORES: None,
    K_NOME_CLIENTE: "",
    # O cashback e negociado por cliente: some junto (plano §1.4, "rateio
    # variavel por negociacao e por cargo").
    **{chave: None for chave in CHAVES_CASHBACK_D},
    **{chave: None for chave in CHAVES_CASHBACK_T},
}


def aplicar_traseiro(fracao: float) -> None:
    """Atalho de aproveitamento traseiro, via on_click.

    Escreve SO o traseiro — nunca toca no dianteiro. O inverso tambem vale
    (§5.4): mover o slider do dianteiro nao altera o traseiro. Acoplar os dois
    recriaria exatamente o risco n. 1 do plano.

    E `on_click` pela mesma razao dos presets (§5.3): escrever a chave de um
    widget depois que ele foi instanciado levanta StreamlitAPIException.
    """
    st.session_state[K_CONV_T] = int(round(fracao * 100))


def novo_cliente() -> None:
    """Limpa o estado de sessao SEM CONFIRMACAO (§5.2, plano §6.3).

    Preco, custo, ancora, deducoes e nome do cliente somem. O cenario
    (aproveitamento) e a operacao (pontos de venda, dias uteis) permanecem,
    porque nao sao sensiveis e refazer isso a cada visita e atrito sem ganho.

    Roda como `on_click`, portanto ANTES da instanciacao dos widgets no rerun —
    e por isso escrever nas chaves aqui e seguro.
    """
    for chave, vazio in _LIMPEZA.items():
        st.session_state[chave] = vazio
    iniciar()


def _num(chave: str) -> float | None:
    """Le um campo numerico opcional. Ausente ou None continua None.

    NUNCA converte None em 0. A diferenca entre "nao informado" e "zero" e a
    diferenca entre o estado E1 e uma ancora falsa no cenario mais favoravel
    possivel (§6.1.6, P9).
    """
    valor = st.session_state.get(chave)
    if valor is None or valor == "":
        return None
    return float(valor)


def ler_entradas() -> Entradas:
    """Monta o Entradas do calculo a partir do session_state."""
    return Entradas(
        pontos_de_venda=int(st.session_state.get(K_PONTOS) or 1),
        passagens_por_ponto=_num(K_PASSAGENS),
        preco_dianteiro=_num(K_PRECO_D),
        custo_dianteiro=_num(K_CUSTO_D),
        preco_traseiro=_num(K_PRECO_T),
        custo_traseiro=_num(K_CUSTO_T),
        aproveitamento_dianteiro=(st.session_state.get(K_CONV_D) or 0) / 100,
        aproveitamento_traseiro=(st.session_state.get(K_CONV_T) or 0) / 100,
        palhetas_originais_mes=_num(K_ORIGINAIS),
        preco_original=_num(K_PRECO_ORIG),
        custo_original=_num(K_CUSTO_ORIG),
        consultores_por_ponto=_num(K_CONSULTORES),
        dias_uteis=int(st.session_state.get(K_DIAS_UTEIS) or P.DIAS_UTEIS_PADRAO),
        cashback_dianteiro=tuple(_num(c) or 0.0 for c in CHAVES_CASHBACK_D),
        cashback_traseiro=tuple(_num(c) or 0.0 for c in CHAVES_CASHBACK_T),
    )


def contar_avancados_alterados() -> int:
    """Quantos campos de Ajustes avancados estao fora do padrao.

    Usado no rotulo do expander. Nada dentro dos avancados pode alterar o
    resultado sem que a faixa de premissas reflita (§5.10) — este contador e
    um reforco, nao o mecanismo.
    """
    n = 0
    if _num(K_CONSULTORES) is not None:
        n += 1
    if int(st.session_state.get(K_DIAS_UTEIS) or P.DIAS_UTEIS_PADRAO) != P.DIAS_UTEIS_PADRAO:
        n += 1
    # O cashback conta como UM item, nao como seis campos: e um programa, e o
    # contador serve para o vendedor saber que ha algo fora do padrao (§5.10).
    if any(
        _num(chave) for chave in (*CHAVES_CASHBACK_D, *CHAVES_CASHBACK_T)
    ):
        n += 1
    return n

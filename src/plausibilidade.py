"""Regras de plausibilidade R1-R5 (DESIGN.md §6.1.8). Aritmetica pura.

"Todas escrevem EXCLUSIVAMENTE na faixa do vendedor (§5.9), em ordem."

"NENHUMA dessas regras bloqueia o calculo. Um numero implausivel exibido com
aviso discreto ainda serve a conversa; um bloqueio na frente do cliente
encerra a cena."

O texto DESCREVE, nao acusa (§5.9): "carga de 34,1 veiculos por consultor por
dia", nunca "valor invalido". O vocabulario de alerta — erro, invalido,
atencao, cuidado — e proibido (§4).

Este modulo devolve strings. Quem as pinta em 12px cinza no rodape e
componentes/faixa_vendedor.py. Nenhuma delas pode virar st.warning ou
st.error: uma caixa amarela na frente do gerente transforma um ajuste tecnico
em vexame publico.
"""

from __future__ import annotations

from src import formato
from src import parametros as P
from src.calculo import Entradas, Resultado, traseiro_entra_na_conta


def avaliar(e: Entradas, r: Resultado) -> list[str]:
    """Devolve as linhas da faixa do vendedor, na ordem das regras da §6.1.8.

    Varios avisos simultaneos viram linhas separadas na mesma faixa (§5.9).
    Nunca um contador, nunca um badge.
    """
    linhas: list[str] = []

    linhas.extend(_r1_carga_por_consultor(e))
    linhas.extend(_r2_custo_acima_do_preco(e))
    linhas.extend(_r3_margem_negativa(r))
    linhas.extend(_r4_traseiro_fora_da_conta(e))
    linhas.extend(_r5_coeficientes_provisorios())
    linhas.extend(_r6_cashback_sem_traseiro_na_conta(e, r))
    linhas.extend(_r8_logo_em_reserva())

    return linhas


def _r6_cashback_sem_traseiro_na_conta(e: Entradas, r: Resultado) -> list[str]:
    """R6 — cashback do traseiro preenchido com o traseiro fora da conta.

    O valor prometido a equipe sairia inflado: haveria cashback previsto para uma
    venda que a simulacao nao contabiliza. Descreve, nao bloqueia.
    """
    if any(e.cashback_traseiro) and not traseiro_entra_na_conta(e):
        return [
            "cashback do traseiro preenchido, mas o traseiro está fora da conta "
            "— informe o preço e o custo do traseiro para o valor entrar"
        ]
    return []


def _r8_logo_em_reserva() -> list[str]:
    """R8 — o logo nao carregou e o cabecalho esta com a marca em texto.

    O vendedor precisa saber; o cliente nao precisa ver isso em destaque. Por
    isso vive na faixa, como todo o resto (§5.9).
    """
    from src import marca

    motivo = marca.motivo_da_reserva()
    return [motivo] if motivo else []


def _r1_carga_por_consultor(e: Entradas) -> list[str]:
    """R1 / R1b — carga de veiculos por consultor por dia.

    DESIGN §6.1.8: "R1 usa grandezas POR PONTO (V e consultores por ponto),
    nao os totais — assim o resultado nao depende de P e a conta permanece a
    mesma do plano (§3.2)."

    R1b: consultores vazio => a verificacao e desligada e isso e DITO.
    A regra nao e avaliada com valor inventado.
    """
    if e.consultores_por_ponto is None or e.consultores_por_ponto <= 0:
        return ["verificação de carga desligada — consultores não informados"]

    if e.passagens_por_ponto is None or e.dias_uteis <= 0:
        return []

    carga = e.passagens_por_ponto / e.consultores_por_ponto / e.dias_uteis
    if carga > P.CARGA_MAXIMA_VEICULOS_DIA:
        return [
            f"carga de {formato.decimal(carga)} veículos por consultor por dia "
            f"— confira se os consultores são por ponto ou no total"
        ]
    return []


def _r2_custo_acima_do_preco(e: Entradas) -> list[str]:
    """R2 — custo acima do preco, margem unitaria negativa.

    Avaliado por categoria, e cada categoria e nomeada. Nao existe validacao
    de piso de preco aqui: a decisao F esta em aberto (§10-F) e o campo aceita
    qualquer numero positivo.
    """
    linhas: list[str] = []

    if (
        e.preco_dianteiro is not None
        and e.custo_dianteiro is not None
        and e.custo_dianteiro > e.preco_dianteiro
    ):
        linhas.append(
            "custo acima do preço no dianteiro — margem unitária negativa"
        )

    if (
        e.preco_traseiro is not None
        and e.custo_traseiro is not None
        and e.custo_traseiro > e.preco_traseiro
    ):
        linhas.append(
            "custo acima do preço no traseiro — margem unitária negativa"
        )

    if (
        e.preco_original is not None
        and e.custo_original is not None
        and e.custo_original > e.preco_original
    ):
        linhas.append(
            "custo acima do preço na palheta original — confira os dois valores"
        )

    return linhas


def _r3_margem_negativa(r: Resultado) -> list[str]:
    """R3 — o cenario fica negativo.

    Sem canibalizacao modelada, isto so acontece se o custo do refil estiver
    acima do preco em alguma categoria — o que R2 tambem aponta, por categoria.
    A regra permanece porque o valor da manchete negativo merece uma frase
    propria: e o que o vendedor le antes de o cliente perguntar.

    O valor continua na tela, com o sinal, em tinta clara. Nada em vermelho
    (§3.1.2, §5.5).
    """
    if r.incremental_mensal is not None and r.incremental_mensal < 0:
        return [
            "a margem do refil está negativa — confira preço e custo das duas "
            "categorias"
        ]
    return []


def _r4_traseiro_fora_da_conta(e: Entradas) -> list[str]:
    """R4 — traseiro fora da conta por preco ou custo nao informados.

    Dispara quando o vendedor informou UM dos dois (sinal de que pretendia
    incluir o traseiro) mas nao o outro. Com os dois vazios, o traseiro
    simplesmente nao faz parte da proposta e nao ha nada a avisar.
    """
    algum_informado = e.preco_traseiro is not None or e.custo_traseiro is not None
    if algum_informado and not traseiro_entra_na_conta(e):
        return ["traseiro fora da conta — preço ou custo não informados"]
    return []


def _r5_coeficientes_provisorios() -> list[str]:
    """R5 — rampa e sazonalidade em definicao (⚠️ I e J).

    Enquanto os coeficientes nao existirem, o anual e regime x 12 e a tela
    DIZ isso. A ausencia e declarada; a curva plana nao e aplicada em silencio.
    """
    if not P.rampa_aplicada() or not P.sazonalidade_aplicada():
        return [
            "rampa e sazonalidade não aplicadas — coeficientes em definição"
        ]
    return []

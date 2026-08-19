"""O calculo. Aritmetica pura.

Este modulo NAO importa streamlit e NAO faz I/O. E o que torna os casos-teste
executaveis sem subir o app, e o que permite auditar a conta sem entender nada
de interface.

    P   pontos de venda
    V   passagens/mes por ponto
    Cd  aproveitamento dianteiro (fracao 0-1)
    Ct  aproveitamento traseiro  (fracao 0-1)
    Pd  preco do par dianteiro      Kd  custo do par dianteiro
    Pt  preco da unidade traseira   Kt  custo da unidade traseira
    Q   palhetas ORIGINAIS vendidas hoje, por mes
    Po  preco da palheta original   Ko  custo da palheta original

    T   = P x V                       passagens totais por mes
    Ud  = T x Cd                      pares dianteiros de refil por mes
    Ut  = T x Ct                      unidades traseiras de refil por mes
    MCd = Ud x (Pd - Kd)
    MCt = Ut x (Pt - Kt)   ou 0 se Pt/Kt vazios
    MC  = MCd + MCt                   margem de contribuicao do refil, por mes

    INC  = MC                         margem de contribuicao mensal
    ANO  = INC x 12                   ano cheio em regime  ⚠️ I, J
    TRAD = Cd                         "X a cada 10 carros que entram"

    MOu  = Po - Ko                    margem unitaria da palheta original
    MA   = Q x MOu                    margem mensal atual com palhetas

CANIBALIZACAO NAO MODELADA (decisao do cliente, 11/08/2026). O campo de
substituicao saiu da interface, e nada e subtraido de MC. O app passa a assumir
que nenhuma venda de refil tira uma venda da palheta original — a premissa mais
favoravel possivel (DESIGN §5.6) e o risco 7 do plano. Ela NAO fica implicita: a
faixa de premissas a declara em toda simulacao, lendo
`parametros.CANIBALIZACAO_MODELADA`.

CASHBACK NAO E DEDUCAO. Sao valores em R$ POR VENDA destinados a Consultor,
Gerente e Marketing, com linhas proprias para dianteiro e traseiro. Pago pela
Suicatech, saindo da margem DELA (plano, decisao A): preencher ACRESCENTA uma
linha ao resultado e NUNCA altera `incremental_mensal` nem `anual`.

A ANCORA MUDOU (11/08/2026, decisao do cliente). Antes o app pedia "margem de
contribuicao mensal atual com palhetas" — uma pergunta que gerente de pos-venda
nao responde de cabeca. Agora pede o que ele sabe de cor:

    quantas palhetas voce vende por mes, e a quanto

O preco da original vem da Tela 3, consultado ao vivo. O custo dela e OPCIONAL,
e a consequencia de nao informar esta em `rotulo_do_resultado`: sem margem da
original nao existe incremental, e o rotulo passa a dizer "margem de
contribuicao do refil". O app nunca ASSUME uma margem para a original.

REGRA CRITICA (DESIGN §5.13, plano §8 decisao B):
    Pt e Kt NUNCA sao derivados de Pd e Kd. Nem por / 2, nem por qualquer
    fator. Dianteiro e par (duas medidas diferentes), traseiro e lamina unica.
    Derivar erra por 2x na tela cuja unica funcao e ser auditavel.
    Nao existe nenhuma expressao neste arquivo relacionando as duas.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal

from src import parametros as P

Estado = Literal[
    "E1_sem_operacao",
    "E1b_sem_produto",
    "E2_sem_cenario",
    "E3_completo",
    "E5_incremental_negativo",
]

MESES_NO_ANO = 12


@dataclass(frozen=True)
class Entradas:
    """O que o vendedor digitou. Campos sensiveis abrem None e continuam None.

    DESIGN P3 / §5.2: preco e custo com value=None. Nenhum default, nenhum
    valor de demonstracao. `None` significa "nao informado", NUNCA zero.
    """

    pontos_de_venda: int = P.PONTOS_DE_VENDA_PADRAO
    passagens_por_ponto: float | None = None

    # O refil — dianteiro (par) e traseiro (unitario), precos INDEPENDENTES
    preco_dianteiro: float | None = None
    custo_dianteiro: float | None = None
    preco_traseiro: float | None = None
    custo_traseiro: float | None = None

    aproveitamento_dianteiro: float = 0.0  # fracao 0-1
    aproveitamento_traseiro: float = 0.0  # fracao 0-1

    # A operacao de hoje — a ancora
    palhetas_originais_mes: float | None = None  # Q, por ponto de venda
    preco_original: float | None = None  # Po — vem da Tela 3
    custo_original: float | None = None  # Ko — OPCIONAL

    # Avancados — plausibilidade apenas, nao entra em conta de margem
    consultores_por_ponto: float | None = None
    dias_uteis: int = P.DIAS_UTEIS_PADRAO

    # Cashback: R$ POR VENDA destinados a cada parte. Zero = nao participa.
    #
    # NAO E DEDUCAO. E pago pela Suicatech, saindo da margem DELA (plano,
    # decisao A). Nenhum destes campos aparece em qualquer expressao que
    # produza `incremental_mensal` — ver `calcular`.
    cashback_dianteiro: tuple[float, ...] = (0.0, 0.0, 0.0)
    cashback_traseiro: tuple[float, ...] = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class Resultado:
    """Campos None significam "nao exibir" — nunca zero disfarcado."""

    estado: Estado

    passagens_totais: float | None = None
    pares_dianteiros: float | None = None
    unidades_traseiras: float | None = None

    margem_dianteiro: float | None = None
    margem_traseiro: float | None = None
    margem_refil: float | None = None  # MC

    faturamento_refil: float | None = None

    # A operacao de hoje
    originais_por_mes: float | None = None  # Q x pontos
    faturamento_atual: float | None = None  # Q x Po
    margem_atual: float | None = None  # Q x (Po - Ko), None sem Ko
    margem_unitaria_original: float | None = None  # Po - Ko

    incremental_mensal: float | None = None
    anual: float | None = None

    traducao_fracao: float = 0.0
    traseiro_na_conta: bool = False
    tem_margem_da_original: bool = False

    # Cashback: exibicao, NUNCA deducao.
    cashback_total: float = 0.0
    cashback_por_destinatario: tuple[tuple[str, float], ...] = field(
        default_factory=tuple
    )
    cashback_por_par_dianteiro: float = 0.0
    cashback_por_unidade_traseira: float = 0.0


# ---------------------------------------------------------------------------
# Regra de unidade — DESIGN §5.13
# ---------------------------------------------------------------------------


def traseiro_entra_na_conta(e: Entradas) -> bool:
    """O traseiro so entra se preco E custo dele foram informados.

    §5.13: "Se o preco ou o custo do traseiro estiver vazio, o traseiro
    contribui com R$ 0 e a faixa de premissas declara. Nunca estimado, nunca
    inferido."
    """
    return e.preco_traseiro is not None and e.custo_traseiro is not None


def tem_margem_da_original(e: Entradas) -> bool:
    """Sem preco E custo da original nao existe margem unitaria dela.

    Consequencia: nao existe incremental, e o rotulo do resultado muda. O app
    NUNCA assume um valor para a margem da original.
    """
    return e.preco_original is not None and e.custo_original is not None


# ---------------------------------------------------------------------------
# O calculo
# ---------------------------------------------------------------------------


def calcular(e: Entradas) -> Resultado:
    faltam_operacao = e.passagens_por_ponto is None
    faltam_produto = e.preco_dianteiro is None or e.custo_dianteiro is None

    if faltam_operacao or faltam_produto:
        estado: Estado = "E1_sem_operacao" if faltam_operacao else "E1b_sem_produto"
        return Resultado(
            estado=estado,
            traducao_fracao=e.aproveitamento_dianteiro,
            originais_por_mes=_originais(e),
            faturamento_atual=_faturamento_atual(e),
        )

    # --- Volume do refil ---------------------------------------------------
    T = e.pontos_de_venda * e.passagens_por_ponto
    Ud = T * e.aproveitamento_dianteiro
    Ut = T * e.aproveitamento_traseiro

    # --- Margem por categoria ---------------------------------------------
    MCd = Ud * (e.preco_dianteiro - e.custo_dianteiro)

    com_traseiro = traseiro_entra_na_conta(e)
    if com_traseiro:
        MCt = Ut * (e.preco_traseiro - e.custo_traseiro)
        faturamento = Ud * e.preco_dianteiro + Ut * e.preco_traseiro
    else:
        # Fora da conta. NAO estimado, NAO inferido, NAO derivado do dianteiro.
        MCt = 0.0
        Ut = 0.0
        faturamento = Ud * e.preco_dianteiro

    MC = MCd + MCt

    # --- A operacao de hoje ------------------------------------------------
    originais = _originais(e)
    faturamento_atual = _faturamento_atual(e)
    com_margem_original = tem_margem_da_original(e)
    margem_unit_original = (
        e.preco_original - e.custo_original if com_margem_original else None
    )
    margem_atual = (
        originais * margem_unit_original
        if (originais is not None and margem_unit_original is not None)
        else None
    )

    # --- Incremental -------------------------------------------------------
    #
    # A canibalizacao NAO E MODELADA (parametros.CANIBALIZACAO_MODELADA). O app
    # assume que nenhuma venda de refil tira venda da palheta original — a
    # premissa mais favoravel possivel, DECLARADA em toda simulacao na faixa de
    # premissas. Nada e subtraido aqui.
    #
    # Sem margem da original nao existe incremental: `rotulo_do_resultado`
    # passa a dizer "margem de contribuicao do refil", sem a palavra
    # "incremental". O app nao assume nada.
    INC = MC
    ANO = INC * MESES_NO_ANO

    # --- Cashback: exibicao, NUNCA deducao --------------------------------
    #
    # Pago pela Suicatech, saindo da margem DELA (plano, decisao A). Preencher
    # ACRESCENTA UMA LINHA no resultado, nunca subtrai. Repare que nenhuma
    # variavel abaixo participa de INC nem de ANO, que ja estao calculados.
    cash_d, cash_t, por_destinatario = _cashback(e, Ud, Ut)

    if INC < 0:
        estado = "E5_incremental_negativo"
    elif e.aproveitamento_dianteiro == 0 and e.aproveitamento_traseiro == 0:
        estado = "E2_sem_cenario"
    else:
        estado = "E3_completo"

    return Resultado(
        estado=estado,
        passagens_totais=T,
        pares_dianteiros=Ud,
        unidades_traseiras=Ut,
        margem_dianteiro=MCd,
        margem_traseiro=MCt,
        margem_refil=MC,
        faturamento_refil=faturamento,
        originais_por_mes=originais,
        faturamento_atual=faturamento_atual,
        margem_atual=margem_atual,
        margem_unitaria_original=margem_unit_original,
        incremental_mensal=INC,
        anual=ANO,
        traducao_fracao=e.aproveitamento_dianteiro,
        traseiro_na_conta=com_traseiro,
        tem_margem_da_original=com_margem_original,
        cashback_total=cash_d + cash_t,
        cashback_por_destinatario=por_destinatario,
        cashback_por_par_dianteiro=sum(e.cashback_dianteiro),
        cashback_por_unidade_traseira=(
            sum(e.cashback_traseiro) if com_traseiro else 0.0
        ),
    )


def _cashback(
    e: Entradas, Ud: float, Ut: float
) -> tuple[float, float, tuple[tuple[str, float], ...]]:
    """Cashback mensal por linha e por destinatario.

    Os valores sao R$ POR VENDA: para cada par dianteiro vendido, tanto vai para
    o consultor, tanto para o gerente, tanto para marketing. Idem por unidade
    traseira, com valores proprios.

    O traseiro so entra se estiver na conta — pagar cashback de uma venda que a
    simulacao nao contabiliza inflaria o numero que o vendedor promete a equipe.
    """
    por_par = sum(e.cashback_dianteiro)
    por_unidade = sum(e.cashback_traseiro) if traseiro_entra_na_conta(e) else 0.0

    total_dianteiro = Ud * por_par
    total_traseiro = Ut * por_unidade

    por_destinatario: list[tuple[str, float]] = []
    for i, nome in enumerate(P.DESTINATARIOS_CASHBACK):
        valor_d = e.cashback_dianteiro[i] if i < len(e.cashback_dianteiro) else 0.0
        valor_t = e.cashback_traseiro[i] if i < len(e.cashback_traseiro) else 0.0
        if not traseiro_entra_na_conta(e):
            valor_t = 0.0
        total = Ud * valor_d + Ut * valor_t
        if total:
            por_destinatario.append((nome, total))

    return total_dianteiro, total_traseiro, tuple(por_destinatario)


def _originais(e: Entradas) -> float | None:
    if e.palhetas_originais_mes is None:
        return None
    return e.palhetas_originais_mes * e.pontos_de_venda


def _faturamento_atual(e: Entradas) -> float | None:
    originais = _originais(e)
    if originais is None or e.preco_original is None:
        return None
    return originais * e.preco_original


# ---------------------------------------------------------------------------
# Rotulo do resultado
# ---------------------------------------------------------------------------


def rotulo_do_resultado(r: Resultado) -> str:
    """O rotulo nomeia a conta que foi feita.

    §6.1.7: "o rotulo tem que nomear so o que de fato foi descontado." Nada e
    descontado da margem exibida: comissao e imposto sairam da interface, e o
    cashback NUNCA foi deducao — ele e pago pela Suicatech.

    "Incremental" so aparece quando existe margem da palheta original para
    comparar. Sem ela o rotulo e "margem de contribuicao do refil": nomear a
    conta errada e pior que nao nomear.

    Em nenhuma combinacao o rotulo vira "lucro" (§4, P12).
    """
    if r.tem_margem_da_original:
        return "margem de contribuição incremental"
    return "margem de contribuição do refil"


# ---------------------------------------------------------------------------
# Curva de sensibilidade (DESIGN §5.11)
# ---------------------------------------------------------------------------


def curva_sensibilidade(e: Entradas, passo_pp: int = 1) -> list[tuple[float, float]]:
    """Margem incremental ANUAL em funcao do aproveitamento dianteiro.

    Dominio identico ao do slider, lido de parametros.SLIDER_DOMINIO, para que
    o marcador nunca saia do plot. So o dianteiro varia — o traseiro NAO
    acompanha (acoplar recriaria o risco n. 1 do plano).
    """
    lo, hi = P.SLIDER_DOMINIO
    pontos: list[tuple[float, float]] = []
    for pp in range(lo, hi + 1, passo_pp):
        r = calcular(replace(e, aproveitamento_dianteiro=pp / 100))
        if r.anual is not None:
            pontos.append((float(pp), r.anual))
    return pontos


def curvas_comparadas(
    e: Entradas, passo_pp: int = 1
) -> tuple[list[tuple[float, float]], float | None]:
    """As duas linhas do grafico, na MESMA grandeza: margem anual TOTAL.

    Devolve `(com_refil, so_original)`:

      com_refil    margem anual total adotando o refil, por aproveitamento
                   dianteiro = margem atual + incremental
      so_original  margem anual se ele continuar SO com a palheta original.
                   E constante: nao depende do aproveitamento do refil, e por
                   isso desenha uma reta horizontal

    A DISTANCIA ENTRE AS DUAS E EXATAMENTE A MANCHETE (o incremental), e o
    ponto onde elas se cruzam responde a pergunta que o gerente faz: "a partir
    de quanto de aproveitamento eu ganho trocando?".

    Devolve `so_original = None` quando falta o custo da palheta original —
    sem ele nao existe margem dela, e o app NAO ASSUME um valor. Nesse caso o
    grafico volta a ter uma linha so.
    """
    lo, hi = P.SLIDER_DOMINIO
    com_refil: list[tuple[float, float]] = []
    base: float | None = None

    for pp in range(lo, hi + 1, passo_pp):
        r = calcular(replace(e, aproveitamento_dianteiro=pp / 100))
        if r.anual is None:
            continue
        atual_anual = (
            r.margem_atual * MESES_NO_ANO if r.margem_atual is not None else 0.0
        )
        if r.margem_atual is not None:
            base = atual_anual
        com_refil.append((float(pp), atual_anual + r.anual))

    return com_refil, base


def preset_ativo(e: Entradas) -> str | None:
    """Qual preset esta ativo — DERIVADO, nunca guardado.

    §5.3: "Um preset esta ativo se e somente se (conv_dianteiro,
    conv_traseiro) for exatamente igual ao par daquele preset. Isso torna
    IMPOSSIVEL a tela mostrar 'REALISTA' aceso com o slider em 27%."
    """
    for p in P.PRESETS:
        if (
            abs(e.aproveitamento_dianteiro - p.dianteiro) < 1e-9
            and abs(e.aproveitamento_traseiro - p.traseiro) < 1e-9
        ):
            return p.nome
    return None

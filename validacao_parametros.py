"""Validacoes V1-V7 dos parametros (DESIGN.md §11.2).

"Rodam na carga do modulo. Falha = o app NAO SOBE, com erro no log do deploy.
Nunca tela quebrada na frente do cliente."

DESIGN §7.4: "falhar alto e cedo — se um preset nao declarar origem, ou se uma
categoria nao declarar unidade, o app nao sobe, com mensagem no log do deploy.
Nunca uma tela quebrada na frente do cliente, nunca um default silencioso."

Chamado por src/__init__.py, portanto qualquer import de qualquer coisa em
src/ ja dispara a validacao. Nao ha caminho que contorne.
"""

from __future__ import annotations

from typing import get_args

from src import parametros as P


class ParametroInvalido(Exception):
    """Erro de configuracao. Aborta a subida do app.

    Nao e excecao de runtime tratavel: se isto sobe, a configuracao esta
    errada e o app nao deve atender ninguem.
    """


def _falhar(regra: str, detalhe: str) -> None:
    raise ParametroInvalido(
        f"{regra} reprovou em parametros.py: {detalhe}\n"
        f"O app nao sobe com parametro invalido (DESIGN §11.2, §7.4)."
    )


def v1_presets_declaram_origem() -> None:
    """V1 — Todo preset declara origem_dianteiro e origem_traseiro.

    Sem isso a tela nao sabe se escreve `◆ carteira` ou `≈ derivado`, e a
    mitigacao do risco n. 1 do plano deixa de existir.
    """
    validas = set(get_args(P.Origem))
    for p in P.PRESETS:
        for campo in ("origem_dianteiro", "origem_traseiro"):
            valor = getattr(p, campo, None)
            if valor is None:
                _falhar("V1", f"preset '{p.nome}' nao declara {campo}")
            if valor not in validas:
                _falhar(
                    "V1",
                    f"preset '{p.nome}'.{campo} = {valor!r}, "
                    f"fora do enum {sorted(validas)}",
                )


def v2_presets_sao_monotonicos() -> None:
    """V2 — pessimista < realista < otimista, no dianteiro E no traseiro."""
    ordem = ("pessimista", "realista", "otimista")
    presentes = {p.nome: p for p in P.PRESETS}

    faltando = [n for n in ordem if n not in presentes]
    if faltando:
        _falhar("V2", f"presets ausentes: {faltando}")

    for campo in ("dianteiro", "traseiro"):
        valores = [getattr(presentes[n], campo) for n in ordem]
        if not (valores[0] < valores[1] < valores[2]):
            _falhar(
                "V2",
                f"{campo} nao e crescente: "
                f"pessimista={valores[0]}, realista={valores[1]}, "
                f"otimista={valores[2]}",
            )


def v3_categorias_declaram_unidade() -> None:
    """V3 — Toda categoria declara `unidade` explicitamente.

    DESIGN §11.2: "Aborta. NUNCA assuma `par` por default."

    Esta e a validacao que impede o erro que erra por 2x na tela cuja unica
    funcao e ser auditavel (plano §2.7).
    """
    validas = set(get_args(P.Unidade))
    if not P.CATEGORIAS:
        _falhar("V3", "nenhuma categoria declarada")

    for c in P.CATEGORIAS:
        unidade = getattr(c, "unidade", None)
        if unidade is None:
            _falhar("V3", f"categoria '{c.nome}' nao declara unidade")
        if unidade not in validas:
            _falhar(
                "V3",
                f"categoria '{c.nome}'.unidade = {unidade!r}, "
                f"fora do enum {sorted(validas)}",
            )
        if not getattr(c, "rotulo_unidade", "").strip():
            _falhar(
                "V3",
                f"categoria '{c.nome}' nao declara rotulo_unidade — "
                f"todo preco e custo carrega a unidade no rotulo (§5.13)",
            )


def v4_presets_em_zero_um() -> None:
    """V4 — Todo valor de preset em 0-1."""
    for p in P.PRESETS:
        for campo in ("dianteiro", "traseiro"):
            v = getattr(p, campo)
            if not isinstance(v, (int, float)) or not (0.0 <= v <= 1.0):
                _falhar(
                    "V4",
                    f"preset '{p.nome}'.{campo} = {v!r}, fora da faixa 0-1 "
                    f"(e fracao, nao percentual)",
                )


def v5_dominio_cobre_presets() -> None:
    """V5 — slider_dominio cobre todos os valores de preset.

    DESIGN §11.2: "Aborta — senao um preset joga o marcador para fora do
    grafico." O dominio do slider e o do eixo X do grafico sao o mesmo valor.
    """
    lo, hi = P.SLIDER_DOMINIO
    if lo >= hi:
        _falhar("V5", f"slider_dominio invalido: {P.SLIDER_DOMINIO}")

    for p in P.PRESETS:
        for campo in ("dianteiro", "traseiro"):
            pct = getattr(p, campo) * 100
            if not (lo <= pct <= hi):
                _falhar(
                    "V5",
                    f"preset '{p.nome}'.{campo} = {pct:.0f}% esta fora do "
                    f"dominio do slider {P.SLIDER_DOMINIO} — o marcador sairia "
                    f"do grafico",
                )


def v6_piso_preco_ausente() -> None:
    """V6 — piso_preco is None enquanto a decisao F estiver aberta.

    DESIGN §11.2: "Aborta — impede que um piso inventado entre pela porta dos
    fundos."

    Esta validacao existe justamente para o caso de alguem (inclusive um agente)
    resolver "destravar" a decisao F escolhendo um numero razoavel.
    """
    if P.PISO_PRECO is not None:
        _falhar(
            "V6",
            f"PISO_PRECO = {P.PISO_PRECO!r}, mas a decisao F esta em aberto. "
            f"Um piso inventado que o vendedor fure vira erro do app; um piso "
            f"inventado que a Suicatech nao honre vira ancora falsa no cliente. "
            f"Se a decisao F foi tomada, remova esta validacao junto com o valor.",
        )


def v7_marcador_obrigatorio_quando_em_aberto() -> None:
    """V7 — rampa/sazonalidade None => a faixa de premissas PRECISA marcar ⚠️.

    DESIGN §11.2: "Se rampa_meses ou sazonalidade_mensal forem None, a faixa
    de premissas precisa renderizar o marcador ⚠️. Aborta."

    A validacao verifica a coerencia entre o parametro e o rotulo que o app
    vai exibir: se a rampa nao esta aplicada, o rotulo do anual e obrigado a
    dizer "ano cheio em regime", nunca "primeiros 12 meses". O rotulo sempre
    descreve a conta que foi feita (§6.1.5).
    """
    em_aberto = not P.rampa_aplicada() or not P.sazonalidade_aplicada()
    rotulo = P.rotulo_do_anual()

    if em_aberto and rotulo != "ano cheio em regime":
        _falhar(
            "V7",
            f"rampa/sazonalidade em aberto, mas rotulo_do_anual() = {rotulo!r}. "
            f"Trocar a conta sem trocar o rotulo e o jeito mais silencioso de "
            f"o app mentir (§6.1.5).",
        )
    if not em_aberto and rotulo == "ano cheio em regime":
        _falhar(
            "V7",
            "rampa e sazonalidade aplicadas, mas o rotulo ainda diz "
            "'ano cheio em regime'.",
        )

    # Se um dia forem preenchidas, precisam ter forma utilizavel.
    if P.RAMPA_MESES is not None and len(P.RAMPA_MESES) != 3:
        _falhar(
            "V7",
            f"RAMPA_MESES tem {len(P.RAMPA_MESES)} elementos; a rampa e dos "
            f"3 primeiros meses (plano §3.2)",
        )
    if P.SAZONALIDADE_MENSAL is not None and len(P.SAZONALIDADE_MENSAL) != 12:
        _falhar(
            "V7",
            f"SAZONALIDADE_MENSAL tem {len(P.SAZONALIDADE_MENSAL)} elementos; "
            f"a curva e mensal e precisa de 12",
        )


VALIDACOES = (
    v1_presets_declaram_origem,
    v2_presets_sao_monotonicos,
    v3_categorias_declaram_unidade,
    v4_presets_em_zero_um,
    v5_dominio_cobre_presets,
    v6_piso_preco_ausente,
    v7_marcador_obrigatorio_quando_em_aberto,
)


def validar_tudo() -> None:
    """Roda V1-V7. Levanta ParametroInvalido na primeira falha.

    Chamado no import de src/. Falha aqui = o app nao sobe.
    """
    for validacao in VALIDACOES:
        validacao()

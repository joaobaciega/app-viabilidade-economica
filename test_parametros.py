"""T15 — V1-V7 abortam o app com parametro invalido (DESIGN §11.2, §7.4).

"Falha = o app NAO SOBE, com erro no log do deploy. Nunca tela quebrada na
frente do cliente, nunca um default silencioso."

Tambem verifica as DECISOES EM ABERTO (§10): as constantes precisam ser None, e
V6 precisa abortar se alguem tentar declarar um piso de preco.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from src import parametros as P
from src import validacao_parametros as V


def test_T15_parametros_reais_passam() -> None:
    """O app sobe com os parametros de producao."""
    V.validar_tudo()


def test_T15_V1_preset_sem_origem_aborta(monkeypatch: pytest.MonkeyPatch) -> None:
    sem_origem = replace(P.PRESETS[1], origem_dianteiro=None)
    monkeypatch.setattr(P, "PRESETS", (P.PRESETS[0], sem_origem, P.PRESETS[2]))
    with pytest.raises(V.ParametroInvalido, match="V1"):
        V.v1_presets_declaram_origem()


def test_T15_V1_origem_fora_do_enum_aborta(monkeypatch: pytest.MonkeyPatch) -> None:
    invalido = replace(P.PRESETS[1], origem_traseiro="chutado")
    monkeypatch.setattr(P, "PRESETS", (invalido,))
    with pytest.raises(V.ParametroInvalido, match="V1"):
        V.v1_presets_declaram_origem()


def test_T15_V2_presets_nao_crescentes_abortam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # otimista abaixo do realista
    quebrado = replace(P.PRESETS[2], dianteiro=0.10)
    monkeypatch.setattr(P, "PRESETS", (P.PRESETS[0], P.PRESETS[1], quebrado))
    with pytest.raises(V.ParametroInvalido, match="V2"):
        V.v2_presets_sao_monotonicos()


def test_T15_V3_categoria_sem_unidade_aborta(monkeypatch: pytest.MonkeyPatch) -> None:
    """"Aborta. NUNCA assuma `par` por default.\""""
    sem_unidade = replace(P.CATEGORIAS[0], unidade=None)
    monkeypatch.setattr(P, "CATEGORIAS", (sem_unidade,))
    with pytest.raises(V.ParametroInvalido, match="V3"):
        V.v3_categorias_declaram_unidade()


def test_T15_V4_preset_fora_de_zero_um_aborta(monkeypatch: pytest.MonkeyPatch) -> None:
    # 30 em vez de 0,30 — o erro classico de percentual x fracao
    percentual = replace(P.PRESETS[1], dianteiro=30.0)
    monkeypatch.setattr(P, "PRESETS", (percentual,))
    with pytest.raises(V.ParametroInvalido, match="V4"):
        V.v4_presets_em_zero_um()


def test_T15_V5_dominio_que_nao_cobre_preset_aborta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Senao um preset joga o marcador para FORA do grafico."""
    monkeypatch.setattr(P, "SLIDER_DOMINIO", (0, 25))
    with pytest.raises(V.ParametroInvalido, match="V5"):
        V.v5_dominio_cobre_presets()


def test_T15_V6_piso_de_preco_inventado_aborta(monkeypatch: pytest.MonkeyPatch) -> None:
    """A validacao que impede um piso de entrar pela porta dos fundos.

    Este e o teste mais importante deste arquivo: ele existe para o caso de
    alguem — inclusive um agente — resolver "destravar" a decisao F escolhendo
    um numero razoavel.
    """
    monkeypatch.setattr(P, "PISO_PRECO", 150.0)
    with pytest.raises(V.ParametroInvalido, match="V6"):
        V.v6_piso_preco_ausente()


def test_T15_V7_rotulo_incoerente_com_a_rampa_aborta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """"Trocar a conta sem trocar o rotulo e o jeito mais silencioso de o app
    mentir." (§6.1.5)"""
    monkeypatch.setattr(P, "rotulo_do_anual", lambda: "primeiros 12 meses")
    with pytest.raises(V.ParametroInvalido, match="V7"):
        V.v7_marcador_obrigatorio_quando_em_aberto()


def test_T15_V7_rampa_com_tamanho_errado_aborta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(P, "RAMPA_MESES", (0.5, 0.8))  # 2 em vez de 3
    monkeypatch.setattr(P, "rotulo_do_anual", lambda: "ano cheio em regime")
    with pytest.raises(V.ParametroInvalido, match="V7"):
        V.v7_marcador_obrigatorio_quando_em_aberto()


# ---------------------------------------------------------------------------
# Decisoes em aberto (§10) — a AUSENCIA das constantes e a definicao de pronto
# ---------------------------------------------------------------------------


def test_decisao_F_sem_piso_de_preco() -> None:
    assert P.PISO_PRECO is None, (
        "decisao F esta em aberto: nao invente um piso. Um piso inventado que "
        "o vendedor fure vira erro do app; um que a Suicatech nao honre vira "
        "ancora falsa no cliente."
    )


def test_decisao_G_sem_numero_de_codigos() -> None:
    assert P.CODIGOS_COBERTURA_97 is None, (
        "decisao G esta em aberto: 'voce troca 40 codigos por 3' e uma frase "
        "que fecha reuniao, e ela precisa do NUMERO CERTO."
    )


def test_decisao_H_traseiro_extremos_sao_derivados() -> None:
    """So a linha realista foi medida. Os extremos NUNCA saem como carteira."""
    por_nome = {p.nome: p for p in P.PRESETS}
    assert por_nome["realista"].origem_traseiro == "carteira_medida"
    assert por_nome["pessimista"].origem_traseiro == "derivado"
    assert por_nome["otimista"].origem_traseiro == "derivado"


def test_decisao_H_derivacao_e_proporcional() -> None:
    """0,67x e 1,33x do dianteiro (plano §3.2)."""
    por_nome = {p.nome: p for p in P.PRESETS}
    realista = por_nome["realista"]
    assert por_nome["pessimista"].traseiro == pytest.approx(
        realista.traseiro * (por_nome["pessimista"].dianteiro / realista.dianteiro),
        abs=0.005,
    )


def test_decisoes_I_e_J_desligadas_e_declaradas() -> None:
    assert P.RAMPA_MESES is None
    assert P.SAZONALIDADE_MENSAL is None
    # O rotulo descreve a conta que foi feita.
    assert P.rotulo_do_anual() == "ano cheio em regime"
    assert not P.rampa_aplicada()
    assert not P.sazonalidade_aplicada()


def test_decisao_L_sem_limiar_de_idade() -> None:
    assert P.LIMIAR_IDADE_DIAS is None, (
        "decisao L esta em aberto: nao invente 60 nem 180. Esse numero decide "
        "quando o vendedor refaz a coleta, e ninguem o decidiu."
    )


def test_marcador_aparece_para_cada_decisao_aberta() -> None:
    """§5.12: o furo fica VISIVEL na interface, nao escondido."""
    from src.componentes import marcador_decisao_aberta as aberto

    letras = {letra for letra, _ in aberto.decisoes_abertas_ativas()}
    assert {"F", "G", "I", "J", "L"} <= letras


def test_texto_da_rampa_na_faixa_de_premissas() -> None:
    from src.componentes import marcador_decisao_aberta as aberto

    texto = aberto.texto_premissas_rampa()
    assert texto is not None
    assert "⚠️" in texto
    assert "não aplicadas" in texto

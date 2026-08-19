"""T6, T7, T8 — as regras de plausibilidade (DESIGN §6.1.8).

O ponto central destes tres: NENHUMA regra bloqueia o calculo, e NADA aparece
na area visivel ao cliente. "Um numero implausivel exibido com aviso discreto
ainda serve a conversa; um bloqueio na frente do cliente encerra a cena."
"""

from __future__ import annotations

import pytest

from testes.conftest import entradas_do_caso, esperado
from src import formato, plausibilidade
from src.calculo import calcular


# Marca exclusiva da regra R1. Nao use "carga de" como substring: ela casa
# tambem com "carga DEsligada" do R1b, e o teste passa a afirmar o contrario
# do que pretende.
MARCA_R1 = "veículos por consultor por dia"


def _faixa(nome_do_caso: str) -> list[str]:
    entradas = entradas_do_caso(nome_do_caso)
    return plausibilidade.avaliar(entradas, calcular(entradas))


def test_T6_carga_implausivel_avisa_sem_bloquear() -> None:
    entradas = entradas_do_caso("T6")
    resultado = calcular(entradas)
    e = esperado("T6")

    carga = (
        entradas.passagens_por_ponto
        / entradas.consultores_por_ponto
        / entradas.dias_uteis
    )
    assert carga == pytest.approx(e["carga"], abs=0.01)
    assert formato.decimal(carga) == "34,1"

    linhas = plausibilidade.avaliar(entradas, resultado)
    assert any(e["faixa_contem"] in linha for linha in linhas), linhas

    # O CALCULO NAO E BLOQUEADO: o resultado continua completo.
    assert resultado.anual is not None
    assert resultado.estado == "E3_completo"


def test_T6_nada_muda_na_area_visivel_ao_cliente() -> None:
    """E4 e "identico a E3 na area visivel ao cliente. A unica diferenca esta
    na faixa do vendedor.\""""
    from dataclasses import replace

    implausivel = entradas_do_caso("T6")
    plausivel = replace(implausivel, consultores_por_ponto=40)

    r_impl, r_plaus = calcular(implausivel), calcular(plausivel)

    # Mesmas entradas de margem => resultado identico. `consultores` nao entra
    # em nenhuma conta de margem.
    assert r_impl.anual == pytest.approx(r_plaus.anual)
    assert r_impl.estado == r_plaus.estado

    # A diferenca vive SO na faixa.
    assert plausibilidade.avaliar(implausivel, r_impl) != plausibilidade.avaliar(
        plausivel, r_plaus
    )


def test_T7_carga_plausivel_nao_dispara() -> None:
    entradas = entradas_do_caso("T7")
    e = esperado("T7")

    carga = (
        entradas.passagens_por_ponto
        / entradas.consultores_por_ponto
        / entradas.dias_uteis
    )
    assert carga == pytest.approx(e["carga"], abs=0.01)

    linhas = _faixa("T7")
    assert not any(MARCA_R1 in linha for linha in linhas), linhas


def test_T7_totais_derivados() -> None:
    """§5.1 / §1.3 do plano — o total derivado e o que impede a conta errada
    de ser dita em voz alta."""
    entradas = entradas_do_caso("T7")
    e = esperado("T7")

    assert (
        formato.total_derivado_passagens(
            entradas.passagens_por_ponto, entradas.pontos_de_venda
        )
        == e["total_passagens_texto"]
    )
    assert (
        formato.total_derivado_consultores(
            entradas.consultores_por_ponto, entradas.pontos_de_venda
        )
        == e["total_consultores_texto"]
    )


def test_T7_derivado_aparece_mesmo_com_multiplicador_1() -> None:
    """§5.1: "Sumir com ele quando o valor e trivial ensina o cliente a nao
    procura-lo quando deixa de ser.\""""
    assert formato.total_derivado_passagens(300, 1) == (
        "→ 300 passagens por mês no total"
    )


def test_T8_verificacao_desligada_sem_valor_inventado() -> None:
    """R1b — a regra NAO e avaliada com valor inventado."""
    linhas = _faixa("T8")
    assert any(esperado("T8")["faixa_contem"] in linha for linha in linhas), linhas
    assert not any(MARCA_R1 in linha for linha in linhas), linhas


def test_R2_custo_acima_do_preco() -> None:
    from dataclasses import replace

    entradas = replace(entradas_do_caso("T1"), custo_dianteiro=300.0)
    linhas = plausibilidade.avaliar(entradas, calcular(entradas))
    assert any("custo acima do preço no dianteiro" in linha for linha in linhas)


def test_R3_margem_negativa_avisa() -> None:
    linhas = _faixa("T3")
    assert any("margem do refil está negativa" in linha for linha in linhas), linhas


def test_R4_traseiro_fora_da_conta_quando_meio_informado() -> None:
    """Dispara quando UM dos dois foi informado — sinal de intencao de incluir."""
    from dataclasses import replace

    meio = replace(entradas_do_caso("T1"), custo_traseiro=None)
    linhas = plausibilidade.avaliar(meio, calcular(meio))
    assert any("traseiro fora da conta" in linha for linha in linhas), linhas

    # Com os DOIS vazios, o traseiro simplesmente nao faz parte da proposta.
    nenhum = replace(
        entradas_do_caso("T1"), preco_traseiro=None, custo_traseiro=None
    )
    linhas = plausibilidade.avaliar(nenhum, calcular(nenhum))
    assert not any("traseiro fora da conta" in linha for linha in linhas)


def test_R5_coeficientes_provisorios_sempre_declarados() -> None:
    """Enquanto I e J estiverem abertas, a ausencia e DECLARADA."""
    linhas = _faixa("T1")
    assert any(
        "rampa e sazonalidade não aplicadas" in linha for linha in linhas
    ), linhas


def test_avisos_simultaneos_viram_linhas_separadas() -> None:
    """§5.9: "Nunca um contador, nunca um badge.\""""
    from dataclasses import replace

    entradas = replace(
        entradas_do_caso("T6"),
        custo_dianteiro=300.0,  # R2 e, por consequencia, R3
        preco_traseiro=None,
        custo_traseiro=None,
        cashback_traseiro=(5.0, 0.0, 0.0),  # R6: traseiro fora da conta
    )
    linhas = plausibilidade.avaliar(entradas, calcular(entradas))
    assert len(linhas) >= 3
    assert all(isinstance(linha, str) and linha for linha in linhas)

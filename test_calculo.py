"""T1-T5, T9-T12 — os casos de calculo do DESIGN §11.3.

"Estes numeros sao de teste. NENHUM DELES VIRA DEFAULT NO CODIGO."
"""

from __future__ import annotations

import pytest

from testes.conftest import entradas_do_caso, esperado
from src import formato
from src import parametros as P
from src.calculo import calcular, curva_sensibilidade, preset_ativo, rotulo_do_resultado

CENTAVO = 0.005


def test_T1_cenario_base() -> None:
    r = calcular(entradas_do_caso("T1"))
    e = esperado("T1")

    assert r.passagens_totais == e["passagens_totais"]
    assert r.pares_dianteiros == e["pares_dianteiros"]
    assert r.unidades_traseiras == e["unidades_traseiras"]
    assert r.margem_dianteiro == pytest.approx(e["margem_dianteiro"], abs=CENTAVO)
    assert r.margem_traseiro == pytest.approx(e["margem_traseiro"], abs=CENTAVO)
    assert r.margem_refil == pytest.approx(e["margem_refil"], abs=CENTAVO)
    assert r.incremental_mensal == pytest.approx(e["incremental_mensal"], abs=CENTAVO)
    assert r.anual == pytest.approx(e["anual"], abs=CENTAVO)
    assert r.estado == e["estado"]
    assert formato.traducao_por_passagem(r.traducao_fracao) == e["traducao"]

    # A ancora nova: o que ele vende hoje.
    assert r.originais_por_mes == pytest.approx(e["originais_por_mes"])
    assert r.margem_unitaria_original == pytest.approx(
        e["margem_unitaria_original"], abs=CENTAVO
    )
    assert r.margem_atual == pytest.approx(e["margem_atual"], abs=CENTAVO)


def test_T1_traducao_vem_antes_do_anual_e_maior() -> None:
    """P2 / §5.5 — a regra de implementacao mais facil de inverter.

    Duas verificacoes, porque as duas podem falhar independentemente:
      1. a traducao e renderizada ANTES do anual, na ordem do script
      2. t-traducao >= 1,25 x t-anual
    """
    import inspect

    from src.componentes import bloco_resultado
    from src.css import T_ANUAL, T_TRADUCAO

    assert T_TRADUCAO >= 1.25 * T_ANUAL, (
        f"t-traducao ({T_TRADUCAO}) precisa ser >= 1,25 x t-anual ({T_ANUAL}). "
        f"Inverter e o erro de implementacao mais provavel desta tela."
    )

    fonte = inspect.getsource(bloco_resultado._resultado)
    assert fonte.index("st-traducao") < fonte.index("st-anual"), (
        "a traducao precisa ser renderizada ANTES do valor anual na ordem do "
        "script (§5.5, §6.1.2)"
    )


def test_T2_cashback_por_venda_nas_duas_categorias() -> None:
    """O cashback e R$ POR VENDA, com linha propria por categoria.

    E a ARMADILHA da §6.1.7: ele e pago pela Suicatech, saindo da margem DELA.
    Preencher ACRESCENTA uma linha ao resultado e NUNCA altera a manchete.
    "Se a implementacao subtrair cashback da margem exibida, ela inverteu o
    principal argumento comercial do bloco."
    """
    r = calcular(entradas_do_caso("T2"))
    e = esperado("T2")

    assert r.cashback_por_par_dianteiro == pytest.approx(
        e["cashback_por_par_dianteiro"], abs=CENTAVO
    )
    assert r.cashback_por_unidade_traseira == pytest.approx(
        e["cashback_por_unidade_traseira"], abs=CENTAVO
    )
    assert r.cashback_total == pytest.approx(e["cashback_total"], abs=CENTAVO)

    por_nome = dict(r.cashback_por_destinatario)
    for nome, valor in e["por_destinatario"].items():
        assert por_nome[nome] == pytest.approx(valor, abs=CENTAVO), nome

    # E a manchete NAO se move.
    assert r.incremental_mensal == pytest.approx(e["incremental_mensal"], abs=CENTAVO)
    assert r.anual == pytest.approx(e["anual"], abs=CENTAVO)
    assert rotulo_do_resultado(r) == e["rotulo"]
    assert "cashback" not in rotulo_do_resultado(r).lower()


def test_T2_cashback_do_traseiro_fora_da_conta_nao_conta() -> None:
    """Pagar cashback de venda que a simulacao nao contabiliza inflaria o valor
    prometido a equipe."""
    from dataclasses import replace

    entradas = replace(
        entradas_do_caso("T2"), preco_traseiro=None, custo_traseiro=None
    )
    r = calcular(entradas)
    # So o dianteiro: 90 pares x R$ 15,00.
    assert r.cashback_total == pytest.approx(1350.0, abs=CENTAVO)
    assert r.cashback_por_unidade_traseira == 0.0


def test_T3_margem_negativa() -> None:
    """O valor e exibido COM O SINAL, em tinta clara. Nada em vermelho."""
    r = calcular(entradas_do_caso("T3"))
    e = esperado("T3")
    assert r.margem_dianteiro == pytest.approx(e["margem_dianteiro"], abs=CENTAVO)
    assert r.incremental_mensal == pytest.approx(e["incremental_mensal"], abs=CENTAVO)
    assert r.anual == pytest.approx(e["anual"], abs=CENTAVO)
    assert r.estado == e["estado"]
    # O sinal aparece na formatacao.
    assert formato.moeda_agregada(r.anual).startswith("−")


def test_T3b_sem_custo_da_original_nao_diz_incremental() -> None:
    """A dependencia dura: sem margem da original nao existe incremental.

    O app NAO ASSUME um valor para a margem da palheta original, e o rotulo
    deixa de dizer "incremental" — nomear a conta errada e pior que nao nomear.
    """
    r = calcular(entradas_do_caso("T3b"))
    e = esperado("T3b")
    assert r.tem_margem_da_original is e["tem_margem_da_original"]
    assert r.incremental_mensal == pytest.approx(e["incremental_mensal"], abs=CENTAVO)
    assert rotulo_do_resultado(r) == e["rotulo"]
    assert "incremental" not in rotulo_do_resultado(r)
    assert r.margem_unitaria_original is None


def test_canibalizacao_nao_modelada_e_declarada() -> None:
    """A premissa mais favoravel possivel nao pode ficar implicita.

    O campo de substituicao saiu da interface (decisao do cliente, 11/08/2026).
    A consequencia — nenhuma venda de refil tira venda da original — e o risco 7
    do plano, e por isso `parametros` a declara e a faixa de premissas a exibe
    em toda simulacao.
    """
    from src.calculo import Entradas

    assert P.CANIBALIZACAO_MODELADA is False
    assert P.TEXTO_SEM_CANIBALIZACAO
    # E o campo nao existe mais nas entradas: nao ha lever escondida.
    assert not hasattr(Entradas(), "substituicao")


def test_curvas_comparadas_duas_linhas_e_a_distancia_e_o_incremental() -> None:
    """As duas linhas do grafico (pedido do cliente, 11/08/2026).

    A regra que mantem o grafico coerente com a manchete: a DISTANCIA entre as
    duas linhas tem de ser exatamente o incremental anual. Se divergirem, a
    tela se contradiz na frente do cliente (§5.11).
    """
    from src.calculo import curvas_comparadas

    entradas = entradas_do_caso("T1")
    r = calcular(entradas)
    com_refil, base = curvas_comparadas(entradas)

    assert base is not None, "com custo da original, a linha de base existe"
    # A base e a margem atual anualizada: 20 palhetas x R$ 189,00 x 12.
    assert base == pytest.approx(20 * 189.00 * 12, abs=CENTAVO)

    atual_x = entradas.aproveitamento_dianteiro * 100
    total_no_ponto = dict(com_refil)[atual_x]
    assert total_no_ponto - base == pytest.approx(r.anual, abs=CENTAVO), (
        "a distancia entre as linhas precisa ser o incremental da manchete"
    )


def test_curvas_comparadas_linha_base_e_constante() -> None:
    """A margem de continuar só com a original NAO depende do refil.

    Por isso ela e uma reta horizontal — e por isso o cruzamento com a outra
    linha responde "a partir de quanto de aproveitamento eu ganho trocando?".
    """
    from src.calculo import curvas_comparadas

    _, base = curvas_comparadas(entradas_do_caso("T1"))
    for pp in (0, 20, 60):
        from dataclasses import replace

        _, b = curvas_comparadas(
            replace(entradas_do_caso("T1"), aproveitamento_dianteiro=pp / 100)
        )
        assert b == pytest.approx(base, abs=CENTAVO)


def test_curvas_comparadas_sem_custo_da_original_volta_a_uma_linha() -> None:
    """Sem margem da original nao ha o que comparar, e o app NAO inventa."""
    from src.calculo import curvas_comparadas

    com_refil, base = curvas_comparadas(entradas_do_caso("T3b"))
    assert base is None
    assert com_refil, "a linha do refil continua existindo"


def test_aproveitamento_traseiro_e_independente_do_dianteiro() -> None:
    """§5.4 / risco n. 1: os dois nunca se acoplam, em nenhuma direcao."""
    from dataclasses import replace

    base = entradas_do_caso("T1")

    # Mudar o dianteiro nao mexe no traseiro.
    for pp in (0, 20, 45, 60):
        variante = replace(base, aproveitamento_dianteiro=pp / 100)
        assert variante.aproveitamento_traseiro == base.aproveitamento_traseiro

    # Mudar o traseiro nao mexe no dianteiro, e muda o resultado.
    maior = replace(base, aproveitamento_traseiro=0.20)
    assert maior.aproveitamento_dianteiro == base.aproveitamento_dianteiro
    assert calcular(maior).margem_traseiro > calcular(base).margem_traseiro


def test_T4_traseiro_nunca_derivado_do_dianteiro() -> None:
    """Preco do traseiro vazio => contribui R$ 0. Nunca estimado, nunca inferido."""
    r = calcular(entradas_do_caso("T4"))
    e = esperado("T4")
    assert r.margem_traseiro == pytest.approx(e["margem_traseiro"], abs=CENTAVO)
    assert r.incremental_mensal == pytest.approx(e["incremental_mensal"], abs=CENTAVO)
    assert r.anual == pytest.approx(e["anual"], abs=CENTAVO)
    assert r.traseiro_na_conta is e["traseiro_na_conta"]
    # A prova de que nao houve derivacao: o resultado e exatamente o do
    # dianteiro sozinho. Se houvesse divisao por 2 em algum lugar, MCt seria
    # 30 x (197,90/2 - 84,90/2) = 1.695,00 e o anual daria 142.380.
    assert r.margem_refil == pytest.approx(r.margem_dianteiro, abs=CENTAVO)


def test_T5_sem_operacao_nao_exibe_anual() -> None:
    """E1 — nenhum valor em R$, e nenhum campo recebe 0 como default."""
    r = calcular(entradas_do_caso("T5"))
    e = esperado("T5")
    assert r.estado == e["estado"]
    assert r.anual is None, "o valor anual nao pode existir sem as passagens"
    assert r.incremental_mensal is None
    # Nao existe default R$ 0 em lugar nenhum do caminho.
    assert r.margem_refil is None


def test_T5_grafico_nao_e_desenhado_sem_operacao() -> None:
    """§6.1.6 E1: "O grafico nao e desenhado.\""""
    entradas = entradas_do_caso("T5")
    # A curva nao produz ponto algum, porque cada ponto depende de `anual`.
    assert curva_sensibilidade(entradas) == []


def test_T9_preset_ativo_e_derivado() -> None:
    """Slider a 27% => NENHUM preset ativo, e `Ct` permanece em 10%."""
    e = esperado("T9")

    # Preset exato: ativo.
    assert preset_ativo(entradas_do_caso("T1")) == "realista"

    # Slider movido para 27%: nenhum botao aceso.
    entradas = entradas_do_caso("T9")
    assert preset_ativo(entradas) == e["preset_ativo"]
    # Mover o slider do dianteiro NAO altera o traseiro (risco n. 1 do plano).
    assert entradas.aproveitamento_traseiro == pytest.approx(
        e["aproveitamento_traseiro_permanece"]
    )


def test_T10_dominio_do_grafico_igual_ao_do_slider() -> None:
    """O marcador nunca sai do plot, nas duas extremidades."""
    lo, hi = P.SLIDER_DOMINIO
    assert [lo, hi] == esperado("T10")["dominio"]

    pontos = curva_sensibilidade(entradas_do_caso("T1"))
    xs = [x for x, _ in pontos]
    assert min(xs) == lo and max(xs) == hi

    # Nas duas extremidades o valor atual cai DENTRO do dominio plotado.
    for pp in (lo, hi):
        from dataclasses import replace

        entradas = replace(
            entradas_do_caso("T1"), aproveitamento_dianteiro=pp / 100
        )
        assert lo <= entradas.aproveitamento_dianteiro * 100 <= hi
        assert calcular(entradas).anual is not None


def test_T10_slider_dominio_cobre_todos_os_presets() -> None:
    """V5 — senao um preset joga o marcador para fora do grafico."""
    lo, hi = P.SLIDER_DOMINIO
    for preset in P.PRESETS:
        assert lo <= preset.dianteiro * 100 <= hi
        assert lo <= preset.traseiro * 100 <= hi


def test_T11_cashback_nao_desconta() -> None:
    """A armadilha da §6.1.7. Ligar o cashback ACRESCENTA linha, nunca subtrai."""
    sem = calcular(entradas_do_caso("T1"))
    com = calcular(entradas_do_caso("T11"))
    e = esperado("T11")

    assert com.incremental_mensal == pytest.approx(e["incremental_mensal"], abs=CENTAVO)
    assert com.anual == pytest.approx(e["anual"], abs=CENTAVO)
    # Identico ao caso sem cashback: nenhum efeito sobre a margem.
    assert com.incremental_mensal == pytest.approx(sem.incremental_mensal, abs=CENTAVO)
    # A linha de exibicao existe.
    assert com.cashback_total == pytest.approx(e["cashback_total"], abs=CENTAVO)
    # E o rotulo NAO menciona cashback.
    assert rotulo_do_resultado(com) == e["rotulo"]
    assert "cashback" not in rotulo_do_resultado(com).lower()


def test_T12_rotulo_acompanha_a_conta() -> None:
    """O rotulo nomeia a conta que foi feita. Nunca "lucro".

    Comissao e imposto sairam da interface (absorvidos pelo Cashback), portanto
    nao existem mais variantes "apos comissao"/"apos impostos": um rotulo que
    anunciasse deducao inexistente seria pior que nenhum rotulo (§6.1.7).
    """
    from dataclasses import replace

    e = esperado("T12")
    base = entradas_do_caso("T1")

    assert rotulo_do_resultado(calcular(base)) == e["com_margem_da_original"]

    sem_margem = replace(base, custo_original=None)
    assert rotulo_do_resultado(calcular(sem_margem)) == e["sem_margem_da_original"]

    for entradas in (base, sem_margem):
        rotulo = rotulo_do_resultado(calcular(entradas))
        assert "lucro" not in rotulo.lower()
        assert "após" not in rotulo, (
            "nao existe mais deducao da margem exibida — nenhum rotulo pode "
            "anunciar uma"
        )


def test_nenhuma_deducao_altera_a_margem_exibida() -> None:
    """Nada mais desconta da margem: comissao e imposto sairam da interface.

    Este teste existe para o caso de alguem devolver uma deducao ao modelo sem
    devolver o rotulo correspondente — o que faria o app exibir um numero
    descontado com o rotulo de um numero bruto.
    """
    from dataclasses import replace

    base = entradas_do_caso("T1")
    r = calcular(base)
    assert r.incremental_mensal == pytest.approx(r.margem_refil, abs=CENTAVO)

    # Cashback cheio nas duas categorias: a margem nao se move um centavo.
    com_cashback = calcular(
        replace(
            base,
            cashback_dianteiro=(25.0, 10.0, 5.0),
            cashback_traseiro=(12.0, 4.0, 2.0),
        )
    )
    assert com_cashback.incremental_mensal == pytest.approx(
        r.incremental_mensal, abs=CENTAVO
    )
    assert com_cashback.cashback_total > 0


def test_curva_plota_a_mesma_grandeza_da_manchete() -> None:
    """§5.11: se divergirem, a tela se contradiz na frente do cliente."""
    entradas = entradas_do_caso("T1")
    r = calcular(entradas)
    pontos = dict(curva_sensibilidade(entradas))
    atual = entradas.aproveitamento_dianteiro * 100
    assert pontos[atual] == pytest.approx(r.anual, abs=CENTAVO)


def test_curva_nao_arrasta_o_traseiro() -> None:
    """§5.11: ao variar o dianteiro, o traseiro NAO acompanha."""
    from dataclasses import replace

    entradas = entradas_do_caso("T1")
    for pp in (0, 20, 60):
        variante = replace(entradas, aproveitamento_dianteiro=pp / 100)
        assert variante.aproveitamento_traseiro == entradas.aproveitamento_traseiro
        # A contribuicao do traseiro e constante ao longo da curva.
        assert calcular(variante).margem_traseiro == pytest.approx(
            calcular(entradas).margem_traseiro, abs=CENTAVO
        )


def test_E2_cenario_de_nao_fazer_nada() -> None:
    """§6.1.6 E2: Cd = 0 calcula normalmente. "Nada de errado.\""""
    from dataclasses import replace

    entradas = replace(
        entradas_do_caso("T1"),
        aproveitamento_dianteiro=0.0,
        aproveitamento_traseiro=0.0,
    )
    r = calcular(entradas)
    assert r.estado == "E2_sem_cenario"
    assert r.incremental_mensal == pytest.approx(0.0, abs=CENTAVO)
    assert r.anual == pytest.approx(0.0, abs=CENTAVO)

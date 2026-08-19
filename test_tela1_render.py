"""Renderizacao da Tela 1 — verifica o que de fato chega na tela.

Usa streamlit.testing.AppTest, que roda o script inteiro headless. E o unico
lugar em que a ORDEM DE LEITURA e a AUSENCIA de componentes proibidos podem ser
verificadas no artefato renderizado, e nao apenas no codigo-fonte.

Estes testes sao mais lentos que os de calculo. Rode `pytest testes/ -k render`
para so eles.
"""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

from testes.conftest import CASOS

TEMPO = 120


def _app() -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=TEMPO)
    at.run()
    return at


def _blocos(at: AppTest) -> list[str]:
    """Os blocos de markdown renderizados, SEM a folha de estilo.

    A folha da camada B e injetada como markdown e contem os nomes de todas as
    classes e todos os tokens de cor. Incluir ela numa busca por "st-anual" ou
    por "#C8102E" faz o teste casar com a DEFINICAO do estilo em vez do uso —
    foi assim que a primeira versao deste arquivo acusou vermelho num numero.
    """
    return [
        m.value
        for m in at.markdown
        if not m.value.lstrip().startswith("<style>")
    ]


def _texto(at: AppTest) -> str:
    """Todo o conteudo renderizado, concatenado, sem a folha de estilo."""
    return "\n".join(_blocos(at) + [c.value for c in at.caption])


def _preencher_dianteiro(at: AppTest) -> AppTest:
    """Preenche a operacao, a ancora e o DIANTEIRO, e aperta REALISTA.

    Isto NAO reproduz o T1 inteiro: preco e custo do TRASEIRO ficam vazios, e o
    resultado esperado aqui e o do T4 — traseiro FORA DA CONTA, R$ 122.040/ano.
    Foi este helper que me fez confundir T1 com T4 na primeira versao.
    """
    base = CASOS["base"]
    at.number_input(key="pontos_de_venda").set_value(base["pontos_de_venda"]).run()
    at.number_input(key="passagens_por_ponto").set_value(
        base["passagens_por_ponto"]
    ).run()
    at.number_input(key="palhetas_originais_mes").set_value(
        base["palhetas_originais_mes"]
    ).run()
    at.number_input(key="preco_original").set_value(base["preco_original"]).run()
    at.number_input(key="custo_original").set_value(base["custo_original"]).run()
    at.number_input(key="preco_dianteiro").set_value(base["preco_dianteiro"]).run()
    at.number_input(key="custo_dianteiro").set_value(base["custo_dianteiro"]).run()
    at.button(key="btn_preset_realista").click().run()
    return at


def _preencher_cenario_base(at: AppTest) -> AppTest:
    """O T1 COMPLETO: dianteiro + traseiro, ambos na conta."""
    base = CASOS["base"]
    _preencher_dianteiro(at)
    at.number_input(key="preco_traseiro").set_value(base["preco_traseiro"]).run()
    at.number_input(key="custo_traseiro").set_value(base["custo_traseiro"]).run()
    return at


# ---------------------------------------------------------------------------
# Estado inicial (E0/E1)
# ---------------------------------------------------------------------------


def test_render_app_sobe_sem_excecao() -> None:
    at = _app()
    assert not at.exception, at.exception


def test_render_estado_inicial_pede_a_operacao() -> None:
    """E1 (§6.1.6): no lugar do bloco de resultado, a pergunta que abre a
    conversa. §7.3: "roteiro de pitch, nao mensagem de erro."

    A pergunta agora e respondivel de cabeca por um gerente de pos-venda —
    passagens, quantas palhetas ele vende e a quanto — em vez da margem de
    contribuicao mensal com palhetas, que ninguem sabe de cor.
    """
    texto = _texto(_app())
    assert "Quantas passagens por mês esta oficina recebe?" in texto
    assert "quantas palhetas são vendidas" in texto
    assert "Preço original" in texto, (
        "o estado vazio precisa apontar para a aba onde o preco da original e "
        "conferido ao vivo"
    )


def test_render_estado_inicial_nao_exibe_zero_reais() -> None:
    """P9 / §6.1.9: nao existe default R$ 0, nem travessao no lugar de moeda."""
    texto = _texto(_app())
    for proibido in ("R$ 0,00", "R$ 0 por ano", "R$ 0 por mês"):
        assert proibido not in texto, f"encontrado {proibido!r} no estado inicial"


def test_render_estado_inicial_nenhum_preset_ativo() -> None:
    """§6.1.4: o campo 6 abre sem preset ativo."""
    at = _app()
    tipos = {b.proto.type for b in at.button if b.key.startswith("btn_preset_")}
    assert "primary" not in tipos, "nenhum preset pode abrir aceso"


def test_render_campos_sensiveis_abrem_vazios() -> None:
    """P3 / §5.2: value=None. Nenhum default, nenhum valor de demonstracao."""
    at = _app()
    for chave in ("preco_dianteiro", "custo_dianteiro", "preco_original", "custo_original"):
        assert at.number_input(key=chave).value is None, (
            f"{chave} abriu preenchido — o link e aberto e o custo de aquisicao "
            f"e o preco de venda da Suicatech"
        )


def test_render_legenda_do_campo_vazio_existe() -> None:
    """§5.2: sem a legenda, o campo vazio parece esquecido.

    "Sem ela, um vendedor novo preenche com o valor da ultima reuniao, ou o
    cliente pergunta se o app esta quebrado."
    """
    texto = _texto(_app())
    assert "negociados caso a caso" in texto
    assert "em branco de propósito" in texto


def test_render_exatamente_seis_campos_primarios() -> None:
    """§6.1.4 / §12: exatamente 6 campos editaveis fora de Ajustes avancados.

    Os 5 number_input primarios + o controle de aproveitamento (presets +
    slider), que conta como UM: e um controle sobre uma grandeza.
    """
    at = _app()
    primarios = {
        "pontos_de_venda",
        "passagens_por_ponto",
        "preco_dianteiro",
        "custo_dianteiro",
        "palhetas_originais_mes",
    }
    rotulados = {w.key for w in at.number_input}
    assert primarios <= rotulados
    # O sexto campo e o aproveitamento.
    assert at.slider(key="conv_dianteiro") is not None
    assert len(primarios) + 1 == 6


# ---------------------------------------------------------------------------
# Cenario completo (E3)
# ---------------------------------------------------------------------------


def test_render_T1_numeros_na_tela() -> None:
    """Os numeros do T1 aparecem formatados como a §6.1.5 manda."""
    at = _preencher_cenario_base(_app())
    assert not at.exception, at.exception
    texto = _texto(at)

    assert "R$ 141.480" in texto, "o valor anual precisa aparecer sem centavos"
    assert "R$ 11.790" in texto, "o valor mensal precisa aparecer"
    assert "3 a cada 10 carros que entram na oficina" in texto


def test_render_T4_traseiro_vazio_fica_fora_da_conta() -> None:
    """T4 na tela: sem preco do traseiro, so o dianteiro entra.

    R$ 122.040/ano, nao R$ 141.480. Se aparecesse 142.380 haveria derivacao
    por /2 em algum lugar (§5.13).
    """
    texto = _texto(_preencher_dianteiro(_app()))
    assert "R$ 122.040" in texto
    assert "R$ 10.170" in texto
    assert "R$ 141.480" not in texto
    assert "R$ 142.380" not in texto, "sinal de derivacao proibida do traseiro"


def test_render_traducao_vem_antes_e_maior_que_o_anual() -> None:
    """P2 / §5.5 / §12 — a regra mais facil de inverter.

    Verificado no ARTEFATO: a classe .st-traducao aparece antes de .st-anual no
    HTML renderizado, e nao apenas na ordem do codigo-fonte.
    """
    at = _preencher_cenario_base(_app())
    texto = _texto(at)

    assert "st-traducao" in texto and "st-anual" in texto
    assert texto.index("st-traducao") < texto.index("st-anual"), (
        "a traducao em escala humana precisa ser renderizada ANTES do valor anual"
    )


def test_render_rotulo_do_anual_descreve_a_conta() -> None:
    """§6.1.5: "ano cheio em regime" enquanto rampa e sazonalidade estao abertas."""
    texto = _texto(_preencher_cenario_base(_app()))
    assert "ano cheio em regime" in texto
    assert "primeiros 12 meses" not in texto


def test_render_faixa_de_premissas_sempre_visivel() -> None:
    """§5.6: aparece SEMPRE, inclusive com tudo em default.

    E a premissa mais favoravel possivel precisa estar DECLARADA. Com a
    canibalizacao fora do modelo, essa premissa e "todo refil e venda nova" — o
    risco 7 do plano. O cliente tem que poder ve-la.
    """
    for at in (_app(), _preencher_cenario_base(_app())):
        texto = _texto(at)
        assert "st-premissas" in texto, "a faixa de premissas precisa existir"
        assert "sem canibalização" in texto, (
            "a premissa mais favoravel nao pode ficar implicita"
        )
        assert "venda nova" in texto


def test_render_procedencia_do_traseiro_derivada_nao_carteira() -> None:
    """§5.7 — a mitigacao do risco n. 1 do plano, na tela.

    Com o preset PESSIMISTA, o traseiro (7%) e DERIVADO. Ele nunca pode sair
    marcado como carteira.
    """
    at = _preencher_cenario_base(_app())
    at.number_input(key="preco_traseiro").set_value(99.0).run()
    at.number_input(key="custo_traseiro").set_value(45.0).run()
    at.button(key="btn_preset_pessimista").click().run()

    texto = _texto(at)
    assert "≈ derivado" in texto, (
        "o traseiro pessimista e derivacao por proporcao, nao medicao"
    )
    assert "não medido" in texto


def test_render_marcador_de_decisao_aberta_visivel() -> None:
    """§5.12: o furo fica VISIVEL, em vez de um chute virar verdade."""
    texto = _texto(_preencher_cenario_base(_app()))
    assert "⚠️" in texto
    assert "não aplicadas" in texto


def _preencher_cashback(at: AppTest) -> AppTest:
    """R$ 10 / 3 / 2 por par dianteiro, como no T2."""
    for chave, valor in zip(("cashback_d_0", "cashback_d_1", "cashback_d_2"),
                            (10.0, 3.0, 2.0)):
        at.number_input(key=chave).set_value(valor).run()
    return at


def test_render_cashback_nao_muda_o_numero() -> None:
    """T11 na tela: preencher o cashback ACRESCENTA linha, nunca subtrai."""
    at = _preencher_cenario_base(_app())
    antes = _texto(at)
    assert "R$ 141.480" in antes

    _preencher_cashback(at)
    depois = _texto(at)

    assert "R$ 141.480" in depois, "o valor nao pode mudar com o cashback preenchido"
    assert "pago pela Suicatech" in depois
    assert "não sai da sua margem" in depois
    # 90 pares x R$ 15,00 = R$ 1.350/mes
    assert "R$ 1.350" in depois


def test_render_cashback_mostra_o_rateio_por_destinatario() -> None:
    """O vendedor promete um valor a cada parte; a tela mostra qual."""
    at = _preencher_cashback(_preencher_cenario_base(_app()))
    texto = _texto(at).lower()
    for nome in ("consultor", "gerente", "marketing"):
        assert nome in texto, nome


def test_render_rotulo_nunca_menciona_cashback() -> None:
    """§6.1.7 / §12: "cashback" nunca aparece no rotulo do resultado."""
    at = _preencher_cashback(_preencher_cenario_base(_app()))

    # `_blocos` exclui a folha de estilo — ela tem um comentario de CSS com a
    # palavra "cashback" e casaria com a busca.
    for bloco in _blocos(at):
        if "st-rotulo-resultado" in bloco:
            assert "cashback" not in bloco.lower()


def test_render_resultado_negativo_sem_vermelho() -> None:
    """T3 na tela: valor com sinal, em tinta clara. NADA em vermelho.

    Com o custo do dianteiro acima do preco, a margem fica negativa. O plano
    §1.1 avisa que isso e possivel, e o app nao esconde.
    """
    at = _preencher_cenario_base(_app())
    at.number_input(key="custo_dianteiro").set_value(250.0).run()

    texto = _texto(at)
    assert "−R$ 36.828" in texto, "o negativo precisa aparecer com o sinal"
    # Nenhum componente de alerta (§3.1.2, §5.9).
    assert not at.error
    assert not at.warning
    # E nenhum uso do vermelho da marca num numero de resultado (§3.1, §13.1):
    # "numero financeiro em vermelho le como prejuizo".
    for bloco in _blocos(at):
        if "st-anual" in bloco or "st-mensal" in bloco:
            assert "C8102E" not in bloco, f"vermelho num numero: {bloco[:120]}"
            assert "color:" not in bloco, f"cor inline num numero: {bloco[:120]}"


def test_render_nenhum_componente_de_alerta_em_nenhum_estado() -> None:
    """§5.9 — regra absoluta, verificada no artefato renderizado."""
    cenarios = [
        _app(),
        _preencher_cenario_base(_app()),
    ]
    # Cenario implausivel (T6) tambem nao pode produzir caixa.
    at = _preencher_cenario_base(_app())
    at.number_input(key="passagens_por_ponto").set_value(1500.0).run()
    at.number_input(key="consultores_por_ponto").set_value(2.0).run()
    cenarios.append(at)

    for i, at in enumerate(cenarios):
        assert not at.error, f"cenario {i}: st.error na tela"
        assert not at.warning, f"cenario {i}: st.warning na tela"
        assert not at.exception, f"cenario {i}: {at.exception}"


def test_render_aviso_de_plausibilidade_so_na_faixa() -> None:
    """T6 na tela: o aviso vive na faixa do vendedor, e o resultado permanece."""
    at = _preencher_cenario_base(_app())
    at.number_input(key="passagens_por_ponto").set_value(1500.0).run()
    at.number_input(key="consultores_por_ponto").set_value(2.0).run()

    texto = _texto(at)
    assert "veículos por consultor por dia" in texto
    # O aviso esta DENTRO da faixa, nao solto na tela.
    faixas = [m.value for m in at.markdown if "st-faixa-vendedor" in m.value]
    assert faixas, "a faixa do vendedor precisa existir"
    assert any("por consultor por dia" in f for f in faixas)
    # E o calculo NAO foi bloqueado.
    assert "por ano" in texto


def test_render_ajustes_avancados_abre_fechado() -> None:
    """§5.10: fechado por padrao, SEMPRE, a cada carga da pagina."""
    at = _app()
    avancados = [e for e in at.expander if "Ajustes avançados" in e.label]
    assert avancados, "o expander de avancados precisa existir"
    # O estado vem no proto; AppTest nao expoe `.expanded` no elemento.
    assert not avancados[0].proto.expanded


def test_render_tabela_gemea_da_curva_existe() -> None:
    """§5.11 / §9: o gemeo em tabela e OBRIGATORIO — substitui o tooltip."""
    at = _preencher_cenario_base(_app())
    rotulos = [e.label for e in at.expander]
    assert any("números da curva" in r for r in rotulos), rotulos


def test_render_painel_de_formula_existe_e_abre_fechado() -> None:
    """§5.8: prova em um toque, fechada por padrao."""
    at = _preencher_cenario_base(_app())
    painel = [e for e in at.expander if "De onde vêm" in e.label]
    assert painel, [e.label for e in at.expander]
    assert not painel[0].proto.expanded


def test_render_novo_cliente_limpa_os_campos_sensiveis() -> None:
    """§5.2: limpa preco, custo e ancora SEM CONFIRMACAO."""
    at = _preencher_cenario_base(_app())
    assert at.number_input(key="preco_dianteiro").value == 197.90

    at.button(key="btn_novo_cliente").click().run()

    for chave in ("preco_dianteiro", "custo_dianteiro", "preco_original", "custo_original"):
        assert at.number_input(key=chave).value is None, (
            f"{chave} sobreviveu ao `novo cliente`"
        )


def test_render_traseiro_vazio_declarado_na_faixa_de_premissas() -> None:
    """§5.13: traseiro sem preco contribui R$ 0 e a faixa DECLARA isso.

    Usa `_preencher_dianteiro` de proposito: com o traseiro preenchido a
    declaracao nao deve aparecer, e ela e o objeto deste teste.
    """
    texto = _texto(_preencher_dianteiro(_app()))
    assert "traseiro: preço não informado — fora da conta" in texto

    # E com o traseiro na conta, a declaracao SOME e o valor dele entra.
    texto_completo = _texto(_preencher_cenario_base(_app()))
    assert "traseiro: preço não informado" not in texto_completo
    assert "R$ 141.480" in texto_completo


def test_render_bloco_de_investimento_ausente() -> None:
    """§10-G: "o bloco nao existe na Fase 1" — ausente, nao desabilitado.

    "Um campo desabilitado com rotulo promete uma funcionalidade que nao existe;
    ausencia nao promete nada."

    A partir de 11/08/2026 nem a DECLARACAO de ausencia esta na Tela 1 (decisao
    do cliente). A decisao G continua visivel onde ela vale algo: no bloco
    "menos codigo na prateleira" da Tela 3 — coberto por cdp_final.py.
    """
    at = _preencher_cenario_base(_app())
    texto = _texto(at).lower()

    # Nenhum campo editavel de investimento, nem desabilitado...
    rotulos = [
        (w.label or "").lower()
        for w in list(at.number_input) + list(at.slider) + list(at.toggle)
    ]
    # ...e nenhuma mencao a eles em texto de tela.
    for proibido in ("payback", "capital de giro", "pedido mínimo", "frete"):
        assert not any(proibido in r for r in rotulos), (
            f"campo de investimento '{proibido}' existe na interface (decisão G)"
        )
        assert proibido not in texto, (
            f"'{proibido}' nao deve mais ser mencionado na Tela 1"
        )


def test_render_a_palavra_lucro_nunca_aparece() -> None:
    """P12 — no artefato renderizado, em todos os estados."""
    for at in (_app(), _preencher_cenario_base(_app())):
        assert "lucro" not in _texto(at).lower()

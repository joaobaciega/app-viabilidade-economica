"""Renderizacao da Tela 1 — verifica o que de fato chega na tela.

Usa streamlit.testing.AppTest, que roda o script inteiro headless. E o unico
lugar em que a ORDEM DE LEITURA e a AUSENCIA de componentes proibidos podem ser
verificadas no artefato renderizado, e nao apenas no codigo-fonte.

Estes testes sao mais lentos que os de calculo. Rode `pytest testes/ -k render`
para so eles.
"""

from __future__ import annotations

import re

import pytest
from streamlit.testing.v1 import AppTest

from src import parametros as P
from testes.checagens import RAIZ
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


def _texto_sem_a_curva(at: AppTest) -> str:
    """O conteudo renderizado SEM a tabela gemea da curva.

    Serve as buscas por valor PROIBIDO, e pelo mesmo motivo que `_blocos`
    exclui a folha de estilo: a busca casaria com a coisa errada.

    O gemeo em tabela (§5.11) varre o dominio INTEIRO do aproveitamento, de 5
    em 5 pontos percentuais. Qualquer numero sentinela — inclusive os que
    denunciariam a derivacao proibida do traseiro (§5.13) — aparece em algum
    ponto dessa varredura por coincidencia aritmetica, com o resultado
    perfeitamente correto. Ali ele e um ponto da curva, nao a manchete.

    Enquanto a tabela era um `st.dataframe` isso nao acontecia: a canvas do
    dataframe nao entrava no markdown renderizado. A tabela propria entra — e
    e melhor assim, porque agora e texto de verdade, conferivel e copiavel.
    """
    return "\n".join(
        [bloco for bloco in _blocos(at) if 'class="st-tabela"' not in bloco]
        + [c.value for c in at.caption]
    )


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

    # O CENARIO VEM DOS SLIDERS, e nao de `btn_preset_realista`.
    #
    # Antes este helper clicava REALISTA. Em D21 o realista virou 40%/10%
    # enquanto o bloco `base` de casos.json seguiu em 30%/10% — os numeros de
    # ouro dos 16 casos NAO foram recalculados de proposito, para nao refazer a
    # mao a aritmetica de T1, T2, T3, T4, T11 e de todo o test_pdf. Ajustar os
    # sliders chega ao mesmo estado sem depender de qual preset e qual.
    #
    # Em D31 (22/09/2026) o realista voltou a 30%/10% e os dois coincidem de
    # novo. MANTER OS SLIDERS MESMO ASSIM: a coincidencia e do momento, e
    # clicar no preset faria dezenas de testes de numero dependerem de um valor
    # que o cliente revisa quando quer.
    #
    # Que apertar REALISTA escreve o par medido do preset e coberto por
    # `test_render_preset_realista_escreve_o_par_medido`, que le de P.PRESETS.
    at.slider(key="conv_dianteiro").set_value(
        int(round(base["aproveitamento_dianteiro"] * 100))
    ).run()
    at.slider(key="conv_traseiro").set_value(
        int(round(base["aproveitamento_traseiro"] * 100))
    ).run()

    return _revelar(at)


def _revelar(at: AppTest) -> AppTest:
    """Aperta "Mostrar Resultado" (D21). Sem isso nao existe numero na tela.

    A tela abre so com os campos: durante o preenchimento nada e calculado e
    nada aparece. O botao so habilita com os seis obrigatorios preenchidos, e
    todo teste que verifica numero na tela precisa passar por aqui.

    Idempotente: com o resultado ja visivel o botao nao existe mais (o lugar
    dele e ocupado por "Esconder resultado"), e o helper nao faz nada.
    """
    if any(b.key == "btn_mostrar" for b in at.button):
        at.button(key="btn_mostrar").click().run()
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


def test_render_estado_inicial_abre_so_com_os_campos() -> None:
    """D21: a tela abre com os campos e o botao desabilitado. Nenhum numero.

    SUBSTITUI `test_render_estado_inicial_pede_a_operacao`, que exigia o
    roteiro de pitch do estado vazio dentro do bloco de resultado ("Quantas
    passagens por mês esta oficina recebe?", §6.1.6 e §7.3: "o vazio desta tela
    nao e uma falha, e a abertura da conversa"). Esse roteiro deixou de existir:
    o vazio da tela agora e a propria area de campos.

    O que este teste trava no lugar, e que e o essencial do modelo novo:
      1. o botao existe desde a primeira carga — e ele que ensina o modelo da
         tela ("preencha e aperte"). Um botao que aparece do nada quando o
         sexto campo e preenchido nao ensinaria nada
      2. ele comeca DESABILITADO
      3. o que falta e DITO, sem componente de alerta e sem vocabulario de erro
      4. nenhum valor em R$ na tela antes do toque
    """
    at = _app()

    botoes = {b.key: b for b in at.button}
    assert "btn_mostrar" in botoes, "o botao precisa existir na primeira carga"
    assert botoes["btn_mostrar"].proto.disabled, (
        "o botao nao pode abrir habilitado — nao ha o que mostrar"
    )

    texto = _texto(at)
    assert "Falta preencher" in texto
    assert "passagens por mês" in texto

    assert "R$" not in texto, (
        "nenhum valor em R$ pode aparecer antes do toque explicito:\n" + texto[:400]
    )
    assert not at.error and not at.warning


def test_render_botao_habilita_quando_os_obrigatorios_estao_preenchidos() -> None:
    """D21 — o gate, campo por campo.

    O traseiro NAO entra na conta de obrigatorios: vazio ali significa "fora da
    conta" e e um estado legitimo (§5.13). Se algum dia ele passar a ser
    exigido, este teste reprova — e e essa a intencao.
    """
    at = _app()
    base = CASOS["base"]

    obrigatorios = (
        "passagens_por_ponto",
        "palhetas_originais_mes",
        "preco_original",
        "custo_original",
        "preco_dianteiro",
        "custo_dianteiro",
    )

    for i, chave in enumerate(obrigatorios):
        assert at.button(key="btn_mostrar").proto.disabled, (
            f"o botão habilitou faltando {len(obrigatorios) - i} campo(s)"
        )
        at.number_input(key=chave).set_value(base[chave]).run()

    assert not at.button(key="btn_mostrar").proto.disabled, (
        "com os seis obrigatórios preenchidos o botão precisa habilitar — o "
        "traseiro é opcional de propósito"
    )
    assert at.number_input(key="preco_traseiro").value is None


def test_render_resultado_so_aparece_depois_do_toque() -> None:
    """D21: preencher NAO revela. O resultado espera o botao."""
    at = _app()
    base = CASOS["base"]
    for chave in (
        "passagens_por_ponto",
        "palhetas_originais_mes",
        "preco_original",
        "custo_original",
        "preco_dianteiro",
        "custo_dianteiro",
    ):
        at.number_input(key=chave).set_value(base[chave]).run()

    assert "st-cartao-valor" not in _texto(at), (
        "com tudo preenchido e sem clique, nenhum número pode estar na tela"
    )

    at.button(key="btn_mostrar").click().run()
    assert "st-cartao-valor" in _texto(at)


def test_render_resultado_esconde_ao_apagar_um_obrigatorio() -> None:
    """D21: o resultado nao sobrevive a entrada que deixou de existir.

    Sem isso, apagar as passagens deixaria na tela um numero que a entrada
    atual nao produz mais — pior do que nao mostrar nada.
    """
    at = _preencher_cenario_base(_app())
    assert "st-cartao-valor" in _texto(at)

    at.number_input(key="passagens_por_ponto").set_value(None).run()

    assert "st-cartao-valor" not in _texto(at)
    assert at.button(key="btn_mostrar").proto.disabled
    assert "Falta preencher" in _texto(at)


def test_render_esconder_resultado_nao_apaga_campo() -> None:
    """"Esconder resultado" volta ao pitch inicial sem limpar nada.

    E o oposto de `novo cliente`, que apaga preco, custo e ancora.
    """
    at = _preencher_cenario_base(_app())
    at.button(key="btn_esconder").click().run()

    assert "st-cartao-valor" not in _texto(at)
    assert at.number_input(key="preco_dianteiro").value == CASOS["base"][
        "preco_dianteiro"
    ]
    # E o botao de mostrar volta, habilitado — nada foi perdido.
    assert not at.button(key="btn_mostrar").proto.disabled


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

    # PRECO TABELADO (D21). O texto dizia "negociados caso a caso"; o cliente
    # corrigiu — o preco do refil e de tabela, e nenhum texto da tela pode
    # sugerir negociacao por cliente.
    assert "caso a caso" not in texto, (
        "o preço do refil é tabelado — nenhum texto pode dizer que é negociado "
        "caso a caso"
    )
    assert "tabela Suicatech vigente" in texto
    # E a consequencia de deixar vazio continua declarada, que e o que a §5.2
    # queria: o campo vazio nao pode parecer esquecido.
    assert "fora da conta" in texto
    assert "nunca estimado" in texto


def test_render_todos_os_campos_estao_na_superficie_primaria() -> None:
    """D21: nada de campo escondido. SUBSTITUI o teto de seis da §6.1.4.

    O teste antigo (`test_render_exatamente_seis_campos_primarios`) afirmava o
    teto de "exatamente seis campos editaveis visiveis fora de Ajustes
    avancados" — e, na pratica, nao contava campo nenhum: ele verificava um
    subconjunto e terminava em `assert 5 + 1 == 6`, que e verdade sempre. O
    teto ja estava rompido por D8 e foi abandonado por D21.

    O que este teste trava agora: TODOS os campos, inclusive os oito que
    moravam no expander, estao alcancaveis sem abrir nada.
    """
    at = _app()
    chaves = {w.key for w in at.number_input}

    obrigatorios = {
        "passagens_por_ponto",
        "palhetas_originais_mes",
        "preco_original",
        "custo_original",
        "preco_dianteiro",
        "custo_dianteiro",
    }
    assert obrigatorios <= chaves, obrigatorios - chaves

    opcionais = {"pontos_de_venda", "preco_traseiro", "custo_traseiro"}
    assert opcionais <= chaves, opcionais - chaves

    # Os oito que vinham de Ajustes avancados: dois de operacao e a grade 2x3.
    dos_avancados = {"consultores_por_ponto", "dias_uteis"} | {
        f"cashback_{lado}_{i}" for lado in ("d", "t") for i in range(3)
    }
    assert dos_avancados <= chaves, (
        "os campos que moravam no expander precisam estar na superficie "
        f"primaria: faltam {sorted(dos_avancados - chaves)}"
    )

    # E os dois controles de aproveitamento continuam existindo, um por
    # categoria — nunca um so acoplando as duas (risco n. 1 do plano).
    assert at.slider(key="conv_dianteiro") is not None
    assert at.slider(key="conv_traseiro") is not None


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

    # Os dois numeros que D21 acrescentou. O faturamento mensal do T1 e
    # R$ 20.781 — o mesmo valor que docs/DIVERGENCIAS.md §5 registra como
    # medido no navegador — e o cartao mostra o anual, 12x isso.
    assert "R$ 249.372" in texto, "o faturamento adicional anual"
    assert "R$ 20.781" in texto, "o faturamento adicional mensal"

    # E o mark up sai em PERCENTUAL desde D27 — era "2,1×".
    #
    # 108%, e nao 208%: o mark up e o ACRESCIMO sobre o custo, e vender a duas
    # vezes o custo e 100%, nao 200%. E nao e 52%, que seria a MARGEM
    # percentual — outra conta, dividida pelo faturamento. O apoio do cartao
    # existe para impedir essa troca, e por isso ele e verificado aqui junto.
    cartoes = [b for b in _blocos(at) if "Mark up da operação" in b]
    assert cartoes, "o cartão de mark up precisa existir"
    assert "108%" in cartoes[0], cartoes[0]
    assert "×" not in cartoes[0], "o mark up deixou de ser múltiplo em D27"
    assert "custo) ÷ custo" in cartoes[0], (
        "o cartão precisa nomear a conta: sem ela, 108% ao lado de duas colunas "
        "de reais lê como margem percentual"
    )


def test_render_T4_traseiro_vazio_fica_fora_da_conta() -> None:
    """T4 na tela: sem preco do traseiro, so o dianteiro entra.

    R$ 122.040/ano, nao R$ 141.480. Se aparecesse 142.380 haveria derivacao
    por /2 em algum lugar (§5.13).

    As duas buscas por valor proibido rodam sobre o texto SEM a tabela da
    curva: lá dentro o dominio inteiro do aproveitamento esta tabulado, e um
    dos pontos da varredura cai em R$ 142.380 sem que nada esteja derivado.
    Ver `_texto_sem_a_curva`.
    """
    at = _preencher_dianteiro(_app())
    texto = _texto(at)
    assert "R$ 122.040" in texto
    assert "R$ 10.170" in texto

    fora_da_curva = _texto_sem_a_curva(at)
    assert "R$ 141.480" not in fora_da_curva
    assert "R$ 142.380" not in fora_da_curva, (
        "sinal de derivacao proibida do traseiro"
    )


def test_render_ordem_do_resultado_no_artefato() -> None:
    """A ordem de leitura do resultado, verificada no ARTEFATO.

    Verificar no artefato e nao so na fonte importa porque em Streamlit a
    hierarquia visual E a ordem das chamadas: uma reordenacao acidental de
    colunas passaria por qualquer checagem de fonte e apareceria so aqui.

    D28 ACRESCENTOU A TRADUCAO DE VOLTA A TELA, e isso REVOGA a ultima
    assercao que este teste fazia. D21.2 tinha tirado "3 a cada 10 carros que
    entram na oficina" da Tela 1, e o teste anterior exigia a ausencia dela.
    Com a tela espelhando o PDF, ela volta — no MESMO cartao de apoio em que o
    documento a mostra, e nao mais como manchete de 48px. O que D21.2 decidiu
    (que ela nao ABRE o resultado) continua de pe; o que ela decidiu (que ela
    nao existe na tela) nao.
    """
    at = _preencher_cenario_base(_app())
    texto = _texto(at)

    # A ordem inteira do resultado, e nao so a dos tres numeros: e a mesma
    # sequencia que `apresentacao.Apresentacao` declara e o PDF imprime.
    sequencia = [
        "Faturamento adicional",
        "Margem de contribuição adicional",
        "Mark up da operação",
        "O que isso significa na oficina",
        "Nova margem com refil",
        "Margem de contribuição no ano: hoje e com o refil",
        "Os três cenários medidos na carteira",
        "Como o resultado varia com o aproveitamento",
        "As premissas desta simulação",
        "O que esta simulação ainda não considera",
    ]
    for rotulo in sequencia:
        assert rotulo in texto, rotulo

    posicoes = [texto.index(rotulo) for rotulo in sequencia]
    assert posicoes == sorted(posicoes), (
        "a ordem do resultado na tela precisa ser a mesma da montagem:\n"
        + "\n".join(
            f"  {p:>7}  {rotulo}" for p, rotulo in zip(posicoes, sequencia)
        )
    )

    # E a tradução está de volta, como cartão de apoio (D28).
    assert "3 a cada 10" in texto
    assert "carros que entram" in texto


def test_render_barras_a_geometria_fecha() -> None:
    """D29 — as alturas do gráfico de barras, conferidas na aritmética.

    O desenho tem DOIS sistemas de porcentagem, e trocá-los desalinha tudo sem
    quebrar nada: `pct_*` é fração do plot (a altura fixa da coluna) e manda na
    pilha e na régua do vão; `dentro_*` é fração da PILHA e manda nos segmentos
    empilhados. Com os dois iguais — que era a primeira versão — o rótulo do
    vão descolava da barra que ele mede.

    A pilha existe para o rótulo ficar colado no topo da barra. Com a base em
    4,8% do plot, "R$ 99.000" aparecia a 300 px do risco que nomeava; é o
    defeito que a captura do cliente mostrou.
    """
    import re

    at = _preencher_cenario_base(_app())
    barras = [b for b in _blocos(at) if "st-barras" in b]
    assert barras, "o gráfico de barras precisa existir"
    html = barras[0]

    def alturas(classe: str) -> list[float]:
        return [
            float(v)
            for v in re.findall(
                rf'class="[^"]*{classe}[^"]*" style="height:([\d.]+)%"', html
            )
        ]

    pilhas = alturas("st-barra-pilha")
    assert len(pilhas) == 2, "uma pilha por barra"
    assert pilhas[1] == pytest.approx(100.0), (
        "a barra mais alta ocupa o plot inteiro — é ela que dá a escala"
    )
    assert pilhas[0] < pilhas[1], "a barra de hoje é a menor no cenário base"

    # Dentro da pilha empilhada, os dois segmentos fecham 100%.
    inc = alturas("st-barra-inc")[0]
    base_dentro = alturas("st-barra-base")
    assert inc + base_dentro[-1] == pytest.approx(100.0, abs=0.02)

    # A base da barra 1 preenche a própria pilha: as duas bases têm a MESMA
    # altura em pixels, que é o que a nota afirma em palavras.
    assert base_dentro[0] == pytest.approx(100.0)
    assert pilhas[0] == pytest.approx(
        pilhas[1] * base_dentro[-1] / 100, abs=0.02
    ), "a base repetida precisa ter a mesma altura nas duas barras"

    # E a régua do vão mede exatamente o segmento vermelho, no plot.
    vao = float(
        re.search(r'st-barra-delta-vao" style="height:([\d.]+)%', html).group(1)
    )
    assert vao == pytest.approx(pilhas[1] - pilhas[0], abs=0.02)


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


def test_render_procedencia_do_traseiro_e_declarada_na_faixa() -> None:
    """§5.7 — a procedencia de CADA numero aparece na tela.

    O QUE MUDOU EM D21: com o preset PESSIMISTA, o traseiro era 7% e era
    DERIVADO do dianteiro pela mesma proporcao, e a tela era obrigada a marcar
    `≈ derivado` e "não medido" — apresentar derivacao com autoridade de medicao
    e o risco n. 1 do plano. O cliente informou em 27/08/2026 que as tres faixas
    do traseiro (5/10/18) sao medidas na carteira, e a marca de derivacao saiu
    porque nao ha mais derivacao.

    O que continua travado: a faixa de premissas DECLARA a procedencia do
    traseiro, qualquer que seja ela. O dia em que um preset voltar a ser
    derivado, este teste continua valendo e a marca reaparece.
    """
    at = _preencher_cenario_base(_app())
    at.number_input(key="preco_traseiro").set_value(99.0).run()
    at.number_input(key="custo_traseiro").set_value(45.0).run()
    at.button(key="btn_preset_pessimista").click().run()

    # `_blocos` exclui a folha de estilo: ela DEFINE `.st-premissas` e casaria
    # com a busca antes da faixa de verdade.
    faixas = [b for b in _blocos(at) if "st-premissas" in b]
    assert faixas, "a faixa de premissas precisa existir"
    faixa = faixas[0]

    assert "traseiro" in faixa
    assert "◆ carteira" in faixa, (
        "a procedência do traseiro precisa estar declarada na faixa"
    )
    assert "≈ derivado" not in faixa, (
        "nenhum preset é derivado desde D21 — se voltar a ser, a legenda de "
        "parametros.LEGENDA_PRESETS_TRASEIRO tem de voltar junto"
    )


def test_render_preset_realista_escreve_o_par_medido() -> None:
    """D21: REALISTA escreve o par medido nas DUAS grandezas, de uma vez.

    Um preset e um PAR medido: apertar o botao escreve as duas grandezas. Mover
    o slider do dianteiro, ao contrario, nunca toca no traseiro — e essa
    assimetria e a mitigacao do risco n. 1 do plano.

    OS SLIDERS SAO TIRADOS DO PRESET ANTES DO TOQUE, e isso e o teste e nao
    preparo. Desde D31 o realista voltou a 30%/10%, que e exatamente onde
    `_preencher_dianteiro` deixa os sliders (o bloco `base` de casos.json) — sem
    este deslocamento o teste passaria com `aplicar_preset` fazendo NADA, porque
    os valores ja estariam certos antes do clique. Foi por um triz.
    """
    realista = next(p for p in P.PRESETS if p.nome == "realista")
    fora_d = int(round(realista.dianteiro * 100)) + 7
    fora_t = int(round(realista.traseiro * 100)) + 3

    at = _preencher_dianteiro(_app())
    at.slider(key="conv_dianteiro").set_value(fora_d).run()
    at.slider(key="conv_traseiro").set_value(fora_t).run()
    assert at.slider(key="conv_dianteiro").value == fora_d, "preparo do teste"

    at.button(key="btn_preset_realista").click().run()

    assert at.slider(key="conv_dianteiro").value == int(
        round(realista.dianteiro * 100)
    )
    assert at.slider(key="conv_traseiro").value == int(
        round(realista.traseiro * 100)
    )


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


def test_render_cashback_todo_campo_tem_rotulo_proprio_visivel() -> None:
    """D23 — o que substituiu a grade 2x3, e o que a grade nao conseguia dar.

    Na grade, quem nomeava os seis campos era um CABECALHO DE COLUNA. Isso
    obrigava a grade a ficar em linha em qualquer largura (D22), porque
    empilhada o cabecalho deixava de encabecar e os campos ficavam anonimos — e
    o preco era um campo de ~85px num celular de 390px.

    O que este teste trava: cada campo carrega o proprio rotulo, e o rotulo diz
    O DESTINATARIO E A CATEGORIA. So o destinatario nao bastaria: "Consultor"
    apareceria duas vezes, e quem chega no campo por leitor de tela nao le o
    titulo da linha de cima ao tabular (§9.6).
    """
    at = _app()
    rotulos = {
        w.key: w.label for w in at.number_input if w.key.startswith("cashback_")
    }
    assert len(rotulos) == 6, rotulos

    for chave, rotulo in rotulos.items():
        assert rotulo, f"{chave} ficou sem rótulo"
        categoria = "dianteiro" if "_d_" in chave else "traseiro"
        assert categoria in rotulo.lower(), (
            f"{chave} tem rótulo {rotulo!r}, que não diz a categoria — "
            f"empilhado no celular ele fica ambíguo com o outro grupo"
        )

    # Os tres destinatarios aparecem em cada categoria, e nenhum rotulo se
    # repete entre as duas.
    assert len(set(rotulos.values())) == 6, rotulos
    for nome in P.DESTINATARIOS_CASHBACK:
        assert sum(nome in r for r in rotulos.values()) == 2, nome


def test_render_cashback_subtotal_por_categoria() -> None:
    """D23: o chip que deixa conferir o combinado sem rolar de volta.

    Num celular os tres campos ficam um embaixo do outro e o primeiro sai da
    tela enquanto o ultimo e preenchido.
    """
    at = _preencher_cenario_base(_app())
    assert not [b for b in _blocos(at) if "no total, por par vendido" in b], (
        "sem cashback preenchido nao existe total de nada (§5.1)"
    )

    _preencher_cashback(at)  # 10 + 3 + 2

    chips = [b for b in _blocos(at) if "no total, por par vendido" in b]
    assert chips, "o subtotal do dianteiro precisa aparecer"
    assert "R$ 15,00" in chips[0], chips[0]
    assert 'class="st-derivado"' in chips[0], (
        "o subtotal usa o mesmo chip dos outros derivados (§5.1)"
    )

    # O traseiro segue vazio: o chip dele NAO aparece.
    assert not [b for b in _blocos(at) if "no total, por unidade vendida" in b]


def test_render_cashback_nao_depende_de_cabecalho_de_coluna() -> None:
    """D23 revoga a excecao de D22: a grade 2x3 nao existe mais.

    Enquanto o cabecalho de coluna existia, o CSS era obrigado a manter o bloco
    em linha em qualquer largura — e era essa regra que produzia os campos de
    ~85px no celular. Este teste garante que ninguem traga o cabecalho de volta
    sem perceber que ele arrasta a regra junto.
    """
    at = _app()
    for bloco in _blocos(at):
        assert "st-cash-cabecalho" not in bloco, (
            "o cabeçalho de coluna do cashback voltou — com ele volta o campo "
            "de ~85px no celular (D22 §celular)"
        )

    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")
    celular = folha[folha.index("@media (max-width: 767px)") :]
    regra = re.search(
        r'\.st-key-entrada_cashback \[data-testid="stHorizontalBlock"\] \{\{'
        r"([^}]*)\}\}",
        celular,
    )
    assert regra is not None, (
        "abaixo de 768px o cashback precisa de uma regra própria: a exceção de "
        "1023px o mantém em linha, e é ela que este bloco revoga"
    )
    assert "flex-direction: column" in regra.group(1), (
        "abaixo de 768px o cashback precisa empilhar: em linha, são três "
        "campos de ~110px num aparelho de 390px"
    )


def test_render_rotulo_nunca_menciona_cashback() -> None:
    """§6.1.7 / §12: "cashback" nunca aparece no rotulo do resultado.

    Desde D21 os rotulos do resultado sao os dos tres cartoes.
    """
    at = _preencher_cashback(_preencher_cenario_base(_app()))

    # `_blocos` exclui a folha de estilo — ela tem um comentario de CSS com a
    # palavra "cashback" e casaria com a busca.
    for bloco in _blocos(at):
        if "st-cartao-rotulo" in bloco:
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
    # "numero financeiro em vermelho le como prejuizo". Desde D21 a classe a
    # vigiar e a dos cartoes, nao mais `.st-anual` / `.st-mensal`.
    cartoes = [b for b in _blocos(at) if "st-cartao-valor" in b]
    assert cartoes, "os cartoes de resultado precisam existir"
    for bloco in cartoes:
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
    # E o calculo NAO foi bloqueado (§6.1.8: "um bloqueio na frente do cliente
    # encerra a cena"). O botao de D21 gateia a EXIBICAO, nunca o calculo: com o
    # resultado revelado, um cenario implausivel continua produzindo numero.
    assert "Valores anuais" in texto
    assert "st-cartao-valor" in texto


def test_render_ajustes_avancados_nao_existe_mais() -> None:
    """D21: o expander da §5.10 foi dissolvido. Nada de campo escondido.

    O teste anterior exigia o oposto — que o expander EXISTISSE e abrisse
    fechado a cada carga da pagina ("§5.10: fechado por padrao, SEMPRE"). O
    cliente pediu que nada ficasse escondido, e o conteudo dele subiu para a
    superficie primaria; `test_render_todos_os_campos_estao_na_superficie_primaria`
    e quem garante que ele subiu inteiro, e nao que apenas desapareceu.

    Os expanders que CONTINUAM existindo sao os tres de leitura — tabela da
    curva, painel de formula e PDF —, e nenhum deles guarda campo de entrada
    que altere o resultado.
    """
    at = _app()
    rotulos = [e.label for e in at.expander]
    assert not [r for r in rotulos if "Ajustes avançados" in r], rotulos


def test_render_tabela_gemea_da_curva_existe() -> None:
    """§5.11 / §9: o gemeo em tabela e OBRIGATORIO — substitui o tooltip."""
    at = _preencher_cenario_base(_app())
    rotulos = [e.label for e in at.expander]
    assert any("números da curva" in r for r in rotulos), rotulos


def test_render_exportar_pdf_o_botao_entrega_o_documento() -> None:
    """D23 / §4.11 — o botao de baixar, verificado no ARTEFATO.

    O componente e testado desde sempre por `test_pdf.py`, que chama
    `gerar_pdf()` direto: o DOCUMENTO estava certo o tempo todo. O que estava
    quebrado era o botao — a unica peca entre o documento e o cliente — e
    nenhum teste olhava para ele.

    O defeito: o rotulo carregava `svg('exportar')`, e o Streamlit trata rotulo
    de botao como markdown e ESCAPA a marcacao. O botao saia com
    `<span class="st-icone" ...><svg ...>` impresso em cima dele.

    Os BYTES nao dao para conferir aqui — o proto do download_button carrega so
    uma URL de midia, nao o conteudo. Quem cobre o conteudo e `test_pdf.py`, e
    o nome do arquivo e `test_pdf_nome_do_arquivo_*`. O que este teste cobre e o
    que so existe no artefato: o rotulo, a presenca do botao e o tipo do
    arquivo que ele serve.
    """
    at = _preencher_cenario_base(_app())
    at.text_input(key="nome_cliente").set_value("Auto Center — Zona Sul").run()

    botoes = at.get("download_button")
    assert botoes, "o botão de baixar o PDF precisa existir com o resultado na tela"
    baixar = botoes[0]

    assert "<" not in baixar.label and ">" not in baixar.label, (
        f"rótulo com marcação: {baixar.label!r}. O Streamlit escapa HTML em "
        f"rótulo de botão — o ícone vai numa linha de markdown, não aqui"
    )
    assert baixar.label == "Baixar PDF do cenário"
    assert baixar.proto.url.endswith(".pdf"), baixar.proto.url

    # E o icone continua na tela, na linha de markdown acima do botao (D2:
    # icone SEMPRE acompanhado de palavra, nunca canal unico).
    notas = [b for b in _blocos(at) if "st-exportar-nota" in b]
    assert notas, "a nota da área de exportação precisa existir"
    assert "<svg" in notas[0]


def test_render_exportar_pdf_so_com_o_resultado_na_tela() -> None:
    """O PDF e montado a cada rerun, e por isso NAO pode existir antes do toque.

    Antes de "Mostrar Resultado" a Tela 1 nao chama o bloco de exportacao —
    montar o documento ali seria trabalho por tecla digitada, e um PDF do
    cenario incompleto ao alcance de um toque.
    """
    at = _app()
    assert not at.get("download_button")


# ---------------------------------------------------------------------------
# D30 — enviar o documento por e-mail
#
# O transporte e trocado por um duplo em todos estes testes. O que se verifica
# aqui e a UNICA coisa que `test_email.py` nao alcanca: quando o transporte e
# chamado, e quantas vezes. `test_email.py` cobre o que sai; estes cobrem o
# gatilho — que e onde o Streamlit morde, porque ele reexecuta o script inteiro
# a cada toque na tela.
# ---------------------------------------------------------------------------


def _envio_falso(monkeypatch, *, configurado: bool = True) -> list[dict]:
    """Substitui o transporte e devolve a lista de chamadas registradas."""
    from src.componentes import enviador_email

    chamadas: list[dict] = []

    def _enviar(**argumentos):
        chamadas.append(argumentos)
        return None

    monkeypatch.setattr(enviador_email, "enviar", _enviar)
    monkeypatch.setattr(enviador_email, "configurado", lambda: configurado)
    return chamadas


def test_render_enviar_email_campo_e_botao_com_o_resultado_na_tela(
    monkeypatch,
) -> None:
    """O pedido do cliente: um botao ABAIXO do de exportar, com campo de e-mail.

    A ordem importa e e a razao do teste ler as duas pecas juntas: o botao de
    baixar e o caminho que nao depende de credencial nem de endereco digitado,
    e ele vem primeiro.
    """
    _envio_falso(monkeypatch)
    at = _preencher_cenario_base(_app())

    campo = at.text_input(key="email_destino")
    assert campo.label == "E-mail para receber o documento"
    assert campo.value in (None, ""), "o campo abre vazio, como todo campo (§5.2)"

    assert at.get("download_button"), "o botão de baixar continua sendo o piso"

    enviar = [b for b in at.button if b.key == "botao_enviar"]
    assert enviar, [b.key for b in at.button]
    assert enviar[0].label == "Enviar por e-mail"
    assert enviar[0].proto.disabled, "sem endereço não há o que enviar"


def test_render_enviar_email_sem_configuracao_mostra_o_botao_desabilitado(
    monkeypatch,
) -> None:
    """Sem credencial o botao APARECE CINZA, com o motivo escrito abaixo.

    Pedido do cliente em 01/09/2026, depois de ver a versao anterior. Aquela
    desenhava o CAMPO de e-mail e depois sumia com o botao — um campo pedindo um
    endereco que nao tem para onde ir, que e o pior dos dois mundos. A forma
    nova e a mesma do botao "Mostrar Resultado" (D21): visivel, desabilitado, e
    o que falta dito em TEXTO, nunca em cor (§3.1.2, §9.4).

    Este e o estado do deploy antes de alguem colar os Secrets no painel.
    """
    _envio_falso(monkeypatch, configurado=False)
    at = _preencher_cenario_base(_app())

    enviar = [b for b in at.button if b.key == "botao_enviar"]
    assert enviar, "o botão precisa existir mesmo sem credencial"
    assert enviar[0].proto.disabled, "sem credencial ele não pode ser tocável"

    assert at.get("download_button"), "o documento continua ao alcance de um toque"
    assert "ainda não está configurado" in _texto(at)
    assert not at.exception, at.exception
    assert not at.error and not at.warning


def test_render_enviar_email_pede_confirmacao_antes_de_sair(monkeypatch) -> None:
    """Decisao do cliente, 01/09/2026 — o custo so sai com um segundo toque.

    Repare que TODO documento desta tela e interno: `custo_original` e
    obrigatorio (D21) e `documento_interno` olha para ele. A confirmacao,
    portanto, e o caminho normal e nao a excecao — e e por isso que ela precisa
    ser barata: duas colunas, 52 px, sem caixa de alerta (§5.9).
    """
    chamadas = _envio_falso(monkeypatch)
    at = _preencher_cenario_base(_app())

    at.text_input(key="email_destino").set_value("gerente@concessionaria.test").run()
    at.button(key="botao_enviar").click().run()

    assert not chamadas, "nada pode sair antes da confirmação"

    chaves = {b.key for b in at.button}
    assert "botao_confirmar_envio" in chaves, chaves
    assert "botao_cancelar_envio" in chaves, chaves

    texto = _texto(at)
    assert "documento interno" in texto
    # O endereco vem escrito: digitar torto e o unico jeito de este envio vazar
    # a tabela de precos, e ler o endereco e a unica defesa contra isso.
    assert "gerente@concessionaria.test" in texto
    assert not at.error and not at.warning


def test_render_enviar_email_confirmado_chama_o_transporte_uma_unica_vez(
    monkeypatch,
) -> None:
    """O defeito que este teste existe para impedir: o documento sair duas vezes.

    O Streamlit reexecuta o script INTEIRO a cada interacao. Se o pedido de
    envio continuasse de pe depois de atendido, qualquer toque seguinte — abrir
    um expander, mexer num slider — remandaria o mesmo PDF. `mexer no cenario`
    abaixo e exatamente essa cena.
    """
    chamadas = _envio_falso(monkeypatch)
    at = _preencher_cenario_base(_app())

    at.text_input(key="email_destino").set_value("gerente@concessionaria.test").run()
    at.button(key="botao_enviar").click().run()
    at.button(key="botao_confirmar_envio").click().run()

    assert len(chamadas) == 1, chamadas
    assert chamadas[0]["destino"] == "gerente@concessionaria.test"
    assert chamadas[0]["documento"].startswith(b"%PDF")
    assert chamadas[0]["nome_arquivo"].endswith(".pdf")

    texto = _texto(at)
    assert "Documento enviado" in texto
    assert "joao@suicatech.com.br" in texto

    # E agora a cena do defeito: mexer no cenario nao pode mandar de novo.
    at.slider(key="conv_dianteiro").set_value(35).run()
    assert len(chamadas) == 1, f"o documento saiu {len(chamadas)} vezes"


def test_render_enviar_email_cancelar_nao_envia(monkeypatch) -> None:
    """Cancelar volta ao botao, sem mandar nada e sem apagar o endereco."""
    chamadas = _envio_falso(monkeypatch)
    at = _preencher_cenario_base(_app())

    at.text_input(key="email_destino").set_value("gerente@concessionaria.test").run()
    at.button(key="botao_enviar").click().run()
    at.button(key="botao_cancelar_envio").click().run()

    assert not chamadas
    assert "botao_enviar" in {b.key for b in at.button}
    assert at.text_input(key="email_destino").value == "gerente@concessionaria.test"


def test_render_enviar_email_endereco_torto_nao_habilita(monkeypatch) -> None:
    """Sem vocabulario de erro (§4): o botao apenas nao habilita, e o texto diz.

    A verificacao e de FORMA e nada mais — so a entrega prova que a caixa
    existe, e por isso nenhum texto da tela declara o endereco correto.
    """
    _envio_falso(monkeypatch)
    at = _preencher_cenario_base(_app())

    at.text_input(key="email_destino").set_value("gerente").run()
    assert at.button(key="botao_enviar").proto.disabled
    assert "Informe um endereço" in _texto(at)

    at.text_input(key="email_destino").set_value("gerente@concessionaria.test").run()
    assert not at.button(key="botao_enviar").proto.disabled


def test_render_enviar_email_no_teto_da_sessao_o_botao_fica_cinza(
    monkeypatch,
) -> None:
    """O teto do link aberto (plano §6.3), verificado no artefato.

    Duas coisas ao mesmo tempo: o botao fica cinza com o motivo, e NENHUM pedido
    fica pendente. A versao anterior saia por `return` antes de atender o pedido
    nesse caso — uma bandeira levantada no rerun anterior ficava presa, e a tela
    podia travar na confirmacao sem caminho de volta.
    """
    from src.componentes import enviador_email

    chamadas = _envio_falso(monkeypatch)
    monkeypatch.setattr(enviador_email, "LIMITE_POR_SESSAO", 1)

    at = _preencher_cenario_base(_app())
    at.text_input(key="email_destino").set_value("gerente@concessionaria.test").run()
    at.button(key="botao_enviar").click().run()
    at.button(key="botao_confirmar_envio").click().run()
    assert len(chamadas) == 1

    # O primeiro envio ja consumiu o teto: o botao volta cinza, dizendo por que.
    enviar = [b for b in at.button if b.key == "botao_enviar"]
    assert enviar and enviar[0].proto.disabled
    assert "Limite de envios desta sessão" in _texto(at)

    assert not at.session_state["envio_pedido"], "nenhum pedido pode ficar preso"
    assert len(chamadas) == 1, "nada mais pode sair depois do teto"


def test_render_novo_cliente_limpa_o_endereco_de_email(monkeypatch) -> None:
    """§5.2 — o endereco e da visita, como o nome do cliente.

    Deixar preenchido mostraria ao proximo gerente para quem o anterior pediu o
    documento, e a linha "Documento enviado para ..." carrega esse endereco na
    tela.
    """
    _envio_falso(monkeypatch)
    at = _preencher_cenario_base(_app())

    at.text_input(key="email_destino").set_value("gerente@concessionaria.test").run()
    at.button(key="botao_enviar").click().run()
    at.button(key="botao_confirmar_envio").click().run()
    assert "Documento enviado" in _texto(at)

    at.button(key="btn_novo_cliente").click().run()

    # O CAMPO NAO EXISTE MAIS NA TELA — `novo cliente` limpa os obrigatorios e a
    # area de exportacao inteira sai com o resultado (D21). A verificacao e no
    # estado, que e onde o vazamento moraria: um widget ausente nesta carga volta
    # com o valor antigo assim que os campos forem preenchidos de novo.
    assert not [t for t in at.text_input if t.key == "email_destino"]
    assert at.session_state["email_destino"] == ""
    assert at.session_state["envio_estado"] is None
    assert "Documento enviado" not in _texto(at)

    # E ao refazer um cenario, o campo volta VAZIO — que e a prova de verdade.
    _preencher_cenario_base(at)
    assert at.text_input(key="email_destino").value in (None, "")


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

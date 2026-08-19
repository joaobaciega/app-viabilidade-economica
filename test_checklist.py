"""O checklist §12 do DESIGN, verificavel por comando.

"Cada item e verificavel olhando a tela ou rodando um grep. NENHUM E OPINIAO."

Este arquivo implementa os itens automatizaveis. Os manuais (legibilidade a 1 m,
marca do framework em todas as resolucoes, reteste visual dos 🔧) vivem em
docs/DIVERGENCIAS.md com espaco para data e assinatura.

verificar.py roda as MESMAS funcoes e imprime linha por linha — o que voce roda
no dia a dia. Aqui elas viram teste, para que `pytest` cubra tudo.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from testes.checagens import (
    ARQUIVOS_PY_APP,
    RAIZ,
    arquivos_que_importam,
    atribuicoes_suspeitas_de_derivar_traseiro,
    chaves_de_container,
    ocorrencias,
    persistencia_de_campos_de_sessao,
    strings_de_tela_que_casam,
)

# ---------------------------------------------------------------------------
# Regras de conteudo (§4, §12)
# ---------------------------------------------------------------------------


def test_a_palavra_lucro_nao_existe() -> None:
    """P12 / §4: `grep -ri "lucro" src/` retorna vazio.

    "'Lucro' convida a correcao do financeiro que derruba a credibilidade de
    tudo que veio antes." O calculo para em margem de contribuicao.
    """
    achados = ocorrencias(r"lucro|lucrativ|rentabil")
    assert not achados, f"vocabulario proibido encontrado:\n" + "\n".join(achados)


def test_vocabulario_de_promessa_nao_existe() -> None:
    """§4: ROI, retorno garantido, gratis — promessa que o app nao sustenta."""
    achados = ocorrencias(r"\bROI\b|garantid|grátis|\bgratis\b|imperdív")
    assert not achados, "\n".join(achados)


def test_vocabulario_de_alerta_nao_existe_em_texto_de_tela() -> None:
    """§4: "Erro", "invalido", "atencao", "cuidado".

    A faixa do vendedor DESCREVE o que observar, nao acusa. Busca so em
    strings literais destinadas a tela, porque `ValueError` e nomes de excecao
    sao legitimos no codigo.
    """
    proibidas = re.compile(r"(?i)\b(inválido|invalida|atenção|cuidado|falha grave)\b")
    achados = strings_de_tela_que_casam(proibidas)
    assert not achados, "\n".join(achados)


def test_nenhum_texto_de_tela_fala_do_cliente_em_terceira_pessoa() -> None:
    """Decisao do cliente (11/08/2026): nenhum rótulo diz "ele".

    O motivo nao e estilo, e a cena: o tablet esta inclinado NA DIRECAO do
    gerente. "Palhetas que ele vende por mes" e uma frase sobre alguem que esta
    lendo a frase — e a §1 do DESIGN insiste que a tela e operada na frente dele.

    Rotulos sao impessoais ("palhetas vendidas por mês"); onde o texto se dirige
    a alguem, dirige-se ao cliente em segunda pessoa.
    """
    proibidas = re.compile(r"(?i)\b(ele|dele)\b")
    achados = [
        a
        # css.py e uma folha de estilo dentro de uma string: os comentarios de
        # CSS ficam no literal e nao sao texto de tela.
        for a in strings_de_tela_que_casam(proibidas, ignorar=("css.py",))
        # "sem ele" / "com ele" em texto tecnico se referem a um CAMPO (o custo
        # da original), nao a uma pessoa.
        if not re.search(r"(?i)\b(sem|com|para|por)\s+ele\b", a)
    ]
    assert not achados, (
        "texto de tela falando do cliente em terceira pessoa:\n" + "\n".join(achados)
    )


def test_componentes_de_alerta_do_streamlit_nao_sao_usados() -> None:
    """§5.9 — REGRA ABSOLUTA.

    "Caixa amarela ou vermelha na frente do gerente transforma um ajuste
    tecnico em VEXAME PUBLICO."

    grep -rn "st\\.warning\\|st\\.error\\|st\\.exception\\|st\\.toast\\|
              st\\.balloons\\|st\\.snow" src/  ->  vazio
    """
    achados = ocorrencias(
        r"st\.(warning|error|exception|toast|balloons|snow)\s*\("
    )
    assert not achados, (
        "componente de alerta proibido na area visivel ao cliente:\n"
        + "\n".join(achados)
    )


def test_nao_usa_st_metric() -> None:
    """§5.5: "Nao use st.metric." Nao chega aos 48px que 1 m exige."""
    assert not ocorrencias(r"st\.metric\s*\(")


def test_nenhuma_promessa_de_offline() -> None:
    """§12, "Promessa da stack".

    "Nenhum item deste app, da interface ou de qualquer texto promete
    comportamento offline." Nao existe offline nesta stack (plano §6.2).

    Busca por promessas em strings de tela — nao pelas palavras em comentario,
    que aqui servem justamente para NEGAR a promessa.
    """
    promessas = re.compile(
        r"(?i)(funciona\s+(sem|offline)|modo\s+offline|sem\s+internet|"
        r"disponível\s+offline|opera\s+sem\s+rede|instale?\s+na\s+tela\s+inicial)"
    )
    achados = strings_de_tela_que_casam(promessas)
    assert not achados, (
        "o app nao pode prometer funcionamento sem rede:\n" + "\n".join(achados)
    )


def test_service_worker_e_pwa_nao_existem() -> None:
    """Nao ha PWA nesta stack. Prometer e nao ter e pior que assumir."""
    assert not list(RAIZ.glob("**/sw.js"))
    assert not list(RAIZ.glob("**/manifest.webmanifest"))
    assert not list(RAIZ.glob("**/service-worker.js"))


# ---------------------------------------------------------------------------
# Unidade e par (§5.13) — a verificacao por AST
# ---------------------------------------------------------------------------


def test_traseiro_nunca_derivado_do_dianteiro() -> None:
    """§5.13, regra critica; §12, "Unidade e par".

    "NENHUMA EXPRESSAO NO CODIGO DERIVA PRECO OU CUSTO DO TRASEIRO A PARTIR DO
    DIANTEIRO — nem /2, nem qualquer fator."

    grep nao serve aqui: `preco_traseiro = preco_dianteiro / 2` e
    `t = d; t /= 2` sao a mesma coisa e o segundo escapa de qualquer regex.
    Por isso a checagem e por AST: procura qualquer atribuicao a um alvo
    "traseiro" cuja expressao mencione "dianteiro", e vice-versa.
    """
    achados = atribuicoes_suspeitas_de_derivar_traseiro()
    assert not achados, (
        "derivacao proibida entre categorias (§5.13):\n" + "\n".join(achados)
    )


def test_nao_existe_funcao_de_conversao_de_unidade() -> None:
    """Converter par<->unidade erra por 2x. A funcao nao deve existir."""
    achados = ocorrencias(
        r"def\s+\w*(par_para_unidade|unidade_para_par|converter_unidade)"
    )
    assert not achados, "\n".join(achados)


def test_unidade_e_atributo_declarado_por_categoria() -> None:
    """§5.13 / V3: atributo por categoria, NUNCA constante global."""
    from src import parametros as P

    for categoria in P.CATEGORIAS:
        assert categoria.unidade in {"par", "unitario"}
    # Nao existe constante global de unidade.
    assert not hasattr(P, "UNIDADE")
    assert not hasattr(P, "UNIDADE_PADRAO")


# ---------------------------------------------------------------------------
# Estado de sessao — nunca persistido (§11.1 acrescentada, P3, §5.2, §6.1.9)
# ---------------------------------------------------------------------------


def test_campos_de_sessao_nunca_sao_persistidos() -> None:
    """O custo de aquisicao E o preco de venda da Suicatech, e o link e aberto.

    Verifica que nenhum campo da tabela de estado de sessao aparece em
    localStorage, sessionStorage, query params, escrita em disco ou cache.
    """
    achados = persistencia_de_campos_de_sessao()
    assert not achados, (
        "campo de sessao sendo persistido:\n" + "\n".join(achados)
    )


def test_nao_ha_cache_de_dados_sensiveis() -> None:
    """st.cache_data/cache_resource nunca envolvem preco, custo ou ancora."""
    achados = ocorrencias(r"localStorage|sessionStorage|st\.query_params")
    assert not achados, "\n".join(achados)


def test_campos_sensiveis_abrem_vazios() -> None:
    """P3 / §5.2: value=None. Nenhum default, nenhum valor de demonstracao."""
    fonte = (RAIZ / "src" / "componentes" / "campo_unidade.py").read_text(
        encoding="utf-8"
    )
    assert "value=None" in fonte, (
        "os campos precisam abrir vazios (value=None), sem default e sem "
        "valor de demonstracao"
    )

    # E os defaults semeados nao incluem nenhum campo sensivel.
    from src import estado

    for chave in (
        estado.K_PRECO_D,
        estado.K_CUSTO_D,
        estado.K_PRECO_T,
        estado.K_CUSTO_T,
        estado.K_ORIGINAIS,
        estado.K_PRECO_ORIG,
        estado.K_CUSTO_ORIG,
    ):
        assert chave not in estado._DEFAULTS, (
            f"{chave} nao pode ter default: um numero na tela vira ancora "
            f"mesmo com etiqueta de exemplo"
        )


def test_novo_cliente_limpa_tudo() -> None:
    from src import estado

    for chave in (
        estado.K_PRECO_D,
        estado.K_CUSTO_D,
        estado.K_PRECO_T,
        estado.K_CUSTO_T,
        estado.K_ORIGINAIS,
        estado.K_PRECO_ORIG,
        estado.K_CUSTO_ORIG,
        estado.K_NOME_CLIENTE,
    ):
        assert chave in estado.CAMPOS_DE_SESSAO


def test_novo_cliente_atribui_em_vez_de_apagar() -> None:
    """Regressao de um vazamento real.

    Apagar a chave de um widget do session_state (`del`) zera o estado no
    servidor mas NAO empurra o reset para o navegador: a tela voltava ao estado
    E1 (correto) e os campos de preco e custo seguiam PREENCHIDOS na cara do
    proximo cliente — exatamente o vazamento que a §5.2 existe para impedir.

    A correcao e atribuir o valor de limpeza. Este teste garante que ninguem
    volte para o `del`.
    """
    from src import estado

    fonte = (RAIZ / "src" / "estado.py").read_text(encoding="utf-8")
    arvore = ast.parse(fonte)

    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == "novo_cliente":
            for interno in ast.walk(no):
                assert not isinstance(interno, ast.Delete), (
                    "novo_cliente() nao pode usar `del` em session_state — "
                    "o campo continuaria preenchido no navegador"
                )

    # E a tabela de limpeza cobre exatamente os campos de sessao.
    assert set(estado._LIMPEZA) == set(estado.CAMPOS_DE_SESSAO), (
        "todo campo de sessao precisa de um valor de limpeza:\n"
        f"sem limpeza: {set(estado.CAMPOS_DE_SESSAO) - set(estado._LIMPEZA)}\n"
        f"sobrando:    {set(estado._LIMPEZA) - set(estado.CAMPOS_DE_SESSAO)}"
    )

    # Nenhum campo sensivel pode ser limpo para um NUMERO — seria um default.
    for chave in (
        estado.K_PRECO_D,
        estado.K_CUSTO_D,
        estado.K_PRECO_T,
        estado.K_CUSTO_T,
        estado.K_ORIGINAIS,
        estado.K_PRECO_ORIG,
        estado.K_CUSTO_ORIG,
    ):
        assert estado._LIMPEZA[chave] is None, (
            f"{chave} precisa ser limpo para None, nunca para um numero"
        )


def test_logo_tem_reserva_e_nunca_quebra_a_tela() -> None:
    """§7.4: nunca uma tela quebrada na frente do cliente.

    Sem `assets/logo.*`, o cabecalho cai na marca em tipografia e o motivo vai
    para a faixa do vendedor — nao para a area que o cliente le.
    """
    from src import marca

    html = marca.html()
    assert html, "a marca sempre renderiza algo"
    if marca.data_uri() is None:
        assert "st-marca" in html, "sem arquivo, usa a reserva tipografica"
        assert marca.motivo_da_reserva() is not None, (
            "o vendedor precisa saber que o logo nao carregou"
        )
    else:
        assert html.startswith("<img"), "com arquivo, renderiza a imagem"
        assert marca.motivo_da_reserva() is None


def test_logo_e_embutido_sem_requisicao_externa() -> None:
    """P11 / §7.1: a Tela 1 nao faz NENHUMA requisicao externa.

    O logo entra como data: URI. `st.image`/`st.logo` criariam um endpoint de
    midia e uma requisicao por render.
    """
    from src import marca

    uri = marca.data_uri()
    if uri is not None:
        assert uri.startswith("data:"), "o logo precisa ser embutido"

    fonte = (RAIZ / "src" / "marca.py").read_text(encoding="utf-8")
    for proibido in ("st.image(", "st.logo(", "http://", "https://"):
        assert proibido not in fonte, f"{proibido} introduz dependencia de rede"


def test_aproveitamento_traseiro_tem_um_unico_controle() -> None:
    """O slider do traseiro subiu para a tela inicial (pedido do cliente).

    Ele NAO pode existir em dois lugares: instanciar duas vezes a mesma chave
    de widget levanta StreamlitAPIException e derruba a tela.
    """
    from src import estado

    ocorrencias_slider = ocorrencias(
        rf"key\s*=\s*(estado\.)?K_CONV_T\b"
    )
    assert len(ocorrencias_slider) == 1, (
        "o aproveitamento traseiro precisa ter exatamente UM widget:\n"
        + "\n".join(ocorrencias_slider)
    )
    assert estado.K_CONV_T == "conv_traseiro"


def test_atalhos_do_traseiro_escrevem_por_on_click() -> None:
    """§5.3: escrever a chave de um widget depois de instanciado levanta
    StreamlitAPIException. Por isso os atalhos usam on_click."""
    fonte = (RAIZ / "src" / "telas" / "tela1_simulador.py").read_text(
        encoding="utf-8"
    )
    assert "on_click=estado.aplicar_traseiro" in fonte


def test_aplicar_traseiro_nao_toca_no_dianteiro() -> None:
    """Acoplar as duas taxas recriaria o risco n. 1 do plano."""
    fonte = (RAIZ / "src" / "estado.py").read_text(encoding="utf-8")
    arvore = ast.parse(fonte)
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == "aplicar_traseiro":
            corpo = ast.get_source_segment(fonte, no) or ""
            assert "K_CONV_D" not in corpo, (
                "aplicar_traseiro nao pode escrever no aproveitamento dianteiro"
            )
            return
    raise AssertionError("aplicar_traseiro nao encontrado")


def test_navegacao_nao_depende_do_chrome_do_streamlit() -> None:
    """Regressao: as Telas 2 e 3 ficaram INALCANCAVEIS.

    A §6.1.9 exige ocultar a barra superior do Streamlit. Fazer isso leva embora
    o controle que abre a barra lateral — e, com a navegacao morando na lateral,
    nao havia como chegar nas Telas 2 e 3. So a verificacao pelo navegador pegou
    (a lateral media 0px de largura e o botao de abrir nao era visivel).

    A navegacao vive no cabecalho da propria pagina, sem depender do chrome do
    framework.
    """
    fonte = (RAIZ / "app.py").read_text(encoding="utf-8")
    assert "st.sidebar" not in fonte, (
        "a navegacao nao pode viver na barra lateral: ocultar a barra superior "
        "do Streamlit (§6.1.9) torna o controle de abri-la inalcancavel"
    )
    assert 'st.container(key="navegacao")' in fonte

    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")
    assert ".st-key-navegacao" in folha


# ---------------------------------------------------------------------------
# Decisoes em aberto — a AUSENCIA das constantes (§10, §12)
# ---------------------------------------------------------------------------


def test_nenhuma_constante_das_decisoes_em_aberto() -> None:
    """§12: "Nenhum valor da §10 aparece fixado fora de parametros.py."""
    from src import parametros as P

    assert P.PISO_PRECO is None, "decisao F"
    assert P.CODIGOS_COBERTURA_97 is None, "decisao G"
    assert P.RAMPA_MESES is None, "decisao I"
    assert P.SAZONALIDADE_MENSAL is None, "decisao J"
    assert P.LIMIAR_IDADE_DIAS is None, "decisao L"


def test_nenhum_piso_de_preco_fixado_no_codigo() -> None:
    """grep -rn "piso" src/ nao encontra nenhum piso com valor.

    Procura por atribuicao de numero a qualquer nome que contenha "piso" ou
    "minimo_preco" fora de parametros.py.
    """
    # O padrao precisa ser de PRECO. "piso" sozinho casa com PISO_TEXTO_CLIENTE,
    # que e o piso tipografico da §3.2 e nao tem nada a ver com a decisao F.
    de_preco = re.compile(
        r"(?i)(piso.*(preco|valor)|(preco|valor).*piso|preco_min|min_preco)"
    )
    achados: list[str] = []

    for caminho in ARQUIVOS_PY_APP:
        if caminho.name == "parametros.py":
            continue  # e o unico lugar onde o valor pode viver, e ali e None
        arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if not isinstance(no, (ast.Assign, ast.AnnAssign)):
                continue
            alvos = no.targets if isinstance(no, ast.Assign) else [no.target]
            for alvo in alvos:
                nome = getattr(alvo, "id", "") or getattr(alvo, "attr", "") or ""
                if not de_preco.search(nome):
                    continue
                if isinstance(no.value, ast.Constant) and isinstance(
                    no.value.value, (int, float)
                ):
                    achados.append(
                        f"{caminho.name}:{no.lineno}: {nome} = {no.value.value}"
                    )

    assert not achados, "piso de preco inventado (decisao F):\n" + "\n".join(achados)


def test_min_value_dos_campos_de_moeda_nao_e_piso_comercial() -> None:
    """§5.2: "Nao implemente validacao de piso de preco."

    `min_value=0.0` impede numero negativo, que nao e piso — e ausencia de
    sentido. Qualquer min_value positivo num campo de moeda seria um piso
    inventado entrando pela porta dos fundos.
    """
    fonte = (RAIZ / "src" / "componentes" / "campo_unidade.py").read_text(
        encoding="utf-8"
    )
    arvore = ast.parse(fonte)
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == "campo_moeda":
            trecho = ast.get_source_segment(fonte, no) or ""
            for valor in re.findall(r"minimo=([0-9.]+)", trecho):
                assert float(valor) == 0.0, (
                    f"campo_moeda com minimo={valor} e um piso de preco "
                    f"inventado (decisao F em aberto)"
                )


def test_bloco_de_investimento_ausente_nao_desabilitado() -> None:
    """§10-G: "nao desabilitado, AUSENTE."

    Nenhum widget de payback/estoque/capital de giro existe na interface.
    """
    achados = ocorrencias(
        r"(st\.\w+\([^)]*)(payback|capital de giro|estoque m[ií]nimo|pedido m[ií]nimo)"
    )
    assert not achados, (
        "bloco de investimento precisa estar AUSENTE (decisao G):\n"
        + "\n".join(achados)
    )


# ---------------------------------------------------------------------------
# Tipografia e tokens (§3.2)
# ---------------------------------------------------------------------------


def test_traducao_pelo_menos_1_25_do_anual() -> None:
    """§3.2, regra de checagem automatica: 48 / 36 = 1,33.

    "Inverter e o erro de implementacao mais provavel desta tela."
    """
    from src.css import T_ANUAL, T_TRADUCAO

    assert T_TRADUCAO >= 1.25 * T_ANUAL


def test_tipografia_do_resultado_vence_a_cascata_do_streamlit() -> None:
    """Regressao do defeito mais grave encontrado nesta construcao.

    O Streamlit estiliza paragrafos de markdown com um seletor de dois niveis
    (`[data-testid="stMarkdownContainer"] p`, especificidade 0-1-1). Uma classe
    sozinha (`.st-traducao`, 0-1-0) PERDE a cascata: a traducao renderizava em
    16px em vez de 48px e o valor anual em 16px em vez de 36px.

    Nenhum teste de unidade pega isso — os tokens em Python estavam corretos, o
    HTML estava correto, e a tela estava errada. So a medicao de `fontSize`
    computado no navegador revelou.

    Regra: toda classe de texto proprio declara font-size com !important.
    """
    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")

    criticas = (
        "st-traducao",
        "st-anual",
        "st-mensal",
        "st-rotulo-resultado",
        "st-linha-apoio",
        "st-falta-ancora",
        "st-premissas",
        "st-faixa-vendedor",
        "st-legenda-bloco",
        "st-chip",
        "st-secao",
    )

    for classe in criticas:
        inicio = folha.find(f".{classe} {{")
        assert inicio != -1, f"classe .{classe} nao existe em css.py"
        bloco = folha[inicio : folha.index("}}", inicio)]
        assert "font-size" in bloco, f".{classe} nao declara font-size"
        linha_tamanho = next(
            linha for linha in bloco.splitlines() if "font-size" in linha
        )
        assert "!important" in linha_tamanho, (
            f".{classe} declara font-size sem !important e vai perder da "
            f"cascata do Streamlit — a leitura a um metro depende disso"
        )


def test_nada_que_o_cliente_le_abaixo_de_22px() -> None:
    """§3.2 / P1."""
    from src import css

    escala_cliente = (
        css.T_TRADUCAO,
        css.T_ANUAL,
        css.T_PRESET_VALOR,
        css.T_MENSAL,
        css.T_PRESET_NOME,
    )
    for tamanho in escala_cliente:
        assert tamanho >= css.PISO_TEXTO_CLIENTE, (
            f"{tamanho}px esta abaixo do piso de leitura do cliente "
            f"({css.PISO_TEXTO_CLIENTE}px)"
        )


def test_faixa_do_vendedor_e_ilegivel_a_um_metro() -> None:
    """§3.2: 12px a 1 m ~= 4,8px de leitura normal. E o MECANISMO."""
    from src import css

    assert css.T_VENDEDOR == 12
    assert css.T_VENDEDOR < css.PISO_TEXTO_CLIENTE


def test_escala_dupla_existe() -> None:
    """§3.2 — duas escalas: cliente a 1 m, vendedor a 40 cm."""
    from src import css

    menor_do_cliente = min(
        css.T_TRADUCAO, css.T_ANUAL, css.T_PRESET_VALOR, css.T_MENSAL
    )
    maior_do_operador = max(css.T_ROTULO, css.T_CAMPO, css.T_DERIVADO)
    assert menor_do_cliente > maior_do_operador, (
        "as duas escalas precisam ser distintas: a do cliente inteira acima "
        "da do operador"
    )


def test_vermelho_nao_e_usado_como_alerta() -> None:
    """§3.1.2: nao existe token --erro, --atencao ou --critico."""
    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")
    for token in ("--erro", "--atencao", "--critico", "--sucesso", "--aviso"):
        assert token not in folha, f"token semantico proibido: {token}"


def test_sombra_e_gradiente_so_nos_lugares_declarados() -> None:
    """§3.5 pede "elevacao por traco, NENHUMA sombra", e §3.1 proibe gradiente.

    O cliente autorizou afrouxar isso (D5 e D7 em docs/DIVERGENCIAS.md), porque
    a versao literal ficou com cara de aplicacao antiga. O afrouxamento e
    LIMITADO, e este teste e o limite:

      - toda sombra vem de um token `--sombra-*` declarado, ou e `none`.
        Nenhuma sombra ad hoc, espalhada, com raio arbitrario
      - gradiente existe apenas nos tres lugares autorizados: a faixa do
        cabecalho, o botao de cenario ATIVO e a regua do bloco de resultado

    Sem este teste, "modernizar" viraria licenca para o app parecer folheto —
    que e exatamente o que a §3.5 existe para impedir.
    """
    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")

    for achado in re.findall(r"box-shadow:\s*([^;]+);", folha):
        limpo = achado.strip()
        ok = (
            "none" in limpo
            or "var(--sombra-" in limpo
            or limpo.startswith("0 0 0 3px var(--marca-lavado)")  # anel de foco
            or "rgba(148,9,31" in limpo  # realce do preset ativo e do polegar
        )
        assert ok, f"sombra ad hoc introduzida: box-shadow: {limpo}"

    # Os tokens de sombra sao poucos e explicitos.
    tokens = set(re.findall(r"--sombra-([a-z]+):", folha))
    assert tokens <= {"cartao", "hero"}, f"tokens de sombra demais: {tokens}"

    # Gradiente: contado, e so nos lugares autorizados.
    linhas_com_gradiente = [
        linha.strip()
        for linha in folha.splitlines()
        if "gradient(" in linha and not linha.strip().startswith("#")
    ]
    assert "radial-gradient" not in folha, "gradiente radial nunca foi autorizado"
    assert len(linhas_com_gradiente) <= 4, (
        "gradiente em lugares demais — autorizados: cabecalho, preset ativo, "
        f"regua do resultado:\n" + "\n".join(linhas_com_gradiente)
    )


# ---------------------------------------------------------------------------
# Stack e configuracao (§12)
# ---------------------------------------------------------------------------


def _requisitos(nome: str) -> list[str]:
    texto = (RAIZ / nome).read_text(encoding="utf-8")
    return [
        linha.strip()
        for linha in texto.splitlines()
        if linha.strip() and not linha.strip().startswith("#")
    ]


def test_versoes_fixadas_com_igual_igual() -> None:
    """§3 camada B: fixa a versao com ==, NUNCA >= nem faixa.

    Vale para os DOIS arquivos: o runtime que o Streamlit Cloud instala e o de
    desenvolvimento. Uma faixa no dev tambem quebra a reprodutibilidade do
    reteste visual, que e o que a camada B exige.
    """
    for nome in ("requirements.txt", "requirements-dev.txt"):
        linhas = _requisitos(nome)
        assert linhas, f"{nome} vazio"
        for linha in linhas:
            if linha.startswith("-r "):
                continue  # inclusao de outro arquivo
            assert "==" in linha, f"{nome}: versao nao fixada com ==: {linha!r}"
            assert (
                ">=" not in linha and "~=" not in linha and "<" not in linha
            ), f"{nome}: faixa de versao proibida: {linha!r}"

    assert any(l.startswith("streamlit==") for l in _requisitos("requirements.txt"))


def test_runtime_nao_carrega_dependencia_de_desenvolvimento() -> None:
    """O que o Streamlit Cloud instala e SO o que o app importa.

    O Community Cloud hiberna apos 12 h sem trafego e a probabilidade de o app
    estar dormindo na visita e MUITO ALTA (plano §9, risco 6). Cada pacote a
    menos e menos tempo entre o vendedor abrir o link e o cliente ver a tela.

    Este teste tambem pega o inverso, que e o erro perigoso: um pacote que o app
    passou a importar e que ficou so no dev — ali o app quebraria no deploy e
    funcionaria na sua maquina.
    """
    import ast

    runtime = {
        linha.split("==")[0].strip().lower()
        for linha in _requisitos("requirements.txt")
    }

    # O que o app de fato importa, por AST — nao por memoria.
    externos: set[str] = set()
    for caminho in ARQUIVOS_PY_APP:
        arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                externos |= {a.name.split(".")[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
                externos.add(no.module.split(".")[0])

    # Nomes de import != nomes de distribuicao.
    distribuicao = {"fpdf": "fpdf2"}
    padrao_ou_local = {
        "src", "pipeline", "testes", "__future__", "dataclasses", "typing",
        "pathlib", "functools", "base64", "io", "json", "re", "ast",
        "unicodedata", "datetime", "collections", "math", "html", "os", "sys",
        "subprocess", "time", "urllib",
    }
    usados = {
        distribuicao.get(nome, nome)
        for nome in externos - padrao_ou_local
    }

    faltando = usados - runtime
    assert not faltando, (
        f"o app importa {sorted(faltando)} mas isso nao esta em "
        f"requirements.txt — quebraria no deploy e funcionaria na sua maquina"
    )

    sobrando = runtime - usados
    assert not sobrando, (
        f"requirements.txt instala {sorted(sobrando)} que o app nao importa — "
        f"mova para requirements-dev.txt"
    )


def test_dependencias_de_teste_nao_estao_no_runtime() -> None:
    dev = {l.split("==")[0].strip().lower() for l in _requisitos("requirements-dev.txt")}
    runtime = {l.split("==")[0].strip().lower() for l in _requisitos("requirements.txt")}
    for pacote in ("pytest", "openpyxl"):
        assert pacote in dev, f"{pacote} precisa estar no dev"
        assert pacote not in runtime, (
            f"{pacote} nao deve ser instalado em producao"
        )


def test_page_config_correto() -> None:
    """§12: layout="wide", initial_sidebar_state="collapsed"."""
    fonte = (RAIZ / "app.py").read_text(encoding="utf-8")
    assert 'layout="wide"' in fonte
    assert 'initial_sidebar_state="collapsed"' in fonte


def test_marca_do_framework_ocultada() -> None:
    """§6.1.9: menu, rodape, "Made with Streamlit" e Deploy ocultos."""
    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")
    for seletor in ("MainMenu", "stAppDeployButton", "stToolbar", "streamlit.io"):
        assert seletor in folha, f"seletor de ocultacao ausente: {seletor}"


def test_ganchos_de_css_que_envolvem_filhos_usam_container_key() -> None:
    """Um <div> injetado por st.markdown NAO envolve os elementos seguintes.

    Regressao de um defeito real: os botoes de cenario estavam embrulhados em
    `st.markdown('<div class="st-cenarios">')`, que abre e FECHA a propria div.
    O seletor `.st-cenarios button` nunca casava, os botoes ficavam em ~52px em
    vez de 96px, e o protagonista da tela deixava de ser o protagonista. So
    apareceu numa captura de tela.

    Regra: todo seletor de CSS que precisa ENVOLVER filhos usa a classe
    `st-key-*`, gerada por st.container(key=...), que e API publica.
    """
    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")

    # Nenhuma classe propria e usada como ancestral de um seletor do Streamlit.
    ancestrais_proibidos = re.findall(
        r"\.st-(?!key-)[a-z-]+\s+\[data-testid=", folha
    )
    assert not ancestrais_proibidos, (
        "estes seletores usam uma classe injetada como ancestral e nao vao "
        f"casar: {ancestrais_proibidos}. Use st.container(key=...) e .st-key-*"
    )

    # Os dois lados precisam casar, nos dois sentidos: toda classe .st-key-*
    # citada no CSS corresponde a um st.container(key=...) real, e todo
    # container com key tem regra de CSS.
    declaradas = set(re.findall(r"\.st-key-([A-Za-z0-9_]+)", folha))
    existentes = chaves_de_container()

    assert declaradas <= existentes, (
        f"CSS referencia container inexistente: {sorted(declaradas - existentes)}"
    )
    assert existentes <= declaradas, (
        f"container com key sem regra de CSS: {sorted(existentes - declaradas)}"
    )


def test_botoes_de_cenario_tem_96px() -> None:
    """§3.4 / §12: "Cada botao de cenario tem >= 96px de altura."

    O maior alvo da tela. E o protagonista.
    """
    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")
    trecho = folha[folha.index(".st-key-cenarios") :][:600]
    alturas = [int(v) for v in re.findall(r"height:\s*(\d+)px", trecho)]
    assert alturas, "nenhuma altura declarada para os botoes de cenario"
    assert min(alturas) >= 96, f"altura menor que 96px: {alturas}"


def test_alvos_de_toque_minimos() -> None:
    """§3.4: minimo global 56px; polegar do slider >= 32px."""
    folha = (RAIZ / "src" / "css.py").read_text(encoding="utf-8")
    assert "height: 56px" in folha, "number_input precisa de 56px de altura"
    assert re.search(r'\[role="slider"\][^}]*height:\s*3[2-9]px', folha, re.S), (
        "o polegar do slider precisa de >= 32px"
    )


def test_presets_escritos_por_on_click() -> None:
    """§5.3 / §12: escrever a chave de um widget depois de instanciado levanta
    StreamlitAPIException. Por isso e on_click."""
    fonte = (RAIZ / "src" / "componentes" / "botoes_cenario.py").read_text(
        encoding="utf-8"
    )
    assert "on_click=aplicar_preset" in fonte


def test_estado_ativo_do_preset_e_derivado() -> None:
    """§5.3: "O estado ativo e DERIVADO, nao guardado."

    Impossibilita a tela mostrar "REALISTA" aceso com o slider em 27%.
    """
    from src import estado

    assert not any("preset_ativo" in c for c in estado._DEFAULTS), (
        "o preset ativo nao pode ser guardado em session_state"
    )
    fonte = (RAIZ / "src" / "componentes" / "botoes_cenario.py").read_text(
        encoding="utf-8"
    )
    assert "preset_ativo(e)" in fonte


def test_slider_nao_altera_o_traseiro() -> None:
    """§5.4: "Mover o slider NAO altera o traseiro."

    Acoplar os dois recriaria exatamente o risco n. 1 do plano.

    A checagem e estrutural: nenhum `Name`/`Attribute` chamado K_CONV_T aparece
    no codigo executavel do modulo. Busca textual nao serve — o proprio arquivo
    comenta "nenhuma escrita em K_CONV_T", e um `not in` no texto reprovaria a
    documentacao que garante a regra.
    """
    caminho = RAIZ / "src" / "componentes" / "slider_ajuste_fino.py"
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))

    referencias = [
        no.lineno
        for no in ast.walk(arvore)
        if (isinstance(no, ast.Name) and no.id == "K_CONV_T")
        or (isinstance(no, ast.Attribute) and no.attr == "K_CONV_T")
    ]
    assert not referencias, (
        f"o slider do dianteiro referencia K_CONV_T nas linhas {referencias} "
        f"— mover o slider nao pode alterar o traseiro (§5.4)"
    )


# ---------------------------------------------------------------------------
# Fronteiras de arquitetura
# ---------------------------------------------------------------------------


def test_pipeline_nao_e_importado_pelo_app() -> None:
    """A fronteira app | pipeline. O pipeline e passo de build."""
    culpados = arquivos_que_importam("pipeline", dentro_de="src")
    culpados += arquivos_que_importam("pipeline", dentro_de="app.py")
    assert not culpados, (
        "o pipeline nunca e importado pelo app:\n" + "\n".join(culpados)
    )


def test_calculo_e_puro() -> None:
    """calculo.py nao importa streamlit — e o que torna os 16 casos
    executaveis sem subir o app."""
    culpados = arquivos_que_importam("streamlit", dentro_de="src/calculo.py")
    culpados += arquivos_que_importam("streamlit", dentro_de="src/formato.py")
    culpados += arquivos_que_importam("streamlit", dentro_de="src/plausibilidade.py")
    culpados += arquivos_que_importam("streamlit", dentro_de="src/parametros.py")
    assert not culpados, "\n".join(culpados)


def test_tela1_nao_le_planilha_nem_faz_requisicao() -> None:
    """P11 / §7.1 / §12: "A Tela 1 nao le planilha nem faz requisicao externa
    alguma na carga inicial.\""""
    alvo = "src/telas/tela1_simulador.py"
    for modulo in (
        "requests",
        "urllib",
        "httpx",
        "openpyxl",
        "src.dados.carregar_snapshot",
    ):
        culpados = arquivos_que_importam(modulo, dentro_de=alvo)
        assert not culpados, (
            f"a Tela 1 nao pode depender de {modulo}:\n" + "\n".join(culpados)
        )


def test_todos_os_16_casos_tem_teste() -> None:
    """§12: "Todos os 16 casos-teste tem teste automatizado correspondente.\""""
    import json

    casos = json.loads(
        (RAIZ / "testes" / "casos.json").read_text(encoding="utf-8")
    )
    esperados = {f"T{n}" for n in range(1, 17)}
    declarados = {k for k in casos if k.startswith("T") and k[1:].isdigit()}
    assert declarados == esperados, f"faltando: {esperados - declarados}"

    fontes = "\n".join(
        p.read_text(encoding="utf-8") for p in (RAIZ / "testes").glob("test_*.py")
    )
    for caso in sorted(esperados):
        assert re.search(rf"def test_{caso}_", fontes), (
            f"{caso} nao tem teste automatizado correspondente"
        )

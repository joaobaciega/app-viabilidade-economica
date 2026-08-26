"""A base de precos da original: gerador, leitor e Tela 3.

Tres camadas, na ordem em que o dado atravessa o projeto:

    aba app_precos  ->  pipeline.gerar_precos  ->  dados/precos.json
                    ->  src.dados.carregar_precos  ->  Tela 3

O que estes testes protegem, em uma frase cada:

  - CELULA VAZIA NUNCA VIRA ZERO nem `False`. Preco ausente e `None`, e
    `tem_traseiro` vazio significa "nao apurado", nao "nao tem". Sao os dois
    jeitos de o app afirmar sozinho algo que a coleta nao apurou.
  - O LEITOR NUNCA LEVANTA. Base ausente, ilegivel ou de outro schema devolve
    base vazia com o motivo — nunca stack trace na frente do cliente (§7.4).
  - A TELA NAO MOSTRA NADA ALEM DO MENU antes da escolha da marca, e mostra a
    ESTRUTURA COM "—" para as marcas que ainda nao passaram pela coleta.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from pipeline.gerar_precos import ABA, ErroDeBase, ler_base, montar
from src.dados import carregar_precos

RAIZ = Path(__file__).resolve().parents[1]
PLANILHA = RAIZ / "emplacamentos_brasil_base.xlsx"

TEMPO = 120


def _linha(**overrides) -> dict:
    """Uma linha da aba `app_precos`, com tudo preenchido."""
    linha = {
        "id_modelo": "Fiat|Strada",
        "marca": "Fiat",
        "modelo": "Strada",
        "categoria": "picape",
        "emplacamentos_2026_ytd": 97941,
        "pn_dianteiro": "7092277",
        "preco_dianteiro_par_brl": 178.27,
        "preco_dianteiro_min_brl": 178.27,
        "preco_dianteiro_max_brl": 399.0,
        "ofertas_dianteiro": 2,
        "tem_traseiro": "nao",
        "pn_traseiro": None,
        "preco_traseiro_unid_brl": None,
        "preco_veiculo_completo_brl": 178.27,
        "canal_preco": "Loja oficial Fiat no Mercado Livre",
        "url_preco_dianteiro": "https://exemplo/dianteiro",
        "url_preco_traseiro": None,
        "data_consulta": "2026-08-26",
        "status_preco": "completo",
        "observacao": "Duas ofertas do mesmo codigo.",
    }
    linha.update(overrides)
    return linha


def _um(linha: dict) -> dict:
    """O modelo montado a partir de uma unica linha."""
    return montar([linha])["marcas"][linha["marca"]]["modelos"][0]


# ---------------------------------------------------------------------------
# Gerador — leitura da planilha real
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not PLANILHA.exists(), reason="planilha de curadoria ausente")
def test_planilha_real_tem_as_18_marcas_e_os_80_modelos() -> None:
    dados = montar(ler_base(PLANILHA))
    assert len(dados["marcas"]) == 18
    assert sum(len(m["modelos"]) for m in dados["marcas"].values()) == 80


@pytest.mark.skipif(not PLANILHA.exists(), reason="planilha de curadoria ausente")
def test_planilha_real_preserva_a_ordem_de_emplacamento_da_marca() -> None:
    """A curadoria ordena por emplacamento; `posicao` grava essa ordem."""
    modelos = montar(ler_base(PLANILHA))["marcas"]["Fiat"]["modelos"]
    assert [m["modelo"] for m in modelos[:3]] == ["Strada", "Argo", "Mobi"]
    assert [m["posicao"] for m in modelos] == list(range(1, len(modelos) + 1))


def test_aba_ausente_para_o_build_com_erro_legivel(tmp_path: Path) -> None:
    """Renomear a aba nao pode virar JSON pela metade (plano §6.4)."""
    import openpyxl

    caminho = tmp_path / "sem_aba.xlsx"
    livro = openpyxl.Workbook()
    livro.active.title = "outra_coisa"
    livro.save(caminho)

    with pytest.raises(ErroDeBase) as erro:
        ler_base(caminho)
    assert ABA in str(erro.value)
    assert "outra_coisa" in str(erro.value)


def test_coluna_renomeada_para_o_build_com_o_cabecalho_na_mensagem(
    tmp_path: Path,
) -> None:
    import openpyxl

    caminho = tmp_path / "coluna_renomeada.xlsx"
    livro = openpyxl.Workbook()
    aba = livro.active
    aba.title = ABA
    cabecalho = list(_linha())
    cabecalho[cabecalho.index("preco_dianteiro_par_brl")] = "preco_par"
    aba.append(cabecalho)
    aba.append(list(_linha().values()))
    livro.save(caminho)

    with pytest.raises(ErroDeBase) as erro:
        ler_base(caminho)
    assert "preco_dianteiro_par_brl" in str(erro.value)


# ---------------------------------------------------------------------------
# Gerador — coercao de campo
# ---------------------------------------------------------------------------


def test_preco_vazio_vira_null_e_nunca_zero() -> None:
    """Zero seria uma afirmacao de preco que a coleta nao faz."""
    modelo = _um(
        _linha(
            preco_dianteiro_par_brl=None,
            preco_traseiro_unid_brl=None,
            preco_veiculo_completo_brl=None,
        )
    )
    assert modelo["preco_dianteiro_par"] is None
    assert modelo["preco_traseiro_unid"] is None
    assert modelo["preco_veiculo_completo"] is None


def test_tem_traseiro_vazio_vira_null_e_nao_false() -> None:
    """Vazio = ninguem verificou. `False` afirmaria que o carro nao tem."""
    assert _um(_linha(tem_traseiro=None))["tem_traseiro"] is None
    assert _um(_linha(tem_traseiro=""))["tem_traseiro"] is None
    assert _um(_linha(tem_traseiro="sim"))["tem_traseiro"] is True
    assert _um(_linha(tem_traseiro="nao"))["tem_traseiro"] is False


def test_part_number_numerico_sai_como_texto_sem_o_ponto_zero() -> None:
    """`52083318.0` na tela de um produto auditavel e defeito."""
    modelo = _um(_linha(pn_traseiro=52083318.0, tem_traseiro="sim"))
    assert modelo["pn_traseiro"] == "52083318"


def test_marca_ou_modelo_vazio_para_o_build() -> None:
    with pytest.raises(ErroDeBase):
        montar([_linha(marca=None)])
    with pytest.raises(ErroDeBase):
        montar([_linha(modelo=None)])


# ---------------------------------------------------------------------------
# Leitor — NUNCA levanta (§7.4)
# ---------------------------------------------------------------------------


def _carregar_de(caminho: Path) -> carregar_precos.BasePrecos:
    """Le uma base especifica, driblando o @st.cache_data."""
    original = carregar_precos.ARQUIVO
    carregar_precos.ARQUIVO = caminho
    try:
        return carregar_precos.carregar.__wrapped__()
    finally:
        carregar_precos.ARQUIVO = original


def test_base_ausente_devolve_vazia_com_motivo(tmp_path: Path) -> None:
    base = _carregar_de(tmp_path / "nao_existe.json")
    assert base.marcas == {}
    assert base.indisponivel
    assert "nenhum" in base.rotulo_versao().lower()


def test_base_ilegivel_devolve_vazia_sem_levantar(tmp_path: Path) -> None:
    caminho = tmp_path / "quebrada.json"
    caminho.write_text("{ isto nao e json", encoding="utf-8")

    base = _carregar_de(caminho)
    assert base.marcas == {}
    assert "ilegível" in base.indisponivel


def test_schema_incompativel_e_recusado_sem_tela_branca(tmp_path: Path) -> None:
    caminho = tmp_path / "futura.json"
    caminho.write_text(
        json.dumps({"schema_versao": 99, "marcas": {}}), encoding="utf-8"
    )

    base = _carregar_de(caminho)
    assert base.marcas == {}
    assert "99" in base.indisponivel


def test_base_malformada_devolve_vazia_sem_levantar(tmp_path: Path) -> None:
    caminho = tmp_path / "malformada.json"
    caminho.write_text(
        json.dumps({"schema_versao": 1, "marcas": {"Fiat": "não é um dicionário"}}),
        encoding="utf-8",
    )

    base = _carregar_de(caminho)
    assert base.marcas == {}
    assert "malformada" in base.indisponivel


# ---------------------------------------------------------------------------
# Leitor — a divergencia deliberada: marca SEM preco entra no seletor
# ---------------------------------------------------------------------------


def _base_publicada() -> carregar_precos.BasePrecos:
    return carregar_precos.carregar.__wrapped__()


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_o_seletor_lista_as_18_marcas_inclusive_as_sem_preco() -> None:
    """Divergencia declarada: a Tela 2 filtra marca sem dado, esta NAO."""
    base = _base_publicada()
    assert len(base.nomes_de_marca) == 18
    assert "Volkswagen" in base.nomes_de_marca
    assert base.marcas["Volkswagen"].modelos_com_preco == 0


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_a_data_e_convertida_uma_vez_na_carga() -> None:
    """A tela nunca formata data — a conversao acontece aqui."""
    strada = _base_publicada().marcas["Fiat"].modelos[0]
    assert strada.data_consulta == "26/08/2026"


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_o_rotulo_de_versao_diz_quantos_modelos_foram_coletados() -> None:
    """A cobertura anda junto com o numero, como os totais da Tela 2."""
    rotulo = _base_publicada().rotulo_versao()
    assert "5 de 80" in rotulo


# ---------------------------------------------------------------------------
# Tela 3 — o que de fato chega na tela
# ---------------------------------------------------------------------------


def _tela3(marca: str | None = None) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=TEMPO)
    at.run()
    at.radio(key="tela_ativa").set_value("Preço original").run()
    if marca is not None:
        at.selectbox(key="tela3_marca").set_value(marca).run()
    return at


def _texto(at: AppTest) -> str:
    """Todo o conteudo renderizado, SEM a folha de estilo.

    A folha da camada B contem os nomes de todas as classes e seria casada por
    qualquer busca por "st-kpi-valor" ou pelo travessao.
    """
    blocos = [
        m.value for m in at.markdown if not m.value.lstrip().startswith("<style>")
    ]
    return "\n".join(blocos + [c.value for c in at.caption])


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_sem_marca_escolhida_nao_aparece_nada_alem_do_menu() -> None:
    """O requisito do cliente: nem cartao, nem campo de preco, nem lista."""
    at = _tela3()

    assert len(at.selectbox) == 1
    assert at.selectbox[0].value is None
    # Os campos de refil so existem depois da escolha.
    assert not [n for n in at.number_input if n.key in ("preco_dianteiro",
                                                        "preco_traseiro")]

    texto = _texto(at)
    assert "Strada" not in texto
    assert "MENOS CÓDIGO NA PRATELEIRA" not in texto


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_o_menu_abre_vazio_com_as_18_marcas() -> None:
    seletor = _tela3().selectbox[0]
    assert seletor.value is None
    assert len(seletor.options) == 18


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_marca_com_preco_mostra_os_valores_coletados() -> None:
    texto = _texto(_tela3("Fiat"))

    assert "STRADA" in texto
    assert "R$ 178,27" in texto
    assert "7092277" in texto
    assert "26/08/2026" in texto
    # O Pulse tem dianteiro mas nao tem traseiro coletado.
    assert "PULSE" in texto


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_marca_sem_coleta_mostra_a_estrutura_com_travessao() -> None:
    """A estrutura fica pronta; o valor NAO e inventado."""
    texto = _texto(_tela3("Volkswagen"))

    assert "POLO" in texto
    assert "Dianteiro · por par" in texto
    assert "Traseiro · por unidade" in texto
    assert "Veículo completo" in texto
    assert "—" in texto
    assert "ainda não passou pela coleta" in texto
    # Nenhum preco aparece para uma marca sem coleta.
    assert "R$" not in texto


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_a_economia_compara_dianteiro_com_dianteiro() -> None:
    at = _tela3("Fiat")
    at.number_input(key="preco_dianteiro").set_value(89.90).run()

    texto = _texto(at)
    assert "Cliente economiza R$ 88,37" in texto
    assert "Requer armação em bom estado" in texto


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_sem_preco_da_original_nao_ha_economia() -> None:
    """Marca sem coleta com o refil preenchido: nenhuma conta na tela."""
    at = _tela3("Volkswagen")
    at.number_input(key="preco_dianteiro").set_value(89.90).run()

    assert "Cliente economiza" not in _texto(at)


@pytest.mark.skipif(
    not carregar_precos.ARQUIVO.exists(), reason="dados/precos.json não publicado"
)
def test_a_procedencia_declara_a_cobertura_da_coleta() -> None:
    """O numero nunca aparece sozinho quando falta modelo dentro dele."""
    texto = _texto(_tela3("Fiat"))
    assert "5 de 5 modelos de Fiat" in texto
    assert "5 de 80 no total" in texto

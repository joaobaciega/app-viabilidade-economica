"""O PDF do cenario — componente +18, gerado no servidor.

O documento SAI DA SALA. Por isso ele obedece as mesmas regras de vocabulario
da tela, e carrega marca-d'agua quando inclui o custo de aquisicao (que e o
preco de venda da Suicatech, plano §6.3).
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from src.calculo import calcular
from src.componentes.exportador_pdf import gerar_pdf
from testes.conftest import entradas_do_caso


def _pdf(nome_do_caso: str = "T1", cliente: str = "") -> bytes:
    entradas = entradas_do_caso(nome_do_caso)
    return gerar_pdf(entradas, calcular(entradas), cliente)


def _texto_do_pdf(dados: bytes) -> str:
    """Extrai texto legivel do PDF sem dependencia extra.

    fpdf2 escreve os literais de texto entre parenteses nos operadores Tj/TJ.
    Isso basta para verificar presenca e ausencia de vocabulario, que e o que
    interessa aqui.
    """
    import re
    import zlib

    partes: list[str] = []
    for fluxo in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", dados, re.S):
        try:
            conteudo = zlib.decompress(fluxo)
        except zlib.error:
            conteudo = fluxo
        for literal in re.findall(rb"\((?:[^()\\]|\\.)*\)", conteudo):
            partes.append(
                literal[1:-1]
                .replace(b"\\(", b"(")
                .replace(b"\\)", b")")
                .decode("latin-1", "ignore")
            )
    return " ".join(partes)


def test_pdf_e_gerado() -> None:
    dados = _pdf()
    assert dados.startswith(b"%PDF"), "saida precisa ser um PDF valido"
    assert len(dados) > 1000


def test_pdf_traz_os_numeros_do_cenario() -> None:
    texto = _texto_do_pdf(_pdf())
    assert "141.480" in texto
    assert "3 a cada 10" in texto


def test_pdf_nunca_escreve_lucro() -> None:
    """P12 / §6.1.9 — inclusive no PDF."""
    texto = _texto_do_pdf(_pdf()).lower()
    assert "lucro" not in texto
    assert "margem de contribui" in texto


def test_pdf_marca_dagua_quando_inclui_custo() -> None:
    """O custo de aquisicao E o preco de venda da Suicatech (plano §6.3)."""
    texto = _texto_do_pdf(_pdf())
    assert "DOCUMENTO INTERNO" in texto, (
        "o PDF com custo precisa sair marcado como interno"
    )


def test_pdf_sem_custo_nao_leva_marca_dagua() -> None:
    """Sem NENHUM custo o documento pode circular — inclusive o da original,
    que tambem e informacao de negociacao."""
    entradas = replace(
        entradas_do_caso("T1"),
        custo_dianteiro=None,
        custo_traseiro=None,
        custo_original=None,
    )
    # Sem custo o calculo entra em E1b, mas o documento ainda e gerado.
    texto = _texto_do_pdf(gerar_pdf(entradas, calcular(entradas)))
    assert "DOCUMENTO INTERNO" not in texto


def test_pdf_declara_as_decisoes_em_aberto() -> None:
    """Um PDF que sai da sala sem dizer o que nao foi decidido e pior que a
    tela, porque ninguem esta ao lado para explicar."""
    texto = _texto_do_pdf(_pdf())
    assert "ainda n" in texto  # "ainda nao considera"
    assert "rampa" in texto.lower()


def test_pdf_rotulo_do_anual_descreve_a_conta() -> None:
    texto = _texto_do_pdf(_pdf())
    assert "ano cheio em regime" in texto
    assert "primeiros 12 meses" not in texto


def test_pdf_cashback_declara_quem_paga_e_nao_desconta() -> None:
    entradas = replace(
        entradas_do_caso("T1"),
        cashback_dianteiro=(10.0, 3.0, 2.0),
        cashback_traseiro=(4.0, 1.5, 1.0),
    )
    resultado = calcular(entradas)
    texto = _texto_do_pdf(gerar_pdf(entradas, resultado))

    assert "pago pela Suicatech" in texto
    # O rateio por destinatario vai impresso.
    for nome in ("Consultor", "Gerente", "Marketing"):
        assert nome in texto, nome
    # O valor do resultado NAO muda.
    assert "141.480" in texto
    assert resultado.incremental_mensal == pytest.approx(11790.0, abs=0.005)


def test_pdf_declara_que_nao_ha_canibalizacao() -> None:
    """A premissa mais favoravel vai IMPRESSA: o documento sai da sala e
    ninguem estara ao lado para explicar."""
    texto = _texto_do_pdf(_pdf())
    assert "Canibaliza" in texto
    assert "venda nova" in texto


def test_pdf_traducao_vem_antes_do_anual() -> None:
    """§5.5 — a ordem de leitura vale no documento tambem."""
    texto = _texto_do_pdf(_pdf())
    assert texto.index("3 a cada 10") < texto.index("141.480")


def test_pdf_com_nome_do_cliente() -> None:
    texto = _texto_do_pdf(_pdf(cliente="Concessionária Exemplo"))
    assert "Concession" in texto


def test_pdf_sem_ancora_nao_inventa_valor() -> None:
    """E1 no documento: nenhum valor anual, e a explicacao do porque."""
    entradas = entradas_do_caso("T5")
    texto = _texto_do_pdf(gerar_pdf(entradas, calcular(entradas)))
    assert "141.480" not in texto
    assert "0,00" not in texto
    assert "margem de contribui" in texto.lower()

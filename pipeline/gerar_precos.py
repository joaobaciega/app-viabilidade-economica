"""Publicacao dos precos da palheta original: xlsx -> JSON versionado.

Mesma fronteira de `gerar_emplacamentos.py` e `publicar.py`: RODA NA SUA MAQUINA
OU NO CI, NUNCA NO NAVEGADOR. Este modulo nao e importado por src/ nem por
app.py (testes/test_checklist.py garante).

POR QUE ESTE PASSO EXISTE, e nao ler o xlsx direto na Tela 3: ler xlsx em
runtime exigiria openpyxl no requirements.txt, e o checklist PROIBE. O JSON
gerado aqui nao custa dependencia nenhuma: a Tela 3 le com o `json` da
biblioteca padrao.

Uso:
    python -m pipeline.gerar_precos
    python -m pipeline.gerar_precos --conferir      # valida sem gravar
    python -m pipeline.gerar_precos --base outra.xlsx

Codigo de saida:
    0  gerado (ou conferencia sem falhas)
    2  erro de leitura da planilha (aba ausente, coluna renomeada, base vazia)

NENHUM VALOR E ESTIMADO. Celula de preco vazia vira `null` — NUNCA zero. Zero
seria uma afirmacao de preco que a coleta nao faz.

TRES ESTADOS EM `tem_traseiro`, e nao dois: "sim", "nao" e VAZIO. Vazio
significa que nem sequer foi verificado se o veiculo tem limpador traseiro, e
vira `null`. Coagir vazio para `false` afirmaria, em 29 modelos, que o carro nao
tem limpador traseiro — coisa que ninguem apurou.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE_PADRAO = RAIZ / "emplacamentos_brasil_base.xlsx"
SAIDA_PADRAO = RAIZ / "dados" / "precos.json"

ABA = "app_precos"
SCHEMA_VERSAO = 1

# As colunas do xlsx que precisam existir. Renomear uma delas para o build
# aqui, com mensagem legivel, em vez de sair um JSON pela metade.
COLUNAS = (
    "id_modelo",
    "marca",
    "modelo",
    "categoria",
    "emplacamentos_2026_ytd",
    "pn_dianteiro",
    "preco_dianteiro_par_brl",
    "preco_dianteiro_min_brl",
    "preco_dianteiro_max_brl",
    "ofertas_dianteiro",
    "tem_traseiro",
    "pn_traseiro",
    "preco_traseiro_unid_brl",
    "preco_veiculo_completo_brl",
    "canal_preco",
    "url_preco_dianteiro",
    "url_preco_traseiro",
    "data_consulta",
    "status_preco",
    "observacao",
)

# Rotulo da janela de emplacamento exibida ao lado do modelo. Fica AQUI e nao na
# tela, pelo mesmo motivo das JANELAS de gerar_emplacamentos: e um atributo do
# recorte da fonte, e muda junto com a edicao do informativo.
JANELA_EMPLACAMENTO = "jan–jul/2026"


class ErroDeBase(Exception):
    """Aba ausente, coluna renomeada ou base vazia. Erro claro, nao tela branca."""


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------


def ler_base(caminho: Path) -> list[dict]:
    """Le a aba `app_precos` e devolve uma lista de dicionarios, uma por modelo."""
    import openpyxl

    if not caminho.exists():
        raise ErroDeBase(f"base não encontrada: {caminho}")

    livro = openpyxl.load_workbook(caminho, data_only=True, read_only=True)
    try:
        if ABA not in livro.sheetnames:
            raise ErroDeBase(
                f"aba obrigatória '{ABA}' ausente. "
                f"Abas encontradas: {livro.sheetnames}"
            )

        linhas = livro[ABA].iter_rows(values_only=True)
        try:
            cabecalho = [str(c).strip() if c is not None else "" for c in next(linhas)]
        except StopIteration:
            raise ErroDeBase(f"aba '{ABA}' está completamente vazia")

        faltando = [c for c in COLUNAS if c not in cabecalho]
        if faltando:
            raise ErroDeBase(
                f"aba '{ABA}': coluna(s) ausente(s) ou renomeada(s): {faltando}. "
                f"Cabeçalho encontrado: {cabecalho}"
            )

        registros = [
            {k: _normalizar(v) for k, v in zip(cabecalho, valores) if k}
            for valores in linhas
            if valores is not None and any(v is not None for v in valores)
        ]
    finally:
        livro.close()

    if not registros:
        raise ErroDeBase(f"aba '{ABA}' não tem nenhuma linha de dado")

    return registros


def _normalizar(valor: object) -> object:
    """Converte tipos do openpyxl em algo serializavel em JSON."""
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, str):
        return valor.strip()
    return valor


# ---------------------------------------------------------------------------
# Coercao de campo
# ---------------------------------------------------------------------------


def _texto(valor: object) -> str | None:
    """Texto da planilha, ou None. Celula vazia NUNCA vira string vazia.

    `pn_traseiro` e numerico puro na planilha (52083318). Sem o corte do `.0`
    o codigo apareceria como `52083318.0` na tela do cliente, numa tela cuja
    unica funcao e ser auditavel.
    """
    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    texto = str(valor).strip()
    return texto or None


def _preco(valor: object) -> float | None:
    """Preco da planilha, ou None. NUNCA devolve zero por engano.

    Celula vazia significa preco NAO COLETADO. Zero seria uma afirmacao de
    preco que a coleta nao faz, e passaria batido por qualquer soma adiante.
    """
    if valor is None or isinstance(valor, bool):
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _inteiro(valor: object) -> int | None:
    """Contagem da planilha (emplacamento, nº de ofertas), ou None."""
    if valor is None or isinstance(valor, bool):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _tres_estados(valor: object) -> bool | None:
    """'sim' -> True, 'nao' -> False, vazio -> None. Ver o cabecalho do modulo."""
    texto = _texto(valor)
    if texto is None:
        return None
    normal = texto.lower()
    if normal in ("sim", "s", "true"):
        return True
    if normal in ("nao", "não", "n", "false"):
        return False
    return None


# ---------------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------------


def montar(registros: list[dict]) -> dict:
    """Agrupa por marca, PRESERVANDO a ordem em que a base lista.

    A ordem das linhas dentro de uma marca ja e a ordem de emplacamento
    decrescente, feita pela curadoria. `posicao` grava essa ordem para a tela
    nao ter que reordenar nada — e para ela nao mudar se a planilha for
    reordenada por engano.
    """
    marcas: dict[str, dict] = {}

    for linha, r in enumerate(registros, start=2):  # +2: cabecalho e base 1
        nome = _texto(r.get("marca"))
        if nome is None:
            raise ErroDeBase(f"linha {linha}: coluna 'marca' vazia")

        modelo = _texto(r.get("modelo"))
        if modelo is None:
            raise ErroDeBase(f"linha {linha} ({nome}): coluna 'modelo' vazia")

        marca = marcas.setdefault(nome, {"modelos": []})
        marca["modelos"].append(
            {
                "modelo": modelo,
                "categoria": _texto(r.get("categoria")) or "",
                "posicao": len(marca["modelos"]) + 1,
                "emplacamentos": _inteiro(r.get("emplacamentos_2026_ytd")),
                "pn_dianteiro": _texto(r.get("pn_dianteiro")),
                "preco_dianteiro_par": _preco(r.get("preco_dianteiro_par_brl")),
                "preco_dianteiro_min": _preco(r.get("preco_dianteiro_min_brl")),
                "preco_dianteiro_max": _preco(r.get("preco_dianteiro_max_brl")),
                "ofertas_dianteiro": _inteiro(r.get("ofertas_dianteiro")),
                "tem_traseiro": _tres_estados(r.get("tem_traseiro")),
                "pn_traseiro": _texto(r.get("pn_traseiro")),
                "preco_traseiro_unid": _preco(r.get("preco_traseiro_unid_brl")),
                "preco_veiculo_completo": _preco(
                    r.get("preco_veiculo_completo_brl")
                ),
                "canal": _texto(r.get("canal_preco")),
                "url_dianteiro": _texto(r.get("url_preco_dianteiro")),
                "url_traseiro": _texto(r.get("url_preco_traseiro")),
                "data_consulta": _texto(r.get("data_consulta")),
                "status": _texto(r.get("status_preco")) or "sem preco",
                "nota": _texto(r.get("observacao")) or "",
            }
        )

    return {
        "schema_versao": SCHEMA_VERSAO,
        "janela_emplacamento": JANELA_EMPLACAMENTO,
        "marcas": dict(sorted(marcas.items())),
    }


def _com_preco(dados: dict) -> list[dict]:
    """Os modelos que tem preco do dianteiro publicado."""
    return [
        m
        for marca in dados["marcas"].values()
        for m in marca["modelos"]
        if m["preco_dianteiro_par"] is not None
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pipeline.gerar_precos",
        description="Converte a aba app_precos em JSON para a Tela 3.",
    )
    parser.add_argument("--base", type=Path, default=BASE_PADRAO)
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    parser.add_argument(
        "--conferir", action="store_true", help="valida e reporta, sem gravar"
    )
    args = parser.parse_args(argv)

    # flush=True: sem isso o stdout com buffer aparece DEPOIS do stderr e o
    # relatorio fica ilegivel no terminal.
    print(f"Lendo {args.base}", flush=True)
    try:
        registros = ler_base(args.base)
        dados = montar(registros)
    except ErroDeBase as erro:
        print(f"\nERRO DE BASE: {erro}", file=sys.stderr, flush=True)
        return 2

    total = sum(len(m["modelos"]) for m in dados["marcas"].values())
    com_preco = _com_preco(dados)
    print(f"  {len(dados['marcas'])} marca(s), {total} modelo(s)", flush=True)
    print(f"  {len(com_preco)} modelo(s) com preço coletado", flush=True)

    # NAO e falha: a coleta ainda esta em andamento, e a tela mostra "—" no
    # lugar do valor. O relatorio existe para a curadoria conferir o que falta.
    parciais = [
        f"{marca} {m['modelo']}"
        for marca, dados_marca in dados["marcas"].items()
        for m in dados_marca["modelos"]
        if m["status"] == "so dianteiro"
    ]
    if parciais:
        print(
            f"  {len(parciais)} modelo(s) só com o dianteiro "
            f"(a tela escreve '—' no traseiro): {', '.join(parciais)}",
            flush=True,
        )

    sem_traseiro_apurado = [
        f"{marca} {m['modelo']}"
        for marca, dados_marca in dados["marcas"].items()
        for m in dados_marca["modelos"]
        if m["tem_traseiro"] is None
    ]
    if sem_traseiro_apurado:
        print(
            f"  {len(sem_traseiro_apurado)} modelo(s) sem verificação de "
            f"limpador traseiro (a tela escreve 'não verificado')",
            flush=True,
        )

    if args.conferir:
        print("\nModo --conferir: nada gravado.", flush=True)
        return 0

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # `relative_to` levanta se --saida apontar para fora do repo, e falhar
    # DEPOIS de gravar seria o pior dos dois mundos.
    try:
        destino = args.saida.resolve().relative_to(RAIZ)
    except ValueError:
        destino = args.saida
    print(f"\nGerado: {destino} (schema v{SCHEMA_VERSAO})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Fixtures compartilhadas. Carrega testes/casos.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

CASOS = json.loads((Path(__file__).parent / "casos.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def casos() -> dict:
    return CASOS


@pytest.fixture
def base() -> dict:
    """As entradas do cenario base (T1), como dicionario mutavel."""
    return dict(CASOS["base"])


def entradas_do_caso(nome: str):
    """Monta um `Entradas` do caso, aplicando os overrides sobre a base."""
    from src.calculo import Entradas

    dados = dict(CASOS["base"])
    dados.update(CASOS[nome].get("entradas", {}))
    return Entradas(**dados)


def esperado(nome: str) -> dict:
    return CASOS[nome]["esperado"]

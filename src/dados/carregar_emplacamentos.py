"""Carrega a base de emplacamentos publicada por `pipeline.gerar_emplacamentos`.

Consumida SOMENTE pela Tela 2. A Tela 1 nao depende disto (P11, §7.1).

Mesmo contrato de `carregar_snapshot.py`, de proposito — §7.4 (erro de dado):
falha de leitura e erro de PUBLICACAO, e o app publicado nunca deveria ve-la.
Se ainda assim ocorrer em runtime, `carregar()` NUNCA levanta excecao: devolve
uma base vazia com o motivo registrado, a Tela 2 mostra o estado vazio, e a
Tela 1 continua funcionando. Nunca tela branca, nunca stack trace, nunca
conteudo parcial que pareca completo.

REGRA DE NUMERO AUSENTE: a base declara que celula vazia significa numero nao
encontrado na fonte, sem estimativa. Aqui isso vira `None` e a tela escreve
"não publicado". `None` NUNCA vira zero: nao ter dado e diferente de ter zero,
e somar zero no lugar de um numero ausente inventa um total que a fonte nao
sustenta. Por isso os totais desta base andam sempre com a contagem de quantos
modelos entraram neles.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import streamlit as st

ARQUIVO = Path(__file__).resolve().parents[2] / "dados" / "emplacamentos.json"

SCHEMA_SUPORTADO = 1


@dataclass(frozen=True)
class Modelo:
    """Uma linha da base: um modelo dentro de uma marca."""

    modelo: str
    categoria: str
    posicao: int
    atual: int | None = None
    anterior: int | None = None
    fechado: int | None = None
    variacao: float | None = None
    nota: str = ""


@dataclass(frozen=True)
class Marca:
    """Uma marca e os modelos dela, ja ordenados pela posicao na fonte."""

    nome: str
    cobertura: str = ""
    modelos: tuple[Modelo, ...] = ()

    @property
    def total_atual(self) -> int:
        return sum(m.atual for m in self.modelos if m.atual is not None)

    @property
    def total_fechado(self) -> int:
        return sum(m.fechado for m in self.modelos if m.fechado is not None)

    @property
    def modelos_com_atual(self) -> int:
        """Quantos modelos entraram em `total_atual`."""
        return sum(1 for m in self.modelos if m.atual is not None)

    @property
    def modelos_com_fechado(self) -> int:
        """Quantos modelos entraram em `total_fechado`.

        A tela compara com `len(modelos)` e qualifica o total quando falta
        alguem, em vez de exibir uma soma parcial como se fosse o total.
        """
        return sum(1 for m in self.modelos if m.fechado is not None)

    @property
    def variacao(self) -> float | None:
        """Variacao da marca entre as duas janelas comparaveis.

        Calculada SO sobre os modelos que tem numero nas duas pontas — misturar
        um modelo lancado em 2026 na base de comparacao infla a variacao da
        marca inteira. Devolve None quando nenhum modelo e comparavel.
        """
        pares = [
            (m.atual, m.anterior)
            for m in self.modelos
            if m.atual is not None and m.anterior is not None
        ]
        base = sum(anterior for _, anterior in pares)
        if not base:
            return None
        return sum(atual for atual, _ in pares) / base - 1

    @property
    def modelos_comparaveis(self) -> int:
        return sum(
            1
            for m in self.modelos
            if m.atual is not None and m.anterior is not None
        )


@dataclass(frozen=True)
class Base:
    criterio: str = ""
    fonte: str = ""
    url: str = ""
    data_consulta: str = ""
    janelas: dict[str, str] = field(default_factory=dict)
    marcas: dict[str, Marca] = field(default_factory=dict)
    indisponivel: str | None = None

    @property
    def nomes_de_marca(self) -> list[str]:
        """Marcas com modelo publicado. Marca sem dado NAO APARECE no seletor."""
        return sorted(nome for nome, m in self.marcas.items() if m.modelos)

    @property
    def total_de_modelos(self) -> int:
        return sum(len(m.modelos) for m in self.marcas.values())

    def janela(self, chave: str) -> str:
        """Rotulo da janela ('jan–jul/2026'), vazio se a base nao declarar."""
        return self.janelas.get(chave, "")

    def rotulo_versao(self) -> str:
        """A linha de proveniencia da faixa do vendedor. Descreve, nao acusa."""
        if self.indisponivel:
            return f"emplacamentos: {self.indisponivel}"
        if not self.marcas:
            return "nenhuma base de emplacamentos publicada"
        return f"emplacamentos Fenabrave · coletado em {self.data_consulta}"


@st.cache_data(show_spinner=False)
def carregar() -> Base:
    """Le a base corrente. NUNCA levanta — devolve vazia com o motivo.

    `st.cache_data` e o que o plano §7 Fase 1 pede para leitura de dado. Repare
    que NENHUM campo da tabela de estado de sessao (§11.1) passa por este cache:
    o que entra aqui e um JSON publico de emplacamentos.
    """
    if not ARQUIVO.exists():
        return Base(indisponivel="nenhuma base publicada")

    try:
        bruto = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erro:
        return Base(indisponivel=f"base ilegível: {type(erro).__name__}")

    schema = bruto.get("schema_versao")
    if schema != SCHEMA_SUPORTADO:
        # Recusa de base incompativel SEM tela branca (§7.4).
        return Base(
            indisponivel=(
                f"schema v{schema} incompatível (app espera v{SCHEMA_SUPORTADO})"
            )
        )

    try:
        marcas = {
            nome: _marca(nome, dados)
            for nome, dados in (bruto.get("marcas") or {}).items()
        }
    except (AttributeError, TypeError, ValueError) as erro:
        return Base(indisponivel=f"base malformada: {type(erro).__name__}")

    return Base(
        criterio=str(bruto.get("criterio") or ""),
        fonte=str(bruto.get("fonte") or ""),
        url=str(bruto.get("url") or ""),
        data_consulta=_data_br(str(bruto.get("data_consulta") or "")),
        janelas=dict(bruto.get("janelas") or {}),
        marcas=marcas,
    )


def _marca(nome: str, dados: dict) -> Marca:
    modelos = tuple(
        Modelo(
            modelo=str(m.get("modelo") or ""),
            categoria=str(m.get("categoria") or ""),
            posicao=_inteiro(m.get("posicao")) or 0,
            atual=_inteiro(m.get("atual")),
            anterior=_inteiro(m.get("anterior")),
            fechado=_inteiro(m.get("fechado")),
            variacao=_decimal(m.get("variacao")),
            nota=str(m.get("nota") or ""),
        )
        for m in (dados.get("modelos") or [])
    )
    return Marca(
        nome=nome,
        cobertura=str(dados.get("cobertura") or ""),
        modelos=tuple(sorted(modelos, key=lambda m: m.posicao)),
    )


def _inteiro(valor: object) -> int | None:
    """Numero da base, ou None. NUNCA levanta e NUNCA devolve zero por engano.

    Uma celula formatada como texto na planilha atravessa o gerador e chegaria
    aqui como str; sem esta coercao o erro so apareceria la na frente, dentro
    de `formato.inteiro`, como stack trace na tela — exatamente o que este
    modulo promete no cabecalho que nunca acontece. Valor ilegivel vira None e
    a tela escreve "não publicado", que e a verdade: o numero nao esta legivel
    na base.
    """
    if valor is None or isinstance(valor, bool):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _decimal(valor: object) -> float | None:
    """Idem para a variacao, que e fracionaria."""
    if valor is None or isinstance(valor, bool):
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _data_br(iso: str) -> str:
    """'2026-08-20' -> '20/08/2026'. Devolve o original se nao for uma data.

    A conversao acontece UMA VEZ, na carga: a tela nunca formata data.
    """
    try:
        return f"{date.fromisoformat(iso):%d/%m/%Y}"
    except ValueError:
        return iso

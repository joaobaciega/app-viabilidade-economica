"""Carrega o snapshot JSON publicado pelo pipeline.

Consumido SOMENTE pelas Telas 2 e 3. A Tela 1 nao depende disto (P11, §7.1).

§7.4 (erro de dado): "Falha de validacao do snapshot e erro de PUBLICACAO, e o
app publicado nunca deveria ve-la. Se ainda assim ocorrer em runtime: a Tela 1
CONTINUA FUNCIONANDO — ela nao depende do snapshot. As telas 2 e 3 exibem
`dados indisponiveis nesta versao` na faixa do vendedor e OMITEM o conteudo
afetado. NUNCA tela branca, nunca stack trace, nunca conteudo parcial que
pareca completo."

Por isso `carregar()` nunca levanta excecao: devolve um snapshot vazio com o
motivo registrado, e as telas mostram o estado vazio.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import streamlit as st

DIRETORIO_SNAPSHOT = Path(__file__).resolve().parents[2] / "dados" / "snapshot"
PONTEIRO = DIRETORIO_SNAPSHOT / "ultimo.json"

SCHEMA_SUPORTADO = 1


@dataclass(frozen=True)
class Snapshot:
    versao_snapshot: int | None = None
    publicado_em: str | None = None
    schema_versao: int | None = None
    modelos: list[dict] = field(default_factory=list)
    aplicacao: list[dict] = field(default_factory=list)
    precos_originais: list[dict] = field(default_factory=list)
    catalogo_refil: list[dict] = field(default_factory=list)
    indisponivel: str | None = None

    @property
    def tem_registros(self) -> bool:
        return bool(self.modelos or self.precos_originais or self.catalogo_refil)

    @property
    def marcas(self) -> list[str]:
        """Marcas com dados. §7.3: marca sem dados NAO APARECE no seletor."""
        return sorted({str(m.get("marca")) for m in self.modelos if m.get("marca")})

    def rotulo_versao(self) -> str:
        if self.indisponivel:
            return "dados indisponíveis nesta versão"
        if self.versao_snapshot is None:
            return "nenhum snapshot publicado"
        return f"snapshot v{self.versao_snapshot} · publicado em {self.publicado_em}"


@st.cache_data(show_spinner=False)
def carregar() -> Snapshot:
    """Le o snapshot corrente. NUNCA levanta — devolve vazio com motivo.

    `st.cache_data` aqui e o que o plano §7 Fase 1 pede para a leitura de dados.
    Repare que NENHUM campo da tabela de estado de sessao (§11.1) passa por
    este cache: preco, custo e ancora vivem so em st.session_state.
    """
    if not PONTEIRO.exists():
        return Snapshot(indisponivel="nenhum snapshot publicado")

    try:
        bruto = json.loads(PONTEIRO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erro:
        return Snapshot(indisponivel=f"snapshot ilegível: {type(erro).__name__}")

    schema = bruto.get("schema_versao")
    if schema != SCHEMA_SUPORTADO:
        # Recusa de snapshot incompativel SEM tela branca (§11.1, §7.4).
        return Snapshot(
            indisponivel=f"schema v{schema} incompatível (app espera v{SCHEMA_SUPORTADO})"
        )

    return Snapshot(
        versao_snapshot=bruto.get("versao_snapshot"),
        publicado_em=bruto.get("publicado_em"),
        schema_versao=schema,
        modelos=bruto.get("modelos") or [],
        aplicacao=bruto.get("aplicacao") or [],
        precos_originais=bruto.get("precos_originais") or [],
        catalogo_refil=bruto.get("catalogo_refil") or [],
    )

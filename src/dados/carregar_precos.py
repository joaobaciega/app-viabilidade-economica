"""Carrega os precos da original publicados por `pipeline.gerar_precos`.

Consumido SOMENTE pela Tela 3. A Tela 1 nao depende disto (P11, §7.1).

Mesmo contrato de `carregar_emplacamentos.py` e `carregar_snapshot.py`, de
proposito — §7.4 (erro de dado): falha de leitura e erro de PUBLICACAO, e o app
publicado nunca deveria ve-la. Se ainda assim ocorrer em runtime, `carregar()`
NUNCA levanta excecao: devolve uma base vazia com o motivo registrado, a Tela 3
mostra o estado vazio, e a Tela 1 continua funcionando. Nunca tela branca,
nunca stack trace, nunca conteudo parcial que pareca completo.

REGRA DE PRECO AUSENTE: celula vazia significa preco NAO COLETADO, sem
estimativa. Aqui isso vira `None`, e a Tela 3 escreve "—" com o rotulo do campo
ao lado — a estrutura fica visivel, o valor nao e inventado. `None` NUNCA vira
zero: nao ter preco e diferente de custar zero.

DUAS DIFERENCAS DELIBERADAS EM RELACAO A `carregar_emplacamentos.py`:

  1. `nomes_de_marca` NAO FILTRA marca sem preco. Na Tela 2 a regra e "marca
     sem dado nao aparece no seletor"; aqui as 18 marcas aparecem de proposito,
     porque o menu precisa mostrar a cobertura pretendida do produto e a tela
     precisa mostrar QUAIS CAMPOS existem numa marca ainda nao coletada.
     Registrado em docs/DIVERGENCIAS.md.
  2. `canal` e `data_consulta` vivem POR MODELO, nao no topo do JSON. Na aba
     `base` esses campos sao iguais nas 80 linhas; aqui so 5 linhas os tem, e
     subi-los para o topo afirmaria uma data de coleta para 75 modelos que
     nunca foram coletados.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import streamlit as st

ARQUIVO = Path(__file__).resolve().parents[2] / "dados" / "precos.json"

SCHEMA_SUPORTADO = 1


@dataclass(frozen=True)
class ModeloPreco:
    """Uma linha da base: o preco da original de um modelo."""

    modelo: str
    categoria: str = ""
    posicao: int = 0
    emplacamentos: int | None = None
    pn_dianteiro: str | None = None
    preco_dianteiro_par: float | None = None
    preco_dianteiro_min: float | None = None
    preco_dianteiro_max: float | None = None
    ofertas_dianteiro: int | None = None
    # Tres estados, nao dois: True (tem), False (nao tem), None (nao apurado).
    tem_traseiro: bool | None = None
    pn_traseiro: str | None = None
    preco_traseiro_unid: float | None = None
    preco_veiculo_completo: float | None = None
    canal: str = ""
    url_dianteiro: str = ""
    url_traseiro: str = ""
    # Ja em pt-BR: a conversao acontece UMA VEZ, na carga (ver `_data_br`).
    data_consulta: str = ""
    status: str = "sem preco"
    nota: str = ""

    @property
    def tem_preco(self) -> bool:
        """Se ha ao menos o preco do dianteiro. E o que liga o selo e a economia."""
        return self.preco_dianteiro_par is not None

    @property
    def tem_faixa(self) -> bool:
        """Se a coleta encontrou mais de uma oferta, com min e max distintos."""
        return (
            self.preco_dianteiro_min is not None
            and self.preco_dianteiro_max is not None
            and self.preco_dianteiro_max > self.preco_dianteiro_min
        )


@dataclass(frozen=True)
class MarcaPrecos:
    """Uma marca e os modelos dela, na ordem de emplacamento da base."""

    nome: str
    modelos: tuple[ModeloPreco, ...] = ()

    @property
    def modelos_com_preco(self) -> int:
        return sum(1 for m in self.modelos if m.tem_preco)

    @property
    def canal(self) -> str:
        """O canal de coleta da marca, se houver um so. Vazio se nao houver.

        Sobe para o rodape de procedencia em vez de repetir em cinco cartoes.
        Com mais de um canal na mesma marca fica vazio de proposito: nesse caso
        o canal e do MODELO, e o cartao ja o exibe.
        """
        canais = {m.canal for m in self.modelos if m.canal}
        return canais.pop() if len(canais) == 1 else ""

    @property
    def data_consulta(self) -> str:
        """Idem para a data. Vazia quando a marca tem mais de uma."""
        datas = {m.data_consulta for m in self.modelos if m.data_consulta}
        return datas.pop() if len(datas) == 1 else ""


@dataclass(frozen=True)
class BasePrecos:
    janela_emplacamento: str = ""
    marcas: dict[str, MarcaPrecos] = field(default_factory=dict)
    indisponivel: str | None = None

    @property
    def nomes_de_marca(self) -> list[str]:
        """TODAS as marcas com modelo — inclusive as sem preco coletado.

        Diferenca deliberada em relacao a Tela 2. Ver o cabecalho do modulo.
        """
        return sorted(nome for nome, m in self.marcas.items() if m.modelos)

    @property
    def total_de_modelos(self) -> int:
        return sum(len(m.modelos) for m in self.marcas.values())

    @property
    def total_com_preco(self) -> int:
        return sum(m.modelos_com_preco for m in self.marcas.values())

    def rotulo_versao(self) -> str:
        """A linha de proveniencia da faixa do vendedor. Descreve, nao acusa."""
        if self.indisponivel:
            return f"preços da original: {self.indisponivel}"
        if not self.marcas:
            return "nenhum preço da original publicado"
        return (
            f"preços da original · {self.total_com_preco} de "
            f"{self.total_de_modelos} modelos coletados"
        )


@st.cache_data(show_spinner=False)
def carregar() -> BasePrecos:
    """Le a base corrente. NUNCA levanta — devolve vazia com o motivo.

    `st.cache_data` e o que o plano §7 Fase 1 pede para leitura de dado. Repare
    que NENHUM campo da tabela de estado de sessao (§11.1) passa por este cache:
    o que entra aqui e um JSON de precos publicos de loja oficial. O preco do
    refil que o vendedor digita continua so em st.session_state.
    """
    if not ARQUIVO.exists():
        return BasePrecos(indisponivel="nenhuma base publicada")

    try:
        bruto = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erro:
        return BasePrecos(indisponivel=f"base ilegível: {type(erro).__name__}")

    schema = bruto.get("schema_versao")
    if schema != SCHEMA_SUPORTADO:
        # Recusa de base incompativel SEM tela branca (§7.4).
        return BasePrecos(
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
        return BasePrecos(indisponivel=f"base malformada: {type(erro).__name__}")

    return BasePrecos(
        janela_emplacamento=str(bruto.get("janela_emplacamento") or ""),
        marcas=marcas,
    )


def _marca(nome: str, dados: dict) -> MarcaPrecos:
    modelos = tuple(
        ModeloPreco(
            modelo=str(m.get("modelo") or ""),
            categoria=str(m.get("categoria") or ""),
            posicao=_inteiro(m.get("posicao")) or 0,
            emplacamentos=_inteiro(m.get("emplacamentos")),
            pn_dianteiro=_texto(m.get("pn_dianteiro")),
            preco_dianteiro_par=_decimal(m.get("preco_dianteiro_par")),
            preco_dianteiro_min=_decimal(m.get("preco_dianteiro_min")),
            preco_dianteiro_max=_decimal(m.get("preco_dianteiro_max")),
            ofertas_dianteiro=_inteiro(m.get("ofertas_dianteiro")),
            tem_traseiro=_booleano(m.get("tem_traseiro")),
            pn_traseiro=_texto(m.get("pn_traseiro")),
            preco_traseiro_unid=_decimal(m.get("preco_traseiro_unid")),
            preco_veiculo_completo=_decimal(m.get("preco_veiculo_completo")),
            canal=str(m.get("canal") or ""),
            url_dianteiro=str(m.get("url_dianteiro") or ""),
            url_traseiro=str(m.get("url_traseiro") or ""),
            data_consulta=_data_br(str(m.get("data_consulta") or "")),
            status=str(m.get("status") or "sem preco"),
            nota=str(m.get("nota") or ""),
        )
        for m in (dados.get("modelos") or [])
    )
    return MarcaPrecos(
        nome=nome,
        modelos=tuple(sorted(modelos, key=lambda m: m.posicao)),
    )


def _texto(valor: object) -> str | None:
    """Codigo de peca, ou None. String vazia tambem vira None.

    `None` e `""` significam a mesma coisa aqui — nao coletado — e a tela testa
    um so caso em vez de dois.
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def _inteiro(valor: object) -> int | None:
    """Numero da base, ou None. NUNCA levanta e NUNCA devolve zero por engano.

    Uma celula formatada como texto na planilha atravessa o gerador e chegaria
    aqui como str; sem esta coercao o erro so apareceria la na frente, dentro
    de `formato.inteiro`, como stack trace na tela — exatamente o que este
    modulo promete no cabecalho que nunca acontece.
    """
    if valor is None or isinstance(valor, bool):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _decimal(valor: object) -> float | None:
    """Idem para o preco, que tem centavos."""
    if valor is None or isinstance(valor, bool):
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _booleano(valor: object) -> bool | None:
    """Tres estados preservados: True, False e None.

    `bool(valor)` seria errado aqui — transformaria "nao apurado" em "nao tem".
    """
    if isinstance(valor, bool):
        return valor
    return None


def _data_br(iso: str) -> str:
    """'2026-08-26' -> '26/08/2026'. Devolve o original se nao for uma data.

    A conversao acontece UMA VEZ, na carga: a tela nunca formata data.
    """
    try:
        return f"{date.fromisoformat(iso):%d/%m/%Y}"
    except ValueError:
        return iso

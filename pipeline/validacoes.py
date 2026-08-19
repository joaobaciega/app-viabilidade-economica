"""Validacoes de publicacao S1-S13.

O plano §6.4 EXIGE validacao de schema na publicacao mas nao enumera as regras.
Estas treze sao a enumeracao adotada (registrada em docs/DIVERGENCIAS.md como
suposicao 4), tomadas do unico conjunto escrito que trata do assunto — o
DESIGN v4 §11.2. Renomeadas S1-S13 para nao colidir com as V1-V7 do DESIGN v5,
que validam parametros.py e sao coisa diferente.

    "O passo planilha -> validacao -> snapshot JSON versionado FALHA O BUILD em
    qualquer uma destas. Erro claro, NUNCA publicacao parcial."

    S1  unidade ausente ou fora do enum
    S2  data_coleta ausente, futura ou nao parseavel
    S3  url_print ausente ou apontando para arquivo inexistente
    S4  nome do print fora de marca_modelo_medida_AAAA-MM-DD.png
    S5  print_sem_banner_conferido != true
    S6  ano_fim < ano_ini, ou faixas sobrepostas para o mesmo marca+modelo+posicao
    S7  tipo_par = par_composto com numero de parcelas != 2 no grupo_par_id
    S8  tipo_fonte = loja_oficial_ml sem o selo de loja oficial no print
    S9  preco <= 0 ou ausente com tipo_fonte != indisponivel
    S10 aplicacao_ref nao resolvivel para linha de aplicacao com medida_mm
    S11 qualquer campo de estado de sessao presente no snapshot
    S12 qualquer campo de custo ou preco de venda da Suicatech no snapshot
    S13 catalogo_refil sem nenhuma linha de categoria = dianteiro

Repare no par S11/S12: sao as que protegem o link aberto. O snapshot e publico.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from pipeline import esquema

PADRAO_PRINT = re.compile(r"^[a-z0-9]+_[a-z0-9-]+_\d{3,4}_\d{4}-\d{2}-\d{2}\.png$")


@dataclass(frozen=True)
class Falha:
    regra: str
    aba: str
    linha: int | None
    mensagem: str

    def __str__(self) -> str:
        onde = f"{self.aba}"
        if self.linha is not None:
            onde += f" linha {self.linha}"
        return f"[{self.regra}] {onde}: {self.mensagem}"


def _data(valor: object) -> date | None:
    if isinstance(valor, date):
        return valor
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(valor.strip(), fmt).date()
            except ValueError:
                continue
    return None


def _vazio(valor: object) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _verdadeiro(valor: object) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return bool(valor)
    if isinstance(valor, str):
        return valor.strip().lower() in {"true", "sim", "verdadeiro", "1", "x"}
    return False


# ---------------------------------------------------------------------------


def validar(
    tabelas: dict[str, list[dict]], raiz_prints: Path | None = None
) -> list[Falha]:
    """Roda S1-S13. Devolve TODAS as falhas, nao para na primeira.

    Devolver tudo de uma vez importa: quem publica quer corrigir a planilha uma
    vez, nao descobrir treze erros em treze execucoes.
    """
    falhas: list[Falha] = []
    precos = tabelas.get("precos_originais") or []
    aplicacao = tabelas.get("aplicacao") or []
    catalogo = tabelas.get("catalogo_refil") or []

    falhas += _s1_unidade(precos, catalogo)
    falhas += _s2_data_coleta(precos)
    falhas += _s3_s4_print(precos, raiz_prints)
    falhas += _s5_banner(precos)
    falhas += _s6_faixas_de_ano(precos)
    falhas += _s7_par_composto(precos)
    falhas += _s8_selo_oficial(precos)
    falhas += _s9_preco(precos)
    falhas += _s10_aplicacao_ref(precos, aplicacao)
    falhas += _s11_s12_campos_proibidos(tabelas)
    falhas += _s13_catalogo_dianteiro(catalogo)

    return falhas


def _s1_unidade(precos: list[dict], catalogo: list[dict]) -> list[Falha]:
    """S1 — Sem unidade, a comparacao erra por 2x."""
    validas = {"par", "unitario"}
    falhas = []
    for aba, linhas in (("precos_originais", precos), ("catalogo_refil", catalogo)):
        for i, r in enumerate(linhas, start=2):
            u = r.get("unidade")
            if _vazio(u):
                falhas.append(
                    Falha("S1", aba, i, "`unidade` ausente — nunca assuma `par`")
                )
            elif str(u).strip() not in validas:
                falhas.append(
                    Falha("S1", aba, i, f"`unidade` = {u!r}, fora de {sorted(validas)}")
                )
    return falhas


def _s2_data_coleta(precos: list[dict]) -> list[Falha]:
    """S2 — Data e o que substitui a trava por idade (plano decisao D)."""
    falhas = []
    hoje = date.today()
    for i, r in enumerate(precos, start=2):
        d = _data(r.get("data_coleta"))
        if d is None:
            falhas.append(
                Falha(
                    "S2",
                    "precos_originais",
                    i,
                    f"`data_coleta` ausente ou não parseável: {r.get('data_coleta')!r}",
                )
            )
        elif d > hoje:
            falhas.append(
                Falha("S2", "precos_originais", i, f"`data_coleta` no futuro: {d}")
            )
    return falhas


def _s3_s4_print(precos: list[dict], raiz: Path | None) -> list[Falha]:
    """S3 — o print e o ativo de prova. S4 — nomenclatura rigida."""
    falhas = []
    for i, r in enumerate(precos, start=2):
        if str(r.get("tipo_fonte", "")).strip() == "indisponivel":
            continue  # sem preco publicado, nao ha print a exigir

        caminho = r.get("url_print")
        if _vazio(caminho):
            falhas.append(
                Falha("S3", "precos_originais", i, "`url_print` ausente")
            )
            continue

        nome = Path(str(caminho)).name
        if not PADRAO_PRINT.match(nome):
            falhas.append(
                Falha(
                    "S4",
                    "precos_originais",
                    i,
                    f"nome do print fora do padrão "
                    f"marca_modelo_medida_AAAA-MM-DD.png: {nome!r}",
                )
            )
        if raiz is not None and not (raiz / nome).exists():
            falhas.append(
                Falha(
                    "S3",
                    "precos_originais",
                    i,
                    f"print não encontrado em {raiz}: {nome}",
                )
            )
    return falhas


def _s5_banner(precos: list[dict]) -> list[Falha]:
    """S5 — conferencia MANUAL obrigatoria (plano §2.6).

    O print nao pode conter o banner "nao e compativel com seu veiculo".
    Mostrar isso e entregar municao ao cliente.
    """
    falhas = []
    for i, r in enumerate(precos, start=2):
        if str(r.get("tipo_fonte", "")).strip() == "indisponivel":
            continue
        if not _verdadeiro(r.get("print_sem_banner_conferido")):
            falhas.append(
                Falha(
                    "S5",
                    "precos_originais",
                    i,
                    "`print_sem_banner_conferido` não é verdadeiro — o print "
                    'pode conter o banner "não é compatível com seu veículo"',
                )
            )
    return falhas


def _s6_faixas_de_ano(precos: list[dict]) -> list[Falha]:
    """S6 — ano-modelo ambiguo produz o cartao errado."""
    falhas = []
    por_chave: dict[tuple, list[tuple[int, int, int]]] = defaultdict(list)

    for i, r in enumerate(precos, start=2):
        try:
            ini, fim = int(r.get("ano_ini")), int(r.get("ano_fim"))
        except (TypeError, ValueError):
            falhas.append(
                Falha("S6", "precos_originais", i, "`ano_ini`/`ano_fim` não numéricos")
            )
            continue
        if fim < ini:
            falhas.append(
                Falha("S6", "precos_originais", i, f"ano_fim {fim} < ano_ini {ini}")
            )
            continue
        chave = (r.get("marca"), r.get("modelo"), r.get("posicao"))
        por_chave[chave].append((ini, fim, i))

    for chave, faixas in por_chave.items():
        faixas.sort()
        for (i1, f1, l1), (i2, _f2, l2) in zip(faixas, faixas[1:]):
            if i2 <= f1:
                falhas.append(
                    Falha(
                        "S6",
                        "precos_originais",
                        l2,
                        f"faixa de ano sobreposta com a linha {l1} para "
                        f"{chave}: {i1}-{f1} e {i2}-{_f2}",
                    )
                )
    return falhas


def _s7_par_composto(precos: list[dict]) -> list[Falha]:
    """S7 — um cartao com METADE do preco e pior que nenhum cartao."""
    falhas = []
    grupos: dict[str, list[int]] = defaultdict(list)

    for i, r in enumerate(precos, start=2):
        if str(r.get("tipo_par", "")).strip() != "par_composto":
            continue
        grupo = r.get("grupo_par_id")
        if _vazio(grupo):
            falhas.append(
                Falha(
                    "S7",
                    "precos_originais",
                    i,
                    "`tipo_par` = par_composto sem `grupo_par_id`",
                )
            )
            continue
        grupos[str(grupo)].append(i)

    for grupo, linhas in grupos.items():
        if len(linhas) != 2:
            falhas.append(
                Falha(
                    "S7",
                    "precos_originais",
                    linhas[0],
                    f"grupo_par_id {grupo!r} tem {len(linhas)} parcela(s); "
                    f"par composto exige exatamente 2",
                )
            )
    return falhas


def _s8_selo_oficial(precos: list[dict]) -> list[Falha]:
    """S8 — sem o selo, o print prova preco, NAO PROVA ORIGEM (plano §5.2)."""
    falhas = []
    for i, r in enumerate(precos, start=2):
        if str(r.get("tipo_fonte", "")).strip() != "loja_oficial_ml":
            continue
        if not _verdadeiro(r.get("selo_oficial_conferido")):
            falhas.append(
                Falha(
                    "S8",
                    "precos_originais",
                    i,
                    "`tipo_fonte` = loja_oficial_ml sem `selo_oficial_conferido` "
                    "— sem o selo o print prova preço, não prova origem",
                )
            )
    return falhas


def _s9_preco(precos: list[dict]) -> list[Falha]:
    falhas = []
    for i, r in enumerate(precos, start=2):
        indisponivel = str(r.get("tipo_fonte", "")).strip() == "indisponivel"
        bruto = r.get("preco")
        if indisponivel:
            continue
        if _vazio(bruto):
            falhas.append(
                Falha("S9", "precos_originais", i, "`preco` ausente")
            )
            continue
        try:
            if float(bruto) <= 0:
                falhas.append(
                    Falha("S9", "precos_originais", i, f"`preco` = {bruto}, <= 0")
                )
        except (TypeError, ValueError):
            falhas.append(
                Falha("S9", "precos_originais", i, f"`preco` não numérico: {bruto!r}")
            )
    return falhas


def _s10_aplicacao_ref(precos: list[dict], aplicacao: list[dict]) -> list[Falha]:
    """S10 — sem medida o cartao NAO E AUDITAVEL.

    `posicao` e `medida_mm` tem uma UNICA fonte autoritativa: a aba `aplicacao`.
    `precos_originais` referencia. Duplicar garante divergencia, e divergencia
    de medida num cartao que existe para ser auditavel e o pior lugar possivel
    para ela aparecer.
    """
    indice = {
        (
            r.get("marca"),
            r.get("modelo"),
            r.get("ano_ini"),
            r.get("ano_fim"),
            r.get("posicao"),
        )
        for r in aplicacao
        if not _vazio(r.get("medida_mm"))
    }

    falhas = []
    for i, r in enumerate(precos, start=2):
        chave = (
            r.get("marca"),
            r.get("modelo"),
            r.get("ano_ini"),
            r.get("ano_fim"),
            r.get("posicao"),
        )
        if chave not in indice:
            falhas.append(
                Falha(
                    "S10",
                    "precos_originais",
                    i,
                    f"sem linha correspondente em `aplicacao` com `medida_mm` "
                    f"preenchida para {chave}",
                )
            )
    return falhas


def _s11_s12_campos_proibidos(tabelas: dict[str, list[dict]]) -> list[Falha]:
    """S11 e S12 — o snapshot e PUBLICO.

    S11: dados de reuniao nunca saem da sessao.
    S12: a tabela de preco da Suicatech nao vive no snapshot (plano §6.4).
    """
    falhas = []
    for aba, linhas in tabelas.items():
        colunas = {c for r in linhas for c in r}
        for coluna in sorted(colunas):
            normal = str(coluna).strip().lower()
            if normal in esquema.CAMPOS_DE_SESSAO_PROIBIDOS:
                falhas.append(
                    Falha(
                        "S11",
                        aba,
                        None,
                        f"coluna {coluna!r} é estado de sessão e nunca é "
                        f"publicada — dado de reunião, não de publicação",
                    )
                )
            elif normal in esquema.CAMPOS_DE_CUSTO_PROIBIDOS:
                falhas.append(
                    Falha(
                        "S12",
                        aba,
                        None,
                        f"coluna {coluna!r} expõe custo ou preço de venda da "
                        f"Suicatech; o snapshot é público",
                    )
                )
    return falhas


def _s13_catalogo_dianteiro(catalogo: list[dict]) -> list[Falha]:
    """S13 — a Tela 1 abre em dianteiro.

    Sem SKU dianteiro o app nao tem estado inicial valido. Nao se aplica
    enquanto o catalogo estiver INTEIRAMENTE vazio: catalogo vazio e o estado
    esperado desta fase, e as telas 2 e 3 exibem o estado vazio (§7.3).
    """
    if not catalogo:
        return []
    if not any(str(r.get("categoria", "")).strip() == "dianteiro" for r in catalogo):
        return [
            Falha(
                "S13",
                "catalogo_refil",
                None,
                "nenhuma linha com `categoria` = dianteiro",
            )
        ]
    return []

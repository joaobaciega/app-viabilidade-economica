"""Checagens do checklist §12, compartilhadas por test_checklist.py e verificar.py.

Um lugar so para as buscas e as analises de AST, para que `pytest` e o comando
do dia a dia nao possam divergir.

Por que AST e nao so grep: o DESIGN pede verificacoes que regex nao alcanca.
`preco_traseiro = preco_dianteiro / 2` casa com um grep; `t = d` seguido de
`t /= 2` nao casa com nenhum, e as duas coisas sao o mesmo erro. As checagens
estruturais estao abaixo.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# O codigo do APP (nao inclui pipeline/, testes/ nem os documentos).
PASTAS_APP = ("src",)
ARQUIVOS_PY_APP: list[Path] = sorted(
    [p for pasta in PASTAS_APP for p in (RAIZ / pasta).rglob("*.py")]
    + [RAIZ / "app.py"]
)

ARQUIVOS_PY_TODOS: list[Path] = sorted(
    ARQUIVOS_PY_APP + list((RAIZ / "pipeline").rglob("*.py"))
)


def _relativo(caminho: Path) -> str:
    try:
        return str(caminho.relative_to(RAIZ))
    except ValueError:  # pragma: no cover
        return str(caminho)


# ---------------------------------------------------------------------------
# Busca textual
# ---------------------------------------------------------------------------


def ocorrencias(
    padrao: str, arquivos: list[Path] | None = None, ignorar_comentarios: bool = True
) -> list[str]:
    """Equivalente a `grep -rn -i`, devolvendo 'arquivo:linha: texto'.

    `ignorar_comentarios` existe porque este projeto CITA as palavras proibidas
    nos comentarios de proposito — e a citacao explicando por que "lucro" e
    proibido nao pode reprovar o checklist que proibe "lucro".
    """
    regex = re.compile(padrao, re.IGNORECASE)
    alvos = arquivos if arquivos is not None else ARQUIVOS_PY_APP
    achados: list[str] = []

    for caminho in alvos:
        try:
            texto = caminho.read_text(encoding="utf-8")
        except OSError:  # pragma: no cover
            continue

        docstrings = _linhas_de_docstring(texto)

        for numero, linha in enumerate(texto.splitlines(), start=1):
            if ignorar_comentarios:
                if numero in docstrings:
                    continue
                sem_comentario = linha.split("#", 1)[0]
            else:
                sem_comentario = linha

            if regex.search(sem_comentario):
                achados.append(
                    f"{_relativo(caminho)}:{numero}: {linha.strip()[:100]}"
                )

    return achados


def strings_de_tela_que_casam(
    regex: re.Pattern[str], ignorar: tuple[str, ...] = ()
) -> list[str]:
    """Strings literais DESTINADAS A TELA que casam com o padrao.

    A distincao importa e e a razao desta funcao existir: este projeto CITA o
    vocabulario proibido nos comentarios e nas docstrings de proposito — a
    frase que explica por que "invalido" e proibido nao pode reprovar o
    checklist que proibe "invalido". So strings de codigo executavel contam.

    `ignorar` aceita nomes de arquivo. Serve para `css.py`, cujo conteudo e uma
    FOLHA DE ESTILO inteira dentro de uma string: os comentarios de CSS ficam
    dentro do literal e nao ha como separa-los por AST, mas nenhum deles e
    texto de tela — uma folha de estilo nao tem copy.
    """
    achados: list[str] = []

    for caminho in ARQUIVOS_PY_APP:
        if caminho.name in ignorar:
            continue
        texto = caminho.read_text(encoding="utf-8")
        try:
            arvore = ast.parse(texto)
        except SyntaxError:  # pragma: no cover
            continue

        docstrings = _nos_de_docstring(arvore)

        for no in ast.walk(arvore):
            if not isinstance(no, ast.Constant) or not isinstance(no.value, str):
                continue
            if id(no) in docstrings:
                continue
            if regex.search(no.value):
                achados.append(
                    f"{_relativo(caminho)}:{no.lineno}: {no.value[:80]!r}"
                )

    return achados


def _nos_de_docstring(arvore: ast.AST) -> set[int]:
    """ids dos nos Constant que sao docstring de modulo, classe ou funcao."""
    ids: set[int] = set()
    for no in ast.walk(arvore):
        if isinstance(
            no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            corpo = getattr(no, "body", None)
            if not corpo:
                continue
            primeiro = corpo[0]
            if (
                isinstance(primeiro, ast.Expr)
                and isinstance(primeiro.value, ast.Constant)
                and isinstance(primeiro.value.value, str)
            ):
                ids.add(id(primeiro.value))
    return ids


def _linhas_de_docstring(texto: str) -> set[int]:
    """Numeros de linha ocupados por docstrings de modulo, classe e funcao."""
    ocupadas: set[int] = set()
    try:
        arvore = ast.parse(texto)
    except SyntaxError:  # pragma: no cover
        return ocupadas

    for no in ast.walk(arvore):
        if isinstance(
            no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            corpo = getattr(no, "body", None)
            if not corpo:
                continue
            primeiro = corpo[0]
            if (
                isinstance(primeiro, ast.Expr)
                and isinstance(primeiro.value, ast.Constant)
                and isinstance(primeiro.value.value, str)
            ):
                fim = primeiro.end_lineno or primeiro.lineno
                ocupadas.update(range(primeiro.lineno, fim + 1))
    return ocupadas


# ---------------------------------------------------------------------------
# §5.13 — traseiro nunca derivado do dianteiro
# ---------------------------------------------------------------------------

_TRASEIRO = re.compile(r"(?i)traseir")
_DIANTEIRO = re.compile(r"(?i)dianteir")


def atribuicoes_suspeitas_de_derivar_traseiro() -> list[str]:
    """Qualquer atribuicao que misture as duas categorias numa expressao.

    Procura, por AST:
      - alvo "traseiro" com expressao que menciona "dianteiro"
      - alvo "dianteiro" com expressao que menciona "traseiro"

    Isso pega `/2`, `*0.5`, `* fator` e tambem a versao em duas linhas.
    """
    achados: list[str] = []

    for caminho in ARQUIVOS_PY_APP:
        texto = caminho.read_text(encoding="utf-8")
        try:
            arvore = ast.parse(texto)
        except SyntaxError:  # pragma: no cover
            continue

        for no in ast.walk(arvore):
            alvos: list[ast.expr] = []
            valor: ast.expr | None = None

            if isinstance(no, ast.Assign):
                alvos, valor = list(no.targets), no.value
            elif isinstance(no, (ast.AugAssign, ast.AnnAssign)):
                alvos, valor = [no.target], no.value

            if not alvos or valor is None:
                continue

            nomes_alvo = " ".join(_nomes(a) for a in alvos)
            nomes_valor = " ".join(_nomes(valor))

            mistura = (
                _TRASEIRO.search(nomes_alvo) and _DIANTEIRO.search(nomes_valor)
            ) or (_DIANTEIRO.search(nomes_alvo) and _TRASEIRO.search(nomes_valor))

            if mistura:
                trecho = texto.splitlines()[no.lineno - 1].strip()
                achados.append(f"{_relativo(caminho)}:{no.lineno}: {trecho[:100]}")

    return achados


def _nomes(no: ast.AST) -> str:
    """Todos os identificadores mencionados numa subarvore, como texto."""
    partes: list[str] = []
    for filho in ast.walk(no):
        if isinstance(filho, ast.Name):
            partes.append(filho.id)
        elif isinstance(filho, ast.Attribute):
            partes.append(filho.attr)
        elif isinstance(filho, ast.Constant) and isinstance(filho.value, str):
            partes.append(filho.value)
    return " ".join(partes)


# ---------------------------------------------------------------------------
# Estado de sessao nunca persistido
# ---------------------------------------------------------------------------

_APIS_DE_PERSISTENCIA = re.compile(
    r"(?i)(localStorage|sessionStorage|query_params|"
    r"cache_data|cache_resource|json\.dump|\.write_text|\.write_bytes|open\()"
)


def campos_de_sessao() -> tuple[str, ...]:
    from src.estado import CAMPOS_DE_SESSAO

    return CAMPOS_DE_SESSAO


def persistencia_de_campos_de_sessao() -> list[str]:
    """Linhas em que um campo de sessao aparece junto de uma API de persistencia.

    §11.1 (tabela acrescentada): preco, custo, ancora, deducoes e nome do
    cliente vivem SO na memoria da sessao. Nunca localStorage, nunca URL,
    nunca disco, nunca cache.
    """
    campos = campos_de_sessao()
    achados: list[str] = []

    for caminho in ARQUIVOS_PY_APP:
        texto = caminho.read_text(encoding="utf-8")
        docstrings = _linhas_de_docstring(texto)

        for numero, linha in enumerate(texto.splitlines(), start=1):
            if numero in docstrings:
                continue
            codigo = linha.split("#", 1)[0]
            if not _APIS_DE_PERSISTENCIA.search(codigo):
                continue
            if any(campo in codigo for campo in campos):
                achados.append(
                    f"{_relativo(caminho)}:{numero}: {linha.strip()[:100]}"
                )

    return achados


# ---------------------------------------------------------------------------
# Fronteiras de import
# ---------------------------------------------------------------------------


def chaves_de_container() -> set[str]:
    """As chaves de todo `st.container(key=...)` do app.

    Resolve tanto o literal (`key="cenarios"`) quanto a constante de modulo
    (`key=CHAVE_CONTAINER`), porque as duas formas aparecem no codigo e um
    casamento por texto perderia a segunda.
    """
    chaves: set[str] = set()

    for caminho in ARQUIVOS_PY_APP:
        texto = caminho.read_text(encoding="utf-8")
        try:
            arvore = ast.parse(texto)
        except SyntaxError:  # pragma: no cover
            continue

        constantes = _constantes_de_texto_do_modulo(arvore)

        for no in ast.walk(arvore):
            if not isinstance(no, ast.Call):
                continue
            alvo = no.func
            if not (isinstance(alvo, ast.Attribute) and alvo.attr == "container"):
                continue
            for arg in no.keywords:
                if arg.arg != "key":
                    continue
                if isinstance(arg.value, ast.Constant) and isinstance(
                    arg.value.value, str
                ):
                    chaves.add(arg.value.value)
                elif isinstance(arg.value, ast.Name):
                    valor = constantes.get(arg.value.id)
                    if valor:
                        chaves.add(valor)

    return chaves


def _constantes_de_texto_do_modulo(arvore: ast.AST) -> dict[str, str]:
    """Constantes de modulo do tipo NOME = "texto"."""
    valores: dict[str, str] = {}
    for no in getattr(arvore, "body", []):
        if isinstance(no, ast.Assign) and len(no.targets) == 1:
            alvo = no.targets[0]
            if (
                isinstance(alvo, ast.Name)
                and isinstance(no.value, ast.Constant)
                and isinstance(no.value.value, str)
            ):
                valores[alvo.id] = no.value.value
    return valores


def arquivos_que_importam(modulo: str, dentro_de: str) -> list[str]:
    """Arquivos sob `dentro_de` que importam `modulo` (ou submodulo dele)."""
    alvo = RAIZ / dentro_de
    caminhos = [alvo] if alvo.is_file() else sorted(alvo.rglob("*.py"))
    achados: list[str] = []

    for caminho in caminhos:
        try:
            arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):  # pragma: no cover
            continue

        for no in ast.walk(arvore):
            nome = ""
            if isinstance(no, ast.Import):
                nome = " ".join(a.name for a in no.names)
            elif isinstance(no, ast.ImportFrom):
                nome = no.module or ""
            if nome and (nome == modulo or nome.startswith(modulo + ".")):
                achados.append(f"{_relativo(caminho)}:{no.lineno}: importa {nome}")

    return achados

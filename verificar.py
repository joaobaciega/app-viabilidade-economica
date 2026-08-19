"""Roda o checklist §12 do DESIGN e imprime linha por linha.

    python verificar.py

Sai com codigo != 0 se qualquer item automatizavel reprovar. As MESMAS
checagens rodam em testes/test_checklist.py — este arquivo e a versao que voce
roda no dia a dia e mostra o que passou e o que nao passou.

DESIGN §0.5: "Rode o checklist da §12 contra a tela pronta. Cada item e
verificavel olhando a tela ou rodando um grep. NENHUM E OPINIAO."

Os itens que NAO dao para automatizar estao listados no fim, porque tambem nao
sao opiniao — so nao sao comando. O mais importante deles e o teste de um metro.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

VERDE, VERMELHO, CINZA, NEGRITO, FIM = (
    "\033[32m",
    "\033[31m",
    "\033[90m",
    "\033[1m",
    "\033[0m",
)

MANUAIS = [
    (
        "O teste de um metro",
        "Afaste-se 1 m do tablet inclinado, sob luz forte. Os tres numeros do "
        "resultado sao lidos SEM ESFORCO e o texto da faixa do vendedor NAO e "
        "decifravel. Nenhum comando substitui este item (§3.2, §12).",
    ),
    (
        "Marca do framework",
        "Confira em 1180x820 e em 1366x1024 que nao aparece menu hamburguer, "
        "rodape, 'Made with Streamlit' nem botao Deploy (§6.1.9).",
    ),
    (
        "Reteste visual dos itens 🔧",
        "Todo item marcado 🔧 em src/css.py foi conferido contra streamlit "
        "1.58.0. Subir a versao exige refazer este item (§3, camada B).",
    ),
    (
        "Queda de rede",
        "Desligue o wi-fi com o app aberto: o ultimo resultado PERMANECE, o "
        "aviso nativo aparece neutralizado no rodape, e NAO ha caixa vermelha "
        "na area visivel ao cliente (§5.14).",
    ),
    (
        "Cor da marca",
        "⚠️ Decisao K: o vermelho e o provisorio validado #C8102E. Ao trocar "
        "pelo oficial, refaca as tres medidas da §3.1.1 e a da §5.11.1.",
    ),
]


def _titulo(texto: str) -> None:
    print(f"\n{NEGRITO}{texto}{FIM}")
    print(CINZA + "-" * len(texto) + FIM)


def main() -> int:
    print(f"{NEGRITO}Checklist §12 — DESIGN.md{FIM}")
    print(f"{CINZA}Simulador de viabilidade · refil de palhetas · Suicatech{FIM}")

    _titulo("Itens verificaveis por comando")
    print(
        f"{CINZA}Rodando as checagens de testes/test_checklist.py "
        f"e os 16 casos da §11.3...{FIM}\n"
    )

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "testes/",
            "-v",
            "--no-header",
            "--tb=short",
            "-q",
        ],
        cwd=RAIZ,
        env={**_ambiente()},
    )

    aprovado = resultado.returncode == 0

    _titulo("Itens verificaveis so olhando a tela")
    print(
        f"{CINZA}Nao sao opiniao — so nao sao comando. "
        f"Marque com data e assinatura em docs/DIVERGENCIAS.md.{FIM}\n"
    )
    for i, (nome, descricao) in enumerate(MANUAIS, 1):
        print(f"  [ ] {NEGRITO}{i}. {nome}{FIM}")
        for linha in _quebrar(descricao, 74):
            print(f"        {CINZA}{linha}{FIM}")
        print()

    _titulo("Resultado")
    if aprovado:
        print(f"  {VERDE}Todos os itens automatizaveis passaram.{FIM}")
        print(
            f"  {CINZA}A Tela 1 nao esta pronta ate os 5 itens manuais acima "
            f"estarem marcados.{FIM}"
        )
    else:
        print(f"  {VERMELHO}Um ou mais itens reprovaram. Veja acima.{FIM}")

    return 0 if aprovado else 1


def _ambiente() -> dict[str, str]:
    import os

    ambiente = dict(os.environ)
    caminho_existente = ambiente.get("PYTHONPATH", "")
    ambiente["PYTHONPATH"] = (
        f"{RAIZ}{os.pathsep}{caminho_existente}" if caminho_existente else str(RAIZ)
    )
    return ambiente


def _quebrar(texto: str, largura: int) -> list[str]:
    palavras, linhas, atual = texto.split(), [], ""
    for palavra in palavras:
        if len(atual) + len(palavra) + 1 > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = f"{atual} {palavra}".strip()
    if atual:
        linhas.append(atual)
    return linhas


if __name__ == "__main__":
    raise SystemExit(main())

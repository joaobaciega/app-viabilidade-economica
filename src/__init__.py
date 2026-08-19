"""App de viabilidade de refil de palhetas — Suicatech / Intrace AG.

Importar qualquer coisa de src/ dispara a validacao V1-V7 dos parametros.
Nao ha caminho de import que contorne isso: e o que garante que o app nao
sobe com parametro invalido (DESIGN.md §11.2, §7.4).
"""

from src.validacao_parametros import validar_tudo as _validar_tudo

_validar_tudo()

"""Icones de linha — DIVERGENCIA D2 (docs/DIVERGENCIAS.md).

O DESIGN P10 pede "sem icone decorativo, sem emoji". Esta divergencia foi
autorizada pelo cliente, e e BOUNDED — as regras abaixo mantem a intencao do
P10 (instrumento, nao peca de marketing):

  1. MONOCROMATICO. `currentColor`, sempre. Nenhum icone introduz cor, e
     nenhum usa --marca-vermelho (§3.1 restringe o vermelho a dois lugares).
  2. FUNCIONAL, nunca decorativo. Identidade de secao e affordance de campo.
     Nao ha icone "para enfeitar".
  3. SEMPRE ACOMPANHADO DE PALAVRA. Nunca canal unico de informacao — a
     independencia de cor e de glifo da §3.1.3 vale aqui tambem: um icone
     sozinho falha a 1 m e falha para quem tem 55 anos.
  4. NUNCA EMOJI em area visivel ao cliente. SVG inline, traco de 1,75px.
     A excecao e o glifo ⚠️ do MarcadorDecisaoAberta, que o proprio DESIGN
     §5.12 especifica literalmente.

Os glifos de procedencia (◆ ▪ ƒ ≈ ⬡) NAO estao aqui: sao especificados pela
§5.7 como caracteres, e continuam caracteres.
"""

from __future__ import annotations

# Traçado de 24x24, sem preenchimento. O CSS em css.py (.st-icone svg)
# aplica stroke=currentColor, width=1em e stroke-width=1.75.
_CAMINHOS: dict[str, str] = {
    # Bloco A — a operacao da concessionaria
    "operacao": '<path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6"/>',
    # Bloco B — o produto (palheta)
    "produto": '<path d="M3 17c4-1 7-4 9-9M3 17h7M5.5 13.5 3 17"/>'
    '<path d="M13 6.5 21 3l-3.5 8"/>',
    # Bloco C — a operacao hoje / ancora
    "hoje": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    # Cenario / presets
    "cenario": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    # Resultado
    "resultado": '<path d="M3 3v18h18"/><path d="M7 15l4-5 3 3 5-7"/>',
    # Grafico de sensibilidade
    "curva": '<path d="M3 3v18h18"/><path d="M4 17c4 0 6-9 16-12"/>',
    # Ajustes avancados
    "ajustes": '<path d="M4 6h16M4 12h16M4 18h16"/>'
    '<circle cx="9" cy="6" r="2"/><circle cx="15" cy="12" r="2"/>'
    '<circle cx="8" cy="18" r="2"/>',
    # Painel de formula / prova
    "formula": '<path d="M5 4h14M9 4v6l-4 10h14l-4-10V4"/>',
    # Tabela da curva
    "tabela": '<rect x="3" y="4" width="18" height="16" rx="2"/>'
    '<path d="M3 10h18M9 10v10"/>',
    # Exportar PDF
    "exportar": '<path d="M12 3v12M8 11l4 4 4-4"/><path d="M4 19h16"/>',
    # Novo cliente
    "novo": '<path d="M12 5v14M5 12h14"/>',
    # Telas 2 e 3
    "veiculos": '<path d="M4 16V9l2-4h12l2 4v7"/><path d="M2 16h20"/>'
    '<circle cx="7.5" cy="18" r="1.8"/><circle cx="16.5" cy="18" r="1.8"/>',
    "preco": '<path d="M12 3v18"/>'
    '<path d="M16 7.5C16 5.6 14.2 4.5 12 4.5S8 5.6 8 7.5s1.8 2.8 4 3.5 '
    "4 1.6 4 3.5-1.8 3-4 3-4-1.1-4-3\"/>",
}


def svg(nome: str) -> str:
    """Devolve o SVG inline do icone, ou string vazia se nao existir.

    String vazia em vez de excecao: um icone ausente nunca deve derrubar a
    tela na frente do cliente (§7.4 — nunca uma tela quebrada). O texto ao
    lado carrega a informacao de qualquer forma, por construcao (regra 3).
    """
    caminho = _CAMINHOS.get(nome)
    if not caminho:
        return ""
    return (
        '<span class="st-icone" aria-hidden="true">'
        f'<svg viewBox="0 0 24 24" role="presentation">{caminho}</svg>'
        "</span>"
    )

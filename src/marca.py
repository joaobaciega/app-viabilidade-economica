"""A marca no cabecalho — logo em arquivo, com reserva tipografica.

O logo NAO vive no codigo: ele vive em `assets/`. Basta soltar o arquivo lá e
ele aparece — nenhuma linha de Python muda.

    assets/logo.png     (ou .svg, .webp, .jpg)

QUAL ARQUIVO USAR. A faixa do cabecalho e vermelha, portanto o logo precisa ser
a versao BRANCA com fundo transparente. No kit da marca:

    Ações 2020/Embalagem 2022/Rótulos 2022/Projeto Externo/01 LOGOTIPO/
      PNG/01 PRINCIPAL/LOGO SUICA TECH HORIZONTAL BRANCO.png

Se voce preferir usar a versao COLORIDA (fundo claro), troque
`FUNDO_CLARO = True` abaixo: o cabecalho passa a ser branco com filete vermelho
e o texto vira tinta escura, sem mexer em mais nada.

POR QUE O ARQUIVO E EMBUTIDO COMO data: URI, e nao servido por caminho:
`st.image` e `st.logo` criam um endpoint de midia e uma requisicao HTTP extra
por render. Embutir em base64 mantem a promessa da §7.1 — a Tela 1 nao faz
nenhuma requisicao externa — e vale a pena porque o arquivo e pequeno. Acima de
`LIMITE_BYTES` o app recusa embutir e cai na reserva, com o motivo na faixa do
vendedor: um logo de 3 MB embutido em cada rerun seria latencia na reuniao.

RESERVA (fallback). Sem arquivo, o cabecalho mostra a marca em tipografia — o
mesmo que ele mostrava antes. Nao ha tela quebrada, nao ha imagem faltando com
o icone de erro do navegador (§7.4: nunca uma tela quebrada na frente do cliente).
"""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

# O logo oficial da Suica Tech e COLORIDO (letras vermelhas com relevo, bandeiras
# suica e alema, tarja de slogan). Letra vermelha sobre faixa vermelha nao tem
# contraste nenhum, portanto o cabecalho e claro: superficie branca com filete
# vermelho embaixo. Ver _cabecalho_claro() em css.py.
FUNDO_CLARO = True

DIRETORIO = Path(__file__).resolve().parents[1] / "assets"
NOMES = ("logo.svg", "logo.png", "logo.webp", "logo.jpg", "logo.jpeg")

# O lockup INTEIRO, com a tarja de slogan. Vai no PDF, onde ha espaco — no
# cabecalho ele reduz a palavra-marca a ~18px e a assinatura a um borrao, e a
# §4 do DESIGN proibe linguagem de anuncio na copy do app. Um documento que sai
# da sala nao e o instrumento da negociacao, e la a tarja cabe.
NOMES_COMPLETO = ("logo-completo.png", "logo-completo.jpg", "logo-completo.webp")

# Acima disto, embutir custa mais do que o logo entrega.
LIMITE_BYTES = 400 * 1024

_TIPOS = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


@lru_cache(maxsize=1)
def _arquivo() -> Path | None:
    for nome in NOMES:
        caminho = DIRETORIO / nome
        if caminho.exists() and caminho.stat().st_size > 0:
            return caminho
    return None


@lru_cache(maxsize=1)
def data_uri() -> str | None:
    """O logo como data: URI, ou None se nao houver arquivo utilizavel."""
    caminho = _arquivo()
    if caminho is None:
        return None
    if caminho.stat().st_size > LIMITE_BYTES:
        return None
    try:
        dados = caminho.read_bytes()
    except OSError:
        # Arquivo ilegivel (placeholder de nuvem, permissao) — cai na reserva.
        return None
    tipo = _TIPOS.get(caminho.suffix.lower(), "application/octet-stream")
    return f"data:{tipo};base64,{base64.b64encode(dados).decode('ascii')}"


def caminho_do_logo() -> Path | None:
    return _arquivo()


@lru_cache(maxsize=1)
def caminho_do_logo_completo() -> Path | None:
    """O lockup inteiro, para o PDF. Cai no do cabecalho se nao existir."""
    for nome in NOMES_COMPLETO:
        caminho = DIRETORIO / nome
        if caminho.exists() and caminho.stat().st_size > 0:
            return caminho
    return _arquivo()


def motivo_da_reserva() -> str | None:
    """Por que a reserva esta em uso — para a faixa do vendedor.

    O vendedor precisa saber que o logo nao carregou; o cliente nao precisa ver
    isso em destaque nenhum. Por isso a mensagem vive na faixa (§5.9).
    """
    caminho = _arquivo()
    if caminho is None:
        return f"logo não encontrado em assets/ — usando a marca em texto"
    if caminho.stat().st_size > LIMITE_BYTES:
        kb = caminho.stat().st_size // 1024
        return (
            f"logo de {kb} kB acima do limite de "
            f"{LIMITE_BYTES // 1024} kB — usando a marca em texto"
        )
    if data_uri() is None:
        return f"logo em assets/{caminho.name} ilegível — usando a marca em texto"
    return None


def html(alt: str = "Suiça Tech") -> str:
    """O bloco da marca para o cabecalho: imagem se houver, texto se nao."""
    uri = data_uri()
    if uri is not None:
        return (
            f'<img class="st-logo" src="{uri}" alt="{alt}" '
            f'title="{alt}" draggable="false">'
        )
    # Reserva tipografica — a mesma marca de antes do arquivo existir.
    from src.icones import svg

    return (
        f'<span class="st-marca">{svg("resultado")} SUICATECH</span>'
    )

"""Componente +19 — EnviadorEmail. ACRESCIMO DECLARADO (docs/DIVERGENCIAS.md D30).

Pedido do cliente em 01/09/2026: *"um botao abaixo do de exportar para PDF que
abre um campo pedindo um e-mail e dispara o documento para o endereco informado,
com uma mensagem pre-programada."*

O QUE ESTE MODULO E, E O QUE ELE NAO E
======================================

Ele e a CAMADA DE TRANSPORTE, e so isso: recebe bytes prontos e um endereco, e
tenta entregar. Nao monta documento, nao desenha widget, nao le session_state.
E a mesma fronteira que ja existe entre `exportador_pdf.py` (decide O QUE entra
no documento) e `pdf_visual.py` (sabe desenhar cartao e curva e nada mais).

Por que a fronteira importa aqui em particular: o envio e a UNICA operacao deste
app que fala com uma maquina de fora. Mante-la num arquivo so e o que deixa o
teste trocar `smtplib.SMTP` por um duplo e cobrir o caminho inteiro sem rede.

`enviar()` NUNCA LEVANTA
========================

§7.4 — nunca uma tela quebrada na frente do cliente. Um servidor SMTP fora do ar,
uma senha trocada, um DNS lento: nada disso pode derrubar o resultado que ja esta
na tela e que e o que o cliente veio ver. `enviar()` devolve `None` em sucesso e
uma string curta de motivo em falha, e o chamador vira isso numa linha discreta.

IMPORTS TARDIOS, DE PROPOSITO
=============================

`smtplib`, `ssl` e `email.message` sao importados DENTRO de `enviar()`. O
Community Cloud hiberna apos 12 h e a probabilidade de o app estar dormindo na
visita e MUITO ALTA (plano §9, risco 6): o que nao e importado na carga nao entra
no caminho entre o vendedor abrir o link e o cliente ver a tela. O envio e raro;
a carga e sempre.

Os tres estao na allowlist de stdlib de `testes/test_checklist.py` — o teste que
compara `requirements.txt` com o que o app de fato importa varre a arvore inteira
por AST, e nao so o topo do arquivo.

O CUSTO DE AQUISICAO PODE IR NO ANEXO
=====================================

Decisao do cliente, 01/09/2026: com custo preenchido o documento sai marcado como
DOCUMENTO INTERNO, e o envio pede CONFIRMACAO na tela antes de sair — mas, uma vez
confirmado, o PDF segue como esta, com o custo. Quem decide isso e a area de
exportacao, nao este modulo: aqui chega bytes.

O TETO POR SESSAO
=================

O app tem link aberto, sem login (plano §6.3). Sem teto, o botao e um jeito de
disparar e-mail de graca a partir da conta configurada. `LIMITE_POR_SESSAO` nao
resolve o problema de fundo — a resposta de fundo seria uma senha de vendedor —,
mas transforma um incomodo automatizavel num incomodo manual, e a copia fixa da
visibilidade de tudo que sai.
"""

from __future__ import annotations

import re

import streamlit as st

# Decisao do cliente, 01/09/2026: toda simulacao enviada sai com copia para este
# endereco. Nao e segredo — e o destinatario fixo, e vive no codigo para poder
# ser lido por teste e aparecer no texto da tela ("com copia para ...").
COPIA_FIXA = "joao@suicatech.com.br"

# Teto de envios por sessao. Ver a nota sobre o link aberto no topo do modulo.
LIMITE_POR_SESSAO = 5

# Segundos. Um SMTP pendurado nao pode congelar o rerun na frente do cliente: o
# Streamlit renderiza no servidor e a tela inteira espera esta chamada.
_TIMEOUT = 15

# Reconhecimento de endereco, deliberadamente FROUXO. A unica verificacao que um
# app pode fazer sozinho e de forma: existe um arroba com algo dos dois lados e
# um ponto no dominio. Dizer mais que isso seria mentira — so a entrega prova que
# a caixa existe, e por isso o texto da tela nunca declara o endereco correto.
_ENDERECO = re.compile(r"^[^@\s,;]+@[^@\s,;]+\.[^@\s,;]{2,}$")

_ASSUNTO = "Simulação de viabilidade — refil de palhetas"

# A MENSAGEM PRE-PROGRAMADA. Obedece a §4 como qualquer texto do app: nao promete,
# nao adjetiva o numero e nomeia a conta que foi feita (margem de contribuição).
# Ela vive aqui, em constante, para o teste conseguir le-la.
_CORPO = """Olá,

Segue em anexo o documento com a simulação de viabilidade do refil de palhetas: o cenário simulado, as premissas assumidas e o que ainda não foi decidido.

Os valores param na margem de contribuição e vêm das premissas informadas na reunião.

Qualquer dúvida, é só responder a este e-mail.

Suicatech · Intrace AG
"""


def endereco_aceitavel(texto: str) -> bool:
    """Forma de endereco. NAO afirma que a caixa existe — ver `_ENDERECO`."""
    return bool(_ENDERECO.match(texto.strip()))


def assunto(cliente: str) -> str:
    """O assunto leva o nome do cliente quando ha nome (D29, mesmo criterio).

    Sem nome, o assunto e o titulo do documento e nada mais — do mesmo jeito que
    o PDF sem nome abre pelo proprio titulo.

    O separador e o PONTO MEDIO, e nao um travessao: o titulo ja tem um travessao
    dentro, e nomes de concessionaria costumam ter outro ("Auto Center — Zona
    Sul"). Com tres travessoes na mesma linha, a caixa de entrada mostra
    "Simulação de viabilidade — refil de palhetas — Auto Center — Zona" e nada
    ali diz onde o titulo acaba e o cliente comeca.
    """
    cliente = cliente.strip()
    return f"{_ASSUNTO} · {cliente}" if cliente else _ASSUNTO


def corpo(cliente: str) -> str:
    """A mensagem, endereçada pelo nome quando ha nome."""
    cliente = cliente.strip()
    if not cliente:
        return _CORPO
    return _CORPO.replace("Olá,", f"Olá, {cliente},", 1)


def _credenciais() -> dict[str, object] | None:
    """Le `[email]` de st.secrets. Devolve None quando nao ha configuracao.

    `st.secrets` LEVANTA quando nao existe `.streamlit/secrets.toml` — e esse e o
    estado normal da maquina local. A captura e larga porque a excecao que o
    Streamlit usa aqui mudou de nome entre versoes, e este modulo nao pode
    quebrar a tela por causa disso (§7.4).
    """
    try:
        secao = st.secrets["email"]
    except Exception:  # noqa: BLE001 — ver o comentario acima
        return None

    try:
        dados = {
            "host": str(secao["host"]).strip(),
            "porta": int(secao["porta"]),
            "usuario": str(secao["usuario"]),
            "senha": str(secao["senha"]),
            "remetente": str(secao.get("remetente") or secao["usuario"]),
        }
    except Exception:  # noqa: BLE001 — configuracao incompleta e o mesmo caso
        return None

    return dados if dados["host"] and dados["porta"] else None


def configurado() -> bool:
    """Se ha credenciais SMTP neste ambiente. Sem elas o botao nao habilita."""
    return _credenciais() is not None


def enviar(
    *,
    destino: str,
    documento: bytes,
    nome_arquivo: str,
    cliente: str = "",
) -> str | None:
    """Entrega o PDF. Devolve None em sucesso, ou um motivo curto em falha.

    O motivo NAO vai para a tela como esta: ele e um rotulo interno, e quem
    decide o que o cliente le e a area de exportacao. Um endereco de SMTP num
    texto de tela seria vazamento de infraestrutura na frente do gerente.
    """
    destino = destino.strip()
    if not endereco_aceitavel(destino):
        return "endereco"

    credenciais = _credenciais()
    if credenciais is None:
        return "sem-configuracao"

    # Tardios de proposito — ver a nota no topo do modulo.
    import smtplib
    import ssl
    from email.message import EmailMessage

    mensagem = EmailMessage()
    mensagem["From"] = str(credenciais["remetente"])
    mensagem["To"] = destino
    mensagem["Cc"] = COPIA_FIXA
    mensagem["Subject"] = assunto(cliente)
    mensagem.set_content(corpo(cliente))
    mensagem.add_attachment(
        documento,
        maintype="application",
        subtype="pdf",
        filename=nome_arquivo,
    )

    host = str(credenciais["host"])
    porta = int(credenciais["porta"])

    try:
        contexto = ssl.create_default_context()
        if porta == 465:
            with smtplib.SMTP_SSL(
                host, porta, timeout=_TIMEOUT, context=contexto
            ) as servidor:
                servidor.login(
                    str(credenciais["usuario"]), str(credenciais["senha"])
                )
                servidor.send_message(mensagem)
        else:
            with smtplib.SMTP(host, porta, timeout=_TIMEOUT) as servidor:
                servidor.starttls(context=contexto)
                servidor.login(
                    str(credenciais["usuario"]), str(credenciais["senha"])
                )
                servidor.send_message(mensagem)
    except Exception:  # noqa: BLE001 — §7.4, ver a nota no topo do modulo
        return "transporte"

    return None

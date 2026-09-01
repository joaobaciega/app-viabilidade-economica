"""D30 — o envio do PDF por e-mail, verificado SEM REDE.

Todo teste daqui troca `smtplib.SMTP` por um duplo. Isso nao e so higiene de
suite: e o unico jeito de conferir o que de fato sai — destinatarios, assunto,
corpo e anexo — sem depender de uma caixa postal e de alguem abrindo o e-mail.

O QUE ESTES TESTES PROTEGEM, em ordem de gravidade:

  1. o anexo e o PDF, com o nome que `nome_do_arquivo()` produz. Um anexo vazio
     ou com outro nome so apareceria na caixa do cliente
  2. a copia fixa sai em TODO envio (decisao do cliente, 01/09/2026). Ela e o
     unico registro do que saiu — o app nao persiste nada em disco (§5.2)
  3. `enviar()` NAO LEVANTA, nunca (§7.4). Uma excecao aqui derrubaria o
     resultado que ja esta na tela, na frente do cliente
"""

from __future__ import annotations

import smtplib
from email import policy
from email.parser import BytesParser

import pytest

from src.componentes import enviador_email
from src.componentes.exportador_pdf import nome_do_arquivo

CREDENCIAIS = {
    "host": "smtp.exemplo.test",
    "porta": 587,
    "usuario": "simulador@exemplo.test",
    "senha": "nao-e-uma-senha",
    "remetente": "Suicatech · Intrace AG <simulador@exemplo.test>",
}

DOCUMENTO = b"%PDF-1.7\n% documento de teste\n"


class _SMTPFalso:
    """Duplo de `smtplib.SMTP`. Guarda a ultima mensagem entregue.

    Registra tambem `starttls` e `login`: um envio que pula o STARTTLS manda a
    senha em texto claro pela rede, e isso nao aparece em nenhuma inspecao da
    mensagem — so na sequencia de chamadas.
    """

    ultima: "_SMTPFalso | None" = None

    def __init__(self, host, porta, timeout=None, context=None) -> None:
        self.host = host
        self.porta = porta
        self.timeout = timeout
        self.chamadas: list[str] = []
        self.mensagem = None
        type(self).ultima = self

    def __enter__(self) -> "_SMTPFalso":
        return self

    def __exit__(self, *_) -> None:
        self.chamadas.append("quit")

    def starttls(self, context=None) -> None:
        self.chamadas.append("starttls")

    def login(self, usuario, senha) -> None:
        self.chamadas.append("login")
        self.usuario = usuario
        self.senha = senha

    def send_message(self, mensagem) -> None:
        self.chamadas.append("send_message")
        self.mensagem = mensagem


class _SMTPQueRecusa(_SMTPFalso):
    def send_message(self, mensagem):
        raise smtplib.SMTPRecipientsRefused({})


class _SMTPQueDemais(_SMTPFalso):
    def __init__(self, *a, **k):
        raise TimeoutError("timed out")


@pytest.fixture
def configurado(monkeypatch) -> None:
    """Credenciais presentes e SMTP trocado pelo duplo."""
    monkeypatch.setattr(
        enviador_email.st, "secrets", {"email": dict(CREDENCIAIS)}, raising=False
    )
    monkeypatch.setattr(smtplib, "SMTP", _SMTPFalso)
    monkeypatch.setattr(smtplib, "SMTP_SSL", _SMTPFalso)
    _SMTPFalso.ultima = None


def _enviar(**overrides) -> str | None:
    argumentos = {
        "destino": "gerente@concessionaria.test",
        "documento": DOCUMENTO,
        "nome_arquivo": nome_do_arquivo("Auto Center — Zona Sul"),
        "cliente": "Auto Center — Zona Sul",
    }
    argumentos.update(overrides)
    return enviador_email.enviar(**argumentos)


def _mensagem_entregue():
    """Reconstroi a mensagem entregue a partir dos bytes, como o servidor a ve.

    Ler o objeto `EmailMessage` que o codigo montou provaria pouco: o que chega
    na caixa e o que foi SERIALIZADO. Passar por `as_bytes()` e reparsear pega
    cabecalho mal codificado e anexo que nao sobreviveu ao transporte.
    """
    bruta = _SMTPFalso.ultima.mensagem.as_bytes()
    return BytesParser(policy=policy.default).parsebytes(bruta)


# ---------------------------------------------------------------------------
# O que sai
# ---------------------------------------------------------------------------


def test_email_anexa_o_pdf_com_o_nome_do_arquivo(configurado) -> None:
    """O anexo e o PDF, byte a byte, com o nome que o botao de baixar usa."""
    assert _enviar() is None

    anexos = [
        p
        for p in _mensagem_entregue().iter_attachments()
        if p.get_content_type() == "application/pdf"
    ]
    assert len(anexos) == 1, "o documento precisa ir como um único anexo PDF"

    anexo = anexos[0]
    assert anexo.get_payload(decode=True) == DOCUMENTO
    assert anexo.get_filename().endswith(".pdf")


def test_email_o_nome_do_anexo_vem_de_nome_do_arquivo(configurado) -> None:
    """Sem slugificador proprio: o nome e o MESMO do arquivo baixado.

    `nome_do_arquivo()` foi escrito pensando neste caso — a docstring dela cita
    o anexo passando por servidor antigo como a razao de tirar acento. Um
    segundo slugificador aqui divergiria dela no primeiro nome com cedilha.
    """
    esperado = nome_do_arquivo("Auto Center — Zona Sul")
    assert _enviar() is None

    anexos = list(_mensagem_entregue().iter_attachments())
    assert anexos[0].get_filename() == esperado
    assert esperado.isascii(), esperado


def test_email_a_copia_fixa_sai_em_todo_envio(configurado) -> None:
    """Decisao do cliente, 01/09/2026. E o unico registro do que saiu."""
    assert _enviar() is None

    entregue = _mensagem_entregue()
    assert entregue["To"] == "gerente@concessionaria.test"
    assert entregue["Cc"] == enviador_email.COPIA_FIXA
    assert enviador_email.COPIA_FIXA == "joao@suicatech.com.br"


def test_email_o_remetente_vem_das_credenciais(configurado) -> None:
    assert _enviar() is None
    assert _mensagem_entregue()["From"] == CREDENCIAIS["remetente"]


def test_email_assunto_e_corpo_levam_o_nome_do_cliente(configurado) -> None:
    """Como o PDF (D29), a mensagem e endereçada a alguem quando ha nome."""
    assert _enviar() is None

    entregue = _mensagem_entregue()
    assert "Auto Center — Zona Sul" in entregue["Subject"]
    assert "refil de palhetas" in entregue["Subject"]
    # O separador do assunto NAO pode ser travessao: o titulo tem um, e o nome
    # da concessionaria costuma ter outro. Ver a docstring de `assunto()`.
    assert entregue["Subject"].count("—") == 2, entregue["Subject"]
    assert " · Auto Center" in entregue["Subject"]

    corpo = entregue.get_body(preferencelist=("plain",)).get_content()
    assert "Auto Center — Zona Sul" in corpo
    assert "margem de contribuição" in corpo


def test_email_sem_nome_de_cliente_continua_integro(configurado) -> None:
    """Documento generico: o assunto e o titulo, e o corpo abre sem nome."""
    assert _enviar(cliente="", nome_arquivo=nome_do_arquivo("")) is None

    entregue = _mensagem_entregue()
    assert entregue["Subject"] == "Simulação de viabilidade — refil de palhetas"

    corpo = entregue.get_body(preferencelist=("plain",)).get_content()
    assert corpo.startswith("Olá,")
    assert "em anexo" in corpo


def test_email_a_mensagem_nao_promete_nada(configurado) -> None:
    """§4 vale para o corpo do e-mail como vale para a tela.

    O documento sai da sala e ninguem estara ao lado para explicar: o texto que
    o acompanha e o unico contexto que o cliente le antes de abrir o anexo.
    """
    corpo = enviador_email.corpo("Auto Center")
    proibidas = (
        "lucro",
        "rentabil",
        "ROI",
        "garantid",
        "grátis",
        "imperdív",
        "atenção",
        "cuidado",
    )
    for palavra in proibidas:
        assert palavra.lower() not in corpo.lower(), palavra


# ---------------------------------------------------------------------------
# O transporte
# ---------------------------------------------------------------------------


def test_email_usa_starttls_antes_do_login(configurado) -> None:
    """Sem STARTTLS a senha vai em texto claro, e nada na mensagem denuncia."""
    assert _enviar() is None
    assert _SMTPFalso.ultima.chamadas[:3] == ["starttls", "login", "send_message"]
    assert _SMTPFalso.ultima.timeout == enviador_email._TIMEOUT


def test_email_porta_465_usa_ssl_direto(monkeypatch) -> None:
    """465 e SMTPS: o TLS comeca na conexao e `starttls` nao existe ali."""
    credenciais = dict(CREDENCIAIS, porta=465)
    monkeypatch.setattr(
        enviador_email.st, "secrets", {"email": credenciais}, raising=False
    )

    class _SSL(_SMTPFalso):
        pass

    monkeypatch.setattr(smtplib, "SMTP_SSL", _SSL)
    monkeypatch.setattr(smtplib, "SMTP", _SMTPQueDemais)  # nao pode ser usada

    assert _enviar() is None
    assert "starttls" not in _SSL.ultima.chamadas
    assert _SSL.ultima.porta == 465


# ---------------------------------------------------------------------------
# As falhas — §7.4, nenhuma delas levanta
# ---------------------------------------------------------------------------


def test_email_endereco_sem_forma_nao_e_enviado(configurado) -> None:
    for torto in ("", "   ", "gerente", "gerente@", "@concessionaria.test",
                  "gerente@local", "um endereco@com espaco.test"):
        assert not enviador_email.endereco_aceitavel(torto), torto
        assert _enviar(destino=torto) == "endereco"

    assert _SMTPFalso.ultima is None, "nada pode chegar ao transporte"


def test_email_enderecos_de_forma_aceitavel() -> None:
    for bom in (
        "gerente@concessionaria.test",
        "nome.sobrenome@auto-center.com.br",
        "  espaco.na.borda@exemplo.test  ",
    ):
        assert enviador_email.endereco_aceitavel(bom), bom


def test_email_sem_credenciais_devolve_motivo_e_nao_levanta(monkeypatch) -> None:
    """O estado NORMAL da maquina local: nao ha `.streamlit/secrets.toml`.

    `st.secrets` LEVANTA nesse caso, e o app precisa continuar de pe — o botao
    de baixar e o que sempre existe.
    """
    class _SemSegredos:
        def __getitem__(self, _):
            raise FileNotFoundError("no secrets.toml")

    monkeypatch.setattr(enviador_email.st, "secrets", _SemSegredos(), raising=False)

    assert not enviador_email.configurado()
    assert _enviar() == "sem-configuracao"


def test_email_configuracao_incompleta_conta_como_ausente(monkeypatch) -> None:
    """Meia configuracao e pior que nenhuma: quebraria so na hora do envio."""
    for faltando in ("host", "porta", "usuario", "senha"):
        parcial = {k: v for k, v in CREDENCIAIS.items() if k != faltando}
        monkeypatch.setattr(
            enviador_email.st, "secrets", {"email": parcial}, raising=False
        )
        assert not enviador_email.configurado(), faltando


def test_email_servidor_que_recusa_devolve_motivo(monkeypatch) -> None:
    monkeypatch.setattr(
        enviador_email.st, "secrets", {"email": dict(CREDENCIAIS)}, raising=False
    )
    monkeypatch.setattr(smtplib, "SMTP", _SMTPQueRecusa)
    assert _enviar() == "transporte"


def test_email_servidor_pendurado_devolve_motivo(monkeypatch) -> None:
    """O caso que o `timeout` existe para limitar. Nao pode virar excecao."""
    monkeypatch.setattr(
        enviador_email.st, "secrets", {"email": dict(CREDENCIAIS)}, raising=False
    )
    monkeypatch.setattr(smtplib, "SMTP", _SMTPQueDemais)
    assert _enviar() == "transporte"


def test_email_o_teto_por_sessao_existe_e_e_pequeno() -> None:
    """O link e aberto, sem login (plano §6.3). Ver a nota no topo do modulo."""
    assert 1 <= enviador_email.LIMITE_POR_SESSAO <= 10

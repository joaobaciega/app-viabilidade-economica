"""§5.1 — Campo numerico com unidade e total derivado.

"Coletar um numero que participa de multiplicacao sem deixar a leitura
ambigua." Resolve P6: rotulo ambiguo e DEFEITO.

Anatomia:
    Passagens por mes, por ponto de venda        <- t-rotulo, 17px/600
    [ 300 ]                                      <- 56px, t-campo
    -> 3.000 passagens por mes no total          <- t-derivado, 15px

REGRAS (§5.1):
  - o rotulo carrega a unidade SEMPRE, mesmo quando parece obvio
  - o total derivado e recalculado a cada rerun, sem custo — a conta e local
  - quando o multiplicador vale 1, o derivado CONTINUA aparecendo. Sumir com
    ele quando o valor e trivial ensina o cliente a nao procura-lo quando
    deixa de ser
  - estado vazio: o derivado NAO aparece — nao existe total de nada
  - estado invalido: NAO EXISTE estado invalido visivel. O min_value impede a
    entrada; nada pisca vermelho (§3.1.2 — nenhuma cor semantica de alerta)

Padrao de rotulo (§4):
    <Grandeza>, <unidade explicita>
    -> <total derivado> <unidade do total>
Sem o total derivado, o campo esta INCOMPLETO.

NOTA DE IMPLEMENTACAO — `value=None` literal, nao `session_state.get(...)`:
Passar `value=` e `key=` juntos e ler o proprio session_state para o `value`
faz o Streamlit brigar consigo mesmo (o widget ja e a fonte da verdade da
chave). `value=None` estatico e o jeito documentado de abrir um number_input
vazio: na primeira renderizacao ele fica em branco, e a partir do primeiro
toque o session_state[key] passa a mandar. Isso tambem faz `novo_cliente()`
funcionar de graca — apagar a chave devolve o campo ao estado vazio.
"""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st


def _renderizar(
    *,
    chave: str,
    rotulo: str,
    minimo: float | int,
    passo: float | int,
    formato_num: str,
    derivado: Callable[[float], str] | None,
    legenda: str | None,
) -> float | None:
    # NENHUM campo desta familia colapsa o rotulo. O parametro `oculto` existiu
    # ate D23 para a grade 2x3 do cashback, em que o cabecalho da coluna nomeava
    # o campo; a grade acabou justamente porque um rotulo que so existe no
    # cabecalho nao sobrevive ao empilhamento do celular (§9.6).
    st.number_input(
        rotulo,
        key=chave,
        min_value=minimo,
        step=passo,
        format=formato_num,
        value=None,
    )

    valor = st.session_state.get(chave)
    tem_valor = valor is not None and valor != ""

    # O total derivado vira um chip destacado em vez de legenda cinza: e o
    # elemento que impede a conta errada de ser dita em voz alta (§1.3 do
    # plano), portanto precisa ser PROCURADO, nao tolerado.
    if tem_valor and derivado is not None:
        st.markdown(
            f'<p class="st-derivado">{derivado(float(valor))}</p>',
            unsafe_allow_html=True,
        )
    if legenda:
        st.markdown(
            f'<p class="st-legenda-bloco">{legenda}</p>', unsafe_allow_html=True
        )

    return float(valor) if tem_valor else None


def campo_quantidade(
    *,
    chave: str,
    rotulo: str,
    derivado: Callable[[float], str] | None = None,
    minimo: int = 0,
    passo: int = 1,
) -> float | None:
    """Quantidade inteira: passagens, consultores, dias uteis."""
    return _renderizar(
        chave=chave,
        rotulo=rotulo,
        minimo=minimo,
        passo=passo,
        formato_num="%d",
        derivado=derivado,
        legenda=None,
    )


def campo_moeda(
    *,
    chave: str,
    rotulo: str,
    derivado: Callable[[float], str] | None = None,
    legenda: str | None = None,
) -> float | None:
    """Valor em reais, com centavos.

    ⚠️ DECISAO F EM ABERTO (§10-F, §5.2): NAO existe validacao de piso de
    preco. `min_value=0.0` impede apenas numero negativo, que nao e piso — e
    ausencia de sentido. Nao acrescente `min_value` com valor comercial aqui.
    A validacao V6 aborta o app se alguem tentar declarar um piso.
    """
    return _renderizar(
        chave=chave,
        rotulo=rotulo,
        minimo=0.0,
        passo=0.01,
        formato_num="%.2f",
        derivado=derivado,
        legenda=legenda,
    )


def campo_percentual(
    *,
    chave: str,
    rotulo: str,
    maximo: int = 100,
    ajuda: str | None = None,
) -> int:
    """Percentual inteiro (substituicao, aliquota). Tem default, nao abre vazio."""
    return int(
        st.slider(
            rotulo,
            min_value=0,
            max_value=maximo,
            key=chave,
            format="%d%%",
            help=ajuda,
        )
    )

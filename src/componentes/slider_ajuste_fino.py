"""§5.4 — Slider de ajuste fino. SECUNDARIO.

"Permitir um valor que nao seja um dos tres presets. NADA ALEM DISSO."

    ajuste fino ─────────────────────────────       <- t-derivado
    0% ──────────────●──────────────────── 60%
                    27%

REGRAS (§5.4):
  - rotulado literalmente "ajuste fino". NUNCA com destaque maior que os presets
  - dominio 0-60%. Este dominio e o do grafico da §5.11 sao O MESMO VALOR —
    mudar um obriga a mudar o outro, senao o marcador sai do grafico. Por isso
    os dois leem `parametros.SLIDER_DOMINIO`, e V5 verifica que ele cobre os
    presets
  - MOVER O SLIDER NAO ALTERA O TRASEIRO. O traseiro so muda por preset ou pelo
    seu proprio controle em Ajustes avancados. Acoplar os dois recriaria
    exatamente o risco n. 1 do plano
  - nao especifique nem tente feedback durante o arraste. ELE NAO EXISTE
    (§3, camada C). O st.slider dispara ao soltar

Se o CSS do polegar quebrar, ele volta ao tamanho padrao do Streamlit —
pequeno, mas ainda operavel. Toleravel PORQUE o slider e secundario. Se o
protagonista dependesse dessa camada, nao seria (§3.4).
"""

from __future__ import annotations

import streamlit as st

from src import parametros as P
from src.estado import K_CONV_D


def slider() -> None:
    lo, hi = P.SLIDER_DOMINIO

    st.markdown('<p class="st-ajuste-fino">ajuste fino</p>', unsafe_allow_html=True)
    st.slider(
        "Aproveitamento dianteiro",
        min_value=lo,
        max_value=hi,
        key=K_CONV_D,
        format="%d%%",
        label_visibility="collapsed",
    )
    # Repare no que NAO esta aqui: nenhuma escrita em K_CONV_T.
    # O traseiro nao acompanha o dianteiro (risco n. 1 do plano).

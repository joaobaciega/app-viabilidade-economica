"""§5.14 — Estado de reconexao. E o ping keep-awake (plano §6.5).

"Se a conexao oscilar, o que o cliente ve NAO PODE SER UM ERRO VERMELHO NO MEIO
DO PITCH."

O Streamlit exibe um aviso nativo de desconexao com estilo proprio. Tratamento
(em css.py, secao 10): CSS que NEUTRALIZA A COR desse aviso (para
--tinta-discreta sobre --superficie-2) e o reposiciona no rodape, junto a faixa
do vendedor.

REGRAS (§5.14):
  - NAO OCULTE O AVISO COMPLETAMENTE. O vendedor precisa saber que caiu;
    ocultar troca um constrangimento por uma confusao pior
  - o ultimo resultado renderizado PERMANECE NA TELA durante a reconexao. Nada
    e limpo, nada vira esqueleto de carregamento. Em Streamlit isso e o
    comportamento padrao desde que nada dependa de st.empty() sendo limpo antes
    do recalculo — NAO use st.empty().empty() no caminho do recalculo (§7.2)
  - verificacao: com o wi-fi desligado, o que aparece na area visivel ao
    cliente NAO E UMA CAIXA VERMELHA

ESTE COMPONENTE NAO E UM "MODO OFFLINE". Nao existe modo offline nesta stack
(§1, §3 camada C, §7.1). Ele apenas evita que a queda vire cena.

O app NAO PROMETE, em nenhum texto, funcionamento sem rede. O checklist §12
("Promessa da stack") verifica a ausencia dessa promessa por grep.
"""

from __future__ import annotations

import streamlit as st

# Intervalo do ping keep-awake. O Community Cloud hiberna apos 12 h sem
# trafego (plano §6.2), e um app de vendas usado 2 ou 3 vezes por semana
# estaria dormindo em quase toda visita — risco 6 do plano, probabilidade
# MUITO ALTA.
#
# O ping REDUZ a hibernacao, mas NAO SUBSTITUI o item de checklist pre-visita
# (abrir o app 5 min antes de entrar na concessionaria). Isso esta em
# docs/CHECKLIST-PRE-VISITA.md e e requisito de OPERACAO, nao de codigo.
INTERVALO_PING_MS = 10 * 60 * 1000  # 10 minutos


def manter_acordado() -> None:
    """Recarrega o fragmento periodicamente para gerar trafego.

    Usa st.fragment com run_every: o rerun e limitado ao fragmento, portanto
    NAO redesenha o bloco de resultado e nao interfere no que o cliente esta
    lendo. Isso importa: um rerun global a cada 10 minutos no meio de uma
    reuniao seria pior que a hibernacao.
    """

    @st.fragment(run_every=INTERVALO_PING_MS / 1000)
    def _ping() -> None:
        # Nada e renderizado. O efeito desejado e o trafego do websocket.
        return None

    _ping()

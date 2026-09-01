"""CAMADA B — CSS injetado. 🔧 FRAGIL (DESIGN.md §3, camada B).

TODO o CSS do app vive neste arquivo. Nao ha CSS em nenhum outro lugar.
Concentrar aqui e o que torna o reteste possivel quando a versao do Streamlit
subir — voce abre um arquivo, nao caca seletor em quinze.

OBRIGACOES DESTA CAMADA (§3, camada B):
  - requirements.txt fixa a versao com == (streamlit==1.58.0)
  - todo item desta camada esta marcado 🔧 abaixo
  - subida de versao = RETESTE VISUAL de todos os itens 🔧, registrado em
    docs/DIVERGENCIAS.md

DEGRADACAO ESCOLHIDA: se todo este CSS morrer, os tres botoes de cenario
continuam funcionando e continuam mostrando o cenario ativo, porque o estado
ativo usa type="primary" NATIVO. So o tamanho degrada.

ESPECIFICIDADE — a armadilha que ja quebrou esta tela uma vez:
o Streamlit estiliza paragrafo de markdown com um seletor de dois niveis
(`[data-testid="stMarkdownContainer"] p`, 0-1-1). Uma classe sozinha (0-1-0)
PERDE a cascata, e a traducao renderiza em 16px em vez de 48px. Por isso as
propriedades tipograficas das classes proprias levam !important.

GANCHOS QUE ENVOLVEM FILHOS usam `st-key-*`, de st.container(key=...), que e
API PUBLICA. Um <div> injetado por st.markdown abre e FECHA a propria div e nao
envolve nada — ja custou os 96px dos botoes de cenario uma vez.

DIVERGENCIAS DECLARADAS (docs/DIVERGENCIAS.md):
  D1 raio 14px/8px         §3.5 pede 4px "nada arredondado demais"
  D2 icones de linha       P10 pede "sem icone decorativo"
  D3 reordenacao por CSS   §8 pede checagem de largura no codigo
  D5 vermelho ampliado     §3.1 restringe a 2 lugares; o cliente pediu mais
  D6 cartao de resultado escuro   §3.1 pede superficie branca dominante
  D7 sombra sutil em cartao       §3.5 pede "elevacao por traco, nenhuma sombra"
  D20 tabela propria, cabecalho grudado, ritmo de secao e tiles de altura igual
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Tokens tipograficos (§3.2), expostos em Python para que o checklist possa
# afirmar as duas regras de checagem automatica sem parsear CSS.
#
# A escala e DUPLA, organizada por QUEM LE e A QUE DISTANCIA.
# ---------------------------------------------------------------------------

# Escala CLIENTE — legivel a 100 cm, em angulo, sob luz forte
T_TRADUCAO = 48
T_ANUAL = 36
T_PRESET_VALOR = 32
T_MENSAL = 22
T_PRESET_NOME = 22

# Escala OPERADOR — legivel a 40 cm, pelo vendedor.
#
# COMPACTADA EM D22 (27/08/2026): o rotulo caiu de 17 para 15px e o texto do
# campo de 20 para 17px, a pedido do cliente ("os campos estao muito grandes, a
# parte de preenchimento ocupa espaco demais"). A escala continua DUPLA e
# continua inteiramente abaixo da escala do cliente (22px), que e o que
# `test_escala_dupla_existe` protege.
T_ROTULO = 15
T_CAMPO = 17
T_DERIVADO = 15
T_PREMISSAS = 15
T_VENDEDOR = 12

PISO_TEXTO_CLIENTE = 22

# Altura de campo (§3.4, divergido em D22).
#
# O DESIGN fixa "minimo global: 56px — acima dos 44px habituais,
# deliberadamente". D22 desce para os 44px HABITUAIS, e nao um pixel abaixo:
# 44x44 e o piso de alvo de toque do WCAG 2.5.5 e das diretrizes de iOS e
# Android. Num celular, campo menor que isso e campo que o dedo erra — e o
# cliente pediu compactacao E portabilidade para celular na mesma frase.
ALTURA_CAMPO = 44

# --- Cor -------------------------------------------------------------------
# Superficies mornas em vez de branco/cinza puros: e o que tira o ar de
# "aplicacao de 2005" sem introduzir matiz nenhuma alem do vermelho da marca.
SUPERFICIE = "#FFFFFF"
SUPERFICIE_2 = "#F7F4F3"
SUPERFICIE_3 = "#EFEAE8"
TINTA_PRIMARIA = "#0B0B0B"
TINTA_SECUNDARIA = "#52514E"
TINTA_DISCRETA = "#898781"
TRACO = "#DED7D4"
GRADE = "#E9E3E1"

# ⚠️ K — provisorio validado (§3.1.1): 5,88:1 sobre branco.
MARCA_VERMELHO = "#C8102E"
MARCA_ESCURO = "#94091F"
MARCA_LAVADO = "#FDF3F5"  # tinta de fundo, para o vermelho aparecer sem saturar
MARCA_BORDA = "#F2CFD6"

# D6 — o cartao de resultado e escuro. Branco sobre #141414 da 17,9:1, mais
# contraste do que preto sobre branco tinha. A area escura e um CARTAO, nao a
# pagina: o risco de reflexo da §3.1 valia para superficie dominante.
SUPERFICIE_ESCURA = "#141414"
SUPERFICIE_ESCURA_2 = "#1F1D1D"
TINTA_CLARA = "#FFFFFF"
TINTA_CLARA_2 = "#B9B4B2"

RAIO_CARTAO = 14  # D1
RAIO_CAMPO = 8  # D1

ALTURA_FAIXA_VENDEDOR = 62


def _cabecalho_claro() -> str:
    """Variante do cabecalho para logo COLORIDO (src.marca.FUNDO_CLARO = True).

    Troca a faixa vermelha por superficie branca com filete vermelho embaixo, e
    inverte a tinta do titulo e das pilulas de navegacao. Um logo colorido sobre
    fundo vermelho nao tem contraste; esta variante existe para o caso de voce
    preferir a versao colorida da marca.
    """
    return """
.st-key-cabecalho {
  background: var(--superficie) !important;
  border-bottom: 3px solid var(--marca);
  box-shadow: var(--sombra-cartao) !important;
}
.st-titulo-tela { color: var(--tinta-secundaria) !important; }
.st-marca { color: var(--tinta-primaria) !important; }
.st-key-navegacao label {
  background: var(--superficie-2); border-color: var(--traco);
}
.st-key-navegacao label:hover { background: var(--superficie-3); }
.st-key-navegacao label p { color: var(--tinta-secundaria) !important; }
.st-key-navegacao label:has(input:checked) {
  background: var(--marca); border-color: var(--marca-escuro);
}
.st-key-navegacao label:has(input:checked) p {
  color: var(--tinta-clara) !important;
}
.st-key-cabecalho :focus-visible { outline-color: var(--marca) !important; }
"""


def _folha() -> str:
    from src import marca

    # A variante vai no FIM da folha: cascata igual, quem vem depois vence.
    variante = _cabecalho_claro() if marca.FUNDO_CLARO else ""
    return f"""
<style>
/* ===================================================================
   0. Tokens
   =================================================================== */
:root {{
  color-scheme: light;

  --superficie:        {SUPERFICIE};
  --superficie-2:      {SUPERFICIE_2};
  --superficie-3:      {SUPERFICIE_3};
  --superficie-escura: {SUPERFICIE_ESCURA};
  --superficie-escura-2: {SUPERFICIE_ESCURA_2};
  --tinta-primaria:    {TINTA_PRIMARIA};
  --tinta-secundaria:  {TINTA_SECUNDARIA};
  --tinta-discreta:    {TINTA_DISCRETA};
  --tinta-clara:       {TINTA_CLARA};
  --tinta-clara-2:     {TINTA_CLARA_2};
  --traco:             {TRACO};
  --grade:             {GRADE};

  --marca:             {MARCA_VERMELHO};
  --marca-escuro:      {MARCA_ESCURO};
  --marca-lavado:      {MARCA_LAVADO};
  --marca-borda:       {MARCA_BORDA};

  --t-traducao:      {T_TRADUCAO}px;
  --t-anual:         {T_ANUAL}px;
  --t-preset-valor:  {T_PRESET_VALOR}px;
  --t-mensal:        {T_MENSAL}px;
  --t-preset-nome:   {T_PRESET_NOME}px;
  --t-rotulo:        {T_ROTULO}px;
  --t-campo:         {T_CAMPO}px;
  --t-derivado:      {T_DERIVADO}px;
  --t-premissas:     {T_PREMISSAS}px;
  --t-vendedor:      {T_VENDEDOR}px;

  --raio-cartao: {RAIO_CARTAO}px;
  --raio-campo:  {RAIO_CAMPO}px;

  --altura-campo: {ALTURA_CAMPO}px;

  /* D7 — sombra MUITO sutil. Nao e vocabulario de material publicitario:
     e 1px de profundidade para o cartao nao parecer recortado com tesoura.
     Sob luz forte ela desaparece e o traco de 1px sustenta sozinho. */
  --sombra-cartao: 0 1px 2px rgba(11,11,11,.05), 0 1px 8px rgba(11,11,11,.04);
  --sombra-hero:   0 2px 4px rgba(11,11,11,.16), 0 12px 32px rgba(11,11,11,.14);

  --dur: 130ms;
  --curva: cubic-bezier(.2,0,0,1);
}}

@media (prefers-reduced-motion: reduce) {{
  * {{ transition-duration: 1ms !important; animation-duration: 1ms !important; }}
}}

html, body, .stApp {{ background: var(--superficie-2) !important; }}

/* ===================================================================
   1. Marca do framework — §6.1.9: nada disso aparece, em nenhuma resolucao
   =================================================================== */
#MainMenu, header [data-testid="stMainMenu"],
footer, [data-testid="stFooter"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stAppDeployButton, [data-testid="stAppDeployButton"],
a[href*="streamlit.io"] {{
  display: none !important; visibility: hidden !important;
}}
header[data-testid="stHeader"] {{
  height: 0 !important; min-height: 0 !important; background: transparent !important;
}}
/* A lateral nao e usada: a navegacao mora no cabecalho da propria pagina.
   Ocultamos a lateral E o controle que a abriria, para nao sobrar affordance
   morto — e porque ocultar a barra superior torna esse controle inalcancavel. */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {{ display: none !important; }}

/* ===================================================================
   2. Pagina 🔧
   =================================================================== */
.stMainBlockContainer, .block-container {{
  padding: 0 28px calc({ALTURA_FAIXA_VENDEDOR}px + 28px) !important;
  max-width: none !important;
}}
[data-testid="stVerticalBlock"] {{ gap: 0.6rem; }}

/* ===================================================================
   3. Cabecalho — faixa vermelha de largura total. D5.
   E aqui que o vermelho ganha presenca: uma area, nao um detalhe.

   GRUDADO NO TOPO (D20). A Tela 1 rola: resultado, faixa de premissas,
   tiles, grafico, tabela, formula, PDF. Com o cabecalho rolando junto, a
   navegacao entre as tres telas ficava fora de alcance justamente quando o
   vendedor precisa dela — no meio da conversa, para conferir o preco da
   original. `position: sticky` resolve sem componente e sem JS.
   Ele NAO ganha altura por isso: 71px do mesmo cabecalho que ja existia.
   =================================================================== */
.st-key-cabecalho {{
  position: sticky; top: 0; z-index: 80;
  margin: 0 -28px 20px !important;
  padding: 14px 28px 13px !important;
  background: linear-gradient(180deg, var(--marca) 0%, var(--marca-escuro) 100%);
  box-shadow: 0 1px 0 rgba(0,0,0,.16), 0 6px 18px rgba(148,9,31,.18);
}}
.st-marca {{
  display: inline-flex; align-items: center; gap: 9px;
  font-size: 21px !important; font-weight: 800 !important;
  letter-spacing: .11em;
  color: var(--tinta-clara) !important;
  text-transform: uppercase;
}}
.st-marca .st-icone svg {{ stroke-width: 2.1; }}
/* O logo em arquivo (assets/logo.*), embutido como data: URI por src/marca.py.
   `height` fixa a altura e `width: auto` preserva a proporcao qualquer que
   seja o arquivo — nao deformamos a marca de ninguem.

   D25: o lockup atual e horizontal e tem DOIS andares (palavra-marca +
   `INTRACE Br`), 1600x301. A 44px de altura ele sai com ~234px de largura, bem
   dentro do teto de 380px, e a palavra-marca fica em ~30px — legivel. O
   `max-width` continua aqui porque ele e a rede: uma arte muito mais larga
   encolhe em vez de empurrar a navegacao para fora da faixa. */
.st-logo {{
  display: block; height: 44px; width: auto;
  max-width: 380px; object-fit: contain;
  image-rendering: -webkit-optimize-contrast;
}}
.st-titulo-tela {{
  display: block; margin-top: 1px;
  font-size: var(--t-derivado) !important; font-weight: 500 !important;
  letter-spacing: .03em;
  color: rgba(255,255,255,.82) !important;
}}

/* Navegacao dentro da faixa vermelha — pilulas brancas. */
.st-key-navegacao {{ display: flex; justify-content: flex-end; align-items: center; }}
.st-key-navegacao [data-testid="stWidgetLabel"] {{ display: none !important; }}
.st-key-navegacao [data-testid="stRadio"] > div {{
  gap: 6px !important; flex-wrap: nowrap !important;
}}
.st-key-navegacao label {{
  min-height: 44px; display: flex; align-items: center;
  padding: 0 15px !important; border-radius: 999px;
  background: rgba(255,255,255,.13);
  border: 1px solid rgba(255,255,255,.28);
  transition: background var(--dur) var(--curva);
}}
.st-key-navegacao label:hover {{ background: rgba(255,255,255,.22); }}
.st-key-navegacao label p {{
  font-size: var(--t-derivado) !important; font-weight: 600 !important;
  color: rgba(255,255,255,.92) !important; white-space: nowrap !important;
}}
.st-key-navegacao label > div:first-child {{ display: none !important; }}
.st-key-navegacao label:has(input:checked) {{
  background: var(--superficie); border-color: var(--superficie);
}}
.st-key-navegacao label:has(input:checked) p {{
  color: var(--marca-escuro) !important; font-weight: 700 !important;
}}

/* ===================================================================
   4. Titulos de secao — etiqueta vermelha + filete. D5.
   =================================================================== */
.st-secao {{
  display: flex; align-items: center; gap: 9px;
  font-size: var(--t-derivado) !important; font-weight: 700 !important;
  letter-spacing: .09em; text-transform: uppercase;
  color: var(--marca-escuro) !important;
  /* PROXIMIDADE (D20): o titulo pertence ao cartao que vem DEPOIS dele, e nao
     ao que vem antes. Antes eram 22px acima e 12px abaixo — quase simetrico,
     e um titulo simetrico flutua entre dois cartoes em vez de encabecar um.
     Mais ar acima, menos abaixo: a area de campos le como cinco grupos com
     titulo, nao como dez faixas alternadas.
     D22 apertou os dois valores (era 28/9) mantendo a proporcao. */
  margin: 17px 0 6px !important; padding: 0 0 6px;
  border-bottom: 2px solid var(--marca-borda);
}}
.st-secao .st-icone {{ color: var(--marca); }}
.st-secao .st-secao-nota {{
  margin-left: auto; text-transform: none; letter-spacing: 0;
  font-weight: 500 !important; color: var(--tinta-discreta) !important;
}}

/* ===================================================================
   5. Cartoes 🔧  — D1, D7
   =================================================================== */
[data-testid="stVerticalBlockBorderWrapper"] > div {{
  border-radius: var(--raio-cartao) !important;
}}
div[data-testid="stExpander"] details {{
  border-radius: var(--raio-cartao) !important;
  border-color: var(--traco) !important;
  background: var(--superficie) !important;
  box-shadow: var(--sombra-cartao) !important;
}}
div[data-testid="stExpander"] summary p {{
  font-size: var(--t-rotulo) !important; font-weight: 600 !important;
  color: var(--tinta-primaria) !important;
}}
div[data-testid="stExpander"] summary {{ min-height: 56px; }}
div[data-testid="stExpander"] summary svg {{ fill: var(--marca) !important; }}

/* Cartoes de entrada — barra vermelha na borda esquerda. D5.
   Cada um e um st.container(key=...), nao um <div> injetado: markdown com
   `<div>` fecha sozinho e o cartao sai como pilula vazia. */
.st-key-entrada_operacao,
.st-key-entrada_hoje,
.st-key-entrada_dianteiro,
.st-key-entrada_traseiro,
.st-key-entrada_cashback {{
  background: var(--superficie);
  border: 1px solid var(--traco);
  border-left: 4px solid var(--marca);
  border-radius: var(--raio-campo);
  box-shadow: var(--sombra-cartao);
  /* D22: era 12px 16px 14px, com 14px de margem embaixo. */
  padding: 9px 14px 10px !important;
  margin-bottom: 9px;
}}
/* D23 — o cashback deixou de ser grade 2x3. Cada categoria virou um titulo por
   cima de tres campos rotulados, e o titulo do segundo grupo precisa de ar: sem
   ele "Consultor · traseiro" encosta no chip de subtotal do dianteiro. */
.st-key-entrada_cashback .st-rotulo-categoria {{ margin: 12px 0 5px !important; }}

/* Atalhos de aproveitamento traseiro — pequenos de proposito. Sao controle de
   OPERACAO, nao o protagonista: os 96px sao dos presets do dianteiro (§5.3). */
.st-key-atalhos_traseiro {{ margin: -8px 0 2px !important; }}
.st-key-atalhos_traseiro [data-testid="stHorizontalBlock"] {{ gap: 6px !important; }}
.st-key-atalhos_traseiro [data-testid="stButton"] button {{
  min-height: 44px !important; height: 44px !important;
  border-radius: var(--raio-campo) !important;
  background: var(--superficie-2) !important;
  border: 1px solid var(--traco) !important;
  box-shadow: none !important;
}}
.st-key-atalhos_traseiro [data-testid="stButton"] button:hover {{
  border-color: var(--marca) !important; background: var(--marca-lavado) !important;
}}
.st-key-atalhos_traseiro [data-testid="stButton"] button p {{
  font-size: var(--t-rotulo) !important; font-weight: 700 !important;
  color: var(--tinta-secundaria) !important;
}}

.st-rotulo-categoria {{
  font-size: var(--t-derivado) !important;
  color: var(--tinta-secundaria) !important;
  margin: 0 0 8px !important;
}}
.st-rotulo-categoria b {{
  color: var(--marca-escuro) !important; font-weight: 700 !important;
  letter-spacing: .03em;
}}

/* ===================================================================
   6. Campos 🔧  (§3.4, divergido em D22 — 44px, o piso de alvo de toque)
   O DESIGN pedia 56px "acima dos 44 habituais, deliberadamente". D22 desce
   para 44, e nao abaixo: e o minimo do WCAG 2.5.5 e das diretrizes de iOS e
   Android, e o app precisa funcionar no celular.
   =================================================================== */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {{
  height: var(--altura-campo) !important;
  font-size: var(--t-campo) !important; font-weight: 600 !important;
  color: var(--tinta-primaria) !important;
  border-radius: var(--raio-campo) !important;
  background: var(--superficie-2) !important;
  border: 1px solid var(--traco) !important;
  transition: border-color var(--dur) var(--curva),
              box-shadow var(--dur) var(--curva);
}}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {{
  background: var(--superficie) !important;
  border-color: var(--marca) !important;
  box-shadow: 0 0 0 3px var(--marca-lavado) !important;
}}
/* O selectbox usava o visual NATIVO do Streamlit, do lado dos campos proprios —
   inconsistencia visivel nas Telas 2 e 3. Aqui ele entra na mesma regra da
   §3.4. O seletor de baseweb e interno, e portanto fragil: se ele mudar de
   nome numa atualizacao, o campo volta ao visual nativo, que continua
   funcional. Degradacao aceitavel, como no resto da camada B. */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
  min-height: var(--altura-campo) !important;
  border-radius: var(--raio-campo) !important;
  background: var(--superficie-2) !important;
  border: 1px solid var(--traco) !important;
  transition: border-color var(--dur) var(--curva),
              box-shadow var(--dur) var(--curva);
}}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {{
  background: var(--superficie) !important;
  border-color: var(--marca) !important;
  box-shadow: 0 0 0 3px var(--marca-lavado) !important;
}}
[data-testid="stNumberInput"] label p,
[data-testid="stTextInput"] label p,
[data-testid="stSlider"] label p,
[data-testid="stCheckbox"] label p,
[data-testid="stSelectbox"] label p {{
  font-size: var(--t-rotulo) !important; font-weight: 600 !important;
  color: var(--tinta-primaria) !important; line-height: 1.3 !important;
}}
/* Sem spinner: alvo pequeno e irrelevante num tablet (§5.1) */
[data-testid="stNumberInput"] button {{ display: none !important; }}

/* ===================================================================
   6.1 RITMO VERTICAL DA AREA DE CAMPOS — D22.
   De onde vinha a altura, e quanto cada peca custava POR CAMPO:

       rotulo 17px + margem do widget      ~30px  ->  ~21px
       campo                                56px  ->   44px
       gap do stVerticalBlock              ~10px  ->   ~5px
       chip derivado / legenda, quando ha  ~34px  ->  ~22px

   Sao ~92px por campo contra ~70px. Somando o padding dos cinco cartoes e a
   margem dos cinco titulos de secao, a estimativa e de 300 a 350px menos na
   area de preenchimento — perto de um quarto dela. ESTIMATIVA, e nao medicao:
   a altura real depende de quantos rotulos quebram em duas linhas na largura
   de cada coluna, e isso so o navegador responde (item 3 do checklist manual).
   =================================================================== */
[data-testid="stWidgetLabel"] {{ margin-bottom: 2px !important; }}
[data-testid="stNumberInput"] label p,
[data-testid="stTextInput"] label p {{ line-height: 1.25 !important; }}

/* Dentro dos cartoes de campo o empilhamento e mais apertado que no resto da
   pagina. Fora deles o gap global de 0.6rem continua valendo — o resultado e o
   grafico precisam de respiro, os campos nao. */
.st-key-entrada_operacao [data-testid="stVerticalBlock"],
.st-key-entrada_hoje [data-testid="stVerticalBlock"],
.st-key-entrada_dianteiro [data-testid="stVerticalBlock"],
.st-key-entrada_traseiro [data-testid="stVerticalBlock"],
.st-key-entrada_cashback [data-testid="stVerticalBlock"] {{
  gap: 0.3rem !important;
}}

/* O seletor de marca da Tela 3 — o menu suspenso EM EVIDENCIA. Gancho
   `st-key-seletor_marca`, de st.container(key=...).
   Ele e a primeira e, ate a escolha, a UNICA coisa na tela: enquanto nenhuma
   marca estiver escolhida a Tela 3 nao mostra cartao, campo nem lista. Por
   isso ele ganha respiro em volta e o nome da marca escolhida e lido em
   --t-campo, a 1 metro, como os demais campos da §3.4. */
.st-key-seletor_marca {{ margin: 6px 0 22px !important; }}
.st-key-seletor_marca [data-testid="stSelectbox"] label p {{
  font-size: var(--t-rotulo) !important; font-weight: 700 !important;
  letter-spacing: .01em;
}}
.st-key-seletor_marca div[data-baseweb="select"] {{
  font-size: var(--t-campo) !important; font-weight: 600 !important;
  color: var(--tinta-primaria) !important;
}}
.st-key-seletor_marca div[data-baseweb="select"] > div {{
  border-color: var(--marca-borda) !important;
}}
[data-testid="stCaptionContainer"] p {{
  font-size: var(--t-derivado) !important;
  color: var(--tinta-secundaria) !important; line-height: 1.4 !important;
}}
/* Total derivado (§5.1) — chip vermelho lavado, para ele ser PROCURADO.
   D22: era `margin: 6px 0 14px; padding: 4px 11px`. */
.st-derivado {{
  display: inline-block; margin: 3px 0 4px;
  padding: 2px 9px; border-radius: 999px;
  background: var(--marca-lavado); border: 1px solid var(--marca-borda);
  font-size: var(--t-derivado) !important; font-weight: 600 !important;
  color: var(--marca-escuro) !important;
}}

/* ===================================================================
   7. Botoes de cenario — O PROTAGONISTA 🔧  (§5.3, §3.4)
   O gancho e `st-key-cenarios`, de st.container(key=...).
   =================================================================== */
.st-key-cenarios [data-testid="stButton"] button {{
  min-height: 96px !important; height: 96px !important;
  border-radius: var(--raio-cartao) !important;
  white-space: pre-line !important; line-height: 1.1 !important;
  padding: 10px 4px !important;
  border: 1.5px solid var(--marca-borda) !important;
  background: var(--superficie) !important;
  box-shadow: var(--sombra-cartao) !important;
  transition: transform var(--dur) var(--curva),
              box-shadow var(--dur) var(--curva),
              background var(--dur) var(--curva);
}}
.st-key-cenarios [data-testid="stButton"] button p {{
  font-size: var(--t-preset-nome) !important; font-weight: 800 !important;
  letter-spacing: .07em; margin: 0 !important; line-height: 1.2 !important;
  color: var(--tinta-secundaria) !important;
}}
.st-key-cenarios [data-testid="stButton"] button p:last-child {{
  font-size: var(--t-preset-valor) !important; font-weight: 800 !important;
  color: var(--tinta-primaria) !important;
}}
.st-key-cenarios [data-testid="stButton"] button:hover {{
  border-color: var(--marca) !important;
  transform: translateY(-1px);
}}
/* Ativo: preenchimento vermelho. O estado vem de type="primary" NATIVO — se
   este CSS morrer, o botao continua mostrando qual cenario esta ativo. */
.st-key-cenarios [data-testid="stButton"] button[kind="primary"] {{
  background: linear-gradient(180deg, var(--marca) 0%, var(--marca-escuro) 100%) !important;
  border-color: var(--marca-escuro) !important;
  box-shadow: 0 2px 4px rgba(148,9,31,.24), 0 8px 20px rgba(148,9,31,.22) !important;
}}
.st-key-cenarios [data-testid="stButton"] button[kind="primary"] p,
.st-key-cenarios [data-testid="stButton"] button[kind="primary"] p:last-child {{
  color: var(--tinta-clara) !important;
}}
.st-key-cenarios [data-testid="stHorizontalBlock"] {{ gap: 12px !important; }}

/* ===================================================================
   8. Slider 🔧  (§5.4, §3.4) — trilho vermelho. D5.
   Polegar >= 32px, faixa de acerto >= 48px. Se quebrar, volta ao padrao:
   pequeno mas operavel, e toleravel PORQUE o slider e secundario.
   =================================================================== */
[data-testid="stSlider"] {{ padding: 4px 0 0 !important; }}
[data-testid="stSlider"] [data-testid="stWidgetLabel"] {{ margin-bottom: 18px !important; }}
[data-testid="stSlider"] [data-baseweb="slider"] > div {{ min-height: 48px !important; }}
[data-testid="stSlider"] [role="slider"] {{
  height: 32px !important; width: 32px !important;
  box-shadow: 0 1px 3px rgba(148,9,31,.4) !important;
}}
/* O valor corrente do slider e desenhado ACIMA do trilho: o rotulo precisa de
   folga abaixo, senao "0%" cai sobre "AJUSTE FINO". */
.st-ajuste-fino {{
  display: flex; align-items: center; gap: 8px;
  font-size: var(--t-derivado) !important; font-weight: 600 !important;
  letter-spacing: .07em; text-transform: uppercase;
  color: var(--tinta-discreta) !important;
  margin: 10px 0 14px !important;  /* D22: era 18px/20px */
}}
.st-ajuste-fino::after {{
  content: ""; flex: 1; height: 1px; background: var(--traco);
}}

/* ===================================================================
   8.1 BOTAO DE ACAO — o gate da exibicao. D21.
   Gancho `st-key-acao`, de st.container(key="acao").
   =================================================================== */
.st-key-acao {{ margin: 18px 0 10px !important; }}
.st-key-acao [data-testid="stButton"] button {{
  min-height: 64px !important; height: 64px !important;
  border-radius: var(--raio-cartao) !important;
  box-shadow: var(--sombra-cartao) !important;
}}
.st-key-acao [data-testid="stButton"] button p {{
  font-size: var(--t-preset-nome) !important; font-weight: 800 !important;
  letter-spacing: .06em;
}}
.st-key-acao [data-testid="stButton"] button[kind="primary"] {{
  background: var(--marca) !important;
  border-color: var(--marca-escuro) !important;
}}
/* DESABILITADO sem cor semantica (§3.1.2 proibe vermelho de alerta, e o
   projeto nao tem token de erro nenhum): o botao apenas perde o preenchimento
   e ganha traco tracejado. A informacao de que falta algo esta no TEXTO abaixo
   dele, nao na cor — o que tambem sobrevive a daltonismo (§9.4). */
.st-key-acao [data-testid="stButton"] button:disabled {{
  background: var(--superficie-2) !important;
  border: 1.5px dashed var(--traco) !important;
  box-shadow: none !important;
}}
.st-key-acao [data-testid="stButton"] button:disabled p {{
  color: var(--tinta-discreta) !important;
}}
.st-acao-falta {{
  font-size: var(--t-derivado) !important; font-weight: 500 !important;
  line-height: 1.4 !important;
  color: var(--tinta-discreta) !important;
  margin: 8px 0 0 !important; text-align: center;
}}

/* ===================================================================
   8.2 EXPORTAR PDF — D23. Gancho `st-key-exportar`, de
   st.container(key="exportar").

   O `st.download_button` era o unico controle da Tela 1 que entrava com o
   visual NATIVO do Streamlit, no meio de uma tela em que todo o resto passou
   pela §3.4 — parecia peca de outro app. Ele fica em vermelho de marca porque
   e a acao final da area de exportacao e nao divide o espaco com nenhuma
   outra: aqui o vermelho e acao, nao alerta (§3.1.2 restringe o vermelho de
   ALERTA, que continua nao existindo).
   =================================================================== */
.st-key-exportar {{ margin: 12px 0 2px !important; }}
.st-key-exportar [data-testid="stDownloadButton"] button {{
  min-height: 52px !important; height: 52px !important;
  border-radius: var(--raio-campo) !important;
  background: var(--marca) !important;
  border: 1px solid var(--marca-escuro) !important;
  box-shadow: var(--sombra-cartao) !important;
}}
.st-key-exportar [data-testid="stDownloadButton"] button p {{
  font-size: var(--t-rotulo) !important; font-weight: 700 !important;
  letter-spacing: .04em; color: var(--tinta-clara) !important;
}}
.st-key-exportar [data-testid="stDownloadButton"] button:hover {{
  background: var(--marca-escuro) !important;
}}
.st-exportar-nota {{
  display: flex; align-items: baseline; gap: 8px;
  font-size: var(--t-derivado) !important; line-height: 1.4 !important;
  color: var(--tinta-secundaria) !important;
  margin: 0 0 8px !important;
}}
.st-exportar-nota .st-icone {{ color: var(--marca); }}

/* ===================================================================
   9. RESULTADO — TRES CARTOES. D21, e D6 no primeiro deles.
   A ordem e normativa: faturamento adicional -> margem de contribuicao
   adicional -> mark up da operacao.
   HIERARQUIA: o primeiro cartao e o escuro E o maior (--t-traducao, 48px);
   os outros dois sao claros e menores (--t-anual, 36px). A razao 48/36 = 1,33
   e a mesma que a §5.5 exigia entre a traducao e o anual.
   NENHUM numero daqui usa vermelho (§3.1, §13.1): numero financeiro em
   vermelho le como prejuizo, que e o oposto do que o pitch afirma. O destaque
   do primeiro cartao e a superficie ESCURA (17,9:1), nunca preenchimento
   vermelho.
   =================================================================== */
.st-key-resultado {{ margin: 6px 0 4px !important; }}
.st-key-resultado [data-testid="stHorizontalBlock"] {{ gap: 12px !important; }}

.st-cartao {{
  position: relative;
  display: flex; flex-direction: column;
  background: var(--superficie);
  border: 1px solid var(--traco);
  border-radius: var(--raio-cartao);
  box-shadow: var(--sombra-cartao);
  padding: 22px 22px 20px;
  height: 100%; min-height: 220px;
  overflow: hidden;
}}
/* O cartao PRINCIPAL — superficie escura (D6) e regua vermelha no topo, que e
   um dos usos de vermelho autorizados pela §3.1.2. */
.st-cartao--principal {{
  background: var(--superficie-escura);
  border-color: var(--superficie-escura);
  box-shadow: var(--sombra-hero);
}}
.st-cartao--principal::before {{
  content: ""; position: absolute; inset: 0 0 auto 0; height: 4px;
  background: var(--marca);
}}
.st-cartao-rotulo {{
  display: block;
  font-size: var(--t-mensal) !important; font-weight: 700 !important;
  line-height: 1.25 !important;
  color: var(--tinta-secundaria) !important;
  margin: 0 0 10px !important;
}}
.st-cartao-valor {{
  display: block;
  font-size: var(--t-anual) !important; font-weight: 800 !important;
  line-height: 1.1 !important; letter-spacing: -.015em;
  color: var(--tinta-primaria) !important;
  font-variant-numeric: proportional-nums;
  margin: 0 !important;
}}
.st-cartao-apoio {{
  display: block;
  font-size: var(--t-mensal) !important; font-weight: 500 !important;
  line-height: 1.3 !important;
  color: var(--tinta-discreta) !important;
  margin: auto 0 0 !important; padding-top: 10px;
}}
.st-cartao--principal .st-cartao-rotulo {{ color: var(--tinta-clara-2) !important; }}
.st-cartao--principal .st-cartao-valor {{
  font-size: var(--t-traducao) !important;
  color: var(--tinta-clara) !important;
}}
.st-cartao--principal .st-cartao-apoio {{ color: var(--tinta-clara-2) !important; }}

.st-anual {{
  font-size: var(--t-anual) !important; font-weight: 700 !important;
  line-height: 1.15 !important;
  color: var(--tinta-clara) !important;
  font-variant-numeric: proportional-nums;
  margin: 0 !important;
}}
.st-rotulo-resultado {{
  font-size: var(--t-mensal) !important; font-weight: 600 !important;
  line-height: 1.3 !important;
  color: var(--tinta-clara-2) !important;
  margin: 3px 0 18px !important;
}}
.st-mensal {{
  font-size: var(--t-mensal) !important; font-weight: 600 !important;
  line-height: 1.3 !important;
  color: var(--tinta-clara) !important;
  font-variant-numeric: proportional-nums;
  margin: 0 !important;
}}
/* AS LINHAS DE APOIO DO RESULTADO — em tinta ESCURA. D21.
   Elas viviam DENTRO do cartao escuro e por isso eram `--tinta-clara`. Com o
   resultado em tres cartoes, elas passaram a ser desenhadas abaixo deles, sobre
   `--superficie-2`. Manter a tinta clara aqui seria branco sobre claro —
   exatamente o defeito de texto invisivel que a §9 registra. */
.st-linha-apoio {{
  font-size: var(--t-mensal) !important; font-weight: 500 !important;
  line-height: 1.35 !important;
  color: var(--tinta-secundaria) !important;
  margin: 12px 0 0 !important;
}}
/* Cashback — bloco proprio, com marca vermelha a esquerda. E o unico bloco do
   resultado que NAO e margem da concessionaria: ele e pago pela Suicatech, e a
   separacao visual existe para o cliente nao somar as duas coisas por engano. */
.st-cashback {{
  display: block; margin: 14px 0 0 !important; padding: 12px 15px 12px 14px;
  background: var(--superficie);
  border: 1px solid var(--traco);
  border-left: 3px solid var(--marca);
  border-radius: var(--raio-campo);
}}
.st-cashback-valor {{
  display: block;
  font-size: var(--t-mensal) !important; font-weight: 700 !important;
  color: var(--tinta-primaria) !important; line-height: 1.3 !important;
}}
.st-cashback-nota {{
  display: block; margin-top: 2px;
  font-size: var(--t-premissas) !important; font-weight: 500 !important;
  color: var(--tinta-secundaria) !important; line-height: 1.4 !important;
}}
.st-cashback-rateio {{
  display: block; margin-top: 4px;
  font-size: var(--t-premissas) !important; font-weight: 600 !important;
  color: var(--tinta-secundaria) !important;
}}

/* As classes `.st-cash-cabecalho` e `.st-cash-linha` sairam em D23, junto com
   a grade 2x3. O bloco de cashback usa agora `.st-rotulo-categoria` — a mesma
   linha de titulo do bloco do refil — e um `.st-derivado` de subtotal. */

/* "hoje X -> com refil Y" — tambem em tinta escura por D21, mesma razao das
   linhas de apoio acima. */
.st-hoje-refil {{
  display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
  margin: 14px 0 0 !important; padding-top: 14px;
  border-top: 1px solid var(--traco);
  font-size: var(--t-mensal) !important; font-weight: 500 !important;
  color: var(--tinta-secundaria) !important;
}}
.st-hoje-refil b {{ color: var(--tinta-primaria) !important; font-weight: 700 !important; }}
.st-hoje-refil .seta {{ color: var(--marca) !important; font-weight: 800 !important; }}

/* ===================================================================
   9.1 O RESULTADO COMPLETO — a tela espelhando o PDF. D28.
   "A tela de resultados deve ser exatamente igual o que aparece no PDF."

   O CONTEUDO vem de `src/apresentacao.py`, que a tela e o papel consomem
   igual. O que mora aqui e SO a tinta da tela — as mesmas pecas que
   `pdf_visual.py` desenha em vetor, desenhadas em HTML.

   Nenhum bloco desta secao usa `st.container(key=...)`: tudo e HTML proprio
   dentro do container `resultado` que ja existe. Por isso nenhuma regra daqui
   precisa (nem pode) usar classe propria como ancestral de `[data-testid=]`.
   =================================================================== */

/* --- a manchete: os dois numeros, lado a lado, no maior corpo (D26) --- */
.st-manchete {{
  display: flex; align-items: stretch;
  background: var(--superficie-escura);
  border-radius: var(--raio-cartao);
  box-shadow: var(--sombra-hero);
  padding: 22px 26px; margin: 6px 0 6px;
}}
.st-manchete-col {{ flex: 1 1 0; min-width: 0; padding-right: 18px; }}
.st-manchete-col + .st-manchete-col {{
  border-left: 1px solid var(--tinta-secundaria);
  padding-left: 26px; padding-right: 0;
}}
.st-manchete-rotulo {{
  display: block; margin-bottom: 10px;
  font-size: var(--t-derivado) !important; font-weight: 700 !important;
  letter-spacing: .09em; text-transform: uppercase;
  color: var(--tinta-clara-2) !important;
}}
/* `clamp` porque o numero e o unico elemento da tela cuja largura depende do
   cliente: "R$ 7.694.784" numa rede de doze pontos tem o dobro dos caracteres
   de "R$ 141.480", e um corpo fixo cortaria um dos dois. E o equivalente do
   `_fonte_que_cabe` do PDF, resolvido pelo navegador. */
.st-manchete-valor {{
  display: block; line-height: 1.05 !important;
  font-size: clamp(30px, 4.2vw, var(--t-traducao)) !important;
  font-weight: 800 !important; letter-spacing: -.02em;
  color: var(--tinta-clara) !important;
  font-variant-numeric: tabular-nums;
}}
.st-manchete-apoio {{
  display: block; margin-top: 8px;
  font-size: var(--t-mensal) !important; font-weight: 500 !important;
  color: var(--tinta-clara-2) !important;
}}
.st-nota-grupo {{
  font-size: var(--t-derivado) !important; font-weight: 500 !important;
  color: var(--tinta-discreta) !important;
  margin: 0 0 14px !important;
}}

/* --- titulo de secao do resultado, o gemeo de `doc.secao()` ---------- */
.st-secao-res {{
  display: block; margin: 26px 0 4px !important; padding-bottom: 6px;
  border-bottom: 1px solid var(--traco);
  font-size: var(--t-rotulo) !important; font-weight: 700 !important;
  color: var(--tinta-primaria) !important;
}}
.st-secao-nota-res {{
  font-size: var(--t-derivado) !important; font-weight: 500 !important;
  line-height: 1.45 !important;
  color: var(--tinta-secundaria) !important;
  margin: 8px 0 0 !important;
}}

/* --- barras: hoje x com o refil, a segunda EMPILHADA ----------------
   D29: o plot passou de 210px para 340px e a barra de 150px para 190px, a
   pedido do cliente ("deixe esse grafico maior, para ficar mais evidente o
   aumento"). E a peca cujo TAMANHO carrega o argumento: a razao entre as duas
   alturas e o que se le antes de qualquer numero, e num plot baixo uma base
   pequena vira um risco de 10px que nao da para comparar com nada.

   `--altura-barras` existe para haver UM lugar onde mexer nisso: o plot, a
   regua do vao e o espacador do delta tem de ter a MESMA altura, senao o
   rotulo do vao descola da barra que ele mede. */
:root {{ --altura-barras: 340px; }}

.st-barras {{
  display: flex; align-items: flex-end; gap: 26px;
  padding: 34px 0 0; margin: 0;
}}
.st-barra {{
  flex: 0 0 auto; width: 190px;
  display: flex; flex-direction: column; align-items: center;
}}
/* A altura do plot e FIXA e comum as duas colunas: e ela que faz a proporcao
   entre as barras ser lida como proporcao. */
.st-barra-corpo {{
  width: 100%; height: var(--altura-barras);
  display: flex; flex-direction: column; justify-content: flex-end;
}}
/* A PILHA e o que tem a altura do valor; os segmentos sao fracoes DELA. Isso
   e o que permite o rotulo ficar colado no topo da barra (`bottom: 100%`) em
   vez de flutuar no topo da coluna — que era o defeito da primeira versao:
   com a base em 4,8% do plot, "R$ 99.000" aparecia a 300px do risco que ele
   nomeava. No PDF o rotulo sempre ficou colado; aqui nao ficava. */
.st-barra-pilha {{
  position: relative; width: 100%;
  display: flex; flex-direction: column; justify-content: flex-end;
}}
.st-barra-valor {{
  position: absolute; bottom: 100%; left: -14px; right: -14px;
  margin-bottom: 8px; text-align: center;
  font-size: var(--t-anual) !important; font-weight: 800 !important;
  line-height: 1.1 !important;
  color: var(--tinta-primaria) !important;
  font-variant-numeric: tabular-nums;
}}
.st-barra-seg {{ width: 100%; border-radius: 6px 6px 0 0; }}
.st-barra-base {{
  background: var(--superficie-3); border: 1px solid var(--traco);
}}
.st-barra-inc {{ background: var(--marca); }}
/* Incremental NEGATIVO: o vao que falta, em contorno tracejado. Nao e
   vermelho — numero e barra de perda em vermelho leem como alerta, e a §13.1
   nao autoriza (o desenho ja diz o que houve). */
.st-barra-falta {{
  border: 1.5px dashed var(--tinta-secundaria);
  border-bottom: none; background: transparent;
}}
.st-barra-nome {{
  display: block; margin-top: 10px; text-align: center;
  font-size: var(--t-rotulo) !important; font-weight: 500 !important;
  line-height: 1.35 !important;
  color: var(--tinta-secundaria) !important;
}}
.st-barra-delta {{
  flex: 1 1 auto; height: var(--altura-barras);
  display: flex; flex-direction: column;
}}
.st-barra-delta-vao {{
  display: flex; align-items: center; padding-left: 16px;
  border-left: 3px solid var(--marca);
}}
.st-barra-delta-vao span {{
  font-size: var(--t-anual) !important; font-weight: 800 !important;
  color: var(--marca) !important;
  font-variant-numeric: tabular-nums;
}}
/* Perda: a regua e o valor em tinta primaria, com o sinal (§13.1). */
.st-barra-delta--perda .st-barra-delta-vao {{
  border-left-color: var(--tinta-primaria);
}}
.st-barra-delta--perda .st-barra-delta-vao span {{
  color: var(--tinta-primaria) !important;
}}

/* --- os tres cenarios medidos --------------------------------------- */
.st-cenarios {{ display: flex; gap: 12px; margin: 14px 0 0; }}
.st-cenario {{
  flex: 1 1 0; min-width: 0;
  background: var(--superficie-2);
  border: 1px solid var(--traco);
  border-radius: var(--raio-campo);
  padding: 12px 14px 12px;
}}
/* O ATIVO nao se distingue so por cor (§3.1.3 / §9.4): barra lateral grossa,
   que sobrevive a impressao em preto e branco e ao daltonismo. */
.st-cenario--ativo {{
  background: var(--marca-lavado); border-color: var(--marca-borda);
  border-left: 4px solid var(--marca);
  padding-left: 11px;
}}
.st-cenario-rotulo {{
  display: block;
  font-size: var(--t-derivado) !important; font-weight: 700 !important;
  letter-spacing: .08em; text-transform: uppercase;
  color: var(--tinta-discreta) !important;
}}
.st-cenario--ativo .st-cenario-rotulo {{ color: var(--marca) !important; }}
.st-cenario-aprov {{
  display: block; margin-top: 2px;
  font-size: var(--t-derivado) !important; font-weight: 500 !important;
  color: var(--tinta-secundaria) !important;
}}
.st-cenario-valor {{
  display: block; margin-top: 10px;
  font-size: var(--t-mensal) !important; font-weight: 800 !important;
  color: var(--tinta-primaria) !important;
  font-variant-numeric: tabular-nums;
}}
.st-cenario-apoio {{
  display: block; margin-top: 2px;
  font-size: var(--t-vendedor) !important; font-weight: 500 !important;
  color: var(--tinta-secundaria) !important;
}}

/* --- as secoes de auditoria: `rotulo ....... valor` ------------------ */
.st-linhas {{ display: block; margin: 10px 0 0; }}
.st-linha-par {{
  display: flex; gap: 16px; align-items: baseline;
  padding: 5px 0;
  border-bottom: 1px solid var(--grade);
}}
.st-linha-par:last-child {{ border-bottom: none; }}
.st-linha-rotulo {{
  flex: 1 1 50%; min-width: 0;
  font-size: var(--t-derivado) !important; font-weight: 500 !important;
  line-height: 1.4 !important;
  color: var(--tinta-secundaria) !important;
}}
.st-linha-valor {{
  flex: 1 1 50%; min-width: 0;
  font-size: var(--t-rotulo) !important; font-weight: 600 !important;
  line-height: 1.4 !important;
  color: var(--tinta-primaria) !important;
}}

/* AS QUATRO CLASSES A SEGUIR SAO DE TINTA CLARA e so funcionam sobre superficie
   escura. Nenhuma e usada pela Tela 1 desde D21 — ficam porque ainda ha
   referencia a elas em `cartao_comparativo.py` (.st-anual, .st-rotulo-resultado)
   e em `estado_vazio_catalogo.py` (.st-falta-ancora), e porque apaga-las
   deixaria esses caminhos sem estilo se alguem os reativar.
   NAO as use em tela clara: sobre branco elas desaparecem. */
.st-falta-ancora {{
  font-size: var(--t-mensal) !important; font-weight: 600 !important;
  line-height: 1.45 !important;
  color: var(--tinta-clara) !important; margin: 0 !important;
}}
.st-falta-ancora span {{
  display: block; margin-top: 8px; font-weight: 400 !important;
  color: var(--tinta-clara-2) !important;
}}

/* ===================================================================
   10. Rotulo e valor de cartao — herdados dos tiles de KPI (D5).
   OS TILES DA TELA 1 FORAM REMOVIDOS por D21, junto do modulo
   `componentes/tiles_kpi.py` e das regras `st-key-kpis` e `st-kpi` (escritas
   aqui sem o ponto de proposito: o checklist casa `.st-key-*` com os
   containers reais, e uma mencao em comentario contaria como referencia).
   Estas duas classes CONTINUAM porque as Telas 2 e 3 e o cartao de preco de
   palheta as usam sobre superficie clara:
     tela2_mais_vendidos.py, tela3_preco_original.py, cartao_preco_palheta.py
   =================================================================== */
.st-kpi-rotulo {{
  display: block;
  font-size: var(--t-vendedor) !important; font-weight: 700 !important;
  letter-spacing: .08em; text-transform: uppercase;
  color: var(--tinta-discreta) !important; margin: 0 0 5px !important;
}}
.st-kpi-valor {{
  display: block; font-size: 26px !important; font-weight: 800 !important;
  line-height: 1.1 !important; color: var(--tinta-primaria) !important;
  font-variant-numeric: proportional-nums; margin: 0 !important;
}}

/* ===================================================================
   11. Faixa de premissas  (§5.6) — aparece SEMPRE
   =================================================================== */
.st-premissas {{
  background: var(--superficie);
  border: 1px solid var(--traco);
  border-left: 4px solid var(--marca-borda);
  border-radius: var(--raio-campo);
  padding: 11px 15px; margin-top: 12px;
  font-size: var(--t-premissas) !important; line-height: 1.55 !important;
  color: var(--tinta-secundaria) !important;
}}
.st-premissas b {{ color: var(--tinta-primaria) !important; font-weight: 700 !important; }}
/* Marcadores de procedencia: glifos monocromaticos, NUNCA cor (§5.7) */
.st-proc {{ color: var(--tinta-discreta) !important; font-weight: 500 !important; }}

/* ===================================================================
   12. Chips e marcadores  (§5.7, §5.12)
   =================================================================== */
.st-chip {{
  display: inline-flex; align-items: center; gap: 5px;
  border: 1px solid var(--traco); border-radius: 999px;
  background: var(--superficie-2);
  color: var(--tinta-secundaria) !important;
  font-size: var(--t-derivado) !important; font-weight: 600 !important;
  padding: 3px 10px; margin: 0 4px 4px 0;
}}
/* MarcadorDecisaoAberta (§5.12): borda TRACEJADA, sem cor de alerta */
.st-chip--aberto {{ border-style: dashed; background: var(--superficie); }}
.st-legenda-bloco {{
  font-size: var(--t-derivado) !important; line-height: 1.4 !important;
  color: var(--tinta-secundaria) !important; margin: 3px 0 0 !important;
}}
.st-icone svg {{
  width: 1em; height: 1em; vertical-align: -0.125em;
  stroke: currentColor; fill: none;
  stroke-width: 1.85; stroke-linecap: round; stroke-linejoin: round;
}}

/* ===================================================================
   13. Faixa do vendedor 🔧  (§5.9, §3.3.1)
   12px, cinza discreto, sem caixa, sem icone, sem cor. A 100 cm, 12px
   subtende ~4,8px de leitura normal: ILEGIVEL. E o mecanismo do canal
   privado, nao um descuido. ALTURA RESERVADA — nao empurra o layout.
   =================================================================== */
.st-faixa-vendedor {{
  position: fixed; inset: auto 0 0 0;
  min-height: {ALTURA_FAIXA_VENDEDOR}px;
  display: flex; flex-direction: column; justify-content: center; gap: 1px;
  padding: 8px 190px 8px 28px;
  background: var(--superficie);
  border-top: 1px solid var(--traco);
  font-size: var(--t-vendedor) !important; line-height: 1.42 !important;
  color: var(--tinta-discreta) !important;
  z-index: 90;
}}
.st-faixa-vendedor p {{
  margin: 0;
  font-size: var(--t-vendedor) !important;
  color: var(--tinta-discreta) !important;
  line-height: 1.42 !important;
}}
.st-faixa-vendedor .st-fv-meta {{ opacity: .8; }}

/* `novo cliente` DENTRO da faixa (§5.9), nao na barra superior — ali seria um
   botao destrutivo na regiao mais visivel ao cliente. */
.st-key-faixa_novo_cliente {{
  position: fixed !important; right: 28px; bottom: 13px;
  width: auto !important; z-index: 96;
}}
.st-key-faixa_novo_cliente [data-testid="stButton"] button {{
  min-height: 36px !important; height: 36px !important;
  padding: 0 14px !important; border-radius: 999px !important;
  background: var(--superficie) !important;
  border: 1px solid var(--traco) !important; box-shadow: none !important;
}}
.st-key-faixa_novo_cliente [data-testid="stButton"] button:hover {{
  border-color: var(--marca) !important; background: var(--marca-lavado) !important;
}}
.st-key-faixa_novo_cliente [data-testid="stButton"] button p {{
  font-size: var(--t-vendedor) !important; font-weight: 600 !important;
  color: var(--tinta-secundaria) !important;
}}

/* ===================================================================
   14. Estado de reconexao 🔧  (§5.14)
   NAO oculta o aviso nativo — NEUTRALIZA a cor e o move para o rodape.
   Ocultar troca um constrangimento por uma confusao pior.
   =================================================================== */
[data-testid="stConnectionStatus"], div[class*="stConnectionStatus"] {{
  position: fixed !important;
  bottom: 4px !important; right: 190px !important;
  top: auto !important; left: auto !important; transform: none !important;
  background: var(--superficie-2) !important;
  color: var(--tinta-discreta) !important;
  border: 1px solid var(--traco) !important;
  border-radius: 999px !important; box-shadow: none !important;
  font-size: var(--t-vendedor) !important; padding: 2px 10px !important;
  z-index: 95 !important;
}}
[data-testid="stConnectionStatus"] * {{
  color: var(--tinta-discreta) !important; fill: var(--tinta-discreta) !important;
  background: transparent !important; font-size: var(--t-vendedor) !important;
}}

/* ===================================================================
   15. Deducoes e interruptores
   =================================================================== */
[data-testid="stCheckbox"] label {{ min-height: 44px; }}
hr, [data-testid="stDivider"] hr {{ border-color: var(--traco) !important; }}
[data-testid="stVegaLiteChart"] {{ min-height: 300px; }}
.st-key-grafico [data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--superficie); box-shadow: var(--sombra-cartao);
}}

/* ===================================================================
   15.1 TABELA PROPRIA — o gemeo em tabela (§5.11), desenhado. D20.
   NAO ha regra para `[data-testid="stDataFrame"]` porque nao ha mais
   `st.dataframe` no app: ele desenha numa <canvas>, nao aceita CSS nenhum, e
   por isso as duas tabelas eram os unicos objetos da tela fora da linguagem
   visual do resto — cabecalho, tipografia e cantos do framework no meio de
   cartoes proprios. Uma <table> de verdade obedece a esta folha como qualquer
   outro elemento. Ver src/componentes/tabela.py.
   =================================================================== */
.st-tabela {{
  max-height: 340px; overflow: auto;
  border: 1px solid var(--traco);
  border-radius: var(--raio-campo);
  background: var(--superficie);
  scrollbar-width: thin;
  scrollbar-color: var(--traco) var(--superficie-2);
}}
.st-tabela table {{
  width: 100%; border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}}
.st-tabela th, .st-tabela td {{
  padding: 9px 14px; text-align: left; white-space: nowrap;
  line-height: 1.35 !important;
}}
/* Numero alinhado a DIREITA. Com `tabular-nums` acima os digitos ficam de
   largura fixa, milhar cai embaixo de milhar e a coluna vira uma regua —
   e conferir uma coluna de margem de relance e a funcao da tabela. */
.st-tabela .st-tabela-num {{ text-align: right; }}
.st-tabela thead th {{
  position: sticky; top: 0; z-index: 1;
  background: var(--superficie-3);
  border-bottom: 1px solid var(--traco);
  font-size: var(--t-vendedor) !important; font-weight: 700 !important;
  letter-spacing: .07em; text-transform: uppercase;
  color: var(--tinta-secundaria) !important;
}}
.st-tabela tbody td {{
  border-top: 1px solid var(--grade);
  font-size: var(--t-derivado) !important; font-weight: 500 !important;
  color: var(--tinta-primaria) !important;
}}
.st-tabela tbody td:first-child {{
  font-weight: 700 !important; color: var(--tinta-secundaria) !important;
}}
.st-tabela tbody tr:hover td {{ background: var(--superficie-2); }}
/* MARCADOR DA POSICAO ATUAL — o mesmo ponto que o grafico desenha (§5.11),
   trazido para o gemeo: sem ele a tabela mostra a curva inteira e nao mostra
   ONDE o cliente esta nela. Fundo lavado e filete vermelho a esquerda;
   NENHUM numero vira vermelho (§13.1). Vem depois do :hover de proposito —
   as duas regras empatam em especificidade e a ultima vence. */
.st-tabela tbody tr.st-tabela-atual td {{
  background: var(--marca-lavado);
  color: var(--tinta-primaria) !important; font-weight: 700 !important;
}}
.st-tabela tbody tr.st-tabela-atual td:first-child {{
  border-left: 3px solid var(--marca); padding-left: 11px;
}}
.st-tabela::-webkit-scrollbar {{ width: 11px; height: 11px; }}
.st-tabela::-webkit-scrollbar-track {{ background: var(--superficie-2); }}
.st-tabela::-webkit-scrollbar-thumb {{
  background: var(--traco); border-radius: 999px;
  border: 3px solid var(--superficie-2);
}}
.st-tabela::-webkit-scrollbar-thumb:hover {{ background: var(--tinta-discreta); }}

/* ===================================================================
   16. Responsividade  (§8)
   Tablet paisagem e o alvo primario; quando houver conflito, o tablet ganha.

   D3 FOI REVOGADA POR D21. Ela existia para inverter a ordem das DUAS COLUNAS
   abaixo de 1024px — o resultado subia acima das entradas, porque em retrato
   quem le e o cliente. Nao ha mais duas colunas: os campos ocupam a largura
   toda e o resultado vem depois deles em qualquer largura, por decisao de
   produto. Com isso saiu tambem a regra que dependia do container `corpo`, que
   deixou de existir (nome escrito sem o prefixo de classe de proposito — ver a
   nota da secao 10).

   O que sobra aqui e empilhar as colunas internas dos cartoes de campo, e
   PRESERVAR em linha os tres grupos que nao podem empilhar: os presets, o
   cabecalho e os tres cartoes de resultado.
   =================================================================== */
@media (max-width: 1023px) {{
  [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; }}
  /* Quatro grupos NAO empilham, e cada um por um motivo diferente:
     - cenarios: tres botoes lado a lado sao a forma do controle (§5.3)
     - resultado: a linha de tres cartoes e a leitura do resultado
     - cabecalho: marca a esquerda, navegacao a direita
     - cashback: tres campos por categoria cabem em linha ate 768px, e em
       linha eles cabem na mesma tela que o resto do cartao. Abaixo de 768px
       a excecao e REVOGADA no bloco do celular — desde D23 cada campo carrega
       o proprio rotulo, e empilhar deixou de custar informacao. */
  .st-key-cenarios [data-testid="stHorizontalBlock"],
  .st-key-resultado [data-testid="stHorizontalBlock"],
  .st-key-cabecalho [data-testid="stHorizontalBlock"],
  .st-key-entrada_cashback [data-testid="stHorizontalBlock"] {{
    flex-direction: row !important;
  }}
  .st-key-cenarios [data-testid="stColumn"],
  .st-key-resultado [data-testid="stColumn"],
  .st-key-cabecalho [data-testid="stColumn"],
  .st-key-entrada_cashback [data-testid="stColumn"] {{ order: 0 !important; }}
}}

/* Abaixo de 900px os tres cartoes de resultado tambem empilham: a 48px, o
   numero do cartao principal nao cabe em um terco dessa largura, e um numero
   cortado e pior do que um empilhamento. */
@media (max-width: 899px) {{
  .st-key-resultado [data-testid="stHorizontalBlock"] {{
    flex-direction: column !important;
  }}
  .st-cartao {{ min-height: 0; }}
}}

/* ===================================================================
   CELULAR (<= 767px) — D22
   O alvo primario continua sendo o tablet paisagem, mas o app tem de ser
   usavel no celular: e o aparelho que o vendedor tem no bolso.

   O QUE NAO MUDA AQUI, de proposito:
     - a altura dos campos continua 44px. E o piso de alvo de toque, e num
       celular ele vale MAIS, nao menos
     - o grafico mantem 300px. Reduzi-lo torna a curva ilegivel; e melhor rolar
   =================================================================== */
@media (max-width: 767px) {{
  /* Tipografia do CLIENTE reduzida em um passo (§8). A do operador nao cai:
     ela ja esta em 15/17px depois de D22.

     Por que o piso de 22px da §3.2 nao se aplica aqui: ele foi derivado de
     "legivel a 100 cm, em angulo, sob luz forte" — a cena do tablet inclinado
     sobre a mesa. Um celular e lido a 30-40 cm, na mao de quem le. A mesma
     conta que pedia 22px a um metro pede menos da metade disso a 40 cm. A
     folha ja fazia isso com a traducao e o anual desde a §8 original. */
  :root {{ --t-traducao: 36px; --t-anual: 28px; --t-mensal: 20px; }}

  /* Largura e o recurso escasso: 28px de padding de cada lado custam 14% da
     tela de um celular de 390px. */
  .stMainBlockContainer, .block-container {{
    padding-left: 14px !important; padding-right: 14px !important;
    padding-bottom: 84px !important;
  }}
  .st-key-cabecalho {{ margin: 0 -14px 14px !important; padding: 10px 14px !important; }}
  /* A reserva de 190px a direita existe para o botao `novo cliente` nao cobrir
     o texto de procedencia — que e justamente o que a faixa existe para
     mostrar (§5.9). No celular a reserva diminui junto com o botao, mas NAO
     desaparece: sem ela os dois se sobrepoem. */
  .st-faixa-vendedor {{ padding: 6px 118px 6px 14px; }}
  .st-key-faixa_novo_cliente {{ right: 14px; bottom: 9px; }}

  /* O cabecalho empilha: marca em cima, navegacao embaixo, pilulas podendo
     quebrar em duas linhas. Lado a lado a 390px, o logo de 380px e as tres
     pilulas nao cabem — a navegacao seria cortada, e ela e o unico caminho
     para as Telas 2 e 3. */
  .st-key-cabecalho [data-testid="stHorizontalBlock"] {{
    flex-direction: column !important; gap: 8px !important;
  }}
  .st-key-navegacao {{ justify-content: flex-start; }}
  .st-key-navegacao [data-testid="stRadio"] > div {{ flex-wrap: wrap !important; }}
  .st-logo {{ height: 34px; max-width: 100%; }}

  /* Presets: 72px em vez de 96. Continuam sendo o maior alvo da tela. */
  .st-key-cenarios [data-testid="stButton"] button {{
    min-height: 72px !important; height: 72px !important;
  }}
  .st-key-cenarios [data-testid="stHorizontalBlock"] {{ gap: 6px !important; }}
  .st-key-cenarios [data-testid="stButton"] button p {{ letter-spacing: .02em; }}

  /* Cartoes de campo: menos padding. */
  .st-key-entrada_operacao,
  .st-key-entrada_hoje,
  .st-key-entrada_dianteiro,
  .st-key-entrada_traseiro,
  .st-key-entrada_cashback {{
    padding: 8px 10px 9px !important;
  }}

  /* CASHBACK — D23 REVOGA A EXCECAO DE D22.
     Ate D22 a grade de cashback ficava em linha em qualquer largura: eram
     QUATRO colunas (categoria + tres destinatarios) e, a 390px, campos de
     ~85px com rotulo nenhum, porque quem nomeava a coluna era um cabecalho
     que o empilhamento levava embora. D22 registrou isso como "o compromisso
     escolhido"; o cliente pediu que deixasse de ser.
     Agora cada campo tem rotulo proprio, sao tres colunas em vez de quatro, e
     empilhar nao perde nada: o campo passa de ~85px para a largura inteira do
     cartao. Custa altura — tres campos por categoria, um por linha — e essa e
     a troca. Esta regra vem DEPOIS da excecao de 1023px de proposito: mesma
     especificidade, e a ultima vence. */
  .st-key-entrada_cashback [data-testid="stHorizontalBlock"] {{
    flex-direction: column !important;
    /* O gap aqui e VERTICAL: e a folga entre o campo de um destinatario e o
       rotulo do proximo. Com 0 o rotulo encosta no campo de cima e os tres
       viram um bloco so. 6px e o mesmo ritmo do empilhamento dentro dos
       cartoes (0,3rem). */
    gap: 6px !important;
  }}
  .st-key-entrada_cashback [data-testid="stColumn"] {{ width: 100% !important; }}

  .st-cartao {{ padding: 16px 16px 14px; }}
  .st-tabela {{ max-height: 260px; }}

  /* D28 — o resultado completo no celular. As tres pecas que NAO cabem em
     linha a 390px empilham; as barras continuam lado a lado porque comparar
     duas alturas e a propria leitura do desenho. */
  .st-manchete {{ flex-direction: column; padding: 16px 18px; }}
  .st-manchete-col {{ padding: 0; }}
  .st-manchete-col + .st-manchete-col {{
    border-left: none; border-top: 1px solid var(--tinta-secundaria);
    padding: 14px 0 0; margin-top: 14px;
  }}
  .st-cenarios {{ flex-direction: column; gap: 8px; }}
  /* As barras continuam LADO A LADO: comparar duas alturas e a propria leitura
     do desenho, e empilhadas elas deixariam de comparar. O plot encolhe de
     340px para 220px — ainda o suficiente para a razao entre as duas ser
     lida —, e a coluna do vao vira uma faixa estreita a direita. */
  .st-barras {{ gap: 8px; padding-top: 26px; }}
  .st-barra {{ width: auto; flex: 1 1 0; min-width: 0; }}
  :root {{ --altura-barras: 220px; }}
  .st-barra-delta {{ flex: 0 0 auto; }}
  .st-barra-delta-vao {{ padding-left: 8px; }}
  .st-barra-valor {{ font-size: var(--t-mensal) !important; left: -6px; right: -6px; }}
  .st-barra-delta-vao span {{ font-size: var(--t-mensal) !important; }}
  .st-barra-nome {{ font-size: var(--t-derivado) !important; }}
  /* O par `rotulo / valor` vira duas linhas: a 390px, 50% de largura para um
     rotulo como "Preço ao consumidor final, por par (dianteiro)" o quebra em
     quatro linhas contra um valor de uma. */
  .st-linha-par {{ flex-direction: column; gap: 0; }}
  .st-linha-rotulo, .st-linha-valor {{ flex: none; width: 100%; }}
}}

/* §9: foco visivel em todos os controles. NUNCA outline: none. */
:focus-visible {{
  outline: 2px solid var(--marca) !important; outline-offset: 2px !important;
}}
.st-key-cabecalho :focus-visible {{
  outline-color: var(--tinta-clara) !important;
}}

/* Variante de cabecalho claro, quando o logo escolhido e colorido. Vazia por
   default; vem por ultimo de proposito, para vencer as regras acima. */
{variante}
</style>
"""


def injetar() -> None:
    """Injeta a folha da camada B. Chamado uma vez, no inicio do script."""
    st.markdown(_folha(), unsafe_allow_html=True)

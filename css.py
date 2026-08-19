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

# Escala OPERADOR — legivel a 40 cm, pelo vendedor
T_ROTULO = 17
T_CAMPO = 20
T_DERIVADO = 15
T_PREMISSAS = 15
T_VENDEDOR = 12

PISO_TEXTO_CLIENTE = 22

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
   =================================================================== */
.st-key-cabecalho {{
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
   seja o arquivo — nao deformamos a marca de ninguem. */
/* 44px com o recorte de dois andares (palavra-marca + assinatura) deixa a
   palavra-marca em ~26px — legivel. Com o lockup de tres andares no mesmo
   espaco ela cairia para ~18px e a assinatura viraria borrao: o lockup inteiro
   vive no PDF, onde ha espaco (ver src/marca.py). */
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
  margin: 22px 0 12px !important; padding: 0 0 8px;
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
.st-key-kpis [data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--superficie);
  border-radius: var(--raio-cartao);
  box-shadow: var(--sombra-cartao);
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
.st-key-entrada_traseiro {{
  background: var(--superficie);
  border: 1px solid var(--traco);
  border-left: 4px solid var(--marca);
  border-radius: var(--raio-campo);
  box-shadow: var(--sombra-cartao);
  padding: 12px 16px 14px !important;
  margin-bottom: 14px;
}}
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
   6. Campos 🔧  (§3.4 — minimo 56px, acima dos 44 habituais)
   =================================================================== */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {{
  height: 56px !important;
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
[data-testid="stCaptionContainer"] p {{
  font-size: var(--t-derivado) !important;
  color: var(--tinta-secundaria) !important; line-height: 1.4 !important;
}}
/* Total derivado (§5.1) — chip vermelho lavado, para ele ser PROCURADO. */
.st-derivado {{
  display: inline-block; margin: 6px 0 14px;
  padding: 4px 11px; border-radius: 999px;
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
  margin: 18px 0 20px !important;
}}
.st-ajuste-fino::after {{
  content: ""; flex: 1; height: 1px; background: var(--traco);
}}

/* ===================================================================
   9. BLOCO DE RESULTADO — cartao escuro. D6.
   A ordem e normativa: traducao -> anual -> mensal.
   REGRA: t-traducao >= 1,25 x t-anual (48/36 = 1,33). Inverter e o erro de
   implementacao mais provavel desta tela.
   NENHUM numero daqui usa vermelho (§3.1, §13.1): numero financeiro em
   vermelho le como prejuizo, que e o oposto do que o pitch afirma.
   =================================================================== */
/* O cartao E o proprio container com key — nao um wrapper interno. Depender de
   `[data-testid="stVerticalBlockBorderWrapper"]` aqui deixou o fundo escuro sem
   aplicar e o texto branco sobre branco: invisivel. */
.st-key-resultado {{
  position: relative;
  background: var(--superficie-escura) !important;
  border-radius: var(--raio-cartao);
  box-shadow: var(--sombra-hero);
  padding: 30px 28px 24px !important;
  margin-top: 6px;
  overflow: hidden;
}}
/* Regua vermelha de 4px no topo do cartao — um dos usos autorizados (§3.1.2) */
.st-key-resultado::before {{
  content: ""; position: absolute; inset: 0 0 auto 0; height: 4px;
  background: linear-gradient(90deg, var(--marca) 0%, var(--marca-escuro) 100%);
}}
.st-key-resultado [data-testid="stVerticalBlockBorderWrapper"],
.st-key-resultado [data-testid="stVerticalBlockBorderWrapper"] > div {{
  background: transparent !important; border: none !important;
  padding: 0 !important;
}}
.st-traducao {{
  font-size: var(--t-traducao) !important; font-weight: 800 !important;
  line-height: 1.08 !important; letter-spacing: -.015em;
  color: var(--tinta-clara) !important;
  font-variant-numeric: proportional-nums;
  margin: 0 0 22px !important;
}}
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
.st-linha-apoio {{
  font-size: var(--t-mensal) !important; font-weight: 500 !important;
  line-height: 1.35 !important;
  color: var(--tinta-clara-2) !important;
  margin: 12px 0 0 !important;
}}
/* Cashback — dentro do cartao escuro, com marca vermelha a esquerda. E o unico
   bloco do resultado que NAO e margem da concessionaria: ele e pago pela
   Suicatech, e a separacao visual existe para o cliente nao somar as duas
   coisas por engano. */
.st-cashback {{
  display: block; margin: 16px 0 0 !important; padding: 12px 0 2px 14px;
  border-left: 3px solid var(--marca);
}}
.st-cashback-valor {{
  display: block;
  font-size: var(--t-mensal) !important; font-weight: 700 !important;
  color: var(--tinta-clara) !important; line-height: 1.3 !important;
}}
.st-cashback-nota {{
  display: block; margin-top: 2px;
  font-size: var(--t-premissas) !important; font-weight: 500 !important;
  color: var(--tinta-clara-2) !important; line-height: 1.4 !important;
}}
.st-cashback-rateio {{
  display: block; margin-top: 4px;
  font-size: var(--t-premissas) !important; font-weight: 600 !important;
  color: var(--tinta-clara-2) !important;
}}

/* Grade de cashback em Ajustes avancados */
.st-cash-cabecalho {{
  font-size: var(--t-derivado) !important; font-weight: 700 !important;
  letter-spacing: .05em; text-transform: uppercase;
  color: var(--marca-escuro) !important;
  margin: 8px 0 2px !important; text-align: center;
}}
.st-cash-linha {{
  font-size: var(--t-derivado) !important; line-height: 1.35 !important;
  color: var(--tinta-secundaria) !important;
  margin: 14px 0 0 !important;
}}
.st-cash-linha b {{
  color: var(--tinta-primaria) !important; font-size: var(--t-rotulo) !important;
}}

/* "hoje X -> com refil Y" */
.st-hoje-refil {{
  display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
  margin: 18px 0 0 !important; padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,.14);
  font-size: var(--t-mensal) !important; font-weight: 500 !important;
  color: var(--tinta-clara-2) !important;
}}
.st-hoje-refil b {{ color: var(--tinta-clara) !important; font-weight: 700 !important; }}
.st-hoje-refil .seta {{ color: var(--marca) !important; font-weight: 800 !important; }}
/* Estado vazio, dentro do cartao escuro (§7.3: e a abertura da conversa) */
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
   10. Tiles de KPI — a grade de cartoes do dashboard do cliente. D5.
   =================================================================== */
.st-key-kpis {{ margin: 14px 0 18px !important; }}
.st-key-kpis [data-testid="stHorizontalBlock"] {{ gap: 10px !important; }}
.st-kpi {{
  background: var(--superficie);
  border: 1px solid var(--traco);
  border-top: 3px solid var(--marca);
  border-radius: var(--raio-campo);
  box-shadow: var(--sombra-cartao);
  padding: 11px 13px 12px;
  height: 100%;
}}
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
.st-kpi-nota {{
  display: block; font-size: var(--t-vendedor) !important;
  color: var(--tinta-secundaria) !important; margin: 4px 0 0 !important;
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
  font-size: var(--t-derivado) !important; line-height: 1.45 !important;
  color: var(--tinta-secundaria) !important; margin: 6px 0 0 !important;
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
[data-testid="stDataFrame"] {{ border-radius: var(--raio-campo); overflow: hidden; }}
[data-testid="stVegaLiteChart"] {{ min-height: 300px; }}
.st-key-grafico [data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--superficie); box-shadow: var(--sombra-cartao);
}}

/* ===================================================================
   16. Responsividade  (§8) — D3
   Tablet paisagem e o alvo primario; quando houver conflito, o tablet ganha.
   Abaixo de 1024px a coluna do RESULTADO sobe acima das entradas, porque quem
   le nessa orientacao e o cliente. O Streamlit empilha na ordem de declaracao
   e a coluna de entradas e declarada primeiro, entao invertemos por `order`.
   =================================================================== */
@media (max-width: 1023px) {{
  [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; }}
  .st-key-corpo > div > [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"]:first-child {{ order: 2 !important; }}
  .st-key-corpo > div > [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"]:last-child {{ order: 1 !important; }}
  .st-key-cenarios [data-testid="stHorizontalBlock"],
  .st-key-kpis [data-testid="stHorizontalBlock"],
  .st-key-cabecalho [data-testid="stHorizontalBlock"] {{
    flex-direction: row !important;
  }}
  .st-key-cenarios [data-testid="stColumn"],
  .st-key-kpis [data-testid="stColumn"],
  .st-key-cabecalho [data-testid="stColumn"] {{ order: 0 !important; }}
}}

/* Celular: tipografia reduzida em um passo (§8). O grafico MANTEM 300px —
   reduzi-lo torna a curva ilegivel, e e melhor rolar. */
@media (max-width: 767px) {{
  :root {{ --t-traducao: 36px; --t-anual: 28px; }}
  .st-key-cenarios [data-testid="stButton"] button {{
    min-height: 72px !important; height: 72px !important;
  }}
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

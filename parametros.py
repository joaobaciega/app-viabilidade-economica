"""Parametros do app — o UNICO lugar onde numeros vivem.

DESIGN.md §5.12: "Um valor em aberto NUNCA e substituido por um numero
plausivel no codigo. Ele vive num unico modulo parametros.py com o valor
marcado como provisorio, e a tela mostra o marcador."

DESIGN.md §12, "Decisoes em aberto": "Nenhum valor da §10 aparece fixado
fora de parametros.py."

Regra de ouro deste arquivo: se voce esta tentando escolher um numero para
destravar alguma coisa, PARE. Um chute fixado no codigo vira verdade em duas
semanas (DESIGN §0.3).

As validacoes V1-V7 (§11.2) rodam em validacao_parametros.py e sao chamadas
no import de src/__init__.py. Parametro invalido = o app NAO SOBE, com erro
no log do deploy — nunca uma tela quebrada na frente do cliente (§7.4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Procedencia (DESIGN §5.7) — a natureza de cada numero na tela.
#
# A distincao carteira_medida x derivado no traseiro e OBRIGATORIA e nao e
# preciosismo: ela ataca o risco n. 1 do plano. Se o 7% e o 13% do traseiro
# forem apresentados com a mesma autoridade do 30% do dianteiro, o app esta
# vendendo derivacao como medicao, e o erro so aparece no mes 3 do cliente.
# ---------------------------------------------------------------------------

Origem = Literal["carteira_medida", "derivado"]
Unidade = Literal["par", "unitario"]


@dataclass(frozen=True)
class Preset:
    """Um cenario de aproveitamento — numero COM procedencia.

    DESIGN §11.1: "O campo origem e a novidade estrutural: o plano trata os
    presets como numeros, e a interface precisa deles como numeros com
    procedencia."
    """

    nome: str
    rotulo: str
    dianteiro: float  # 0-1
    traseiro: float  # 0-1
    origem_dianteiro: Origem
    origem_traseiro: Origem


@dataclass(frozen=True)
class Categoria:
    """Uma categoria do catalogo.

    DESIGN §5.13 / §11.1: `unidade` e ATRIBUTO DECLARADO por categoria,
    nunca constante global e nunca inferida do nome. V3 aborta o app se
    estiver ausente, e nunca assume `par` por default.
    """

    nome: str
    rotulo: str
    unidade: Unidade
    rotulo_unidade: str  # como aparece no rotulo do campo: "por par (dianteiro)"


# ---------------------------------------------------------------------------
# Presets de aproveitamento (plano §3.2, §8 decisao 2 e C)
#
# Dianteiro: carteira real de 15+ concessionarias. NAO e estimativa — e dado
# proprio, e a palavra "estimativa" e PROIBIDA junto deles (DESIGN §4).
#
# Traseiro: so a linha realista (10%) foi medida. Os extremos sao derivados
# do dianteiro pela mesma proporcao (0,67x e 1,33x) e obrigatoriamente
# marcados `≈ derivado`, nunca `◆ carteira` (DESIGN §5.7, §10-H).
# ---------------------------------------------------------------------------

PRESETS: tuple[Preset, ...] = (
    Preset(
        nome="pessimista",
        rotulo="PESSIMISTA",
        dianteiro=0.20,
        traseiro=0.07,
        origem_dianteiro="carteira_medida",
        origem_traseiro="derivado",  # ⚠️ H — derivado, nao medido
    ),
    Preset(
        nome="realista",
        rotulo="REALISTA",
        dianteiro=0.30,
        traseiro=0.10,
        origem_dianteiro="carteira_medida",
        origem_traseiro="carteira_medida",  # a unica linha medida nos dois
    ),
    Preset(
        nome="otimista",
        rotulo="OTIMISTA",
        dianteiro=0.40,
        traseiro=0.13,
        origem_dianteiro="carteira_medida",
        origem_traseiro="derivado",  # ⚠️ H — derivado, nao medido
    ),
)

# Legenda de procedencia dos presets do dianteiro (DESIGN §5.3).
# "argumento comercial, nao nota de rodape". A palavra "estimativa" e proibida aqui.
LEGENDA_PRESETS_DIANTEIRO = (
    "Aproveitamento dianteiro medido em 15+ concessionárias "
    "da carteira Suicatech — não é estimativa"
)
LEGENDA_PRESETS_TRASEIRO = (
    "10% medido na carteira · extremos derivados do dianteiro "
    "na mesma proporção — não medidos"
)

# ---------------------------------------------------------------------------
# Categorias do catalogo (plano §8, decisoes 4, 5 e B)
#
# DESIGN §5.13, regra critica: "E PROIBIDO derivar o preco ou o custo do
# traseiro a partir do dianteiro por qualquer fator, inclusive / 2. Nao e
# arredondamento, e erro de fato."
#
# O par dianteiro tem DUAS medidas diferentes (motorista e passageiro).
# O traseiro e lamina unica. As duas formas coexistem na mesma tela.
# ---------------------------------------------------------------------------

CATEGORIAS: tuple[Categoria, ...] = (
    Categoria(
        nome="dianteiro",
        rotulo="Dianteiro",
        unidade="par",
        rotulo_unidade="por par (dianteiro)",
    ),
    Categoria(
        nome="traseiro",
        rotulo="Traseiro",
        unidade="unitario",
        rotulo_unidade="por unidade (traseiro)",
    ),
)

# ---------------------------------------------------------------------------
# Operacao
# ---------------------------------------------------------------------------

# Default seguro, quase nunca muda (DESIGN §6.1.4). Fica em Ajustes avancados.
DIAS_UTEIS_PADRAO: int = 22

# Limiar da regra R1 (DESIGN §6.1.8): acima disso a faixa do vendedor avisa.
# Vem do plano §3.2: "se passagens / consultores / dias uteis passar de ~20
# veiculos/consultor/dia, o app avisa".
CARGA_MAXIMA_VEICULOS_DIA: float = 20.0

# Dominio do slider E do eixo X do grafico — O MESMO VALOR NOS DOIS.
# DESIGN §5.4: "mudar um obriga a mudar o outro, senao o marcador sai do
# grafico". V5 verifica que ele cobre todos os presets.
SLIDER_DOMINIO: tuple[int, int] = (0, 60)

# Pontos de venda: o unico campo primario com default (DESIGN §6.1.4).
PONTOS_DE_VENDA_PADRAO: int = 1

# ---------------------------------------------------------------------------
# Canibalizacao — NAO MODELADA (decisao do cliente, 11/08/2026)
#
# O campo de substituicao foi retirado da interface. Consequencia que precisa
# ficar dita: o app passa a assumir PERMANENTEMENTE que nenhuma venda de refil
# tira uma venda da palheta original.
#
# Essa e a premissa MAIS FAVORAVEL POSSIVEL (DESIGN §5.6) e e o risco 7 do
# plano ("canibalizacao anula o incremental"). Por isso ela nao fica implicita:
# a faixa de premissas a declara em toda simulacao, lendo esta constante.
# Trocar para True aqui NAO reativa o campo — reativar exige devolver o
# controle a interface, e a §5.10 proibe premissa que muda o resultado sem
# aparecer na faixa.
CANIBALIZACAO_MODELADA: bool = False

TEXTO_SEM_CANIBALIZACAO = "sem canibalização — todo refil é venda nova"

# Destinatarios do cashback (decisao do cliente, 11/08/2026). O plano §1.4
# falava de consultores, gerentes e mecanicos; o programa atual e este.
DESTINATARIOS_CASHBACK: tuple[str, ...] = ("Consultor", "Gerente", "Marketing")

# ---------------------------------------------------------------------------
# ⚠️ DECISOES EM ABERTO — DESIGN §10
#
# NENHUM destes valores vai fixado no codigo. Todos sao None, e a tela mostra
# MarcadorDecisaoAberta (§5.12). O checklist §12 verifica a AUSENCIA das
# constantes; testes/test_checklist.py falha se algum deixar de ser None.
#
# Quando uma decisao for tomada, o valor entra AQUI e o marcador some junto.
# Nao ha outro lugar para mexer.
# ---------------------------------------------------------------------------

# ⚠️ F — Existe piso de preco que o vendedor nao pode furar?
# Bloqueia: validacao de entrada dos campos de preco e custo.
# Comportamento conservador: NENHUMA validacao de piso. Os campos aceitam
# qualquer numero positivo. DESIGN §5.2: "Nao invente um piso."
# Um piso inventado que o vendedor fure vira erro do app; um piso inventado
# que a Suicatech nao honre vira ancora falsa no cliente.
PISO_PRECO: float | None = None

# ⚠️ G — Quantos codigos de refil cobrem os 97% do mercado?
# Bloqueia: bloco de investimento, estoque e payback.
# Comportamento conservador: o bloco NAO EXISTE na Fase 1 — nao desabilitado,
# ausente. Um campo desabilitado com rotulo promete funcionalidade que nao
# existe; ausencia nao promete nada.
CODIGOS_COBERTURA_97: int | None = None

# ⚠️ I — Coeficientes da rampa dos 3 primeiros meses.
# Bloqueia: projecao de 12 meses.
# Comportamento conservador: ANO = INC x 12, rotulado "ano cheio em regime",
# e `rampa ⚠️ nao aplicada` na faixa de premissas. DESIGN §10: "Nao escolha
# fracoes." O mes 1 nao converte como o mes 12.
RAMPA_MESES: tuple[float, ...] | None = None

# ⚠️ J — Curva de sazonalidade mensal (palheta e produto de chuva).
# Bloqueia: projecao de 12 meses.
# Comportamento conservador: idem. Curva plana NAO e aplicada silenciosamente
# — a ausencia e declarada. O cliente avalia voce no mes seco.
SAZONALIDADE_MENSAL: tuple[float, ...] | None = None

# ⚠️ L — A partir de quantos dias um preco coletado deve ser recoletado?
# Bloqueia: o limiar do aviso de idade na faixa do vendedor (Tela 3).
# Comportamento conservador: NENHUM limiar. A faixa exibe a idade crua em
# dias, sem faixa de severidade. Nao invente 60 nem 180 — esse numero decide
# quando o vendedor refaz a coleta, e ninguem o decidiu.
LIMIAR_IDADE_DIAS: int | None = None


# ---------------------------------------------------------------------------
# Derivados de leitura (nao sao decisoes — sao consultas)
# ---------------------------------------------------------------------------


def preset_por_nome(nome: str) -> Preset | None:
    for p in PRESETS:
        if p.nome == nome:
            return p
    return None


def categoria_por_nome(nome: str) -> Categoria | None:
    for c in CATEGORIAS:
        if c.nome == nome:
            return c
    return None


def rampa_aplicada() -> bool:
    """DESIGN §6.1.5, decisao 3: o rotulo sempre descreve a conta que foi feita."""
    return RAMPA_MESES is not None


def sazonalidade_aplicada() -> bool:
    return SAZONALIDADE_MENSAL is not None


def rotulo_do_anual() -> str:
    """O rotulo do valor anual muda junto com a conta.

    DESIGN §6.1.5: "ANO e regime x 12 enquanto rampa e sazonalidade estiverem
    em aberto, e o rotulo diz isso: 'ano cheio em regime'. Quando os
    coeficientes forem definidos (§10), ANO passa a ser a soma dos 12 meses
    com rampa e sazonalidade aplicadas, e o rotulo muda para 'primeiros 12
    meses'. Trocar a conta sem trocar o rotulo e o jeito mais silencioso de
    o app mentir."
    """
    if rampa_aplicada() or sazonalidade_aplicada():
        return "primeiros 12 meses"
    return "ano cheio em regime"

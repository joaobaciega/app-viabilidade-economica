"""Schema das abas da planilha (plano §6.4, DESIGN v4 §11.1).

O plano §6.4 define tres abas; a interface exige uma quarta (`catalogo_refil`)
e campos adicionais nas outras. Tudo declarado aqui, num lugar so, para que
renomear uma coluna produza ERRO CLARO na publicacao em vez de tela branca no
app.

VERSAO DO SCHEMA: incrementar quando um campo obrigatorio mudar. O app recusa
snapshot de schema incompativel sem tela branca (src/dados/carregar_snapshot.py).
"""

from __future__ import annotations

from dataclasses import dataclass

SCHEMA_VERSAO = 1


@dataclass(frozen=True)
class Coluna:
    nome: str
    obrigatoria: bool = True
    enum: tuple[str, ...] | None = None
    tipo: str = "texto"  # texto | inteiro | decimal | data | booleano


@dataclass(frozen=True)
class Aba:
    nome: str
    colunas: tuple[Coluna, ...]
    obrigatoria: bool = True

    @property
    def nomes(self) -> tuple[str, ...]:
        return tuple(c.nome for c in self.colunas)


# --- Aba `modelos` (plano §6.4 + acrescimos da interface) -------------------
MODELOS = Aba(
    "modelos",
    (
        Coluna("marca"),
        Coluna("modelo"),
        Coluna("ano_lancamento", tipo="inteiro", obrigatoria=False),
        Coluna("emplac_2025", tipo="inteiro"),
        Coluna("emplac_2022_2025", tipo="inteiro", obrigatoria=False),
        Coluna("emplac_2025_varejo", tipo="inteiro", obrigatoria=False),
        Coluna("emplac_2025_direta", tipo="inteiro", obrigatoria=False),
        Coluna("data_lancamento", tipo="data", obrigatoria=False),
        Coluna(
            "perfil_frota",
            obrigatoria=False,
            enum=("picape_comercial",),
        ),
        # Plano §4.2: link para o PDF PUBLICO. NUNCA area logada.
        Coluna("fonte_pdf_url"),
        Coluna("fonte_pdf_pagina", tipo="inteiro", obrigatoria=False),
        Coluna("fonte_data", tipo="data"),
    ),
)

# --- Aba `aplicacao` — a fonte autoritativa de posicao e medida ------------
APLICACAO = Aba(
    "aplicacao",
    (
        Coluna("marca"),
        Coluna("modelo"),
        Coluna("ano_ini", tipo="inteiro"),
        Coluna("ano_fim", tipo="inteiro"),
        Coluna("posicao", enum=("motorista", "passageiro", "traseira")),
        Coluna("medida_mm", tipo="inteiro"),
        Coluna("sku_refil", obrigatoria=False),
    ),
)

# --- Aba `precos_originais` ------------------------------------------------
PRECOS_ORIGINAIS = Aba(
    "precos_originais",
    (
        Coluna("marca"),
        Coluna("modelo"),
        Coluna("ano_ini", tipo="inteiro"),
        Coluna("ano_fim", tipo="inteiro"),
        Coluna("posicao", enum=("motorista", "passageiro", "traseira")),
        Coluna("sku_original", obrigatoria=False),
        # Implementa a §2.7: unidade e atributo por linha, nunca global.
        Coluna("unidade", enum=("par", "unitario")),
        Coluna("preco", tipo="decimal", obrigatoria=False),
        Coluna("url_fonte", obrigatoria=False),
        Coluna("url_print", obrigatoria=False),
        Coluna("data_coleta", tipo="data"),
        # Implementa a §2.4: regra de fallback de fonte.
        Coluna(
            "tipo_fonte",
            enum=("loja_oficial_ml", "ecommerce_montadora", "indisponivel"),
        ),
        Coluna("tipo_par", enum=("par_nativo", "par_composto", "unitario")),
        Coluna("grupo_par_id", obrigatoria=False),
        # Conferencia manual da regra de captura (plano §2.6, §5.2).
        Coluna("print_sem_banner_conferido", tipo="booleano"),
        Coluna("selo_oficial_conferido", tipo="booleano"),
        Coluna("coletado_por", obrigatoria=False),
    ),
)

# --- Aba `catalogo_refil` — NOVA. O plano nao a tem -----------------------
CATALOGO_REFIL = Aba(
    "catalogo_refil",
    (
        Coluna("sku"),
        Coluna("categoria", enum=("dianteiro", "traseiro")),
        # dianteiro = par, traseiro = unitario (plano decisao B)
        Coluna("unidade", enum=("par", "unitario")),
        Coluna("medida_min_mm", tipo="inteiro"),
        Coluna("medida_max_mm", tipo="inteiro"),
        Coluna("cobertura_pct", tipo="decimal", obrigatoria=False),
    ),
)

ABAS: tuple[Aba, ...] = (MODELOS, APLICACAO, PRECOS_ORIGINAIS, CATALOGO_REFIL)


# --- Campos que NUNCA podem aparecer no snapshot --------------------------
#
# S11 e S12. O snapshot e PUBLICO: a tabela de preco da Suicatech nao vive
# nele, e dados de reuniao nao saem da sessao.
CAMPOS_DE_SESSAO_PROIBIDOS: tuple[str, ...] = (
    "preco_dianteiro",
    "custo_dianteiro",
    "preco_traseiro",
    "custo_traseiro",
    "preco_venda_refil",
    "custo_aquisicao_refil",
    "palhetas_originais_mes",
    "custo_original",
    "substituicao",
    "comissao_por_unidade",
    "aliquota",
    "cashback_total_mensal",
    "nome_cliente",
    "preco_balcao_concessionaria",
)

CAMPOS_DE_CUSTO_PROIBIDOS: tuple[str, ...] = (
    "custo",
    "custo_aquisicao",
    "preco_suicatech",
    "preco_venda_suicatech",
    "tabela_preco",
    "margem_concessionaria",
    "cashback_custo",
)


def aba_por_nome(nome: str) -> Aba | None:
    for aba in ABAS:
        if aba.nome == nome:
            return aba
    return None

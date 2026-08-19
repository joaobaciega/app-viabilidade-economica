"""§5.13 — Regra de unidade: dianteiro e PAR, traseiro e UNITARIO.

"Este e o furo mais facil de introduzir e o mais caro de descobrir tarde, e o
gerente de pecas e justamente quem encontra primeiro."

O par dianteiro tem DUAS MEDIDAS DIFERENTES (motorista e passageiro). O
traseiro e lamina unica. Decisao B do plano: dianteiro = par, traseiro =
unitario, e as duas formas COEXISTEM na mesma tela e no mesmo catalogo.

REGRAS — a primeira e critica:
  - E PROIBIDO derivar o preco ou o custo do traseiro a partir do dianteiro por
    QUALQUER FATOR, INCLUSIVE / 2. Nao e arredondamento, e ERRO DE FATO.
    Verificacao: nenhuma expressao no codigo relaciona preco_traseiro a
    preco_dianteiro. testes/test_checklist.py varre todo o src/ por AST
  - todo campo de preco e custo carrega a unidade no rotulo:
    `por par (dianteiro)`, `por unidade (traseiro)`
  - se o preco ou o custo do traseiro estiver vazio, O TRASEIRO CONTRIBUI COM
    R$ 0 e a faixa de premissas declara `traseiro: preco nao informado — fora
    da conta`. NUNCA estimado, NUNCA inferido
  - a unidade de cada categoria e ATRIBUTO DECLARADO em parametros.py, nao
    constante global e nao inferida do nome. V3 aborta o app se faltar

Este modulo nao renderiza nada: ele expoe a regra como funcao consultavel, para
que a proibicao seja testavel e para que nenhum outro modulo precise reimplementar
a leitura da unidade.
"""

from __future__ import annotations

from src import parametros as P


def rotulo_unidade(categoria_nome: str) -> str:
    """'por par (dianteiro)' — lido do atributo declarado, nunca inferido."""
    categoria = P.categoria_por_nome(categoria_nome)
    if categoria is None:  # pragma: no cover — V3 ja teria abortado
        return ""
    return categoria.rotulo_unidade


def unidade(categoria_nome: str) -> str:
    """'par' | 'unitario' — o enum declarado (V3)."""
    categoria = P.categoria_por_nome(categoria_nome)
    if categoria is None:  # pragma: no cover
        return ""
    return categoria.unidade


def unidades_sao_comparaveis(categoria_a: str, categoria_b: str) -> bool:
    """Duas categorias so sao comparaveis se a unidade for a MESMA.

    Usado pela Tela 3. plano §2.7: "o app BLOQUEIA a comparacao quando as
    unidades divergem EM VEZ DE CONVERTER". Se um lado for par e o outro
    unidade, o resultado erra por 2x na tela cuja unica funcao e ser auditavel.

    Nao existe, e nunca deve existir, uma funcao `converter_par_para_unidade`
    neste projeto.
    """
    return unidade(categoria_a) == unidade(categoria_b)


TEXTO_TRASEIRO_FORA_DA_CONTA = "traseiro: preço não informado — fora da conta"

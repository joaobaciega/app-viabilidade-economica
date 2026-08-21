"""Tela 2 — Carros mais vendidos por marca.

O DESIGN v5 nao especifica esta tela (a §6 dele cobre so a Tela 1). A estrutura
segue o plano §4, e e PROVISORIA ate o DESIGN ser regerado.

REGRA DA TELA, pedida pelo cliente e implementada pelo `index=None` do seletor:
o menu suspenso de marca vem ANTES de qualquer veiculo, e em nenhum momento a
tela mostra o catalogo inteiro. Sem marca escolhida nao ha um unico modelo na
tela; escolhida uma marca, so os modelos dela aparecem. Isso nao e enfeite: a
conversa e com o gerente de UMA concessionaria, e uma lista de 80 modelos de 18
marcas na frente dele nao e informacao, e ruido.

Plano §4.2: rodape com fonte, periodo e link para o PDF PUBLICO da Fenabrave.
NUNCA para area logada — a secao "Mais Vendidos" do portal exige login, os
informes em PDF nao. Um link que pede senha na frente do cliente e a
auditabilidade se autodestruindo.

Plano §7 Fase 2: o app mostra APENAS marcas com dados. Sem registros, exibe o
estado vazio — nunca uma marca listada pela metade.

NOTA SOBRE AS CLASSES DE CSS USADAS AQUI: esta tela vive sobre fundo BRANCO, e
por isso usa `.st-kpi-valor`, `.st-kpi-rotulo`, `.st-legenda-bloco`, `.st-chip`,
`.st-derivado` e `.st-premissas`. NAO use `.st-mensal`, `.st-anual`,
`.st-traducao` nem `.st-falta-ancora`: todas sao `color: var(--tinta-clara)` e
so funcionam dentro do cartao escuro `.st-key-resultado` — sobre branco elas
somem. O proprio css.py registra esse defeito na §9, quando ele aconteceu com o
cartao de resultado.
"""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from src import formato
from src.componentes import faixa_vendedor
from src.dados.carregar_emplacamentos import Base, Marca, Modelo, carregar
from src.icones import svg

SEM_NUMERO = "não publicado"
CHAVE_MARCA = "tela2_marca"


def renderizar() -> None:
    """Desenha a tela inteira, inclusive a propria faixa do vendedor."""
    base = carregar()

    _titulo(base)

    if not base.nomes_de_marca:
        _estado_vazio(base)
        faixa_vendedor.faixa([], meta=[base.rotulo_versao()])
        return

    # Marca que saiu da base entre uma publicacao e outra: o Streamlit levanta
    # se a chave guardar um valor fora das opcoes. Zerar ANTES de instanciar o
    # widget e a direcao segura (§5.3 proibe escrever a chave DEPOIS), e
    # atribuir e nao apagar, como em estado.novo_cliente().
    if st.session_state.get(CHAVE_MARCA) not in (None, *base.nomes_de_marca):
        st.session_state[CHAVE_MARCA] = None

    # `index=None` E O REQUISITO: o seletor abre VAZIO. Com o padrao do
    # Streamlit (index=0) a tela escolheria uma marca sozinha e ja mostraria
    # veiculos antes de alguem pedir.
    coluna_seletor, _ = st.columns([4, 8], gap="large")
    with coluna_seletor:
        escolhida = st.selectbox(
            "Marca",
            base.nomes_de_marca,
            index=None,
            placeholder="Escolha a marca…",
            key=CHAVE_MARCA,
        )

    marca = base.marcas.get(escolhida) if escolhida else None

    if marca is None:
        _convite(base)
    else:
        _ranking(base, marca)
        _tabela(base, marca)

    _procedencia(base, marca)
    faixa_vendedor.faixa([], meta=[base.rotulo_versao()])


# ---------------------------------------------------------------------------
# Blocos
# ---------------------------------------------------------------------------


def _titulo(base: Base) -> None:
    nota = ""
    if base.nomes_de_marca:
        nota = (
            f"{len(base.nomes_de_marca)} marcas · "
            f"{base.total_de_modelos} modelos · {base.janela('atual')}"
        )
    st.markdown(
        f'<div class="st-secao">{svg("veiculos")}'
        f"<span>Carros mais vendidos por marca</span>"
        f'<span class="st-secao-nota">{html.escape(nota)}</span></div>',
        unsafe_allow_html=True,
    )


def _convite(base: Base) -> None:
    """O estado antes da escolha. So NOMES DE MARCA — nenhum modelo."""
    with st.container(border=True):
        st.markdown(
            '<p class="st-kpi-valor">Escolha a marca da concessionária.</p>'
            '<p class="st-legenda-bloco">Só os modelos dessa marca aparecem — '
            "a lista completa do mercado não entra na tela. Os números são "
            f"emplacamentos da base Fenabrave em {html.escape(base.janela('atual'))}"
            f", com {html.escape(base.janela('fechado'))} ao lado para "
            "comparação.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="st-legenda-bloco">'
            + "".join(
                f'<span class="st-chip">{html.escape(nome)}</span>'
                for nome in base.nomes_de_marca
            )
            + "</p>",
            unsafe_allow_html=True,
        )


def _ranking(base: Base, marca: Marca) -> None:
    """A lista da marca escolhida, uma linha por modelo."""
    with st.container(border=True):
        cabecalho = st.columns([6, 3, 5], gap="medium")
        for coluna, texto in zip(
            cabecalho,
            (
                f"{marca.nome} · {len(marca.modelos)} modelos",
                base.janela("atual"),
                f"comparação · {base.janela('fechado')}",
            ),
        ):
            with coluna:
                st.markdown(
                    f'<span class="st-kpi-rotulo">{html.escape(texto)}</span>',
                    unsafe_allow_html=True,
                )

        for modelo in marca.modelos:
            _linha(base, modelo)

        st.divider()
        st.markdown(_total(base, marca), unsafe_allow_html=True)


def _linha(base: Base, modelo: Modelo) -> None:
    """Um modelo. As tres colunas sao alinhadas ao topo pelo proprio Streamlit."""
    col_modelo, col_atual, col_contexto = st.columns([6, 3, 5], gap="medium")

    with col_modelo:
        st.markdown(
            f'<p class="st-kpi-valor">{modelo.posicao}º '
            f"{html.escape(modelo.modelo)}</p>"
            f'<p class="st-legenda-bloco">'
            f'<span class="st-chip">{html.escape(modelo.categoria)}</span></p>',
            unsafe_allow_html=True,
        )

    with col_atual:
        st.markdown(
            f'<p class="st-kpi-valor">{_unidades(modelo.atual)}</p>',
            unsafe_allow_html=True,
        )

    with col_contexto:
        linhas = []
        if modelo.variacao is not None:
            linhas.append(
                f"{_variacao(modelo.variacao)} vs. {base.janela('anterior')}"
            )
        else:
            linhas.append(f"sem comparação com {base.janela('anterior')}")
        linhas.append(f"{_unidades(modelo.fechado)} no {base.janela('fechado')}")
        st.markdown(
            "".join(
                f'<p class="st-legenda-bloco">{html.escape(t)}</p>' for t in linhas
            ),
            unsafe_allow_html=True,
        )


def _total(base: Base, marca: Marca) -> str:
    """A soma da marca, sempre dizendo QUANTOS modelos entraram nela.

    Somar so o que existe e correto; exibir essa soma como se fosse o total da
    marca nao e. Por isso o numero anda com a contagem quando falta alguem.
    """
    total = len(marca.modelos)

    def _com_contagem(texto: str, entraram: int) -> str:
        """A soma nunca aparece sozinha quando falta modelo dentro dela."""
        if entraram >= total:
            return texto
        return f"{texto} ({entraram} de {total} modelos)"

    partes = [
        _com_contagem(
            f"→ {formato.inteiro(marca.total_atual)} unidades em "
            f"{base.janela('atual')}",
            marca.modelos_com_atual,
        )
    ]

    if marca.variacao is not None:
        partes.append(
            _com_contagem(
                f"{_variacao(marca.variacao)} vs. {base.janela('anterior')}",
                marca.modelos_comparaveis,
            )
        )

    if marca.modelos_com_fechado:
        partes.append(
            _com_contagem(
                f"{formato.inteiro(marca.total_fechado)} no {base.janela('fechado')}",
                marca.modelos_com_fechado,
            )
        )

    return f'<span class="st-derivado">{html.escape(" · ".join(partes))}</span>'


def _tabela(base: Base, marca: Marca) -> None:
    """A tabela gemea — os mesmos numeros, conferiveis linha a linha."""
    notas = [(m.modelo, m.nota) for m in marca.modelos if m.nota]

    # O contador entra no ROTULO do expander porque a explicacao de um numero
    # estranho nao pode ficar escondida atras de um painel fechado. O Tera com
    # +761% e o caso: sem o aviso de que existe uma observacao, o vendedor nao
    # tem como saber que a fonte explica o salto (modelo lancado em 2025).
    rotulo = "Ver os números"
    if notas:
        rotulo += (
            " e a observação da fonte"
            if len(notas) == 1
            else f" e as {len(notas)} observações da fonte"
        )

    with st.expander(rotulo, expanded=False):
        # As tres janelas viram NOME DE COLUNA, e um dicionario nao tem duas
        # chaves iguais: se a base subir sem `janelas`, os tres rotulos seriam
        # "" e duas colunas sumiriam sem aviso. O fallback garante rotulos
        # distintos mesmo com a base incompleta.
        colunas = [
            base.janela("atual") or "período atual",
            base.janela("anterior") or "período anterior",
            base.janela("fechado") or "ano fechado",
        ]

        # Convencao do projeto: o valor entra na tabela JA FORMATADO como
        # texto, para o pt-BR nao depender de configuracao do navegador.
        st.dataframe(
            pd.DataFrame(
                {
                    "#": [f"{m.posicao}º" for m in marca.modelos],
                    "Modelo": [m.modelo for m in marca.modelos],
                    "Categoria": [m.categoria for m in marca.modelos],
                    colunas[0]: [_unidades(m.atual) for m in marca.modelos],
                    colunas[1]: [_unidades(m.anterior) for m in marca.modelos],
                    "Variação": [_variacao(m.variacao) for m in marca.modelos],
                    colunas[2]: [_unidades(m.fechado) for m in marca.modelos],
                }
            ),
            hide_index=True,
            width="stretch",
        )

        for modelo, nota in notas:
            st.markdown(
                f'<p class="st-legenda-bloco"><b>{html.escape(modelo)}</b> — '
                f"{html.escape(nota)}</p>",
                unsafe_allow_html=True,
            )


def _procedencia(base: Base, marca: Marca | None) -> None:
    """Criterio, fonte, data e link do PDF publico. Aparece SEMPRE."""
    if base.indisponivel:
        return

    linhas = [
        f"<b>Critério</b> {html.escape(base.criterio)}",
        f"<b>Fonte</b> {html.escape(base.fonte)} · coletado em "
        f"{html.escape(base.data_consulta)}",
    ]
    if base.url:
        linhas.append(
            f'<a href="{html.escape(base.url, quote=True)}" target="_blank" '
            'rel="noopener">abrir o PDF público da fonte</a>'
        )
    if marca is not None and marca.cobertura:
        linhas.append(
            f"<b>Cobertura de {html.escape(marca.nome)} na fonte</b> "
            f"{html.escape(marca.cobertura)}"
        )

    st.markdown(
        '<div class="st-premissas">' + "<br>".join(linhas) + "</div>",
        unsafe_allow_html=True,
    )


def _estado_vazio(base: Base) -> None:
    """Sem base publicada. Nunca tela branca, nunca conteudo pela metade."""
    with st.container(border=True):
        st.markdown(
            '<p class="st-kpi-valor">Nenhuma marca publicada ainda.</p>'
            '<p class="st-legenda-bloco">Esta tela existe para dar credibilidade '
            "antes da comparação de preço, e por isso não exibe número sem fonte "
            "e data. Enquanto a base não for publicada, nenhuma marca aparece no "
            "seletor.</p>"
            '<p class="st-legenda-bloco">Publicação: '
            "<code>python -m pipeline.gerar_emplacamentos</code> lê a planilha "
            "da curadoria e grava <code>dados/emplacamentos.json</code>.</p>",
            unsafe_allow_html=True,
        )
    if base.indisponivel:
        st.caption(f"Estado da base: {base.indisponivel}.")


# ---------------------------------------------------------------------------
# Formatacao
# ---------------------------------------------------------------------------


def _unidades(valor: int | None) -> str:
    """Numero de emplacamentos, ou a ausencia dele por extenso.

    Celula vazia na base significa numero NAO ENCONTRADO na fonte, e a base
    declara que nada foi estimado. Zero seria uma afirmacao que a fonte nao faz,
    e um travessao pareceria defeito de layout.
    """
    return SEM_NUMERO if valor is None else formato.inteiro(valor)


def _variacao(fracao: float | None) -> str:
    """0.2957 -> '+30%'; -0.0639 -> '−6%'. Sinal sempre, cor nunca.

    O menos e o U+2212 de `formato.MENOS`, em tinta primaria: §3.1.2 reserva o
    vermelho para a marca, e queda de emplacamento nao e alarme.
    """
    if fracao is None:
        return SEM_NUMERO
    if fracao < 0:
        return f"{formato.MENOS}{formato.percentual(abs(fracao))}"
    return f"+{formato.percentual(fracao)}"

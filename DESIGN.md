# DESIGN.md — Tela 1: Simulador de viabilidade

**Fonte única de verdade de UX/UI para a construção da Tela 1.** Onde este documento e o gosto de quem constrói divergirem, este documento vence.

| | |
|---|---|
| **Escopo** | Tela 1 — Simulador de viabilidade (Fase 1 do plano). Telas 2 e 3 fora deste documento |
| **Derivado de** | `projeto/plano-app-viabilidade.md`, versão 5.0 de 07/08/2026 |
| **Stack** | Python + Streamlit, deploy no Streamlit Community Cloud (§6.1 do plano) |
| **Gerado em** | 11/08/2026 |
| **Alvo primário** | Tablet em paisagem, ~1180×820 CSS px |

Se o plano for revisado, este documento precisa ser regerado antes de qualquer código novo. Ele não repete os números do plano por acaso: repete só os que viram elemento de tela, e cada um aponta para a seção de origem.

---

## 0. Como usar este documento

1. **Leia inteiro antes de escrever a primeira linha de código.** As seções 3, 5 e 6 se contradizem se lidas isoladamente — a 6 é a que manda para a Tela 1.
2. **Os tokens da §3 são fixos.** Não são sugestão de partida. Se um valor parecer grande demais, leia a §1 antes de mudar: quase sempre o valor está calibrado para leitura a um metro, não para a sua tela a quarenta centímetros.
3. **Tudo marcado `⚠️ EM ABERTO` é bloqueio, não campo a preencher com um valor razoável.** Não escolha um número para destravar. Use o componente da §5.12 e deixe o marcador visível. Um chute fixado no código vira verdade em duas semanas.
4. **Tudo marcado `🔧 CSS INJETADO (FRÁGIL)` depende de seletor interno do Streamlit** e quebra em atualização de versão. Só implemente esses itens depois de fixar a versão no `requirements.txt` com `==`. Subir a versão é mudança que exige reteste visual de todos esses itens.
5. **Rode o checklist da §12 contra a tela pronta.** Cada item é verificável olhando a tela ou rodando um `grep`. Nenhum é opinião.
6. Onde este documento diz "nunca", é nunca. As proibições da §4 e da §6.1.9 têm custo comercial, não estético.

---

## 1. Contexto de uso

Reconstrua a cena antes de decidir qualquer coisa, porque é dela que sai tudo que vem depois:

Um vendedor da Suicatech, em pé num balcão de peças ou sentado numa sala de reunião de concessionária, segura um tablet em paisagem **inclinado na direção do gerente de pós-venda**, que está do outro lado da mesa. A distância de leitura do cliente é de **aproximadamente um metro, em ângulo** — o que reduz o contraste percebido. A luz é de showroom: forte, às vezes sol direto no vidro. O ambiente tem telefone tocando e gente interrompendo. A conversa dura **minutos**. O wi-fi da concessionária é ruim.

Quatro consequências que atravessam o documento inteiro:

- **A escala tipográfica é reprogramada.** O que seria corpo de texto vira legenda; o que seria título vira corpo. Um caractere de 44px a um metro subtende o mesmo ângulo que 17,6px a quarenta centímetros. É por isso que os números de resultado são enormes: não é ênfase, é geometria.
- **O app não é aprendido.** Não há onboarding, não há usuário recorrente do lado do cliente. Ou a tela se explica no primeiro segundo, ou não serve.
- **Existe informação na tela que custa dinheiro se aparecer na hora errada.** O custo de aquisição da concessionária é o preço de venda da Suicatech, e o app tem link aberto sem login.
- **O objetivo da tela é o cliente pegar o tablet.** Cliente que mexe nos números dele está comprando. Todo o desenho da §6.1 é organizado em torno desse momento.

**A rede é dependência absoluta.** Streamlit renderiza no servidor; o navegador só mantém um websocket. Sem conexão não existe app degradado — existe tela morta. Este documento **não promete nenhum comportamento offline**, e nenhuma seção dele deve ser lida como se prometesse. O que o design controla está na §7.

---

## 2. Princípios inegociáveis

Cada princípio abaixo tem consequência verificável na tela. Um princípio sem consequência não estaria aqui.

| # | Princípio | Consequência verificável |
|---|---|---|
| P1 | **Leitura a um metro, não a quarenta centímetros** | Tradução em escala humana ≥ 48px; valor anual ≥ 36px; nada que o cliente precise ler abaixo de 22px (§3.2) |
| P2 | **A tradução manda sobre o número grande** | `font-size` da tradução ≥ 1,25 × `font-size` do valor anual, e a chamada que renderiza a tradução vem **antes** no script (§6.1.5) |
| P3 | **Campo sensível abre vazio** | Preço e custo com `value=None`. Nenhum default, nenhum valor de demonstração sem rótulo (§5.2) |
| P4 | **Os presets são o protagonista; o slider é ajuste fino** | Três botões ≥ 96px de altura, acima do bloco de resultado; slider abaixo deles, altura de controle menor, rotulado "ajuste fino" (§5.3, §5.4) |
| P5 | **Todo número declara de onde veio** | Faixa de premissas sempre visível distinguindo catálogo, digitado, calculado e derivado (§5.7) |
| P6 | **Rótulo ambíguo é defeito** | Todo campo multiplicável carrega a unidade no rótulo e mostra o total derivado abaixo (§5.1) |
| P7 | **Par nunca é unitário × 2** | Dianteiro (par) e traseiro (unitário) têm preço e custo próprios. É proibido derivar um do outro por qualquer fator (§5.13) |
| P8 | **A tela discorda sem constranger** | Todo aviso vive na faixa do vendedor, 12px, cinza `#898781`, sem caixa. `st.warning` e `st.error` são proibidos na área visível ao cliente (§5.9) |
| P9 | **O resultado é ancorado** | Sem a margem atual do cliente, o valor anual não é exibido. Não existe default R$ 0 (§6.1.6, estado E1) |
| P10 | **Instrumento, não peça de marketing** | Sem ícone decorativo, sem emoji, sem `st.balloons`, sem gradiente. Vermelho só como acento de marca, nunca como alerta (§3.1) |
| P11 | **Peso mínimo por interação** | Nenhuma leitura de planilha na Tela 1. Nenhum recálculo que não seja disparado por toque explícito (§7.3) |
| P12 | **Nunca "lucro"** | `grep -ri "lucro" src/` retorna vazio (§4) |

---

## 3. Design tokens

Organizados em **três camadas conforme o que a stack suporta**. A separação não é burocracia: ela diz o que é seguro e o que precisa de reteste quando a versão do Streamlit subir.

### Camada A — Tema nativo (`.streamlit/config.toml`)

Estável, não quebra em atualização de versão. **Tudo que couber aqui fica aqui.**

```toml
[theme]
primaryColor = "#C8102E"            # ⚠️ SUBSTITUIR — ver §3.1.1
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#0B0B0B"
font = "sans serif"

[server]
headless = true
```

O que o tema nativo cobre neste app, e portanto **não precisa de CSS**: a cor de acento dos botões `type="primary"`, do slider e do foco; o fundo branco dominante; o fundo cinza dos contêineres com borda; a cor do texto; a família tipográfica.

**Ganho de resiliência que isso compra:** o estado ativo dos três botões de cenário é feito com `type="primary"` / `type="secondary"` — nativo. Se todo o CSS injetado quebrar numa atualização, os botões continuam funcionando e continuam mostrando qual cenário está ativo. Só o tamanho degrada. Isso é deliberado: o protagonista da tela não pode depender da camada frágil.

### Camada B — CSS injetado 🔧 FRÁGIL

Via `st.markdown("<style>…</style>", unsafe_allow_html=True)`. Depende de classes e estruturas internas do Streamlit e **muda entre versões**.

Obrigações que acompanham esta camada:

- `requirements.txt` fixa a versão com `==` (ex.: `streamlit==1.40.1`), nunca `>=` nem faixa
- Todo item desta camada está marcado `🔧` neste documento
- Subida de versão do Streamlit = reteste visual de todos os itens `🔧` antes de subir para produção

Itens desta camada na Tela 1: escala tipográfica de resultado, altura dos botões de cenário, altura e alvo do slider, ocultação da marca do framework, faixa do vendedor, neutralização do aviso nativo de desconexão, espaçamento vertical entre blocos.

### Camada C — Não especificável (não tente)

Registrado aqui para ninguém perder tempo:

| O que | Por quê |
|---|---|
| Animação contínua durante o arraste do slider | O `st.slider` só dispara ao soltar; não existe evento durante o arraste |
| Recálculo sem ida ao servidor | A lógica roda no servidor; toda interação é um round-trip |
| **Qualquer funcionamento sem rede** | Não há o que cachear — a conta não acontece no aparelho |
| Hover / tooltip como canal de leitura | Não existe hover em tablet. O canal de reserva é a tabela (§5.11) |
| Controle de foco e teclado ao nível de app nativo | Fora do alcance do framework |
| Layout livre por coordenada | O fluxo é vertical, organizado por `st.columns` e contêineres |
| Estilizar a tela de hibernação do Community Cloud | É tela do provedor, servida antes do app subir. Vira requisito de operação (§7.1) |

### 3.1 Cor

Superfície branca dominante, texto preto, **vermelho como acento em 5–10%** (§8, decisão 7 do plano — o plano registra divergência com a proporção 60/30/10 sugerida pelo cliente, e este documento segue a recomendação de 5–10%).

| Token | Valor | Contraste sobre `#FFFFFF` | Uso |
|---|---|---|---|
| `--superficie` | `#FFFFFF` | — | Fundo da página |
| `--superficie-2` | `#F5F5F5` | — | Fundo de contêiner com borda, faixa de premissas |
| `--tinta-primaria` | `#0B0B0B` | 19,68:1 | Todo número de resultado, todo rótulo de campo |
| `--tinta-secundaria` | `#52514E` | 7,94:1 | Rótulos de eixo do gráfico, totais derivados, legendas do bloco de resultado |
| `--tinta-discreta` | `#898781` | 3,59:1 | **Exclusivo da faixa do vendedor.** O contraste baixo é o mecanismo, não um descuido (§5.9) |
| `--traco` | `#C3C2B7` | 1,79:1 | Borda de contêiner, linha de base do gráfico, marcas de preset no eixo |
| `--grade` | `#E1E0D9` | 1,32:1 | Linhas de grade horizontais do gráfico, hairline 1px sólida |
| `--marca-vermelho` | `#C8102E` ⚠️ SUBSTITUIR | 5,88:1 | Botão de cenário ativo, marcador de posição no gráfico. **Nada mais** |

#### 3.1.1 O vermelho é placeholder — e há uma armadilha medida

A identidade da Suiça Tech / Intrace AG está definida em espécie (bandeira vermelha, tipografia preta sobre branco), **mas o hexadecimal oficial não está no plano**. O valor acima é placeholder.

Ao substituir, o vermelho oficial precisa passar em três medidas:

| Medida | Mínimo | Por quê |
|---|---|---|
| Contraste sobre `#FFFFFF` | ≥ 4,5:1 | Leitura em ângulo sob luz forte |
| Contraste sobre `#F5F5F5` | ≥ 4,5:1 | O botão inativo vive sobre o cinza secundário |
| Branco sobre o vermelho | ≥ 4,5:1 | Rótulo do botão de cenário ativo é branco sobre vermelho |

**Armadilha medida:** o vermelho de bandeira suíça puro `#FF0000` mede **4,00:1** sobre branco — reprova nas três. `#E30613` mede 4,88:1 e passa raspando. O placeholder `#C8102E` mede 5,88:1 sobre branco, 5,40:1 sobre `#F5F5F5` e 5,88:1 para branco sobre ele.

Se o vermelho oficial da marca for `#FF0000` ou equivalente, a regra é: **ele fica no logo, e a interface usa um passo escurecido da mesma matiz.** Logo e acento de interface não precisam ser o mesmo hexadecimal; contraste de leitura a um metro não é negociável.

#### 3.1.2 Vermelho é marca, portanto vermelho não é alerta

O vermelho está gasto como acento de marca. Consequência dura, e ela resolve dois problemas de uma vez:

> **É proibido usar vermelho, amarelo ou qualquer cor semântica de alerta na área visível ao cliente.** Não existe token `--erro`, `--atencao` ou `--critico` neste design. Toda discordância da tela com o usuário é comunicada por **texto cinza discreto na faixa do vendedor** (§5.9).

Isso mata `st.error`, `st.warning`, `st.exception` e `st.toast` na área visível, e mata a tentação de pintar um resultado negativo de vermelho. Um resultado negativo é preto, como todos os outros números — o que muda é a frase na faixa do vendedor.

#### 3.1.3 Independência de cor

Nenhum estado é comunicado só por matiz. O botão de cenário ativo é vermelho **e** tem peso de fonte maior **e** o valor escolhido aparece por extenso na faixa de premissas. O marcador do gráfico é vermelho **e** é o único ponto marcado **e** carrega rótulo direto com o valor.

### 3.2 Tipografia

Família: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` (o `font = "sans serif"` do tema resolve; sem fonte de display, sem serifa — serifa aqui lê como material publicitário).

**A escala é organizada por quem lê e a que distância.** Este é o token mais fácil de "corrigir" por engano, então a justificativa vem junto:

| Token | px | Peso | Entrelinha | Quem lê | Onde |
|---|---|---|---|---|---|
| `t-traducao` | **48** | 700 | 1,15 | Cliente, a 1 m | A tradução em escala humana. O maior elemento da tela 🔧 |
| `t-anual` | **36** | 600 | 1,20 | Cliente, a 1 m | O valor anual 🔧 |
| `t-preset-valor` | 32 | 700 | 1,10 | Cliente, a 1 m | O "30%" dentro do botão de cenário 🔧 |
| `t-mensal` | 22 | 500 | 1,30 | Cliente, a 1 m | Valor mensal, no bloco de resultado 🔧 |
| `t-preset-nome` | 22 | 700 | 1,20 | Cliente, a 1 m | "REALISTA" dentro do botão 🔧 |
| `t-rotulo` | 17 | 600 | 1,35 | Vendedor, a 40 cm | Rótulo de campo de entrada |
| `t-campo` | 20 | 400 | 1,40 | Vendedor, a 40 cm | Texto dentro do `number_input` 🔧 |
| `t-derivado` | 15 | 500 | 1,35 | Vendedor, a 40 cm | Total derivado sob o campo (`st.caption`) |
| `t-premissas` | 15 | 400 | 1,45 | Ambos | Faixa de premissas |
| `t-vendedor` | **12** | 400 | 1,40 | **Só o vendedor** | Faixa do vendedor. Ilegível a 1 m — é para isso que serve 🔧 |

**Por que a escala tem esse passo, e por que não reduzir.** Tamanho angular é proporcional a tamanho ÷ distância. Um caractere de 16px lido a 40 cm equivale a 40px lido a 1 m. Logo:

- `t-traducao` a 48px ≈ 19px de leitura normal para o cliente — confortável
- `t-anual` a 36px ≈ 14px — legível porque é uma cadeia curta em peso 600
- `t-vendedor` a 12px ≈ **4,8px** para o cliente — abaixo do limiar de leitura. É o mecanismo do canal privado, não um descuido

Quem achar a escala exagerada está olhando de quarenta centímetros. Ela não é para essa distância.

**Duas regras de checagem automática:**

- `t-traducao` ≥ 1,25 × `t-anual` (48 / 36 = 1,33 ✓). Inverter é o erro de implementação mais provável desta tela
- Nenhum texto que o cliente precise ler fica abaixo de 22px

**Figuras numéricas:** proporcionais nos números grandes (`t-traducao`, `t-anual`, `t-preset-valor`, `t-mensal`) — `tabular-nums` a 48px deixa `141` visivelmente frouxo. `tabular-nums` só nos ticks do eixo do gráfico e na tabela da §5.11.

### 3.3 Espaçamento e grid

Escala base 4px: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`.

| Token | Valor | Uso |
|---|---|---|
| `sp-campo` | 16px | Entre campos de entrada dentro de um bloco |
| `sp-bloco` | 32px | Entre blocos nomeados 🔧 |
| `sp-secao` | 48px | Entre a coluna de entrada e o bloco de resultado 🔧 |
| `pad-container` | 24px | Interno de `st.container(border=True)` 🔧 |
| `pad-pagina` | 32px lateral | Margem da página 🔧 |

**Grid.** `st.set_page_config(layout="wide")`. No alvo primário (tablet paisagem), duas colunas via `st.columns([5, 7], gap="large")`:

- **Coluna esquerda (5/12)** — entradas. É o lado do vendedor
- **Coluna direita (7/12)** — cenário e resultado. É o lado que o cliente lê

A coluna do resultado é a maior porque é a que precisa dos 48px. Dentro dela, `st.columns(3)` para os botões de cenário — um nível de aninhamento, que o Streamlit suporta no corpo principal.

Largura máxima de conteúdo: nenhuma. `layout="wide"` já entrega o comportamento correto no tablet; no desktop a tela fica larga, e isso é aceitável porque desktop é portabilidade (§8).

### 3.4 Alvos de toque

**Mínimo global: 56px** — acima dos 44px habituais, deliberadamente. O dedo pode ser de um gerente de cinquenta e poucos anos que não usa tablet todo dia, num aparelho inclinado que ele está segurando com a outra mão.

| Elemento | Alvo | Nota |
|---|---|---|
| Botão de cenário | **96px de altura**, largura total da coluna (≈ 200px cada) | O maior alvo da tela. É o protagonista 🔧 |
| `number_input` | 56px de altura | 🔧 |
| Polegar do slider | ≥ 32px de diâmetro, faixa de acerto ≥ 48px de altura | 🔧 |
| Cabeçalho de `st.expander` | 56px de altura | 🔧 |
| Espaço entre alvos adjacentes | ≥ 12px | Evita toque errado no tablet inclinado |

**Se o CSS do slider quebrar**, o polegar volta ao tamanho padrão do Streamlit — pequeno, mas ainda operável. Isso é tolerável **porque o slider é secundário**. Se o protagonista dependesse dessa camada, não seria.

### 3.5 Superfície

Sóbrio. A referência mental é painel de instrumentos ou relatório financeiro bem feito, não landing page.

| Token | Valor |
|---|---|
| `raio` | 4px — em tudo. Nada arredondado demais 🔧 |
| `traco-container` | 1px sólido `--traco` |
| `elevacao` | **Nenhuma.** Sem sombra, sem gradiente, sem brilho |
| Bloco de resultado | `st.container(border=True)`, fundo `--superficie` (branco), borda 1px `--traco` |
| Faixa de premissas | fundo `--superficie-2`, sem borda, `pad` 12px 16px |

Sombra é a primeira coisa que faz uma tela parecer material publicitário. Não há nenhuma neste design.

### 3.6 Movimento

| Token | Valor |
|---|---|
| `dur-transicao` | 120ms |
| `curva` | `ease-out` |
| Onde é permitido | Estado de pressionado dos botões e do slider. Mais nada |

**O recálculo não é animado.** Ele acontece no servidor; a tela nova simplesmente aparece. Não tente mascarar a latência com transição — isso soma tempo percebido ao tempo real.

`@media (prefers-reduced-motion: reduce)` zera `dur-transicao`. 🔧

---

## 4. Vocabulário

Tratado com o mesmo rigor de um token de cor. Rótulo errado aqui tem custo comercial.

### Obrigatórios

| Termo | Onde | Por quê |
|---|---|---|
| **Margem de contribuição** | Rótulo de todo resultado financeiro | O cálculo para em preço − custo do produto. É o que a conta é |
| **Aproveitamento** | Rótulo da taxa de conversão | É a métrica nativa do gerente de pós-venda (§8, decisão 8 do plano). Falar a língua dele é meio caminho |
| **Passagens** | Rótulo do volume de veículos | Termo de oficina. "Fluxo" e "carros" são vagos |
| **por ponto de venda** / **no total** | Sufixo obrigatório de todo campo multiplicável | §1.3 do plano: a leitura errada erra por 10× |
| **par** / **unidade** | Sufixo obrigatório de todo preço e custo | §2.7 do plano: dianteiro é par, traseiro é unitário |
| **Refil** | O produto da Suicatech | Refil é a borracha; palheta é o conjunto. Confundir os dois na tela cujo objetivo é ser conferível é caro |
| **estimativa** / **derivado** | Obrigatório nos presets do traseiro pessimista e otimista | São derivação por proporção, não medição (§3.2 do plano) |

### Permitidos, com restrição

| Termo | Restrição |
|---|---|
| **Faturamento** | Só em linha secundária. **Nunca** como manchete — o resultado é lido em margem (§3.3 do plano) |
| **Cashback** | Permitido. Mas ver §6.1.7: ele **não desconta** da margem exibida |
| **Estimativa** | **Proibido** nos presets do dianteiro (são carteira real de 15+ concessionárias) e **obrigatório** nos extremos do traseiro. A mesma palavra, dois destinos opostos |

### Proibidos

| Termo | Por quê |
|---|---|
| **Lucro**, **lucratividade**, **lucro líquido** | O cálculo é margem de contribuição. "Lucro" convida a correção do financeiro que derruba a credibilidade de tudo que veio antes. `grep -ri "lucro" src/` retorna vazio |
| **ROI**, **retorno garantido**, **garantia de retorno** | Promessa que o app não pode sustentar |
| **Economia** | É vocabulário da Tela 3 (comparação com a original). Na Tela 1 não há com o que economizar |
| **Grátis**, **de graça** | Tom de marketing |
| **Erro**, **inválido**, **atenção**, **cuidado** | Vocabulário de alerta. A faixa do vendedor descreve o que observar, não acusa (§5.9) |

### Padrão de rótulo de campo multiplicável

```
<Grandeza>, <unidade explícita>
→ <total derivado> <unidade do total>
```

Exemplo: rótulo `Passagens por mês, por ponto de venda`; abaixo, `→ 3.000 passagens por mês no total`. Sem o total derivado, o campo está incompleto.

---

## 5. Inventário de componentes

Componentes das Telas 2 e 3 (cartão de preço com print e link, selo de coleta, marcador de dado vencido, par composto de dois anúncios, comparação bloqueada entre original e refil) **não estão aqui**, porque a Tela 1 não depende de nenhum dado externo — é a única tela que não depende (§0 do plano). A regra do par, porém, aparece na Tela 1 em outra forma, e está na §5.13.

### 5.1 Campo numérico com unidade e total derivado

**Propósito.** Coletar um número que participa de multiplicação sem deixar a leitura ambígua.

**Anatomia.**
```
Passagens por mês, por ponto de venda        ← t-rotulo, 17px/600
┌──────────────────────────────────┐
│ 300                              │         ← st.number_input, 56px, t-campo
└──────────────────────────────────┘
→ 3.000 passagens por mês no total           ← t-derivado, 15px, --tinta-secundaria
```

**Implementação.** `st.number_input(label=…, value=None, min_value=…, step=…)` + `st.caption(…)` para o derivado.

**Estados.**

| Estado | Aparência |
|---|---|
| Vazio | Campo em branco. O derivado **não aparece** — não existe total de nada |
| Preenchido | Derivado presente, sempre |
| Foco | Contorno `--marca-vermelho` (nativo, via `primaryColor`) |
| Inválido | Não existe estado inválido visível. O `min_value` impede a entrada; nada pisca vermelho |

**Regras.**
- O rótulo carrega a unidade **sempre**, mesmo quando parece óbvio. "Pontos de venda" não precisa; "Passagens por mês" precisa
- O total derivado é recalculado a cada rerun, sem custo — a conta é local
- Quando o multiplicador vale 1 (um ponto de venda), o derivado **continua aparecendo**. Sumir com ele quando o valor é trivial ensina o cliente a não procurá-lo quando deixa de ser

### 5.2 Campo sensível não preenchido (preço e custo)

**Propósito.** O custo de aquisição da concessionária é o preço de venda da Suicatech. Numa tela de link aberto, um default é tabela de preço exposta (§6.3 do plano).

**Anatomia.** Idêntica à §5.1, mais uma legenda fixa **sob o bloco inteiro de preço e custo**, não sob cada campo:

```
Preço ao consumidor final, por par (dianteiro)
┌──────────────────────────────────┐
│                                  │        ← vazio, sempre
└──────────────────────────────────┘

Custo de aquisição, por par (dianteiro)
┌──────────────────────────────────┐
│                                  │        ← vazio, sempre
└──────────────────────────────────┘
Preço e custo são negociados caso a caso.    ← t-derivado, --tinta-secundaria
Abrem em branco de propósito.
```

**Regras.**
- `value=None`. Nunca um número, nunca um `placeholder` numérico que pareça valor
- A legenda existe para o campo vazio **não parecer esquecido**. Sem ela, um vendedor novo preenche com o valor da última reunião, ou o cliente pergunta se o app está quebrado
- ⚠️ **Não implemente validação de piso de preço.** A decisão F do plano está em aberto (§10). Não invente um piso

### 5.3 Botão de cenário — o protagonista

**Propósito.** É o momento em que o cliente age. Três botões grandes, uma ida ao servidor cada, resposta decisiva, imunes à latência.

Isso substitui a ideia original de slider em tempo real, que **não é reproduzível em Streamlit** (§3.7 e §6.2 do plano). E a substituição é melhor que a original: os presets vêm de carteira real de 15+ concessionárias, e apertar "REALISTA" é invocar um dado. Arrastar até o mesmo número é só mexer num controle.

**Anatomia.**
```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PESSIMISTA  │ │   REALISTA   │ │   OTIMISTA   │   ← t-preset-nome 22/700
│     20%      │ │     30%      │ │     40%      │   ← t-preset-valor 32/700
└──────────────┘ └──────────────┘ └──────────────┘
   96px de altura, largura total da coluna, gap 12px
Aproveitamento dianteiro medido em 15+ concessionárias
da carteira Suicatech — não é estimativa                ← t-derivado
```

**Implementação.**
```python
c1, c2, c3 = st.columns(3)
c1.button("PESSIMISTA\n\n20%", type=tipo(p), use_container_width=True,
          on_click=aplicar_preset, args=("pessimista",))
```

**Estados.**

| Estado | Tratamento |
|---|---|
| Ativo | `type="primary"` — preenchido em `--marca-vermelho`, rótulo branco. **Nativo, não CSS** |
| Inativo | `type="secondary"` — fundo `--superficie-2`, borda `--traco`, rótulo `--tinta-primaria` |
| Nenhum ativo | Quando o slider foi movido para um valor que não corresponde a nenhum preset. Os três ficam `secondary`, e a faixa de premissas diz "ajustado na reunião" |

**Regras.**
- **O estado ativo é derivado, não guardado.** Um preset está ativo se e somente se `(conv_dianteiro, conv_traseiro)` for exatamente igual ao par daquele preset. Isso torna impossível a tela mostrar "REALISTA" aceso com o slider em 27%
- Cada botão escreve **os dois valores** — dianteiro e traseiro — em `st.session_state`, via `on_click`. Escrever a chave de um widget depois que ele foi instanciado levanta `StreamlitAPIException`; por isso é `on_click`, não código depois do botão
- Os três botões ficam **acima do bloco de resultado, dentro da coluna do cliente**. O controle que muda o número está imediatamente acima do número que ele muda, ao alcance de quem estiver do outro lado da mesa
- A legenda de procedência ("medido em 15+ concessionárias") é argumento comercial, não nota de rodapé. Fica em 15px, sempre visível. A palavra "estimativa" é proibida aqui (§4)

### 5.4 Slider de ajuste fino — secundário

**Propósito.** Permitir um valor que não seja um dos três presets. Nada além disso.

**Anatomia.**
```
ajuste fino ─────────────────────────────       ← t-derivado, --tinta-secundaria
0% ──────────────●──────────────────── 60%
                27%
```

**Implementação.** `st.slider("Aproveitamento dianteiro", 0, 60, key="conv_dianteiro", format="%d%%")` com rótulo colapsado e a legenda "ajuste fino" acima.

**Regras.**
- Rotulado literalmente **"ajuste fino"**. Nunca com destaque maior que os presets
- Domínio **0–60%**. Este domínio e o do gráfico da §5.11 são o mesmo valor — mudar um obriga a mudar o outro, senão o marcador sai do gráfico
- Mover o slider **não** altera o traseiro. O traseiro só muda por preset ou pelo seu próprio controle em Ajustes avançados. Acoplar os dois recriaria exatamente o risco nº 1 do plano
- Não especifique nem tente feedback durante o arraste. Ele não existe (§3, camada C)

### 5.5 Bloco de resultado

**Propósito.** É o que o cliente lê. A ordem de leitura é o requisito mais importante desta tela.

**Anatomia — a ordem é normativa:**
```
┌────────────────────────────────────────────────────┐
│                                                    │
│  3 a cada 10 carros que entram                     │  ← t-traducao 48/700
│  na oficina                                        │     PRIMEIRO
│                                                    │
│  R$ 141.480 por ano                                │  ← t-anual 36/600
│  margem de contribuição incremental                │  ← t-mensal 22/500
│                                                    │
│  R$ 11.790 por mês                                 │  ← t-mensal 22/500
│                                                    │
└────────────────────────────────────────────────────┘
```

**Regras.**
- **A tradução em escala humana vem antes do valor anual.** Em Streamlit isso é literalmente a ordem das chamadas no script. "R$ 1,2 milhão por ano" é rejeitado pelo cérebro antes de ser avaliado; "3 a cada 10 carros que entram na oficina" é verificado pela intuição em dois segundos. O anual sozinho parece promessa; precedido da meta, parece aritmética
- A tradução é **por passagem**, nunca por consultor/dia. A tradução por consultor herda a ambiguidade da §1.3 do plano e pode errar por 10×
- A tradução é maior que o anual. `t-traducao` ≥ 1,25 × `t-anual`
- **Não use `st.metric`.** A tipografia dele é própria, pouco controlável, e não chega aos 48px que a leitura a um metro exige. Use markdown com as classes da §3.2 🔧
- Resultado negativo é exibido em `--tinta-primaria` como qualquer outro número, com o sinal. Nada fica vermelho (§3.1.2)
- O rótulo diz **"margem de contribuição incremental"**. Se algum campo opcional estiver ligado, ver §6.1.7 para a regra de mudança de rótulo

### 5.6 Faixa de premissas

**Propósito.** Declarar, de forma permanentemente visível, o que a simulação está assumindo. É o que separa premissa de fato sem ninguém precisar perguntar.

**Anatomia.** Faixa horizontal em `--superficie-2`, logo abaixo do bloco de resultado, `t-premissas` 15px:

```
 dianteiro 30% ◆ carteira · traseiro 10% ◆ carteira · substituição 0% ▪ premissa
 · rampa e sazonalidade ⚠️ não aplicadas · ano cheio em regime
```

**Regras.**
- Aparece **sempre**, inclusive quando todos os valores são os default. A hipótese favorável precisa estar dita na tela, não escondida no default. Substituição em 0% significa "o refil não tira nenhuma venda da original" — é a premissa mais favorável possível, e o cliente tem que poder vê-la
- Cada item carrega o marcador de procedência da §5.7
- Quando o valor de aproveitamento não corresponde a nenhum preset, o item lê `dianteiro 27% ▪ ajustado na reunião` — a procedência muda junto com o valor
- Quando um coeficiente é placeholder, o item carrega `⚠️` e o marcador da §5.12

### 5.7 Marcador de procedência

**Propósito.** A tela mistura naturezas muito diferentes de número, e o cliente não tem como distinguir. Quando o gerente aponta um número e pergunta "de onde saiu isso?", a resposta já tem que estar na tela.

| Marcador | Natureza | O que é na Tela 1 | Como se prova |
|---|---|---|---|
| `◆ carteira` | **Catálogo** — dado próprio da Suicatech | Presets 20/30/40 do dianteiro; 10% do traseiro | Legenda: "medido em 15+ concessionárias" |
| `▪ premissa` | **Digitado** — informado na hora | Pontos de venda, passagens, preço, custo, margem atual, substituição | Nada a provar. Mas precisa ficar claro que é premissa |
| `ƒ calculado` | **Calculado** — derivado por fórmula | Total de passagens, pares/mês, margem mensal, anual, tradução | A fórmula, sob demanda (§5.8) |
| `≈ derivado` | **Calculado, subclasse** | Traseiro pessimista 7% e otimista 13% — derivação por proporção, **não medição** | Legenda: "derivado do dianteiro na mesma proporção — não medido" |
| `⬡ coletado` | **Coletado** de fonte externa | **Não ocorre na Tela 1** | — |

**Regras.**
- Os marcadores são glifos monocromáticos em `--tinta-secundaria`, **nunca cor**. Cor está gasta (§3.1.2), e o cliente lê em ângulo
- O marcador nunca é o único canal: cada um vem acompanhado da palavra ("carteira", "premissa", "calculado", "derivado")
- **A distinção `◆ carteira` × `≈ derivado` no traseiro é obrigatória e não é preciosismo.** Ela ataca o risco nº 1 do plano: se o 7% e o 13% do traseiro forem apresentados com a mesma autoridade do 30% do dianteiro, o app está vendendo derivação como medição, e o erro só aparece no mês 3 do cliente

### 5.8 Painel de fórmula

**Propósito.** Prova em um toque para todo número `ƒ calculado`.

**Implementação.** `st.expander("De onde vêm esses números")`, fechado por padrão, ao final da coluna de resultado. Dentro: cada linha de resultado com sua fórmula em texto e os valores substituídos.

```
Pares dianteiros por mês
  passagens totais × aproveitamento dianteiro
  3.000 × 30% = 900

Margem mensal do dianteiro
  pares × (preço − custo)
  900 × (R$ 197,90 − R$ 84,90) = R$ 101.700,00
```

**Regras.** Fechado por padrão — abrir custa um round-trip e ocupa a tela. Mas existe, e o vendedor sabe onde está. É a diferença entre parecer honesto e ser verificável.

### 5.9 Faixa do vendedor — o canal de aviso discreto

**Propósito.** A tela precisa poder discordar do usuário sem constranger ninguém. Se o vendedor digitar números que produzem um cenário implausível, o app avisa — mas o cliente está olhando, e um alerta vermelho transforma um ajuste técnico em vexame público.

**Anatomia.** Faixa no **rodapé** da página — a borda mais próxima de quem segura o aparelho e a mais escorçada para quem está do outro lado da mesa. `t-vendedor` 12px, `--tinta-discreta` `#898781`, sem caixa, sem borda, sem ícone, sem cor.

```
carga de 34 veículos por consultor por dia — confira se os consultores são por ponto ou no total
```

**Implementação.** `st.caption()` dentro de um contêiner no fim do script, com CSS para tamanho e cor. 🔧 Se o CSS quebrar, o texto volta ao tamanho padrão de `st.caption` — ainda discreto, ainda sem caixa, ainda cinza. Degradação aceitável.

**Regras — estas são absolutas:**
- **`st.warning`, `st.error`, `st.exception`, `st.toast` e `st.balloons` são proibidos em qualquer ponto da área visível ao cliente.** Caixa amarela ou vermelha na frente do gerente transforma um ajuste técnico em vexame público. Verificação: `grep -rn "st\.warning\|st\.error\|st\.exception\|st\.toast\|st\.balloons" src/` retorna vazio
- O texto **descreve, não acusa**. "carga de 34 veículos por consultor por dia" e não "valor inválido"
- Vários avisos simultâneos viram linhas separadas na mesma faixa, na ordem das regras da §6.1.8. Nunca um contador, nunca um badge
- A faixa **não empurra o layout** quando aparece. Ela ocupa altura reservada, vazia quando não há aviso 🔧

### 5.10 Revelação progressiva — "Ajustes avançados"

**Propósito.** Segurar o limite de seis campos editáveis visíveis. A planilha original tem ~30 células; num tablet, na frente do cliente, isso é morte.

**Implementação.** Um único `st.expander("Ajustes avançados", expanded=False)` em largura total, abaixo das duas colunas.

**Regras.**
- Fechado por padrão, **sempre**, inclusive depois de o vendedor ter aberto na simulação anterior. Ele reabre fechado a cada carga da página
- Nenhum campo dentro dele altera o resultado sem que a faixa de premissas (§5.6) reflita a mudança. Uma alteração escondida atrás de um acordeão que muda o número da manchete sem deixar rastro é a pior falha possível nesta tela
- O expander conta como **um** elemento na contagem de densidade, não como N campos

### 5.11 Gráfico de sensibilidade

**Propósito.** Recuperar parte do efeito perdido do arraste. Como o servidor calcula tudo de uma vez, a curva inteira aparece com marcador na posição atual — o cliente vê o intervalo completo **sem interagir**.

**Forma.** Série única, curva de resposta. Não é série temporal, não é categórico. Forma de ênfase: uma linha, um marcador. **Sem legenda** — série única, o título já diz o que está plotado.

**Biblioteca.** Altair via `st.altair_chart(chart, use_container_width=True)`. `st.line_chart` não dá controle de espessura, de marcador nem de regra vertical.

**Especificação de marcas** (validada — ver §5.11.1):

| Elemento | Especificação |
|---|---|
| Curva | `mark_line`, **2px**, `strokeCap="round"`, `strokeJoin="round"`, cor `--tinta-primaria` `#0B0B0B` |
| Preenchimento de área | **Nenhum.** Um wash a 10% desaparece a um metro em ângulo sob luz de showroom e não acrescenta leitura |
| Marcador da posição atual | `mark_point`, círculo **r = 8** (16px de diâmetro — acima do mínimo de 8px, por causa da distância), preenchido em `--marca-vermelho`, com anel de 2px na cor da superfície |
| Rótulo direto | **Exatamente um**, junto ao marcador, com o valor anual. `t-derivado`, `--tinta-primaria`. A menos de 80px da borda direita, o rótulo vira para o lado esquerdo do marcador |
| Marcas dos presets | Três `mark_rule` verticais em 20/30/40%, 1px **sólida** `--traco`. Nunca tracejadas |
| Linha do zero | `mark_rule` horizontal em y = 0, 1px sólida `--tinta-secundaria`, rotulada `R$ 0`. **Desenhada apenas quando o domínio de y cruza o zero** |
| Grade | Horizontal, 1px sólida `--grade`. **Sem grade vertical** — as marcas dos presets já ocupam esse canal |
| Eixos | Rótulos em `--tinta-secundaria` 15px, `tabular-nums`. Eixo Y com no máximo 4 ticks, arredondados e compactados ("R$ 140 mil") |
| Altura do contêiner | **300px** = 260px de plot + 40px de faixa de eixo. Não fixe uma altura que exclua a faixa do eixo — isso cria uma barra de rolagem interna |

**Título e subtítulo.**
```
Margem incremental anual por aproveitamento dianteiro
traseiro fixo em 10% · substituição 0% · demais premissas conforme a faixa acima
```

**Regras.**
- **Um eixo Y só.** Nunca dois. Duas grandezas de escalas diferentes viram dois gráficos, nunca dois eixos
- **O domínio de X é idêntico ao domínio do slider (0–60%)**, para que o marcador nunca saia do plot
- **A curva plota exatamente a mesma grandeza da manchete.** Se a manchete é margem incremental, a curva é incremental. Se divergirem, a tela se contradiz na frente do cliente
- Só o traseiro fica congelado; ao variar o dianteiro, o traseiro **não** acompanha. O subtítulo diz isso literalmente
- **Sem hover, sem tooltip.** Não existe hover em tablet, e o marcador é permanente, não sob demanda
- **Gêmeo em tabela, obrigatório.** `st.expander("Ver os números da curva")` com `st.dataframe` da curva de 0 a 60% em passos de 5pp. É o canal de reserva que substitui o tooltip que a stack não tem

#### 5.11.1 Validação de cor do gráfico

As três marcas que precisam ser distinguidas entre si são a curva `#0B0B0B`, o marcador `#C8102E` e as marcas de preset `#898781`. Medido com o validador, superfície `#FFFFFF`, todos os pares:

- **Separação sob daltonismo:** pior par `#898781 ↔ #C8102E`, ΔE **11,5** (deuteranopia) — acima do alvo de 8
- **Piso de visão normal:** pior par ΔE **22,4** — acima do piso de 15
- **Contraste sobre a superfície:** as três marcas ≥ 3:1

As checagens de faixa de luminosidade e piso de croma **reprovam por construção** e isso é esperado: elas validam paletas *categóricas*, e preto e cinza não são matizes de identidade. Este é um gráfico de série única com um acento — a checagem que vale é a de contraste e separação, e ela passa.

**Ao substituir o vermelho da marca (§3.1.1), refaça esta medição.**

### 5.12 Marcador de decisão em aberto

**Propósito.** Tornar visível que um valor ainda não foi decidido, em vez de deixar um chute virar verdade.

**Anatomia.** O glifo `⚠️` seguido do texto em `--tinta-secundaria`, **sem cor de alerta e sem caixa**. Na faixa de premissas: `rampa e sazonalidade ⚠️ não aplicadas`.

**Regras.**
- Um valor em aberto **nunca** é substituído por um número plausível no código. Ele vive num único módulo `parametros.py` com o valor marcado como provisório, e a tela mostra o marcador
- O marcador é discreto o bastante para não alarmar o cliente, e explícito o bastante para o vendedor saber que aquele item está pendente
- Quando a decisão for tomada, o marcador some junto com a substituição do valor em `parametros.py`. Não há outro lugar para mexer

### 5.13 Regra de unidade — dianteiro é par, traseiro é unitário

**Propósito.** Este é o furo mais fácil de introduzir e o mais caro de descobrir tarde, e o gerente de peças é justamente quem encontra primeiro.

O par dianteiro tem **duas medidas diferentes** (motorista e passageiro). O traseiro é lâmina única. Decisão B do plano: **dianteiro = par, traseiro = unitário**, e as duas formas coexistem na mesma tela e no mesmo catálogo.

**Regras — a primeira é crítica:**
- **É proibido derivar o preço ou o custo do traseiro a partir do dianteiro por qualquer fator, inclusive ÷ 2.** Não é arredondamento, é erro de fato. Verificação: nenhuma expressão no código relaciona `preco_traseiro` a `preco_dianteiro`
- Todo campo de preço e custo carrega a unidade no rótulo: `por par (dianteiro)`, `por unidade (traseiro)`
- Se o preço ou o custo do traseiro estiver vazio, **o traseiro contribui com R$ 0** e a faixa de premissas declara `traseiro: preço não informado — fora da conta`. Nunca estimado, nunca inferido
- A unidade de cada categoria é **atributo declarado** em `parametros.py`, não constante global e não inferida do nome

### 5.14 Estado de reconexão

**Propósito.** Se a conexão oscilar, o que o cliente vê não pode ser um erro vermelho no meio do pitch.

O Streamlit exibe um aviso nativo de desconexão com estilo próprio. Tratamento: 🔧 CSS que **neutraliza a cor** desse aviso (para `--tinta-discreta` sobre `--superficie-2`) e o reposiciona no rodapé, junto à faixa do vendedor.

**Regras.**
- **Não oculte o aviso completamente.** O vendedor precisa saber que caiu; ocultar troca um constrangimento por uma confusão pior
- O último resultado renderizado **permanece na tela** durante a reconexão. Nada é limpo, nada vira esqueleto de carregamento
- Verificação: com o wi-fi desligado, o que aparece na área visível ao cliente não é uma caixa vermelha
- **Este componente não é um "modo offline".** Não existe modo offline nesta stack. Ele apenas evita que a queda vire cena

---

## 6. Especificação de telas

Este documento cobre **apenas a Tela 1**. As Telas 2 e 3 dependem da Fase 0 de curadoria de dados e serão especificadas quando aquela fase tiver dados suficientes (§7 do plano).

### 6.1 Tela 1 — Simulador de viabilidade

#### 6.1.1 Objetivo

Fazer o cliente pegar o tablet. Concretamente: chegar num número anual de margem de contribuição incremental que ele mesmo ajudou a montar, com uma tradução por passagem que ele valide por intuição, e com o controle de cenário ao alcance da mão dele.

É a única tela que não depende de dado externo e a única que sozinha já substitui a planilha na reunião.

#### 6.1.2 Hierarquia — o que o cliente vê, em ordem

1. **A tradução em escala humana** — "3 a cada 10 carros que entram na oficina", 48px
2. **Os três botões de cenário** — 96px de altura, imediatamente acima do resultado
3. **O valor anual** — 36px
4. **O valor mensal e a faixa de premissas**
5. **O gráfico de sensibilidade**
6. A coluna de entradas, à esquerda — é o lado do vendedor
7. A faixa do vendedor, no rodapé — o cliente não lê a um metro, e é assim que tem que ser

#### 6.1.3 Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ▮ Suiça Tech      Simulador de viabilidade — refil de palhetas             │  cabeçalho
├─────────────────────────────┬──────────────────────────────────────────────┤
│ COLUNA A — ENTRADAS  (5/12) │ COLUNA B — CENÁRIO E RESULTADO       (7/12)  │
│                             │                                              │
│ A operação da concessionária│ ┌───────────┐┌───────────┐┌───────────┐      │
│                             │ │PESSIMISTA ││ REALISTA  ││ OTIMISTA  │      │
│ Pontos de venda             │ │    20%    ││    30%    ││    40%    │      │
│ [           10 ]            │ └───────────┘└───────────┘└───────────┘      │
│                             │ medido em 15+ concessionárias da carteira    │
│ Passagens por mês,          │                                              │
│ por ponto de venda          │ ajuste fino ────────────────────────         │
│ [          300 ]            │ 0% ─────────────●──────────────── 60%        │
│ → 3.000 passagens por mês   │                                              │
│   no total                  │ ┌──────────────────────────────────────────┐ │
│                             │ │                                          │ │
│ O produto — dianteiro       │ │  3 a cada 10 carros que entram           │ │
│                             │ │  na oficina                              │ │
│ Preço ao consumidor final,  │ │                                          │ │
│ por par                     │ │  R$ 141.480 por ano                      │ │
│ [              ]            │ │  margem de contribuição incremental       │ │
│                             │ │                                          │ │
│ Custo de aquisição, por par │ │  R$ 11.790 por mês                       │ │
│ [              ]            │ │                                          │ │
│ Preço e custo são negociados│ └──────────────────────────────────────────┘ │
│ caso a caso. Abrem em branco│ dianteiro 30% ◆ carteira · traseiro 10% ◆    │
│ de propósito.               │ carteira · substituição 0% ▪ premissa ·      │
│                             │ rampa e sazonalidade ⚠️ não aplicadas        │
│ A operação hoje             │                                              │
│                             │ ┌──────────────────────────────────────────┐ │
│ Margem de contribuição      │ │ Margem incremental anual por              │ │
│ mensal que você tem hoje    │ │ aproveitamento dianteiro                  │ │
│ com palhetas                │ │      ╱─────●                              │ │
│ [              ]            │ │   ╱──                                     │ │
│                             │ │ ╱   ┊    ┊    ┊                           │ │
│                             │ │    20%  30%  40%                          │ │
│                             │ └──────────────────────────────────────────┘ │
│                             │ ▸ Ver os números da curva                    │
│                             │ ▸ De onde vêm esses números                  │
├─────────────────────────────┴──────────────────────────────────────────────┤
│ ▸ Ajustes avançados                                                         │
├────────────────────────────────────────────────────────────────────────────┤
│ carga de 4,5 veículos por consultor por dia                                 │  faixa do vendedor
└────────────────────────────────────────────────────────────────────────────┘
```

**Estrutura em Streamlit, na ordem do script:**

```python
st.set_page_config(page_title="Simulador de viabilidade",
                   layout="wide", initial_sidebar_state="collapsed")
injetar_css()                       # 🔧 tokens da camada B
cabecalho()
col_a, col_b = st.columns([5, 7], gap="large")
with col_a:  entradas()             # 6 campos primários
with col_b:
    botoes_de_cenario()             # protagonista
    slider_ajuste_fino()            # secundário
    bloco_de_resultado()            # tradução ANTES do anual
    faixa_de_premissas()
    grafico_de_sensibilidade()
    tabela_da_curva()
    painel_de_formula()
ajustes_avancados()
faixa_do_vendedor()
```

#### 6.1.4 Campos primários — exatamente seis

O plano fixa **no máximo seis campos editáveis visíveis** (§3.1). São estes:

| # | Campo | Unidade no rótulo | Default |
|---|---|---|---|
| 1 | Pontos de venda | — | 1 |
| 2 | Passagens por mês, **por ponto de venda** | derivado: total | vazio |
| 3 | Preço ao consumidor final, **por par (dianteiro)** | par | **vazio, sempre** |
| 4 | Custo de aquisição, **por par (dianteiro)** | par | **vazio, sempre** |
| 5 | Margem de contribuição mensal que você tem hoje com palhetas | R$/mês | **vazio, obrigatório** |
| 6 | Aproveitamento dianteiro (três presets + slider) | % | nenhum preset ativo |

O conjunto presets + slider conta como **um** campo: é um controle sobre uma grandeza.

**O que ficou em Ajustes avançados, e por que cada um não merece o espaço:**

| Campo | Por que saiu |
|---|---|
| **Consultores por ponto de venda** | **Não entra em nenhuma conta de margem.** Ele alimenta só a verificação de carga (§6.1.8, R1), e o próprio plano proíbe a tradução "por consultor/dia" por ser ambígua (§3.6). Um campo que não muda o resultado e cuja leitura errada custa 10× não ocupa a superfície primária |
| **Dias úteis por mês** | Tem default 22 e serve exclusivamente à mesma verificação de carga. Ninguém abre a reunião discutindo dias úteis |
| **Preço e custo do traseiro** | Só entram se a proposta incluir traseiro. Enquanto vazios, o traseiro fica fora da conta e a faixa de premissas declara isso (§5.13). Trazê-los para a superfície primária levaria a oito campos e forçaria o vendedor a explicar par × unidade antes de ter um número na tela |
| **Aproveitamento traseiro** | Já é definido pelos presets junto com o dianteiro. Um segundo slider no primeiro plano competiria com o protagonista e convidaria justamente o erro que o risco nº 1 descreve |
| **Substituição / canibalização (%)** | Default 0, **mas declarado permanentemente na faixa de premissas** (§5.6). A premissa fica visível sem ocupar campo |
| **Mix de SKUs** | Só existe com mais de um produto. Soma validada em 100% |
| **Comissão, cashback, impostos** | Desligados por default. Entram quando o financeiro entra na conversa (§6.1.7) |
| **Investimento, estoque e payback** | ⚠️ Bloqueado pela decisão G (quantos códigos cobrem os 97%). Não entra na Fase 1 |

Sem esta tabela, o próximo a editar o documento simplesmente adiciona os campos de volta.

#### 6.1.5 O cálculo

Notação: `P` pontos de venda · `V` passagens/mês por ponto · `Cd`/`Ct` aproveitamento dianteiro/traseiro · `Pd`/`Kd` preço/custo do par dianteiro · `Pt`/`Kt` preço/custo da unidade traseira · `Ma` margem mensal atual com palhetas · `s` substituição.

```
T  = P × V                                    passagens totais por mês
Ud = T × Cd                                   pares dianteiros por mês
Ut = T × Ct                                   unidades traseiras por mês
MCd = Ud × (Pd − Kd)                          margem mensal do dianteiro
MCt = Ut × (Pt − Kt)     ou 0 se Pt/Kt vazios
MC  = MCd + MCt                               margem de contribuição bruta mensal
INC = MC − (Ma × s)                           margem de contribuição INCREMENTAL mensal
ANO = INC × 12                                ano cheio em regime  ⚠️ ver abaixo
TRAD = Cd                                     tradução: "X a cada 10 carros que entram"
```

**Três decisões de modelagem, cada uma com sua razão:**

1. **A âncora é em margem, não em faturamento.** O plano enuncia a pergunta como "quanto você fatura hoje com palhetas?" (§3.3) mas fixa como regra que "o resultado é lido em margem, não em receita". A regra vence a redação da pergunta: pedir faturamento e subtrair de margem misturaria grandezas. O campo pergunta **margem de contribuição mensal atual com palhetas**.

2. **A substituição opera sobre a âncora, não sobre uma margem unitária da original.** `INC = MC − Ma × s` mantém tudo na mesma língua e não exige um sétimo campo (a margem unitária da palheta original) que a Tela 1 não tem de onde tirar. Em `s = 100%`, o incremental é exatamente a diferença entre a margem nova e a atual — que é o que §3.3 descreve, inclusive podendo ser negativa.

3. **`ANO` é regime × 12 enquanto rampa e sazonalidade estiverem em aberto**, e o rótulo diz isso: "ano cheio em regime". Quando os coeficientes forem definidos (§10), `ANO` passa a ser a soma dos 12 meses com rampa e sazonalidade aplicadas, e o rótulo muda para "primeiros 12 meses". **O rótulo sempre descreve a conta que foi feita.** Trocar a conta sem trocar o rótulo é o jeito mais silencioso de o app mentir.

**Arredondamento e formatação.** Contas em `float`; exibição em Real com separador de milhar por ponto e sem centavos nos valores agregados (`R$ 141.480`), com centavos nos valores unitários (`R$ 197,90`). A tradução arredonda para o inteiro mais próximo em base 10: 30% → "3 a cada 10"; 27% → "quase 3 a cada 10"; 34% → "3 a cada 10". Nunca "3,4 a cada 10" — o ganho de precisão é nulo e o custo de credibilidade é alto.

#### 6.1.6 Estados

| Estado | Gatilho | Comportamento |
|---|---|---|
| **E0 — Inicial** | Primeira carga | Campos 2–5 vazios, nenhum preset ativo, bloco de resultado no estado E1. Nenhuma leitura de planilha, nenhuma rede além do próprio websocket |
| **E1 — Sem âncora** | Campo 5 vazio | **O valor anual não é exibido.** No lugar do bloco de resultado: `Falta a margem que você tem hoje com palhetas.` em `t-mensal`. O gráfico não é desenhado. Isto é deliberado: um default R$ 0 ancoraria no cenário mais favorável possível, e é falso — a concessionária já vende a palheta original hoje |
| **E2 — Sem cenário** | Campo 5 preenchido, nenhum preset e slider em 0 | Resultado calculado normalmente com Cd = 0. Nada de errado: é o cenário de não fazer nada |
| **E3 — Completo** | Campos 1–6 preenchidos | Resultado, faixa de premissas e gráfico renderizados |
| **E4 — Implausível** | Qualquer regra da §6.1.8 dispara | **Idêntico a E3 na área visível ao cliente.** A única diferença está na faixa do vendedor |
| **E5 — Incremental negativo** | `INC < 0` | Valor exibido com sinal, em `--tinta-primaria`. Nada em vermelho. A faixa do vendedor explica |
| **E6 — Reconectando** | Websocket cai | Último resultado permanece em tela. Aviso nativo neutralizado, no rodapé (§5.14) |
| **E7 — Hibernando** | App sem tráfego há 12 h | Tela do Streamlit Community Cloud, **não estilizável**. Mitigação é operacional: abrir o app antes de entrar na concessionária (§7.1) |

Não há estado "offline". Não existe (§1, §3 camada C).

#### 6.1.7 Comissão, cashback e impostos — a armadilha

Três campos em Ajustes avançados, **desligados por default**.

| Campo | Efeito no cálculo |
|---|---|
| Comissão do consultor | Abatida da margem: `MC − comissão × Ud` |
| Impostos sobre venda | Abatidos: `MC − aliquota × faturamento` |
| **Cashback** | **Nenhum efeito sobre a margem exibida** |

**Por que o cashback não desconta, e por que isso é fácil de errar.** A decisão A do plano define que o cashback **sai da margem da Suicatech**, não da concessionária. Ele é um argumento comercial, não uma dedução: *"são R$ 13.500 por mês distribuídos na sua equipe — consultores, gerentes e mecânicos. Pago por nós, não sai da sua margem."*

Consequências que o código precisa obedecer:
- Ligar o cashback **acrescenta uma linha de exibição**, nunca subtrai do resultado
- **A palavra "cashback" nunca aparece no rótulo do resultado.** O plano sugere "Margem após comissão e cashback" (§3.4), mas isso foi escrito antes da decisão A e agora estaria errado: o rótulo tem que nomear só o que de fato foi descontado. Rótulos corretos: `Margem de contribuição incremental` → `Margem incremental após comissão` → `Margem incremental após comissão e impostos`
- **O custo do cashback para a Suicatech não existe como campo.** Não há onde digitá-lo, não há onde exibi-lo. É informação interna, e o app tem link aberto (§1.4 do plano)
- Em nenhuma combinação o rótulo vira "lucro"

#### 6.1.8 Regras de plausibilidade

Todas escrevem **exclusivamente** na faixa do vendedor (§5.9), em ordem.

| # | Condição | Texto na faixa do vendedor |
|---|---|---|
| R1 | `V ÷ (consultores_por_ponto × dias_úteis) > 20` | `carga de {x} veículos por consultor por dia — confira se os consultores são por ponto ou no total` |
| R1b | `consultores_por_ponto` vazio | `verificação de carga desligada — consultores não informados` |
| R2 | `Kd > Pd` (ou `Kt > Pt`) | `custo acima do preço no {dianteiro/traseiro} — margem unitária negativa` |
| R3 | `INC < 0` | `com a substituição informada, o cenário fica negativo — reveja a substituição ou a margem atual` |
| R4 | `Pt` ou `Kt` vazios e mix inclui traseiro | `traseiro fora da conta — preço ou custo não informados` |
| R5 | Coeficientes de rampa/sazonalidade provisórios | `rampa e sazonalidade não aplicadas — coeficientes em definição` |

**Nenhuma dessas regras bloqueia o cálculo.** Um número implausível exibido com aviso discreto ainda serve à conversa; um bloqueio na frente do cliente encerra a cena.

**R1 usa grandezas por ponto** (`V` e consultores por ponto), não os totais — assim o resultado não depende de `P` e a conta permanece a mesma do plano (§3.2).

#### 6.1.9 O que nunca aparece na Tela 1

- A palavra **"lucro"**, em qualquer rótulo, tooltip, PDF ou nome de variável exibida
- Qualquer campo de **preço ou custo pré-preenchido**
- O **custo do cashback para a Suicatech**
- **`st.warning`, `st.error`, `st.exception`, `st.toast`, `st.balloons`, `st.snow`** — em qualquer ponto
- **Qualquer caixa vermelha ou amarela** na área visível ao cliente
- **A marca do Streamlit**: menu hambúrguer, rodapé, "Made with Streamlit", botão Deploy
- **Preço ou custo do traseiro derivado do dianteiro** por qualquer fator
- **O valor anual antes da tradução em escala humana**
- Qualquer **promessa de funcionamento sem rede**
- Ícone decorativo, emoji de ênfase, gradiente, sombra
- Um piso de preço inventado (decisão F em aberto)

---

## 7. Estados globais

### 7.1 Rede — o único que acontece com certeza

**Não existe offline nesta stack.** A lógica roda no servidor e o navegador só mantém um websocket. Sem conexão, tela morta. Nenhum cache, PWA ou service worker resolve, porque não há o que cachear.

Este documento **não promete nenhum comportamento offline**. Prometer e não ter é pior que assumir a dependência.

**O que o design controla:**

| Alavanca | Implementação nesta tela |
|---|---|
| **Peso mínimo por interação** | 6 campos primários, um controle de cenário, um recálculo por toque. Resultados agrupados num bloco só |
| **Primeira renderização leve** | A Tela 1 **não lê a planilha e não faz nenhuma requisição externa**. Zero dependência de dado externo (§0 do plano). Verificação: nenhuma chamada de rede fora do websocket na carga inicial |
| **Reconexão que não pareça pane** | §5.14 — aviso neutralizado no rodapé, último resultado preservado |
| **Nenhum elemento dependente de rede após carregar** | A Tela 1 não tem nenhum. Nem link externo |

**O que virou requisito de operação, não de interface** (§6.5 do plano): chip 4G no tablet ou roteamento pelo celular do vendedor; e **abrir o app cinco minutos antes de entrar na concessionária**, porque o Community Cloud hiberna após 12 h sem tráfego e a tela de "acordar o app" é do provedor, não estilizável. Um app de vendas usado duas ou três vezes por semana estará dormindo em quase toda visita.

### 7.2 Carregando

Entre o toque e a resposta do servidor, o Streamlit exibe seu indicador nativo. **Não substitua por esqueleto de carregamento** — o esqueleto limpa a tela e o cliente vê o resultado sumir.

Regra: o resultado anterior **permanece renderizado** durante o rerun. Em Streamlit isso é o comportamento padrão desde que nada dependa de `st.empty()` sendo limpo antes do recálculo. Não use `st.empty().empty()` no caminho do recálculo.

`st.spinner` é permitido apenas se algum cálculo passar de 500ms — o que nesta tela não deve acontecer, já que a conta é aritmética local.

### 7.3 Vazio

Estado E1 da §6.1.6. O vazio desta tela **não é uma falha, é a abertura da conversa**: a tela pede a margem que o cliente tem hoje, e essa é exatamente a pergunta que o vendedor precisa fazer. Trate o texto de estado vazio como roteiro de pitch, não como mensagem de erro.

### 7.4 Erro de dado

A Tela 1 não consome dado externo, então não há erro de dado de planilha aqui. O que pode falhar é `parametros.py` (presets, unidades, coeficientes). Regra: **falhar alto e cedo** — se um preset não declarar `origem`, ou se uma categoria não declarar `unidade`, o app **não sobe**, com mensagem no log do deploy. Nunca uma tela quebrada na frente do cliente, nunca um default silencioso.

### 7.5 Dado vencido

Não se aplica à Tela 1: não há dado coletado com data (§5.7). Este estado é da Tela 3.

---

## 8. Responsividade

**Tablet paisagem é o alvo primário. Quando houver conflito, o tablet ganha** — sem exceção e sem discussão.

| Faixa | Alvo | Layout |
|---|---|---|
| **≥ 1024px** | **Tablet paisagem (primário)** e desktop | Duas colunas `[5, 7]`. Todos os tokens da §3.2 nos valores nominais |
| 768–1023px | Tablet retrato | Coluna única. Ordem: cenário → resultado → premissas → gráfico → entradas → avançados. **O resultado sobe acima das entradas**, porque quem lê nessa orientação é o cliente |
| < 768px | Celular | Coluna única, mesma ordem. Tipografia reduzida em um passo (`t-traducao` 36px, `t-anual` 28px). Botões de cenário empilhados, 72px de altura cada |

**Regras.**
- Em nenhuma faixa os presets ficam abaixo do bloco de resultado
- Em nenhuma faixa a tradução fica abaixo do valor anual
- Em nenhuma faixa a faixa do vendedor sai do rodapé
- No celular, o gráfico mantém os 300px de altura — reduzi-lo torna a curva ilegível e é melhor rolar

Streamlit reordena `st.columns` empilhando na ordem de declaração quando a largura aperta. Como a coluna de entradas é declarada primeiro, **é preciso inverter a ordem de declaração abaixo de 1024px** para que o resultado suba. Faça isso com uma checagem de largura no código, não com CSS.

---

## 9. Acessibilidade

Aqui acessibilidade é legibilidade comercial, não conformidade formal. Parte do público é um gerente de cinquenta e poucos anos lendo em ângulo, sob luz forte, a um metro.

| Requisito | Especificação |
|---|---|
| **Contraste de texto** | Todo texto que o cliente lê: ≥ 4,5:1. Os tokens da §3.1 entregam 19,68:1 (primária) e 7,94:1 (secundária) |
| **Contraste de acento** | `--marca-vermelho` ≥ 4,5:1 sobre `#FFFFFF` e sobre `#F5F5F5`; branco sobre ele ≥ 4,5:1 (§3.1.1) |
| **A exceção deliberada** | `--tinta-discreta` na faixa do vendedor mede 3,59:1 a 12px. **Está abaixo do padrão de propósito** — é o mecanismo do canal privado. É o único texto do app nessa condição, e nenhuma informação necessária ao cliente vive nele |
| **Alvo de toque** | ≥ 56px em tudo; 96px nos presets (§3.4) |
| **Foco visível** | Contorno de 2px em `--marca-vermelho` (nativo via `primaryColor`). Nunca `outline: none` |
| **Teclado** | No desktop, ordem de tabulação = ordem do script: entradas → presets → slider → avançados. Presets acionáveis por Enter e Espaço (nativo) |
| **Redução de movimento** | `prefers-reduced-motion: reduce` zera as transições (§3.6) |
| **Independência de cor** | Nenhum estado depende só de matiz (§3.1.3). O preset ativo tem preenchimento **e** peso **e** menção por extenso na faixa de premissas. O marcador do gráfico é vermelho **e** único **e** rotulado |
| **Gêmeo em tabela** | O gráfico tem tabela equivalente (§5.11), obrigatória — é também o canal que substitui o tooltip inexistente em tablet |

---

## 10. Decisões em aberto

**Nenhum valor desta tabela vai fixado no código.** Todos vivem em `parametros.py` marcados como provisórios, e a tela exibe o marcador da §5.12.

| # | Decisão pendente | O que bloqueia na Tela 1 | Comportamento enquanto não houver resposta |
|---|---|---|---|
| **F** | Existe piso de preço que o vendedor não pode furar? | Validação de entrada dos campos 3 e 4 | **Nenhuma validação de piso.** Não invente um valor. Os campos aceitam qualquer número positivo |
| **G** | Quantos códigos de refil cobrem os 97% do mercado? | Bloco de investimento, estoque e payback | **O bloco não existe na Fase 1.** Não construa uma versão com número aproximado |
| **H** | Dispersão real do aproveitamento traseiro | Presets pessimista (7%) e otimista (13%) do traseiro | Derivados do dianteiro pela mesma proporção (0,67× e 1,33×) e **obrigatoriamente marcados `≈ derivado`**, nunca `◆ carteira` (§5.7). Só a linha realista (10%) é medida |
| **I** | Coeficientes da rampa dos 3 primeiros meses | Projeção de 12 meses | `ANO = INC × 12`, rotulado **"ano cheio em regime"**, e `rampa ⚠️ não aplicada` na faixa de premissas. Não escolha frações |
| **J** | Curva de sazonalidade (palheta é produto de chuva) | Projeção de 12 meses | Idem. Curva plana **não** é aplicada silenciosamente — a ausência é declarada |

**F, G e H** vêm da §8 do plano. **I e J** decorrem de §3.2 do plano, que exige rampa e sazonalidade sem fixar os coeficientes — o que na prática é uma decisão em aberto, e é tratada como tal.

**Item resolvido neste documento, registrado para rastreabilidade:** a §3.3 do plano enuncia a âncora como "quanto você fatura hoje com palhetas?" e ao mesmo tempo fixa que "o resultado é lido em margem, não em receita". Este documento segue a regra, não a redação: o campo pergunta **margem de contribuição mensal**. Ver §6.1.5, decisão 1.

---

## 11. Contrato de dados implicado

A Tela 1 não lê planilha. Mas a interface especificada acima exige campos que o modelo de dados do plano (§6.4) não tem, porque o plano modelou as Telas 2 e 3.

### 11.1 Campos que a interface exige e o plano ainda não tem

Todos em `parametros.py`, versionado com o código:

| Campo | Tipo | Valores aceitos | Elemento da tela que depende |
|---|---|---|---|
| `presets[].nome` | str | `pessimista` \| `realista` \| `otimista` | Rótulo do botão (§5.3) |
| `presets[].dianteiro` | float | 0–1 | Valor no botão e no slider |
| `presets[].traseiro` | float | 0–1 | Valor aplicado ao traseiro |
| **`presets[].origem_dianteiro`** | enum | `carteira_medida` \| `derivado` | **Marcador de procedência (§5.7).** Sem ele a tela não sabe se escreve `◆ carteira` ou `≈ derivado` |
| **`presets[].origem_traseiro`** | enum | `carteira_medida` \| `derivado` | Idem. `realista` é `carteira_medida`; `pessimista` e `otimista` são `derivado` |
| **`categorias[].unidade`** | enum | `par` \| `unitario` | Sufixo do rótulo de preço/custo e a regra de bloqueio (§5.13). **Atributo por categoria, nunca constante global** |
| `dias_uteis_padrao` | int | 22 | Campo em avançados |
| `carga_maxima_veiculos_dia` | float | 20 | Limiar da regra R1 (§6.1.8) |
| `slider_dominio` | tupla | (0, 60) | Domínio do slider **e** do eixo X do gráfico — o mesmo valor nos dois |
| `rampa_meses` | lista\|None | `None` enquanto ⚠️ I estiver aberta | Projeção anual e marcador (§5.12) |
| `sazonalidade_mensal` | lista\|None | `None` enquanto ⚠️ J estiver aberta | Idem |
| `piso_preco` | float\|None | **`None` obrigatoriamente** enquanto ⚠️ F estiver aberta | Ausência de validação de piso |

O campo `origem` é a novidade estrutural: o plano trata os presets como números, e a interface precisa deles como **números com procedência**. Sem esse campo, a tela não consegue distinguir os 10% medidos do traseiro dos 7% derivados — e essa distinção é a mitigação do risco nº 1 do plano.

### 11.2 Validações de publicação

Rodam na carga do módulo. Falha = o app **não sobe**, com erro no log do deploy. Nunca tela quebrada na frente do cliente.

| # | Validação | Se falhar |
|---|---|---|
| V1 | Todo preset declara `origem_dianteiro` e `origem_traseiro` | Aborta |
| V2 | `pessimista.dianteiro < realista.dianteiro < otimista.dianteiro`, idem traseiro | Aborta |
| V3 | Toda categoria declara `unidade` explicitamente | Aborta. **Nunca assuma `par` por default** |
| V4 | Todo valor de preset em 0–1 | Aborta |
| V5 | `slider_dominio` cobre todos os valores de preset | Aborta — senão um preset joga o marcador para fora do gráfico |
| V6 | `piso_preco is None` enquanto a decisão F estiver aberta | Aborta — impede que um piso inventado entre pela porta dos fundos |
| V7 | Se `rampa_meses` ou `sazonalidade_mensal` forem `None`, a faixa de premissas **precisa** renderizar o marcador ⚠️ | Aborta |

### 11.3 Casos-teste

Entradas e saídas esperadas. **Estes números são de teste. Nenhum deles vira default no código.**

**T1 — Cenário base.**
`P=1 · V=300 · Cd=30% · Ct=10% · Pd=197,90 · Kd=84,90 · Pt=99,00 · Kt=45,00 · Ma=4.000 · s=0`
```
T   = 300 passagens/mês
Ud  = 90 pares · Ut = 30 unidades
MCd = 90 × 113,00 = R$ 10.170,00
MCt = 30 × 54,00  = R$  1.620,00
MC  = R$ 11.790,00/mês · INC = R$ 11.790,00/mês · ANO = R$ 141.480,00
Tradução: "3 a cada 10 carros que entram na oficina"
```
Verificar também: a tradução é renderizada **antes** do valor anual, e em fonte maior.

**T2 — Substituição total, ainda positivo.**
T1 com `s=100%` → `INC = 11.790 − 4.000 = R$ 7.790,00/mês` · `ANO = R$ 93.480,00`.
A faixa de premissas passa a ler `substituição 100% ▪ premissa`.

**T3 — Substituição total, incremental negativo.**
T1 com `Ma=15.000` e `s=100%` → `INC = −R$ 3.210,00/mês` · `ANO = −R$ 38.520,00`.
Esperado: valor exibido com sinal, em `--tinta-primaria`, **sem nada vermelho e sem `st.error`**. Regra R3 escreve na faixa do vendedor. O gráfico desenha a linha do zero.

**T4 — Bloqueio de derivação de unidade.**
T1 com `Pt` e `Kt` vazios → `MCt = 0` · `INC = R$ 10.170,00/mês` · `ANO = R$ 122.040,00`.
Esperado: faixa de premissas lê `traseiro: preço não informado — fora da conta`; regra R4 na faixa do vendedor. **Verificar no código que `Pt` nunca é derivado de `Pd`**, nem por ÷2 nem por qualquer fator.

**T5 — Âncora vazia (estado E1).**
T1 com `Ma` vazio → **nenhum valor anual exibido, gráfico não desenhado.** No lugar: `Falta a margem que você tem hoje com palhetas.`
Esperado: em nenhum lugar do código `Ma` recebe 0 como default.

**T6 — Carga implausível (regra R1).**
`P=1 · V=1.500 · consultores_por_ponto=2 · dias_úteis=22` → `1.500 ÷ 2 ÷ 22 = 34,1`.
Esperado: faixa do vendedor lê `carga de 34,1 veículos por consultor por dia — confira se os consultores são por ponto ou no total`. **O cálculo não é bloqueado** e a área visível ao cliente fica idêntica ao estado E3.

**T7 — Carga plausível (não dispara).**
`P=10 · V=300 · consultores_por_ponto=3 · dias_úteis=22` → `300 ÷ 3 ÷ 22 = 4,55`. Nenhuma linha na faixa do vendedor por R1.
Verificar também: `→ 3.000 passagens por mês no total` e `→ 30 consultores no total` aparecem como totais derivados.

**T8 — Verificação de carga desligada.**
T1 com `consultores_por_ponto` vazio → faixa do vendedor lê `verificação de carga desligada — consultores não informados`. R1 não é avaliada com valor inventado.

**T9 — Preset ativo é derivado, não guardado.**
Pressionar REALISTA (Cd=30%, Ct=10%), depois mover o slider para 27%.
Esperado: **nenhum** dos três botões em `type="primary"`; faixa de premissas lê `dianteiro 27% ▪ ajustado na reunião`; **`Ct` permanece em 10%** — mover o slider do dianteiro não altera o traseiro.

**T10 — Domínio do gráfico igual ao do slider.**
Com `Cd` em 0% e em 60%, o marcador vermelho fica dentro do plot nas duas extremidades, sem recorte.

**T11 — Cashback não desconta.**
T1 com cashback ligado em qualquer valor → `INC` **inalterado** em R$ 11.790,00/mês. Rótulo permanece `margem de contribuição incremental` (a palavra "cashback" não entra no rótulo). Uma linha de exibição é acrescentada.

**T12 — Rótulo acompanha a conta.**
T1 com comissão ligada → rótulo vira `margem incremental após comissão`. Com comissão e impostos → `margem incremental após comissão e impostos`. Em nenhuma combinação aparece "lucro".

---

## 12. Checklist de aceite

Cada item é verificável olhando a tela pronta ou rodando o comando indicado. Marque todos antes de considerar a Tela 1 entregue.

### Stack e configuração

- [ ] `st.set_page_config(layout="wide", initial_sidebar_state="collapsed")` presente
- [ ] **Menu hambúrguer, rodapé, "Made with Streamlit" e botão Deploy ocultos** — nenhuma marca do framework visível em nenhuma resolução
- [ ] **Versão do Streamlit fixada com `==` no `requirements.txt`** (não `>=`, não faixa)
- [ ] Todo item marcado `🔧` neste documento foi testado contra exatamente essa versão
- [ ] O cenário sobrevive às interações via `st.session_state`
- [ ] Presets escritos em `st.session_state` por `on_click`, não por atribuição após a criação do widget
- [ ] **A Tela 1 não lê planilha nem faz requisição externa alguma** na carga inicial
- [ ] `grep -rn "st\.warning\|st\.error\|st\.exception\|st\.toast\|st\.balloons\|st\.snow" src/` retorna vazio

### Hierarquia e leitura

- [ ] **A tradução em escala humana é renderizada antes do valor anual na ordem do script**
- [ ] `font-size` da tradução ≥ 1,25 × `font-size` do valor anual (48 vs 36)
- [ ] A tradução é **por passagem**, nunca por consultor/dia
- [ ] Os três botões de cenário estão **acima** do bloco de resultado, na coluna do cliente
- [ ] Cada botão de cenário tem ≥ 96px de altura
- [ ] O slider está **abaixo** dos presets e rotulado "ajuste fino"
- [ ] Nenhum texto que o cliente precise ler está abaixo de 22px
- [ ] O bloco de resultado é legível a um metro (teste real: afaste-se um metro do tablet inclinado)

### Campos e densidade

- [ ] **Exatamente seis campos editáveis visíveis** fora de "Ajustes avançados"
- [ ] "Ajustes avançados" abre fechado a cada carga da página
- [ ] **Nenhum campo de preço ou custo vem preenchido** — `value=None` nos quatro
- [ ] Legenda explicando que os campos de preço/custo abrem vazios de propósito
- [ ] **Todo campo multiplicável mostra o total derivado**, inclusive quando o multiplicador é 1
- [ ] Todo campo multiplicável carrega a unidade no rótulo ("por ponto de venda" / "no total")
- [ ] Todo campo de preço e custo carrega a unidade ("por par" / "por unidade")
- [ ] Sem a margem atual do cliente, o valor anual **não** é exibido, e não existe default R$ 0

### Regras de conteúdo

- [ ] `grep -ri "lucro" src/` retorna vazio
- [ ] `grep -ri "ROI\|garantido\|grátis" src/` retorna vazio
- [ ] Todo resultado financeiro é rotulado "margem de contribuição"
- [ ] O rótulo do resultado nomeia só o que de fato foi descontado — **"cashback" nunca aparece nele**
- [ ] Ligar o cashback **não altera** o valor do resultado
- [ ] Não existe campo para o custo do cashback da Suicatech
- [ ] Presets do dianteiro rotulados como carteira real; a palavra "estimativa" **não** aparece junto deles
- [ ] Presets pessimista e otimista do **traseiro** marcados `≈ derivado`, nunca `◆ carteira`
- [ ] Faixa de premissas sempre visível, inclusive com todos os valores em default
- [ ] Substituição em 0% aparece declarada na faixa de premissas

### Unidade e par

- [ ] **Nenhuma expressão no código deriva preço ou custo do traseiro a partir do dianteiro** — nem ÷2, nem qualquer fator
- [ ] Com preço do traseiro vazio, o traseiro contribui R$ 0 e isso é declarado na faixa de premissas
- [ ] `unidade` é atributo declarado por categoria, e V3 aborta o app se estiver ausente

### Discordância sem constrangimento

- [ ] **Nenhuma caixa vermelha ou amarela em nenhum estado**, incluindo resultado negativo e queda de rede
- [ ] Todo aviso de plausibilidade vive na faixa do vendedor, 12px, cinza, sem caixa
- [ ] Nenhum cenário implausível é exibido sem aviso na faixa do vendedor
- [ ] Resultado negativo é exibido em tinta primária, com sinal, sem cor de alerta
- [ ] Nenhuma regra de plausibilidade bloqueia o cálculo
- [ ] Com o wi-fi desligado, o que aparece na área visível ao cliente não é uma caixa vermelha

### Gráfico

- [ ] Um eixo Y só — **nenhum gráfico de eixo duplo**
- [ ] Domínio de X do gráfico idêntico ao domínio do slider; o marcador nunca sai do plot
- [ ] Marcador da posição atual permanente, r = 8, com anel de 2px na cor da superfície
- [ ] Exatamente um rótulo direto, junto ao marcador; sem número em todos os pontos
- [ ] Marcas de preset e linhas de grade **sólidas**, nunca tracejadas
- [ ] Linha do zero desenhada sempre que o domínio de Y cruzar o zero
- [ ] Contêiner de 300px inclui a faixa do eixo — sem rolagem interna
- [ ] **Tabela gêmea da curva presente** (o canal que substitui o tooltip inexistente em tablet)
- [ ] Subtítulo declara que o traseiro está congelado e em que valor

### Decisões em aberto

- [ ] `grep -rn "piso" src/` não encontra nenhum piso de preço fixado (decisão F)
- [ ] Bloco de investimento/estoque/payback **não existe** na Fase 1 (decisão G)
- [ ] `rampa_meses` e `sazonalidade_mensal` são `None`, e a faixa de premissas mostra o marcador ⚠️ (decisões I e J)
- [ ] O rótulo do valor anual diz "ano cheio em regime" enquanto a rampa não estiver aplicada
- [ ] Nenhum valor da §10 aparece fixado fora de `parametros.py`

### Marca e acessibilidade

- [ ] `--marca-vermelho` substituído pelo vermelho oficial, e as três medidas da §3.1.1 refeitas e aprovadas
- [ ] Medição de cor do gráfico (§5.11.1) refeita após a substituição
- [ ] Nenhum estado comunicado só por matiz
- [ ] Foco visível em todos os controles; nenhum `outline: none`
- [ ] `prefers-reduced-motion: reduce` respeitado

### Promessa da stack

- [ ] **Nenhum item deste app, da interface ou de qualquer texto promete comportamento offline**
- [ ] Nenhuma tela sugere que o app funciona sem rede
- [ ] O material de operação registra o checklist pré-visita: abrir o app antes de entrar na concessionária

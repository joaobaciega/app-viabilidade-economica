# Plano do Aplicativo de Pitch — Refil de Palhetas para Concessionárias

**Versão 5.0 — 7 de agosto de 2026**
Documento de planejamento. Passou por revisão adversarial (v2), por duas rodadas de decisões do cliente (v3 e v4) e pela definição da stack (v5).

**Stack definida:** Python + Streamlit, com deploy no Streamlit Community Cloud. Decisão mandatória do cliente. Ela troca velocidade de construção por três perdas concretas — offline deixa de ser possível, o app hiberna após 12h sem uso, e toda interação custa uma ida ao servidor. As três estão tratadas nas §6.2, §6.5 e §3.7.

**Mudança estrutural na v4, ainda válida:** o refil é **universal** e atende 97% do mercado. Reduz a Fase 0 de ~225 para ~75 registros, destrava o cálculo de payback e cria o argumento comercial mais forte do produto — §2.5.

**Identidade visual:** Suiça Tech / Intrace AG. Logo com bandeira vermelha e tipografia preta sobre branco. Paleta do app: branco dominante, preto para texto, **vermelho como acento em 5–10%** — ver §8, decisão 7, para a divergência registrada em relação à proporção 60/30/10 sugerida.

---

## 0. Resumo executivo

Três telas, pesos e dificuldades muito diferentes:

| Tela | Valor no pitch | Dependência de dado externo | Esforço código | Esforço curadoria |
|---|---|---|---|---|
| 1. Simulador de viabilidade | Alto — é o pitch | Nenhuma | Médio | Nenhum |
| 2. Top 5 carros por marca | Médio — é credibilidade | Alta | Baixo | Médio |
| 3. Preço da palheta original | Alto — é a prova | Muito alta | Baixo | **Muito alto** |

**A conclusão mais importante:** o gargalo não é software, é **dado**. As telas 2 e 3 são triviais de programar e caras de manter. A tela 1 é a única que você coloca em campo sem depender de ninguém.

**Sequência recomendada:** lançar a tela 1 sozinha. Ela já substitui a planilha na reunião. As telas 2 e 3 entram depois, marca por marca.

**Correção importante em relação à v1:** minha tese de que "carro mais vendido em 2025 não é o que entra na oficina" **estava errada para o canal concessionária**. Ver §2.1. Sua intuição original estava mais certa que minha correção.

---

## 1. Diagnóstico da planilha atual

### 1.1 O comparativo "3,49x" não se sustenta

Na aba `Potencial Margem`, o resultado de 3,49x mais margem anual vem de premissas assimétricas que você arbitrou:

| Premissa | Palheta inteira | Refil |
|---|---|---|
| Preço de venda | R$ 459,00 | R$ 199,90 |
| Custo | R$ 270,00 (calculado como preço ÷ 1,7) | R$ 99,90 |
| Margem unitária | R$ 189,00 | R$ 100,00 |
| Vendas mensais/ponto | **10** | **66** |
| Taxa de conversão | **3,3%** | **22%** |

A aritmética está correta (R$79.200 ÷ R$22.680 = 3,49). O problema é outro: **a margem unitária do refil é MENOR** (R$100 contra R$189). O 3,49x vem inteiramente dos volumes e conversões que você escolheu para cada lado — 6,6x mais vendas.

Repare no que isso significa se o cliente ler com atenção: a tabela dele diz que ele ganha menos por unidade vendendo o seu produto. O argumento só funciona pelo volume, e o volume é premissa sua.

**Tratamento:** ver §3.3.

### 1.2 As duas abas se contradizem — e isso precisa ser resolvido antes do código

| Parâmetro | Aba `Estimativa` | Aba `Potencial Margem` | Diferença |
|---|---|---|---|
| Preço de venda do refil | R$ 197,90 | R$ 199,90 | 1% |
| Custo do refil | R$ 84,90 | R$ 99,90 | **18%** |
| Margem unitária | R$ 113,00 | R$ 100,00 | **13%** |
| Conversão | 30% | 22% | 36% |

Na projeção anual isso move o resultado em aproximadamente R$ 140 mil. **Esta é a decisão nº 1 da §8** — não dá para programar um simulador sem saber qual é o número verdadeiro.

### 1.3 A ambiguidade que pode explodir na sua mão

`C2: CONSULTORES DE VENDAS = 3` e `F2: PONTOS DE VENDAS = 10`. O rótulo não diz se os 3 consultores são **por ponto** ou **no total**.

A fórmula `F3 = F2*C3` prova que os 300 atendimentos são por ponto, o que sugere fortemente que os consultores também são. Mas *sugere* não é *diz*. E as duas leituras produzem resultados que diferem em 10x:

| Leitura | Consultores totais | Pares/consultor/dia |
|---|---|---|
| 3 por ponto (provável) | 30 | **1,4** — plausível |
| 3 no total | 3 | **13,6** — implausível, derruba o pitch |

Se um gerente fizer essa conta pela leitura errada na frente dos colegas, você não tem como recuperar. **Requisito do app:** todo campo multiplicável carrega o rótulo explícito ("por ponto de venda" / "no total"), e a tela mostra o total derivado em tempo real.

### 1.4 O cashback — resolvido, e melhor do que parecia

`J11 = R$ 13.500` aparecia na planilha sem afetar nada e sem dono. As duas lacunas foram fechadas:

- **Quem recebe:** consultores, gerentes e mecânicos. Rateio variável por negociação e por cargo
- **Quem paga: a Suicatech**, saindo da própria margem

Isso valida uma frase que a v2 marcava como não verificada, e ela pode ser dita literalmente na reunião:

> *"São R$ 13.500 por mês distribuídos na sua equipe — consultores, gerentes e mecânicos. Pago por nós, não sai da sua margem."*

Duas consequências de projeto:

- **A margem exibida ao cliente não é afetada.** O incentivo é custo da Suicatech; o app não o desconta da conta da concessionária
- **O custo do cashback para a Suicatech nunca aparece na tela.** É informação interna, e o app tem link aberto

Sanidade: R$ 13.500 ÷ 30 consultores = R$ 450/mês por pessoa. Plausível como incentivo — e agora com origem conhecida.

Incluir o mecânico é comercialmente acertado: é quem enxerga a borracha gasta primeiro. Vale só confirmar se algum grupo do portfólio tem política interna restringindo incentivo a pessoal técnico.

### 1.5 "Margem" não é "lucro"

A planilha para na margem de contribuição (preço − CMV). Você optou por manter, e é defensável **desde que a tela escreva "margem de contribuição", nunca "lucro"**. Comissão, imposto e cashback existem como campos opcionais (§3.4).

### 1.6 A linha de produto não distribui

`C8 = I2` joga todas as 900 vendas no primeiro produto; `C9` e `C10` vazias zeram o resto. Não há mix. **Tratamento:** mix percentual com validação de soma = 100%.

### 1.7 Não há investimento nem estoque

A primeira pergunta de uma concessionária é "quanto fica parado em estoque?". A planilha não responde. Ver §3.5 — e §3.5 depende de resolver a questão de medidas da §2.5.

---

## 2. Verificações de campo

### 2.1 CORREÇÃO: para concessionária, o carro novo É o carro relevante

Na v1 deste plano eu argumentei que palheta se troca na frota de 1 a 5 anos e que o ranking de emplacamentos 2025 seria enganoso. **Isso está errado para o seu canal**, e a correção importa:

- Vida útil de palheta é de **6 a 12 meses**, não anos
- Veículo em garantia (0 a 3 anos) é justamente o que **volta para a concessionária** na revisão; a migração para oficina independente acontece depois disso
- Logo, um carro emplacado em 2025 troca palheta em 2026 — **dentro da garantia, no balcão do seu cliente**

Minha afirmação de que o Tera "não vai gerar uma única venda de refil nos próximos anos" era falsa. Os 48 mil Teras de 2025 estão entrando na primeira troca agora.

**O que sobrevive da crítica, em forma menor:**

- **Tera** foi lançado ao longo de 2025 — a frota real é menor que os 48.143 emplacamentos sugerem, e é a mais nova dos cinco
- **Saveiro** é picape com forte componente de frota e uso comercial; perfil de manutenção diferente e frequentemente atendido fora da rede

Top 5 Volkswagen em 2025 (Fenabrave, via compilação Carro.Blog):

| # geral | Modelo | Emplacamentos 2025 |
|---|---|---|
| 2 | Polo | 122.677 |
| 4 | T-Cross | 92.842 |
| 9 | Saveiro | 67.753 |
| 20 | Nivus | 48.763 |
| 21 | Tera | 48.143 |

**Decisão revisada:** a manchete é o ranking 2025, como você pediu. A segunda coluna é o **acumulado 2022–2025 (janela de garantia e revisão)**, não 5 anos. A coluna B deixa de ser "correção" e vira **ampliação**: *"esses são os novos; somando os últimos quatro anos, é essa a base que passa pela sua oficina."*

### 2.2 VERIFICADO: o informe público da Fenabrave tem granularidade por modelo

Confirmei em um informe mensal real. O documento traz:

- Modelos mais emplacados por **segmento** (entrada, hatch pequeno, sedã compacto, SUV, picape)
- Volume por modelo individual (ex.: "1º VW/POLO 12.911")
- Separação por **canal** — venda direta versus varejo, que é relevante para você: varejo é o cliente que volta para a revisão
- Dados do mês e acumulado do ano

**Ressalva:** o menu "Mais Vendidos" do portal exige login, mas o **informe em PDF é público e gratuito**, com série histórica desde 2003. É esse o link que vai no app. Auditabilidade preservada.

**Achado extra:** o corte por canal (direta × varejo) é melhor dado que emplacamento total para o seu argumento. Venda direta é frota e locadora — não volta para a revisão do jeito que carro de varejo volta. Vale usar.

### 2.3 O Mercado Livre bloqueia raspagem automatizada — mas não bloqueia o clique

O `robots.txt` do Mercado Livre proíbe acesso automatizado às páginas de produto (confirmado ao tentar acessá-lo: o próprio arquivo está sob a regra). A API oficial exige registro de aplicação e token OAuth.

O que isso significa, com precisão:

- **Raspagem automática de preço está fora.** Bloqueada e frágil.
- **Um humano abrir o link na reunião continua sendo perfeitamente possível** — é exatamente o que o botão "ver no Mercado Livre" faz, e é o plano B se alguém questionar o print.
- A atualização dos preços será **manual**. Se quiser automatizar depois, o caminho é registrar aplicação no programa de desenvolvedores do ML. Projeto separado.

Sua escolha do modelo híbrido não foi só a melhor — era a única viável.

### 2.4 Cobertura de lojas oficiais no ML é incompleta

**Confirmado com fonte:** Volkswagen, Chevrolet, e as marcas Stellantis — Fiat, Jeep, Citroën, Peugeot, Ram (anúncio de agosto/2024).

**Indício, sem confirmação:** Nissan (existe uma loja "Nissan Peças & Acessórios" nos resultados, não verifiquei se é oficial da montadora).

**Não verificado:** Toyota, Honda, Hyundai (peças), Renault, GWM, BYD, CAOA Chery, Mitsubishi.

Você escolheu ~15 marcas. **Parte do item 3 não terá fonte no ML.** Regra de fallback, definida antes de começar:

| Prioridade | Fonte | Rótulo no card |
|---|---|---|
| 1 | Loja oficial da montadora no ML | "loja oficial [marca] — Mercado Livre" |
| 2 | E-commerce oficial de peças da própria montadora | "loja oficial [marca]" |
| 3 | Nenhuma disponível | "sem preço oficial publicado" — campo vazio |

**Nunca** preencher com preço de vendedor terceiro e chamar de "original". O item 3 existe para ser auditável; uma linha inventada destrói as outras 200.

### 2.5 A assimetria que virou o melhor argumento do produto

A v2 deste plano assumia que o refil, como a palheta original, era específico por modelo — e estimava 150 a 225 registros de curadoria. **Isso está errado.** O refil da Suicatech é **universal** e o mix atende **97% do mercado**.

A consequência não é só operacional. É comercial, e é o argumento mais forte que este produto tem:

| | Palheta original | Refil Suicatech |
|---|---|---|
| Aplicação | Específica por modelo e ano | Universal |
| Códigos para estocar | Dezenas | Punhado |
| Risco de peça parada | Alto — cada código tem giro próprio | Baixo |
| Ruptura de estoque | Frequente em código de baixo giro | Rara |

Para um gerente de pós-venda, isso significa: **atender mais carros com muito menos código em prateleira.** Não é um detalhe de catálogo — é redução de capital parado, de ruptura e de complexidade de compra, tudo de uma vez. E é verificável na hora, olhando a prateleira dele.

Este argumento não estava em nenhuma versão anterior do plano. Ele deveria estar em destaque na tela 3, não escondido numa nota.

**A assimetria permanece de um lado só:** a palheta original continua sendo específica por modelo, ano e posição. É por isso que o anúncio do exemplo se chama "Polo 2023 a 2025". Logo:

- **Lado do refil no card:** um preço, uma linha, zero curadoria
- **Lado da original no card:** continua exigindo modelo, faixa de ano e posição

**Fase 0 recalculada:** ~75 registros de preço original (15 marcas × 5 modelos), não 225. A tabela de aplicação some do lado do refil e permanece só do lado da original — e mesmo lá, só o suficiente para identificar o anúncio certo.

**Efeito colateral positivo:** o bloco de investimento e payback (§3.5) deixa de estar bloqueado. Com refil universal, estoque mínimo e capital de giro passam a ser calculáveis.

**Os 3% não atendidos** precisam de um estado na interface. Card que não tem cobertura mostra "fora do mix", não uma aproximação.

### 2.6 O print que você enviou não pode ser usado

O exemplo do Polo traz banner vermelho ocupando meia tela: **"Não é compatível com seu veículo"** — resultado de haver um veículo selecionado na sessão do ML. Mostrar isso é entregar munição ao cliente. Regra de captura na §5.2.

### 2.7 A unidade é por categoria, não global

Decisão 4 da §8: **os preços da Suicatech são por par.** Isso resolve o dianteiro — o anúncio do exemplo se chama "**Palhetas** Volkswagen Polo 2023 a 2025" (plural, imagem com duas lâminas), e o par bate com par.

**Mas colide com a decisão 5.** Palheta traseira é lâmina única na esmagadora maioria dos modelos. Se o catálogo tem categoria Traseiro e o preço é "por par", uma das duas afirmações precisa ser corrigida — ou o traseiro é vendido em par (e isso exige explicação ao cliente), ou **a unidade é atributo da categoria, não do catálogo**.

O modelo de dados assume a segunda hipótese: `unidade` é campo por linha, não constante global. Fica em aberto (decisão B da §8) qual é o valor correto para o traseiro.

Se um lado da comparação for par e o outro unidade, **o resultado erra por 2x** — na tela cuja única função é ser auditável. Todo preço, dos dois lados, exibe a unidade explicitamente, e o app bloqueia a comparação quando as unidades divergem em vez de converter.

---

## 3. Tela 1 — Simulador de viabilidade

### 3.1 Princípio de desenho

A planilha tem cerca de 30 células. Num tablet, na frente do cliente, isso é morte.

> **Máximo de 6 campos editáveis visíveis. Todo o resto vai para "Ajustes avançados".**

O objetivo não é reproduzir a planilha. É o cliente mexer em 2 ou 3 números e ver o resultado mudar na hora.

### 3.2 Estrutura

**Bloco A — A realidade dele** *(ele responde, você digita)*
- Pontos de venda
- Passagens/mês **por ponto** *(rótulo explícito — §1.3)*
- Consultores **por ponto** *(rótulo explícito)*
- Dias úteis/mês (padrão 22)
- *Exibe em tempo real: total de pontos × passagens e total de consultores*

**Bloco B — O produto** *(abre vazio ou em modo demo — §6.3)*
- Preço de venda ao consumidor final **— com unidade (par/unidade)**
- Custo de aquisição da concessionária **— mesma unidade**
- Mix de SKUs, se houver mais de um (soma validada em 100%)

**Bloco C — A conversão** *(duas barras, não uma)*

O catálogo se divide em **Dianteiro** e **Traseiro** (§8, decisão 5), e os dois convertem em taxas diferentes. Uma única barra aplicaria a taxa medida de dianteiro ao traseiro, inflando a projeção justamente na parte nunca medida.

- **Aproveitamento dianteiro** — presets com base de carteira real (15+ concessionárias):

| Preset | Valor |
|---|---|
| Pessimista | 20% |
| Realista | 30% |
| Otimista | 40% |

- **Aproveitamento traseiro** — média de **10%** na mesma carteira de 15+ concessionárias. Como só a média foi medida, os extremos são derivados pela mesma proporção do dianteiro (0,67× e 1,33×) e **rotulados como derivação, não como medição**:

| Preset | Dianteiro | Traseiro |
|---|---|---|
| Pessimista | 20% | 7% |
| Realista | **30%** | **10%** |
| Otimista | 40% | 13% |

Só a linha "realista" é dado medido nos dois casos. Se você tiver a dispersão real do traseiro, ela substitui a derivação.
- **Rampa:** os 3 primeiros meses entram com fração da conversão-alvo. Mês 1 não converte como o mês 12, e prometer isso é o jeito mais rápido de perder o cliente
- **Sazonalidade:** palheta é produto de chuva. Curva plana erra para menos na seca e para mais na chuva — e o cliente avalia você no mês seco

Os presets de dianteiro **não são estimativa**: vêm da sua carteira. Rotule como tal na tela — é um argumento que a concorrência não tem. E o preset otimista de 40% é batido por clientes reais seus (casos acima de 75%), o que torna a posição difícil de atacar.

**Bloco D — Resultado**
- Vendas, faturamento e margem de contribuição por mês
- Projeção 12 meses **com rampa e sazonalidade aplicadas**
- Tradução por passagem — §3.6

**Validação de sanidade** *(trava contra o pitch se destruir sozinho)*: se passagens ÷ consultores ÷ dias úteis passar de ~20 veículos/consultor/dia, o app avisa. Um número implausível na tela vale menos que campo vazio.

### 3.3 A âncora: incremental, não bruto

Você quer liberdade nos inputs — concordo. Mas o resultado precisa de âncora, senão não significa nada. Três regras:

**1. Campo obrigatório, sem default.**

> *"Quanto você fatura hoje com palhetas?"*

Sem valor padrão. Deixar R$ 0 como default ancora no cenário mais favorável possível — e é falso: a concessionária **já vende a palheta original hoje**. Se o cliente perceber que você contou como incremental o que ele já faturava, você perde tudo o que construiu.

**2. O resultado é lido em margem, não em receita.**

O documento inteiro insiste em margem de contribuição. A âncora tem que falar a mesma língua.

**3. Campo de substituição (canibalização).**

Que percentual das vendas de refil substitui uma palheta original que teria sido vendida de qualquer jeito? Se for 100%, o incremental é apenas a **diferença de margem** — que, pelos números da §1.1, pode ser **negativa por unidade**.

Este é o ponto mais desconfortável do plano e o mais importante. Se o refil canibaliza a palheta inteira e tem margem unitária menor, seu argumento **precisa** ser volume: *"você converte 3 a cada 10 carros em vez de 1 a cada 30, porque R$ 197 fecha e R$ 477 não fecha."* Esse argumento é forte e verdadeiro. Mas ele só aparece se o app permitir que a conta seja feita — e é melhor você chegar nele antes do gerente.

### 3.4 Comissão, cashback e imposto

Margem de contribuição é o padrão da tela. Três campos disponíveis, desligados por default:

| Campo | Efeito | Quando ligar |
|---|---|---|
| Comissão do consultor | % ou R$/unidade, abatido da margem | "e quanto o vendedor ganha?" |
| Cashback | Rateio entre consultores, gerentes e mecânicos — **pago pela Suicatech, saindo da margem dela** | Sempre que fizer parte da proposta |
| Impostos sobre venda | % sobre faturamento | Quando o financeiro entrar |

Com qualquer um ligado, o rótulo muda de "Margem de contribuição" para "Margem após comissão e cashback". **Nunca** "lucro".

### 3.5 Investimento e payback — destravado

A v2 bloqueava este bloco por falta da tabela de aplicação. Com o refil universal (§2.5), ele passa a ser calculável e vira um dos argumentos mais fortes da tela 1:

- **Códigos necessários para cobrir 97% do mercado** — o número exato ainda falta (decisão G da §8)
- Estoque mínimo em unidades e em reais
- Pedido mínimo, frete e prazo de pagamento negociado
- Resultado: capital de giro imobilizado e em quantas semanas o estoque gira

O comparativo que este bloco permite fazer é o mais persuasivo do produto para um gestor de estoque:

> *"Para cobrir os mesmos carros com palheta original, você precisa de dezenas de códigos. Com refil, de um punhado. Mesmo alcance, uma fração do capital parado."*

Falta apenas a política de sell-in para o bloco entrar na Fase 1.

### 3.6 A tradução que fecha a venda

R$ 1,2 milhão de margem anual soa irreal para um gerente. O cérebro rejeita antes de avaliar. Traduzir sempre para a escala da operação dele — mas para a escala **certa**:

| Tradução | Valor | Serve? |
|---|---|---|
| Por consultor/dia | 1,4 pares | Depende da leitura ambígua da §1.3 — **evitar** |
| **Por passagem** | **3 a cada 10 carros que entram** | **Sim** — sem ambiguidade |

A tradução por passagem é imune ao problema da §1.3 e é a que o gerente valida por intuição. E ela expõe imediatamente o que a §1.2 escondia: **30% de aproveitamento significa converter 3 de cada 10 carros que entram na oficina.** Se esse número não se sustenta, é melhor descobrir agora.

Ordem na tela: **primeiro a meta por passagem, depois o anual como consequência.** O anual sozinho parece promessa; precedido da meta, parece aritmética.

### 3.7 Sensibilidade — os presets viram o protagonista

A intenção original era um slider recalculando em tempo real: o cliente arrasta, o número muda na mão dele, e cliente que pega o tablet está comprando.

**Isso não é reproduzível em Streamlit** (§6.2): cada interação é uma ida ao servidor e o `st.slider` só dispara ao soltar. Insistir no slider como elemento principal entrega a pior versão da ideia — arraste sem retorno visual, seguido de um salto com latência.

**A adaptação, que é melhor do que um remendo:**

| Elemento | Papel |
|---|---|
| **Três botões grandes** — Pessimista 20% / Realista 30% / Otimista 40% | **Protagonista.** Uma ida ao servidor cada, resposta decisiva, imune à latência |
| Slider de conversão | Ajuste fino, secundário |
| Mini-gráfico de sensibilidade | Renderizado junto com o resultado, mostrando a curva inteira de uma vez |

Por que isso funciona melhor do que parece: agora que os presets vêm de **carteira real de 15+ concessionárias** (§8, decisão 2), apertar "Realista — 30%" é um gesto mais forte do que arrastar até 30%. O botão carrega a autoridade do dado; o arraste não carrega nada.

**Compensação importante:** como a curva inteira é calculada de uma vez no servidor, o mini-gráfico pode mostrar todos os cenários simultaneamente, com marcador na posição atual. O cliente vê o intervalo completo sem precisar interagir — o que recupera parte do efeito perdido, sem depender de latência.

### 3.8 Como calibrar os presets sem backend

Três seções deste plano dizem que os presets precisam vir de dados reais, e o app — sem login, sem servidor — não tem como coletá-los. O dado necessário para consertar o maior risco do projeto nunca vai existir sozinho.

Mínimo viável: o PDF exportado (§7, Fase 3) carrega identificação do cliente e os parâmetros simulados. Você cria uma rotina de conferir o realizado em 90 dias contra o simulado. Em dois trimestres você tem preset calibrado com dado próprio — que é um ativo comercial, não só um número de tela.

Enquanto isso não existir: **rotular os presets na tela como estimativa, não como histórico.** Vender um "conservador" que na verdade é otimista é o jeito mais rápido de perder o cliente no mês 2 e a indicação junto.

---

## 4. Tela 2 — Top 5 carros por marca

### 4.1 Conteúdo

Seletor de marca. Duas colunas:

| Coluna A — Emplacamentos 2025 | Coluna B — Acumulado 2022–2025 |
|---|---|
| Ranking do ano fechado | Janela de garantia e revisão |
| "Os carros novos da sua marca" | "A base que passa pela sua oficina" |

Cada linha: posição, modelo, volume, fonte.

**Refinamento recomendado:** se o esforço permitir, separar **varejo × venda direta** (§2.2). Venda direta é frota e locadora, que não volta para a revisão do mesmo jeito. É um dado mais fino que a concorrência não vai levar.

### 4.2 Auditabilidade

Rodapé fixo: fonte, período e link para o **PDF público** da Fenabrave. Nunca para área logada. Botão "Ver fonte" abre o documento; offline, exibe o PDF em cache.

### 4.3 Alerta de leitura

Modelo lançado há menos de **12 meses** recebe marca discreta: *"lançamento recente — frota em formação"*. Janela de 12 meses (não 3 anos, como na v1) para ficar coerente com a vida útil de 6 a 12 meses da palheta.

---

## 5. Tela 3 — Preço da palheta original

### 5.1 O card

Mostrar o preço da original sozinho não convence ninguém. O card precisa fazer a ponte:

```
┌──────────────────────────────────────────────┐
│  VOLKSWAGEN POLO  2023–2025                  │
│  Dianteira — par (600mm + 400mm)             │
│  ──────────────────────────────────────────  │
│  Palheta original — loja oficial VW          │
│  R$ 477,17  (par)     [print]  [ver no ML]   │
│  coletado em 06/08/2026                      │
│                                              │
│  Seu refil (par)                             │
│  R$ 197,90                        [editável] │
│  ──────────────────────────────────────────  │
│  Cliente economiza      R$ 279,27  (58,5%)   │
│                                              │
│  Requer armação em bom estado                │
└──────────────────────────────────────────────┘
```

Regras que o card precisa obedecer:

- **Unidade declarada dos dois lados** (§2.7). Par contra par, ou unidade contra unidade
- **Medida e ano-modelo visíveis** (§2.5), senão o card não é auditável
- **A ressalva sobre a armação** — comparar palheta inteira com refil é comparar coisas diferentes, e é o mesmo vício que derruba o 3,49x da §1.1. Declarar a condição desarma a objeção antes dela chegar
- **A margem da concessionária NÃO aparece no card.** O custo dela é seu preço de venda, que por decisão da §6.3 não vive na planilha pública. Esse número aparece só na tela 1, depois que o vendedor digitar

### 5.2 Regra de captura de print

- Janela anônima, **sem veículo selecionado no ML**, sem carrinho
- Recorte contendo: nome do produto, preço, e **o selo de loja oficial da montadora**
- Nome do arquivo: `marca_modelo_medida_AAAA-MM-DD.png`

O selo de loja oficial é o elemento mais importante. Sem ele o print prova preço, não prova origem.

### 5.3 Carimbo de data — sem bloqueio

**Decisão do cliente (07/08/2026): o preço é sempre exibido. Não há trava por idade do dado.**

O raciocínio está correto e a v2 deste plano errava: card bloqueado na frente do cliente é pior que preço velho. Vendedor com tela vazia perdeu a cena; vendedor com número datado ainda negocia.

Mas remover a trava não é remover o sinal. A regra que substitui:

| Elemento | Comportamento |
|---|---|
| Preço | **Sempre exibido**, qualquer idade |
| Data de coleta | **Sempre visível**, colada ao preço, na mesma classe de leitura |
| Aviso de idade | Apenas na faixa do vendedor — ilegível a um metro, invisível ao cliente |
| Link para a fonte | Sempre ativo |

**Por que a data resolve o que a trava resolvia.** Se o cliente clicar no link e encontrar outro valor, um preço com data é um fato datado — "esse é o preço de fevereiro, subiu desde então". O mesmo preço sem data é você sendo pego com dado velho. A data transforma a discrepância de armadilha em contexto.

O aviso interno existe só para você saber o que atualizar antes da visita, e conversa diretamente com a coleta sob demanda da §8, decisão 6.

---

## 6. Arquitetura

### 6.1 Stack — Python + Streamlit *(decisão do cliente, 07/08/2026)*

| Camada | Escolha | Observação |
|---|---|---|
| Linguagem | **Python** | Decisão mandatória |
| Framework | **Streamlit** | Decisão mandatória |
| Hospedagem | **Streamlit Community Cloud** | Deploy a partir do repositório, custo zero |
| Dados | Google Sheets lido pelo app, com `st.cache_data` | Integração nativa e simples — ponto forte real desta stack |
| Prints | Storage com URL pública, referenciada pela planilha | Servidos pelo servidor, não pelo aparelho |
| PDF | Gerado no servidor (`fpdf`/`reportlab`) + `st.download_button` | Mais simples aqui do que seria no navegador |
| Estado | `st.session_state` | Preserva o cenário entre interações |

**O que esta escolha entrega de verdade:** velocidade de construção e de iteração. Você mesmo consegue mexer no app sem depender de terceiros, a leitura da planilha é trivial, o deploy é um clique e o custo é zero. Para uma operação do seu tamanho, isso pesa mais do que a maioria dos argumentos técnicos contra.

**O que ela custa está na §6.2, e o custo é real.**

### 6.2 O que o Streamlit tira do plano

Streamlit renderiza no servidor: o navegador mantém um websocket aberto e cada interação envia um evento para o Python recalcular e devolver a tela. Isso tem três consequências diretas sobre requisitos que as versões anteriores tratavam como inegociáveis.

**1. Offline deixa de ser possível — não fica degradado, deixa de existir.**

A conta não acontece no aparelho. Sem conexão não há app: a tela morre. Não existe PWA, service worker ou cache que resolva, porque não há o que cachear — a lógica mora no servidor.

O requisito de offline **sai do plano** e é substituído por um requisito de conectividade (§6.5).

**2. O app dorme depois de 12 horas sem tráfego.**

Regra documentada do Streamlit Community Cloud. Quem abre um app dormindo vê uma tela com o botão *"Yes, get this app back up!"* e espera o servidor subir.

Um app de vendas usado duas ou três vezes por semana estará dormindo **em quase toda visita** — e isso acontece mesmo com wi-fi excelente. É o risco mais provável desta stack e o mais fácil de subestimar.

**3. Toda interação custa uma ida ao servidor.**

O `st.slider` dispara ao soltar, não durante o arraste. O momento que a §3.7 identifica como o que fecha a venda — o cliente arrastando e vendo o número mudar na mão — não é reproduzível aqui. Ver §3.7 revisada.

**Limites de recurso do plano gratuito**, para dimensionamento: até 2 núcleos de CPU e ~2,7 GB de memória por app. Folgado para este caso de uso; o gargalo é a hibernação, não o processamento.

### 6.5 Conectividade vira requisito de equipamento, não de código

Como o offline não é alcançável nesta stack, a resposta correta deixa de ser software e passa a ser hardware:

| Medida | Custo | O que resolve |
|---|---|---|
| Chip 4G no tablet, ou roteamento pelo celular do vendedor | ~R$ 50/mês por vendedor | Independência do wi-fi da concessionária |
| Abrir o app 5 minutos antes de entrar | Zero | Acorda o servidor antes do cliente ver |
| Ping automático mantendo o app acordado | Baixo | Reduz a hibernação, mas não substitui o item acima |

Vale registrar que a conectividade própria resolve **mais** do que um app offline resolveria: ela também faz funcionar o botão "ver no Mercado Livre", que depende de rede em qualquer arquitetura.

**Item obrigatório no checklist pré-visita:** abrir o app e confirmar que carregou, antes de entrar na concessionária.

### 6.3 Link aberto sem login — mitigação

Você optou por link aberto. Aceito, com uma trava barata: o app abre com os **campos de custo vazios** (ou com valores de demonstração claramente rotulados como exemplo). O vendedor digita os reais na frente do cliente.

O link público expõe a **estrutura**, não sua tabela de preços.

Nota honesta: se algum dia a preocupação virar real, **senha compartilhada não resolve** — ela vaza no primeiro cliente. A alternativa que de fato protege é login por vendedor, com o custo de complexidade que isso traz. Melhor saber disso agora do que implementar uma senha e achar que está protegido.

### 6.4 Modelo de dados

Planilha alimentando o app funciona **se o schema for rígido e se houver um passo de publicação**.

**Fluxo obrigatório:** planilha → validação de schema → **snapshot JSON versionado** → cache no service worker.

Sem esse passo intermediário, "você edita e o app lê" e "funciona sem rede" não coexistem: o app sem sinal carrega vazio. Com ele, você publica quando quiser e o app leva a última versão publicada no bolso.

**Aba `modelos`**

| marca | modelo | ano_lancamento | emplac_2025 | emplac_2022_2025 | canal_varejo | fonte_url | fonte_data |
|---|---|---|---|---|---|---|---|

**Aba `aplicacao`** *(a que faltava na v1 — §2.5)*

| marca | modelo | ano_ini | ano_fim | posicao | medida_mm | sku_refil |
|---|---|---|---|---|---|---|

`posicao` ∈ {`motorista`, `passageiro`, `traseira`}

**Aba `precos_originais`**

| marca | modelo | ano_ini | ano_fim | sku_original | unidade | preco | url_fonte | url_print | data_coleta | tipo_fonte |
|---|---|---|---|---|---|---|---|---|---|---|

`unidade` ∈ {`par`, `unitario`} — implementa a §2.7
`tipo_fonte` ∈ {`loja_oficial_ml`, `ecommerce_montadora`, `indisponivel`} — implementa a §2.4

**Riscos desta escolha, que você aceitou:**

- Alguém renomeia coluna e o app quebra → **validação de schema na publicação**, com erro claro em vez de tela branca
- Prints ficam soltos → nomenclatura rígida (§5.2) e pasta única
- Planilha encontrável → **ela não contém seu preço de venda à concessionária**. Esse campo vive só no app, digitado na hora

---

## 7. Sequência de entrega

### Fase 0 — Dados *(começa antes do código, roda em paralelo, é o gargalo real)*

Por marca:

1. Consolidar emplacamentos 2025 e acumulado 2022–2025 dos informes públicos da Fenabrave — **5 anos × 15 marcas de extração de PDF**, não "apenas somar"
2. Identificar a fonte de preço (loja oficial ML → e-commerce da montadora → indisponível)
3. **Montar a tabela de aplicação**: medidas por posição e por faixa de ano-modelo
4. Localizar o SKU original correspondente a cada medida
5. Capturar preço, link e print pela regra da §5.2

**Volume real: 150 a 225 registros**, não 75. E o passo 3 é o mais trabalhoso e o menos visível.

**Antes de estimar prazo, cronometre 5 registros reais de ponta a ponta.** Multiplicar dado medido é estimativa; multiplicar intuição é chute. E a Fase 0 precisa de **um nome responsável** — sem isso ela não acontece, e sem ela as telas 2 e 3 não existem.

**Recomendação forte:** começar por **3 marcas** — VW, Fiat, Chevrolet, as três com loja oficial confirmada e maior volume. Você descobre onde o processo quebra com ~40 registros em vez de 225.

### Fase 1 — Simulador

Tela 1 completa: blocos A–D, rótulos explícitos de multiplicação, **presets como elemento principal** e slider como ajuste fino, duas conversões (dianteiro e traseiro), rampa e sazonalidade, âncora incremental com campo de canibalização, tradução por passagem, campos opcionais de comissão/cashback/imposto, validação de sanidade.

**Zero dependência da Fase 0.** Vai para campo assim que pronta e já substitui a planilha.

Itens específicos do Streamlit que entram aqui, e não depois:

- `st.set_page_config(layout="wide")` — tablet em paisagem é o alvo
- **Ocultar o menu, o rodapé e a marca do Streamlit.** Um pitch de credibilidade com "Made with Streamlit" no rodapé contradiz o tom de instrumento
- `st.session_state` para o cenário sobreviver às interações
- `st.cache_data` na leitura da planilha
- Ping mantendo o app acordado (§6.5)

Sem bloqueios: o preço deixou de ser constante e virou campo de entrada (§8, decisão 1).

### Fase 2 — Telas 2 e 3

Marca por marca, conforme a Fase 0 avança. O app mostra **apenas marcas com dados completos** — melhor 3 marcas sólidas que 15 pela metade.

### Fase 3 — Fechamento

- PDF do cenário simulado, com fontes, links e identificação do cliente (§3.8) — gerado no servidor e entregue por `st.download_button`
- Carimbo de data nos preços e aviso interno de idade (§5.3)
- Bloco de investimento e payback (§3.5), destravado pelo refil universal
- Ajustes de leitura em tablet, via tema do Streamlit e CSS injetado

**Nota sobre CSS no Streamlit:** o tema nativo cobre cor primária, fundo e fonte. Tudo além disso — tamanho de fonte para leitura a um metro, alvos de toque, remoção da marca — exige CSS injetado via `st.markdown(unsafe_allow_html=True)`, que depende de classes internas do Streamlit e **quebra em atualizações de versão**. Fixe a versão do Streamlit no `requirements.txt` e trate a subida de versão como mudança que exige reteste visual.

### Esforço

Não tenho base para estimar horas ou custo sem saber quem constrói. O que dá para dizer com segurança:

| Fase | Esforço de código | Esforço de dado |
|---|---|---|
| 0 | Nenhum | **O maior do projeto** |
| 1 | Médio | Nenhum |
| 2 | Baixo | Consome o resultado da Fase 0 |
| 3 | Médio | Baixo |

A Fase 1 sozinha é um projeto pequeno. As Fases 0+2 juntas são o projeto de verdade — e a maior parte não é software.

---

## 8. Decisões — respondidas em 07/08/2026

### Resolvidas

**1. Preço e custo do refil — não existe número único.** O preço varia por negociação, cliente a cliente. Os R$ 197,90 e R$ 199,90 da planilha eram duas negociações diferentes, não uma contradição.

*Consequência de projeto:* preço e custo são **sempre campos de entrada**, nunca constantes. Isso reforça a §6.3 — o app abre com esses campos vazios e o vendedor digita os valores daquela negociação na frente do cliente.

*Risco novo que isso cria:* sem piso, um vendedor pode simular um preço abaixo do que a Suicatech honra, e o cliente ancora nele. Ver risco nº 4 da §9.

**2. Presets de conversão — com base real.** Carteira de 15+ concessionárias, aproveitamento médio de **30–35%**, variando mês a mês, com casos acima de 75%.

| Preset | Valor |
|---|---|
| Pessimista | 20% |
| Realista | 30% |
| Otimista | 40%+ |

Isso muda o status da §3.8: os presets **não são estimativa**, são dado de carteira própria. Podem e devem ser rotulados como tal na tela — é um ativo comercial que a concorrência não tem.

*Ponto forte que vale explorar:* o preset otimista (40%) é **batido por clientes reais da própria carteira** (75%). Prometer menos do que o melhor caso comprovado é uma posição rara e muito defensável numa objeção.

*Mas atenção — ver decisão 5:* a métrica coletada é **refis dianteiros ÷ passagens**. É aproveitamento de dianteiro, não do catálogo inteiro.

**3. Cashback — destinatários definidos, pagador não.** Recebem consultores, gerentes e mecânicos; quem recebe e quanto varia por negociação.

*Consequência de projeto:* não é um campo, é **rateio**. O componente precisa aceitar múltiplos destinatários com valores distintos, e o total precisa fechar.

*Continua em aberto:* **de quem sai o dinheiro.** Se sai da margem da Suicatech, são R$ 13.500/mês no cenário da planilha que não estão em lugar nenhum deste plano. Se sai da margem da concessionária, ela cai de R$ 113 para R$ 98 por par e o pitch precisa dizer isso na tela.

*Observação:* incluir o mecânico é comercialmente inteligente — é quem enxerga a borracha gasta primeiro. Vale confirmar se algum grupo do seu portfólio tem política interna que restrinja incentivo a pessoal técnico.

**4. Preços por par.** Resolve a §2.7 para o dianteiro. **Conflita com a decisão 5:** palheta traseira é lâmina única. Ou o traseiro também é vendido em par, ou a unidade é **por categoria**, não global. Ver §2.7 revisada.

**5. Catálogo dividido em Dianteiro e Traseiro.** Todos os produtos seguem essa divisão.

*Consequência mais importante deste documento:* **uma única taxa de conversão deixa de servir.** O dado de 30–35% é de dianteiro. Aplicar a mesma taxa ao traseiro infla a projeção exatamente na parte que nunca foi medida. A tela 1 precisa de **duas conversões independentes**, com o traseiro partindo de um valor conservador até haver medição própria.

**6. Coleta — feita pelo João, cadência semestral proposta.**

*Conflito direto com a §5.3:* a regra de validade bloqueia preço com mais de 60 dias. Com refresh semestral, o app fica bloqueado a maior parte do tempo.

*Solução que reduz o trabalho em vez de aumentar:* **coleta sob demanda, não em lote.** Você não precisa de 15 marcas atualizadas o tempo todo — precisa da marca daquela visita atualizada antes daquela reunião. São ~5 registros por visita em vez de ~225 por semestre. A regra de validade continua íntegra e o volume de trabalho cai.

*Risco que permanece:* a pessoa mais cara da operação fazendo a tarefa mais repetitiva. A coleta sob demanda ameniza, não elimina.

**7. Identidade visual — Suiça Tech.** Logo com bandeira vermelha e tipografia preta sobre branco; assinatura "INTRACE AG". Proporção sugerida pelo cliente: 60% branco / 30% vermelho / 10% preto.

*Divergência técnica, registrada:* 60/30/10 é regra de composição de ambiente, não de interface. Em tela de instrumento, 30% de vermelho lê como alerta e satura a leitura a um metro sob luz de showroom — e o plano já exige que nada em vermelho apareça na área visível ao cliente (§ tela 1 e 3).

*Recomendação:* manter branco como superfície dominante, preto para texto, e **vermelho como acento em 5–10%**, concentrado no controle deslizante e no número de resultado. Vermelho concentrado num ponto tem mais presença de marca que vermelho espalhado. O logo carrega o resto da identidade.

**8. Interlocutor — gerente de pós-venda.**

*Consequências:*
- O **risco nº 1 do plano v2 (verba de peças genuínas) cai de prioridade** — é métrica do gerente de peças, não dele. Continua relevante só na hora de destravar o estoque.
- **"Aproveitamento" é a métrica nativa dele.** O app inteiro deve falar nessa língua: conversão por passagem em primeiro plano, faturamento como consequência.
- A tradução da §3.6 (X a cada 10 carros que entram) deixa de ser recurso didático e vira **o KPI que ele já usa**.

### Rodada 2 — respondidas em 07/08/2026

**A. Cashback sai da margem da Suicatech.** Não afeta a margem exibida ao cliente, e vira uma frase literal do pitch (§3.4). O custo interno nunca aparece na tela.

**B. Traseiro é vendido por unidade.** Confirma que `unidade` é atributo de categoria: **dianteiro = par, traseiro = unitário** (§2.7). Como as duas formas coexistem no mesmo catálogo e na mesma tela, a proibição de converter unitário para par multiplicando por dois deixa de ser precaução e vira regra crítica.

**C. Aproveitamento traseiro: 10%** de média na mesma carteira. Presets derivados na §3.2.

**D. Preço sem trava de atualização.** Sempre exibido, com data sempre visível e aviso de idade só na faixa do vendedor (§5.3).

**E. O refil é universal — mix atende 97% do mercado.** A resposta de maior impacto do projeto inteiro (§2.5): Fase 0 cai de ~225 para ~75 registros, o bloco de payback destrava, e surge um argumento comercial que não existia em nenhuma versão anterior.

### Continuam em aberto

| # | Decisão | Bloqueia |
|---|---|---|
| F | Existe piso de preço que o vendedor não pode furar? | Validação de entrada da tela 1 |
| G | Quantos códigos de refil cobrem os 97%? | Argumento de estoque da §2.5 e cálculo de capital de giro |
| H | Dispersão real do aproveitamento traseiro | Substitui a derivação dos presets pessimista/otimista |

Nenhuma bloqueia o início da Fase 1. A **G** é a mais valiosa: o número exato de códigos é o que transforma "menos peça em prateleira" de adjetivo em argumento — *"você troca 40 códigos por 3"* é uma frase que fecha reunião, e ela precisa do número certo.

---

## 9. Riscos

Ordenados por impacto × probabilidade estimados. **Os três primeiros são objeções comerciais que o plano v1 não tinha e são as mais prováveis de aparecer numa reunião real.**

| # | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| 1 | **Conversão do traseiro aplicada por analogia ao dianteiro.** O dado de 30–35% é só de dianteiro. Se a mesma taxa for usada nos dois, a projeção infla na metade nunca medida — e o erro só aparece no mês 3 do cliente | Alta | Alto | Duas barras independentes (§3.2); traseiro rotulado como estimativa até haver medição própria |
| 2 | **Preço de balcão ≠ preço do ML.** O card assume que o cliente final pagaria R$ 477,17. Se a concessionária vende a original por outro valor, a economia exibida está errada — e se ela vende mais caro, você acabou de mostrar ao gerente que o balcão dele está fora de mercado, na frente dele | Alta | Alto | Campo editável: "quanto você cobra hoje pela original?" — transforma um constrangimento em diagnóstico |
| 3 | **Preço desatualizado sem contexto.** Sem trava por idade (§8, decisão D), um preço de meses atrás pode ser conferido pelo cliente e divergir | Alta | Médio | Data sempre visível colada ao preço; aviso de idade na faixa do vendedor; coleta sob demanda por marca antes de cada visita |
| 4 | **Vendedor simula preço abaixo do piso.** Preço é campo livre e negociado; o cliente ancora num número que a Suicatech não honra | Média | Alto | Definir se existe piso (decisão D da §8) e validar na entrada |
| 5 | **Política de garantia.** Peça não genuína em veículo em garantia de fábrica | Média | Alto | Levantar a posição de cada montadora antes de vender para a marca |
| 6 | **App dormindo no início da reunião.** Streamlit Community Cloud hiberna após 12h sem tráfego; o cliente vê a tela de "acordar o app" nos primeiros segundos do pitch | **Muito alta** | Alto | Abrir o app antes de entrar (checklist §6.5); ping automático como reforço |
| 6b | **Queda de rede mata o app.** Sem offline possível nesta stack (§6.2), perder conexão encerra a apresentação | Média | **Crítico** | Conectividade própria: chip 4G ou roteamento pelo celular (§6.5) |
| 7 | Canibalização anula o incremental | Média | Médio | Campo explícito na §3.3 — melhor você chegar nele antes do gerente |
| 8 | Marca sem loja oficial no ML | Alta | Médio | Regra de fallback (§2.4); nunca inventar preço |
| 9 | **Verba / rebate de peças genuínas.** Objeção nº 1 do gerente de peças — **rebaixado** porque o interlocutor definido é o gerente de pós-venda (§8, decisão 8) | Média | Médio | Volta a importar na hora de destravar estoque com o setor de peças |
| 10 | Concorrente recebe o link e vê sua tabela | Baixa | Médio | Campos de preço e custo vazios por padrão (§6.3) — reforçado pelo fato de o preço ser negociado caso a caso |
| 11 | ML muda estrutura de link | Baixa | Baixo | Print funciona sozinho; link é reforço |

---

## Fontes

- [Portal Fenabrave — Emplacamentos](https://www.fenabrave.org.br/portalv2/Conteudo/Emplacamentos) — informes mensais e anuais em PDF, série histórica 2003–2025; seção "Mais Vendidos" do portal exige login, os informes em PDF não
- [Fenabrave — Resumo Mensal (exemplo de informe público)](https://static.poder360.com.br/2025/06/Resumo-Mensal-Maio-de-2025-fenabrave-4-jun-2025.pdf) — verificação de granularidade: traz ranking por modelo individual, por segmento e por canal (direta × varejo)
- [Ranking 2025: os 100 carros mais vendidos do Brasil — Carro.Blog](https://carro.blog.br/noticia/brasil/100-carros-mais-vendidos-de-2025.html) — compilação com fonte Fenabrave
- [AUTOO — Veículos mais vendidos 2025](https://www.autoo.com.br/emplacamentos/veiculos-mais-vendidos/2025/) — ranking com filtro por marca, modelo, ano e mês
- [Stellantis amplia lojas oficiais no Mercado Livre](https://www.media.stellantis.com/br-pt/stellantis-parts-services/press/stellantis-amplia-lojas-oficiais-das-marcas-no-mercado-livre-a) — confirmação de lojas oficiais Fiat, Jeep, Citroën, Peugeot e Ram (ago/2024)
- [Mercado Livre Developers — Items & Searches](https://developers.mercadolivre.com.br/en_us/items-and-searches) — API exige registro de aplicação e token OAuth
- [Loja oficial Volkswagen — Peças e Acessórios](https://www.mercadolivre.com.br/loja/volkswagen/pecas-e-acessorios) e [Chevrolet loja oficial](https://www.mercadolivre.com.br/a/store/chevrolet-loja-oficial) — lojas oficiais confirmadas
- [Dyna — Quanto tempo dura uma palheta de para-brisa](https://dyna.com.br/quanto-tempo-dura-uma-palheta-de-para-brisa/) — vida útil de 6 a 12 meses, base da correção da §2.1

---

## Anexo A — O que mudou da v4 para a v5

Origem: definição da stack pelo cliente em 07/08/2026 — Python + Streamlit, deploy no Streamlit Community Cloud.

| § | Mudança |
|---|---|
| 6.1 | Stack reescrita para Python/Streamlit. Ganho real: velocidade de construção, leitura de planilha trivial, deploy de um clique, custo zero |
| 6.2 | **Seção nova.** Três perdas documentadas: offline impossível, hibernação após 12h sem tráfego, latência de servidor a cada interação |
| 6.5 | **Seção nova.** Offline sai do plano; conectividade vira requisito de equipamento (chip 4G ~R$50/mês) e item de checklist pré-visita |
| 3.7 | Slider deixa de ser protagonista; **os três presets assumem o papel**. Adaptação favorecida pelo fato de os presets virem de carteira real |
| 7 Fase 1 | Offline removido; entram os itens específicos de Streamlit, incluindo ocultar a marca do framework |
| 7 Fase 3 | Alerta sobre fragilidade do CSS injetado e necessidade de fixar a versão do Streamlit |
| 9 | Dois riscos novos: hibernação (probabilidade muito alta) e queda de rede (impacto crítico, sem mitigação em software) |

## Anexo B — O que mudou da v3 para a v4

Origem: segunda rodada de respostas do cliente, em 07/08/2026.

| § | Mudança |
|---|---|
| 2.5 | **Reescrita.** Refil é universal, atende 97% do mercado. Fase 0 cai de ~225 para ~75 registros. Surge o argumento de redução de códigos em estoque — o mais forte do produto e ausente de todas as versões anteriores |
| 1.4 / 3.4 | **Resolvido:** cashback é pago pela Suicatech, sai da margem dela. Não afeta a margem exibida ao cliente e vira frase literal do pitch |
| 2.7 | **Confirmado:** dianteiro = par, traseiro = unitário. As duas formas coexistem, o que torna crítica a proibição de converter multiplicando por 2 |
| 3.2 | Presets do traseiro: 10% medido, extremos derivados por proporção e rotulados como derivação |
| 3.5 | **Destravado.** Payback e capital de giro voltam a ser calculáveis |
| 5.3 | **Revertido:** sem trava por idade. Preço sempre exibido, data sempre visível, aviso de idade só na faixa do vendedor |
| 8 | Decisões A–E resolvidas; F, G e H abertas — nenhuma bloqueia a Fase 1 |
| 9 | Risco 3 reclassificado de Alto para Médio impacto |

## Anexo C — O que mudou da v2 para a v3

Origem: respostas do cliente às 8 decisões pendentes, em 07/08/2026.

| § | Mudança |
|---|---|
| Cabeçalho | Identidade Suiça Tech registrada, com divergência sobre a proporção de vermelho |
| 1.2 / 8.1 | **Resolvido:** não existe preço único — é negociado caso a caso. Preço e custo viram campos de entrada permanentes |
| 2.7 | **Revisado:** unidade é atributo da categoria, não do catálogo. Par confirmado para dianteiro; traseiro em aberto |
| 3.2 Bloco C | **Reescrito:** duas barras de conversão (dianteiro e traseiro), presets 20/30/40 com base de carteira real |
| 3.8 | Presets deixam de ser estimativa — passam a ser dado próprio de 15+ concessionárias |
| 8 | Seção reescrita: 8 decisões respondidas, 5 novas abertas (A–E) |
| 9 | Riscos reordenados. Conversão do traseiro entra como nº 1; verba de peças genuínas cai para nº 9 |
| — | **Decisão E é a de maior impacto:** se o refil for universal por comprimento, a Fase 0 encolhe de ~225 para ~15 registros |

## Anexo D — O que mudou da v1 para a v2

| § | Mudança | Origem |
|---|---|---|
| 2.1 | **Tese invertida.** Para concessionária, carro novo é o carro relevante | Revisão adversarial + vida útil de 6–12 meses verificada |
| 2.5 | **Seção nova.** Tabela de medidas e aplicação; volume real de 150–225 registros, não 75 | Revisão adversarial |
| 2.7 | **Seção nova.** Declaração de unidade (par × unitário) | Revisão adversarial |
| 1.3 | **Seção nova.** Ambiguidade "3 consultores" e o risco de 10x | Revisão adversarial (que errou a leitura, mas acertou o risco) |
| 3.3 | Âncora sem default R$ 0, em margem, com campo de canibalização | Revisão adversarial |
| 3.6 | Tradução por **passagem**, não por consultor/dia | Revisão adversarial |
| 5.1 | Margem removida do card (não havia fonte de dado para ela) | Revisão adversarial |
| 5.3 | Validade 30/60/90 em vez de 90 | Revisão adversarial |
| 6.2/7 | Offline movido para a Fase 1 | Revisão adversarial |
| 9 | Rebate, garantia e preço de balcão adicionados como riscos 1–3 | Revisão adversarial |
| 2.2 | Granularidade do PDF Fenabrave **verificada**, não inferida | Verificação direta |

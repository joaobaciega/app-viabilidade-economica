# Divergências e acréscimos declarados

O `DESIGN.md` v5 não tem uma seção de divergências. Este arquivo é ela.

**Regra que este arquivo existe para cumprir:** nada foge do DESIGN em silêncio.
Toda divergência tem quem autorizou, o motivo e o custo de reverter.

| | |
|---|---|
| Fonte de verdade | `DESIGN.md` v5 e `plano-app-viabilidade_1.md` v5.0, ambos de 11/08/2026 |
| Stack | Python 3.14.6 + Streamlit **1.58.0** (fixada com `==`) |
| Gerado em | 11/08/2026 |

---

## 1. Divergências autorizadas pelo cliente

Autorizadas na sessão de 11/08/2026, quando o cliente pediu que a interface
ficasse parecida com um dashboard próprio (escuro, arredondado, com ícones) e
escolheu a opção "claro do DESIGN + estrutura do print".

### D1 — Raio de 12 px em cartão/bloco e 6 px em campo/chip

| | |
|---|---|
| O que o DESIGN diz | §3.5: `raio` 4 px "em tudo. Nada arredondado demais" |
| O que foi feito | 12 px em cartão e bloco, 6 px em campo e chip |
| Por quê | Pedido explícito de "visual arredondado". 12 px ainda é sóbrio: a referência continua sendo painel de instrumento, não landing page |
| Onde | `src/css.py`, tokens `--raio-cartao` e `--raio-campo` |
| Reverter | Trocar dois valores em `src/css.py` |

### D2 — Ícones de linha monocromáticos

| | |
|---|---|
| O que o DESIGN diz | P10: "Sem ícone decorativo, sem emoji" |
| O que foi feito | SVG inline de traço, em `currentColor`, **funcional apenas** |
| Por quê | Pedido de "ícones bonitos". A divergência é limitada para preservar a intenção do P10 |
| Onde | `src/icones.py` |
| Reverter | `svg()` passa a devolver `""` — nenhum outro arquivo muda |

Regras que mantêm a intenção do P10 (todas verificadas em `src/icones.py`):

1. **Monocromático.** Nenhum ícone introduz cor, e nenhum usa `--marca-vermelho`.
2. **Funcional, nunca decorativo.** Só identidade de seção e affordance de campo.
3. **Sempre acompanhado de palavra.** Nunca canal único de informação.
4. **Nunca emoji** em área visível ao cliente. A única exceção é o glifo `⚠️` do
   `MarcadorDecisaoAberta`, que a §5.12 especifica literalmente.

### D3 — Reordenação de coluna abaixo de 1024 px por CSS

| | |
|---|---|
| O que o DESIGN diz | §8: "Faça isso com uma checagem de largura no código, **não com CSS**" |
| O que foi feito | `order` de flexbox sob `@media (max-width: 1023px)` |
| Por quê | **O Streamlit não expõe a largura da viewport ao Python.** As alternativas eram um componente de terceiro lendo `window.innerWidth` — que adiciona dependência e um round-trip antes da primeira pintura, piorando exatamente o que a §7.2 protege — ou aceitar que em retrato as entradas fiquem acima do resultado, o que a §8 proíbe |
| Onde | `src/css.py`, seção 13 |
| Se preferir o componente JS | É troca de abordagem, não de resultado. Diga e eu troco |

### D5 — Vermelho ampliado, e uma área em vez de um detalhe

| | |
|---|---|
| O que o DESIGN diz | §3.1: `--marca-vermelho` serve ao **botão de cenário ativo** e ao **marcador do gráfico**, "Nada mais". §3.1.2 fixa 5–10% da tela |
| O que foi feito | Faixa de cabeçalho vermelha de largura total; pílulas de navegação; etiquetas e filetes de seção; borda esquerda dos cartões de entrada; borda superior dos tiles; régua no topo do bloco de resultado; trilho do slider; chip do total derivado |
| Por quê | O cliente avaliou a versão literal como "muito feia e totalmente branca, falta capricho, parece uma aplicação de 2005" e pediu explicitamente **mais vermelho**. Vermelho concentrado num detalhe não dá presença de marca numa tela desta densidade |
| O que **não** mudou | **Nenhum número de resultado usa vermelho.** §13.1 vale integralmente: número financeiro em vermelho lê como prejuízo, que é o oposto do que o pitch afirma. O vermelho também não é usado em nenhum aviso, erro ou bloqueio — §3.1.2 |
| Limite testado | `test_sombra_e_gradiente_so_nos_lugares_declarados` e `test_render_resultado_negativo_sem_vermelho` |

### D6 — Cartão de resultado escuro

| | |
|---|---|
| O que o DESIGN diz | §3.1: superfície branca dominante |
| O que foi feito | O bloco de resultado é um cartão `#141414` com texto branco e régua vermelha no topo |
| Por quê | Resolve as duas partes da crítica de uma vez: tira o "totalmente branco" e dá ao número da manchete o maior contraste da tela. **Branco sobre `#141414` mede 17,9:1** — mais do que os 18,9:1 de preto sobre branco perdia ao virar cinza, e muito acima do piso AAA de 7:1 |
| Por que o risco de reflexo da §3.1 não se aplica | Ali o argumento era sobre **superfície dominante**: uma página escura inteira vira espelho sob luz de showroom. Aqui a área escura é um cartão de ~35% da coluna direita, cercado de superfície clara |
| Reverter | Dois tokens em `css.py` (`SUPERFICIE_ESCURA`, `TINTA_CLARA`) |

### D7 — Sombra sutil em cartão

| | |
|---|---|
| O que o DESIGN diz | §3.5: "elevação por traço, **nenhuma** sombra. Sombra é a primeira coisa que faz uma tela parecer material publicitário" |
| O que foi feito | Dois tokens: `--sombra-cartao` (1px + 8px, opacidade 4–5%) e `--sombra-hero` (só no cartão de resultado) |
| Por quê | Sem nenhuma profundidade os cartões ficam com aparência de recorte. A sombra é fraca o bastante para desaparecer sob luz forte, e o traço de 1px continua sustentando a borda sozinho — a degradação da §3.5 é preservada |
| Limite testado | `test_sombra_e_gradiente_so_nos_lugares_declarados`: toda sombra vem de um token declarado, e não há gradiente fora dos três lugares autorizados |

### D8 — Mais de seis campos na superfície primária

| | |
|---|---|
| O que o plano diz | §3.1: "máximo de 6 campos editáveis visíveis" |
| O que foi feito | Nove campos, em quatro cartões nomeados: operação (2), o que ele vende hoje (3), refil dianteiro (2), refil traseiro (2) |
| Por quê | Duas decisões do cliente em 11/08/2026: **(a)** a âncora deixou de ser um campo único e virou três — quantas palhetas ele vende, a quanto, e o custo dela; **(b)** preço e custo do traseiro subiram de Ajustes avançados para a tela inicial, por pedido explícito |
| Como o teto continua sendo respeitado | Por **bloco**, não por tela: nenhum cartão tem mais de três campos, e cada um tem um título que diz qual pergunta ele responde. O objetivo da §3.1 era "não reproduzir a planilha de 30 células"; quatro cartões de 2–3 campos com pergunta declarada não é a planilha |
| O que continua fora | Consultores, dias úteis, substituição, aproveitamento traseiro, comissão, imposto e cashback seguem em Ajustes avançados |

### D9 — A âncora deixou de ser "margem de contribuição atual"

Esta é a mudança de **produto** desta rodada, não de estilo.

| | |
|---|---|
| O que o DESIGN diz | §6.1.5, decisão 1: o campo pergunta *margem de contribuição mensal atual com palhetas*, escolhida sobre faturamento para não misturar grandezas |
| O que foi feito | Três campos: **quantas palhetas ele vende por mês**, **o preço da original que ele cobra** e **o custo dela (opcional)** |
| Por quê | O cliente: *"não gosto da ideia de você colocar a margem de contribuição atual. Devemos perguntar quantas palhetas ele vende por mês e o preço delas."* Está correto — um gerente de pós-venda não sabe de cabeça a própria margem de contribuição com palhetas, e a §13.5 do DESIGN v4 já registrava esse risco. As três perguntas novas são respondíveis na hora, e amarram a aba **Preço original** ao fluxo: o preço da original é conferido ao vivo |
| Como a regra "resultado lido em margem" foi preservada | O custo da original é o que produz `margem unitária = Po − Ko`, e a canibalização desconta `canibalizados × margem unitária`. **Sem o custo não existe incremental**, e o rótulo passa a dizer `margem de contribuição do refil` — nunca "incremental". O app não assume margem nenhuma para a original |
| Consequência no cálculo | `INC = MC − (Ud × s) × (Po − Ko)`. A canibalização incide **só no dianteiro**, que é o par que o cliente trocaria de qualquer forma; o traseiro é venda que não existia |
| Novas regras de plausibilidade | R6 (substituição sem custo da original) e R7 (canibaliza mais do que ele vende) |

### D10 — O gráfico tem duas linhas, em margem total

| | |
|---|---|
| O que o DESIGN diz | §5.11: "**série única**", "sem caixa de legenda", "exatamente um rótulo direto", e "a curva plota **exatamente a mesma grandeza da manchete**" |
| O que foi feito | Duas linhas: **com refil** (preta, cheia, crescente) e **só com a palheta original** (cinza, tracejada, horizontal). Rótulo direto em cada uma, mais o do marcador |
| Por quê | Pedido do cliente (11/08/2026). E é o comparativo que o gerente pede: mostra o **absoluto** dos dois cenários, não só o delta |
| Como a regra da "mesma grandeza" foi preservada | A **distância entre as linhas é exatamente o incremental**, que é a manchete — e ela está anotada no gráfico, no ponto atual, em vermelho: `+ R$ 141.480`. Assim o número da manchete aparece no gráfico como medida, não desapareceu. `test_curvas_comparadas_duas_linhas_e_a_distancia_e_o_incremental` trava isso |
| Legenda | Continua sem caixa de legenda: cada linha tem **rótulo direto** (`com refil`, `só com a palheta original`). Rótulo direto identifica melhor e não gasta o espaço que a §5.11 quer preservar |
| Independência de cor | As duas linhas diferem por **tinta e por tracejado**, não só por cor (§3.1.3, §9.4). Sobrevive a impressão e a daltonismo |
| Sem o custo da original | Volta a **uma linha**, plotando o incremental. O app não inventa margem para a original |
| Frase de apoio | Abaixo do gráfico, o cruzamento: "a partir de X% de aproveitamento o refil passa a render mais". Se não houver cruzamento na faixa, o app **diz que não há** em vez de sugerir que existe |

### D11 — Aproveitamento traseiro na superfície primária

| | |
|---|---|
| O que o DESIGN diz | §6.1.4: o aproveitamento traseiro fica em Ajustes avançados, porque "um segundo slider no primeiro plano competiria com o protagonista e convidaria justamente o erro que o risco nº 1 descreve" |
| O que foi feito | Slider + três atalhos (7% / 10% / 13%) no cartão do traseiro, na **coluna de entradas** |
| Por quê | Pedido do cliente: *"adicione um campo para colocarmos o aproveitamento das traseiras — normalmente elas tem aproveitamento menor, algo em torno de 10% — deixe fácil de trocar o valor"* |
| Como o risco nº 1 continua mitigado | Três coisas, todas intactas: **(a)** ele vive na coluna do **vendedor**, não na coluna que o cliente lê — o protagonista (presets de 96 px) segue sem concorrente; **(b)** os atalhos são de 44 px, não 96; **(c)** a procedência continua declarada — 10% é `◆ carteira`, 7% e 13% são `≈ derivado`, e o `title` de cada atalho diz qual é qual |
| Acoplamento | Nenhum, nas duas direções. `aplicar_traseiro` não escreve no dianteiro, e o slider do dianteiro não escreve no traseiro. Verificado por AST em `test_aplicar_traseiro_nao_toca_no_dianteiro` e `test_slider_nao_altera_o_traseiro` |
| Um widget só | O controle **saiu** de Ajustes avançados. Instanciar a mesma chave duas vezes levantaria `StreamlitAPIException` e derrubaria a tela; `test_aproveitamento_traseiro_tem_um_unico_controle` garante que existe exatamente um |

### D12 — Logo em arquivo, com reserva

Não é divergência do DESIGN — ele não especifica o logo. Registro porque tem
regra própria.

| | |
|---|---|
| Onde | `assets/logo.svg` (ou `.png`, `.webp`, `.jpg`). Ver `assets/LEIA-ME.md` |
| Como entra na página | Embutido como `data:` URI por `src/marca.py`. **Não** `st.image` nem `st.logo`: os dois criam endpoint de mídia e uma requisição HTTP por render, e a §7.1 exige que a Tela 1 não faça nenhuma requisição externa |
| Limite | 400 kB. Acima disso o app usa a reserva e diz o motivo na faixa do vendedor — um logo de 3 MB embutido a cada rerun seria latência na reunião |
| Reserva | Sem arquivo (ou com arquivo ilegível), o cabeçalho mostra a marca em tipografia e a faixa do vendedor avisa. Nunca imagem quebrada, nunca tela travada (§7.4) |
| Estado atual | **Logo oficial instalado** (11/08/2026), a partir do `logo.png` que o cliente colocou na raiz. `FUNDO_CLARO = True`, porque o logo é vermelho sobre branco e letra vermelha sobre faixa vermelha não tem contraste |
| Dois recortes | `logo.png` (palavra-marca + bandeiras + assinatura) no **cabeçalho**; `logo-completo.png` (com a tarja de slogan) no **PDF**. Ver D13 |

### D13 — A tarja de slogan não vai no cabeçalho

| | |
|---|---|
| O que o cliente pediu | "coloque a logo que está no arquivo logo" |
| O que foi feito | O cabeçalho usa o logo **sem a tarja** `O NÚMERO 1 EM BORRACHA PARA PALHETA`. O lockup inteiro vai no PDF |
| Motivo 1 — legibilidade | O lockup tem três andares. Em 44 px de cabeçalho a palavra-marca cairia para ~18 px e a assinatura viraria borrão. Um logo ilegível presta menos serviço à marca que um logo menor e nítido |
| Motivo 2 — tom | §4 do DESIGN proíbe linguagem de anúncio na copy do app ("linguagem de anúncio destrói o tom de instrumento"), porque ela trabalha contra a tese da tela, que é **"confira você mesmo"**. Um superlativo não verificável no topo de uma ferramenta de auditoria enfraquece o resto |
| Onde a tarja aparece | No **PDF**, onde há espaço e o documento não é o instrumento da negociação |
| Reverter | Uma linha, em `assets/LEIA-ME.md`: copiar `logo-completo.png` sobre `logo.png` e subir `.st-logo` para ~64px |

### D14 — Nenhum texto de tela fala do cliente em terceira pessoa

| | |
|---|---|
| O que o cliente pediu | "não mencione 'ele', por exemplo em palhetas que ele vende por mês, coloque apenas 'palhetas vendidas por mês'. Faça em todos os outros campos" |
| O que foi feito | Todos os rótulos passaram a ser impessoais. `A operação dele` → `A operação da concessionária`; `O que ele vende hoje` → `A venda de palhetas hoje`; `Palhetas que ele vende por mês` → `Palhetas vendidas por mês`; `Preço da palheta original que ele cobra hoje` → `Preço da palheta original cobrado hoje`; `Custo da palheta original para ele` → `Custo da palheta original`; `ele responde, você digita` → `informado na reunião`. Idem no PDF, nos tiles, na faixa do vendedor e no painel de fórmula |
| Por que isso importa mais do que parece | Não é estilo, é a cena da §1: **o tablet está inclinado na direção do gerente**. "Palhetas que ele vende por mês" é uma frase sobre alguém que está lendo a frase. Falar de quem está do outro lado da mesa em terceira pessoa é o tipo de detalhe que custa uma reunião |
| Onde continua havendo pessoa | Onde o texto se **dirige** a alguém, dirige-se ao cliente em segunda pessoa — "não sai da sua margem", "Cashback para sua equipe". Isso é o oposto do problema |
| Travado por | `test_nenhum_texto_de_tela_fala_do_cliente_em_terceira_pessoa` |

### D15 — Canibalização deixou de ser modelada

**Esta é a divergência de maior consequência do projeto.** Registro completo
porque ela troca uma pergunta desconfortável por uma premissa favorável.

| | |
|---|---|
| O que o cliente pediu | "Tirar a Substituição (canibalização)" |
| O que o plano diz | §3.3, regra 3: o campo de substituição é uma das **três regras** da âncora. §9, risco 7: *"canibalização anula o incremental"*, com mitigação *"campo explícito na §3.3 — melhor você chegar nele antes do gerente"* |
| O que o DESIGN diz | §5.6: *"Substituição em 0% significa 'o refil não tira nenhuma venda da original' — é a premissa **mais favorável possível**, e o cliente tem que poder vê-la"* |
| O que foi feito | O campo saiu da interface e do modelo. `INC = MC`: nada é subtraído |
| Como a honestidade foi preservada | A premissa não ficou implícita. `parametros.CANIBALIZACAO_MODELADA = False` é a fonte única, e **a faixa de premissas declara `sem canibalização — todo refil é venda nova` em toda simulação**. O PDF imprime a mesma linha, porque o documento sai da sala e ninguém estará ao lado para explicar |
| O que se perdeu, e vale saber antes de ir a campo | **1.** Se um gerente perguntar *"mas isso não tira da minha venda de palheta?"*, o app não tem mais como fazer a conta na tela. **2.** O gráfico perdeu o ponto de cruzamento: sem canibalização o refil sempre soma, então a frase passou a ser "supera em toda a faixa" em quase todo cenário. **3.** A palavra "incremental" no rótulo agora repousa sobre essa premissa, não sobre uma subtração |
| Travado por | `test_canibalizacao_nao_modelada_e_declarada` (a constante existe, o campo não existe em `Entradas`) e `test_render_faixa_de_premissas_sempre_visivel` (a premissa aparece na tela) |

### D16 — Deduções unificadas em Cashback, com grade 2 × 3

| | |
|---|---|
| O que o cliente pediu | "Juntar a parte das deduções em uma só, chamada Cashback. Nela teremos 2 linhas, dianteiro e traseiro. Em cada linha, 3 campos: Consultor, Gerente, Marketing" |
| O que o DESIGN diz | §6.1.7 define **três** campos opcionais em avançados: comissão, cashback e impostos. §5.18 modela o cashback como **rateio percentual** de um total, com validação de soma = 100% |
| O que foi feito | Uma seção só, **Cashback**, com R$ **por venda** para cada destinatário, em duas linhas (dianteiro por par, traseiro por unidade). Comissão e impostos saíram |
| Por que o modelo novo é melhor | O valor destinado ao consultor por venda **é** a comissão dele — o modelo antigo tinha a mesma coisa em dois lugares. E R$ absoluto por venda dispensa a validação de soma 100% da §5.18: não há como "não fechar" |
| A regra que **não** mudou | Cashback é pago pela Suicatech, saindo da margem **dela** (plano, decisão A). Preencher **acrescenta uma linha** ao resultado e nunca altera a manchete. Nenhum campo de cashback aparece em qualquer expressão que produza `incremental_mensal` |
| O que se perdeu | Impostos saíram, então o app não responde mais *"e com imposto?"* quando o financeiro entra na conversa (§6.1.7 previa isso). Não há mais rótulo `após comissão` / `após impostos` — e `test_T12` proíbe qualquer rótulo com "após", para nunca anunciar dedução inexistente |
| Onde aparece no resultado | Bloco próprio dentro do cartão escuro, com filete vermelho à esquerda e o rateio por destinatário. A separação visual existe para o cliente **não somar** cashback com margem |
| Travado por | `test_T2_cashback_por_venda_nas_duas_categorias`, `test_nenhuma_deducao_altera_a_margem_exibida`, `test_render_cashback_nao_muda_o_numero` |

### D17 — Bloco de investimento/estoque/payback: nem a declaração de ausência

| | |
|---|---|
| O que o cliente pediu | "tire a parte de investimento, estoque e payback" |
| Situação anterior | O bloco nunca existiu (⚠️ G). O que existia era uma **declaração** de que ele está ausente, com o `MarcadorDecisaoAberta` |
| O que foi feito | A declaração saiu da Tela 1 |
| Por que é seguro | §10-G diz *"ausência não promete nada"* — e a decisão G continua **visível onde vale algo**: no bloco "menos código na prateleira" da Tela 3, que é onde o número faria diferença comercial |
| Travado por | `test_render_bloco_de_investimento_ausente` (nenhum campo **e** nenhuma menção na Tela 1) e a verificação de navegador, que confirma "decisão G" na Tela 3 |

### D4 — Vermelho não é usado em filete de seção *(revogada por D5)*

Registro para rastreabilidade: na rodada anterior os filetes de seção usavam
`--traco` para respeitar a §3.1. **D5 substitui isso** — o cliente pediu mais
vermelho, e as etiquetas e filetes de seção passaram a usá-lo. O que permanece
intacto é a proibição do vermelho **nos números** e **nos avisos**.

### D4-antiga — o que continua valendo dela

Não é divergência do DESIGN, é **fidelidade a ele contra o print.** O dashboard
de referência usa laranja como acento em todo título de seção. A §3.1 restringe
`--marca-vermelho` ao **botão de cenário ativo** e ao **marcador do gráfico** —
"Nada mais" — porque §3.1.2 estabelece que o vermelho está gasto como marca e
portanto não é alerta. Os filetes de seção usam `--traco`.

Se quiser os filetes em vermelho, a §3.1 precisa ser editada primeiro.

---

## 2. Acréscimos declarados

Coisas que o DESIGN v5 não cobre porque ele especifica **só a Tela 1**, e que o
escopo desta entrega exige.

| # | Acréscimo | Origem | Status |
|---|---|---|---|
| +15 | `CartaoComparativo` | plano §5.1 | **Provisório** até o DESIGN ser regerado para a Tela 3 |
| +16 | `SeloProcedencia` | plano §5.3 | **Provisório** |
| +17 | `EstadoVazioCatalogo` | plano §7 Fase 2 | **Provisório** |
| +18 | `ExportadorPDF` | plano §3.8, §6.1, §7 Fase 3 | Pedido para esta entrega |

### As duas famílias de validação

O prompt pedia "as validações V1–V13 no pipeline". A v5 do DESIGN tem **V1–V7**,
e elas validam `parametros.py`, não a planilha. Resolvido sem colisão de nome:

| Família | Onde roda | Falha causa | Origem |
|---|---|---|---|
| **V1–V7** | `src/validacao_parametros.py`, no import | **O app não sobe** | DESIGN §11.2, canônico |
| **S1–S13** | `pipeline/validacoes.py`, na publicação | **`exit != 0`**, nada publicado | Enumeração adotada — ver abaixo |

**S1–S13 é suposição declarada.** O plano §6.4 **exige** validação de schema na
publicação ("com erro claro em vez de tela branca") mas **não enumera as regras**.
Usei como enumeração as treze do `DESIGN.md` v4 §11.2 — o único conjunto escrito
que trata desse assunto no projeto. Se você tiver outra lista, ela substitui.

### Os quatro casos-teste que fecham 16

A §11.3 da v5 tem **T1–T12**. O prompt pedia 16. Os quatro acrescentados cobrem
exigências que a v5 escreve mas não transformou em caso-teste:

| Caso | Cobre | Exigência da v5 |
|---|---|---|
| T13 | Tradução e arredondamento | §6.1.5 |
| T14 | Formatação de moeda | §6.1.5 |
| T15 | V1–V7 abortam o app | §11.2, §7.4 |
| T16 | Build reprova snapshot inválido | plano §6.4 |

### Decisões em aberto K e L

A §10 da v5 tem **F, G, H, I, J**. O prompt pedia **F–L**. K e L entram como
extensões já implícitas na v5:

| # | Decisão | Onde já estava implícita | Comportamento conservador |
|---|---|---|---|
| **K** | Hexadecimal oficial do vermelho | §3.1.1 marca `⚠️ SUBSTITUIR` | Provisório validado `#C8102E` |
| **L** | A partir de quantos dias recoletar um preço | plano §5.3 não fixa limiar | `None` — a faixa exibe a idade **crua em dias** |

### Outros acréscimos menores

| O que | Por quê |
|---|---|
| Estado `E1b_sem_produto` | A v5 nomeia E0–E5 e não nomeia "âncora informada, preço ainda vazio". Mesma consequência de E1: nenhum valor em R$ na tela |
| Botão `novo cliente` | A não persistência (P3, §5.2, plano §6.3) precisa de um gatilho de limpeza entre visitas |
| Tabela de estado de sessão | A §11.1 da v5 lista campos de `parametros.py`; a tabela de sessão é exigida por P3, §5.2, §6.1.9 e plano §6.3 |
| Ping keep-awake | plano §6.5, risco 6 (hibernação após 12 h, probabilidade **muito alta**) |

---

## 3. Suposições marcadas no código

Todas com `# SUPOSIÇÃO:` no arquivo indicado. Nenhuma trava a construção; todas
podem ser derrubadas com uma frase sua.

| # | Suposição | Arquivo |
|---|---|---|
| 1 | Comissão e imposto abatem de `MC` **antes** da substituição. A §6.1.7 não diz a ordem | `src/calculo.py` |
| 2 | Comissão incide sobre **todas** as unidades (`Ud + Ut`). A §6.1.7 escreve `MC − comissão × Ud`, citando só o dianteiro; ignorar `Ut` superestimaria a margem quando o traseiro entra na conta | `src/calculo.py` |
| 3 | Rótulo para imposto sozinho: `margem incremental após impostos`. A §6.1.7 dá os outros dois | `src/calculo.py` |
| 4 | Limiar do "quase" na tradução: `n = arredonda(Cd×10)`; se `Cd×10 < n`, prefixo "quase". Reproduz os três exemplos da §6.1.5. Meio arredonda para cima, logo 25% → "quase 3 a cada 10" | `src/formato.py` |
| 5 | Em 0%: `nenhum a cada 10`. "0 a cada 10" é lido em voz alta como "zero" e soa como impossibilidade, quando 0% é só o cenário de não fazer nada (E2) | `src/formato.py` |
| 6 | R4 dispara quando **um** dos dois campos do traseiro foi informado. Com os dois vazios, o traseiro não faz parte da proposta e não há o que avisar | `src/plausibilidade.py` |
| 7 | O PDF leva marca-d'água `DOCUMENTO INTERNO` quando inclui o custo de aquisição. O custo é o preço de venda da Suicatech e o PDF sai da sala (plano §6.3) | `src/componentes/exportador_pdf.py` |
| 8 | `nome_cliente` vive na área de exportação e **não conta** contra o teto de 6 campos | `src/telas/tela1_simulador.py` |

---

## 4. Defeitos encontrados na construção, e o que os pegou

Registro porque cada um destes é uma armadilha que volta.

### 4.1 A tipografia do resultado perdia da cascata do Streamlit

**O mais grave.** O Streamlit estiliza parágrafo de markdown com um seletor de
dois níveis (`[data-testid="stMarkdownContainer"] p`, especificidade 0-1-1). Uma
classe sozinha (`.st-traducao`, 0-1-0) **perde**.

Resultado: a tradução renderizava em **16 px** em vez de 48, e o valor anual em
**16 px** em vez de 36. Os tokens em Python estavam certos, o HTML estava certo,
e **a tela estava errada** — a premissa inteira da leitura a um metro caída.

- **O que pegou:** medição de `getComputedStyle().fontSize` no navegador real.
  Nenhum teste de unidade pegaria.
- **Correção:** `!important` nas propriedades tipográficas das classes próprias.
- **Regressão:** `test_tipografia_do_resultado_vence_a_cascata_do_streamlit`.

### 4.2 O wrapper `<div>` injetado não envolvia as colunas

Os botões de cenário estavam embrulhados em
`st.markdown('<div class="st-cenarios">')`. Um markdown injetado **abre e fecha
a própria div**: as colunas seguintes não ficam dentro dela. O seletor
`.st-cenarios button` nunca casava, os botões ficavam em **~52 px** em vez de 96,
e o protagonista da tela deixava de ser o protagonista.

- **O que pegou:** captura de tela.
- **Correção:** `st.container(key="cenarios")`, que gera `st-key-cenarios` **no
  elemento que envolve os filhos**. É API pública, portanto o gancho de CSS
  menos frágil do app.
- **Regressão:** `test_ganchos_de_css_que_envolvem_filhos_usam_container_key`,
  que proíbe qualquer classe própria como ancestral de um seletor do Streamlit,
  e `test_botoes_de_cenario_tem_96px`.

### 4.3 `novo cliente` não limpava os campos — o vazamento que a §5.2 proíbe

`novo_cliente()` fazia `del st.session_state[chave]`. Isso zera o estado no
servidor mas **não empurra o reset para o navegador**: a tela voltava ao estado
E1 (correto) e os campos de **preço e custo continuavam preenchidos** na cara do
próximo cliente.

É exatamente o vazamento que a §5.2 existe para impedir — a próxima
concessionária vendo o preço da anterior.

- **O que pegou:** verificação no navegador, comparando os valores dos campos
  antes e depois do clique.
- **Correção:** atribuir o valor de limpeza (`None`, `False`, `""`, `0`) em vez
  de apagar a chave. Ver `_LIMPEZA` em `src/estado.py`.
- **Regressão:** `test_novo_cliente_atribui_em_vez_de_apagar`, que proíbe `del`
  dentro de `novo_cliente()` por AST e exige que a tabela de limpeza cubra
  exatamente os campos de sessão.

### 4.4 As Telas 2 e 3 ficaram inalcançáveis

A navegação morava na barra lateral. A §6.1.9 exige ocultar a barra superior do
Streamlit — e fazer isso **leva embora o controle que abre a lateral**. Resultado:
a lateral media 0 px, o botão de abrir não era visível, e **não havia como chegar
nas Telas 2 e 3**.

- **O que pegou:** verificação no navegador, medindo a largura da lateral e a
  visibilidade dos candidatos a botão de abrir.
- **Correção:** a navegação passou para o **cabeçalho da própria página**
  (`app.py::_cabecalho`). Resolve os dois requisitos de uma vez: nenhuma marca do
  framework, nenhuma dependência do chrome dele, e nada roubando largura da
  coluna que o cliente lê. A lateral foi ocultada por completo, para não sobrar
  affordance morto.
- **Regressão:** `test_navegacao_nao_depende_do_chrome_do_streamlit`, que proíbe
  `st.sidebar` em `app.py`.

### 4.5 A linha de ajuda da planilha era lida como dado

A primeira versão de `pipeline/criar_planilha_modelo.py` escrevia a descrição de
cada coluna na **linha 2**. O pipeline leu essa linha como registro e reprovou o
build com 8 falhas.

- **Correção:** a ajuda foi para **comentário de célula** no cabeçalho. Os dados
  começam na linha 2.

### 4.8 Os cartões de entrada renderizavam como pílulas vazias

Mesmo defeito da §4.2, de novo: os quatro cartões da coluna de entradas estavam
embrulhados em `st.markdown('<div class="st-cartao-entrada">')`. A div fecha
sozinha, os campos ficam fora dela, e o "cartão" aparece como uma pílula fina
com a borda vermelha e nada dentro.

- **O que pegou:** captura de tela.
- **Correção:** `st.container(key="entrada_*")`, um por cartão.
- **Lição:** este é o erro que mais reincide nesta stack. **Todo gancho de CSS
  que precisa envolver filhos usa `st-key-*`.** O
  `test_ganchos_de_css_que_envolvem_filhos_usam_container_key` proíbe classe
  própria como ancestral de seletor do Streamlit, mas não pega o caso em que a
  classe é usada isoladamente — a captura de tela é a rede.

### 4.9 O cartão escuro não aplicava e o texto virava branco sobre branco

O fundo escuro estava pendurado em
`.st-key-resultado [data-testid="stVerticalBlockBorderWrapper"]`, mas a cor do
texto estava na classe própria. O seletor do wrapper não pegou, o fundo continuou
branco, e o texto branco ficou **invisível**.

- **Correção:** o cartão é o **próprio** `st.container(key="resultado")`; o
  `st.container(border=True)` interno foi removido.
- **Lição:** quando fundo e texto vêm de seletores diferentes, a falha de um dos
  dois produz texto invisível em vez de um erro. Prefira o mesmo elemento.

### 4.10 Reescrita de arquivo pelo PowerShell corrompeu cinco arquivos de teste

Usei `Get-Content -Raw | Set-Content -Encoding utf8` para renomear campos em
massa. O PowerShell 5.1 leu UTF-8 como cp1252 e reescreveu como UTF-8,
produzindo mojibake (`preÃ§o`, `â€”`) e um BOM. Os testes passaram a falhar por
comparação de string com acento.

- **Correção:** reversão por `encode('cp1252') → decode('utf-8')`, com
  `latin-1` como reserva para os bytes que cp1252 não define.
- **Lição:** **não editar arquivos com acento pelo PowerShell.** Use as
  ferramentas de edição ou Python com `encoding='utf-8'` explícito.

### 4.6 O valor do slider colidia com o rótulo do campo

O Streamlit desenha o valor corrente do slider acima do trilho, na mesma caixa do
rótulo. Sem folga entre os dois, `0%` e `10%` ficavam **sobre** o texto do rótulo
nos sliders de Ajustes avançados.

- **Correção:** `margin-bottom` no rótulo do slider. Padding no container não
  resolve — desce o rótulo junto.

---

## 4.7 O que este histórico ensina sobre esta stack

Quatro dos seis defeitos acima **passaram por 162 testes automatizados** e só
apareceram na medição pelo navegador. Todos os quatro são da camada B:
especificidade de CSS, wrapper que não envolve, estado de widget que não
sincroniza, e chrome do framework que leva a navegação embora.

Consequência prática: **`pytest` verde não é evidência suficiente para subir.**
O checklist manual da §5 abaixo não é burocracia — é a única rede que pega essa
classe de defeito. E é por isso que subir a versão do Streamlit exige refazer o
reteste visual inteiro.

---

## 5. Itens de verificação manual

Não são opinião — só não são comando. `python verificar.py` os lista no fim.

| # | Item | Data | Quem |
|---|---|---|---|
| 1 | **Teste de um metro.** A 1 m do tablet inclinado, sob luz forte: os três números do resultado são lidos sem esforço e o texto da faixa do vendedor **não** é decifrável (§3.2, §12) | | |
| 2 | **Marca do framework.** Em 1180×820 e 1366×1024: nenhum menu hambúrguer, rodapé, "Made with Streamlit" ou botão Deploy (§6.1.9) | | |
| 3 | **Reteste dos itens 🔧** contra `streamlit==1.58.0`. Subir a versão exige refazer (§3, camada B) | | |
| 4 | **Queda de rede.** Wi-fi desligado com o app aberto: o último resultado permanece, o aviso nativo aparece neutralizado no rodapé, **nenhuma caixa vermelha** (§5.14) | | |
| 5 | **Cor da marca.** Ao trocar `#C8102E` pelo vermelho oficial, refazer as três medidas da §3.1.1 e a validação da §5.11.1 (⚠️ K) | | |

**Medições já conferidas no navegador** (Chrome headless, 1180×1100, 11/08/2026).
Estas cobrem o item 3 parcialmente — o que resta dele é olhar a tela ligada.

| Elemento | Exigido | Medido |
|---|---|---|
| Tradução | 48 px | **48 px** ✓ |
| Valor anual | 36 px | **36 px** ✓ |
| Razão tradução ÷ anual | ≥ 1,25 | **1,33** ✓ |
| Botão de cenário | ≥ 96 px | **96 px** ✓ |
| `number_input` | 56 px | **56 px** ✓ |
| Polegar do slider | ≥ 32 px | **32 px** ✓ |
| Faixa do vendedor | 12 px | **12 px** ✓ |
| Marca do framework | ausente | **ausente** ✓ (sem lateral, menu, deploy, toolbar ou rodapé) |

**Comportamento conferido no navegador — 48/48 itens**, cobrindo: estado E0/E1
sem `R$ 0`; T1 completo (R$ 141.480/ano, R$ 11.790/mês, R$ 20.781 de faturamento);
ordem tradução → anual no DOM; T11 (cashback não altera o valor nem o rótulo);
T3 (negativo com sinal, em `rgb(11,11,11)`, sem caixa de alerta); T6 (aviso de
carga na faixa, cálculo não bloqueado); `novo cliente` limpando de fato;
navegação para as Telas 2 e 3 com estado vazio honesto e o marcador da decisão G;
e ausência de "lucro", "ROI", "garantido" e "grátis" em toda a sessão.

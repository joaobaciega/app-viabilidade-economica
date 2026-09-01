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

### D3 — Reordenação de coluna abaixo de 1024 px por CSS *(revogada por D21)*

> **Revogada em 27/08/2026.** D21 acabou com as duas colunas, e sem duas colunas
> não há reordenação a fazer. A regra de CSS e o container `corpo` de que ela
> dependia saíram. O registro abaixo fica para rastreabilidade.


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

### D8 — Mais de seis campos na superfície primária *(ampliada por D21)*

> **Superada em 27/08/2026.** D21 dissolveu o expander "Ajustes avançados" e
> levou os oito campos dele para a superfície primária: são dezessete controles
> visíveis, não nove. A linha "o que continua fora" abaixo **está desatualizada**
> — ver D21.5.


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

### D11 — Aproveitamento traseiro na superfície primária *(mitigação alterada por D21)*

> **Atenção em 27/08/2026.** O item (a) da mitigação abaixo — "ele vive na coluna
> do vendedor, não na coluna que o cliente lê" — **deixou de existir**: D21
> acabou com as duas colunas. E os valores mudaram de 7/10/13 para 5/10/18. O que
> continua de pé está em D21.5.


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

### D18 — Tela 3: as 18 marcas no menu, e "—" no lugar do valor não coletado

| | |
|---|---|
| O que o cliente pediu | "Um menu suspenso bem em evidência com todas as marcas disponíveis… para os modelos que não têm dados, deixe a estrutura pronta e adicione um `-` no lugar" |
| O que o projeto dizia | Duas regras em sentido contrário. Plano §7 Fase 2: *"o app mostra APENAS marcas com dados"* — `carregar_emplacamentos.nomes_de_marca` filtra marca sem modelo, e a Tela 2 nunca lista marca vazia. E `estado_vazio_catalogo.py`: *"não há travessão no lugar de valor"*; a Tela 2 escreve **"não publicado"** por extenso porque *"um travessão pareceria defeito de layout"* |
| O que foi feito | O seletor da Tela 3 lista as **18 marcas** da base `app_precos`, inclusive as 17 sem coleta. O cartão de um modelo sem preço mantém **os rótulos de pé** — `Dianteiro · por par`, `Traseiro · por unidade`, `Veículo completo` — com **"—"** no lugar do número |
| Por que é seguro aqui e não era na Tela 2 | Na Tela 2 o travessão substituiria um número **que existe na fonte**; aqui ele marca um campo **que ainda não foi coletado**, e o rótulo ao lado é a informação: o gerente vê quais campos o produto entrega para a marca dele. A coleta cobre 5 de 80 modelos, então o estado "ainda não coletado" é o caso **dominante**, não a exceção |
| A regra que **não** mudou | Plano §2.4, inteira: **nenhum preço estimado, nenhum preço de vendedor terceiro chamado de original.** "Uma linha inventada destrói as outras 200." Célula vazia vira `null` no pipeline e `None` no leitor, **nunca zero** |
| Consequência declarada | O rodapé de procedência **sempre** diz a cobertura ("5 de 5 modelos de Fiat · 5 de 80 no total"), e a marca sem coleta ganha a frase explícita de que ainda não passou pela loja oficial. O número nunca aparece sozinho quando falta modelo dentro dele — a mesma regra dos totais da Tela 2 |
| Travado por | `testes/test_precos.py`: `test_o_seletor_lista_as_18_marcas_inclusive_as_sem_preco`, `test_marca_sem_coleta_mostra_a_estrutura_com_travessao`, `test_preco_vazio_vira_null_e_nunca_zero`, `test_sem_preco_da_original_nao_ha_economia` |

### D19 — Tela 3: nada além do menu antes da escolha da marca

| | |
|---|---|
| O que o cliente pediu | "Não aparecerá nada além do menu quando nenhuma marca estiver selecionada" |
| O que o projeto fazia | A Tela 2 mostra um **convite** com os nomes das marcas em chips antes da escolha, e a Tela 3 anterior mostrava o bloco "menos código na prateleira" e os campos de refil já na carga |
| O que foi feito | Sem marca escolhida a Tela 3 tem **só o título da seção e o seletor**. Sem convite, sem chips, sem campos de preço, sem o bloco "menos código" |
| A tensão que isso criou | O cabeçalho de `tela3_preco_original.py` fixa que o bloco "menos código na prateleira" fica **no topo, acima dos cartões**, porque é o argumento mais forte do produto (plano §2.5) e não pode virar nota de rodapé |
| Como foi reconciliado | O bloco continua **acima dos cartões** — só passa a aparecer **junto** com eles, depois da escolha. As duas regras valem ao mesmo tempo, e nenhuma foi enfraquecida |
| Travado por | `test_sem_marca_escolhida_nao_aparece_nada_alem_do_menu`, `test_o_menu_abre_vazio_com_as_18_marcas` |

### D20 — Tabela própria, cabeçalho grudado, ritmo de seção e tiles de altura igual

Rodada de acabamento pedida em 27/08/2026, tendo como referência de estrutura
um simulador de juros compostos que o cliente enviou em prints. **Nada de
conteúdo mudou:** nenhum número, nenhum rótulo, nenhum campo, nenhuma ordem de
leitura. São quatro itens de forma, e cada um resolve um defeito que estava na
tela.

#### 1. A tabela deixou de ser `st.dataframe`

| | |
|---|---|
| O que o DESIGN diz | §5.11 exige o **gêmeo em tabela** ("o canal de reserva que substitui o tooltip que a stack não tem") e que ele mostre **as mesmas séries do gráfico**. Não especifica widget |
| O defeito | `st.dataframe` desenha numa `<canvas>`. Nenhuma regra da camada B pega nele, e as duas tabelas do app — a curva na Tela 1 e os modelos na Tela 2 — eram os **únicos objetos da tela** com cabeçalho, tipografia, alinhamento e cantos do framework, no meio de cartões próprios. Era exatamente o que o print de referência faz bem: lá a tabela é um objeto desenhado |
| O que foi feito | `src/componentes/tabela.py` — uma `<table>` de verdade, estilizada na §15.1 de `css.py`: cabeçalho grudado no topo em `--superficie-3`, filete de 1px por linha, número à direita com `tabular-nums`, rolagem em 340px com barra fina |
| O que isso **acrescentou** ao gêmeo | O **marcador da posição atual**. O gráfico desenha um ponto vermelho onde o cliente está; a tabela não tinha equivalente, e um gêmeo que mostra menos que o gráfico deixa de ser gêmeo. Agora a linha atual vem com fundo lavado e filete vermelho à esquerda — e, quando o aproveitamento não cai na grade de 5 em 5 (23%, por exemplo), **o ponto exato entra como linha própria** em vez de marcar o número errado |
| Ganho de acessibilidade | Leitor de tela lê célula por célula com o cabeçalho associado (`scope="col"`), o cliente seleciona e copia, e o conteúdo sobrevive ao print e ao PDF do navegador. Nenhuma das três coisas acontece com uma canvas (§9) |
| O que se perdeu | Ordenação por clique e redimensionamento de coluna. Nenhuma das duas era usada: as duas tabelas são curtas e já saem ordenadas pela grandeza que interessa |
| Vermelho | Só fundo e filete do marcador. **Nenhum número vira vermelho** — §13.1 intacta |
| Custo de reverter | Trocar duas chamadas de `tabela.tabela(...)` por `st.dataframe(...)` e apagar a §15.1 de `css.py` |
| Efeito colateral registrado | `test_render_T4_traseiro_vazio_fica_fora_da_conta` busca valores **proibidos** no texto renderizado. A tabela varre o domínio inteiro do aproveitamento, e um ponto da varredura cai em `R$ 142.380` — o sentinela da derivação proibida do traseiro — com o resultado perfeitamente correto. As duas buscas por valor proibido passaram a rodar sobre o texto **sem a tabela da curva** (`_texto_sem_a_curva`), pelo mesmo motivo que elas já ignoravam a folha de estilo: ali o número é um ponto da curva, não a manchete. As buscas por valor **esperado** continuam sobre a tela inteira |

#### 2. Cabeçalho grudado no topo

| | |
|---|---|
| O defeito | A Tela 1 rola — resultado, premissas, tiles, gráfico, tabela, fórmula, PDF. Com o cabeçalho rolando junto, a navegação entre as três telas saía de alcance justamente quando o vendedor precisa dela: no meio da conversa, para conferir o preço da original |
| O que foi feito | `position: sticky; top: 0` na faixa do cabeçalho |
| Por que não é divergência de conteúdo | Nenhum pixel de altura novo, nenhum elemento novo: é o mesmo cabeçalho de 71px que a §6.1.3 já põe ali. Também não reintroduz chrome do framework — a barra do Streamlit continua oculta (§6.1.9) |
| Reverter | Uma linha em `css.py`, seção 3 |

#### 3. Ritmo das seções da coluna do vendedor

| | |
|---|---|
| O defeito | `.st-secao` tinha 22px acima e 12px abaixo — quase simétrico. Um título simétrico flutua **entre** dois cartões em vez de encabeçar um, e a coluna lia como oito faixas alternadas em vez de quatro grupos com título |
| O que foi feito | 28px acima, 9px abaixo. Proximidade passa a declarar o agrupamento |
| Reverter | Um valor em `css.py`, seção 4 |

#### 4. Tiles de KPI com altura igual

| | |
|---|---|
| O defeito | Os quatro tiles são lidos como **uma linha**, e uma linha em que um cartão é 14px mais alto que o vizinho lê como descuido |
| O que foi feito | `min-height: 96px`, coluna flex, e a nota grudada no rodapé do cartão (`margin-top: auto`) — as notas ficam na mesma altura mesmo quando um valor quebra em duas linhas |
| Reverter | Três declarações em `css.py`, seção 10 |

#### O que **não** foi feito, e por quê

| Ideia do print de referência | Por que ficou fora |
|---|---|
| Prefixo `R$` / `%` colado à esquerda do campo | É o melhor empréstimo do print, e não foi feito porque não há gancho de DOM confiável para separar campo de moeda de campo de quantidade: `st.number_input` não expõe classe nem `data-testid` por tipo, e as alternativas eram um `st.container(key=...)` por campo (chave dinâmica, que o `test_ganchos_de_css_que_envolvem_filhos_usam_container_key` não consegue conferir) ou apagar a borda do `input` na esperança de que um seletor interno do BaseWeb exista — se ele mudar de nome, os campos ficam **sem borda**. Degradação inaceitável na camada B. A unidade continua no rótulo, como a §5.1 exige |
| Dois campos por linha dentro do cartão | Os rótulos deste app são longos **de propósito** (§5.1, P6: rótulo ambíguo é defeito). Em metade da largura, "Preço ao consumidor final, por par (dianteiro)" quebra em quatro linhas — o cartão fica mais alto do que era com um campo por linha |
| Um dos cartões de resultado preenchido de vermelho | No print é o "Valor total final". Aqui seria número financeiro sobre fundo vermelho, a dois passos do que a §13.1 proíbe — e a manchete já tem o cartão escuro, que dá mais contraste (17,9:1) do que qualquer preenchimento |
| Legenda com quadradinhos de cor acima do gráfico | A §5.11 dispensa caixa de legenda de propósito, e as duas linhas já têm **rótulo direto** (D10). Rótulo direto identifica melhor e não gasta o espaço |

### D21 — Modelo calculadora: campos primeiro, resultado por toque

**É a maior divergência do projeto até aqui.** Pedida pelo cliente em 27/08/2026,
tendo como referência um simulador de juros compostos que ele enviou em prints:
a tela abre só com os campos, distribuídos pela largura toda; nada é calculado
durante o preenchimento; um botão **Mostrar Resultado** habilita quando os
obrigatórios estão preenchidos e revela o resultado abaixo, em três números.

Ela contraria regras centrais do DESIGN v5 — não por efeito colateral, mas
porque é isso que foi pedido. Cada choque está declarado abaixo, com o que se
perdeu e o que foi preservado no lugar.

#### 1. O faturamento virou manchete

| | |
|---|---|
| O que o DESIGN diz | §4: "**Faturamento** — Só em linha secundária. **Nunca** como manchete — o resultado é lido em margem (§3.3 do plano)". E §4 exige que **todo** resultado financeiro seja rotulado "margem de contribuição" |
| O que foi feito | Três cartões, nesta ordem: **Faturamento adicional**, **Margem de contribuição adicional**, **Mark up da operação** |
| Consequência que precisa ficar dita | O gráfico plota **margem** adicional anual, e a §5.11 exige que "a curva plota exatamente a mesma grandeza da manchete… **se divergirem, a tela se contradiz na frente do cliente**". A regra passa a valer contra o **segundo** cartão. O título do gráfico continua dizendo qual grandeza está plotada, e a nota abaixo dos cartões diz "Valores anuais · margem de contribuição incremental · ano cheio em regime" |
| Hierarquia | O primeiro cartão é o **escuro** (D6, 17,9:1) e o **maior** (48px contra 36px). Vermelho não foi usado: número financeiro sobre vermelho é a dois passos do que a §13.1 proíbe, e o cartão escuro dá mais contraste que qualquer preenchimento |
| Travado por | `test_T1_ordem_dos_tres_cartoes_e_a_hierarquia` (ordem na fonte + razão 1,25×), `test_render_ordem_dos_tres_cartoes_no_artefato` (ordem no artefato), `test_render_resultado_negativo_sem_vermelho` (nenhuma cor inline nos cartões) |

#### 2. A tradução em escala humana saiu da tela

| | |
|---|---|
| O que o DESIGN diz | §5.5: "**A tradução em escala humana vem antes do valor anual.** … 'R$ 1,2 milhão por ano' é rejeitado pelo cérebro antes de ser avaliado; '3 a cada 10 carros que entram na oficina' é verificado pela intuição em dois segundos". Mais P2, §6.1.2, §6.1.9 ("o valor anual antes da tradução" está entre o que **nunca** aparece) e um item do checklist §12 |
| O que foi feito | A tradução saiu da tela. Continua no **PDF**, no painel "De onde vêm esses números" e na faixa do vendedor |
| O que se perdeu | O argumento que a §5.5 chama de "o requisito mais importante desta tela". O primeiro número que o cliente lê agora é em reais, sem a âncora de intuição antes dele |
| O que foi preservado | A ordem de leitura do **documento** não mudou: no PDF a tradução continua abrindo a seção do resultado, antes do valor anual. `test_pdf_traducao_vem_antes_do_anual` continua verde e não foi tocado |

#### 3. Resultado por toque explícito, e nada antes

| | |
|---|---|
| Onde o DESIGN **apoia** | P11: "**nenhum recálculo que não seja disparado por toque explícito**". §7.1: "um recálculo por toque" |
| Onde o DESIGN **contraria** | §5.11: "o cliente vê o intervalo completo **sem interagir**". §6.1.6: o estado E3 dispara por **preenchimento**, não por clique. §7.3: "o vazio desta tela **não é uma falha, é a abertura da conversa** … trate o texto de estado vazio como roteiro de pitch" |
| O que se perdeu | **O roteiro de pitch do estado vazio.** "Quantas passagens por mês esta oficina recebe?" em 48px dentro do cartão de resultado deixou de existir; o vazio da tela agora é a própria área de campos |
| Obrigatórios | passagens, palhetas vendidas/mês, preço da original, **custo da original**, preço e custo do dianteiro. O custo da original passou de opcional a obrigatório porque o mark up da operação inteira precisa dele — e, de lambuja, o rótulo do resultado parou de alternar entre "incremental" e "do refil" |
| O traseiro continua OPCIONAL | Vazio ali significa "fora da conta" e é estado legítimo (§5.13). Exigi-lo travaria o vendedor quando o traseiro ainda não foi fechado, e mataria os casos T4 e T3b |
| Nada bloqueia o CÁLCULO | §6.1.8: "um bloqueio na frente do cliente encerra a cena". O botão gateia a **exibição**; a plausibilidade continua avisando só na faixa do vendedor, sem impedir número nenhum. `test_render_aviso_de_plausibilidade_so_na_faixa` cobre isso |
| Apagar um obrigatório | Esconde o resultado e desabilita o botão de novo. Sem isso, a tela ficaria com um número que a entrada atual não produz mais — pior do que não mostrar nada |
| Botão desabilitado, sem cor semântica | Perde o preenchimento e ganha traço tracejado; o que falta é dito em texto discreto ("Falta preencher: …"). Sem `st.warning` (proibido) e sem vocabulário de alerta (§4) |
| Caminho de volta | "Esconder resultado" volta à tela de campos **sem apagar nada** — é o oposto de `novo cliente`. Recomeça o pitch com o cenário montado |
| Travado por | `test_render_estado_inicial_abre_so_com_os_campos`, `test_render_botao_habilita_quando_os_obrigatorios_estao_preenchidos`, `test_render_resultado_so_aparece_depois_do_toque`, `test_render_resultado_esconde_ao_apagar_um_obrigatorio`, `test_render_esconder_resultado_nao_apaga_campo` |

#### 4. Fim das duas colunas — **D3 fica revogada**

| | |
|---|---|
| O que o DESIGN diz | §3.3: "duas colunas via `st.columns([5, 7])` — **coluna esquerda (5/12)**, entradas, é o lado do vendedor / **coluna direita (7/12)**, cenário e resultado, é o lado que o cliente lê" |
| O que foi feito | Uma coluna de campos em largura total, com 2 a 4 campos por linha dentro de cada cartão, e o resultado abaixo de tudo |
| O que morre com isso | **D3 inteira** (a reordenação de coluna por CSS abaixo de 1024px): não há mais o que reordenar. O container `corpo` e a regra de CSS dele saíram |
| O que precisa ser refeito | O argumento de **D6**: o cartão escuro era "~35% da coluna direita, cercado de superfície clara". Agora é 1/3 da largura de uma linha de três cartões — a área escura ficou **menor**, então o argumento contra o reflexo continua de pé, mas por outro motivo |

#### 5. Os avançados na superfície primária — **D8 fica reescrita**

| | |
|---|---|
| O que o DESIGN diz | §5.10: "Segurar o limite de campos editáveis visíveis. A planilha original tem ~30 células; num tablet, na frente do cliente, isso é morte." §6.1.4: "**exatamente seis** campos primários", com uma tabela do que ficou em Ajustes avançados "e por que cada um não merece o espaço" — e o aviso: "**sem esta tabela, o próximo a editar o documento simplesmente adiciona os campos de volta**" |
| O que foi feito | O expander deixou de existir. Consultores, dias úteis e a grade 2×3 de cashback estão na superfície primária. A Tela 1 passou de nove para dezessete controles visíveis |
| O que fica falso em D8 | A linha "o que continua fora — consultores, dias úteis, substituição, aproveitamento traseiro, comissão, imposto e cashback seguem em Ajustes avançados". Só substituição, comissão e imposto continuam fora, e por não existirem no modelo (D15, D16) |
| O que da §5.10 **não** caiu | "Nenhum campo altera o resultado sem que a faixa de premissas reflita a mudança" — essa era a regra que importava, e ela continua valendo. A faixa de premissas subiu para o fim da área de campos e aparece **sempre**, antes de existir qualquer número |
| Efeito em D11 | A mitigação declarada era "**(a)** ele vive na coluna do vendedor, não na coluna que o cliente lê". Com a coluna do vendedor abolida, o item (a) deixou de existir. Continuam de pé: os atalhos do traseiro são de 44px e não de 96, e o aproveitamento traseiro segue junto do preço e do custo da própria categoria, longe dos presets |
| Correção de acessibilidade feita de passagem | Os seis campos de cashback tinham rótulo invisível "Dianteiro 0", "Dianteiro 1"… — índice de chave, não destinatário. Passaram a "Dianteiro · Consultor" (§9.6) |

#### 6. Presets 10/40/70 e 5/10/18, os seis declarados medidos

| | |
|---|---|
| O que foi feito | Dianteiro **10% / 40% / 70%** (era 20/30/40) e traseiro **5% / 10% / 18%** (era 7/10/13). Os seis declaram `carteira_medida` |
| Quem afirmou | O cliente, em 27/08/2026, ao ser perguntado explicitamente: a legenda "Aproveitamento dianteiro medido em 15+ concessionárias da carteira Suicatech — não é estimativa" foi **mantida a pedido dele**, com a afirmação de que os novos números são dado medido |
| O que o DESIGN e o plano registram | §10-H: "Derivados do dianteiro pela mesma proporção (0,67× e 1,33×) e **obrigatoriamente marcados `≈ derivado`**, nunca `◆ carteira`. **Só a linha realista (10%) é medida**". O plano §3.2 documenta 20/30/40 e 7/10/13, e o **risco nº 1** é "conversão do traseiro aplicada por analogia ao dianteiro… a projeção infla na metade nunca medida — e o erro só aparece no mês 3 do cliente" |
| O que mudou na tela | A derivação proporcional deixou de existir, e com ela a marca `≈ derivado` e o texto "não medidos". `LEGENDA_PRESETS_TRASEIRO` passou a afirmar medição nas três faixas |
| O que continua montado | O mecanismo de procedência (`Origem`, `marcador_procedencia`, a faixa de premissas). No dia em que um preset voltar a ser derivado, basta trocar o campo e a tela volta a marcá-lo — `test_decisao_H_todo_preset_declara_procedencia_coerente` reprova se um preset virar `derivado` sem a legenda mudar junto |
| **Bloqueio técnico que isso causou** | 70% não caberia em `SLIDER_DOMINIO = (0, 60)`, e a validação **V5** levanta `ParametroInvalido` no import: **o app não subia**. O domínio subiu para **(0, 80)**, que é o mesmo valor do eixo X do gráfico (§5.4). `casos.json` T10 acompanhou |
| Testes afetados | `test_decisao_H_derivacao_e_proporcional` foi **removido** (a proporção deixou de ser a regra) e `test_decisao_H_traseiro_extremos_sao_derivados` foi reescrito |

#### 7. Mark up da operação — vocabulário novo

| | |
|---|---|
| A conta | `(faturamento do refil + faturamento da original) ÷ (CMV do refil + CMV da original)`, mensal, adimensional. Exibido como `2,1×` |
| Por que a operação inteira, e não só o refil | Decisão do cliente. É o mark up da operação que ele quer ver, não o do produto isolado |
| Por que CMV é campo explícito em `Resultado` | Para o painel de fórmula poder mostrar a conta. Deduzir custo por `faturamento − margem` obrigaria o leitor a fazer a subtração de cabeça, e a §5.8 existe para o contrário |
| Quando **não** aparece | Falta qualquer parcela, ou custo total zero → `None`, e o cartão declara o motivo. Um mark up de 1,0 significaria "vende ao preço de custo", que é uma afirmação que ninguém fez |
| O que a §4 exige e como foi atendido | "Todo resultado financeiro é rotulado margem de contribuição". Mark up **não é** margem: o cartão diz `faturamento ÷ custo` embaixo do número, e o painel de fórmula diz "é adimensional — não é margem e não é percentual: é quantas vezes o preço cobre o custo" |
| ⚠️ **Risco que fica em aberto** | Mark up na tela **entrega o custo de aquisição por inferência**: com o faturamento no cartão ao lado, uma divisão devolve o custo. O projeto trata custo como dado sensível — o PDF ganha marca d'água "DOCUMENTO INTERNO" quando o inclui, e o plano lista isso como risco 10. **Um número na tela do cliente não tem marca d'água.** Registrado aqui porque a decisão de exibir foi do cliente, e ela não é reversível depois da reunião |

#### 8. Preço tabelado, não "caso a caso"

| | |
|---|---|
| O que o cliente pediu | "tirar todas as menções que a negociação é caso a caso. falamos pro cliente que o preço é tabelado" |
| Onde estava | `tela1_simulador.py` (título da seção e legenda do traseiro), `bloco_resultado.py` (estado vazio, que saiu junto), `exportador_pdf.py` (seção de preço e custo) e `campo_sensivel.py` (`LEGENDA_BLOCO`, módulo órfão) |
| Nova redação | "Preço e custo vêm da tabela Suicatech vigente." O campo continua abrindo em branco, mas o motivo declarado deixa de ser negociação |
| O que **não** mudou | Tela 3: "Seu preço nesta negociação" continua — ali "negociação" é o preço que a **concessionária** cobra pela palheta original e o escopo da sessão, não o preço tabelado da Suicatech |
| Travado por | `test_render_legenda_do_campo_vazio_existe`, que agora proíbe "caso a caso" na tela |

#### 9. Tiles de KPI removidos

Eram acréscimo de D5 ("os números `ƒ calculado` que já existiam espalhados como
legenda, reunidos numa grade legível"). O módulo `componentes/tiles_kpi.py` e as
regras `st-key-kpis` e `st-kpi` saíram. As classes `.st-kpi-rotulo` e
`.st-kpi-valor` **ficaram**: as Telas 2 e 3 e `cartao_preco_palheta.py` as usam
sobre superfície clara.

#### 10. Defeito de contraste corrigido de passagem

`_bloco_menos_codigo` da Tela 3 usava `.st-mensal` — `color: var(--tinta-clara)`,
branco — dentro de um `st.container(border=True)`, que é superfície branca. O
texto "Palheta original: dezenas de códigos… cobrem 97% do mercado" era
**branco sobre branco**, invisível; o bloco renderizava só a legenda. A docstring
do próprio arquivo registrava a classe como "herdada da versão anterior desta
tela e mantido como estava". Trocado por `.st-kpi-valor`, que é a classe que a
mesma docstring manda usar. É o mesmo defeito que a §9 de `css.py` registra no
cartão de resultado.

#### O que ainda precisa de olho humano

1. **O teste de um metro.** O item 1 do checklist manual fala de "os três números
   do resultado" — que eram tradução/anual/mensal e agora são faturamento/margem/
   mark up. Precisa ser refeito no tablet. `pytest` verde não basta: a §4.7 deste
   documento registra que quatro dos seis defeitos desta construção passaram por
   162 testes e só apareceram na medição pelo navegador.
2. **Densidade.** Dezessete controles a 56px mais os presets de 96px na largura de
   um tablet paisagem. Se estourar, o caminho é agrupar em mais cartões — nunca
   reduzir altura de alvo (§3.4 é piso, não sugestão).
3. **O mark up expondo o custo** (item 7 acima).

### D22 — Campos compactados para 44 px, e o celular como alvo real

Pedido do cliente em 27/08/2026, logo depois de D21: *"eu achei os campos muito
grandes, não precisa ser assim. A parte de preenchimento está ocupando um espaço
muito grande na tela… igual no exemplo do site da calculadora"*, com a ressalva
de que *"o app tem que ter uma boa portabilidade para celulares"*.

As duas coisas na mesma frase é o que define o limite: compactar até o piso de
alvo de toque, e parar ali.

#### O que mudou

| | Antes | Agora |
|---|---|---|
| Altura de campo (`ALTURA_CAMPO`) | 56 px | **44 px** |
| Texto do campo (`T_CAMPO`) | 20 px | **17 px** |
| Rótulo do campo (`T_ROTULO`) | 17 px | **15 px** |
| Margem do rótulo | ~8 px | 2 px |
| Empilhamento dentro dos cartões | 0,6 rem | 0,3 rem |
| Padding do cartão de campo | 12/16/14 px | 9/14/10 px |
| Margem entre cartões | 14 px | 9 px |
| Título de seção | 28 px acima, 9 abaixo | 17 acima, 6 abaixo |
| Chip do total derivado | margem 6/14, padding 4/11 | margem 3/4, padding 2/9 |

Estimativa: ~92 px por campo contra ~70 px, e algo entre 300 e 350 px menos na
área de preenchimento — perto de um quarto dela. **É estimativa, não medição:**
a altura real depende de quantos rótulos quebram em duas linhas na largura de
cada coluna, e isso só o navegador responde.

#### Onde a compactação PARA, e por quê

| | |
|---|---|
| O que o DESIGN diz | §3.4: "**Mínimo global: 56px** — acima dos 44px habituais, deliberadamente" |
| O que foi feito | 44 px — os "44 habituais" que a §3.4 cita para dizer que ficava acima deles |
| Por que não menos | 44×44 CSS px é o piso de alvo de toque do **WCAG 2.5.5** e das diretrizes de **iOS e Android**. Abaixo disso o dedo erra o campo. E o mesmo pedido trouxe "boa portabilidade para celulares", onde esse piso vale mais, não menos |
| O que **não** foi compactado | Os presets de cenário (96 px, 72 no celular) — são o protagonista da §5.3 e o maior alvo da tela; o polegar do slider (32 px, faixa de 48); o gráfico (300 px — reduzi-lo torna a curva ilegível, e é melhor rolar) |
| Travado por | `test_alvos_de_toque_minimos`, reescrito: ele afirma `ALTURA_CAMPO >= 44`, exige que o campo use o token (um lugar só para mexer) e proíbe qualquer media query de rebaixar o token no celular |

#### Celular (≤ 767 px) — o que passou a existir

Antes deste item o único tratamento de celular era reduzir dois tokens de
tipografia. Agora:

- **Padding da página** cai de 28 px para 14 px de cada lado — 28 px custam 14%
  da largura de um aparelho de 390 px.
- **O cabeçalho empilha**: marca em cima, navegação embaixo, pílulas podendo
  quebrar em duas linhas. Lado a lado a 390 px o logo e as três pílulas não
  cabem, e a navegação seria cortada — ela é o **único** caminho para as Telas 2
  e 3, porque a barra lateral do Streamlit está oculta (§6.1.9).
- **A grade de cashback continua em linha** em qualquer largura. Empilhada, o
  cabeçalho de coluna ("Consultor", "Gerente", "Marketing") deixa de encabeçar
  nada e os seis campos ficam sem rótulo visível: a grade viraria seis caixas
  anônimas. A 390 px ela fica apertada — quatro colunas de ~85 px — e isso é o
  compromisso escolhido.
- **A reserva de 118 px à direita na faixa do vendedor** para o botão `novo
  cliente` não cobrir o texto de procedência (§5.9).
- **Tipografia do cliente** um passo abaixo, incluindo `--t-mensal` a 20 px. O
  piso de 22 px da §3.2 foi derivado de "legível a 100 cm, sob luz forte" — a
  cena do tablet sobre a mesa. Um celular é lido a 30–40 cm, e a mesma conta
  que pedia 22 px a um metro pede menos da metade a 40 cm. A folha já fazia
  isso com a tradução e o valor anual desde a §8 original.

#### O que precisa de olho humano

O item 3 do checklist manual (reteste visual dos itens 🔧) precisa rodar em três
larguras, não em uma: **1366×1024**, **1180×820** e **390×844**. O que eu não
consigo verificar daqui é quantos rótulos quebram em duas linhas em cada
largura — é isso que decide se a compactação entregou o que promete.

### D23 — O cashback deixou de ser grade, e o botão de PDF virou um botão

Pedido do cliente em 27/08/2026: *"refaça a parte de cashback da tela 1 para
ficar melhor de preencher no celular"* e *"faça a funcionalidade de exportar pra
PDF ser funcional"*.

#### O cashback — o que a grade cobrava, e por quê

D16 desenhou o bloco como **grade 2 × 3**: uma coluna com o nome da categoria
mais uma coluna por destinatário, os seis campos com o rótulo colapsado
(`label_visibility="collapsed"`) e o cabeçalho de coluna nomeando cada um.

Isso amarrava o layout de um jeito que só aparece no celular: **empilhar a grade
apaga o cabeçalho de quem ele encabeça**, e os seis campos ficam anônimos. D22 já
tinha topado com isso e escolheu o outro lado — manter a grade em linha em
qualquer largura — registrando o preço em texto:

> "A 390 px ela fica apertada — quatro colunas de ~85 px — e isso é o
> compromisso escolhido."

Um campo de moeda de **85 px**, com dedo, é o que o cliente pediu para acabar.

#### O que mudou

| | Antes (D16/D22) | Agora |
|---|---|---|
| Forma | grade 2 × 3, cabeçalho de coluna | dois grupos, um por categoria |
| Colunas | 4 (categoria + 3 destinatários) | **3** (um por destinatário) |
| Rótulo do campo | colapsado; quem nomeava era o cabeçalho | **visível**, `Consultor · dianteiro` |
| Título da categoria | primeira coluna da linha | linha acima dos três campos, em `.st-rotulo-categoria` — a mesma do bloco do refil |
| Abaixo de 768 px | em linha, campos de ~85 px | **empilhado**, campo de largura inteira (~360 px) |
| Conferência | só no bloco de resultado | **chip de subtotal** por categoria, `→ R$ 15,00 no total, por par vendido` |

O rótulo diz o destinatário **e a categoria**, e não só o destinatário: quem
chega no campo por leitor de tela não lê o título da linha de cima ao tabular, e
"Consultor" apareceria duas vezes idêntico (§9.6). A unidade fica de fora dele
porque já está no título logo acima — e vem de `Categoria.unidade`, declarada
(§5.13 / V3), nunca de um literal no componente.

**O custo assumido:** "Consultor · Gerente · Marketing" aparece duas vezes, uma
por categoria, em vez de uma vez no cabeçalho — ~21 px por rótulo. É o que
compra o campo de ~360 px. No celular o bloco fica mais alto: seis campos, um
por linha. Rolar é barato; errar o campo com o dedo, não.

O subtotal existe pela cena: empilhados, o primeiro campo sai da tela enquanto o
último é preenchido, e o chip é o que deixa conferir o combinado sem rolar de
volta. Ele **não** é, e não pode virar, o custo do programa para a Suicatech
(§6.1.9) — é o valor por venda que acabou de ser digitado, somado.

*Efeito colateral:* o parâmetro `oculto` de `campo_moeda` **deixou de existir**.
Ele só servia à grade, e um rótulo que só vive no cabeçalho é justamente o que
não sobrevive ao empilhamento.

#### O PDF — o documento estava certo, o botão é que não

`test_pdf.py` cobria o documento desde sempre, chamando `gerar_pdf()` direto, e
os doze testes passavam. **Nenhum teste olhava para o botão** — a única peça
entre o documento e o cliente. Ver §4.11.

| | Antes | Agora |
|---|---|---|
| Rótulo | `f"{svg('exportar')} Baixar PDF do cenário"` — o Streamlit escapa HTML em rótulo de botão, e o `<span class="st-icone"><svg …>` saía **impresso em cima do botão** | texto puro; o ícone vai numa linha de markdown acima (`.st-exportar-nota`) |
| Visual | o único controle da Tela 1 com o visual **nativo** do Streamlit | vermelho de marca, 52 px, `st-key-exportar` (§3.4) |
| Nome do arquivo | `c if c.isalnum() else "-"` deixava passar **acento** (`"á".isalnum()` é `True`) e traço repetido (`auto-center-----zona-sul`) | `nome_do_arquivo()`, ASCII, traços colapsados, testada |
| Falha ao montar | exceção derrubava o **resultado inteiro**, já na tela | linha discreta dizendo o que fazer, sem componente de alerta (§5.9, §7.4) |

O documento continua sendo montado **a cada rerun**, e não atrás de um botão
"gerar": são ~19 ms por PDF, contra um toque a mais na frente do cliente e um
estado a mais para dessincronizar. O risco real de um fluxo de dois passos é o
vendedor baixar o PDF do cenário **anterior**. A conta só roda com o resultado
visível — a Tela 1 não chama o bloco antes do toque.

**Travado por:** `test_render_cashback_todo_campo_tem_rotulo_proprio_visivel`,
`test_render_cashback_subtotal_por_categoria`,
`test_render_cashback_nao_depende_de_cabecalho_de_coluna` (que lê o CSS e exige
o empilhamento abaixo de 768 px),
`test_render_exportar_pdf_o_botao_entrega_o_documento`,
`test_render_exportar_pdf_so_com_o_resultado_na_tela`,
`test_pdf_nome_do_arquivo_*` e `test_venda_da_unidade_concorda_com_a_unidade_declarada`.

### D24 — O PDF virou documento visual, sem virar folheto

Pedido do cliente em 27/08/2026: *"o PDF tem que ser mais visual. Use os cards
de KPI, gráficos, faça cenários. Deve ser algo que o cliente bata o olho e fique
evidente que é um bom negócio."*

O documento era uma lista de `rótulo … valor` em duas colunas, da primeira linha
à última. Passou a ter **duas páginas com papéis distintos**:

| | Conteúdo | Para quê |
|---|---|---|
| **Página 1** | faixa escura de abertura; cartões de apoio; barras **hoje × com o refil**; os **três cenários** medidos; a linha de cashback | a leitura de relance |
| **Página 2** | a **curva de sensibilidade** inteira com marcador, as premissas, preço e custo de tabela (só em documento interno) e o que ainda não foi decidido | a auditoria |

#### A tensão que este item resolve, e como

"Bata o olho e fique evidente que é um bom negócio" é um **pedido de persuasão**,
e a §4 é dura a respeito: o app não promete, e a §12 reprova "ROI", "retorno
garantido" e "estimativa" ao lado de número medido. A leitura de relance ficou
mais forte **pelo desenho** — hierarquia, contraste, uma grandeza por elemento —
e não por adjetivo. Nenhuma palavra de venda entrou; `test_pdf_cenarios_nao_prometem`
varre o documento inteiro atrás delas.

O que sustenta a decisão de que isso não vira folheto:

- **O cenário PESSIMISTA entra na página 1, do mesmo tamanho dos outros dois.**
  Um documento que mostrasse só o cenário favorável seria material de venda; a
  faixa inteira é o que deixa o gerente escolher em qual acreditar. Com o T1, a
  faixa vai de R$ 50.400 a R$ 319.752 — e o pessimista fica impresso.
- **As barras são empilhadas, não justapostas.** Duas barras soltas convidam a
  ler "de X para Y" como *substituição*, e substituição é exatamente o que a
  premissa `CANIBALIZACAO_MODELADA = False` **não** afirma. A base repetida diz,
  no desenho, que nada foi trocado — e o parágrafo abaixo repete em palavras.
- **Nenhum número de resultado é vermelho** (§13.1). O vermelho é marca de
  gráfico: o segmento da barra, o marcador da curva e a anotação do vão — os
  mesmos usos que `grafico_sensibilidade.py` já faz na tela. Travado por
  `test_pdf_nenhum_numero_de_resultado_em_vermelho`, que lê a função `kpi` por
  AST em vez de procurar a cor no arquivo (onde ela é legítima).
- **Margem negativa continua saindo.** Com custo acima do preço, a segunda barra
  fica **mais baixa** que a primeira e o vão que falta aparece em contorno
  tracejado, com o valor em tinta primária e o sinal — nunca em vermelho, nunca
  escondido. O plano §1.1 avisa que isso é possível.
- **Sem valor anual não existe página 1.** O documento abre dizendo o que falta,
  e não com cartões de R$ 0 (P9, §6.1.9).

#### Desenhado à mão, sem matplotlib

Cartões, barras e curva são retângulo e linha vetoriais do próprio `fpdf2`, num
módulo novo — `src/componentes/pdf_visual.py`. Três razões, nesta ordem:

1. `requirements.txt` instala **exatamente** o que o app importa, e
   `test_runtime_nao_carrega_dependencia_de_desenvolvimento` reprova o contrário.
   matplotlib são ~30 MB no Community Cloud, que hiberna após 12 h e precisa
   **acordar** antes de o cliente olhar a tela (§9, risco 6).
2. Gráfico rasterizado em A4 ou serrilha na impressão ou pesa. Vetor imprime
   nítido.
3. A paleta vem de `src/css.py` — não há **nenhuma** cor definida no módulo
   novo. O PDF e a tela são a mesma marca, e o documento sai da sala junto com a
   lembrança da tela.

#### Os cinco defeitos que só a renderização mostrou

`pytest` continuou verde durante todos eles. São a mesma lição da §4.7, agora na
camada do papel — foram encontrados rasterizando o PDF e **olhando**.

| | O que aparecia | Correção |
|---|---|---|
| Goteira do eixo Y | a curva entrava por baixo dos rótulos "R$ 200 mil" e o "0%" caía fora do eixo desenhado | o plot começa **depois** da goteira, não na margem |
| Um tick só | numa faixa de R$ 45 mil a R$ 390 mil o eixo saía com **um** rótulo — sem um segundo tick não há escala, só um número solto | o passo é escolhido pela **contagem** que produz, e não arredondando a largura do intervalo para cima |
| Rótulos iguais | numa faixa estreita, `R$ 1.000 / 1.050 / 1.100` viravam três ticks lendo "R$ 1 mil" | quando a forma curta repete, o eixo cai para o número inteiro |
| Rótulo riscado | o valor do marcador saía cortado pela própria curva, que sobe justamente ali | retângulo da cor da superfície atrás do rótulo |
| Valor cortado | a decisão G saía "bloco de investimento **ausent**" — `cell` de largura 0 não quebra | `linha()` quebra o valor em `multi_cell`, com `align="L"` explícito (o default do fpdf2 é **justificado**) |

#### Latin-1: transcrever, não apagar

As fontes núcleo do `fpdf2` são Latin-1, e `—`, `→`, `−`, `≈` e `◆` não cabem
nela. O `NFKD` + `ignore` anterior os **apagava**: o título do próprio documento
saía `"Simulação de viabilidade  refil de palhetas"`, com o buraco no lugar do
travessão — e passou despercebido porque as buscas dos testes eram por trechos
curtos. Agora há uma tabela de transcrição (`—` → `-`, `→` → `->`, `−` → `-`),
aplicada **antes** do teste de codificação. `→` vira `->` e não `>` de propósito:
sozinho ao lado de um número, `>` lê como "maior que", e a faixa de manchete tem
exatamente essa vizinhança.

#### Marca-d'água em todas as páginas

Ela era desenhada **uma vez**, depois do `add_page`. Com duas páginas, um
documento interno sairia com a segunda limpa — justamente a que carrega preço e
custo de tabela (plano §6.3). Passou para o `header()`, que roda em toda página,
e vem **primeiro** nele: PDF não tem camadas, só ordem de escrita, e é isso que
a deixa atrás do conteúdo.

**Travado por:** `test_pdf_duas_paginas_com_resultado_e_uma_sem`,
`test_pdf_traz_os_tres_cenarios_medidos`, `test_pdf_cenarios_nao_prometem`,
`test_pdf_marca_dagua_em_TODAS_as_paginas`,
`test_pdf_transcreve_o_travessao_em_vez_de_apagar`,
`test_pdf_valor_longo_nao_e_cortado`, `test_pdf_eixo_da_curva_sempre_tem_escala`,
`test_pdf_rotulos_do_eixo_nunca_se_repetem`,
`test_pdf_nenhum_numero_de_resultado_em_vermelho`,
`test_pdf_incremental_negativo_sai_com_sinal_e_sem_promessa`,
`test_T14_moeda_curta_espelha_o_eixo_da_tela` e
`test_T14_abreviacao_de_moeda_e_so_para_eixo`.

### D29 — O gráfico de barras maior, e o PDF endereçado ao cliente

Dois pedidos do cliente em 27/08/2026, com uma captura da tela anexada:
*"deixe esse gráfico maior, para ficar mais evidente o aumento que a nossa
solução traz"* e *"deixe o PDF personalizado também, mostrando no topo o nome do
cliente (atualmente ele pede o nome do cliente, mas não aparece em nenhum lugar
essa informação)"*.

#### 1. As barras

| | Antes | Agora |
|---|---|---|
| Altura do plot | 210 px | **340 px** (220 px no celular) |
| Largura da barra | 150 px | **190 px** |
| Valor da barra | 22 px | **36 px** (`--t-anual`) |
| Rótulo do vão | 22 px | **36 px**, régua de 3 px |
| No PDF | 60 mm | **66 mm** |

É a peça cujo **tamanho carrega o argumento**: a razão entre as duas alturas é o
que se lê antes de qualquer número, e num plot baixo uma base pequena vira um
risco de 10 px que não se compara com nada. A altura mora num token
(`--altura-barras`) porque o plot, a régua do vão e o espaçador do delta têm de
ter a **mesma** altura — se divergirem, o rótulo descola da barra que mede.

**A captura mostrou um defeito de paridade que nenhum teste pegava.** O valor
`R$ 99.000` aparecia no **topo da coluna**, e não acima da barra dele: com a base
em 4,8% do plot, o rótulo ficava a ~300 px do risco que nomeava. No PDF ele
sempre esteve colado (`base_y - altura - faixa_valor`); na tela, não.

- **Correção:** uma `.st-barra-pilha` com a altura do valor, e o rótulo
  posicionado sobre ela (`bottom: 100%`). Isso criou **dois sistemas de
  porcentagem**, e confundi-los desalinha o desenho sem quebrar nada:

  | | Fração de quê | Manda em |
  |---|---|---|
  | `pct_*` | o **plot** (altura fixa da coluna) | altura de cada pilha, as duas faixas da régua do vão |
  | `dentro_*` | a **pilha** | os segmentos empilhados |

- **Travado por:** `test_render_barras_a_geometria_fecha`, que confere a
  aritmética no HTML: a barra mais alta ocupa o plot inteiro, os segmentos
  fecham 100% da pilha, **a base repetida tem a mesma altura nas duas barras**
  (que é o que a nota afirma em palavras) e a régua do vão mede exatamente o
  segmento vermelho.

#### 2. O nome do cliente

Ele **já entrava** no PDF — dentro da linha de metadados, em 8,5 pt cinza, entre
a marca e a data: `Concessionária Exemplo · Suicatech · Intrace AG · gerado em…`.
Tecnicamente presente; na prática invisível, e o cliente relatou exatamente isso.

```
[logo]
Concessionária Exemplo                          <- 17 pt, tinta primária
Simulação de viabilidade — refil de palhetas    <- 10,5 pt, subtítulo
Suicatech · Intrace AG · gerado em 01/09/2026   <- 8,5 pt, discreta
────────────────────────────────────────────── filete de marca
```

Um documento personalizado é **endereçado a alguém**, e quem ele é vem antes do
que ele é. Sem nome, o título sobe para o lugar do nome e nada mais muda — o
`if` existe para isso, não para deixar um espaço vazio.

O nome **repete em todas as páginas**, porque o `header` roda em cada uma: uma
folha solta de um documento personalizado tem de dizer de quem ela é.

**Travado por:** `test_pdf_o_nome_do_cliente_ABRE_o_documento` (vem antes do
título, não é pedaço da linha de metadados, e aparece uma vez por página) e
`test_pdf_sem_nome_do_cliente_abre_pelo_titulo`.

#### O custo em altura, e o que foi cedido

O cabeçalho ficou ~6 mm mais alto **em cada página**, e as barras +6 mm. Isso
levou o documento a 3 páginas, com `decisão L` sozinha na última. A curva da
página 2 desceu de 54 mm para **48 mm** e o documento voltou a duas.

Não foi o conteúdo que cedeu: a curva continua com o domínio inteiro, os
mesmos ticks e o mesmo marcador. Cedeu a folga vertical dela, que era a única
peça da página 2 com folga a ceder.

### D28 — A tela de resultados e o PDF passaram a ser a mesma coisa

Pedido do cliente em 27/08/2026: *"ajuste a tela de resultados… ela deve ser
exatamente igual o que aparece no PDF. Com todos os gráficos, tabelas e KPIs.
Exatamente igual."*

Entre D24 e D27 o documento ganhou manchete dupla, barras, cenários, curva
vetorial, premissas e decisões impressas. **A tela ficou com três cartões e um
gráfico.** O PDF virou o produto e a tela, o rascunho dele.

#### O que a tela ganhou

| | Antes | Agora |
|---|---|---|
| Abertura | três cartões (faturamento, margem, mark up) | **manchete escura** com os dois números lado a lado, no maior corpo da tela |
| Apoio | — | três cartões: mark up, tradução, nova margem com refil |
| Comparativo anual | — | **barras hoje × com o refil**, empilhadas |
| Cenários | — | **as três faixas medidas**, com a simulada destacada |
| Curva | gráfico com título próprio | mesmo gráfico, com o título e o subtítulo **da montagem** |
| Premissas | só a faixa de premissas | **a seção inteira**, como no papel |
| Preço e custo de tabela | só os campos de entrada | a seção, quando há custo informado |
| Decisões em aberto | só o marcador ⚠️ | **a seção inteira** |

#### Como "exatamente igual" virou verificável

Escrever a mesma coisa em dois arquivos não é paridade — é duas chances de
divergir. A decisão saiu dos dois desenhos e foi para um lugar só:

```
src/apresentacao.py          <- decide QUAIS blocos, EM QUE ordem,
    montar(entradas, r)         com QUE rótulo e QUE número já formatado
        │
        ├── componentes/bloco_resultado.py    desenha em HTML/CSS
        └── componentes/exportador_pdf.py     desenha em vetor
```

`apresentacao.py` é **puro** — não importa streamlit nem fpdf, nem
indiretamente —, e a ordem de leitura é literalmente a ordem dos campos do
dataclass `Apresentacao`. Reordenar lá reordena os dois desenhos de uma vez.

`test_paridade_tela_e_pdf` percorre tudo que a montagem produz e exige que cada
texto apareça **nos dois** desenhos, em quatro cenários (completo, com cashback,
margem negativa, sem custo da original). Ele chama o desenhador da tela com um
`st` de mentira e extrai o texto do PDF de verdade: comparar o modelo consigo
mesmo não provaria nada. `test_paridade_cobre_os_blocos_que_importam` garante
que o caso base exercita todos os blocos — sem ele, a rede continuaria verde se
a montagem parasse de produzir barras ou cenários.

#### O que a tela tem a mais, e por quê

Três peças, todas depois do resultado: o **gêmeo em tabela** da curva
(obrigatório pela §5.11 e pela §9 — substitui o tooltip, que não existe em
tablet e muito menos no papel), o **painel de fórmula** e a **área de
exportação**. Nenhuma é resultado; são ferramenta de operação.

#### O que isto revogou

| | |
|---|---|
| **D21.2** *(parcialmente)* | "A tradução em escala humana saiu da tela." Ela **volta** — no mesmo cartão de apoio em que o PDF a mostra, e não como manchete de 48 px. O que D21.2 decidiu sobre ela **não abrir** o resultado continua de pé |
| `test_render_ordem_dos_tres_cartoes_no_artefato` | Substituído por `test_render_ordem_do_resultado_no_artefato`, que verifica a sequência **inteira** de dez blocos, e não só a dos três números. A asserção de que a tradução estava ausente foi retirada de propósito, e não por acidente |
| `test_T1_ordem_dos_tres_cartoes_e_a_hierarquia` | Lia a **fonte** de `bloco_resultado._cartoes` por AST. A ordem mudou de casa; o teste passou a ler o **modelo montado**, que é mais forte — afirma o que sai, e vale para as duas superfícies |
| `pdf_visual.KPI` e `pdf_visual.Cenario` | Deixaram de existir. Dois dataclasses com os mesmos campos em arquivos diferentes é a forma mais discreta de a tela e o papel divergirem |
| Título do gráfico de sensibilidade | Saiu do Altair. Quem nomeia o que está plotado é o subtítulo da seção, que vem da montagem e é o **mesmo texto** que o PDF imprime acima da curva dele |

#### O defeito que isto expôs

A seção de decisões cresceu uma linha e o PDF **saltou de 2 para 4 páginas**:
`linha()` desenha **duas** células que começam no mesmo `y`, e a quebra
automática do fpdf2 age por célula. Um par no fim da página saía **rasgado** —
`decisão L` numa página e `idade de recoleta não definida` na seguinte, com o
cabeçalho do documento entre as duas.

- **Correção:** `_reservar()` mede o par com `dry_run=True, output="HEIGHT"` e
  quebra a página **antes** dele. Um rótulo sem o valor dele é pior do que o par
  inteiro na página de baixo.
- **Lição:** quebra automática por célula não sabe o que é um par. Todo bloco
  que desenha duas células no mesmo `y` precisa reservar a altura antes.
- **Travado por:** `test_pdf_par_rotulo_valor_nunca_e_rasgado_entre_paginas`,
  que testa a costura por dentro (a reserva) e por fora (nenhum cabeçalho entre
  um rótulo e o valor dele, em todas as seções).

#### O que continua sem verificação automática

O layout em si. As barras usam altura em `%` dentro de um container de altura
fixa, e o `style` inline que carrega essas alturas atravessa o sanitizador do
`st.markdown` — **isso não é verificável por `pytest`**. É a mesma classe de
defeito da §4.7, e por isso entrou como item manual 11.

### D27 — Mark up em percentual, e "Nova margem com refil"

Pedido do cliente em 27/08/2026: *"coloque o mark up em % (exemplo, ao invés de
2x colocar 100%)"* e *"reescrever 'MARGEM COM PALHETAS - POR MÊS' para 'NOVA
MARGEM COM REFIL'"*.

#### 1. O mark up virou percentual

| | Antes | Agora |
|---|---|---|
| Valor | `2,1×` | **`108%`** |
| Apoio | `faturamento ÷ custo` | **`(faturamento − custo) ÷ custo`** |
| Formatador | `formato.multiplo()` | `formato.markup_percentual()` |

**É o acréscimo sobre o custo, não a razão.** Vender a duas vezes o custo é
100%, e não 200% — a diferença entre as duas leituras é o próprio custo, e
trocar uma pela outra **dobra o número**. O exemplo do cliente fixa qual das
duas vale.

**O cálculo não mudou.** `Resultado.markup_operacao` continua sendo a razão
`faturamento ÷ custo`, adimensional, e continua `None` quando falta uma parcela.
A conversão vive em `formato`, que é a camada de apresentação — `calculo.py`
segue puro e auditável, e os testes de aritmética não foram tocados.

**A linha de apoio passou a valer mais, e não menos.** Um percentual ao lado de
duas colunas de reais convida a leitura de **margem percentual**, que é outra
conta:

| | Conta | T1 |
|---|---|---|
| Mark up | (faturamento − custo) ÷ **custo** | **108%** |
| Margem % | (faturamento − custo) ÷ **faturamento** | 52% |

O múltiplo `2,1×` era imune a essa confusão por construção — nenhuma margem se
expressa em "vezes". O percentual não é, e a mitigação é o rótulo, que a §4 já
exigia: **todo resultado financeiro diz qual conta ele é.**
`test_markup_percentual_nao_e_margem_percentual` trava a distinção, e os testes
de cartão da tela e do PDF exigem a linha da conta junto do número.

**Mudou nos três lugares**, e de propósito: cartão da tela, cartão do PDF e
painel de fórmula. `2,1×` na tela e `108%` no papel seria a tela se
contradizendo na frente do cliente — o mesmo princípio da §5.11 sobre a curva e
a manchete. O painel de fórmula passou a mostrar a subtração inteira:

```
[(R$ 20.781 + R$ 9.180) − (R$ 8.991 + R$ 5.400)] ÷ (R$ 8.991 + R$ 5.400) = 108%
```

`formato.multiplo()` **deixou de existir** — era usado só aqui.

#### 2. "Nova margem com refil"

O cartão de apoio do PDF que mostra a margem mensal do cenário adotado.

| | Antes | Agora |
|---|---|---|
| Rótulo | `MARGEM COM PALHETAS, POR MÊS` | **`NOVA MARGEM COM REFIL`** |
| Valor | `R$ 15.570` | `R$ 15.570` |
| Apoio | `hoje R$ 3.780 → adotando o refil` | **`por mês · hoje R$ 3.780`** |

O rótulo antigo dizia a grandeza e o período, mas não dizia que o número grande
é o cenário **novo** — e o valor de hoje aparece logo abaixo dele, no mesmo
cartão, sem distinção no rótulo. "Nova margem com refil" nomeia o que o número é.

**O período desceu para o apoio, e não sumiu.** Sair do rótulo sem reaparecer
deixaria o número grande sem período, e um valor mensal lido como anual erra por
12×. `test_pdf_mark_up_em_percentual_e_a_nova_margem_nomeada` verifica as duas
coisas.

### D26 — O PDF abre pelos dois números, e a tradução desce

Pedido do cliente em 27/08/2026, logo depois de D24: *"no PDF, a primeira coisa
que deve aparecer em evidência máxima é o faturamento e a margem de contribuição
adicional, lado a lado, de forma bem grande e evidente. Rearranje de modo que o
faturamento adicional fique aonde agora está o 'o que isso significa na
oficina'."*

#### O que mudou

| | D24 | Agora |
|---|---|---|
| Faixa escura de abertura | tradução à esquerda, contraste do mês à direita | **faturamento adicional \| margem de contribuição adicional**, lado a lado, mesmo corpo |
| Corpo do número de abertura | 15 pt (a tradução) | **até 32 pt**, o maior da folha |
| Os três cartões da tela | linha própria, abaixo da faixa | os dois primeiros **subiram para a faixa**; sobrou o mark up |
| Tradução em escala humana | abertura, 15 pt | cartão de apoio: `3 a cada 10` + `carros que entram viram um par de refil` |
| Contraste `hoje → com o refil` | metade direita da faixa | cartão de apoio |

A linha de cartões de apoio ficou com três: **mark up da operação**, **o que
isso significa na oficina** e **margem com palhetas, por mês**.

#### O que isso contraria, e por que foi feito assim mesmo

| | |
|---|---|
| O que o DESIGN diz | §5.5 e P2: a tradução vem **primeiro e maior**. "R$ 1,2 milhão por ano" é rejeitado pelo cérebro antes de ser avaliado; "3 a cada 10 carros que entram" é conferido pela intuição em dois segundos |
| Onde a regra já tinha caído | Na tela, em **D21.2** — a tradução saiu da Tela 1 por completo. O PDF era o **último lugar** em que a ordem original da §5.5 sobrevivia |
| O que se perde | O documento passa a abrir por um número que o cérebro rejeita antes de avaliar. A mitigação é que a tradução **não saiu**: ela está a 4 cm abaixo, na mesma página, e o PDF continua sendo o único lugar em que ela existe |
| Travado por | `test_pdf_faturamento_e_margem_abrem_o_documento`, que **substitui** `test_pdf_traducao_vem_antes_do_anual`. O novo lê a ordem no fluxo de conteúdo do PDF e exige as três coisas: os dois números abrem, o faturamento vem antes da margem (ordem de D21), e a tradução continua presente |

#### Os dois números têm o mesmo corpo, e isso é decisão

O corpo é calculado **uma vez, pelo mais largo dos dois**, e aplicado aos dois.
Ajustar cada um por conta própria faria `R$ 7.694.784` sair menor que
`R$ 141.480` ao lado — e, em dois números pareados, **tamanho diferente lê como
importância diferente**, que é o contrário do que este desenho afirma.

Pelo mesmo motivo cada um carrega o **próprio rótulo** na faixa, e não só a nota
de rodapé do grupo: são duas contas diferentes no mesmo tamanho, e a §4 exige que
todo resultado financeiro diga qual conta ele é. "Faturamento" não é "margem".

Nenhum dos dois é vermelho — a faixa é escura (D6, 17,9:1), e com margem
**negativa** o número sai branco, com o sinal, ao lado de um faturamento
positivo do mesmo tamanho. §13.1 intacta.

### D25 — Lockup novo: `assets/logo.jpeg`, dois andares, `INTRACE Br`

Arquivo entregue pelo cliente em 27/08/2026 —
`assets/logo-suica-tech-atual.jpeg`, 1600 × 301, JPEG, fundo `#FFFFFF` opaco.

| | Lockup anterior | Lockup atual |
|---|---|---|
| Andares | três (palavra-marca, assinatura, tarja de slogan) | **dois** (palavra-marca + assinatura) |
| Assinatura | `:::SWISSINT INTRACE AG` | **`INTRACE Br`** |
| Bandeiras | suíça e alemã | nenhuma |
| Tarja | `O NÚMERO 1 EM BORRACHA PARA PALHETA` | nenhuma |
| Proporção | 1322 × 356 (3,7:1) | 1600 × 301 (**5,3:1**) |
| No cabeçalho | 44 px → 163 px de largura | 44 px → **234 px** (teto de `max-width` é 380 px) |

**A distinção cabeçalho/PDF ficou dormente.** Ela existia porque a tarja não
sobrevive a 44 px e porque um superlativo no topo de uma ferramenta de auditoria
trabalha contra a tese da tela (§4). Sem tarja, a mesma arte serve os dois
lugares: `NOMES_COMPLETO` não encontra nada e `caminho_do_logo_completo()` cai
em `_arquivo()`, que é o comportamento correto. O mecanismo **continua de pé** —
basta soltar um `logo-completo.png` para o PDF voltar a ter arte própria.

`FUNDO_CLARO` continua `True`, agora por **dois** motivos que andam juntos: a
palavra-marca é vermelha (sobre a faixa vermelha original não haveria contraste)
e o arquivo é JPEG, sem canal alfa — sobre qualquer faixa colorida o retângulo
branco apareceria como uma caixa. Sobre o cabeçalho claro ele some, porque o
branco do arquivo é `#FFFFFF` exato, o mesmo de `--superficie`.

#### A armadilha que isto revelou, e o teste que a fecha

Ao trocar o arquivo, `assets/logo.png` saiu antes de existir qualquer nome que
`marca.NOMES` procura. O app **continuou subindo, verde, e sem marca nenhuma** —
a reserva tipográfica entrou e o aviso foi para a faixa do vendedor, em 12 px,
que é onde ele deve ficar em reunião (§7.4, §5.9) e é exatamente o lugar errado
para um erro de deploy ser notado.

`test_o_logo_entregue_esta_de_fato_em_uso` passou a exigir que o arquivo do
repositório esteja **em uso**, e não apenas presente — e que ele não seja SVG,
porque um SVG resolveria o cabeçalho e deixaria o **PDF sem logo** (o `fpdf2`
não rasteriza SVG por caminho de imagem, e `_Documento.header` pula a extensão).

#### ⚠️ Em aberto: `Intrace AG` no rodapé do documento

O logo novo assina **`INTRACE Br`**; a linha de cabeçalho do PDF
(`exportador_pdf`) continua dizendo `Suicatech · Intrace AG`. As duas coisas
aparecem **a três centímetros uma da outra** na mesma folha, e ela sai da sala.

Não foi alterado: qual entidade assina o documento é decisão do cliente, não
de implementação. Trocar é uma linha.

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
| +19 | `CartaoPrecoPalheta` | plano §5.1, §5.3 — base `app_precos` | **Provisório** até o DESIGN ser regerado para a Tela 3 |

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

### 4.11 O botão de baixar o PDF imprimia o próprio HTML do ícone

O rótulo era `f"{svg('exportar')} Baixar PDF do cenário"`. O Streamlit trata
rótulo de widget como markdown e **escapa** a marcação — nem `unsafe_allow_html`
existe ali. O botão saía com

```
<span class="st-icone" aria-hidden="true"><svg viewBox="0 0 24 24" …></span> Baixar PDF do cenário
```

impresso em cima dele, no fim da tela que o cliente acabou de ver.

O que torna este o defeito mais instrutivo do arquivo: **`gerar_pdf()` estava
perfeito**, e doze testes provavam isso — vocabulário, marca-d'água, decisões em
aberto, ordem de leitura, cashback que não desconta. Todos chamavam a função
direto. Nenhum instanciava a tela e olhava para o botão, que é a única peça entre
o documento e o cliente. Do lado de fora, "exportar para PDF" simplesmente não
funcionava.

- **Correção:** rótulo em texto puro; o ícone foi para uma linha de markdown
  acima (`.st-exportar-nota`), onde `unsafe_allow_html` vale.
- **Lição:** `svg()` só pode entrar em `st.markdown(..., unsafe_allow_html=True)`.
  Em rótulo de botão, de campo, de expander ou de aba, ele vira texto. E, mais
  geral: **testar a função não é testar o componente.** Um teste de renderização
  por elemento — não só por texto na página — é o que pega esta classe.

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

§4.11 acrescenta uma variante da mesma lição, e ela é mais barata de fechar: ali
a suíte tinha **doze testes** provando que o PDF estava certo, e nenhum
instanciando o botão que o entregava. Onde o teste de navegador é caro, o de
renderização por elemento (`AppTest` + `at.get("download_button")`, `at.button`,
`at.number_input(...).label`) cobre boa parte — e cobre justamente a peça que
fica entre a função correta e o cliente.

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
| 6 | **Cashback no celular (D23).** Em 390×844: os seis campos aparecem **um por linha**, cada um com o rótulo `<destinatário> · <categoria>` visível e sem quebra em duas linhas; o chip de subtotal aparece ao preencher e some ao apagar | | |
| 7 | **Cashback no tablet (D23).** Em 1180×820 e em 768 px: os três campos de cada categoria continuam **lado a lado**, e o título da categoria não encosta no campo de cima | | |
| 8 | **Baixar o PDF (D23 / §4.11).** Com o resultado na tela, abrir "Levar esta simulação — PDF": o botão está em vermelho de marca, **sem nenhuma marcação impressa no rótulo**, e o toque baixa um arquivo que abre num leitor de PDF. Repetir com o nome do cliente acentuado e conferir o nome do arquivo baixado | | |
| 9 | **O PDF impresso (D24).** Imprimir a página 1 **em preto e branco**: a segunda barra continua distinguível da primeira e as duas linhas da curva continuam distinguíveis entre si (§3.1.3 / §9.4 — a distinção não pode depender de cor) | | |
| 11 | **O resultado na tela (D28).** Com o resultado revelado, conferir que a tela mostra, nesta ordem: manchete com os dois números, três cartões de apoio, **barras hoje × com o refil** (as alturas em proporção, e o segmento vermelho visível), os três cenários, o gráfico, a tabela, e as seções de premissas / preço e custo / decisões. **As barras dependem de `style` inline sobreviver ao `st.markdown`** — se elas saírem sem altura, é isso | | |
| 13 | **O PDF endereçado (D29).** Gerar com nome de cliente preenchido: o nome abre o documento em 17 pt, o título vira subtítulo, e o nome **repete na página 2**. Gerar sem nome: o título volta a abrir, sem espaço vazio no lugar | | |
| 12 | **Tela × PDF, lado a lado (D28).** Abrir o PDF da mesma simulação e comparar bloco a bloco com a tela: mesmos rótulos, mesmos números, mesma ordem | | |
| 10 | **O PDF de uma rede grande (D24).** Simular 8+ pontos de venda: os valores de sete dígitos cabem nos cartões sem corte, e os rótulos do eixo Y da curva não se repetem | | |

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

# Simulador de viabilidade — refil de palhetas

App de pitch para a **Suicatech / Intrace AG**. Um vendedor abre num tablet, em
paisagem, e inclina na direção do gerente de pós-venda do outro lado da mesa.

**Fonte de verdade:** [`DESIGN.md`](DESIGN.md) para UX/UI e
[`plano-app-viabilidade_1.md`](plano-app-viabilidade_1.md) para produto, cálculo e
sequência. Onde o código divergir deles, o código está errado — exceto pelas
divergências registradas em [`docs/DIVERGENCIAS.md`](docs/DIVERGENCIAS.md).

---

## Rodar

```powershell
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

`requirements.txt` tem só as 4 dependências que o **app** importa — é o que o
Streamlit Cloud instala. `requirements-dev.txt` acrescenta `openpyxl` (usado só
pelo pipeline) e `pytest`.

**Para colocar no ar:** [docs/DEPLOY.md](docs/DEPLOY.md). O passo que mais falha
é a versão do Python — `pandas` exige ≥ 3.11, e isso se escolhe em *Advanced
settings* na criação do app, sem poder mudar depois.

## Os quatro comandos que importam

```powershell
python -m pytest testes/ -q          # os 16 casos-teste + S1-S13 + o checklist
python verificar.py                  # o checklist §12, linha por linha
python -m pipeline.publicar          # planilha -> validação -> snapshot
python -m pipeline.publicar --conferir   # valida sem publicar
```

`python -m pytest testes/ -k T1` roda um caso só. `-k render` roda só os testes
que sobem a tela.

---

## Estrutura

```
app.py                    ponto de entrada. A ordem das chamadas É a ordem de leitura
verificar.py              roda o checklist §12 e imprime linha por linha
requirements.txt          runtime: o que o Streamlit Cloud instala
requirements-dev.txt      runtime + openpyxl + pytest
.gitignore                segredos, cache e PDFs de reunião ficam fora do repo
.streamlit/config.toml    CAMADA A do tema — estável, não quebra em atualização
assets/                   o logo da marca. Ver assets/LEIA-ME.md

src/                      ══ APP ══ roda no servidor Streamlit
  marca.py                o logo: arquivo em assets/, com reserva tipográfica
  parametros.py           O ÚNICO lugar onde números vivem. Decisões F–L como None
  validacao_parametros.py V1–V7. Falha = o app NÃO SOBE
  calculo.py              §6.1.5. Aritmética pura: sem streamlit, sem I/O
  formato.py              moeda, percentual, tradução por passagem
  plausibilidade.py       R1–R5 → só a faixa do vendedor
  estado.py               session_state; preço e custo NUNCA persistem
  css.py                  CAMADA B 🔧 FRÁGIL — todo o CSS do app, num arquivo só
  icones.py               ícones de linha (divergência D2)
  componentes/            os 18 componentes da §5
  telas/                  tela1 completa; telas 2 e 3 como estrutura vazia
  dados/                  leitura do snapshot. A Tela 1 nunca importa isto

pipeline/                 ══ PIPELINE ══ sua máquina ou CI, NUNCA o navegador
  publicar.py             CLI: planilha → validação → snapshot versionado
  esquema.py              schema das 4 abas
  validacoes.py           S1–S13. Qualquer falha = exit != 0
  criar_planilha_modelo.py  gera a planilha vazia com os cabeçalhos certos

dados/
  planilha_modelo.xlsx    abas com cabeçalho e ZERO registros
  snapshot/               snapshot_vN.json + ultimo.json

testes/
  casos.json              os 16 casos como DADO, não código
  checagens.py            buscas e análises de AST, compartilhadas com verificar.py

docs/
  DEPLOY.md               o que subir no GitHub e como publicar
  DIVERGENCIAS.md         o que foge do DESIGN, por quê, e como reverter
  CHECKLIST-PRE-VISITA.md a mitigação do risco mais provável do projeto
```

### A fronteira app | pipeline

Três regras, todas verificadas por AST em `testes/test_checklist.py`:

1. `pipeline/` **nunca** é importado por `src/` nem por `app.py`.
2. A Tela 1 **não lê planilha e não faz nenhuma requisição**. Só as Telas 2 e 3
   consomem o snapshot.
3. `calculo.py` **não importa streamlit** — é o que torna os 16 casos
   executáveis sem subir o app.

---

## Três coisas que parecem defeito e são especificação

**Preço e custo abrem vazios, sempre.** Não é bug e não é esquecimento. O custo
de aquisição da concessionária é o preço de venda da Suicatech, e o app tem link
aberto sem login. Nenhum default, nenhum valor de demonstração — nem rotulado
como exemplo, porque um número na tela vira âncora mesmo com etiqueta.

**O custo da palheta original é opcional, e isso muda o rótulo do resultado.**
Sem ele não existe margem da original para descontar, então não existe
*incremental*: o rótulo passa a dizer `margem de contribuição do refil`. O app
não assume uma margem para a palheta original — nomear a conta errada é pior que
não nomear.

**Sem as passagens por mês, nenhum valor em R$ aparece.** Um default de R$ 0
ancoraria no cenário mais favorável possível. O vazio dessa tela é a abertura da
conversa, não uma falha: ela pergunta o que o vendedor precisa perguntar.

**A canibalização não é modelada, e isso está declarado na tela.** O campo de
substituição saiu por decisão do cliente, então o app assume que nenhuma venda de
refil tira venda da palheta original — a premissa mais favorável possível. Ela
aparece na faixa de premissas de toda simulação (`sem canibalização — todo refil
é venda nova`) e sai impressa no PDF. Ver D15 em
[docs/DIVERGENCIAS.md](docs/DIVERGENCIAS.md).

**O cashback nunca desconta da margem.** São valores em R$ por venda para
Consultor, Gerente e Marketing, com linhas próprias para dianteiro e traseiro.
Pago pela Suicatech: preencher **acrescenta uma linha** ao resultado e nunca
altera a manchete. Se algum dia subtrair, o principal argumento comercial do
bloco foi invertido — e três testes existem só para impedir isso.

**Rampa, sazonalidade, piso de preço e número de códigos estão marcados com ⚠️.**
Não foram decididos, e o app se recusa a escolher um número plausível para
qualquer um deles. O comportamento é sempre o mais conservador, e a validação V6
**aborta o app** se alguém tentar declarar um piso de preço. Ver
[`docs/DIVERGENCIAS.md`](docs/DIVERGENCIAS.md) §2 e a §10 do DESIGN.

---

## Não existe offline

O Streamlit renderiza no servidor; o navegador só mantém um websocket. Sem
conexão a tela morre — não fica degradada. Não há PWA, service worker ou cache
que resolva, porque a conta não acontece no aparelho (plano §6.2, DESIGN §7.1).

Isso virou requisito de **operação**, não de código:
[`docs/CHECKLIST-PRE-VISITA.md`](docs/CHECKLIST-PRE-VISITA.md). O checklist §12
verifica ativamente que o app **não promete** funcionamento sem rede em nenhum
texto.

---

## Antes de subir a versão do Streamlit

A versão está fixada com `==` em `requirements.txt` **de propósito**. Todo o CSS
da camada B depende de seletores internos do Streamlit e quebra entre versões.

Subir a versão exige refazer o reteste visual de todos os itens marcados 🔧 em
`src/css.py`, e registrar em `docs/DIVERGENCIAS.md` §5. Dois defeitos reais dessa
natureza já aconteceram aqui e estão documentados na §4 do mesmo arquivo — vale
ler antes de mexer.

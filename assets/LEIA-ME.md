# assets/ — o logo da marca

| Arquivo | Onde aparece | O que contém |
|---|---|---|
| `logo.png` | **cabeçalho do app** | palavra-marca `SUIÇA TECH` + bandeiras + assinatura `:::SWISSINT INTRACE AG` |
| `logo-completo.png` | **cabeçalho do PDF** | o lockup inteiro, incluindo a tarja `O NÚMERO 1 EM BORRACHA PARA PALHETA` |

Os dois foram gerados a partir do `logo.png` que você colocou na raiz do projeto
(1322×356, RGBA, fundo branco opaco).

## Por que o cabeçalho não usa o lockup inteiro

O logo tem três andares. No cabeçalho ele cabe em 44 px de altura — e com os
três andares nesse espaço a palavra-marca cai para ~18 px e a assinatura vira
borrão. **Um logo ilegível presta menos serviço à marca do que um logo menor e
nítido.**

Há um segundo motivo, e é de conteúdo: a tarja é um superlativo. A §4 do DESIGN
proíbe linguagem de anúncio na copy do app —

> *"Até 40% de aproveitamento" → "Aproveitamento realista: 30%". Linguagem de
> anúncio destrói o tom de instrumento."*

— porque ela trabalha contra a tese da tela, que é **"confira você mesmo"**. Uma
afirmação não verificável no topo de uma ferramenta de auditoria enfraquece o
resto.

No **PDF** o lockup inteiro aparece: lá há espaço, e um documento que sai da sala
não é o instrumento da negociação.

## Se você quiser o lockup inteiro também no cabeçalho

```powershell
Copy-Item assets\logo-completo.png assets\logo.png -Force
```

E aumente a altura em `src/css.py`, na regra `.st-logo`, de `44px` para ~`64px`,
senão a assinatura fica ilegível.

## Trocar o logo

Solte o arquivo aqui como `logo.png` (ou `.svg`, `.webp`, `.jpg` — o app procura
nessa ordem) e recarregue a página. Nenhuma linha de código muda.

Se o logo novo for **claro** (para fundo escuro), abra `src/marca.py` e troque:

```python
FUNDO_CLARO = False   # cabeçalho volta a ser a faixa vermelha
```

Hoje está `True`, porque o logo oficial é vermelho sobre branco: letra vermelha
sobre faixa vermelha não tem contraste nenhum.

## Limites

| | |
|---|---|
| Tamanho máximo | **400 kB.** Acima disso o app usa a marca em texto e diz o motivo na faixa do vendedor |
| Altura no cabeçalho | 44 px, largura automática — a proporção do arquivo é preservada |
| Formato | PNG (com ou sem transparência) ou SVG |

O arquivo é embutido na página como `data:` URI, e não servido por `st.image`.
Isso mantém a promessa da §7.1 do DESIGN — a Tela 1 não faz **nenhuma**
requisição externa — e é o motivo do limite de tamanho: um logo de 3 MB embutido
a cada rerun seria latência na reunião.

## Sem arquivo

O cabeçalho mostra a marca em tipografia e a faixa do vendedor avisa
`logo não encontrado em assets/ — usando a marca em texto`. O cliente não vê
imagem quebrada, e a tela não trava (§7.4).

# assets/ — o logo da marca

| Arquivo | Papel |
|---|---|
| `logo.jpeg` | **o que o app lê** — cabeçalho da tela e cabeçalho do PDF |
| `logo-suica-tech-atual.jpeg` | o original entregue pelo cliente, guardado como veio |
| `originais/` | artes anteriores. O app **não** olha aqui — `src/marca.py` procura só na raiz de `assets/` |

O logo em uso (27/08/2026) é o lockup horizontal: palavra-marca `SUIÇA TECH` em
vermelho com a assinatura `INTRACE Br` embaixo, à direita. **1600 × 301, JPEG,
fundo branco `#FFFFFF` opaco.**

Os dois JPEG são byte a byte iguais. Existem separados de propósito: `logo.jpeg`
é um nome que o código procura, e trocá-lo é uma operação de manutenção; o outro
é o arquivo como o cliente mandou, e serve de referência quando alguém perguntar
"que arte é essa?".

## Trocar o logo

Solte o arquivo aqui como `logo.png` — ou `.svg`, `.webp`, `.jpg`, `.jpeg`; o app
procura **nessa ordem** e usa o primeiro que encontrar. Recarregue a página.
Nenhuma linha de código muda.

> Cuidado com a ordem: `logo.png` vence `logo.jpeg`. Se você soltar um PNG novo
> sem apagar o `logo.jpeg` atual, o PNG passa a valer — que em geral é o que se
> quer, mas convém saber.

Se o logo novo for **claro** (letras brancas, para fundo escuro), abra
`src/marca.py` e troque:

```python
FUNDO_CLARO = False   # cabeçalho volta a ser a faixa vermelha
```

Hoje está `True`, e por dois motivos que andam juntos: a palavra-marca é
**vermelha** (letra vermelha sobre faixa vermelha não tem contraste nenhum) e o
arquivo é **JPEG**, que não tem transparência — sobre uma faixa colorida o
retângulo branco apareceria como uma caixa. Sobre o cabeçalho claro ele
desaparece, porque o branco do arquivo é exatamente o `--superficie` do app.

## Um lockup maior só para o PDF

Se algum dia voltar a existir uma arte com mais andares — por exemplo com a
tarja `O NÚMERO 1 EM BORRACHA PARA PALHETA`, que o lockup anterior tinha —,
solte-a como `logo-completo.png` e o **PDF** passa a usá-la, sem tocar no
cabeçalho da tela.

O motivo de a distinção existir: a 44 px de altura, um lockup de três andares
reduz a palavra-marca a ~18 px e a assinatura vira borrão. **Um logo ilegível
presta menos serviço à marca do que um logo menor e nítido.** E há um motivo de
conteúdo: a tarja é um superlativo, e a §4 do DESIGN proíbe linguagem de anúncio
na copy do app —

> *"Até 40% de aproveitamento" → "Aproveitamento realista: 30%". Linguagem de
> anúncio destrói o tom de instrumento."*

— porque ela trabalha contra a tese da tela, que é **"confira você mesmo"**. Num
documento que sai da sala, e que não é o instrumento da negociação, ela cabe.

O lockup atual tem dois andares e cabe inteiro nos 44 px, então hoje a mesma
arte serve os dois lugares.

## Limites

| | |
|---|---|
| Tamanho máximo | **400 kB.** Acima disso o app usa a marca em texto e diz o motivo na faixa do vendedor. O arquivo atual tem 41 kB |
| Altura no cabeçalho | 44 px (34 px no celular), largura automática — a proporção do arquivo é preservada |
| Largura máxima | 380 px. É a rede que impede uma arte muito larga de empurrar a navegação para fora da faixa |
| Altura no PDF | 11 mm, largura automática |
| Formato | SVG, PNG, WEBP ou JPEG |

O arquivo é embutido na página como `data:` URI, e não servido por `st.image`.
Isso mantém a promessa da §7.1 do DESIGN — a Tela 1 não faz **nenhuma**
requisição externa — e é o motivo do limite de tamanho: um logo de 3 MB embutido
a cada rerun seria latência na reunião.

## Sem arquivo

O cabeçalho mostra a marca em tipografia e a faixa do vendedor avisa
`logo não encontrado em assets/ — usando a marca em texto`. O cliente não vê
imagem quebrada, e a tela não trava (§7.4).

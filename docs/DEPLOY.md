# Colocar o app no ar — Streamlit Community Cloud

## 0. O erro que já aconteceu aqui — leia antes de qualquer coisa

> ### 🚫 Não suba os arquivos pela página do GitHub
>
> A primeira publicação foi feita arrastando arquivos para a interface web do
> GitHub. **A interface web achata a estrutura de pastas:** os 72 arquivos
> caíram todos na raiz do repositório, `src/` deixou de existir, e o deploy
> morreu em `app.py` com:
>
> ```
> ModuleNotFoundError: No module named 'src'
> ```
>
> O sinal que confirma o diagnóstico: apareceram arquivos `.pyc` no
> repositório. Eles estão no `.gitignore`, então `git add` **nunca** os
> incluiria — a presença deles prova que o upload passou por fora do git.
>
> **Este app tem 8 pastas e 5 níveis de import. A estrutura não é decoração —
> é o que faz o `import` funcionar.** A única forma correta de publicar é
> `git push`. Ver §3.

Duas consequências menores do mesmo achatamento, que teriam quebrado o app
mesmo se o `import` tivesse passado: `assets/logo.png` não subiu (o cabeçalho
cairia na reserva tipográfica) e `.streamlit/config.toml` não subiu (a camada A
do tema — acento, fundo e fonte — simplesmente não existiria).

---

## 1. O que sobe para o GitHub

**Sobe tudo o que está na pasta hoje, exceto o que o `.gitignore` já exclui.**
Não há nada sensível no repositório: `python verificar.py` confirma que preço,
custo e âncora nunca são persistidos, e as validações S11/S12 impedem que eles
entrem no snapshot.

O que o app **precisa** para rodar (se faltar, não sobe):

```
app.py                     ponto de entrada
requirements.txt           as 4 dependências de runtime
.streamlit/config.toml     tema nativo — a camada estável do visual
src/                       todo o código do app
assets/logo.png            a marca no cabeçalho
assets/logo-completo.png   a marca no PDF
```

O que **deve** subir junto, mesmo sem ser necessário para o app subir:

```
dados/snapshot/            sem isto as Telas 2 e 3 dizem "nenhum snapshot publicado"
dados/planilha_modelo.xlsx o formato da curadoria da Fase 0
pipeline/                  o passo de publicação que você roda toda semana
requirements-dev.txt       para instalar o ambiente de teste em outra máquina
testes/                    os 16 casos e o checklist §12
verificar.py               roda o checklist por comando
docs/                      divergências e checklist pré-visita
DESIGN.md                  fonte de verdade de UX/UI
plano-app-viabilidade_1.md fonte de verdade de produto
README.md                  como rodar e as três coisas que parecem defeito
assets/LEIA-ME.md          como trocar o logo
assets/originais/          os arquivos de logo que você entregou, como procedência
```

O que **não** sobe (já no `.gitignore`): `__pycache__/`, `.pytest_cache/`,
`.venv/`, `.streamlit/secrets.toml`, PDFs gerados na reunião.

> **Por que subir `testes/` e `docs/`:** o repositório é o único lugar onde as
> divergências em relação ao DESIGN estão registradas. Quem abrir este código em
> seis meses — inclusive você — precisa do `docs/DIVERGENCIAS.md` para saber o
> que foge do documento e por quê. E `pytest` no CI é o que impede uma
> atualização de Streamlit de quebrar a tela em silêncio.

---

## 2. A versão do Python — verificada em deploy real

**`pandas 3.0.3` exige Python ≥ 3.11.**

**Situação confirmada no deploy de 19/08/2026:** o Community Cloud usou
**Python 3.14.7** e instalou as 45 dependências sem um único erro. O aviso
abaixo continua valendo como regra, mas hoje o padrão da plataforma já a
satisfaz — não foi este o passo que falhou.

Ao criar o app, se **"Advanced settings"** oferecer escolha de versão, qualquer
coisa **≥ 3.11** serve. Só recuse 3.9 e 3.10.

Isso **não pode ser mudado depois** de criar o app — se errar, é mais rápido
apagar e criar de novo do que tentar corrigir.

Se por algum motivo só houver Python 3.10 disponível, a saída é relaxar um pino:

```
pandas==2.2.3     # em vez de 3.0.3
```

`pandas` é dependência transitiva do Streamlit; o pino exato existe por
consistência com a regra da camada B, não porque o app dependa dessa versão.
**Não relaxe o pino do `streamlit`** — esse é o que sustenta todo o CSS injetado.

---

## 3. Passo a passo

### 3.1 O git que você já tem

Não há `git` no `PATH`, mas **o GitHub Desktop está instalado e traz um git
completo** (versão 2.53.0). Ele resolve tudo, sem instalar nada:

```powershell
$git = "$env:LOCALAPPDATA\GitHubDesktop\app-3.5.12\resources\app\git\cmd\git.exe"
& $git --version
```

> Ao atualizar o GitHub Desktop, o `app-3.5.12` do caminho muda. Para achar o
> atual:
> ```powershell
> $git = (Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe" | Sort-Object FullName -Descending)[0].FullName
> ```

Se preferir o git de verdade no `PATH` — vale a pena, porque aí `git` funciona
em qualquer terminal sem a variável:

```powershell
winget install --id Git.Git -e
```

Feche e reabra o terminal depois de instalar.

### 3.2 Uma decisão antes: tirar o projeto do OneDrive

A pasta está em `OneDrive\Documents\`. O OneDrive sincroniza a pasta `.git`, e
isso corrompe repositório — é uma das causas mais comuns de "meu git quebrou do
nada". **Recomendo mover o projeto para fora do OneDrive** antes de rodar
`git init`:

```powershell
$origem  = "$env:USERPROFILE\OneDrive\Documents\APP VIABILIDADE ECONOMICA PYTHON"
$destino = "$env:USERPROFILE\projetos\app-viabilidade-refil"
New-Item -ItemType Directory -Force -Path (Split-Path $destino) | Out-Null
Move-Item $origem $destino
cd $destino
```

Se preferir manter no OneDrive, ao menos exclua a pasta `.git` da sincronização
nas configurações do OneDrive.

### 3.3 O repositório local — já está pronto

`git init`, `git add` e o commit **já foram feitos**, com o `origin` apontando
para `joaobaciega/app-viabilidade-economica`. Confira antes de publicar:

```powershell
$git = "$env:LOCALAPPDATA\GitHubDesktop\app-3.5.12\resources\app\git\cmd\git.exe"
& $git log --oneline -1
& $git ls-tree -r HEAD --name-only    # 72 arquivos, COM as pastas
```

A lista tem que mostrar `src/calculo.py`, `assets/logo.png` e
`.streamlit/config.toml` **com a barra** — se algum aparecer sem pasta, a árvore
está achatada de novo (ver §0).

### 3.3.1 Publicar pelo GitHub Desktop — sem comando

O upload achatado tinha histórico próprio, então o commit local não descendia
dele e um `push` normal seria recusado. **Isso já foi resolvido** com um merge
`-s ours`, que mantém a árvore correta e registra o dump achatado como
ancestral. Consequência prática: o remoto é ancestral do local, o push é um
avanço normal, e **nem `--force` nem apagar o repositório são necessários.**

1. Abra o **GitHub Desktop** (você já está logado como `joaobaciega`)
2. **File → Add local repository…** → *Choose…* → selecione a pasta do projeto
   → **Add repository**
3. No topo, clique **Push origin** (mostra uma seta ↑ com o número de commits)
4. Espere a barra terminar

Se o botão do topo disser **Fetch origin** em vez de *Push origin*, clique nele
uma vez — o *Push origin* aparece em seguida.

**Não clique em *Pull origin*.** O histórico achatado ainda existe do lado
remoto; um pull traria os 60 arquivos soltos de volta para dentro da sua pasta.
Depois deste primeiro push isso deixa de ser um risco.

<details>
<summary>Alternativa por comando, se o GitHub Desktop falhar</summary>

```powershell
$git = "$env:LOCALAPPDATA\GitHubDesktop\app-3.5.12\resources\app\git\cmd\git.exe"
& $git push -u origin main
```
</details>

### 3.3.2 Público ou privado — decida antes da primeira visita

**O repositório está público hoje.** Ele não contém tabela de preço nem custo
— `verificar.py` e as validações S11/S12 garantem isso —, mas contém o
`DESIGN.md` e o `plano-app-viabilidade_1.md`, que descrevem a estratégia
comercial, a margem-alvo e o posicionamento contra a palheta original em
detalhe. **Sugiro privado.**

*Settings → General → Danger Zone → Change repository visibility → Make
private.* O Community Cloud funciona igual com repositório privado.

A lista tem que mostrar `src/calculo.py` **com a barra**. Se algum arquivo do
app aparecer sem pasta, a árvore está achatada de novo — volte para a §0.

### 3.4 Publicar

**O app do Streamlit já existe** e já está apontado para o repositório certo.
Depois do `push` da §3.3.1 ele **rebuilda sozinho** — não crie um app novo. Se
demorar, abra <https://share.streamlit.io> e use **Reboot app** no menu do app.

Para criar de novo a partir do zero, se algum dia precisar:

1. <https://share.streamlit.io> → **New app** → **From existing repo**
2. Repository: `joaobaciega/app-viabilidade-economica`
3. Branch: `main`
4. Main file path: **`app.py`**
5. **Advanced settings → Python version:** qualquer ≥ 3.11 (ver §2)
6. **Deploy**

A primeira subida instala as dependências e leva alguns minutos. Depois disso,
`git push` republica automaticamente.

---

## 4. Depois de publicar

- [ ] No GitHub, confira que a raiz mostra **pastas** (`src`, `assets`, `docs`,
      `dados`, `pipeline`, `testes`) e **não** dezenas de `.py` soltos
- [ ] Confira que **não há nenhum `.pyc`** no repositório — se houver, o upload
      passou por fora do git (§0)
- [ ] Abra o link e confira que a **Tela 1 carrega inteira**
- [ ] Confirme que o **logo aparece** no cabeçalho. Reserva tipográfica no lugar
      dele significa que `assets/` não subiu
- [ ] Rode os 5 itens manuais do `python verificar.py` na tela publicada — em
      especial o **teste de um metro**, que nenhum comando substitui
- [ ] Confirme que **nenhuma marca do Streamlit** aparece (menu, rodapé, Deploy)
- [ ] Leia `docs/CHECKLIST-PRE-VISITA.md` **antes da primeira visita**

Lembre que **não existe offline**: o Community Cloud hiberna após 12 h sem
tráfego e a probabilidade de o app estar dormindo na visita é **muito alta**
(plano §9, risco 6). O ping automático reduz, não resolve. **Abrir o app 5
minutos antes de entrar na concessionária é requisito de operação, não sugestão.**

---

## 5. Publicar dados novos (Telas 2 e 3)

O snapshot é um arquivo no repositório, então publicar dado é um commit:

```powershell
$git = "$env:LOCALAPPDATA\GitHubDesktop\app-3.5.12\resources\app\git\cmd\git.exe"
python -m pipeline.publicar --conferir    # valida sem publicar
python -m pipeline.publicar               # gera dados/snapshot/snapshot_vN.json
& $git add dados/snapshot
& $git commit -m "snapshot vN: <marcas incluídas>"
& $git push
```

(Se você instalou o git pelo `winget`, use `git` direto, sem a variável.)

O build **reprova** se qualquer validação S1–S13 falhar, e nada é publicado. Isso
é deliberado: um erro claro aqui vale mais que uma tela quebrada na frente do
cliente.

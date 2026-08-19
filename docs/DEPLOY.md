# Colocar o app no ar — Streamlit Community Cloud

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

## 2. O ajuste que decide se o deploy funciona

**`pandas 3.0.3` exige Python ≥ 3.11.**

Ao criar o app no Streamlit Cloud, abra **"Advanced settings"** e escolha
**Python 3.12** ou **3.13**. No padrão antigo (3.9) a instalação falha em
`pandas` e o app não sobe.

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

### 3.1 Instalar o git

Não está instalado nesta máquina. Baixe em <https://git-scm.com/download/win> e
instale com as opções padrão.

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

### 3.3 Criar o repositório

```powershell
git init
git add .
git status          # CONFIRA a lista antes de commitar
git commit -m "Simulador de viabilidade de refil de palhetas"
```

Crie um repositório vazio no GitHub (**sem** README, `.gitignore` ou licença — o
projeto já tem os dois primeiros) e conecte:

```powershell
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/app-viabilidade-refil.git
git push -u origin main
```

**Público ou privado?** O Community Cloud funciona com os dois. O repositório
não contém tabela de preço nem custo — mas contém o `DESIGN.md`, que descreve a
estratégia comercial em detalhe. **Sugiro privado.**

### 3.4 Publicar

1. <https://share.streamlit.io> → **New app** → **From existing repo**
2. Repository: `SEU-USUARIO/app-viabilidade-refil`
3. Branch: `main`
4. Main file path: **`app.py`**
5. **Advanced settings → Python version: 3.13** ← o passo que mais falha
6. **Deploy**

A primeira subida instala as dependências e leva alguns minutos. Depois disso,
`git push` republica automaticamente.

---

## 4. Depois de publicar

- [ ] Abra o link e confira que a **Tela 1 carrega inteira**
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
python -m pipeline.publicar --conferir    # valida sem publicar
python -m pipeline.publicar               # gera dados/snapshot/snapshot_vN.json
git add dados/snapshot
git commit -m "snapshot vN: <marcas incluídas>"
git push
```

O build **reprova** se qualquer validação S1–S13 falhar, e nada é publicado. Isso
é deliberado: um erro claro aqui vale mais que uma tela quebrada na frente do
cliente.

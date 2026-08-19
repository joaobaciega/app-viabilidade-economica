"""Pipeline de publicacao — Python, roda na SUA maquina ou no CI.

FRONTEIRA (a regra mais importante deste pacote):

    pipeline/ NUNCA e importado por src/ nem por app.py.

Ele nao roda no navegador e nao roda dentro do app. E um passo de build:
planilha -> validacao de schema -> snapshot JSON versionado.

testes/test_checklist.py verifica a fronteira por AST.

Plano §6.4: "Alguem renomeia coluna e o app quebra -> VALIDACAO DE SCHEMA NA
PUBLICACAO, com erro claro em vez de tela branca."

Uso:
    python -m pipeline.publicar --planilha dados/planilha_modelo.xlsx
"""

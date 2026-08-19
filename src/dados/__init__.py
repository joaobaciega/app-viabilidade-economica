"""Leitura do snapshot publicado.

FRONTEIRA (plano §6.4, DESIGN P11): a Tela 1 NUNCA importa nada daqui. Ela nao
le planilha e nao faz nenhuma requisicao externa. Somente as Telas 2 e 3
consomem o snapshot que o pipeline publicou.

testes/test_checklist.py verifica por AST que src/telas/tela1_simulador.py nao
importa este pacote.
"""

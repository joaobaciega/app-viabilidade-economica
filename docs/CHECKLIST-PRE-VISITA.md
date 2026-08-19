# Checklist pré-visita

**Este documento é a mitigação do risco mais provável do projeto.**

O plano §9 classifica *"app dormindo no início da reunião"* com probabilidade
**muito alta** e impacto **alto**. Não é um risco de software: é o Streamlit
Community Cloud hibernando após 12 h sem tráfego. Um app de vendas usado duas ou
três vezes por semana estará dormindo **em quase toda visita** — e isso acontece
mesmo com wi-fi excelente.

Não existe correção no código. A correção é este checklist.

---

## Antes de sair

- [ ] **Abrir o app e confirmar que a Tela 1 carregou.** Não basta abrir: espere
      ver os três botões de cenário. Se aparecer a tela do provedor com
      *"Yes, get this app back up!"*, o servidor estava dormindo — espere subir.
- [ ] **Fazer isso 5 minutos antes de entrar na concessionária**, não na porta.
- [ ] Confirmar que o tablet tem **internet própria**: chip 4G ou roteamento
      pelo celular. O wi-fi da concessionária não conta.
- [ ] Bateria acima de 50%.

## Por que a internet própria não é opcional

**Não existe modo offline neste app.** O Streamlit renderiza no servidor e o
navegador só mantém um websocket: sem conexão, a tela morre — não fica degradada
(plano §6.2, DESIGN §1 e §7.1).

O plano §6.5 registra a troca: offline sai do plano e conectividade vira
**requisito de equipamento**, a ~R$ 50/mês por vendedor. E resolve **mais** do
que um app offline resolveria, porque também faz funcionar o botão "ver no
Mercado Livre" da Tela 3, que depende de rede em qualquer arquitetura.

O app tem um ping automático que reduz a hibernação, mas ele **não substitui**
abrir o app antes. Não confie nele.

## Se a rede cair no meio da reunião

O último resultado **permanece na tela**. O aviso de desconexão do Streamlit
aparece neutralizado, em cinza, no rodapé — junto à faixa do vendedor, onde o
cliente não lê (§5.14).

Não é modo offline. É a queda não virar cena. Enquanto isso:

1. Não recarregue a página — você perde os valores digitados (eles nunca são
   salvos, de propósito).
2. Ative o roteamento pelo celular.
3. O PDF já baixado continua no aparelho.

## Antes de cada cliente novo

- [ ] Toque em **`novo cliente`**, no canto inferior direito. Limpa preço, custo,
      âncora e deduções, sem confirmação.

Preço e custo **nunca** são salvos: eles não sobrevivem a recarregar a página, e
não existe nenhum default. Isso é deliberado — o custo de aquisição da
concessionária é o preço de venda da Suicatech, e o app tem link aberto sem login
(plano §6.3, DESIGN §5.2).

## O que dizer se o cliente perguntar dos números em aberto

Três premissas estão marcadas com ⚠️ na tela porque ainda não foram decididas, e
o app **não escolhe um número plausível** para nenhuma:

| Marcador | O que dizer |
|---|---|
| `rampa e sazonalidade ⚠️ não aplicadas` | *"O anual aqui é o mês em regime × 12. Não estou aplicando curva de aprendizado nem sazonalidade — palheta é produto de chuva, e eu prefiro te mostrar o número sem essa curva do que te mostrar uma curva que eu inventei."* |
| `≈ derivado` no traseiro | *"O aproveitamento do dianteiro é medido em 15+ concessionárias da nossa carteira. O do traseiro, só a média. Os extremos são derivados na mesma proporção, e estão marcados como derivados justamente para você não confundir com o que foi medido."* |
| Bloco de códigos em aberto (Tela 3) | *"O número exato de códigos que cobrem 97% do mercado eu te confirmo — não vou chutar."* |

Admitir o que não se sabe é coerente com a tese da tela, que é *"confira você
mesmo"*. É o oposto de fraqueza: é o que torna o resto conferível.

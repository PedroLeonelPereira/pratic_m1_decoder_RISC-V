# 06 — Arquivos, listagens, custo e fluxo final

**What to build:** como estudante, escolho o arquivo, vejo conflitos separados entre dados e controle, recebo os dois arquivos corrigidos no mesmo formato da entrada com listagens legíveis e vejo o relatório de custo comparando as duas técnicas.

**Blocked by:** 03 — Correção só com nops de dados e de controle; 05 — Reordenação intra-bloco com slot útil.

**Status:** ready-for-agent

- [ ] Dois arquivos gerados no mesmo formato da entrada, cada um com sua listagem legível contendo endereço, código de máquina, instrução desmontada e marcação do que foi inserido ou movido
- [ ] Relatório de custo no console com contagem original, contagem final, acrescentadas e percentual por técnica, comparando só nops contra reordenação no formato canônico
- [ ] Fluxo completo escolher arquivo, mostrar conflitos separados, gerar um arquivo por técnica e exibir sobrecusto funciona de ponta a ponta
- [ ] Quatro casos próprios cobertos: cadeia sem independente, laço com desvio para trás, desvio para frente e caso onde a reordenação elimina todos os nops; códigos da lista de exercícios batem o mínimo conhecido
- [ ] Código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações novas além de módulos locais

# 05 — Reordenação intra-bloco com slot útil

**What to build:** como estudante, obtenho um segundo programa corrigido que reordena instruções dentro do bloco básico para preencher o slot com instrução útil sempre que houver candidata correta, completando com nops só onde a reordenação não resolver, sem nunca alterar o resultado do programa.

**Blocked by:** 02 — Detecção de conflitos de controle, blocos básicos e borda; 04 — Recálculo de endereços e reescrita de desvios e saltos.

**Status:** ready-for-agent

- [ ] Reordenação limitada ao mesmo bloco básico; única travessia admitida é instrução vinda de antes do desvio para o slot, correta nos dois caminhos
- [ ] Candidata preserva leitura após escrita, escrita após leitura, escrita após escrita e ordem de acessos à memória que possam se sobrepor; mesma base com deslocamentos diferentes conta como distinto
- [ ] Após mover para o slot, início dos dois caminhos reverificado e conflito novo corrigido; onde não houver candidata, completa com nops
- [ ] Redução de nops face à técnica só com nops sem alterar o resultado; programa final sem conflito restante
- [ ] Código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações novas além de módulos locais

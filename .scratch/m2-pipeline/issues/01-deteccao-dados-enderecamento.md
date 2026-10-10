# 01 — Endereçamento sequencial e detecção de conflitos de dados

**What to build:** como estudante, a partir do mesmo arquivo da M1 vejo cada instrução com endereço sequencial e a lista de conflitos de dados no console com endereço do produtor e do consumidor, registrador envolvido, distância e nops necessários, considerando só leitura após escrita com o produtor mais recente.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Cada instrução do arquivo ganha endereço sequencial a partir da base canônica com passo fixo; linhas puladas não ocupam endereço e inválidas nunca produzem nem consomem registrador
- [ ] Conflito só quando distância é 1 (2 nops) ou 2 (1 nop); distância 3 ou mais não conflita; registrador zero nunca conflita
- [ ] Leitura e escrita respeitam o formato real (armazenamento e desvio condicional leem dois e não escrevem; constante escreve sem ler); campo destino inexistente nunca gera conflito
- [ ] Saída de dados no formato canônico com produtor, consumidor, registrador, distância e nops; escrita após leitura e escrita após escrita não aparecem como conflito
- [ ] Código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações novas além de módulos locais

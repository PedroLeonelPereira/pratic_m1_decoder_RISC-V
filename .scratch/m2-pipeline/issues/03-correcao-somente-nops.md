# 03 — Correção só com nops de dados e de controle

**What to build:** como estudante, obtenho um programa corrigido só com nops, sem mudar a ordem das instruções, onde nenhum conflito de dados permanece e cada slot de atraso está preenchido com nop.

**Blocked by:** 01 — Endereçamento sequencial e detecção de conflitos de dados; 02 — Detecção de conflitos de controle, blocos básicos e borda.

**Status:** ready-for-agent

- [ ] Menor número possível de nops inseridos entre produtor e consumidor sem alterar a ordem; após inserir, nenhum conflito de dados permanece
- [ ] Cada slot de atraso de desvio preenchido com o nop canônico; nenhuma instrução original removida ou movida
- [ ] Programa corrigido decodifica de volta na M1 instrução por instrução com os mesmos mnemônicos
- [ ] Código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações novas além de módulos locais

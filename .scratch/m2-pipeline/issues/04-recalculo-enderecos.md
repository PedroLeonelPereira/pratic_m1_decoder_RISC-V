# 04 — Recálculo de endereços e reescrita de desvios e saltos

**What to build:** como estudante, após cada nop inserido ou instrução movida vejo todos os endereços seguintes deslocados e cada instrução de desvio e salto reescrita em linguagem de máquina apontando para o mesmo alvo correto de antes.

**Blocked by:** 03 — Correção só com nops de dados e de controle.

**Status:** ready-for-agent

- [ ] Endereços refeitos em ordem após cada inserção ou movimento antes de qualquer recálculo de deslocamento
- [ ] Deslocamento novo calculado como alvo menos endereço da instrução que desvia ou salta e remontado no campo embaralhado de cada formato por concatenação de texto
- [ ] Instrução reescrita decodifica de volta para o mesmo mnemônico e o mesmo alvo; arquivo corrigido é legível de volta pelo decodificador da M1
- [ ] Código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações novas além de módulos locais

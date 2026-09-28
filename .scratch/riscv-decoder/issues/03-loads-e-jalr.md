# 03 — Loads e jalr

**What to build:** como estudante, consigo decodificar cargas (`lb`, `lh`, `lw`, `lbu`, `lhu`) e `jalr` vendo registrador destino, base em ABI e deslocamento com sinal no formato de memória e no assembly correspondente.

**Blocked by:** 01 — Fundação didática e tipo R de ponta a ponta.

**Status:** done

- [x] Loads resolvidos por funct3 com condicionais, assembly no formato registrador mais deslocamento entre parênteses
- [x] `jalr` exige funct3 de zeros, resto é inválida sem campos
- [x] Verificação ponta a ponta via arquivo com deslocamento positivo e negativo

## Comments

- Implementado em `src/riscv_decoder/decoder.py`: `resolver_mnemonico_load`, `decodificar_load`, `decodificar_jalr` + despacho em `decodificar_e_mostrar`.
- Verificado via seam principal (11 casos: lb/lh/lw/lbu/lhu, jalr +-deslocamento, funct3 inválidos, regressão R/I) e ponta a ponta via arquivo (hex e binário, `0x00c12503` -> `lw a0,12(sp)`, deslocamento -1 e -4, linhas inválidas não abortam).

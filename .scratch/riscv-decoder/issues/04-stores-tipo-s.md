# 04 — Stores tipo S

**What to build:** como estudante, consigo decodificar armazenamentos (`sb`, `sh`, `sw`) vendo os dois registradores origem em ABI e o imediato dividido remontado por concatenação, com assembly no formato de memória.

**Blocked by:** 01 — Fundação didática e tipo R de ponta a ponta.

**Status:** done

- [x] Stores resolvidos por funct3 com condicionais, sem campo de destino na saída
- [x] Imediato dividido remontado na ordem arquitetural antes da conversão com sinal
- [x] Verificação ponta a ponta via arquivo com deslocamento positivo e negativo

## Comments

- Implementado em `src/riscv_decoder/decoder.py` (`resolver_mnemonico_s`, `decodificar_tipo_s`).
- Verificado via regressao: `sb t1,8(s0)` e `sw a2,-4(sp)` decodificam sem `rd`.

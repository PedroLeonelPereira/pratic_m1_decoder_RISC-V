# 05 — Branches tipo B

**What to build:** como estudante, consigo decodificar desvios (`beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu`) vendo os dois registradores em ABI e o deslocamento embaralhado remontado com sinal, com assembly de comparação mais deslocamento.

**Blocked by:** 01 — Fundação didática e tipo R de ponta a ponta.

**Status:** done

- [x] Branches resolvidos por funct3 com condicionais explícitas
- [x] Imediato embaralhado remontado por concatenação na ordem arquitetural antes da conversão com sinal
- [x] Verificação ponta a ponta via arquivo com deslocamento para trás (negativo) e para frente

## Comments

- Implementado em `src/riscv_decoder/decoder.py` (`resolver_mnemonico_b`, `decodificar_tipo_b`).
- Verificado via regressao: `beq t0,t1,12` e `bne s0,s1,-12` decodificam com deslocamento com sinal.

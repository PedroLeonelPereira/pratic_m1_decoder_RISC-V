# 02 — Instruções I aritméticas e deslocamentos

**What to build:** como estudante, consigo decodificar do mesmo arquivo as operações imediatas (`addi`, `slti`, `sltiu`, `xori`, `ori`, `andi`) e os deslocamentos (`slli`, `srli`, `srai`) vendo imediato em decimal com sinal e funct7 só quando existir para shifts, com a mesma saída que omite ausentes e o mesmo assembly por família.

**Blocked by:** 01 — Fundação didática e tipo R de ponta a ponta.

**Status:** done

- [x] Imediato do tipo I remontado por concatenação de texto e convertido com sinal por laço simples
- [x] Shifts distinguem mnemônico por funct3 mais funct7 com condicionais explícitas
- [x] Imediatos positivo, negativo e zero verificados de ponta a ponta via arquivo

## Comments

- Implementado em `src/riscv_decoder/decoder.py` (`resolver_mnemonico_i`, `decodificar_tipo_i`).
- Verificado via regressao: `addi 12`/`addi -1`, `slli`, `srai` decodificam com `imm` e `f7` so nos shifts.

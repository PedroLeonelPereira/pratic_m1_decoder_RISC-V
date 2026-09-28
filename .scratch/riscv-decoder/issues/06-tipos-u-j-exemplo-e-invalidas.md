# 06 — Tipos U e J mais arquivo exemplo e inválidas

**What to build:** como estudante, consigo decodificar `lui`, `auipc` e `jal` com imediato alto ou deslocamento, e validar o programa inteiro com o arquivo de exemplo das 20 instruções conhecidas nos dois alfabetos, vendo que qualquer opcode ou combinação funct desconhecida e qualquer caractere fora do alfabeto imprime só a marca de inválida sem abortar.

**Blocked by:** 02 — Instruções I aritméticas e deslocamentos; 03 — Loads e jalr; 04 — Stores tipo S; 05 — Branches tipo B.

**Status:** done

- [x] `lui`, `auipc` e `jal` decodificados sem funct3/funct7 na saída, com assembly de registrador mais valor
- [x] Arquivo de exemplo com as 20 instruções conhecidas decodifica de ponta a ponta nos dois alfabetos
- [x] Inválidas por opcode, funct ou caractere imprimem só a marca, omitem campos e não interrompem o arquivo

## Comments

- Implementado em `src/riscv_decoder/decoder.py`: `decodificar_lui`, `decodificar_auipc`, `decodificar_tipo_j` + despacho em `decodificar_e_mostrar`.
- Verificado via seam principal (lui/auipc/jal +-deslocamento, zero, opcode e funct invalidos) e ponta a ponta via `exemplo_hex.txt` e `exemplo_bin.txt` (20/20 nos dois alfabetos, misto com invalidas nao aborta).
- Review: standards 0 hard violations; spec sem faltas nem creep.

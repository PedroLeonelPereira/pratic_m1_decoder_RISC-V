# 01 — Fundação didática e tipo R de ponta a ponta

**What to build:** como estudante, consigo informar um arquivo com uma instrução `0x` ou binária por linha e ver decodificada uma instrução tipo R (`add`, `sub`, `sll`, `slt`, `sltu`, `xor`, `srl`, `sra`, `or`, `and`) com formato, mnemônico, registradores em nome ABI, funct3/funct7 e linha em assembly, omitindo o imediato que não existe; linhas vazias e de comentário são ignoradas, resto é marca de inválida sem quebrar o laço; todo o código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações não aprovadas, com as regras registradas no guia de agentes.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Arquivo lido via caminho pedido interativamente, uma instrução por linha, hex com prefixo ou binário completado à esquerda até 32 bits
- [x] Tipo R resolvido por opcode mais funct3/funct7 com condicionais encadeadas, registradores em ABI, assembly com três registradores
- [x] Saída genérica omite campos inexistentes; inválida imprime só a marca e o laço continua
- [x] Nenhuma anotação de tipagem, nenhum operador binário, nenhuma importação nova no código deste ticket

## Comments

- Implementado em `src/riscv_decoder/decoder.py` (`programa_principal`, `identificar_tipo`, `resolver_mnemonico_r`, `decodificar_tipo_r`, `mostrar_resultado`), `utils.py` (`normalizar_linha`, `hex_to_bin`, `completar_32`) e `config.py` (`tabela_abi`); regras no `AGENTS.md`.
- Verificado via regressao: `add`/`sub` decodificam, `0x1` completa a esquerda, vazio e `#` pulam.

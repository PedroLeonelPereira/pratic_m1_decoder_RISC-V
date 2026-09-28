## Regras do projeto — decodificador RV32I simples e didático

Público: pessoa com conhecimento básico em lógica de programação. Código verboso e explícito é melhor que código curto e esperto. Se precisar, estenda o código, mas não complique a lógica.

### Proibido (quebra de padrão)

- Operadores binários: `&`, `|`, `^`, `~`, `<<`, `>>`.
- Sintaxe de tipagem: `x: int`, `-> str`, `typing.*`. Nenhuma anotação de tipo.
- Import de biblioteca externa ou da biblioteca padrão sem perguntar antes. `open`, `print`, `input`, `len`, `int`, `str` são liberados sem importar.

### Permitido (subconjunto simples)

- `if/elif/else`, `for`, `while`, `def`, `return`, `try/except ValueError` (só para validar a entrada sem quebrar o programa).
- Comparação `==`, `!=`, `<`, `>`, aritmética decimal simples `+`, `-`, `*`.
- Texto: indexação, concatenação com `+`, `split`, `join`, `strip`, fatiamento para leitura de campos. Prefira sempre a sintaxe `[x:y]` para recortar trechos de strings.
- Embutidas elementares: `len()`, `int()` (decimal; base 16 só na leitura de hex, base 2 só na validação de binário), `str()`, `open()`, `print()`, `input()`, `format()` (só `"b"` para gerar binário).
- `dict` somente para a tabela de nomes ABI, quando for mais simples que `if/elif`.
- Import entre arquivos locais do projeto (`main`, `decoder`, `entrada`, `instrucoes`, `cpi`, `config`, `pseudo`) liberado, para não duplicar código. Rode da raiz do projeto com `python src/riscv_decoder/main.py`.

### Domínio

- Só RV32I base, menos `fence`, `ecall`, `ebreak`.
- Entrada: arquivo texto, uma instrução por linha. Prefixo `0x` = hex, senão binário. Linha vazia e `#` pulam. Completa à esquerda até 32 bits.
- Saída: função genérica mostra só campos existentes na ordem `formato, mnemonico, rd, rs1, rs2, imm, f3, f7` + linha `assembly`. Inválida imprime só `instrucao invalida`.
- Registradores em nome ABI, imediato em decimal com sinal.

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

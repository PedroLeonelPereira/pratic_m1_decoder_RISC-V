# 01 — Pseudo-instruções comuns nop, mv, j e ret

**What to build:** como estudante, após ver a instrução real decodificada (formato, mnemônico, registradores em nome ABI, imediato, funct3/funct7 e assembly), vejo uma linha extra com a pseudo-instrução comum quando o código corresponde a `nop`, `mv`, `j` (incluindo `j 0`) ou `ret`; quando não corresponde, nada extra aparece e inválida continua só com a marca de inválida.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Instrução real somando zero em destino zero mostra pseudo de operação vazia, com prioridade sobre cópia
- [ ] Soma com imediato zero e origem e destino diferentes de zero mostra pseudo de cópia entre registradores; soma com imediato não-zero e soma com destino zero fora do caso vazio não mostram pseudo
- [ ] Salto com ligação e destino zero mostra pseudo de salto incondicional, incluindo deslocamento zero; salto com destino diferente de zero não mostra pseudo
- [ ] Retorno indireto com destino zero, origem no registrador de retorno e deslocamento zero mostra pseudo de retorno; origem diferente do registrador de retorno não mostra pseudo
- [ ] Saída real inalterada antes da linha pseudo, linha pseudo no formato canônico, arquivo de exemplo só com os 4 positivos decodifica com a linha extra
- [ ] Código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações novas além de módulos locais

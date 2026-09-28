Status: ready-for-agent

# Spec — Identificação de pseudo-instruções comuns (nop, mv, j, ret)

## Problem Statement

Sou estudante e já consigo ver a instrução real decodificada (formato, mnemônico, registradores em nome ABI, imediato, funct3/funct7 e assembly), mas nos exemplos de sala e simuladores aparecem nomes curtos como `nop`, `mv`, `j` e `ret` que não entendo de onde vêm. Quero que o decodificador me mostre, além da instrução real, qual pseudo-instrução comum aquele código representa, para que eu ligue o código de máquina ao vocabulário usado em aula sem perder a informação real.

## Solution

Após decodificar e mostrar a instrução real normalmente, o programa identifica se ela corresponde a uma das 4 pseudo-instruções mais comuns e imprime uma linha extra `pseudo: ...` logo depois. Se não houver correspondência, nada extra é impresso. Instrução inválida continua imprimindo só a marca de inválida, sem linha pseudo. `j 0` conta como pseudo válida.

## User Stories

1. Como estudante, quero ver `pseudo: nop` quando a instrução for `addi zero,zero,0`, para que eu entenda que aquele código é uma operação vazia.
2. Como estudante, quero ver `pseudo: mv a0,a1` quando a instrução for `addi a0,a1,0` com origem e destino diferentes de zero, para que eu entenda a cópia entre registradores.
3. Como estudante, quero ver `pseudo: j 8` quando a instrução for `jal zero,8`, para que eu entenda o salto incondicional.
4. Como estudante, quero ver `pseudo: j 0` quando a instrução for `jal zero,0`, para que eu entenda que laço infinito também é salto.
5. Como estudante, quero ver `pseudo: ret` quando a instrução for `jalr zero,0(ra)`, para que eu entenda o retorno de função.
6. Como estudante, quero que `addi zero,zero,0` mostre só `nop` e não `mv zero,zero`, para que eu não me confunda com duas respostas.
7. Como estudante, quero que `addi a0,zero,5` não mostre pseudo, para que eu não confunda valor imediato com cópia.
8. Como estudante, quero que `addi zero,a1,0` não mostre pseudo, para que eu aprenda que destino zero descarta o resultado.
9. Como estudante, quero que `jalr zero,0(t1)` não mostre pseudo, para que eu aprenda que só o retorno pelo registrador de retorno é `ret`.
10. Como estudante, quero que `jal ra,8` não mostre pseudo, para que eu aprenda que salto com ligação não é `j`.
11. Como estudante, quero que a saída real (formato, mnemônico, registradores em nome ABI, imediato, funct3/funct7 e assembly) continue igual antes da linha pseudo, para que eu não perca a informação real.
12. Como estudante, quero que instrução inválida imprima só a marca de inválida sem linha pseudo, para que o erro continue óbvio.

## Implementation Decisions

- Seam de teste: uma única seam no ponto mais alto possível — da instrução real já decodificada (mnemônico, registrador destino, registrador origem, imediato em texto/decimal) para o texto pseudo (`nop`, `mv ...`, `j ...`, `ret` ou vazio). Reusa a seam principal existente (linha normalizada de 32 caracteres até saída impressa); nenhuma seam nova além da função pura de identificação.
- Novo módulo local para a identificação, importado pelos módulos locais existentes sem duplicar código, sem caminhos ou trechos de código nesta spec.
- Uma única função pura de identificação que recebe mnemônico real mais nomes ABI e imediato e devolve texto pseudo pronto ou vazio, com condicionais encadeadas explícitas e comparação de texto, sem operadores binários e sem anotação de tipagem.
- Regras travadas: `nop` tem prioridade sobre `mv`; `mv` só com imediato zero e origem e destino diferentes de zero; `j` com destino zero incluindo deslocamento zero; `ret` só com destino zero, origem igual ao registrador de retorno e deslocamento zero.
- Integração sem tocar a impressão genérica: cada rotina de decodificação dos tipos já cobertos chama a identificação depois de mostrar o resultado real e imprime a linha extra só quando o retorno não é vazio.
- Restrições de linguagem herdadas: só condicionais, repetições, funções, comparação, aritmética decimal simples, texto por fatiamento e concatenação e embutidas elementares; proibidos operadores binários, tipagem e imports novos sem pergunta.

## Testing Decisions

- O que faz um bom teste aqui: só comportamento externo observável (dada uma linha de arquivo, qual texto sai incluindo ou não a linha pseudo), nunca detalhes internos.
- O que será testado: a seam única com os 4 positivos (nop, mv, j com deslocamento positivo, j com deslocamento zero, ret) e os negativos (imediato não-zero, destino zero fora do nop, jalr com origem diferente do registrador de retorno, jal com destino diferente de zero); ponta a ponta com arquivo de exemplo só com os 4 positivos conferindo que a saída real vem antes da linha pseudo e que inválida não ganha linha pseudo.
- Prior art: primeiro conjunto de testes do repositório será entrada e saída esperada lado a lado por iniciante; este segue o mesmo estilo, sem framework novo.

## Out of Scope

- `li` (precisaria de duas instruções `lui` + `addi` e a entrada é uma linha por instrução), `jr` genérico, `beqz`/`bnez` e família, `neg`, `not` e qualquer outra pseudo além das 4.
- Trocar mnemônico ou assembly real pelo pseudo; o real sempre permanece.
- Instruções de sistema, extensões, comprimidas ou largura diferente de 32 bits.
- Mudança no formato da saída real, na normalização de entrada ou nas regras de simplicidade.

## Further Notes

- Vocabulário: instrução, formato, opcode, mnemônico, registrador destino/origem, imediato, assembly, nome ABI, instrução inválida, pseudo-instrução.
- Decisão de `j 0` como pseudo confirmada com o usuário na sessão de grilling.

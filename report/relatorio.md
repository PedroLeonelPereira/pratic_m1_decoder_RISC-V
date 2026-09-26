# Relatório técnico — Decodificador de Instruções RISC-V, Etapa 1

## Objetivo e escopo

O programa lê uma ROM textual de instruções RISC-V de 32 bits, decodifica cada palavra e apresenta uma listagem com assembly e estatísticas. O [enunciado oficial](../Arq2_PraticaM1_Decodificador_RISCV.pdf) define R1–R5. O decoder cobre o [conjunto base RV32I](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html) e não há análise de hazards nesta etapa.

## Atendimento aos requisitos

| Requisito | Implementação |
| --- | --- |
| R1 | Parser de ROM hexadecimal ou binária, detecção por largura, comentários e linhas vazias, `0x`, PC configurável com incremento de quatro bytes. |
| R2 | Tabela declarativa com os 40 mnemônicos RV32I nos seis formatos, mais a variante `fence.tso`; validação de opcode, funct3 e bits altos quando necessários; codificações desconhecidas não interrompem a listagem. |
| R3 | Modelo com campos opcionais conforme formato; reconstrução e extensão de sinal de imediatos I/S/B/U/J. A instrução B de teste não recebe `rd`. |
| R4 | Listagem com palavra, PC, campos, nomes ABI e assembly; destinos absolutos `PC + imediato` para B/J; reconhecimento de pseudoinstruções de uma palavra. |
| R5 | Contagem e percentuais por formato, e CPI médio ponderado a partir de classes e valores fornecidos em JSON. |

## Decodificação e extensão futura

`Instruction` separa palavra de máquina e dados decodificados da representação em assembly. Somente campos existentes recebem valores; os demais permanecem `None`. A distinção é essencial para evitar falsas dependências de registradores na Etapa 2. Bits 31–25 das instruções de deslocamento imediato validam a codificação, mas não são expostos como campo `funct7` do formato I. `fence`, `ecall` e `ebreak` também não expõem `rd` ou `rs1` como operandos de registrador.

## Testes executados

`python3 -m unittest discover -s tests -v` cobre parser, campos dos seis formatos, diferenciação por opcode/funct3/funct7, imediatos com sinal, pseudoinstruções, destinos absolutos, palavras inválidas e estatísticas. As ROMs `examples/teste_hex.txt` e `examples/teste_bin.txt` contêm pelo menos uma instrução de cada formato e um `beq` com deslocamento `-8`. O caso `0xFE628CE3` resulta em `beq`, `rs1=5`, `rs2=6`, imediato `-8` e `rd=None`. `examples/casos_invalidos.txt` demonstra continuidade depois de palavras inválidas.

## Critério para palavras inválidas

Por decisão do projeto, explicitada no README, palavras inválidas são contadas separadamente. Os percentuais por formato consideram somente instruções válidas; o CPI considera somente instruções válidas com classe configurada. O PDF não estabelece esse critério de denominador.

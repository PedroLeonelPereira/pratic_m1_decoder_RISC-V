# Decodificador RISC-V

Vocabulário usado pelo projeto para descrever palavras de máquina e as instruções RV32I que elas representam.

## Linguagem

**Palavra de instrução**:
Valor de 32 bits lido da ROM, ainda sem interpretação dos campos e do mnemônico.
_Evitar_: linha de assembly (antes da decodificação)

**Instrução decodificada**:
Interpretação válida de uma palavra de instrução, com formato, mnemônico e os campos definidos por esse formato.
_Evitar_: palavra decodificada (quando se quer falar da interpretação, e não do valor de máquina)

**Formato da instrução**:
Uma das seis organizações de campos R, I, S, B, U ou J usadas pelo conjunto coberto.
_Evitar_: tipo da instrução (pode ser confundido com a classe de CPI)

**Pseudoinstrução**:
Forma de assembly abreviada que representa uma instrução real, sem alterar a palavra de máquina.
_Evitar_: mnemônico real (para o alias apresentado)

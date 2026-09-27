# Decodificador de Instruções RISC-V — Etapa 1

Implementação em Python 3.11+ da Etapa 1 da Avaliação Prática M1 de Organização de Computadores (UNIVALI). A referência dos requisitos R1–R5 é o [enunciado oficial](Arq2_PraticaM1_Decodificador_RISCV.pdf). Esta etapa decodifica instruções; não analisa hazards.

## Executar

Não há dependências externas. Use uma instalação de Python 3.11 ou superior:

```bash
python3 main.py examples/teste_hex.txt --cpi-table examples/cpi_demonstracao.json
python3 main.py examples/teste_bin.txt --base-address 0x1000 --cpi-table examples/cpi_demonstracao.json
python3 main.py examples/casos_invalidos.txt --cpi-table examples/cpi_demonstracao.json
```

O arquivo ROM contém uma palavra de 32 bits por linha: oito dígitos hexadecimais ou 32 dígitos binários. A largura determina o formato automaticamente. O prefixo `0x` é aceito em hexadecimal. Linhas vazias e comentários iniciados por `#`, `//` ou `;` são ignorados; comentários também podem aparecer após a palavra. Os PCs começam em zero ou no endereço indicado por `--base-address` e avançam quatro bytes por palavra processada. Uma linha textual malformada produz erro com seu número; uma palavra de 32 bits com codificação desconhecida aparece como inválida e não interrompe o processamento.

## Tabela de CPI

`--cpi-table` recebe um arquivo JSON com duas relações independentes dos formatos R/I/S/B/U/J:

```json
{
  "class_cpi": {"classe_exemplo_a": 1.0, "classe_exemplo_b": 3.0},
  "mnemonic_class": {"addi": "classe_exemplo_a", "sw": "classe_exemplo_b"}
}
```

Os nomes e valores acima são apenas uma demonstração do formato; não representam a tabela de CPI da disciplina. Substitua-os pelas classes e valores fornecidos para a análise. Um mnemônico sem entrada em `mnemonic_class` não participa do CPI médio. Uma classe indicada em `mnemonic_class` precisa existir em `class_cpi`.

**Decisão de projeto para palavras inválidas:** o PDF não define sua participação no relatório estatístico. A saída informa separadamente palavras processadas, instruções válidas e palavras inválidas. Os percentuais por formato usam somente instruções válidas como denominador. O CPI médio ponderado usa somente instruções válidas com classe de CPI configurada; a saída informa também essa quantidade. Se nenhuma instrução tiver classe configurada, o CPI é mostrado como `indisponível`. Essa é uma decisão acordada para o projeto, não um requisito atribuído ao PDF.

## Instruções suportadas

A tabela declarativa em `src/decoder/instruction_table.py` contém os 40 mnemônicos do conjunto base RV32I, conforme a [especificação oficial](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html). Também reconhece `fence.tso`, uma codificação de `fence` definida nessa base. Não inclui extensões como M, A, C, Zicsr ou Zifencei. Codificações dessas extensões são informadas como inválidas. A tabela pode ser estendida com novas definições sem misturar regras de opcode, `funct3` e `funct7` com a apresentação da saída.

Pseudoinstruções comuns de uma única palavra são reconhecidas conforme o [manual oficial de assembly](https://github.com/riscv-non-isa/riscv-asm-manual/blob/main/src/asm-manual.adoc): `nop`, `ret`, `li` quando cabe em `addi`, `mv`, `not`, `neg`, `zext.b`, `seqz`, `snez`, `sltz`, `sgtz`, aliases de branch com zero, aliases com operandos invertidos, `j`, `jr` e formas abreviadas de `jal`/`jalr`. O mnemônico real permanece no modelo. Para preservar os exemplos explícitos do enunciado, a linha `Assembly` mostra a instrução original quando a abreviação é opcional, e a linha `Pseudo` mostra o alias reconhecido. `nop` e `ret` permanecem na linha `Assembly`, como exigido no enunciado. Pseudoinstruções que exigem mais de uma palavra não são inferidas a partir de uma instrução isolada.

`fence`, `ecall` e `ebreak` usam codificação de tipo I, mas não possuem operandos de registrador semanticamente válidos. Seus campos `rd` e `rs1` ficam ausentes no modelo; `fence` expõe os conjuntos predecessor/sucessor e o modo de ordenação separadamente.

## Testes e organização

```bash
python3 -m unittest discover -s tests -v
```

`src/parser` transforma texto em pares PC/palavra. `src/decoder` contém tabela, decodificação e imediatos. `src/models/instruction.py` cria um dicionário com todos os dados da instrução; campos que não existem no formato ficam como `None`. `src/assembler` gera assembly com nomes ABI, `src/statistics` calcula R5, e `src/output.py` formata a listagem. `main.py` apenas coordena essas partes. O dicionário preserva os dados necessários para a futura Etapa 2, sem implementar análise de hazards agora.

O código-fonte usa funções, condicionais, laços, listas e dicionários para facilitar a apresentação por quem está aprendendo Python. A tabela de instruções é uma lista de dicionários: cada item nomeia o mnemônico, o formato e os bits que identificam a codificação. A configuração de CPI também é um dicionário. Erros de entrada são apresentados com uma mensagem em `ValueError`.

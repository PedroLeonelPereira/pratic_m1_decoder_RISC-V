Status: done

# Spec — Decodificador RV32I em Python simples e didático

## Problem Statement

Sou estudante e preciso de um decodificador de instruções RV32I em Python que eu consiga ler, explicar e modificar com conhecimento básico de lógica de programação. Quero passar um arquivo com uma instrução por linha (em hexadecimal ou binário) e ver para cada linha o formato, o mnemônico, os registradores em nome ABI, o imediato, funct3/funct7 e a linha em assembly. O código atual está incompleto (só trata tipo R, tabelas ausentes, entrada como inteiros em código) e usa construções avançadas para um iniciante. Preciso de um programa completo, extremamente simples, sem operadores binários e sem dependências, que trate todas as instruções da base menos sistema e nunca quebre com entrada inválida.

## Solution

Um programa que pergunta o caminho de um arquivo texto via entrada interativa, lê uma instrução por linha, normaliza cada linha para uma sequência de 32 caracteres binários usando só manipulação de texto, identifica o formato pelo opcode, resolve o mnemônico por funct3/funct7 com condicionais encadeadas, extrai registradores e imediato como texto, converte registradores para nomes ABI e imediato para decimal com sinal, e imprime por instrução só os campos que existem mais a linha em assembly. Instrução inválida imprime só a marca de inválida. Todo o código usa só condicionais, repetições, funções básicas e manipulação de texto, sem anotação de tipagem, com imports só entre arquivos locais do projeto e conversão de base só na leitura de hex.

## User Stories

1. Como estudante, quero informar o caminho de um arquivo texto quando o programa perguntar, para que eu não precise editar código para trocar a entrada.
2. Como estudante, quero escrever uma instrução hexadecimal com prefixo `0x` por linha, para que eu possa colar valores de simuladores e listas de exercício.
3. Como estudante, quero escrever uma instrução binária de 32 caracteres por linha, para que eu possa exercitar a leitura bit a bit.
4. Como estudante, quero que linhas vazias sejam ignoradas silenciosamente, para que eu possa espaçar meu arquivo de teste.
5. Como estudante, quero que linhas de comentário sejam ignoradas, para que eu possa anotar meu arquivo de entrada.
6. Como estudante, quero que hexadecimal curto seja completado com zeros à esquerda até 32 bits, para que `0x1` funcione sem eu calcular o preenchimento.
7. Como estudante, quero que binário curto seja completado com zeros à esquerda até 32 bits pela função de formatação existente, para que o comportamento seja previsível.
8. Como estudante, quero ver o formato da instrução (tipo R, I, S, B, U, J e variantes de load/jalr/lui/auipc), para que eu aprenda a classificar pelo opcode.
9. Como estudante, quero ver o mnemônico resolvido (por exemplo `add`, `sub`, `lw`, `beq`, `jal`), para que eu associe opcode/funct ao nome da operação.
10. Como estudante, quero ver registradores em nome ABI (`zero`, `ra`, `sp`, `a0`, `t0` e demais), para que eu aprenda o vocabulário usado em sala e nos simuladores.
11. Como estudante, quero ver o imediato em decimal com sinal quando o formato tiver imediato, para que eu entenda extensão de sinal sem fazer conta manual.
12. Como estudante, quero ver funct3 e funct7 em binário quando o formato tiver esses campos, para que eu confira a tabela à mão.
13. Como estudante, quero que campos inexistentes nem apareçam na saída, para que eu não confunda `imm` de `add` com zero.
14. Como estudante, quero ver a linha final em assembly (`add a1,a1,a2`, `lw a0,12(sp)`, `beq t0,t1,-12` e demais por tipo), para que eu confira meu entendimento de uma vez.
15. Como estudante, quero que instrução com opcode ou combinação funct desconhecida imprima só a marca de inválida sem campos, para que o erro fique óbvio e o programa continue.
16. Como estudante, quero que linha com caractere fora do alfabeto esperado seja tratada como inválida sem quebrar o programa, para que um erro de digitação não aborte a lista inteira.
17. Como estudante, quero que todas as instruções da base menos sistema sejam reconhecidas, para que minha lista de exercícios funcione por completo.
18. Como estudante, quero ler cada ramo de decisão como um `se/senão` explícito e verboso, para que eu consiga explicar cada linha em voz alta.
19. Como estudante, quero não encontrar nenhuma anotação de tipagem no código, para que a sintaxe não me distraia do algoritmo.
20. Como estudante, quero ter certeza de que nenhum operador binário foi usado, para que toda manipulação de bits seja visível como texto.
21. Como estudante, quero ter certeza de que nenhuma biblioteca foi importada sem aviso, para que eu saiba exatamente do que o programa depende.
22. Como usuário do repositório, quero um arquivo de exemplo com as 20 instruções já conhecidas, para que eu valide o programa com um caso real.
23. Como usuário do repositório, quero regras de simplicidade registradas no guia de agentes, para que futuras mudanças não reintroduzam sintaxe avançada.

## Implementation Decisions

- Seams de teste: uma única seam principal no nível mais alto possível — da linha de entrada já normalizada em 32 caracteres de texto até a estrutura de saída impressa (campos presentes mais linha em assembly). Seam secundária só se necessária — normalização de linha bruta (hex com prefixo ou binário) para 32 caracteres ou marca de inválida. Verificação com o usuário: a principal cobre todo o domínio (formato, mnemônico, registradores ABI, imediato com sinal, assembly por tipo); a secundária isola validação de texto sem contaminar a lógica de decodificação. Nenhuma seam nova além dessas duas.
- Pipeline por instrução: normalizar texto, identificar formato pelo opcode, resolver mnemônico, extrair campos como fatias de texto, converter registradores e imediato, montar impressão genérica. Cada etapa é uma função pequena com nome didático.
- Normalização estrita: começa com prefixo de hex é hexadecimal (converte para binário com `hex_to_bin`); senão é binário (valida com `int(texto, 2)` dentro de `try/except ValueError`). Linha vazia e comentário pulam. Nos dois alfabetos, só completa à esquerda até 32 bits via função de completar existente quando o valor tem 32 ou menos; passou disso ou falhou na conversão é instrução inválida. Todo o resto é instrução inválida.
- Conversão hex para bin com validação dos dígitos por comparação de texto seguida de `int(texto, 16)` e `format(numero, "b")`, completando à esquerda até 32 bits.
- Conversão binário para inteiro com sinal por laço de duplicação e soma de dígitos com inteiros decimais simples, com ajuste de sinal quando o primeiro bit é `1`, sem operadores binários.
- Tabelas opcode para formato e funct3/funct7 para mnemônico como condicionais encadeadas explícitas, mesmo que longas; dicionários permitidos somente para a tabela de nomes ABI quando isso deixar o código mais simples.
- Extração de campos (opcode, registradores, funct3, funct7, pedaços de imediato por tipo I, S, B, U, J) por posição em texto, com remontagem de imediato por concatenação na ordem arquitetural antes da conversão com sinal.
- Impressão genérica que recebe formato, mnemônico, campos presentes e assembly e monta a saída na ordem fixa de campos, omitindo ausentes; inválida imprime só a marca canônica.
- Templates de assembly por tipo travados: R com três registradores; I aritmético com dois registradores mais imediato; loads com base mais deslocamento; stores com dois registradores mais deslocamento; branches com dois registradores mais deslocamento; U com registrador mais imediato alto; J com registrador mais deslocamento; jalr com registrador destino, registrador base e deslocamento.
- Escopo de instruções: toda a base inteira RV32I menos as de sistema; combinações fora da tabela são inválidas sem abortar o processamento.
- Restrições de linguagem: só condicionais, repetições, definição e chamada de função, comparação, aritmética decimal simples e operações básicas de texto e funções embutidas elementares, mais `try/except ValueError` só para validar a entrada sem quebrar o programa; proibidos operadores binários, casamento de padrões, compreensões e qualquer importação além dos arquivos locais do projeto sem pergunta prévia; conversão de base liberada só na normalização de entrada (`int` com base 16 na leitura de hex, `int` com base 2 na validação de binário, `format` com `"b"`); proibida qualquer sintaxe de tipagem.
- Estrutura em quatro responsabilidades: decodificação, utilidades de texto e números, tabelas de formato e mnemônico, e ponto de entrada que faz o laço de leitura do arquivo e impressão, com imports locais ligando os módulos sem duplicar código. Sem caminhos ou trechos de código nesta spec para não envelhecer.
- Massa de teste canônica: as 20 instruções já conhecidas viram arquivo de exemplo em ambos os alfabetos de entrada.

## Testing Decisions

- O que faz um bom teste aqui: só comportamento externo observável (dada uma linha de arquivo, qual texto sai), nunca detalhes internos (nomes de variáveis, ordem de ramos, uso ou não de dicionário).
- O que será testado: a seam principal com uma linha de 32 caracteres por formato e por família (R, I aritmético com e sem deslocamento, loads, jalr, stores, branches, U alto, J), incluindo imediatos positivos, negativos e zero; a seam de normalização com hex curto, binário curto, linha vazia, comentário e linhas com caracteres inválidos (valendo a gramática do `int` com base 2: sublinhado, sinal e prefixo `0b` passam na normalização e caem como inválida na decodificação); o programa de ponta a ponta com o arquivo de exemplo, conferindo que inválidas não abortam e que campos ausentes somem.
- Prior art: não há testes no repositório hoje; este será o primeiro conjunto, então cada caso deve ser legível por iniciante com entrada e saída esperada lado a lado.

## Out of Scope

- Instruções de sistema (`fence`, `ecall`, `ebreak`) e qualquer extensão além da base inteira.
- Aceitar instruções comprimidas, 64 bits ou qualquer largura diferente de 32 bits.
- Interface gráfica, linha de comando com argumentos, saída em arquivo ou formato máquina (JSON, CSV).
- Suporte a hexadecimal sem prefixo, prefixo binário, separadores digitados no meio da linha ou múltiplas instruções por linha.
- Otimizações, novas dependências, importações adicionais ou qualquer sintaxe além do subconjunto simples.
- Nomes de registradores numéricos na saída; a saída usa somente nomes ABI.

## Further Notes

- Vocabulário canônico do glossário: instrução, formato, opcode, funct3, funct7, registrador destino/origem, imediato, mnemônico, assembly, nome ABI, instrução inválida.
- Decisões arquiteturais a registrar: ausência de operadores binários e de importações sem aprovação; escopo sem sistema; entrada em arquivo com os dois alfabetos; saída que omite ausentes.
- Regras de simplicidade e proibição de tipagem devem ser promovidas ao guia de agentes para valer para mudanças futuras.

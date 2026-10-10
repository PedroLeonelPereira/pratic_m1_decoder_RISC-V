Status: ready-for-agent

# Spec — Conflitos de dados e de controle no pipeline (M2, só software)

## Problem Statement

Sou estudante e já tenho o decodificador da Prática M1 funcionando: ele lê um arquivo de memória de instruções e extrai de cada instrução o formato, o mnemônico e os campos, entre eles rs1, rs2 e rd. Agora preciso responder à pergunta central da M2: quais instruções leem um registrador antes que a instrução anterior tenha conseguido escrevê-lo, e qual instrução cai no slot de atraso de cada desvio. O processador-alvo é um pipeline de cinco estágios sem qualquer proteção de hardware, então cabe ao meu programa detectar esses conflitos e produzir versões corrigidas do programa que executem corretamente nele, só com nops e reordenação. Quero ver os conflitos no console, receber dois programas corrigidos que eu consiga ler de volta no decodificador da M1, mais listagens legíveis e um relatório de custo comparando as duas técnicas.

## Solution

Estender o programa da M1 para, a partir do mesmo arquivo de memória de instruções, atribuir um endereço sequencial a cada instrução decodificada, detectar conflitos de dados por dependência verdadeira com o produtor mais recente e conflitos de controle por slot de atraso e blocos básicos, e depois produzir duas correções por software: uma só com inserção mínima de nops sem reordenar, outra com reordenação dentro do bloco básico preenchendo o slot com instrução útil sempre que houver candidata correta, recalculando endereços e deslocamentos e reescrevendo as instruções de desvio e salto em linguagem de máquina. O fluxo continua interativo: escolho o arquivo, vejo os conflitos separados entre dados e controle, recebo dois arquivos novos no mesmo formato de entrada mais duas listagens legíveis, e vejo o sobrecusto de cada técnica no console.

## User Stories

1. Como estudante, quero informar o mesmo arquivo de entrada da M1 e ver cada instrução com seu endereço sequencial, para que eu localize produtor e consumidor pelo endereço.
2. Como estudante, quero que cada nop inserido e cada instrução movida desloque os endereços seguintes, para que os alvos de desvio continuem fazendo sentido.
3. Como estudante, quero ver todos os pares produtor/consumidor que violam a distância mínima com endereço das duas instruções, registrador envolvido e distância entre elas, para que eu confira cada conflito à mão.
4. Como estudante, quero que só dependência verdadeira (leitura após escrita) seja reportada como conflito de dados, para que eu não confunda com escrita após leitura ou escrita após escrita.
5. Como estudante, quero que escrita após leitura e escrita após escrita não gerem conflito mas restrinjam a reordenação, para que a correção nunca troque o resultado do programa.
6. Como estudante, quero que o detector respeite quais campos cada formato realmente usa, para que instrução de tipo S e desvio condicional sejam tratados como quem lê dois registradores e não escreve nenhum.
7. Como estudante, quero que o campo rd de um formato que não o possui nunca gere conflito, para que eu não caia no erro mais comum desta etapa.
8. Como estudante, quero que leituras e escritas no registrador zero nunca gerem conflito, para que escritas descartadas não virem nop à toa.
9. Como estudante, quero que sempre o produtor mais recente de cada registrador seja considerado, para que cadeias de dependência apontem para a instrução certa.
10. Como estudante, quero que consumidor a distância 1 exija 2 nops e a distância 2 exija 1 nop, para que a regra 3 menos d fique visível na saída.
11. Como estudante, quero que consumidor a distância 3 ou mais não gere conflito, para que o programa não insira nop desnecessário.
12. Como estudante, quero ver para cada desvio qual instrução ocupa o seu slot de atraso, para que eu entenda que a instrução seguinte sempre executa.
13. Como estudante, quero ver os blocos básicos do programa onde todo alvo de desvio inicia um bloco e toda instrução de desvio encerra um, para que eu saiba até onde posso reordenar.
14. Como estudante, quero que conflitos de dados que atravessam a fronteira do desvio sejam detectados entre produtor anterior ao desvio e consumidor no início de qualquer um dos dois caminhos possíveis, para que nenhum caminho fique quebrado.
15. Como estudante, quero uma correção só com nops que insira o menor número possível sem alterar a ordem, para que nenhum conflito de dados permaneça.
16. Como estudante, quero que o slot de atraso de cada desvio seja preenchido com nop na técnica só com nops, para que nenhuma instrução seja executada indevidamente.
17. Como estudante, quero uma segunda correção com reordenação que preencha o slot com instrução útil sempre que houver candidata, para que eu precise de menos nops.
18. Como estudante, quero que a reordenação se limite a um mesmo bloco básico, para que a ordem entre blocos nunca mude o fluxo do programa.
19. Como estudante, quero que a única instrução que pode atravessar o desvio seja a que vai para o slot vinda de antes do desvio, para que sua execução seja correta nos dois caminhos.
20. Como estudante, quero que a reordenação preserve todas as dependências entre movidas inclusive escrita após leitura e escrita após escrita, para que reduzir nops nunca altere o resultado.
21. Como estudante, quero que a ordem relativa de acessos à memória que possam se sobrepor seja preservada na reordenação, para que carga e armazenamento na mesma posição não troquem de ordem.
22. Como estudante, quero que acessos com mesmo registrador-base e deslocamentos diferentes sejam tratados como endereços distintos, para que possam ser reordenados entre si.
23. Como estudante, quero que após mover instrução para o slot o início dos dois caminhos do desvio seja reverificado, para que o conflito novo criado na saída do bloco seja corrigido.
24. Como estudante, quero que onde a reordenação não resolver o programa complete com nops, para que o programa final nunca tenha conflito restante.
25. Como estudante, quero que os deslocamentos de desvio e salto sejam recalculados após cada inserção e movimento e as instruções reescritas em linguagem de máquina, para que continuem apontando para o alvo correto.
26. Como estudante, quero receber um primeiro arquivo corrigido só com nops no mesmo formato da entrada, para que eu consiga lê-lo de volta no decodificador da M1.
27. Como estudante, quero receber um segundo arquivo corrigido com reordenação e nops no mesmo formato da entrada, para que eu compare as duas técnicas instrução por instrução.
28. Como estudante, quero uma listagem legível para cada arquivo com endereço, código de máquina, instrução desmontada e marcação do que foi inserido ou movido, para que eu explique cada mudança na defesa.
29. Como estudante, quero ver no console o relatório de custo com contagem original, contagem final, quantas foram acrescentadas e percentual de acréscimo por técnica, para que eu compare as duas soluções de um olhar.
30. Como estudante, quero ver os conflitos separados entre dados e controle e o custo no formato canônico do exemplo, para que eu confira com a lista de exercícios.
31. Como estudante, quero que instrução inválida não participe de conflitos nem quebre a análise, para que um erro de digitação não vire nop fantasma.
32. Como estudante, quero poder corrigir falhas da minha M1 sem perder a nota anterior, para que a M2 funcione sobre uma base correta.
33. Como estudante, quero testar com cadeia de dependências sem instrução independente, laço com desvio para trás, desvio para frente e caso onde reordenação elimina todos os nops, para que eu cubra os casos pedidos na validação.
34. Como estudante, quero ler cada decisão como condicionais e repetições explícitas e verbosas, para que eu consiga explicar o algoritmo em voz alta na defesa.
35. Como estudante, quero ter certeza de que nenhum operador binário, tipagem ou biblioteca nova foi usada, para que o código continue no subconjunto simples do projeto.

## Implementation Decisions

- Seams de teste: uma única seam principal no nível mais alto possível — de lista ordenada de instruções já decodificadas (endereço sequencial mais estrutura de saída da M1 com formato, mnemônico, rd, rs1, rs2, imm) para resultados observáveis (lista de conflitos de dados, lista de conflitos de controle com blocos básicos, dois programas corrigidos e relatório de custo). Reusa as duas seams existentes da M1 (linha bruta para 32 caracteres; 32 caracteres para estrutura impressa) sem criar seam nova abaixo delas; se precisar isolar, a única seam secundária admitida é a recodificação de uma instrução com novo deslocamento para linguagem de máquina. Verificação com o usuário dispensada por instrução expressa na tarefa (sintetizar direto); a seam única cobre todo o domínio e mantém o número de seams no mínimo.
- Modelo de pipeline travado: cinco estágios com nomes canônicos, sem adiantamento, sem detecção em hardware, sem descarte e sem predição; banco escrito na primeira metade e lido na segunda, logo conflito quando distância é 1 ou 2 com nops iguais a 3 menos d; desvios condicionais resolvidos no estágio de decodificação com slot sempre executado; registrador zero constante; nop canônico equivalente à soma com zero em destino zero.
- Endereçamento didático: primeira instrução válida num endereço base canônico de segmento de texto, cada instrução seguinte soma 4; linhas puladas não ocupam endereço; inválidas ocupam endereço para não deslocar o resto mas nunca produzem nem consomem registrador; após cada inserção ou movimento todos os endereços seguintes são refeitos antes de qualquer recálculo de deslocamento.
- Leitura e escrita por formato travadas: quem escreve é só quem tem registrador destino real; quem lê é só quem tem origem real; armazenamento e desvio condicional leem dois e não escrevem; saltos com ligação escrevem destino e salto por registrador lê origem; instruções de constante escrevem destino e não leem; imediato nunca é registrador.
- Detecção de dados: varredura em ordem mantendo o produtor mais recente por registrador; para cada leitura procura para trás até o produtor vivo mais próximo e mede a distância em instruções; zero nunca gera conflito; só leitura após escrita gera conflito; escrita após leitura e escrita após escrita só bloqueiam reordenação.
- Detecção de controle: toda instrução de desvio condicional e todo salto encerram um bloco; todo alvo de desvio ou salto inicia um bloco; a instrução seguinte ao desvio condicional é o ocupante do slot; conflitos de borda verificam o produtor anterior ao desvio contra a primeira leitura de cada um dos dois caminhos.
- Correção só com nops: percorre em ordem inserindo nops mínimos entre produtor e consumidor sem mudar a ordem; depois preenche cada slot com nop; nunca remove instrução original.
- Reordenação: só dentro do bloco básico; candidata ao slot vem de antes do desvio e precisa ser correta nos dois caminhos (não pode depender do resultado do desvio nem quebrar nenhuma dependência verdadeira, de escrita após leitura, de escrita após escrita ou de memória sobreposta em nenhum dos caminhos); após mover, reverifica a saída do bloco e completa com nops onde não houver candidata; correção parcial que reduz nops sem atingir o mínimo vale metade, correção que altera o resultado não pontua.
- Memória conservadora e didática: dois acessos só podem trocar de ordem quando dá para mostrar que são distintos (mesma base com deslocamentos diferentes); mesmo base com mesmo deslocamento ou base desconhecida preserva a ordem relativa.
- Recálculo: deslocamento novo é alvo menos endereço da instrução que desvia ou salta, convertido para o campo embaralhado de cada formato por concatenação de texto na ordem arquitetural; instrução reescrita precisa decodificar de volta para o mesmo mnemônico e mesmo alvo; solução sem recálculo ainda recebe os pontos de correção, mas sem correções não há endereços a recalcular.
- Saídas: dois arquivos novos no mesmo alfabeto de entrada (uma instrução por linha, mesmo estilo de prefixo e comentários simples), cada um acompanhado de listagem legível com endereço, código de máquina, desmontada e marcação de inserido ou movido; relatório de custo com as quatro contagens por técnica e comparação entre elas.
- Restrições de linguagem herdadas da M1: só condicionais, repetições, funções, comparação, aritmética decimal simples e operações de texto por fatiamento e concatenação mais embutidas elementares e validação de entrada com tentativa e erro de valor; dicionários só para tabelas de consulta quando mais simples que condicional; imports só entre módulos locais; proibidos operadores binários, tipagem e biblioteca nova sem pergunta.
- Estrutura por responsabilidades sem caminhos nesta spec: normalização e decodificação reusadas da M1 intocadas; nova responsabilidade de análise de conflitos; nova responsabilidade de correção com nops; nova responsabilidade de reordenação; nova responsabilidade de recálculo e reescrita; responsabilidade de saída em arquivos e listagens; responsabilidade de relatório de custo; ponto de entrada orquestra escolher arquivo, mostrar conflitos separados, gerar um arquivo por técnica e exibir sobrecusto.

## Testing Decisions

- O que faz um bom teste aqui: só comportamento externo observável (dado um arquivo de entrada, quais conflitos aparecem no console, quais arquivos e listagens saem e qual o custo), nunca detalhes internos (nomes de variáveis, ordem de ramos, estrutura de listas).
- O que será testado: a seam principal com cadeias de dependência a distância 1 e 2 exigindo 2 e 1 nops, distância 3 sem conflito, registrador zero sem conflito, armazenamento e desvio sem destino, produtor mais recente prevalecendo, slot ocupado identificado, blocos básicos por alvo e por desvio, conflito de borda nos dois caminhos, correção só com nops mínima sem reordenar, slot preenchido com nop, reordenação preenchendo slot com útil só dentro do bloco e só vinda de antes, preservação de escrita após leitura e escrita após escrita e de memória sobreposta, reverificação da saída do bloco após mover, recálculo conferido pela releitura do arquivo gerado no decodificador da M1, listagens com marcação e relatório com contagens e percentual.
- Prior art: primeiro conjunto de testes do repositório será entrada e saída esperada lado a lado legível por iniciante; este segue o mesmo estilo, com os códigos da lista de exercícios como casos de resposta conhecida para o mínimo de nops e com quatro casos próprios obrigatórios (cadeia sem independente, laço para trás, desvio para frente, reordenação que zera nops).

## Out of Scope

- Qualquer solução de hardware: adiantamento, unidade de detecção, bolha por hardware, predição de desvio, descarte automático.
- Instruções de sistema, exceções e qualquer extensão além da base inteira já coberta pela M1.
- Instruções comprimidas, 64 bits ou largura diferente de 32 bits; hexadecimal sem prefixo, múltiplas instruções por linha ou separadores no meio da linha.
- Reordenação ótima exigida para pontuar: redução correta sem mínimo vale metade; reordenação entre blocos ou que altere o resultado não pontua.
- Interface gráfica, argumentos de linha de comando novos além da escolha interativa de arquivo, saída em formato máquina além dos dois arquivos no formato de entrada.
- Tratamento de exceções, pseudos novas além das já existentes, mudança no formato da saída da M1 ou nas regras de simplicidade.

## Further Notes

- Vocabulário canônico: instrução, formato, opcode, funct3, funct7, registrador destino e origem, imediato, mnemônico, assembly, nome ABI, instrução inválida, mais conflito de dados, conflito de controle, produtor, consumidor, distância, nop, slot de atraso, bloco básico, reordenação, alvo de desvio, deslocamento, listagem, relatório de custo.
- Fluxo canônico: escolher arquivo, mostrar conflitos separados entre dados e controle, gerar um arquivo novo por técnica, exibir sobrecusto de cada técnica.
- Exemplo canônico de console com duas linhas de dados, uma de controle e três de custo serve de trava visual para os testes de console.
- Decisão de endereço base e passo fixo precisa ser registrada como decisão arquitetural junto com ausência de hardware e escopo só de software.

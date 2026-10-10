Prof. Thiago Felski Pereira, M.Sc. **Avaliação Prática M2 – Conflitos de Dados e de Controle no Pipeline (Etapa 2 de 2)** 

# **UNIVALI – Arquitetura e Organização de Computadores II** 

# **Instruções** 

1. Esta atividade deve ser realizada em duplas ou trios, preferencialmente nos mesmos grupos da Prática M1. 

2. A data da defesa e a data final da postagem do código-fonte comentado estarão indicadas no AVA 2.0. Defesas ou entregas feitas na aula seguinte valerão 70% da nota. 

3. A implementação poderá ser realizada em qualquer linguagem de programação. O código deve ser entregue (também vale o link para o repositório no GitHub) e apresentado. 

4. Todos os integrantes devem estar presentes na apresentação, e os códigos devem conter a identificação dos autores. Quem faltar apresentará sozinho na semana seguinte, sujeito à instrução 2. 

5. Se forem identificados trabalhos com grau de similaridade que caracterize cópia ou adaptação (autorizadas ou não pelos seus autores originais), a nota dos grupos será a nota de um trabalho dividida pelo número de grupos que entregou esses trabalhos similares. 

# **Contexto** 

Esta é a segunda e última etapa do trabalho iniciado na Prática M1. Lá, o programa passou a ler um arquivo de memória de instruções em linguagem de máquina e a extrair, de cada instrução, o formato, o mnemônico e os campos — entre eles rs1, rs2 e rd. São exatamente esses campos que permitem agora responder à pergunta central desta etapa: quais instruções leem um registrador antes que a instrução anterior tenha conseguido escrevê-lo. 

O decodificador da M1 é a entrada desta etapa. Grupos que identificarem falhas na própria implementação anterior podem e devem corrigi-las; isso não altera a nota já atribuída à M1, mas é pré-requisito para que a M2 funcione. 

**Esta etapa trata apenas de soluções de software.** Nenhuma solução de hardware é exigida: não é preciso implementar adiantamento (forwarding), unidade de detecção de conflitos, inserção de bolhas por hardware nem predição de desvio. O processador-alvo é um pipeline sem qualquer proteção, e cabe ao programa transformar o código de entrada em um código que execute corretamente nesse processador. 

# **Premissas do modelo de pipeline** 

Todas as decisões do programa devem seguir as premissas abaixo, as mesmas adotadas na lista de exercícios sobre conflitos: 

1. O pipeline tem cinco estágios: IF, ID, EX, MEM e WB. 

2. Não há adiantamento (forwarding), detecção de conflitos, descarte (flush) nem predição de desvio. 

3. O banco de registradores é escrito na primeira metade do ciclo e lido na segunda metade. Portanto, um consumidor situado a uma distância d do seu produtor sofre conflito quando d = 1 ou d = 2, e o número de nops necessários é 3 − d. 

4. Os desvios condicionais são resolvidos no estágio ID. A instrução imediatamente seguinte ao desvio — o slot de atraso — é sempre executada, seja o desvio tomado ou não. 

5. O registrador zero é constante: escritas nele são descartadas e leituras dele nunca geram conflito. 

6. Acessos à memória com o mesmo registrador-base e deslocamentos diferentes referem-se a endereços distintos. 

7. A instrução nop equivale a addi zero, zero, 0, codificada como 0x00000013. 

# **Atividade** 

Estender o programa da Prática M1 para que, a partir do mesmo arquivo de memória de instruções, ele detecte os conflitos do pipeline e produza versões corrigidas do programa. 

## **R1 — Detecção de conflitos de dados** [1,5 ponto] 

- Identificar todos os pares produtor/consumidor que violam a distância mínima, informando o endereço das duas instruções, o registrador envolvido e a distância entre elas. 

- Considerar apenas a dependência verdadeira (leitura após escrita). Escrita após leitura e escrita após escrita não geram conflito em um pipeline em ordem, embora restrinjam a reordenação exigida em R5. 

- Respeitar quais campos cada formato realmente usa: uma instrução de tipo S lê dois registradores e não escreve nenhum; um desvio condicional também lê dois e não escreve. Tratar o campo rd de um formato que não o possui é o erro mais comum nesta etapa. 

- Considerar sempre o produtor mais recente de cada registrador. 

## **R2 — Detecção de conflitos de controle** [1,0 ponto] 

- Identificar as instruções de desvio e, para cada uma, qual instrução ocupa o seu slot de atraso. 

- Determinar os blocos básicos do programa: todo alvo de desvio inicia um bloco, e toda instrução de desvio encerra um. 

- Detectar também os conflitos de dados que atravessam a fronteira do desvio, isto é, entre um produtor anterior ao desvio e um consumidor situado no início de qualquer um dos dois caminhos possíveis. 

## **R3 — Correção de conflitos de dados com NOPs** [1,5 ponto] 

Inserir o menor número possível de nops, sem alterar a ordem das instruções, de modo que nenhum conflito de dados permaneça. 

## **R4 — Correção de conflitos de controle com NOPs** [1,0 ponto] 

Preencher com nop o slot de atraso de cada desvio, garantindo que nenhuma instrução seja executada indevidamente. 

## **R5 — Reordenação de instruções** [2,0 pontos] 

- Reordenar instruções para reduzir a quantidade de nops, preenchendo o slot de atraso com uma instrução útil sempre que houver uma candidata. 

- A reordenação deve se limitar a um mesmo bloco básico. A única instrução que pode atravessar o desvio é a que vai para o slot, e ela deve vir de antes do desvio, de modo que sua execução seja correta nos dois caminhos. 

- Preservar todas as dependências entre as instruções movidas, inclusive escrita após leitura, escrita após escrita e a ordem relativa dos acessos à memória que possam se sobrepor. 

- Após mover uma instrução para o slot, reverificar o início dos dois caminhos do desvio: **preencher o slot frequentemente cria um conflito novo na saída do bloco.** 

- Completar com nops apenas onde a reordenação não resolver. 

**Não se exige que a reordenação seja ótima.** Uma reordenação correta que reduza o número de nops, mas não alcance o mínimo possível, vale metade da pontuação do requisito (1,0 ponto). A pontuação integral exige atingir o mínimo nos códigos de referência apresentados na defesa. Já uma reordenação que altere o resultado do programa não pontua: reduzir nops às custas da correção é pior do que não reordenar. 

## **R6 — Recálculo de endereços e deslocamentos** [1,5 ponto] 

Cada nop inserido e cada instrução movida desloca todas as instruções seguintes. Os deslocamentos das instruções de desvio e de salto precisam ser recalculados, e as instruções reescritas em linguagem de máquina, para que continuem apontando para o alvo correto. 

**Este requisito é avaliado separadamente.** Uma solução que detecta os conflitos e insere os nops corretamente, mas não recalcula os endereços, é uma solução incompleta — e ainda assim recebe integralmente a pontuação de R3, R4 e R5. O contrário, porém, não se aplica: sem as correções, não há endereços a recalcular. 

## **R7 — Arquivos de saída** [1,0 ponto] 

Gerar dois arquivos, no mesmo formato do arquivo de entrada, de modo que possam ser lidos novamente pelo decodificador da Prática M1: 

- **Arquivo 1:** programa corrigido usando apenas nops (R3 e R4). 

- **Arquivo 2:** programa corrigido com reordenação e nops (R5). 

Gerar também, para cada um, uma listagem legível contendo o endereço, o código de máquina, a instrução desmontada e uma marcação indicando o que foi inserido ou movido. 

## **R8 — Relatório de custo** [0,5 ponto] 

Exibir no console, para cada técnica, a contagem de instruções do programa original, a contagem final, quantas instruções foram acrescentadas e o percentual de acréscimo. Comparar as duas soluções. 

# **Fluxo de operação** 

1. Escolher o arquivo com o programa em binário ou hexadecimal. 

2. Mostrar no console os conflitos detectados, separados entre conflitos de dados e de controle. 

3. Gerar um arquivo novo para cada técnica aplicada. 

4. Exibir no console o sobrecusto de cada técnica. 

# **Exemplo de saída no console** 

```
CONFLITOS DE DADOS
  0x00400008  add  t1, t0, s3   <- 0x00400004  lw   t0, 0(a0)    [t0, d=1, 2 nops]
  0x0040000C  sw   t1, 0(a0)    <- 0x00400008  add  t1, t0, s3   [t1, d=1, 2 nops]
CONFLITOS DE CONTROLE
  0x00400018  bne  t0, t1, 0x00400004   slot ocupado por: 0x0040001C  slli s0, s0, 1
CUSTO
  original .............. 12 instrucoes
  somente nops .......... 21 instrucoes  (+9, +75,0%)
  nops + reordenacao .... 14 instrucoes  (+2, +16,7%)
```

# **Validação** 

- Utilize os códigos assembly produzidos na disciplina de Arquitetura de Computadores I, gerando os arquivos com o comando de dump do RARS ou com o botão de exportação do simulador usado na Prática M1. 

- Os códigos da lista de exercícios sobre conflitos no pipeline servem como casos de teste com resposta conhecida: para eles, o número mínimo de nops já foi determinado em aula. 

- O arquivo de saída deve poder ser lido de volta pelo decodificador da Prática M1. Se ele não for decodificável, a reescrita das instruções de desvio está incorreta. 

- Monte casos de teste próprios cobrindo pelo menos: uma cadeia de dependências sem nenhuma instrução independente, um laço com desvio para trás, um desvio para a frente e um caso em que a reordenação elimina todos os nops. 

# **Distribuição da nota** 

As notas só serão validadas mediante demonstração da execução correta e domínio do algoritmo implementado. 

|**Requisito**|**Pontos**|**Observações**|
|---|---|---|
|R1 — Detecção de conflitos de dados|1,5|independente|
|R2 — Detecção de conflitos de controle|1,0|independente|
|R3 — Correção de conflitos de dados com NOPs|1,5|independente de R6|
|R4 — Correção de conflitos de controle com NOPs|1,0|independente de R6|
|R5 — Reordenação de instruções|2,0|exige R3 e R4; 1,0 se não ótima|
|R6 — Recálculo de endereços e deslocamentos|1,5|critério separado|
|R7 — Geração dos dois arquivos de saída|1,0|exige R3 e R4|
|R8 — Relatório de custo|0,5|independente|



A defesa é individual e poderá ajustar a nota de cada integrante em relação à nota do grupo. 

**Fora do escopo** 

Não são exigidos, e não valem pontuação adicional: adiantamento (forwarding), unidade de detecção de conflitos em hardware, inserção de bolhas por hardware, predição de desvio, tratamento de exceções e extensões além do RV32I. 


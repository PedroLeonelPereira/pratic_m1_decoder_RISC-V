# Decodificador RV32I — didático e simples

Decodificador de instruções da base inteira **RV32I** (menos `fence`, `ecall`, `ebreak`),
feito para quem tem conhecimento básico em lógica de programação.

Você entrega um arquivo texto com **uma instrução por linha** (hexadecimal ou binário)
e o programa imprime, para cada linha, o **formato, mnemônico, registradores em nome
ABI, imediato decimal com sinal, funct3/funct7 e a linha em assembly**.
No final, imprime um **resumo de CPI médio** por formato.

Público e estilo: código **verboso e explícito** é melhor que código curto e esperto.
Toda manipulação de bits é feita como **texto** (fatiamento `[x:y]`, concatenação
com `+`), sem operadores binários, sem tipagem, sem biblioteca externa.

## 1. Como rodar

Da raiz do projeto:

```bash
python src/riscv_decoder/main.py
```

O programa pergunta interativamente:

```text
caminho do arquivo: exemplo_hex.txt
caminho do csv de pesos: exemplo_pesos.csv
```

Exemplo mínimo de sessão (arquivo com 1 instrução):

```text
caminho do arquivo: exemplo_hex.txt
caminho do csv de pesos: exemplo_pesos.csv
formato: R
mnemonico: add
rd: a1
rs1: a1
rs2: a2
f3: 000
f7: 0000000
assembly: add a1,a1,a2
...
Instrucoes totais = 20
Instrucoes por formato, R = 10.0% I = 50.0% S = 10.0% B = 15.0% U = 10.0% J = 5.0%
CPI medio = 3.95
```

Não há argumentos de linha de comando, saída em arquivo, JSON ou interface gráfica.
Não há testes automatizados no repositório (ver seção 12).

## 2. Organização das pastas

```text
.
├── src/riscv_decoder/        # código-fonte (único lugar com lógica)
│   ├── main.py               # ponto de entrada, só chama programa_principal
│   ├── decoder.py            # laço principal + despacho por tipo
│   ├── config.py             # tabela de nomes ABI
│   ├── cpi.py                # pesos por formato + resumo de CPI
│   ├── pseudo.py             # identifica nop, mv, j, ret
│   ├── entrada/
│   │   ├── linhas.py        # normaliza linha -> 32 chars binários
│   │   └── conversoes.py    # binário texto -> inteiro com/sem sinal
│   └── instrucoes/
│       ├── identificacao.py # opcode -> tipo, funct3/funct7 -> mnemônico
│       ├── comum.py         # registrador_para_abi + mostrar_resultado
│       ├── aritmetica.py    # tipos R e I
│       ├── memoria.py       # load, jalr, tipo S
│       ├── desvios.py       # tipo B e tipo J
│       └── constantes.py    # lui e auipc
├── exemplo_hex.txt           # 20 instruções conhecidas em hex
├── exemplo_bin.txt           # mesmas 20 em binário
├── exemplo_pesos.csv         # pesos de CPI por formato, sem cabeçalho
├── pseudo-instrucoes/spec.md # spec das 4 pseudos
├── .scratch/riscv-decoder/   # spec + issues do decodificador base
├── docs/agents/              # convenções de skills de agente
├── AGENTS.md                 # regras de simplicidade do projeto
└── pyproject.toml            # nome, versão, script riscv-decoder
```

Responsabilidade de cada camada:

| Camada | Arquivos | Faz | Não faz |
|---|---|---|---|
| Entrada | `main.py`, `decoder.py:programa_principal`, `entrada/linhas.py` | lê arquivo, pula vazio/`#`, normaliza para 32 chars | não decodifica |
| Identificação | `instrucoes/identificacao.py`, `decoder.py:decodificar_e_mostrar` | opcode -> tipo, funct -> mnemônico | não converte número |
| Extração | `aritmetica.py`, `memoria.py`, `desvios.py`, `constantes.py` | fatia texto, remonta imediato, converte ABI/decimal | não imprime direto sem passar pela saída genérica |
| Saída | `instrucoes/comum.py:mostrar_resultado` | imprime só campos existentes em ordem fixa + `assembly` | nunca inventa campo ausente |
| Extra | `pseudo.py`, `cpi.py` | linha `pseudo:` e resumo de CPI | nunca troca o assembly real pelo pseudo |

Import entre arquivos locais é liberado para não duplicar código. Exemplo
(`src/riscv_decoder/decoder.py:1-17`):

```python
from entrada.linhas import normalizar_linha
from instrucoes.identificacao import identificar_tipo
from instrucoes.comum import mostrar_resultado
from instrucoes.aritmetica import decodificar_tipo_r
from instrucoes.aritmetica import decodificar_tipo_i
from cpi import ler_pesos_csv
```

E o ponto de entrada (`src/riscv_decoder/main.py:1-11`) é propositalmente fino:

```python
from decoder import programa_principal


def main():
    programa_principal()


if __name__ == "__main__":
    main()
```

## 3. Entrada: uma instrução por linha

Regras (`src/riscv_decoder/entrada/linhas.py:normalizar_linha`):

1. `strip()` na linha.
2. Linha vazia -> `"pular"` (ignorada silenciosamente).
3. Começa com `#` -> `"pular"` (comentário).
4. Começa com `0x` ou `0X` -> hexadecimal: converte o resto com `hex_to_bin`.
5. Senão -> binário: valida com `int(binario, 2)` dentro de `try/except ValueError`.
6. Se passou de 32 bits -> `"invalida"`.
7. Senão completa à esquerda com zeros até 32 bits.

Exemplos reais (testados com `normalizar_linha`):

| Linha bruta | Resultado |
|---|---|
| `0x00c585b3` | `00000000110001011000010110110011` |
| `00000000110001011000010110110011` | igual (já tem 32) |
| `0x1` | `00000000000000000000000000000001` (completa à esquerda) |
| `""` (vazia) | `pular` |
| `# exemplo` | `pular` |
| `XYZ` | `invalida` (não quebra o programa) |

### 3.1 `completar_32` e `hex_to_bin`

`src/riscv_decoder/entrada/linhas.py:3-5`:

```python
def completar_32(bits):
    falta = 32 - len(bits)
    return "0" * falta + bits
```

Exemplo: `completar_32("1")` devolve 31 zeros + `"1"`.

`src/riscv_decoder/entrada/linhas.py:8-23` valida dígito por dígito com
comparação de texto (`"0"`, `"9"`, `"A"`, `"F"`, `"a"`, `"f"`) e só depois usa
as duas conversões de base liberadas no projeto:

```python
numero = int(texto, 16)
return format(numero, "b")
```

Exemplo: `hex_to_bin("c585b3")` -> `int("c585b3", 16)` -> `format(..., "b")`,
depois o chamador completa até 32 bits.

## 4. Pipeline: normalizar -> identificar -> decodificar -> mostrar

`src/riscv_decoder/decoder.py:20-66` (`decodificar_e_mostrar`):

```python
def decodificar_e_mostrar(bits):
    if len(bits) != 32:
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    # monta "validos" só com 0/1 e compara com a entrada
    # ...
    opcode = bits[25:32]
    tipo = identificar_tipo(opcode)
    if tipo == "invalida":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    if tipo == "R":
        decodificar_tipo_r(bits)
        return
    # ... I, load, jalr, S, B, lui, auipc, J
```

Repare: o opcode são sempre os **últimos 7 caracteres** (`bits[25:32]`),
porque a string está em ordem arquitetural (bit 31 primeiro).

`src/riscv_decoder/decoder.py:69-108` (`programa_principal`) faz o laço:

```python
caminho = input("caminho do arquivo: ")
caminho_pesos = input("caminho do csv de pesos: ")
peso_r, peso_i, peso_s, peso_b, peso_u, peso_j = ler_pesos_csv(caminho_pesos)
arquivo = open(caminho)
for linha in arquivo:
    normalizada = normalizar_linha(linha)
    if normalizada != "pular":
        if normalizada == "invalida":
            mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        else:
            decodificar_e_mostrar(normalizada)
            # ... conta por formato para o CPI
arquivo.close()
mostrar_resumo_cpi(...)
```

Inválida **nunca aborta**: imprime só `instrucao invalida` e segue para a
próxima linha.

## 5. Identificação: opcode -> tipo, funct -> mnemônico

### 5.1 Opcode -> tipo (`src/riscv_decoder/instrucoes/identificacao.py:3-22`)

| `bits[25:32]` | Tipo interno | Formato clássico |
|---|---|---|
| `0110011` | `R` | R |
| `0010011` | `I` | I |
| `0000011` | `load` | I |
| `1100111` | `jalr` | I |
| `0100011` | `S` | S |
| `1100011` | `B` | B |
| `0110111` | `lui` | U |
| `0010111` | `auipc` | U |
| `1101111` | `J` | J |
| outro | `invalida` | — |

Exemplo:

```python
def identificar_tipo(opcode):
    if opcode == "0110011":
        return "R"
    if opcode == "0010011":
        return "I"
    # ...
    return "invalida"
```

Por que `load`, `jalr`, `lui`, `auipc` são tipos separados se o formato é
I ou U? Porque o **template de assembly** e os campos impressos são diferentes
(ver seção 7). O `cpi.py` reagrupa depois (seção 9).

### 5.2 funct3/funct7 -> mnemônico

Tudo com `if/elif` encadeado e explícito, mesmo que longo. Exemplos:

Tipo R (`src/riscv_decoder/instrucoes/identificacao.py:25-33`):

```python
def resolver_mnemonico_r(f3, f7):
    if f3 == "000":
        if f7 == "0000000":
            return "add"
        else:
            if f7 == "0100000":
                return "sub"
```

Tipo I com shifts (`src/riscv_decoder/instrucoes/identificacao.py:75-101`):
`addi/slti/sltiu/xori/ori/andi` resolvem só por `f3`; `slli/srli/srai`
exigem também `f7` (`0000000` ou `0100000`).

Loads (`lb/lh/lw/lbu/lhu`), stores (`sb/sh/sw`) e branches
(`beq/bne/blt/bge/bltu/bgeu`) resolvem só por `f3`. `jalr` exige `f3 == "000"`,
senão é inválida. `lui`, `auipc` e `jal` não têm funct: o opcode basta.

Tabela completa suportada (toda a base RV32I menos sistema):

- R: `add sub sll slt sltu xor srl sra or and`
- I: `addi slti sltiu xori ori andi slli srli srai`
- Load: `lb lh lw lbu lhu`
- `jalr`, S: `sb sh sw`, B: `beq bne blt bge bltu bgeu`, `lui auipc jal`

## 6. Conversões de número e registradores

### 6.1 Binário texto -> inteiro (`src/riscv_decoder/entrada/conversoes.py`)

Sem operadores binários: laço de `valor = valor * 2`, soma `1` quando o
caractere é `"1"`. Com sinal, se o primeiro bit é `"1"`, subtrai `2^len`
calculado com `while`:

```python
def binario_para_inteiro_sem_sinal(bits):
    valor = 0
    for caractere in bits:
        valor = valor * 2
        if caractere == "1":
            valor = valor + 1
    return valor


def binario_para_inteiro_com_sinal(bits):
    valor = 0
    for caractere in bits:
        valor = valor * 2
        if caractere == "1":
            valor = valor + 1
    if bits[0:1] == "1":
        potencia = 1
        contador = 0
        tamanho = len(bits)
        while contador < tamanho:
            potencia = potencia * 2
            contador = contador + 1
        valor = valor - potencia
    return valor
```

Exemplo: `binario_para_inteiro_com_sinal("111111111111")` -> `-1`
(imediato de `addi t0,sp,-1`). `binario_para_inteiro_sem_sinal("00011")`
-> `3` (quantidade de `slli t0,t1,3` — shifts usam sem sinal).

### 6.2 Registradores -> nome ABI (`src/riscv_decoder/config.py`, `comum.py`)

Único `dict` permitido no projeto, quando é mais simples que `if/elif`:

```python
tabela_abi = {
    "00000": "zero",
    "00001": "ra",
    "00010": "sp",
    # ... até
    "11111": "t6",
}
```

Uso (`src/riscv_decoder/instrucoes/comum.py:5-6`):

```python
def registrador_para_abi(pedaco):
    return tabela_abi[pedaco]
```

Exemplo: `registrador_para_abi("01010")` -> `"a0"`.
A saída **sempre** usa ABI (`zero ra sp gp tp t0-t2 s0-s1 a0-a7 s2-s11 t3-t6`),
nunca número `x10`.

## 7. Saída: só campos existentes + `assembly`

`src/riscv_decoder/instrucoes/comum.py:9-27`:

```python
def mostrar_resultado(tipo, nome, rd, rs1, rs2, imm, f3, f7, montada):
    if tipo == "invalida":
        print("instrucao invalida")
        return
    print("formato: " + tipo)
    print("mnemonico: " + nome)
    if rd != "":
        print("rd: " + rd)
    if rs1 != "":
        print("rs1: " + rs1)
    # ... rs2, imm, f3, f7
    print("assembly: " + montada)
```

Ordem fixa: `formato, mnemonico, rd, rs1, rs2, imm, f3, f7` + linha `assembly`.
Campo vazio (`""`) **nem aparece**. Inválida imprime só `instrucao invalida`.

Exemplos reais por tipo (de `exemplo_hex.txt`):

**R** — `0x00c585b3`:

```text
formato: R
mnemonico: add
rd: a1
rs1: a1
rs2: a2
f3: 000
f7: 0000000
assembly: add a1,a1,a2
```

Código (`src/riscv_decoder/instrucoes/aritmetica.py:11-25`): fatia
`f7 = bits[0:7]`, `rs2 = bits[7:12]`, `rs1 = bits[12:17]`, `f3 = bits[17:20]`,
`rd = bits[20:25]`, monta `nome + " " + rd + "," + rs1 + "," + rs2`.

**I aritmético** — `0x00c10513` (`addi a0,sp,12`):

```text
formato: I
mnemonico: addi
rd: a0
rs1: sp
imm: 12
f3: 000
assembly: addi a0,sp,12
```

Repare: sem `f7` na saída (só shifts imprimem `f7`). Imediato `bits[0:12]`
convertido com sinal.

**I shift** — `0x00331293` (`slli t0,t1,3`):

```text
formato: I
mnemonico: slli
rd: t0
rs1: t1
imm: 3
f3: 001
f7: 0000000
assembly: slli t0,t1,3
```

Aqui o imediato é só `bits[7:12]` convertido **sem** sinal.

**Load** — `0x00c12503` (`lw a0,12(sp)`):

```text
formato: load
mnemonico: lw
rd: a0
rs1: sp
imm: 12
f3: 010
assembly: lw a0,12(sp)
```

Template travado: `nome + " " + rd + "," + imm + "(" + rs1 + ")"`.

**jalr** — `0x000100e7` (`jalr ra,0(sp)`): mesmo template do load, mas
`formato: jalr` e `f3` precisa ser `000`.

**S** — `0x00640423` (`sb t1,8(s0)`):

```text
formato: S
mnemonico: sb
rs1: s0
rs2: t1
imm: 8
f3: 000
assembly: sb t1,8(s0)
```

Sem `rd`. Imediato dividido remontado por concatenação
(`src/riscv_decoder/instrucoes/memoria.py:56`):

```python
pedaco_imm = pedaco_alto + pedaco_baixo
```

onde `pedaco_alto = bits[0:7]` e `pedaco_baixo = bits[20:25]`.

**B** — `0x00628663` (`beq t0,t1,12`):

```text
formato: B
mnemonico: beq
rs1: t0
rs2: t1
imm: 12
f3: 000
assembly: beq t0,t1,12
```

Imediato embaralhado remontado na ordem arquitetural
(`src/riscv_decoder/instrucoes/desvios.py:21`):

```python
pedaco_imm = pedaco_12 + pedaco_11 + pedaco_10_5 + pedaco_4_1 + "0"
```

**lui** — `0x12345537` (`lui a0,305418240`):

```text
formato: lui
mnemonico: lui
rd: a0
imm: 305418240
assembly: lui a0,305418240
```

Sem `f3`/`f7`. Imediato: `bits[0:20] + "000000000000"` com sinal.

**auipc** — `0x00001117`: igual ao `lui`, mas `formato: auipc`.

**J** — `0x010000ef` (`jal ra,16`):

```text
formato: J
mnemonico: jal
rd: ra
imm: 16
assembly: jal ra,16
```

Imediato (`src/riscv_decoder/instrucoes/desvios.py:37`):

```python
pedaco_imm = pedaco_20 + pedaco_19_12 + pedaco_11 + pedaco_10_1 + "0"
```

**Inválida** — opcode desconhecido, funct inválido ou caractere errado:

```text
instrucao invalida
```

Só isso, sem campos, e o laço continua.

## 8. Pseudo-instruções: `nop mv j ret`

Depois de mostrar a instrução real, as rotinas de I, `jalr` e J chamam
`identificar_pseudo` e imprimem `pseudo: ...` só quando o retorno não é vazio.
R, load, S, B, lui e auipc **nunca** geram pseudo.

Regras travadas (`src/riscv_decoder/pseudo.py:6-23`):

```python
def identificar_pseudo(nome, rd, rs1, imm):
    if nome == "addi":
        if rd == "zero":
            if rs1 == "zero":
                if imm == "0":
                    return "nop"
        else:
            if rs1 != "zero":
                if imm == "0":
                    return "mv " + rd + "," + rs1
    if nome == "jal":
        if rd == "zero":
            return "j " + imm
    if nome == "jalr":
        if rd == "zero":
            if rs1 == "ra":
                if imm == "0":
                    return "ret"
    return ""
```

| Real | Pseudo | Exemplo verificado |
|---|---|---|
| `addi zero,zero,0` | `nop` (prioridade sobre `mv`) | `0x00000013` -> `pseudo: nop` |
| `addi rd,rs1,0` com `rd != zero` e `rs1 != zero` | `mv rd,rs1` | `0x00058513` (`addi a0,a1,0`) -> `pseudo: mv a0,a1` |
| `jal zero,imm` (inclui `0`) | `j imm` | `0x0080006f` (`jal zero,8`) -> `pseudo: j 8`; `0x0000006f` -> `pseudo: j 0` |
| `jalr zero,0(ra)` | `ret` | `0x00008067` -> `pseudo: ret` |

Negativos que **não** geram pseudo (testados na spec):

- `addi a0,zero,5` (imediato não-zero)
- `addi zero,a1,0` (destino zero fora do `nop` descarta resultado)
- `jalr zero,0(t1)` (origem diferente de `ra`)
- `jal ra,8` (destino diferente de `zero`, tem ligação)

Saída real completa do `nop`, para ver a ordem (real antes, pseudo depois):

```text
formato: I
mnemonico: addi
rd: zero
rs1: zero
imm: 0
f3: 000
assembly: addi zero,zero,0
pseudo: nop
```

Integração sem tocar a impressão genérica (exemplo em
`src/riscv_decoder/instrucoes/aritmetica.py:70-74`):

```python
mostrar_resultado("I", nome, rd, rs1, "", imm, f3, "", montada)
texto_pseudo = identificar_pseudo(nome, rd, rs1, imm)
if texto_pseudo != "":
    print("pseudo: " + texto_pseudo)
```

## 9. CPI médio por formato

Arquivo de pesos (`exemplo_pesos.csv`): sem cabeçalho, uma linha por formato:

```csv
# exemplo de pesos de cpi por formato, sem cabecalho
# uma linha por formato: FORMATO,peso
R,2
I,5
S,3
B,4
U,2
J,3
```

Linha vazia e `#` pulam; linha ruim mantém peso zero e segue.

Agrupamento (`src/riscv_decoder/cpi.py:10-29`): os 9 tipos internos viram
os 6 clássicos — `load` e `jalr` contam como `I`, `lui` e `auipc` como `U`:

```python
def agrupar_formato(tipo):
    if tipo == "R":
        return "R"
    if tipo == "I":
        return "I"
    if tipo == "load":
        return "I"
    if tipo == "jalr":
        return "I"
    # ... S, B, lui/auipc -> U, J
    return ""
```

Leitura (`ler_pesos_csv`) e guarda (`guardar_peso`) usam só `open`, `strip`,
`split(",")`, `int()` e condicionais — sem `csv`, sem `dict`.

Resumo (`src/riscv_decoder/cpi.py:83-105`): imprime totais, porcentagem por
formato e média ponderada. Exceção pontual à regra de simplicidade: divisão
(`/`) e decimal só neste arquivo. Inválida não entra na conta.

Saída real de `exemplo_hex.txt` com `exemplo_pesos.csv`:

```text
Instrucoes totais = 20
Instrucoes por formato, R = 10.0% I = 50.0% S = 10.0% B = 15.0% U = 10.0% J = 5.0%
CPI medio = 3.95
```

## 10. Arquivos de exemplo (20 instruções)

`exemplo_hex.txt` e `exemplo_bin.txt` têm as **mesmas 20 instruções**, só muda
o alfabeto. Linhas vazias e `#` são ignoradas.

| Hex | Assembly |
|---|---|
| `0x00c585b3` | `add a1,a1,a2` |
| `0x40c58533` | `sub a0,a1,a2` |
| `0x00c10513` | `addi a0,sp,12` |
| `0xfff10293` | `addi t0,sp,-1` |
| `0x00331293` | `slli t0,t1,3` |
| `0x40335293` | `srai t0,t1,3` |
| `0x0075e513` | `ori a0,a1,7` |
| `0x00c12503` | `lw a0,12(sp)` |
| `0xffc41283` | `lh t0,-4(s0)` |
| `0x00065583` | `lhu a1,0(a2)` |
| `0x000100e7` | `jalr ra,0(sp)` |
| `0xff808467` | `jalr s0,-8(ra)` |
| `0x00640423` | `sb t1,8(s0)` |
| `0xfec12e23` | `sw a2,-4(sp)` |
| `0x00628663` | `beq t0,t1,12` |
| `0xfe941ae3` | `bne s0,s1,-12` |
| `0x00b54463` | `blt a0,a1,8` |
| `0x12345537` | `lui a0,305418240` |
| `0x00001117` | `auipc sp,4096` |
| `0x010000ef` | `jal ra,16` |

## 11. Regras de simplicidade (resumo do `AGENTS.md`)

Proibido (quebra de padrão):

- Operadores binários: `& | ^ ~ << >>`.
- Sintaxe de tipagem: `x: int`, `-> str`, `typing.*`.
- Import externo ou da biblioteca padrão sem perguntar antes.
  Liberados sem importar: `open print input len int str`.

Permitido (subconjunto simples):

- `if/elif/else for while def return try/except ValueError` (só para validar
  entrada sem quebrar).
- Comparação `== != < >`, aritmética decimal `+ - *`.
- Texto: indexação, concatenação com `+`, `split join strip`, fatiamento `[x:y]`.
- Embutidas: `len() int()` (decimal; base 16 só na leitura de hex, base 2 só na
  validação de binário) `str() open() print() input() format()` (só `"b"`).
- `dict` somente para a tabela ABI.
- Import entre arquivos locais (`main decoder entrada instrucoes cpi config pseudo`).

Domínio: só RV32I base menos `fence/ecall/ebreak`; registradores em ABI;
imediato em decimal com sinal.

## 12. Limitações e fora de escopo

- Sem `fence`, `ecall`, `ebreak`, sem extensões, sem comprimidas, sem 64 bits.
- Uma instrução por linha; hex exige prefixo `0x`/`0X`; sem `0b`, sem
  separadores no meio da linha, sem múltiplas instruções por linha.
- Pseudos só `nop mv j ret` (sem `li jr beqz neg not` e família).
- Pseudo nunca substitui o real; `j 0` conta como pseudo válida.
- Sem testes automatizados, sem CLI com argumentos, sem saída em arquivo/JSON/CSV.
- `README.md` estava vazio antes desta escrita; `pyproject.toml` declara
  `riscv-decoder = "riscv_decoder.decoder:main"`.

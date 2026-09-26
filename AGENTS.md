# AGENTS.md

## Project Overview

This project implements **Etapa 1 — Decodificador de Instruções RISC-V** for the Organização de Computadores course at UNIVALI.

The program receives a ROM-like file containing RISC-V machine-code instructions and decodes each instruction into:

- PC/address
- original machine word
- instruction format
- mnemonic
- valid instruction fields
- immediate value when applicable
- ABI register names
- disassembled assembly representation
- absolute branch/jump target when applicable

The project must also generate format statistics and calculate the program's weighted average CPI.

The implementation must be designed so it can be extended in **Etapa 2** to detect data and control hazards in a five-stage RISC-V pipeline. No hazard analysis is required in this stage.

---

# 1. Source of Truth

The official assignment PDF is the primary source of truth for project requirements.

Important requirements from the assignment:

- The implementation may be written in any programming language.
- The program must read one instruction per line.
- Input may be hexadecimal or binary.
- The input format must be detected automatically.
- Blank lines and comments must be ignored.
- `0x` prefixes must be accepted and ignored.
- Each instruction receives a configurable PC/address.
- Instructions must be classified as R, I, S, B, U, or J.
- The mnemonic must be identified, not only the format.
- Invalid instructions must be reported without stopping processing.
- Only fields that actually exist in the instruction format may be reported.
- B and J immediates must be reconstructed from their non-contiguous bit fields.
- Signed immediates must use proper sign extension.
- Assembly output must use RISC-V ABI register names.
- Branch/jump output must contain the absolute target address.
- Common pseudo-instructions must be recognized.
- Format counts and percentages must be reported.
- Weighted average CPI must be calculated from an input CPI table.
- A custom test set must include at least one instruction of every format and at least one branch with a negative displacement.
- The code must be maintainable because it will be extended in Etapa 2.

---

# 2. Technology

## Language

Use:

**Python 3.11+**

Avoid unnecessary external dependencies.

Prefer Python's standard library for:

- file handling
- command-line arguments
- data structures
- testing
- formatting

Recommended test framework:

```text
pytest
```

If pytest is used, keep it as the only required external development dependency unless another dependency is clearly justified.

---

# 3. Architecture

The project should follow a modular architecture.

Recommended structure:

```text
riscv-decoder/
│
├── AGENTS.md
├── README.md
├── requirements.txt
├── main.py
│
├── src/
│   ├── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── instruction.py
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   └── input_parser.py
│   │
│   ├── decoder/
│   │   ├── __init__.py
│   │   ├── decoder.py
│   │   ├── instruction_table.py
│   │   └── immediate.py
│   │
│   ├── assembler/
│   │   ├── __init__.py
│   │   └── disassembler.py
│   │
│   ├── statistics/
│   │   ├── __init__.py
│   │   └── statistics.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── bits.py
│       └── registers.py
│
├── tests/
│   ├── test_parser.py
│   ├── test_decoder.py
│   ├── test_immediate.py
│   ├── test_disassembler.py
│   └── test_statistics.py
│
├── examples/
│   ├── teste_hex.txt
│   ├── teste_bin.txt
│   └── casos_invalidos.txt
│
└── report/
    └── relatorio.pdf
```

Do not place all logic inside `main.py`.

---

# 4. Module Responsibilities

## `models/instruction.py`

Define the internal representation of a decoded instruction.

Recommended structure:

```python
@dataclass
class Instruction:
    pc: int
    word: int

    format: str | None = None
    mnemonic: str | None = None

    rd: int | None = None
    rs1: int | None = None
    rs2: int | None = None

    funct3: int | None = None
    funct7: int | None = None

    immediate: int | None = None

    assembly: str | None = None
    target: int | None = None

    valid: bool = True
```

Use `None` for fields that do not exist in a particular instruction format.

Do NOT invent values for nonexistent fields.

For example:

- B instructions must not receive an `rd`.
- U instructions must not receive `rs1`, `rs2`, or `funct3`.
- J instructions must not receive `rs1` or `rs2`.

This is important for the future hazard analysis.

---

# 5. Input Parser

File:

```text
src/parser/input_parser.py
```

Responsibilities:

1. Read the input file.
2. Process one instruction per line.
3. Ignore blank lines.
4. Ignore comments.
5. Accept hexadecimal input.
6. Accept binary input.
7. Automatically detect whether the file is hexadecimal or binary.
8. Ignore optional `0x` prefixes.
9. Convert instructions to 32-bit integer values.
10. Assign sequential PC values.
11. Support a configurable base address.

Suggested interface:

```python
def parse_file(
    path: str,
    base_address: int = 0
) -> list[tuple[int, int]]:
    ...
```

The parser must not know anything about instruction mnemonics.

It should only transform input text into machine words and addresses.

---

# 6. Bit Utilities

File:

```text
src/utils/bits.py
```

Provide reusable low-level bit manipulation functions.

Recommended:

```python
def get_bits(value: int, start: int, end: int) -> int:
    ...

def sign_extend(value: int, bits: int) -> int:
    ...
```

Use inclusive bit indexes consistently.

Example:

```python
opcode = get_bits(word, 0, 6)
rd = get_bits(word, 7, 11)
funct3 = get_bits(word, 12, 14)
rs1 = get_bits(word, 15, 19)
rs2 = get_bits(word, 20, 24)
funct7 = get_bits(word, 25, 31)
```

Do not duplicate bit-mask logic throughout the project.

---

# 7. Instruction Formats

The decoder must support these six formats:

```text
R
I
S
B
U
J
```

Field availability:

| Format | rd  | rs1 | rs2 | funct3 | funct7 | immediate |
| ------ | --- | --- | --- | ------ | ------ | --------- |
| R      | yes | yes | yes | yes    | yes    | no        |
| I      | yes | yes | no  | yes    | no     | 12-bit    |
| S      | no  | yes | yes | yes    | no     | 12-bit    |
| B      | no  | yes | yes | yes    | no     | 13-bit    |
| U      | yes | no  | no  | no     | no     | 32-bit    |
| J      | yes | no  | no  | no     | no     | 21-bit    |

Never expose fields that do not belong to the instruction format.

---

# 8. Instruction Table

File:

```text
src/decoder/instruction_table.py
```

Keep instruction definitions separate from decoding logic.

Use a data-driven structure rather than a very large nested `if`/`elif` chain.

Recommended conceptual model:

```python
@dataclass(frozen=True)
class InstructionDefinition:
    mnemonic: str
    format: str
    opcode: int
    funct3: int | None = None
    funct7: int | None = None
```

Example:

```python
InstructionDefinition(
    mnemonic="add",
    format="R",
    opcode=0b0110011,
    funct3=0b000,
    funct7=0b0000000,
)
```

The table must distinguish instructions using the appropriate combination of:

- opcode
- funct3
- funct7

Do not identify an instruction using opcode alone when funct3/funct7 are required.

---

# 9. Decoder

File:

```text
src/decoder/decoder.py
```

Recommended interface:

```python
def decode(pc: int, word: int) -> Instruction:
    ...
```

The decoder should:

1. Extract opcode.
2. Determine instruction format.
3. Extract valid fields.
4. Find the corresponding instruction definition.
5. Decode the immediate if applicable.
6. Return an `Instruction`.
7. Mark unknown instructions as invalid.
8. Never stop processing the entire input because one instruction is invalid.

Invalid instructions must retain enough information to report:

- PC
- original word
- invalid status

---

# 10. Immediate Decoding

File:

```text
src/decoder/immediate.py
```

Implement separate functions:

```python
def decode_i_immediate(word: int) -> int:
    ...

def decode_s_immediate(word: int) -> int:
    ...

def decode_b_immediate(word: int) -> int:
    ...

def decode_u_immediate(word: int) -> int:
    ...

def decode_j_immediate(word: int) -> int:
    ...
```

The B and J formats require special attention because their immediate bits are stored in non-contiguous positions.

Always apply sign extension where appropriate.

Mandatory regression test:

```text
0xFE628CE3
```

Expected:

```text
format = B
mnemonic = beq
rs1 = 5
rs2 = 6
immediate = -8
```

This test is important because bits 11–7 must NOT be interpreted as `rd` for a B instruction.

---

# 11. ABI Registers

File:

```text
src/utils/registers.py
```

Maintain the complete RISC-V ABI register mapping.

Example:

```python
ABI_REGISTERS = {
    0: "zero",
    1: "ra",
    2: "sp",
    3: "gp",
    4: "tp",
    5: "t0",
    6: "t1",
    7: "t2",
    8: "s0",
    9: "s1",
    10: "a0",
    ...
}
```

Provide:

```python
def register_name(register: int) -> str:
    ...
```

Assembly output must use ABI names rather than `xN` names.

---

# 12. Disassembler

File:

```text
src/assembler/disassembler.py
```

Despite the module name, this component generates assembly text from decoded instructions.

Recommended:

```python
def to_assembly(instruction: Instruction) -> str:
    ...
```

The output must:

- use the correct mnemonic
- use ABI register names
- include only valid operands
- format immediates correctly
- handle memory operands such as `offset(register)`
- recognize required pseudo-instructions
- display absolute targets for branches and jumps

Required examples include:

```text
addi s0, zero, 5
add a2, a1, a2
sw t1, 8(s1)
```

---

# 13. Pseudo-Instructions

Recognize common pseudo-instructions required by the assignment.

At minimum, the implementation must recognize:

```text
addi x0, x0, 0 → nop
jalr x0, 0(x1) → ret
```

Do not confuse a pseudo-instruction with a different machine instruction.

The original machine instruction must remain available in the `Instruction` object.

---

# 14. Branch and Jump Targets

For branch and jump instructions, calculate the absolute destination.

Conceptually:

```python
target = instruction.pc + instruction.immediate
```

Store the result in:

```python
instruction.target
```

The assembly output should use the absolute target address as required by the assignment.

---

# 15. Statistics

File:

```text
src/statistics/statistics.py
```

Implement:

```python
def count_formats(instructions):
    ...

def calculate_percentages(instructions):
    ...

def calculate_average_cpi(instructions, cpi_table):
    ...
```

Required output:

- number of instructions per format
- percentage per format
- weighted average CPI

Weighted CPI:

```text
average_cpi =
    sum(quantity_i * cpi_i) / total_quantity
```

The CPI table must be treated as input/configuration, not hard-coded unless the assignment explicitly provides fixed values.

---

# 16. CLI

The program should eventually support a simple command-line interface.

Suggested usage:

```bash
python main.py examples/teste_hex.txt
```

Optional base address:

```bash
python main.py examples/teste_hex.txt --base-address 0x1000
```

If CPI data is provided separately, support a clear mechanism for loading it.

Do not make the CLI responsible for decoding logic.

---

# 17. Output

The output should be human-readable.

Each instruction should contain at least:

```text
PC
Original word
Format
Mnemonic
Fields that exist
Immediate when applicable
Assembly
Target when applicable
```

Example conceptual output:

```text
PC: 0x00000000
Word: 0x00500413
Format: I
Mnemonic: addi
rd: x8 (s0)
rs1: x0 (zero)
funct3: 0
Immediate: 5
Assembly: addi s0, zero, 5
```

For invalid instructions:

```text
PC: 0x00000020
Word: 0x12345678
INVALID INSTRUCTION
```

Processing must continue after an invalid instruction.

---

# 18. Testing Strategy

Tests are mandatory for all important decoding behavior.

At minimum, cover:

## Parser

- hexadecimal input
- binary input
- automatic format detection
- `0x` prefix
- blank lines
- comments
- PC increments
- custom base address
- malformed input

## Formats

At least one valid instruction for each:

```text
R
I
S
B
U
J
```

## Mnemonics

Test instructions where:

- opcode is shared
- funct3 distinguishes instructions
- funct7 distinguishes instructions

Examples include distinctions such as:

```text
add vs sub
srli vs srai
lb vs lw
beq vs bltu
```

## Immediates

Test:

- positive I immediate
- negative I immediate
- S immediate
- positive B immediate
- negative B immediate
- U immediate
- positive J immediate
- negative J immediate

## Invalid instructions

Verify that:

1. invalid instructions are reported
2. processing continues
3. subsequent valid instructions are still decoded

## ABI

Verify important mappings such as:

```text
x0 → zero
x1 → ra
x2 → sp
x5 → t0
x6 → t1
x8 → s0
```

## Pseudo-instructions

Test:

```text
nop
ret
```

## Targets

Test branch/jump target calculation, including negative displacement.

## Statistics

Test:

- counts
- percentages
- weighted CPI

---

# 19. Required Initial Regression Cases

The following examples from the assignment must be used as initial regression tests.

### ADDI

```text
0x00500413
```

Expected:

```text
format = I
mnemonic = addi
rd = 8
rs1 = 0
immediate = 5
funct3 = 0
assembly = addi s0, zero, 5
```

### ADD

```text
0x00C58633
```

Expected:

```text
format = R
mnemonic = add
rd = 12
rs1 = 11
rs2 = 12
funct3 = 0
funct7 = 0
assembly = add a2, a1, a2
```

### SW

```text
0x0064A423
```

Expected:

```text
format = S
mnemonic = sw
rs1 = 9
rs2 = 6
immediate = 8
```

Assembly:

```text
sw t1, 8(s1)
```

### BEQ

```text
0xFE628CE3
```

Expected:

```text
format = B
mnemonic = beq
rs1 = 5
rs2 = 6
immediate = -8
```

Do not create `rd` for this instruction.

---

# 20. Error Handling

Errors should be explicit and useful.

Examples:

```text
Invalid hexadecimal instruction
Invalid binary instruction
Instruction must contain 32 bits
Unknown opcode
Unknown instruction encoding
Invalid input file
```

An unknown machine instruction inside an otherwise valid ROM must be reported as an invalid instruction rather than terminating the entire decoding process.

---

# 21. Code Quality Rules

Prefer:

- small functions
- single responsibility
- descriptive names
- type hints
- dataclasses
- immutable instruction definitions
- clear module boundaries
- automated tests
- deterministic output

Avoid:

- giant functions
- duplicated bit extraction
- duplicated register mappings
- hard-coded decoding logic scattered across files
- global mutable state
- unnecessary dependencies
- silently ignoring invalid input

Do not optimize prematurely.

Correctness and readability are more important than micro-optimizations.

---

# 22. Important Design Rule for Etapa 2

The first-stage decoder must preserve enough semantic information to support future hazard analysis.

Do not reduce an instruction to an assembly string only.

The decoded representation must preserve:

```text
PC
machine word
format
mnemonic
rd
rs1
rs2
immediate
```

Future Etapa 2 logic will need to determine:

```text
registers read
registers written
control-flow instructions
```

Therefore, the `Instruction` model should be treated as the interface between Etapa 1 and Etapa 2.

Do not implement hazard detection in the current stage unless explicitly requested.

---

# 23. Development Order

Implement the project in this order:

1. Create project structure.
2. Implement `Instruction`.
3. Implement bit utilities.
4. Implement ABI register mapping.
5. Implement input parser.
6. Add parser tests.
7. Implement instruction definitions.
8. Implement format detection.
9. Implement field extraction.
10. Implement immediate decoding.
11. Add immediate tests.
12. Implement mnemonic lookup.
13. Add decoder tests.
14. Implement disassembly.
15. Implement pseudo-instructions.
16. Implement branch/jump targets.
17. Implement statistics.
18. Implement CLI.
19. Run full test suite.
20. Create final test ROMs.
21. Review output manually.
22. Document usage in README.
23. Prepare report.

Do not implement the entire application in one pass.

---

# 24. Definition of Done — Etapa 1

The implementation is considered complete when:

- [ ] Python project structure is organized into modules.
- [ ] Hexadecimal input works.
- [ ] Binary input works.
- [ ] Input format is detected automatically.
- [ ] Blank lines are ignored.
- [ ] Comments are ignored.
- [ ] `0x` is accepted.
- [ ] Configurable base PC works.
- [ ] R format is decoded.
- [ ] I format is decoded.
- [ ] S format is decoded.
- [ ] B format is decoded.
- [ ] U format is decoded.
- [ ] J format is decoded.
- [ ] Mnemonics are correctly identified.
- [ ] `opcode`, `funct3`, and `funct7` are used where required.
- [ ] Only valid fields are exposed.
- [ ] I immediates work.
- [ ] S immediates work.
- [ ] B immediates work.
- [ ] U immediates work.
- [ ] J immediates work.
- [ ] Sign extension works.
- [ ] ABI register names are displayed.
- [ ] Branch targets are calculated.
- [ ] Jump targets are calculated.
- [ ] Required pseudo-instructions are recognized.
- [ ] Invalid instructions are reported.
- [ ] Processing continues after invalid instructions.
- [ ] Format statistics are generated.
- [ ] Percentages are generated.
- [ ] Weighted average CPI is calculated.
- [ ] Tests cover all six formats.
- [ ] Tests include a negative branch displacement.
- [ ] README explains how to run the program.
- [ ] Code is structured for future hazard analysis.
- [ ] No Etapa 2 hazard analysis is mixed into Etapa 1.

---

# 25. Agent Behavior

When modifying this project:

1. Read `AGENTS.md` before making architectural changes.
2. Preserve the modular architecture.
3. Do not silently change the interpretation of the assignment requirements.
4. Add or update tests whenever decoder behavior changes.
5. Prefer fixing the underlying abstraction rather than adding special cases.
6. Never introduce an `rd`, `rs1`, `rs2`, `funct3`, or `funct7` field when it does not exist for the instruction format.
7. Treat B and J immediate decoding as high-risk logic and always test it.
8. Keep machine-code representation and assembly representation separate.
9. Do not replace structured instruction data with strings.
10. Keep the implementation ready for Etapa 2.
11. Do not add hazard detection unless explicitly requested.
12. Before considering a change complete, run the relevant tests and then the full test suite.

---

# 26. Final Principle

The primary goal of this project is:

> **Reliable RISC-V instruction decoding.**

Correctness is more important than the number of instructions supported.

A decoder that incorrectly reports registers can create false hazards in Etapa 2. Therefore, instruction format, field validity, immediate reconstruction, and register read/write semantics must be implemented carefully and tested thoroughly.

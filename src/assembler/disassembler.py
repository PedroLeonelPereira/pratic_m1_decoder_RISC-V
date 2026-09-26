"""Render an already decoded instruction using ABI register names."""

from src.models.instruction import Instruction
from src.utils.registers import register_name


def _absolute_address(target: int) -> str:
    return f"0x{target:08X}" if target >= 0 else f"-0x{-target:X}"


def _fence_set(mask: int) -> str:
    return "".join(letter for bit, letter in ((3, "i"), (2, "o"), (1, "r"), (0, "w"))
                   if mask & (1 << bit)) or "0"


def _arithmetic_pseudo(instruction: Instruction) -> str | None:
    rd = register_name(instruction.rd) if instruction.rd is not None else None
    rs1 = register_name(instruction.rs1) if instruction.rs1 is not None else None
    rs2 = register_name(instruction.rs2) if instruction.rs2 is not None else None
    mnemonic = instruction.mnemonic
    immediate = instruction.immediate
    if mnemonic == "addi" and (instruction.rd, instruction.rs1, immediate) == (0, 0, 0):
        return "nop"
    if instruction.rd == 0:
        return None
    if mnemonic == "addi" and instruction.rs1 == 0:
        return f"li {rd}, {immediate}"
    if mnemonic == "addi" and immediate == 0:
        return f"mv {rd}, {rs1}"
    if mnemonic == "xori" and immediate == -1:
        return f"not {rd}, {rs1}"
    if mnemonic == "andi" and immediate == 255:
        return f"zext.b {rd}, {rs1}"
    if mnemonic == "sub" and instruction.rs1 == 0:
        return f"neg {rd}, {rs2}"
    if mnemonic == "sltiu" and immediate == 1:
        return f"seqz {rd}, {rs1}"
    if mnemonic == "sltu" and instruction.rs1 == 0:
        return f"snez {rd}, {rs2}"
    if mnemonic == "slt" and instruction.rs2 == 0:
        return f"sltz {rd}, {rs1}"
    if mnemonic == "slt" and instruction.rs1 == 0:
        return f"sgtz {rd}, {rs2}"
    return None


def _branch_pseudo(instruction: Instruction) -> str | None:
    first = register_name(instruction.rs1)
    second = register_name(instruction.rs2)
    target = _absolute_address(instruction.target)
    mnemonic = instruction.mnemonic
    if instruction.rs2 == 0:
        alias = {"beq": "beqz", "bne": "bnez", "blt": "bltz", "bge": "bgez"}.get(mnemonic)
        if alias:
            return f"{alias} {first}, {target}"
    if instruction.rs1 == 0:
        alias = {"blt": "bgtz", "bge": "blez"}.get(mnemonic)
        if alias:
            return f"{alias} {second}, {target}"
    alias = {"blt": "bgt", "bge": "ble", "bltu": "bgtu", "bgeu": "bleu"}.get(mnemonic)
    if alias:
        return f"{alias} {second}, {first}, {target}"
    return None


def _jump_pseudo(instruction: Instruction) -> str | None:
    if instruction.mnemonic == "jal":
        target = _absolute_address(instruction.target)
        if instruction.rd == 0:
            return f"j {target}"
        if instruction.rd == 1:
            return f"jal {target}"
    if instruction.mnemonic == "jalr" and instruction.immediate == 0:
        source = register_name(instruction.rs1)
        if instruction.rd == 0 and instruction.rs1 == 1:
            return "ret"
        if instruction.rd == 0:
            return f"jr {source}"
        if instruction.rd == 1:
            return f"jalr {source}"
    return None


def to_pseudo_assembly(instruction: Instruction) -> str | None:
    """Recognize single-word RV32I aliases without changing the real mnemonic."""
    if not instruction.valid:
        return None
    if instruction.format == "B":
        return _branch_pseudo(instruction)
    if instruction.mnemonic in ("jal", "jalr"):
        return _jump_pseudo(instruction)
    if instruction.mnemonic in ("addi", "xori", "andi", "sub", "sltiu", "sltu", "slt"):
        return _arithmetic_pseudo(instruction)
    return None


def to_assembly(instruction: Instruction) -> str:
    """Return assembly text; keep the original machine mnemonic in the model."""
    if not instruction.valid:
        return "INVALID INSTRUCTION"
    mnemonic = instruction.mnemonic
    rd = register_name(instruction.rd) if instruction.rd is not None else None
    rs1 = register_name(instruction.rs1) if instruction.rs1 is not None else None
    rs2 = register_name(instruction.rs2) if instruction.rs2 is not None else None
    immediate = instruction.immediate

    pseudo = to_pseudo_assembly(instruction)
    if pseudo in ("nop", "ret"):
        return pseudo
    if mnemonic == "fence.tso":
        return "fence.tso"
    if mnemonic == "fence":
        return (f"fence {_fence_set(instruction.fence_predecessor)}, "
                f"{_fence_set(instruction.fence_successor)}")
    if mnemonic in ("ecall", "ebreak"):
        return mnemonic
    if instruction.format == "R":
        return f"{mnemonic} {rd}, {rs1}, {rs2}"
    if mnemonic in ("lb", "lh", "lw", "lbu", "lhu", "jalr"):
        return f"{mnemonic} {rd}, {immediate}({rs1})"
    if instruction.format == "I":
        return f"{mnemonic} {rd}, {rs1}, {immediate}"
    if instruction.format == "S":
        return f"{mnemonic} {rs2}, {immediate}({rs1})"
    if instruction.format == "B":
        return f"{mnemonic} {rs1}, {rs2}, {_absolute_address(instruction.target)}"
    if instruction.format == "U":
        return f"{mnemonic} {rd}, 0x{(immediate >> 12) & 0xFFFFF:X}"
    if instruction.format == "J":
        return f"{mnemonic} {rd}, {_absolute_address(instruction.target)}"
    raise ValueError(f"Unsupported format: {instruction.format}")

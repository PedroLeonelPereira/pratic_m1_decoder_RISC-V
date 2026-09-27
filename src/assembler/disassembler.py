"""Turn decoded instruction dictionaries into assembly text."""

from src.utils.registers import register_name


def _absolute_address(target):
    if target >= 0:
        return f"0x{target:08X}"
    return f"-0x{-target:X}"


def _fence_set(mask):
    result = ""
    bit_names = ((3, "i"), (2, "o"), (1, "r"), (0, "w"))
    for bit, letter in bit_names:
        if mask & (1 << bit):
            result += letter
    if result == "":
        return "0"
    return result


def _arithmetic_pseudo(instruction):
    rd = instruction["rd"]
    rs1 = instruction["rs1"]
    rs2 = instruction["rs2"]
    mnemonic = instruction["mnemonic"]
    immediate = instruction["immediate"]

    if mnemonic == "addi" and (rd, rs1, immediate) == (0, 0, 0):
        return "nop"
    if rd == 0:
        return None
    if mnemonic == "addi" and rs1 == 0:
        return f"li {register_name(rd)}, {immediate}"
    if mnemonic == "addi" and immediate == 0:
        return f"mv {register_name(rd)}, {register_name(rs1)}"
    if mnemonic == "xori" and immediate == -1:
        return f"not {register_name(rd)}, {register_name(rs1)}"
    if mnemonic == "andi" and immediate == 255:
        return f"zext.b {register_name(rd)}, {register_name(rs1)}"
    if mnemonic == "sub" and rs1 == 0:
        return f"neg {register_name(rd)}, {register_name(rs2)}"
    if mnemonic == "sltiu" and immediate == 1:
        return f"seqz {register_name(rd)}, {register_name(rs1)}"
    if mnemonic == "sltu" and rs1 == 0:
        return f"snez {register_name(rd)}, {register_name(rs2)}"
    if mnemonic == "slt" and rs2 == 0:
        return f"sltz {register_name(rd)}, {register_name(rs1)}"
    if mnemonic == "slt" and rs1 == 0:
        return f"sgtz {register_name(rd)}, {register_name(rs2)}"
    return None


def _branch_pseudo(instruction):
    first = register_name(instruction["rs1"])
    second = register_name(instruction["rs2"])
    target = _absolute_address(instruction["target"])
    mnemonic = instruction["mnemonic"]

    if instruction["rs2"] == 0:
        aliases = {
            "beq": "beqz", "bne": "bnez", "blt": "bltz", "bge": "bgez",
        }
        if mnemonic in aliases:
            return f"{aliases[mnemonic]} {first}, {target}"

    if instruction["rs1"] == 0:
        aliases = {"blt": "bgtz", "bge": "blez"}
        if mnemonic in aliases:
            return f"{aliases[mnemonic]} {second}, {target}"

    aliases = {"blt": "bgt", "bge": "ble", "bltu": "bgtu", "bgeu": "bleu"}
    if mnemonic in aliases:
        return f"{aliases[mnemonic]} {second}, {first}, {target}"
    return None


def _jump_pseudo(instruction):
    mnemonic = instruction["mnemonic"]
    rd = instruction["rd"]
    rs1 = instruction["rs1"]
    immediate = instruction["immediate"]

    if mnemonic == "jal":
        target = _absolute_address(instruction["target"])
        if rd == 0:
            return f"j {target}"
        if rd == 1:
            return f"jal {target}"

    if mnemonic == "jalr" and immediate == 0:
        source = register_name(rs1)
        if rd == 0 and rs1 == 1:
            return "ret"
        if rd == 0:
            return f"jr {source}"
        if rd == 1:
            return f"jalr {source}"
    return None


def to_pseudo_assembly(instruction):
    """Return a recognized pseudo-instruction, if one applies."""
    if not instruction["valid"]:
        return None
    if instruction["format"] == "B":
        return _branch_pseudo(instruction)
    if instruction["mnemonic"] == "jal" or instruction["mnemonic"] == "jalr":
        return _jump_pseudo(instruction)

    mnemonic = instruction["mnemonic"]
    if mnemonic in ("addi", "xori", "andi", "sub", "sltiu", "sltu", "slt"):
        return _arithmetic_pseudo(instruction)
    return None


def to_assembly(instruction):
    """Return the assembly representation using ABI register names."""
    if not instruction["valid"]:
        return "INVALID INSTRUCTION"

    mnemonic = instruction["mnemonic"]
    rd = instruction["rd"]
    rs1 = instruction["rs1"]
    rs2 = instruction["rs2"]
    immediate = instruction["immediate"]

    rd_name = register_name(rd) if rd is not None else None
    rs1_name = register_name(rs1) if rs1 is not None else None
    rs2_name = register_name(rs2) if rs2 is not None else None

    pseudo = to_pseudo_assembly(instruction)
    if pseudo == "nop" or pseudo == "ret":
        return pseudo
    if mnemonic == "fence.tso":
        return "fence.tso"
    if mnemonic == "fence":
        predecessor = _fence_set(instruction["fence_predecessor"])
        successor = _fence_set(instruction["fence_successor"])
        return f"fence {predecessor}, {successor}"
    if mnemonic == "ecall" or mnemonic == "ebreak":
        return mnemonic
    if instruction["format"] == "R":
        return f"{mnemonic} {rd_name}, {rs1_name}, {rs2_name}"
    if mnemonic in ("lb", "lh", "lw", "lbu", "lhu", "jalr"):
        return f"{mnemonic} {rd_name}, {immediate}({rs1_name})"
    if instruction["format"] == "I":
        return f"{mnemonic} {rd_name}, {rs1_name}, {immediate}"
    if instruction["format"] == "S":
        return f"{mnemonic} {rs2_name}, {immediate}({rs1_name})"
    if instruction["format"] == "B":
        target = _absolute_address(instruction["target"])
        return f"{mnemonic} {rs1_name}, {rs2_name}, {target}"
    if instruction["format"] == "U":
        value = (immediate >> 12) & 0xFFFFF
        return f"{mnemonic} {rd_name}, 0x{value:X}"
    if instruction["format"] == "J":
        target = _absolute_address(instruction["target"])
        return f"{mnemonic} {rd_name}, {target}"

    raise ValueError(f"Unsupported format: {instruction['format']}")

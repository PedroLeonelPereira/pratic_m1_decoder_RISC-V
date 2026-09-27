"""Instruction encodings supported by the RV32I decoder."""

from src.utils.bits import get_bits


# Each dictionary describes one instruction encoding.
DEFINITIONS = [
    {"mnemonic": "add", "format": "R", "opcode": 0x33, "funct3": 0, "funct7": 0x00},
    {"mnemonic": "sub", "format": "R", "opcode": 0x33, "funct3": 0, "funct7": 0x20},
    {"mnemonic": "sll", "format": "R", "opcode": 0x33, "funct3": 1, "funct7": 0x00},
    {"mnemonic": "slt", "format": "R", "opcode": 0x33, "funct3": 2, "funct7": 0x00},
    {"mnemonic": "sltu", "format": "R", "opcode": 0x33, "funct3": 3, "funct7": 0x00},
    {"mnemonic": "xor", "format": "R", "opcode": 0x33, "funct3": 4, "funct7": 0x00},
    {"mnemonic": "srl", "format": "R", "opcode": 0x33, "funct3": 5, "funct7": 0x00},
    {"mnemonic": "sra", "format": "R", "opcode": 0x33, "funct3": 5, "funct7": 0x20},
    {"mnemonic": "or", "format": "R", "opcode": 0x33, "funct3": 6, "funct7": 0x00},
    {"mnemonic": "and", "format": "R", "opcode": 0x33, "funct3": 7, "funct7": 0x00},
    {"mnemonic": "addi", "format": "I", "opcode": 0x13, "funct3": 0},
    {"mnemonic": "slti", "format": "I", "opcode": 0x13, "funct3": 2},
    {"mnemonic": "sltiu", "format": "I", "opcode": 0x13, "funct3": 3},
    {"mnemonic": "xori", "format": "I", "opcode": 0x13, "funct3": 4},
    {"mnemonic": "ori", "format": "I", "opcode": 0x13, "funct3": 6},
    {"mnemonic": "andi", "format": "I", "opcode": 0x13, "funct3": 7},
    {"mnemonic": "slli", "format": "I", "opcode": 0x13, "funct3": 1, "shift_upper_bits": 0x00},
    {"mnemonic": "srli", "format": "I", "opcode": 0x13, "funct3": 5, "shift_upper_bits": 0x00},
    {"mnemonic": "srai", "format": "I", "opcode": 0x13, "funct3": 5, "shift_upper_bits": 0x20},
    {"mnemonic": "lb", "format": "I", "opcode": 0x03, "funct3": 0},
    {"mnemonic": "lh", "format": "I", "opcode": 0x03, "funct3": 1},
    {"mnemonic": "lw", "format": "I", "opcode": 0x03, "funct3": 2},
    {"mnemonic": "lbu", "format": "I", "opcode": 0x03, "funct3": 4},
    {"mnemonic": "lhu", "format": "I", "opcode": 0x03, "funct3": 5},
    {"mnemonic": "jalr", "format": "I", "opcode": 0x67, "funct3": 0},
    {"mnemonic": "sb", "format": "S", "opcode": 0x23, "funct3": 0},
    {"mnemonic": "sh", "format": "S", "opcode": 0x23, "funct3": 1},
    {"mnemonic": "sw", "format": "S", "opcode": 0x23, "funct3": 2},
    {"mnemonic": "beq", "format": "B", "opcode": 0x63, "funct3": 0},
    {"mnemonic": "bne", "format": "B", "opcode": 0x63, "funct3": 1},
    {"mnemonic": "blt", "format": "B", "opcode": 0x63, "funct3": 4},
    {"mnemonic": "bge", "format": "B", "opcode": 0x63, "funct3": 5},
    {"mnemonic": "bltu", "format": "B", "opcode": 0x63, "funct3": 6},
    {"mnemonic": "bgeu", "format": "B", "opcode": 0x63, "funct3": 7},
    {"mnemonic": "lui", "format": "U", "opcode": 0x37},
    {"mnemonic": "auipc", "format": "U", "opcode": 0x17},
    {"mnemonic": "jal", "format": "J", "opcode": 0x6F},
    # FENCE.TSO is a named encoding of the RV32I FENCE instruction.
    {"mnemonic": "fence.tso", "format": "I", "opcode": 0x0F,
     "funct3": 0, "encoding_mask": 0xFFFFFFFF,
     "encoding_value": 0x8330000F, "operand_kind": "fence"},
    {"mnemonic": "fence", "format": "I", "opcode": 0x0F,
     "funct3": 0, "operand_kind": "fence"},
    {"mnemonic": "ecall", "format": "I", "opcode": 0x73,
     "funct3": 0, "encoding_mask": 0xFFFFFFFF,
     "encoding_value": 0x00000073, "operand_kind": "system"},
    {"mnemonic": "ebreak", "format": "I", "opcode": 0x73,
     "funct3": 0, "encoding_mask": 0xFFFFFFFF,
     "encoding_value": 0x00100073, "operand_kind": "system"},
]


def find_definition(word):
    """Find the instruction whose encoding matches this word."""
    opcode = get_bits(word, 0, 6)
    funct3 = get_bits(word, 12, 14)
    funct7 = get_bits(word, 25, 31)

    for definition in DEFINITIONS:
        if definition["opcode"] != opcode:
            continue
        if "funct3" in definition and definition["funct3"] != funct3:
            continue
        if "funct7" in definition and definition["funct7"] != funct7:
            continue
        if ("shift_upper_bits" in definition
                and definition["shift_upper_bits"] != funct7):
            continue
        mask = definition.get("encoding_mask", 0)
        value = definition.get("encoding_value", 0)
        if word & mask != value:
            continue
        return definition

    return None

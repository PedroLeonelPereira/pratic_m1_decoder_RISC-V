"""Declarative encodings for the RV32I base instruction set."""

from dataclasses import dataclass

from src.utils.bits import get_bits


@dataclass(frozen=True)
class InstructionDefinition:
    mnemonic: str
    format: str
    opcode: int
    funct3: int | None = None
    funct7: int | None = None
    # I-format shifts use bits 31:25 to validate their encoding. These bits
    # are not an exposed funct7 field of the decoded I-format instruction.
    shift_upper_bits: int | None = None
    encoding_mask: int = 0
    encoding_value: int = 0
    operand_kind: str = "normal"


DEFINITIONS = (
    InstructionDefinition("add", "R", 0x33, 0, 0x00),
    InstructionDefinition("sub", "R", 0x33, 0, 0x20),
    InstructionDefinition("sll", "R", 0x33, 1, 0x00),
    InstructionDefinition("slt", "R", 0x33, 2, 0x00),
    InstructionDefinition("sltu", "R", 0x33, 3, 0x00),
    InstructionDefinition("xor", "R", 0x33, 4, 0x00),
    InstructionDefinition("srl", "R", 0x33, 5, 0x00),
    InstructionDefinition("sra", "R", 0x33, 5, 0x20),
    InstructionDefinition("or", "R", 0x33, 6, 0x00),
    InstructionDefinition("and", "R", 0x33, 7, 0x00),
    InstructionDefinition("addi", "I", 0x13, 0),
    InstructionDefinition("slti", "I", 0x13, 2),
    InstructionDefinition("sltiu", "I", 0x13, 3),
    InstructionDefinition("xori", "I", 0x13, 4),
    InstructionDefinition("ori", "I", 0x13, 6),
    InstructionDefinition("andi", "I", 0x13, 7),
    InstructionDefinition("slli", "I", 0x13, 1, shift_upper_bits=0x00),
    InstructionDefinition("srli", "I", 0x13, 5, shift_upper_bits=0x00),
    InstructionDefinition("srai", "I", 0x13, 5, shift_upper_bits=0x20),
    InstructionDefinition("lb", "I", 0x03, 0),
    InstructionDefinition("lh", "I", 0x03, 1),
    InstructionDefinition("lw", "I", 0x03, 2),
    InstructionDefinition("lbu", "I", 0x03, 4),
    InstructionDefinition("lhu", "I", 0x03, 5),
    InstructionDefinition("jalr", "I", 0x67, 0),
    InstructionDefinition("sb", "S", 0x23, 0),
    InstructionDefinition("sh", "S", 0x23, 1),
    InstructionDefinition("sw", "S", 0x23, 2),
    InstructionDefinition("beq", "B", 0x63, 0),
    InstructionDefinition("bne", "B", 0x63, 1),
    InstructionDefinition("blt", "B", 0x63, 4),
    InstructionDefinition("bge", "B", 0x63, 5),
    InstructionDefinition("bltu", "B", 0x63, 6),
    InstructionDefinition("bgeu", "B", 0x63, 7),
    InstructionDefinition("lui", "U", 0x37),
    InstructionDefinition("auipc", "U", 0x17),
    InstructionDefinition("jal", "J", 0x6F),
    # FENCE.TSO is a named encoding of the RV32I FENCE instruction.
    InstructionDefinition("fence.tso", "I", 0x0F, 0,
                          encoding_mask=0xFFFFFFFF, encoding_value=0x8330000F,
                          operand_kind="fence"),
    InstructionDefinition("fence", "I", 0x0F, 0, operand_kind="fence"),
    InstructionDefinition("ecall", "I", 0x73, 0,
                          encoding_mask=0xFFFFFFFF, encoding_value=0x00000073,
                          operand_kind="system"),
    InstructionDefinition("ebreak", "I", 0x73, 0,
                          encoding_mask=0xFFFFFFFF, encoding_value=0x00100073,
                          operand_kind="system"),
)


def find_definition(word: int) -> InstructionDefinition | None:
    """Match the complete encoding constraints of an approved instruction."""
    opcode = get_bits(word, 0, 6)
    for definition in DEFINITIONS:
        if definition.opcode != opcode:
            continue
        if definition.funct3 is not None and get_bits(word, 12, 14) != definition.funct3:
            continue
        if definition.funct7 is not None and get_bits(word, 25, 31) != definition.funct7:
            continue
        if (definition.shift_upper_bits is not None
                and get_bits(word, 25, 31) != definition.shift_upper_bits):
            continue
        if word & definition.encoding_mask != definition.encoding_value:
            continue
        return definition
    return None

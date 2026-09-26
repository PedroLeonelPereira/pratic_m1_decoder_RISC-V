"""Turn a machine word into format-correct structured instruction data."""

from src.decoder.immediate import (
    decode_b_immediate, decode_i_immediate, decode_j_immediate,
    decode_s_immediate, decode_u_immediate,
)
from src.decoder.instruction_table import DEFINITIONS, find_definition
from src.models.instruction import Instruction
from src.utils.bits import get_bits


def decode(pc: int, word: int) -> Instruction:
    """Decode one word; an unknown encoding returns an invalid instruction."""
    if not 0 <= word <= 0xFFFFFFFF:
        raise ValueError("Instruction word must contain 32 bits")
    opcode = get_bits(word, 0, 6)
    definition = find_definition(word)
    if definition is None:
        reason = ("Unknown instruction encoding" if any(
            item.opcode == opcode for item in DEFINITIONS
        ) else "Unknown opcode")
        return Instruction(pc=pc, word=word, valid=False, error=reason)

    instruction = Instruction(
        pc=pc, word=word, format=definition.format,
        mnemonic=definition.mnemonic, opcode=opcode,
    )
    if definition.operand_kind == "system":
        # ECALL and EBREAK are I-shaped encodings without register operands.
        return instruction
    if definition.operand_kind == "fence":
        # The encoded rd/rs1 positions are reserved, not register operands.
        instruction.fence_mode = get_bits(word, 28, 31)
        instruction.fence_predecessor = get_bits(word, 24, 27)
        instruction.fence_successor = get_bits(word, 20, 23)
        return instruction
    format_name = definition.format
    if format_name in ("R", "I", "U", "J"):
        instruction.rd = get_bits(word, 7, 11)
    if format_name in ("R", "I", "S", "B"):
        instruction.rs1 = get_bits(word, 15, 19)
        instruction.funct3 = get_bits(word, 12, 14)
    if format_name in ("R", "S", "B"):
        instruction.rs2 = get_bits(word, 20, 24)
    if format_name == "R":
        instruction.funct7 = get_bits(word, 25, 31)
    elif format_name == "I":
        instruction.immediate = (
            get_bits(word, 20, 24) if definition.shift_upper_bits is not None
            else decode_i_immediate(word)
        )
    elif format_name == "S":
        instruction.immediate = decode_s_immediate(word)
    elif format_name == "B":
        instruction.immediate = decode_b_immediate(word)
    elif format_name == "U":
        instruction.immediate = decode_u_immediate(word)
    elif format_name == "J":
        instruction.immediate = decode_j_immediate(word)
    if format_name in ("B", "J"):
        instruction.target = pc + instruction.immediate
    return instruction

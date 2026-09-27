"""Decode one 32-bit machine word into instruction fields."""

from src.decoder.immediate import (
    decode_b_immediate, decode_i_immediate, decode_j_immediate,
    decode_s_immediate, decode_u_immediate,
)
from src.decoder.instruction_table import DEFINITIONS, find_definition
from src.models.instruction import new_instruction
from src.utils.bits import get_bits


def decode(pc, word):
    """Decode one word, or return it marked as invalid."""
    if word < 0 or word > 0xFFFFFFFF:
        raise ValueError("Instruction word must contain 32 bits")

    opcode = get_bits(word, 0, 6)
    definition = find_definition(word)
    instruction = new_instruction(pc, word)

    if definition is None:
        instruction["valid"] = False
        found_opcode = False
        for item in DEFINITIONS:
            if item["opcode"] == opcode:
                found_opcode = True
                break
        if found_opcode:
            instruction["error"] = "Unknown instruction encoding"
        else:
            instruction["error"] = "Unknown opcode"
        return instruction

    instruction["format"] = definition["format"]
    instruction["mnemonic"] = definition["mnemonic"]
    instruction["opcode"] = opcode

    # ECALL and EBREAK do not use register operands.
    if definition.get("operand_kind") == "system":
        return instruction

    if definition.get("operand_kind") == "fence":
        # These bit positions describe FENCE ordering sets, not registers.
        instruction["fence_mode"] = get_bits(word, 28, 31)
        instruction["fence_predecessor"] = get_bits(word, 24, 27)
        instruction["fence_successor"] = get_bits(word, 20, 23)
        return instruction

    format_name = definition["format"]
    if format_name in ("R", "I", "U", "J"):
        instruction["rd"] = get_bits(word, 7, 11)
    if format_name in ("R", "I", "S", "B"):
        instruction["rs1"] = get_bits(word, 15, 19)
        instruction["funct3"] = get_bits(word, 12, 14)
    if format_name in ("R", "S", "B"):
        instruction["rs2"] = get_bits(word, 20, 24)

    if format_name == "R":
        instruction["funct7"] = get_bits(word, 25, 31)
    elif format_name == "I":
        if "shift_upper_bits" in definition:
            instruction["immediate"] = get_bits(word, 20, 24)
        else:
            instruction["immediate"] = decode_i_immediate(word)
    elif format_name == "S":
        instruction["immediate"] = decode_s_immediate(word)
    elif format_name == "B":
        instruction["immediate"] = decode_b_immediate(word)
    elif format_name == "U":
        instruction["immediate"] = decode_u_immediate(word)
    elif format_name == "J":
        instruction["immediate"] = decode_j_immediate(word)

    if format_name == "B" or format_name == "J":
        instruction["target"] = pc + instruction["immediate"]

    return instruction

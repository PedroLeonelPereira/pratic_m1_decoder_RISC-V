"""Create the dictionary used to store one decoded instruction."""


def new_instruction(pc, word):
    """Return an instruction with every field initialized."""
    return {
        "pc": pc,
        "word": word,
        "format": None,
        "mnemonic": None,
        "opcode": None,
        "rd": None,
        "rs1": None,
        "rs2": None,
        "funct3": None,
        "funct7": None,
        "immediate": None,
        "assembly": None,
        "pseudo": None,
        "target": None,
        "fence_mode": None,
        "fence_predecessor": None,
        "fence_successor": None,
        "valid": True,
        "error": None,
    }

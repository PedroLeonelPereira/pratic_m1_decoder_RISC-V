"""Read ROM text and return pairs of program counter and machine word."""


def _without_comment(line):
    for marker in ("#", "//", ";"):
        line = line.split(marker, 1)[0]
    return line.strip()


def _parse_word(token, line_number):
    has_prefix = token.lower().startswith("0x")
    digits = token[2:] if has_prefix else token

    if not has_prefix and len(digits) == 32:
        for digit in digits:
            if digit != "0" and digit != "1":
                raise ValueError(
                    f"Line {line_number}: invalid binary instruction"
                )
        return int(digits, 2), "binary"

    if len(digits) != 8:
        raise ValueError(
            f"Line {line_number}: instruction must contain 32 bits"
        )

    try:
        return int(digits, 16), "hexadecimal"
    except ValueError:
        raise ValueError(
            f"Line {line_number}: invalid hexadecimal instruction"
        )


def parse_file(path, base_address=0):
    """Read one hexadecimal or binary instruction from each non-empty line."""
    if base_address < 0:
        raise ValueError("Base address must be nonnegative")

    instructions = []
    file_format = None

    with open(path, encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, start=1):
            token = _without_comment(line)
            if not token:
                continue

            word, detected_format = _parse_word(token, line_number)
            if file_format is not None and detected_format != file_format:
                raise ValueError(
                    f"Line {line_number}: mixed hexadecimal and binary instructions"
                )

            file_format = detected_format
            pc = base_address + 4 * len(instructions)
            instructions.append((pc, word))

    return instructions

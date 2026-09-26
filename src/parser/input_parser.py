"""Read ROM text without interpreting instruction encodings."""

from pathlib import Path


class InputFormatError(ValueError):
    """A non-comment input line is not one 32-bit machine word."""


def _without_comment(line: str) -> str:
    for marker in ("#", "//", ";"):
        line = line.split(marker, 1)[0]
    return line.strip()


def _parse_word(token: str, line_number: int) -> tuple[int, str]:
    prefixed = token.lower().startswith("0x")
    digits = token[2:] if prefixed else token
    if not prefixed and len(digits) == 32:
        if any(digit not in "01" for digit in digits):
            raise InputFormatError(f"Line {line_number}: invalid binary instruction")
        return int(digits, 2), "binary"
    if len(digits) != 8:
        raise InputFormatError(f"Line {line_number}: instruction must contain 32 bits")
    try:
        return int(digits, 16), "hexadecimal"
    except ValueError as error:
        raise InputFormatError(
            f"Line {line_number}: invalid hexadecimal instruction"
        ) from error


def parse_file(path: str | Path, base_address: int = 0) -> list[tuple[int, int]]:
    """Return sequential (PC, word) pairs from one hex or binary ROM file."""
    if base_address < 0:
        raise ValueError("Base address must be nonnegative")
    instructions: list[tuple[int, int]] = []
    file_format: str | None = None
    with Path(path).open(encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, start=1):
            token = _without_comment(line)
            if not token:
                continue
            word, detected = _parse_word(token, line_number)
            if file_format is not None and detected != file_format:
                raise InputFormatError(
                    f"Line {line_number}: mixed hexadecimal and binary instructions"
                )
            file_format = detected
            instructions.append((base_address + 4 * len(instructions), word))
    return instructions

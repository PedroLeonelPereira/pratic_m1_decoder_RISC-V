"""Bit operations shared by the decoder and immediate reconstruction."""


def get_bits(value: int, start: int, end: int) -> int:
    """Return bits from start through end, with both indexes inclusive."""
    if start < 0 or end < start:
        raise ValueError("Invalid bit range")
    return (value >> start) & ((1 << (end - start + 1)) - 1)


def sign_extend(value: int, bits: int) -> int:
    """Interpret the low ``bits`` of value as a signed two's-complement number."""
    if bits <= 0:
        raise ValueError("Bit width must be positive")
    value &= (1 << bits) - 1
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign

"""Immediate reconstruction for the six 32-bit instruction formats."""

from src.utils.bits import get_bits, sign_extend


def decode_i_immediate(word: int) -> int:
    return sign_extend(get_bits(word, 20, 31), 12)


def decode_s_immediate(word: int) -> int:
    value = (get_bits(word, 25, 31) << 5) | get_bits(word, 7, 11)
    return sign_extend(value, 12)


def decode_b_immediate(word: int) -> int:
    value = (get_bits(word, 31, 31) << 12)
    value |= get_bits(word, 7, 7) << 11
    value |= get_bits(word, 25, 30) << 5
    value |= get_bits(word, 8, 11) << 1
    return sign_extend(value, 13)


def decode_u_immediate(word: int) -> int:
    return sign_extend(get_bits(word, 12, 31) << 12, 32)


def decode_j_immediate(word: int) -> int:
    value = get_bits(word, 31, 31) << 20
    value |= get_bits(word, 12, 19) << 12
    value |= get_bits(word, 20, 20) << 11
    value |= get_bits(word, 21, 30) << 1
    return sign_extend(value, 21)

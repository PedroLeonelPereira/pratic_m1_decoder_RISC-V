import unittest

from src.decoder.immediate import (
    decode_b_immediate, decode_i_immediate, decode_j_immediate,
    decode_s_immediate, decode_u_immediate,
)


class ImmediateTests(unittest.TestCase):
    def test_i_positive_and_negative(self):
        self.assertEqual(decode_i_immediate(0x00500413), 5)
        self.assertEqual(decode_i_immediate(0xFF800413), -8)

    def test_s_positive_and_negative(self):
        self.assertEqual(decode_s_immediate(0x0064A423), 8)
        self.assertEqual(decode_s_immediate(0xFE64AC23), -8)

    def test_b_positive_and_negative(self):
        self.assertEqual(decode_b_immediate(0x00628463), 8)
        self.assertEqual(decode_b_immediate(0xFE628CE3), -8)

    def test_u_aligned_signed_32_bit_value(self):
        self.assertEqual(decode_u_immediate(0x12345437), 0x12345000)
        self.assertEqual(decode_u_immediate(0xFFFFF437), -4096)

    def test_j_reassembles_scrambled_bits_and_extends_sign(self):
        self.assertEqual(decode_j_immediate(0x008000EF), 8)
        self.assertEqual(decode_j_immediate(0xFF9FF0EF), -8)
        self.assertEqual(decode_j_immediate(0x7FFFF0EF), 1048574)
        self.assertEqual(decode_j_immediate(0x800000EF), -1048576)

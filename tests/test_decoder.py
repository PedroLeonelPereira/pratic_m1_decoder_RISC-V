import unittest

from src.decoder.decoder import decode


class DecoderTests(unittest.TestCase):
    def test_assignment_regressions(self):
        cases = (
            (0x00500413, "I", "addi", 8, 0, None, 5),
            (0x00C58633, "R", "add", 12, 11, 12, None),
            (0x0064A423, "S", "sw", None, 9, 6, 8),
            (0xFE628CE3, "B", "beq", None, 5, 6, -8),
        )
        for word, format_name, mnemonic, rd, rs1, rs2, immediate in cases:
            with self.subTest(word=hex(word)):
                item = decode(0x1000, word)
                self.assertEqual(
                    (item.format, item.mnemonic, item.rd, item.rs1, item.rs2,
                     item.immediate),
                    (format_name, mnemonic, rd, rs1, rs2, immediate),
                )

    def test_only_valid_fields_are_exposed(self):
        b = decode(0, 0xFE628CE3)
        self.assertIsNone(b.rd)
        self.assertIsNone(b.funct7)
        self.assertEqual(b.target, -8)
        u = decode(0, 0x12345437)
        for field in ("rs1", "rs2", "funct3", "funct7"):
            self.assertIsNone(getattr(u, field))
        j = decode(0x1000, 0xFF9FF0EF)
        for field in ("rs1", "rs2", "funct3", "funct7"):
            self.assertIsNone(getattr(j, field))
        self.assertEqual((j.immediate, j.target), (-8, 0xFF8))

    def test_opcode_funct3_and_encoding_differences(self):
        words = {
            0x00C58633: "add", 0x40C58633: "sub",
            0x0020D093: "srli", 0x4020D093: "srai",
            0x00008083: "lb", 0x0000A083: "lw",
            0x00628463: "beq", 0x0062E463: "bltu",
        }
        for word, mnemonic in words.items():
            with self.subTest(word=hex(word)):
                self.assertEqual(decode(0, word).mnemonic, mnemonic)
        for word in (0xFFFFFFFF, 0x02000033, 0x2020D093):
            with self.subTest(invalid=hex(word)):
                item = decode(4, word)
                self.assertFalse(item.valid)
                self.assertEqual((item.pc, item.word), (4, word))

    def test_shift_encoding_bits_are_not_reported_as_i_funct7(self):
        item = decode(0, 0x4020D093)
        self.assertEqual((item.format, item.immediate), ("I", 2))
        self.assertIsNone(item.funct7)

import unittest

from src.assembler.disassembler import to_assembly
from src.decoder.decoder import decode


def encode_r(funct3: int, funct7: int) -> int:
    return (funct7 << 25) | (10 << 20) | (9 << 15) | (funct3 << 12) | (8 << 7) | 0x33


def encode_i(opcode: int, funct3: int, immediate: int = -8) -> int:
    return ((immediate & 0xFFF) << 20) | (9 << 15) | (funct3 << 12) | (8 << 7) | opcode


def encode_s(funct3: int) -> int:
    immediate = -8 & 0xFFF
    return (((immediate >> 5) & 0x7F) << 25) | (10 << 20) | (9 << 15) | (funct3 << 12) | ((immediate & 0x1F) << 7) | 0x23


def encode_b(funct3: int) -> int:
    immediate = -8 & 0x1FFF
    return (((immediate >> 12) & 1) << 31) | (((immediate >> 5) & 0x3F) << 25) | (10 << 20) | (9 << 15) | (funct3 << 12) | (((immediate >> 1) & 0xF) << 8) | (((immediate >> 11) & 1) << 7) | 0x63


class Rv32iTests(unittest.TestCase):
    def test_all_register_and_immediate_arithmetic_encodings(self):
        registers = (("add", 0, 0), ("sub", 0, 0x20), ("sll", 1, 0),
                     ("slt", 2, 0), ("sltu", 3, 0), ("xor", 4, 0),
                     ("srl", 5, 0), ("sra", 5, 0x20), ("or", 6, 0),
                     ("and", 7, 0))
        for mnemonic, funct3, funct7 in registers:
            with self.subTest(mnemonic=mnemonic):
                item = decode(0x1000, encode_r(funct3, funct7))
                self.assertEqual((item.format, item.mnemonic, item.rd, item.rs1,
                                  item.rs2, item.funct3, item.funct7),
                                 ("R", mnemonic, 8, 9, 10, funct3, funct7))
        immediates = (("addi", 0), ("slti", 2), ("sltiu", 3),
                      ("xori", 4), ("ori", 6), ("andi", 7))
        for mnemonic, funct3 in immediates:
            with self.subTest(mnemonic=mnemonic):
                item = decode(0x1000, encode_i(0x13, funct3))
                self.assertEqual((item.mnemonic, item.immediate, item.funct7),
                                 (mnemonic, -8, None))
        for mnemonic, funct3, upper in (("slli", 1, 0), ("srli", 5, 0),
                                        ("srai", 5, 0x20)):
            word = encode_i(0x13, funct3, (upper << 5) | 3)
            item = decode(0, word)
            self.assertEqual((item.mnemonic, item.immediate, item.funct7),
                             (mnemonic, 3, None))

    def test_all_memory_and_branch_encodings(self):
        for mnemonic, funct3 in (("lb", 0), ("lh", 1), ("lw", 2),
                                 ("lbu", 4), ("lhu", 5)):
            item = decode(0, encode_i(0x03, funct3))
            self.assertEqual((item.mnemonic, item.rd, item.rs1, item.rs2),
                             (mnemonic, 8, 9, None))
            self.assertEqual(to_assembly(item), f"{mnemonic} s0, -8(s1)")
        for mnemonic, funct3 in (("sb", 0), ("sh", 1), ("sw", 2)):
            item = decode(0, encode_s(funct3))
            self.assertEqual((item.mnemonic, item.rd, item.rs1, item.rs2, item.immediate),
                             (mnemonic, None, 9, 10, -8))
            self.assertEqual(to_assembly(item), f"{mnemonic} a0, -8(s1)")
        for mnemonic, funct3 in (("beq", 0), ("bne", 1), ("blt", 4),
                                 ("bge", 5), ("bltu", 6), ("bgeu", 7)):
            item = decode(0x1000, encode_b(funct3))
            self.assertEqual((item.mnemonic, item.rd, item.immediate, item.target),
                             (mnemonic, None, -8, 0xFF8))

    def test_control_upper_fence_and_system(self):
        words = ((0x12345437, "lui", "U"), (0x12345417, "auipc", "U"),
                 (0x008000EF, "jal", "J"), (0x00008067, "jalr", "I"),
                 (0x0FF0000F, "fence", "I"), (0x8330000F, "fence.tso", "I"),
                 (0x00000073, "ecall", "I"), (0x00100073, "ebreak", "I"))
        for word, mnemonic, format_name in words:
            with self.subTest(mnemonic=mnemonic):
                item = decode(0x1000, word)
                self.assertEqual((item.mnemonic, item.format, item.valid),
                                 (mnemonic, format_name, True))
        for word in (0x0FF0000F, 0x8330000F, 0x00000073, 0x00100073):
            item = decode(0, word)
            for field in ("rd", "rs1", "rs2", "funct3", "funct7", "immediate"):
                self.assertIsNone(getattr(item, field))
        self.assertEqual(to_assembly(decode(0, 0x0FF0000F)), "fence iorw, iorw")
        self.assertEqual(to_assembly(decode(0, 0x8330000F)), "fence.tso")
        self.assertEqual(to_assembly(decode(0, 0x00000073)), "ecall")
        self.assertEqual(to_assembly(decode(0, 0x00100073)), "ebreak")

    def test_other_extensions_and_reserved_encodings_are_invalid(self):
        for word in (0x02000033, 0x0000100F, 0x001010F3, 0x0000001B,
                     encode_i(0x13, 1, 0x401), encode_i(0x13, 5, 0x201)):
            with self.subTest(word=hex(word)):
                self.assertFalse(decode(0, word).valid)

import unittest

from src.models.instruction import Instruction
from src.utils.bits import get_bits, sign_extend
from src.utils.registers import register_name


class FoundationTests(unittest.TestCase):
    def test_instruction_starts_with_only_machine_identity(self):
        instruction = Instruction(pc=0x1000, word=0xFE628CE3)
        self.assertEqual((instruction.pc, instruction.word), (0x1000, 0xFE628CE3))
        for field in ("rd", "rs1", "rs2", "funct3", "funct7", "immediate"):
            self.assertIsNone(getattr(instruction, field))

    def test_bit_range_is_inclusive(self):
        self.assertEqual(get_bits(0xFE628CE3, 0, 6), 0x63)
        self.assertEqual(get_bits(0xFE628CE3, 7, 11), 25)
        with self.assertRaises(ValueError):
            get_bits(0, 7, 6)

    def test_sign_extension(self):
        self.assertEqual(sign_extend(0x7FF, 12), 2047)
        self.assertEqual(sign_extend(0xFF8, 12), -8)
        self.assertEqual(sign_extend(0x1FFFF8, 21), -8)

    def test_abi_registers(self):
        self.assertEqual([register_name(i) for i in (0, 1, 2, 5, 6, 8, 31)],
                         ["zero", "ra", "sp", "t0", "t1", "s0", "t6"])
        with self.assertRaises(ValueError):
            register_name(32)

import unittest

from src.decoder.instruction_table import DEFINITIONS, find_definition


class InstructionTableTests(unittest.TestCase):
    def test_rv32i_repertoire_and_six_formats(self):
        self.assertEqual(
            {item.mnemonic for item in DEFINITIONS} - {"fence.tso"},
            {"lui", "auipc", "jal", "jalr", "beq", "bne", "blt", "bge",
             "bltu", "bgeu", "lb", "lh", "lw", "lbu", "lhu", "sb", "sh",
             "sw", "addi", "slti", "sltiu", "xori", "ori", "andi", "slli",
             "srli", "srai", "add", "sub", "sll", "slt", "sltu", "xor",
             "srl", "sra", "or", "and", "fence", "ecall", "ebreak"},
        )
        self.assertEqual(len(DEFINITIONS), 41)
        self.assertEqual({item.format for item in DEFINITIONS}, set("RISBUJ"))

    def test_funct3_and_funct7_are_checked(self):
        self.assertEqual(find_definition(0x00C58633).mnemonic, "add")
        self.assertEqual(find_definition(0x40C58633).mnemonic, "sub")
        self.assertEqual(find_definition(0x0020D093).mnemonic, "srli")
        self.assertEqual(find_definition(0x4020D093).mnemonic, "srai")
        self.assertIsNone(find_definition(0x2020D093))
        self.assertIsNone(find_definition(0x02000033))

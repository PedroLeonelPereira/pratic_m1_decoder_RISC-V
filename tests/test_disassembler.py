import unittest

from src.assembler.disassembler import to_assembly, to_pseudo_assembly
from src.decoder.decoder import decode


class DisassemblerTests(unittest.TestCase):
    @staticmethod
    def i_word(opcode, funct3, rd, rs1, immediate):
        return ((immediate & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

    @staticmethod
    def r_word(funct3, funct7, rd, rs1, rs2):
        return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | 0x33

    @staticmethod
    def b_word(funct3, rs1, rs2):
        immediate = 8
        return (((immediate >> 12) & 1) << 31) | (((immediate >> 5) & 0x3F) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (((immediate >> 1) & 0xF) << 8) | (((immediate >> 11) & 1) << 7) | 0x63

    def test_assignment_examples_and_memory_syntax(self):
        examples = {
            0x00500413: "addi s0, zero, 5",
            0x00C58633: "add a2, a1, a2",
            0x0064A423: "sw t1, 8(s1)",
            0x0000A083: "lw ra, 0(ra)",
        }
        for word, expected in examples.items():
            with self.subTest(word=hex(word)):
                self.assertEqual(to_assembly(decode(0, word)), expected)

    def test_pseudo_output_preserves_machine_mnemonic(self):
        nop = decode(0, 0x00000013)
        ret = decode(4, 0x00008067)
        self.assertEqual((nop["mnemonic"], to_assembly(nop)), ("addi", "nop"))
        self.assertEqual((ret["mnemonic"], to_assembly(ret)), ("jalr", "ret"))
        self.assertEqual(to_assembly(decode(0, 0x00100013)), "addi zero, zero, 1")

    def test_branch_and_jump_show_absolute_target(self):
        self.assertEqual(to_assembly(decode(0x1000, 0xFE628CE3)),
                         "beq t0, t1, 0x00000FF8")
        self.assertEqual(to_assembly(decode(0x1000, 0x008000EF)),
                         "jal ra, 0x00001008")
        self.assertEqual(to_assembly(decode(0x1000, 0xFF9FF0EF)),
                         "jal ra, 0x00000FF8")

    def test_u_and_invalid_output(self):
        self.assertEqual(to_assembly(decode(0, 0x12345437)), "lui s0, 0x12345")
        self.assertEqual(to_assembly(decode(0, 0xFFFFFFFF)), "INVALID INSTRUCTION")

    def test_common_single_word_arithmetic_aliases(self):
        cases = (
            (self.i_word(0x13, 0, 8, 0, 5), "li s0, 5"),
            (self.i_word(0x13, 0, 8, 9, 0), "mv s0, s1"),
            (self.i_word(0x13, 4, 8, 9, -1), "not s0, s1"),
            (self.i_word(0x13, 7, 8, 9, 255), "zext.b s0, s1"),
            (self.r_word(0, 0x20, 8, 0, 9), "neg s0, s1"),
            (self.i_word(0x13, 3, 8, 9, 1), "seqz s0, s1"),
            (self.r_word(3, 0, 8, 0, 9), "snez s0, s1"),
            (self.r_word(2, 0, 8, 9, 0), "sltz s0, s1"),
            (self.r_word(2, 0, 8, 0, 9), "sgtz s0, s1"),
        )
        for word, pseudo in cases:
            with self.subTest(pseudo=pseudo):
                item = decode(0, word)
                self.assertEqual(to_pseudo_assembly(item), pseudo)
                self.assertNotEqual(item["mnemonic"], pseudo.split()[0])
        self.assertEqual(to_assembly(decode(0, 0x00500413)), "addi s0, zero, 5")
        self.assertIsNone(to_pseudo_assembly(decode(0, 0x00100013)))

    def test_common_branch_and_jump_aliases_use_absolute_target(self):
        cases = (
            (self.b_word(0, 9, 0), "beqz s1, 0x00001008"),
            (self.b_word(1, 9, 0), "bnez s1, 0x00001008"),
            (self.b_word(4, 9, 0), "bltz s1, 0x00001008"),
            (self.b_word(5, 9, 0), "bgez s1, 0x00001008"),
            (self.b_word(4, 0, 9), "bgtz s1, 0x00001008"),
            (self.b_word(5, 0, 9), "blez s1, 0x00001008"),
            (self.b_word(4, 9, 10), "bgt a0, s1, 0x00001008"),
            (self.b_word(5, 9, 10), "ble a0, s1, 0x00001008"),
            (self.b_word(6, 9, 10), "bgtu a0, s1, 0x00001008"),
            (self.b_word(7, 9, 10), "bleu a0, s1, 0x00001008"),
            (0x0080006F, "j 0x00001008"),
            (0x008000EF, "jal 0x00001008"),
            (self.i_word(0x67, 0, 0, 9, 0), "jr s1"),
            (self.i_word(0x67, 0, 1, 9, 0), "jalr s1"),
            (0x00008067, "ret"),
        )
        for word, pseudo in cases:
            with self.subTest(pseudo=pseudo):
                self.assertEqual(to_pseudo_assembly(decode(0x1000, word)), pseudo)

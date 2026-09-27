import tempfile
import unittest
from pathlib import Path

from src.parser.input_parser import parse_file


class ParserTests(unittest.TestCase):
    def parse_text(self, text: str, base_address: int = 0):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rom.txt"
            path.write_text(text, encoding="utf-8")
            return parse_file(path, base_address)

    def test_hex_with_prefix_comments_blank_lines_and_pc(self):
        self.assertEqual(
            self.parse_text("# header\n\n0x00500413 # addi\n0064A423 ; sw\n", 0x1000),
            [(0x1000, 0x00500413), (0x1004, 0x0064A423)],
        )

    def test_binary_is_detected_from_width(self):
        self.assertEqual(
            self.parse_text("00000000010100000000010000010011\n// comment\n"
                            "11111110011000101000110011100011\n"),
            [(0, 0x00500413), (4, 0xFE628CE3)],
        )

    def test_invalid_width_and_digits_report_line(self):
        for text, message in (("123\n", "32 bits"),
                              ("00500G13\n", "hexadecimal"),
                              ("0" * 31 + "2\n", "binary")):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, message):
                self.parse_text(text)

    def test_mixed_formats_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Line 2: mixed"):
            self.parse_text("00500413\n" + "0" * 32 + "\n")

    def test_missing_file_is_explicit(self):
        with self.assertRaises(FileNotFoundError):
            parse_file("/nonexistent/rom.txt")

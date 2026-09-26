import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from main import main


class CliTests(unittest.TestCase):
    def test_end_to_end_keeps_processing_after_invalid_word(self):
        with tempfile.TemporaryDirectory() as directory:
            rom = Path(directory) / "rom.txt"
            cpi = Path(directory) / "cpi.json"
            rom.write_text("00500413\nFFFFFFFF\nFE628CE3\n008000EF\n",
                           encoding="utf-8")
            cpi.write_text(json.dumps({
                "class_cpi": {"arithmetic": 1, "control": 3},
                "mnemonic_class": {"addi": "arithmetic", "beq": "control"},
            }), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(rom), "--base-address", "0x1000",
                                       "--cpi-table", str(cpi)]), 0)
            report = output.getvalue()
            self.assertIn("PC: 0x00001004\nPalavra: 0xFFFFFFFF\nINSTRUÇÃO INVÁLIDA", report)
            self.assertIn("PC: 0x00001008", report)
            self.assertIn("Destino absoluto: 0x00001000", report)
            self.assertIn("PC: 0x0000100C", report)
            self.assertIn("Destino absoluto: 0x00001014", report)
            self.assertIn("Palavras processadas: 4", report)
            self.assertIn("Instruções válidas: 3", report)
            self.assertIn("Palavras inválidas: 1", report)
            self.assertIn("Pseudo: li s0, 5", report)
            self.assertIn("Instruções válidas com classe de CPI: 2", report)
            self.assertIn("CPI médio (somente válidas com classe de CPI): 2.000", report)
            self.assertIn("I: 1 (33.33%)", report)

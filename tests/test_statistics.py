import json
import tempfile
import unittest
from pathlib import Path

from src.decoder.decoder import decode
from src.statistics.statistics import (
    CpiTable, calculate_average_cpi, calculate_percentages,
    count_cpi_eligible, count_formats, count_words, load_cpi_table,
)


class StatisticsTests(unittest.TestCase):
    def test_invalid_words_are_separate_and_not_in_format_denominator(self):
        items = [decode(0, 0x00500413), decode(4, 0xFFFFFFFF),
                 decode(8, 0x00C58633), decode(12, 0x0064A423)]
        self.assertEqual((count_words(items).processed, count_words(items).valid,
                          count_words(items).invalid), (4, 3, 1))
        self.assertEqual(count_formats(items),
                         {"R": 1, "I": 1, "S": 1, "B": 0, "U": 0, "J": 0})
        self.assertAlmostEqual(calculate_percentages(items)["R"], 100 / 3)
        self.assertEqual(sum(calculate_percentages(items).values()), 100.0)

    def test_cpi_excludes_invalid_and_valid_without_configured_class(self):
        items = [decode(0, 0x00500413), decode(4, 0x00C58633),
                 decode(8, 0x0064A423), decode(12, 0xFFFFFFFF)]
        table = CpiTable(
            class_cpi={"arithmetic": 1.0, "memory": 3.0},
            mnemonic_class={"addi": "arithmetic", "sw": "memory",
                            "invalid": "memory"},
        )
        self.assertEqual(count_cpi_eligible(items, table), 2)
        self.assertEqual(calculate_average_cpi(items, table), 2.0)

    def test_no_eligible_instructions_has_no_average(self):
        items = [decode(0, 0xFFFFFFFF), decode(4, 0x00500413)]
        table = CpiTable({"arithmetic": 1.0}, {})
        self.assertEqual(count_cpi_eligible(items, table), 0)
        self.assertIsNone(calculate_average_cpi(items, table))
        self.assertEqual(sum(calculate_percentages([items[0]]).values()), 0.0)

    def test_loads_generic_class_mapping_and_rejects_invalid_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cpi.json"
            path.write_text(json.dumps({
                "class_cpi": {"example_class": 2.5},
                "mnemonic_class": {"addi": "example_class"},
            }), encoding="utf-8")
            self.assertEqual(load_cpi_table(path).class_cpi["example_class"], 2.5)
            path.write_text(json.dumps({
                "class_cpi": {"example_class": -1},
                "mnemonic_class": {"addi": "example_class"},
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid CPI"):
                load_cpi_table(path)

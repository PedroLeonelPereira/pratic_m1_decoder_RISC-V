"""Format distribution and CPI of decoded, valid instructions."""

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from src.models.instruction import Instruction

FORMATS = ("R", "I", "S", "B", "U", "J")


@dataclass(frozen=True)
class WordCounts:
    processed: int
    valid: int
    invalid: int


@dataclass(frozen=True)
class CpiTable:
    """Caller-supplied CPI classes, independent of instruction formats."""

    class_cpi: Mapping[str, float]
    mnemonic_class: Mapping[str, str]


def load_cpi_table(path: str | Path) -> CpiTable:
    """Read a JSON CPI table; no classes or values are built into the program."""
    with Path(path).open(encoding="utf-8") as source:
        data = json.load(source)
    if not isinstance(data, dict):
        raise ValueError("CPI configuration must be a JSON object")
    class_cpi = data.get("class_cpi")
    mnemonic_class = data.get("mnemonic_class")
    if not isinstance(class_cpi, dict) or not isinstance(mnemonic_class, dict):
        raise ValueError("CPI configuration needs class_cpi and mnemonic_class objects")
    for name, cpi in class_cpi.items():
        if (not isinstance(name, str) or not name
                or isinstance(cpi, bool) or not isinstance(cpi, (int, float))
                or not math.isfinite(cpi) or cpi <= 0):
            raise ValueError(f"Invalid CPI for class {name!r}")
    for mnemonic, class_name in mnemonic_class.items():
        if (not isinstance(mnemonic, str) or not mnemonic
                or not isinstance(class_name, str) or class_name not in class_cpi):
            raise ValueError(f"Invalid CPI class mapping for {mnemonic!r}")
    return CpiTable(class_cpi, mnemonic_class)


def count_words(instructions: Sequence[Instruction]) -> WordCounts:
    valid = sum(instruction.valid for instruction in instructions)
    return WordCounts(len(instructions), valid, len(instructions) - valid)


def count_formats(instructions: Sequence[Instruction]) -> dict[str, int]:
    """Count valid instructions; invalid words have no instruction format."""
    counts = dict.fromkeys(FORMATS, 0)
    for instruction in instructions:
        if instruction.valid:
            if instruction.format not in counts:
                raise ValueError("Valid instruction has no supported format")
            counts[instruction.format] += 1
    return counts


def calculate_percentages(instructions: Sequence[Instruction]) -> dict[str, float]:
    """Use only valid instructions as the percentage denominator."""
    counts = count_formats(instructions)
    total = sum(counts.values())
    return {format_name: 100 * count / total if total else 0.0
            for format_name, count in counts.items()}


def _cpi_class_counts(
    instructions: Sequence[Instruction], cpi_table: CpiTable
) -> Counter[str]:
    return Counter(
        cpi_table.mnemonic_class[instruction.mnemonic]
        for instruction in instructions
        if instruction.valid and instruction.mnemonic in cpi_table.mnemonic_class
    )


def count_cpi_eligible(instructions: Sequence[Instruction], cpi_table: CpiTable) -> int:
    """Count valid instructions with a configured CPI class."""
    return sum(_cpi_class_counts(instructions, cpi_table).values())


def calculate_average_cpi(
    instructions: Sequence[Instruction], cpi_table: CpiTable
) -> float | None:
    """Weighted CPI over valid instructions with a configured class only."""
    class_counts = _cpi_class_counts(instructions, cpi_table)
    total = sum(class_counts.values())
    if total == 0:
        return None
    return sum(quantity * cpi_table.class_cpi[class_name]
               for class_name, quantity in class_counts.items()) / total

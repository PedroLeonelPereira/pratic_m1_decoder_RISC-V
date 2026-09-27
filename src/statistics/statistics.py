"""Count instruction formats and calculate the weighted average CPI."""

import json
import math


FORMATS = ("R", "I", "S", "B", "U", "J")


def load_cpi_table(path):
    """Read CPI classes and mnemonic mappings from a JSON file."""
    with open(path, encoding="utf-8") as source:
        data = json.load(source)

    if not isinstance(data, dict):
        raise ValueError("CPI configuration must be a JSON object")

    class_cpi = data.get("class_cpi")
    mnemonic_class = data.get("mnemonic_class")
    if not isinstance(class_cpi, dict) or not isinstance(mnemonic_class, dict):
        raise ValueError("CPI configuration needs class_cpi and mnemonic_class objects")

    for name in class_cpi:
        cpi = class_cpi[name]
        if (not isinstance(name, str) or not name
                or isinstance(cpi, bool)
                or not isinstance(cpi, (int, float))
                or not math.isfinite(cpi) or cpi <= 0):
            raise ValueError(f"Invalid CPI for class {name!r}")

    for mnemonic in mnemonic_class:
        class_name = mnemonic_class[mnemonic]
        if (not isinstance(mnemonic, str) or not mnemonic
                or not isinstance(class_name, str)
                or class_name not in class_cpi):
            raise ValueError(f"Invalid CPI class mapping for {mnemonic!r}")

    return {
        "class_cpi": class_cpi,
        "mnemonic_class": mnemonic_class,
    }


def count_words(instructions):
    """Count processed, valid, and invalid words."""
    valid = 0
    for instruction in instructions:
        if instruction["valid"]:
            valid += 1

    return {
        "processed": len(instructions),
        "valid": valid,
        "invalid": len(instructions) - valid,
    }


def count_formats(instructions):
    """Count valid instructions in each supported format."""
    counts = {"R": 0, "I": 0, "S": 0, "B": 0, "U": 0, "J": 0}

    for instruction in instructions:
        if instruction["valid"]:
            format_name = instruction["format"]
            if format_name not in counts:
                raise ValueError("Valid instruction has no supported format")
            counts[format_name] += 1

    return counts


def calculate_percentages(instructions):
    """Calculate format percentages using valid words as the total."""
    counts = count_formats(instructions)
    total = sum(counts.values())
    percentages = {}

    for format_name in FORMATS:
        if total == 0:
            percentages[format_name] = 0.0
        else:
            percentages[format_name] = 100 * counts[format_name] / total

    return percentages


def _cpi_class_counts(instructions, cpi_table):
    counts = {}
    mappings = cpi_table["mnemonic_class"]

    for instruction in instructions:
        mnemonic = instruction["mnemonic"]
        if instruction["valid"] and mnemonic in mappings:
            class_name = mappings[mnemonic]
            if class_name not in counts:
                counts[class_name] = 0
            counts[class_name] += 1

    return counts


def count_cpi_eligible(instructions, cpi_table):
    """Count valid instructions with a configured CPI class."""
    counts = _cpi_class_counts(instructions, cpi_table)
    total = 0
    for quantity in counts.values():
        total += quantity
    return total


def calculate_average_cpi(instructions, cpi_table):
    """Calculate the weighted CPI for configured valid instructions."""
    counts = _cpi_class_counts(instructions, cpi_table)
    total = 0
    weighted_total = 0

    for class_name in counts:
        quantity = counts[class_name]
        total += quantity
        weighted_total += quantity * cpi_table["class_cpi"][class_name]

    if total == 0:
        return None
    return weighted_total / total

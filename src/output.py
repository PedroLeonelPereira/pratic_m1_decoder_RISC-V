"""Build the human-readable instruction list and statistics report."""

from src.statistics.statistics import (
    calculate_average_cpi, calculate_percentages, count_cpi_eligible,
    count_formats, count_words,
)
from src.utils.registers import register_name


def _address(value):
    if value >= 0:
        return f"0x{value:08X}"
    return f"-0x{-value:X}"


def format_instruction(instruction):
    lines = [
        f"PC: {_address(instruction['pc'])}",
        f"Palavra: 0x{instruction['word']:08X}",
    ]

    if not instruction["valid"]:
        lines.append(f"INSTRUÇÃO INVÁLIDA: {instruction['error']}")
        return "\n".join(lines)

    lines.append(f"Formato: {instruction['format']}")
    lines.append(f"Mnemônico: {instruction['mnemonic']}")
    lines.append(f"opcode: {instruction['opcode']}")

    fields = ("rd", "rs1", "rs2")
    for field in fields:
        value = instruction[field]
        if value is not None:
            lines.append(f"{field}: x{value} ({register_name(value)})")

    fields = ("funct3", "funct7")
    for field in fields:
        value = instruction[field]
        if value is not None:
            lines.append(f"{field}: {value}")

    if instruction["immediate"] is not None:
        lines.append(f"Imediato: {instruction['immediate']}")

    if instruction["fence_mode"] is not None:
        lines.append(f"fence_mode: {instruction['fence_mode']}")
        lines.append(f"fence_predecessor: {instruction['fence_predecessor']}")
        lines.append(f"fence_successor: {instruction['fence_successor']}")

    lines.append(f"Assembly: {instruction['assembly']}")
    pseudo = instruction["pseudo"]
    if pseudo is not None and pseudo != instruction["assembly"]:
        lines.append(f"Pseudo: {pseudo}")
    if instruction["target"] is not None:
        lines.append(f"Destino absoluto: {_address(instruction['target'])}")

    return "\n".join(lines)


def format_statistics(instructions, cpi_table):
    totals = count_words(instructions)
    counts = count_formats(instructions)
    percentages = calculate_percentages(instructions)
    eligible = count_cpi_eligible(instructions, cpi_table)
    cpi = calculate_average_cpi(instructions, cpi_table)

    lines = [
        "Estatísticas:",
        f"Palavras processadas: {totals['processed']}",
        f"Instruções válidas: {totals['valid']}",
        f"Palavras inválidas: {totals['invalid']}",
        "Percentuais por formato (denominador: instruções válidas):",
    ]

    for format_name in counts:
        line = (f"  {format_name}: {counts[format_name]} "
                f"({percentages[format_name]:.2f}%)")
        lines.append(line)

    lines.append(f"Instruções válidas com classe de CPI: {eligible}")
    if cpi is None:
        cpi_text = "indisponível"
    else:
        cpi_text = f"{cpi:.3f}"
    lines.append("CPI médio (somente válidas com classe de CPI): " + cpi_text)

    return "\n".join(lines)

"""Human-readable listing and statistical report."""

from collections.abc import Sequence

from src.models.instruction import Instruction
from src.statistics.statistics import (
    CpiTable, calculate_average_cpi, calculate_percentages,
    count_cpi_eligible, count_formats, count_words,
)
from src.utils.registers import register_name


def _address(value: int) -> str:
    return f"0x{value:08X}" if value >= 0 else f"-0x{-value:X}"


def format_instruction(instruction: Instruction) -> str:
    lines = [f"PC: {_address(instruction.pc)}", f"Palavra: 0x{instruction.word:08X}"]
    if not instruction.valid:
        lines.append(f"INSTRUÇÃO INVÁLIDA: {instruction.error}")
        return "\n".join(lines)
    lines.extend((f"Formato: {instruction.format}",
                  f"Mnemônico: {instruction.mnemonic}",
                  f"opcode: {instruction.opcode}"))
    for field in ("rd", "rs1", "rs2"):
        value = getattr(instruction, field)
        if value is not None:
            lines.append(f"{field}: x{value} ({register_name(value)})")
    for field in ("funct3", "funct7"):
        value = getattr(instruction, field)
        if value is not None:
            lines.append(f"{field}: {value}")
    if instruction.immediate is not None:
        lines.append(f"Imediato: {instruction.immediate}")
    if instruction.fence_mode is not None:
        lines.append(f"fence_mode: {instruction.fence_mode}")
        lines.append(f"fence_predecessor: {instruction.fence_predecessor}")
        lines.append(f"fence_successor: {instruction.fence_successor}")
    lines.append(f"Assembly: {instruction.assembly}")
    if instruction.pseudo is not None and instruction.pseudo != instruction.assembly:
        lines.append(f"Pseudo: {instruction.pseudo}")
    if instruction.target is not None:
        lines.append(f"Destino absoluto: {_address(instruction.target)}")
    return "\n".join(lines)


def format_statistics(instructions: Sequence[Instruction], cpi_table: CpiTable) -> str:
    totals = count_words(instructions)
    counts = count_formats(instructions)
    percentages = calculate_percentages(instructions)
    eligible = count_cpi_eligible(instructions, cpi_table)
    cpi = calculate_average_cpi(instructions, cpi_table)
    lines = ["Estatísticas:",
             f"Palavras processadas: {totals.processed}",
             f"Instruções válidas: {totals.valid}",
             f"Palavras inválidas: {totals.invalid}",
             "Percentuais por formato (denominador: instruções válidas):"]
    lines.extend(f"  {format_name}: {counts[format_name]} ({percentages[format_name]:.2f}%)"
                 for format_name in counts)
    lines.append(f"Instruções válidas com classe de CPI: {eligible}")
    lines.append("CPI médio (somente válidas com classe de CPI): "
                 + (f"{cpi:.3f}" if cpi is not None else "indisponível"))
    return "\n".join(lines)

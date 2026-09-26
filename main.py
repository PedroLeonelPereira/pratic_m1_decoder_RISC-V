"""Command-line entry point for Etapa 1."""

import argparse
import json
from collections.abc import Sequence

from src.assembler.disassembler import to_assembly, to_pseudo_assembly
from src.decoder.decoder import decode
from src.output import format_instruction, format_statistics
from src.parser.input_parser import InputFormatError, parse_file
from src.statistics.statistics import load_cpi_table


def _address_argument(value: str) -> int:
    try:
        address = int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Endereço-base inválido") from error
    if address < 0:
        raise argparse.ArgumentTypeError("Endereço-base deve ser não negativo")
    return address


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decodificador RISC-V — Etapa 1")
    parser.add_argument("rom", help="arquivo ROM em hexadecimal ou binário")
    parser.add_argument("--base-address", type=_address_argument, default=0,
                        help="PC inicial (decimal ou 0x...)")
    parser.add_argument("--cpi-table", required=True,
                        help="arquivo JSON com CPI por classe e mapeamento de mnemônicos")
    args = parser.parse_args(argv)
    try:
        words = parse_file(args.rom, args.base_address)
        cpi_table = load_cpi_table(args.cpi_table)
    except (OSError, InputFormatError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    instructions = [decode(pc, word) for pc, word in words]
    for instruction in instructions:
        instruction.assembly = to_assembly(instruction)
        instruction.pseudo = to_pseudo_assembly(instruction)
        print(format_instruction(instruction))
        print()
    print(format_statistics(instructions, cpi_table))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

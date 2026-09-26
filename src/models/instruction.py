"""Structured result of decoding one 32-bit machine word."""

from dataclasses import dataclass


@dataclass
class Instruction:
    pc: int
    word: int
    format: str | None = None
    mnemonic: str | None = None
    opcode: int | None = None
    rd: int | None = None
    rs1: int | None = None
    rs2: int | None = None
    funct3: int | None = None
    funct7: int | None = None
    immediate: int | None = None
    assembly: str | None = None
    pseudo: str | None = None
    target: int | None = None
    fence_mode: int | None = None
    fence_predecessor: int | None = None
    fence_successor: int | None = None
    valid: bool = True
    error: str | None = None

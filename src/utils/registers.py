"""Integer register names from the RISC-V ABI."""

ABI_REGISTERS = (
    "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
    "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
    "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
    "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6",
)


def register_name(register: int) -> str:
    """Return the ABI name of register x0 through x31."""
    if not 0 <= register < len(ABI_REGISTERS):
        raise ValueError(f"Invalid register: {register}")
    return ABI_REGISTERS[register]

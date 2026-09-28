# identifica formatos e mnemonicos a partir dos campos da instrucao

def identificar_tipo(opcode):
    if opcode == "0110011":
        return "R"
    if opcode == "0010011":
        return "I"
    if opcode == "0000011":
        return "load"
    if opcode == "1100111":
        return "jalr"
    if opcode == "0100011":
        return "S"
    if opcode == "1100011":
        return "B"
    if opcode == "0110111":
        return "lui"
    if opcode == "0010111":
        return "auipc"
    if opcode == "1101111":
        return "J"
    return "invalida"


def resolver_mnemonico_r(f3, f7):
    if f3 == "000":
        if f7 == "0000000":
            return "add"
        else:
            if f7 == "0100000":
                return "sub"
            else:
                return "invalida"
    if f3 == "001":
        if f7 == "0000000":
            return "sll"
        else:
            return "invalida"
    if f3 == "010":
        if f7 == "0000000":
            return "slt"
        else:
            return "invalida"
    if f3 == "011":
        if f7 == "0000000":
            return "sltu"
        else:
            return "invalida"
    if f3 == "100":
        if f7 == "0000000":
            return "xor"
        else:
            return "invalida"
    if f3 == "101":
        if f7 == "0000000":
            return "srl"
        else:
            if f7 == "0100000":
                return "sra"
            else:
                return "invalida"
    if f3 == "110":
        if f7 == "0000000":
            return "or"
        else:
            return "invalida"
    if f3 == "111":
        if f7 == "0000000":
            return "and"
        else:
            return "invalida"
    return "invalida"


def resolver_mnemonico_i(f3, f7):
    if f3 == "000":
        return "addi"
    if f3 == "010":
        return "slti"
    if f3 == "011":
        return "sltiu"
    if f3 == "100":
        return "xori"
    if f3 == "110":
        return "ori"
    if f3 == "111":
        return "andi"
    if f3 == "001":
        if f7 == "0000000":
            return "slli"
        else:
            return "invalida"
    if f3 == "101":
        if f7 == "0000000":
            return "srli"
        else:
            if f7 == "0100000":
                return "srai"
            else:
                return "invalida"
    return "invalida"


def resolver_mnemonico_load(f3):
    if f3 == "000":
        return "lb"
    if f3 == "001":
        return "lh"
    if f3 == "010":
        return "lw"
    if f3 == "100":
        return "lbu"
    if f3 == "101":
        return "lhu"
    return "invalida"


def resolver_mnemonico_s(f3):
    if f3 == "000":
        return "sb"
    if f3 == "001":
        return "sh"
    if f3 == "010":
        return "sw"
    return "invalida"


def resolver_mnemonico_b(f3):
    if f3 == "000":
        return "beq"
    if f3 == "001":
        return "bne"
    if f3 == "100":
        return "blt"
    if f3 == "101":
        return "bge"
    if f3 == "110":
        return "bltu"
    if f3 == "111":
        return "bgeu"
    return "invalida"

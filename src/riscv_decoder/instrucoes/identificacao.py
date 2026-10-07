# identifica formatos e mnemonicos a partir dos campos da instrucao
# cada tabela abaixo e um map de chave para valor
# a chave e o pedaco de bits, o valor e o nome devolvido
# quando a chave nao esta na tabela, a instrucao e invalida

tabela_tipo = {
    "0110011": "R",
    "0010011": "I",
    "0000011": "load",
    "1100111": "jalr",
    "0100011": "S",
    "1100011": "B",
    "0110111": "lui",
    "0010111": "auipc",
    "1101111": "J",
}

tabela_r = {
    "0000000000": "add",
    "0000100000": "sub",
    "0010000000": "sll",
    "0100000000": "slt",
    "0110000000": "sltu",
    "1000000000": "xor",
    "1010000000": "srl",
    "1010100000": "sra",
    "1100000000": "or",
    "1110000000": "and",
}

tabela_i = {
    "000": "addi",
    "010": "slti",
    "011": "sltiu",
    "100": "xori",
    "110": "ori",
    "111": "andi",
}

tabela_i_deslocamento = {
    "0010000000": "slli",
    "1010000000": "srli",
    "1010100000": "srai",
}

tabela_load = {
    "000": "lb",
    "001": "lh",
    "010": "lw",
    "100": "lbu",
    "101": "lhu",
}

tabela_s = {
    "000": "sb",
    "001": "sh",
    "010": "sw",
}

tabela_b = {
    "000": "beq",
    "001": "bne",
    "100": "blt",
    "101": "bge",
    "110": "bltu",
    "111": "bgeu",
}


def identify_type(opcode):
    if opcode in tabela_tipo:
        return tabela_tipo[opcode]
    return "invalida"


def lookup_r_name(f3, f7):
    chave = f3 + f7
    if chave in tabela_r:
        return tabela_r[chave]
    return "invalida"


def lookup_i_name(f3, f7):
    if f3 in tabela_i:
        return tabela_i[f3]
    chave = f3 + f7
    if chave in tabela_i_deslocamento:
        return tabela_i_deslocamento[chave]
    return "invalida"


def lookup_load_name(f3):
    if f3 in tabela_load:
        return tabela_load[f3]
    return "invalida"


def lookup_s_name(f3):
    if f3 in tabela_s:
        return tabela_s[f3]
    return "invalida"


def lookup_b_name(f3):
    if f3 in tabela_b:
        return tabela_b[f3]
    return "invalida"

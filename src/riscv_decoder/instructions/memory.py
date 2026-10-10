# decodificacao das instrucoes de carga, armazenamento e salto por registrador
from input.convert import binary_to_signed
from pseudo import identify_pseudo
from instructions.common import register_to_abi
from instructions.common import criar_registro
from instructions.identify import lookup_load_name
from instructions.identify import lookup_s_name


def decode_load(bits):
    pedaco_imm = bits[0:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    nome = lookup_load_name(f3)
    if nome == "invalida":
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    rd = register_to_abi(rd_pedaco)
    rs1 = register_to_abi(rs1_pedaco)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rd + "," + imm + "(" + rs1 + ")"
    return criar_registro("load", nome, rd, rs1, "", imm, f3, "", montada, "")


def decode_jalr(bits):
    pedaco_imm = bits[0:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    if f3 != "000":
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    rd = register_to_abi(rd_pedaco)
    rs1 = register_to_abi(rs1_pedaco)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = "jalr" + " " + rd + "," + imm + "(" + rs1 + ")"
    texto_pseudo = identify_pseudo("jalr", rd, rs1, imm)
    return criar_registro("jalr", "jalr", rd, rs1, "", imm, f3, "", montada, texto_pseudo)


def decode_s_type(bits):
    pedaco_alto = bits[0:7]
    rs2_pedaco = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    pedaco_baixo = bits[20:25]
    nome = lookup_s_name(f3)
    if nome == "invalida":
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    pedaco_imm = pedaco_alto + pedaco_baixo
    rs1 = register_to_abi(rs1_pedaco)
    rs2 = register_to_abi(rs2_pedaco)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rs2 + "," + imm + "(" + rs1 + ")"
    return criar_registro("S", nome, "", rs1, rs2, imm, f3, "", montada, "")

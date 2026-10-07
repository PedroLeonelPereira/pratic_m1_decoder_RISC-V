# decodificacao das instrucoes de carga, armazenamento e salto por registrador
from entrada.conversoes import binary_to_signed
from pseudo import identify_pseudo
from instrucoes.comum import register_to_abi
from instrucoes.comum import print_result
from instrucoes.identificacao import lookup_load_name
from instrucoes.identificacao import lookup_s_name


def decode_load(bits):
    pedaco_imm = bits[0:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    nome = lookup_load_name(f3)
    if nome == "invalida":
        print_result("invalida", "", "", "", "", "", "", "", "")
        return
    rd = register_to_abi(rd_pedaco)
    rs1 = register_to_abi(rs1_pedaco)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rd + "," + imm + "(" + rs1 + ")"
    print_result("load", nome, rd, rs1, "", imm, f3, "", montada)


def decode_jalr(bits):
    pedaco_imm = bits[0:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    if f3 != "000":
        print_result("invalida", "", "", "", "", "", "", "", "")
        return
    rd = register_to_abi(rd_pedaco)
    rs1 = register_to_abi(rs1_pedaco)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = "jalr" + " " + rd + "," + imm + "(" + rs1 + ")"
    print_result("jalr", "jalr", rd, rs1, "", imm, f3, "", montada)
    texto_pseudo = identify_pseudo("jalr", rd, rs1, imm)
    if texto_pseudo != "":
        print("pseudo: " + texto_pseudo)


def decode_s_type(bits):
    pedaco_alto = bits[0:7]
    rs2_pedaco = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    pedaco_baixo = bits[20:25]
    nome = lookup_s_name(f3)
    if nome == "invalida":
        print_result("invalida", "", "", "", "", "", "", "", "")
        return
    pedaco_imm = pedaco_alto + pedaco_baixo
    rs1 = register_to_abi(rs1_pedaco)
    rs2 = register_to_abi(rs2_pedaco)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rs2 + "," + imm + "(" + rs1 + ")"
    print_result("S", nome, "", rs1, rs2, imm, f3, "", montada)

# decodificacao das instrucoes de desvio condicional e jal
from entrada.conversoes import binary_to_signed
from pseudo import identify_pseudo
from instrucoes.comum import register_to_abi
from instrucoes.comum import print_result
from instrucoes.identificacao import lookup_b_name


def decode_b_type(bits):
    pedaco_12 = bits[0:1]
    pedaco_10_5 = bits[1:7]
    rs2_pedaco = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    pedaco_4_1 = bits[20:24]
    pedaco_11 = bits[24:25]
    nome = lookup_b_name(f3)
    if nome == "invalida":
        print_result("invalida", "", "", "", "", "", "", "", "")
        return
    pedaco_imm = pedaco_12 + pedaco_11 + pedaco_10_5 + pedaco_4_1 + "0"
    rs1 = register_to_abi(rs1_pedaco)
    rs2 = register_to_abi(rs2_pedaco)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rs1 + "," + rs2 + "," + imm
    print_result("B", nome, "", rs1, rs2, imm, f3, "", montada)


def decode_j_type(bits):
    pedaco_20 = bits[0:1]
    pedaco_10_1 = bits[1:11]
    pedaco_11 = bits[11:12]
    pedaco_19_12 = bits[12:20]
    rd_pedaco = bits[20:25]
    rd = register_to_abi(rd_pedaco)
    pedaco_imm = pedaco_20 + pedaco_19_12 + pedaco_11 + pedaco_10_1 + "0"
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = "jal" + " " + rd + "," + imm
    print_result("J", "jal", rd, "", "", imm, "", "", montada)
    texto_pseudo = identify_pseudo("jal", rd, "", imm)
    if texto_pseudo != "":
        print("pseudo: " + texto_pseudo)

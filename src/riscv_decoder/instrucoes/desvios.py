# decodificacao das instrucoes de desvio condicional e jal
from entrada.conversoes import binario_para_inteiro_com_sinal
from pseudo import identificar_pseudo
from instrucoes.comum import registrador_para_abi
from instrucoes.comum import mostrar_resultado
from instrucoes.identificacao import resolver_mnemonico_b


def decodificar_tipo_b(bits):
    pedaco_12 = bits[0:1]
    pedaco_10_5 = bits[1:7]
    rs2_pedaco = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    pedaco_4_1 = bits[20:24]
    pedaco_11 = bits[24:25]
    nome = resolver_mnemonico_b(f3)
    if nome == "invalida":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    pedaco_imm = pedaco_12 + pedaco_11 + pedaco_10_5 + pedaco_4_1 + "0"
    rs1 = registrador_para_abi(rs1_pedaco)
    rs2 = registrador_para_abi(rs2_pedaco)
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rs1 + "," + rs2 + "," + imm
    mostrar_resultado("B", nome, "", rs1, rs2, imm, f3, "", montada)


def decodificar_tipo_j(bits):
    pedaco_20 = bits[0:1]
    pedaco_10_1 = bits[1:11]
    pedaco_11 = bits[11:12]
    pedaco_19_12 = bits[12:20]
    rd_pedaco = bits[20:25]
    rd = registrador_para_abi(rd_pedaco)
    pedaco_imm = pedaco_20 + pedaco_19_12 + pedaco_11 + pedaco_10_1 + "0"
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = "jal" + " " + rd + "," + imm
    mostrar_resultado("J", "jal", rd, "", "", imm, "", "", montada)
    texto_pseudo = identificar_pseudo("jal", rd, "", imm)
    if texto_pseudo != "":
        print("pseudo: " + texto_pseudo)

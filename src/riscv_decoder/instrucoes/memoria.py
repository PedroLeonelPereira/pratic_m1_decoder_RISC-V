# decodificacao das instrucoes de carga, armazenamento e salto por registrador
from entrada.conversoes import binario_para_inteiro_com_sinal
from pseudo import identificar_pseudo
from instrucoes.comum import registrador_para_abi
from instrucoes.comum import mostrar_resultado
from instrucoes.identificacao import resolver_mnemonico_load
from instrucoes.identificacao import resolver_mnemonico_s


def decodificar_load(bits):
    pedaco_imm = bits[0:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    nome = resolver_mnemonico_load(f3)
    if nome == "invalida":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    rd = registrador_para_abi(rd_pedaco)
    rs1 = registrador_para_abi(rs1_pedaco)
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rd + "," + imm + "(" + rs1 + ")"
    mostrar_resultado("load", nome, rd, rs1, "", imm, f3, "", montada)


def decodificar_jalr(bits):
    pedaco_imm = bits[0:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    if f3 != "000":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    rd = registrador_para_abi(rd_pedaco)
    rs1 = registrador_para_abi(rs1_pedaco)
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = "jalr" + " " + rd + "," + imm + "(" + rs1 + ")"
    mostrar_resultado("jalr", "jalr", rd, rs1, "", imm, f3, "", montada)
    texto_pseudo = identificar_pseudo("jalr", rd, rs1, imm)
    if texto_pseudo != "":
        print("pseudo: " + texto_pseudo)


def decodificar_tipo_s(bits):
    pedaco_alto = bits[0:7]
    rs2_pedaco = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    pedaco_baixo = bits[20:25]
    nome = resolver_mnemonico_s(f3)
    if nome == "invalida":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    pedaco_imm = pedaco_alto + pedaco_baixo
    rs1 = registrador_para_abi(rs1_pedaco)
    rs2 = registrador_para_abi(rs2_pedaco)
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rs2 + "," + imm + "(" + rs1 + ")"
    mostrar_resultado("S", nome, "", rs1, rs2, imm, f3, "", montada)

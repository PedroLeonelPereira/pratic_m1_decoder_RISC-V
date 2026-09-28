# decodificacao das instrucoes aritmeticas dos formatos R e I
from entrada.conversoes import binario_para_inteiro_com_sinal
from entrada.conversoes import binario_para_inteiro_sem_sinal
from pseudo import identificar_pseudo
from instrucoes.comum import registrador_para_abi
from instrucoes.comum import mostrar_resultado
from instrucoes.identificacao import resolver_mnemonico_r
from instrucoes.identificacao import resolver_mnemonico_i


def decodificar_tipo_r(bits):
    f7 = bits[0:7]
    rs2_pedaco = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    nome = resolver_mnemonico_r(f3, f7)
    if nome == "invalida":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    rd = registrador_para_abi(rd_pedaco)
    rs1 = registrador_para_abi(rs1_pedaco)
    rs2 = registrador_para_abi(rs2_pedaco)
    montada = nome + " " + rd + "," + rs1 + "," + rs2
    mostrar_resultado("R", nome, rd, rs1, rs2, "", f3, f7, montada)


def decodificar_tipo_i(bits):
    f7 = bits[0:7]
    pedaco_imm = bits[0:12]
    pedaco_deslocamento = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    nome = resolver_mnemonico_i(f3, f7)
    if nome == "invalida":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    rd = registrador_para_abi(rd_pedaco)
    rs1 = registrador_para_abi(rs1_pedaco)
    if nome == "slli":
        quantidade = binario_para_inteiro_sem_sinal(pedaco_deslocamento)
        imm = str(quantidade)
        montada = nome + " " + rd + "," + rs1 + "," + imm
        mostrar_resultado("I", nome, rd, rs1, "", imm, f3, f7, montada)
        texto_pseudo = identificar_pseudo(nome, rd, rs1, imm)
        if texto_pseudo != "":
            print("pseudo: " + texto_pseudo)
        return
    if nome == "srli":
        quantidade = binario_para_inteiro_sem_sinal(pedaco_deslocamento)
        imm = str(quantidade)
        montada = nome + " " + rd + "," + rs1 + "," + imm
        mostrar_resultado("I", nome, rd, rs1, "", imm, f3, f7, montada)
        texto_pseudo = identificar_pseudo(nome, rd, rs1, imm)
        if texto_pseudo != "":
            print("pseudo: " + texto_pseudo)
        return
    if nome == "srai":
        quantidade = binario_para_inteiro_sem_sinal(pedaco_deslocamento)
        imm = str(quantidade)
        montada = nome + " " + rd + "," + rs1 + "," + imm
        mostrar_resultado("I", nome, rd, rs1, "", imm, f3, f7, montada)
        texto_pseudo = identificar_pseudo(nome, rd, rs1, imm)
        if texto_pseudo != "":
            print("pseudo: " + texto_pseudo)
        return
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rd + "," + rs1 + "," + imm
    mostrar_resultado("I", nome, rd, rs1, "", imm, f3, "", montada)
    texto_pseudo = identificar_pseudo(nome, rd, rs1, imm)
    if texto_pseudo != "":
        print("pseudo: " + texto_pseudo)

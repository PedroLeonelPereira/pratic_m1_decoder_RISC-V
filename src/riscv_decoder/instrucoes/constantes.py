# decodificacao das instrucoes lui e auipc
from entrada.conversoes import binario_para_inteiro_com_sinal
from instrucoes.comum import registrador_para_abi
from instrucoes.comum import mostrar_resultado


def decodificar_lui(bits):
    pedaco_alto = bits[0:20]
    rd_pedaco = bits[20:25]
    rd = registrador_para_abi(rd_pedaco)
    pedaco_imm = pedaco_alto + "000000000000"
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = "lui" + " " + rd + "," + imm
    mostrar_resultado("lui", "lui", rd, "", "", imm, "", "", montada)


def decodificar_auipc(bits):
    pedaco_alto = bits[0:20]
    rd_pedaco = bits[20:25]
    rd = registrador_para_abi(rd_pedaco)
    pedaco_imm = pedaco_alto + "000000000000"
    valor = binario_para_inteiro_com_sinal(pedaco_imm)
    imm = str(valor)
    montada = "auipc" + " " + rd + "," + imm
    mostrar_resultado("auipc", "auipc", rd, "", "", imm, "", "", montada)

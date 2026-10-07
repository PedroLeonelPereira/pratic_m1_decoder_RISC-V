# decodificacao das instrucoes lui e auipc
from entrada.conversoes import binary_to_signed
from instrucoes.comum import register_to_abi
from instrucoes.comum import print_result


def decode_lui(bits):
    pedaco_alto = bits[0:20]
    rd_pedaco = bits[20:25]
    rd = register_to_abi(rd_pedaco)
    pedaco_imm = pedaco_alto + "000000000000"
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = "lui" + " " + rd + "," + imm
    print_result("lui", "lui", rd, "", "", imm, "", "", montada)


def decode_auipc(bits):
    pedaco_alto = bits[0:20]
    rd_pedaco = bits[20:25]
    rd = register_to_abi(rd_pedaco)
    pedaco_imm = pedaco_alto + "000000000000"
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = "auipc" + " " + rd + "," + imm
    print_result("auipc", "auipc", rd, "", "", imm, "", "", montada)

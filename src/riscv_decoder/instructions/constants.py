# decodificacao das instrucoes lui e auipc
from input.convert import binary_to_signed
from instructions.common import register_to_abi
from instructions.common import criar_registro


def decode_lui(bits):
    pedaco_alto = bits[0:20]
    rd_pedaco = bits[20:25]
    rd = register_to_abi(rd_pedaco)
    pedaco_imm = pedaco_alto + "000000000000"
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = "lui" + " " + rd + "," + imm
    return criar_registro("lui", "lui", rd, "", "", imm, "", "", montada, "")


def decode_auipc(bits):
    pedaco_alto = bits[0:20]
    rd_pedaco = bits[20:25]
    rd = register_to_abi(rd_pedaco)
    pedaco_imm = pedaco_alto + "000000000000"
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = "auipc" + " " + rd + "," + imm
    return criar_registro("auipc", "auipc", rd, "", "", imm, "", "", montada, "")

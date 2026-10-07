# conversao de registradores e exibicao do resultado
from config import tabela_abi
from entrada.conversoes import binary_to_unsigned
from cpi import group_format


def register_to_abi(pedaco):
    return tabela_abi[pedaco]


def print_result(tipo, nome, rd, rs1, rs2, imm, f3, f7, montada):
    print("")
    if tipo == "invalida":
        print("instrucao invalida")
        return
    formato = group_format(tipo)
    if formato == "":
        formato = tipo
    print("formato: " + formato)
    print("mnemonico: " + nome)
    if rd != "":
        print("rd: " + rd)
    if rs1 != "":
        print("rs1: " + rs1)
    if rs2 != "":
        print("rs2: " + rs2)
    if imm != "":
        print("imm: " + imm)
    if f3 != "":
        valor_f3 = binary_to_unsigned(f3)
        print("f3: " + str(valor_f3))
    if f7 != "":
        valor_f7 = binary_to_unsigned(f7)
        print("f7: " + str(valor_f7))
    print("assembly: " + montada)

# conversao de registradores e exibicao do resultado
from config import tabela_abi


def registrador_para_abi(pedaco):
    return tabela_abi[pedaco]


def mostrar_resultado(tipo, nome, rd, rs1, rs2, imm, f3, f7, montada):
    if tipo == "invalida":
        print("instrucao invalida")
        return
    print("formato: " + tipo)
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
        print("f3: " + f3)
    if f7 != "":
        print("f7: " + f7)
    print("assembly: " + montada)

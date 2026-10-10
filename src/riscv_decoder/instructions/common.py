# conversao de registradores, montagem e exibicao do resultado
from config import tabela_abi
from input.convert import binary_to_unsigned
from cpi import group_format


def register_to_abi(pedaco):
    return tabela_abi[pedaco]


# monta um dicionario com o resultado da instrucao decodificada
# sempre tem as mesmas chaves, campo ausente fica com texto vazio
# pseudo fica com texto vazio quando nao ha correspondencia
# endereco comeca zerado e e preenchido depois pelo modulo de pipeline
def criar_registro(tipo, nome, rd, rs1, rs2, imm, f3, f7, montada, pseudo):
    registro = {}
    registro["tipo"] = tipo
    if tipo == "invalida":
        registro["formato"] = ""
    else:
        formato = group_format(tipo)
        if formato == "":
            formato = tipo
        registro["formato"] = formato
    registro["mnemonico"] = nome
    registro["rd"] = rd
    registro["rs1"] = rs1
    registro["rs2"] = rs2
    registro["imm"] = imm
    registro["f3"] = f3
    registro["f7"] = f7
    registro["assembly"] = montada
    registro["pseudo"] = pseudo
    registro["endereco"] = 0
    registro["endereco_texto"] = ""
    return registro


# mostra um registro na ordem fixa de campos, omitindo ausentes
# invalida imprime endereco quando existe e so a marca canonica e segue
def mostrar_registro(registro):
    print("")
    if registro["endereco_texto"] != "":
        print("endereco: " + registro["endereco_texto"])
    if registro["tipo"] == "invalida":
        print("instrucao invalida")
        return
    print("formato: " + registro["formato"])
    print("mnemonico: " + registro["mnemonico"])
    if registro["rd"] != "":
        print("rd: " + registro["rd"])
    if registro["rs1"] != "":
        print("rs1: " + registro["rs1"])
    if registro["rs2"] != "":
        print("rs2: " + registro["rs2"])
    if registro["imm"] != "":
        print("imm: " + registro["imm"])
    if registro["f3"] != "":
        valor_f3 = binary_to_unsigned(registro["f3"])
        print("f3: " + str(valor_f3))
    if registro["f7"] != "":
        valor_f7 = binary_to_unsigned(registro["f7"])
        print("f7: " + str(valor_f7))
    print("assembly: " + registro["assembly"])
    if registro["pseudo"] != "":
        print("pseudo: " + registro["pseudo"])

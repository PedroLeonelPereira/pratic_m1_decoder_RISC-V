# decodificacao das instrucoes aritmeticas dos formatos R e I
from input.convert import binary_to_signed
from input.convert import binary_to_unsigned
from pseudo import identify_pseudo
from instructions.common import register_to_abi
from instructions.common import criar_registro
from instructions.identify import lookup_r_name
from instructions.identify import lookup_i_name


def decode_r_type(bits):
    f7 = bits[0:7]
    rs2_pedaco = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    nome = lookup_r_name(f3, f7)
    if nome == "invalida":
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    rd = register_to_abi(rd_pedaco)
    rs1 = register_to_abi(rs1_pedaco)
    rs2 = register_to_abi(rs2_pedaco)
    montada = nome + " " + rd + "," + rs1 + "," + rs2
    return criar_registro("R", nome, rd, rs1, rs2, "", f3, f7, montada, "")


def decode_i_type(bits):
    f7 = bits[0:7]
    pedaco_imm = bits[0:12]
    pedaco_deslocamento = bits[7:12]
    rs1_pedaco = bits[12:17]
    f3 = bits[17:20]
    rd_pedaco = bits[20:25]
    nome = lookup_i_name(f3, f7)
    if nome == "invalida":
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    rd = register_to_abi(rd_pedaco)
    rs1 = register_to_abi(rs1_pedaco)
    if nome == "slli":
        quantidade = binary_to_unsigned(pedaco_deslocamento)
        imm = str(quantidade)
        montada = nome + " " + rd + "," + rs1 + "," + imm
        texto_pseudo = identify_pseudo(nome, rd, rs1, imm)
        return criar_registro("I", nome, rd, rs1, "", imm, f3, f7, montada, texto_pseudo)
    if nome == "srli":
        quantidade = binary_to_unsigned(pedaco_deslocamento)
        imm = str(quantidade)
        montada = nome + " " + rd + "," + rs1 + "," + imm
        texto_pseudo = identify_pseudo(nome, rd, rs1, imm)
        return criar_registro("I", nome, rd, rs1, "", imm, f3, f7, montada, texto_pseudo)
    if nome == "srai":
        quantidade = binary_to_unsigned(pedaco_deslocamento)
        imm = str(quantidade)
        montada = nome + " " + rd + "," + rs1 + "," + imm
        texto_pseudo = identify_pseudo(nome, rd, rs1, imm)
        return criar_registro("I", nome, rd, rs1, "", imm, f3, f7, montada, texto_pseudo)
    valor = binary_to_signed(pedaco_imm)
    imm = str(valor)
    montada = nome + " " + rd + "," + rs1 + "," + imm
    texto_pseudo = identify_pseudo(nome, rd, rs1, imm)
    return criar_registro("I", nome, rd, rs1, "", imm, f3, "", montada, texto_pseudo)

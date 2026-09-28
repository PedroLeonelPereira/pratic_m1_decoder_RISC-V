# identifica pseudo-instrucao comum a partir da instrucao real
# recebe mnemonico real, nomes ABI de destino e origem e imediato em texto
# devolve texto pseudo pronto ou vazio quando nao ha correspondencia


def identificar_pseudo(nome, rd, rs1, imm):
    if nome == "addi":
        if rd == "zero":
            if rs1 == "zero":
                if imm == "0":
                    return "nop"
        else:
            if rs1 != "zero":
                if imm == "0":
                    return "mv " + rd + "," + rs1
    if nome == "jal":
        if rd == "zero":
            return "j " + imm
    if nome == "jalr":
        if rd == "zero":
            if rs1 == "ra":
                if imm == "0":
                    return "ret"
    return ""

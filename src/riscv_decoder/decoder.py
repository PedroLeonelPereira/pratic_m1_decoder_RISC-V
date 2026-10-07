# ponto central do programa pede arquivo, encaminha a decodificacao e mostra cada linha
# rode pelo arquivo principal com python src/riscv_decoder/main.py
from entrada.linhas import clean_line
from instrucoes.identificacao import identify_type
from instrucoes.comum import print_result
from instrucoes.aritmetica import decode_r_type
from instrucoes.aritmetica import decode_i_type
from instrucoes.memoria import decode_load
from instrucoes.memoria import decode_jalr
from instrucoes.memoria import decode_s_type
from instrucoes.desvios import decode_b_type
from instrucoes.desvios import decode_j_type
from instrucoes.constantes import decode_lui
from instrucoes.constantes import decode_auipc
from cpi import read_weights_csv
from cpi import group_format
from cpi import print_cpi_summary


def decode_and_print(bits):
    if len(bits) != 32:
        print_result("invalida", "", "", "", "", "", "", "", "")
        return
    validos = ""
    for caractere in bits:
        if caractere == "0":
            validos = validos + "0"
        else:
            if caractere == "1":
                validos = validos + "1"
    if validos != bits:
        print_result("invalida", "", "", "", "", "", "", "", "")
        return
    opcode = bits[25:32]
    tipo = identify_type(opcode)
    if tipo == "invalida":
        print_result("invalida", "", "", "", "", "", "", "", "")
        return
    if tipo == "R":
        decode_r_type(bits)
        return
    if tipo == "I":
        decode_i_type(bits)
        return
    if tipo == "load":
        decode_load(bits)
        return
    if tipo == "jalr":
        decode_jalr(bits)
        return
    if tipo == "S":
        decode_s_type(bits)
        return
    if tipo == "B":
        decode_b_type(bits)
        return
    if tipo == "lui":
        decode_lui(bits)
        return
    if tipo == "auipc":
        decode_auipc(bits)
        return
    if tipo == "J":
        decode_j_type(bits)
        return
    print_result("invalida", "", "", "", "", "", "", "", "")


def run_program():
    caminho = input("caminho do arquivo: ")
    caminho_pesos = input("caminho do csv de pesos: ")
    peso_r, peso_i, peso_s, peso_b, peso_u, peso_j = read_weights_csv(caminho_pesos)
    contadores = {"R": 0, "I": 0, "S": 0, "B": 0, "U": 0, "J": 0}
    arquivo = open(caminho)
    for linha in arquivo:
        normalizada = clean_line(linha)
        if normalizada != "pular":
            if normalizada == "invalida":
                print_result("invalida", "", "", "", "", "", "", "", "")
            else:
                decode_and_print(normalizada)
                opcode = normalizada[25:32]
                tipo = identify_type(opcode)
                grupo = group_format(tipo)
                if grupo in contadores:
                    contadores[grupo] = contadores[grupo] + 1
    arquivo.close()
    cont_r = contadores["R"]
    cont_i = contadores["I"]
    cont_s = contadores["S"]
    cont_b = contadores["B"]
    cont_u = contadores["U"]
    cont_j = contadores["J"]
    print_cpi_summary(cont_r, cont_i, cont_s, cont_b, cont_u, cont_j, peso_r, peso_i, peso_s, peso_b, peso_u, peso_j)


def main():
    run_program()


if __name__ == "__main__":
    main()

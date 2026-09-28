# ponto central do programa pede arquivo, encaminha a decodificacao e mostra cada linha
# rode pelo arquivo principal com python src/riscv_decoder/main.py
from entrada.linhas import normalizar_linha
from instrucoes.identificacao import identificar_tipo
from instrucoes.comum import mostrar_resultado
from instrucoes.aritmetica import decodificar_tipo_r
from instrucoes.aritmetica import decodificar_tipo_i
from instrucoes.memoria import decodificar_load
from instrucoes.memoria import decodificar_jalr
from instrucoes.memoria import decodificar_tipo_s
from instrucoes.desvios import decodificar_tipo_b
from instrucoes.desvios import decodificar_tipo_j
from instrucoes.constantes import decodificar_lui
from instrucoes.constantes import decodificar_auipc
from cpi import ler_pesos_csv
from cpi import agrupar_formato
from cpi import mostrar_resumo_cpi


def decodificar_e_mostrar(bits):
    if len(bits) != 32:
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    validos = ""
    for caractere in bits:
        if caractere == "0":
            validos = validos + "0"
        else:
            if caractere == "1":
                validos = validos + "1"
    if validos != bits:
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    opcode = bits[25:32]
    tipo = identificar_tipo(opcode)
    if tipo == "invalida":
        mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
        return
    if tipo == "R":
        decodificar_tipo_r(bits)
        return
    if tipo == "I":
        decodificar_tipo_i(bits)
        return
    if tipo == "load":
        decodificar_load(bits)
        return
    if tipo == "jalr":
        decodificar_jalr(bits)
        return
    if tipo == "S":
        decodificar_tipo_s(bits)
        return
    if tipo == "B":
        decodificar_tipo_b(bits)
        return
    if tipo == "lui":
        decodificar_lui(bits)
        return
    if tipo == "auipc":
        decodificar_auipc(bits)
        return
    if tipo == "J":
        decodificar_tipo_j(bits)
        return
    mostrar_resultado("invalida", "", "", "", "", "", "", "", "")


def programa_principal():
    caminho = input("caminho do arquivo: ")
    caminho_pesos = input("caminho do csv de pesos: ")
    peso_r, peso_i, peso_s, peso_b, peso_u, peso_j = ler_pesos_csv(caminho_pesos)
    cont_r = 0
    cont_i = 0
    cont_s = 0
    cont_b = 0
    cont_u = 0
    cont_j = 0
    arquivo = open(caminho)
    for linha in arquivo:
        normalizada = normalizar_linha(linha)
        if normalizada != "pular":
            if normalizada == "invalida":
                mostrar_resultado("invalida", "", "", "", "", "", "", "", "")
            else:
                decodificar_e_mostrar(normalizada)
                opcode = normalizada[25:32]
                tipo = identificar_tipo(opcode)
                grupo = agrupar_formato(tipo)
                if grupo == "R":
                    cont_r = cont_r + 1
                else:
                    if grupo == "I":
                        cont_i = cont_i + 1
                    else:
                        if grupo == "S":
                            cont_s = cont_s + 1
                        else:
                            if grupo == "B":
                                cont_b = cont_b + 1
                            else:
                                if grupo == "U":
                                    cont_u = cont_u + 1
                                else:
                                    if grupo == "J":
                                        cont_j = cont_j + 1
    arquivo.close()
    mostrar_resumo_cpi(cont_r, cont_i, cont_s, cont_b, cont_u, cont_j, peso_r, peso_i, peso_s, peso_b, peso_u, peso_j)


def main():
    programa_principal()


if __name__ == "__main__":
    main()

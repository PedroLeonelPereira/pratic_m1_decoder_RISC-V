# ponto central do programa pede arquivo, encaminha a decodificacao e mostra cada linha
# guarda cada resultado numa lista e conta o cpi a partir dessa lista
# rode pelo arquivo principal com python src/riscv_decoder/main.py
from input.lines import clean_line
from instructions.identify import identify_type
from instructions.common import criar_registro
from instructions.common import mostrar_registro
from instructions.arithmetic import decode_r_type
from instructions.arithmetic import decode_i_type
from instructions.memory import decode_load
from instructions.memory import decode_jalr
from instructions.memory import decode_s_type
from instructions.jumps import decode_b_type
from instructions.jumps import decode_j_type
from instructions.constants import decode_lui
from instructions.constants import decode_auipc
from cpi import read_weights_csv
from cpi import print_cpi_summary
from pipeline import atribuir_enderecos
from pipeline import detectar_conflitos_dados
from pipeline import mostrar_conflitos_dados
from pipeline import detectar_conflitos_controle
from pipeline import delimitar_blocos_basicos
from pipeline import detectar_conflitos_borda
from pipeline import mostrar_controle
from pipeline import corrigir_somente_nops
from pipeline import corrigir_com_reordenacao
from pipeline import descobrir_estilo_entrada
from pipeline import gerar_nome_saida
from pipeline import escrever_arquivo_corrigido
from pipeline import mostrar_listagem
from pipeline import mostrar_custo
from pipeline import bits_para_hex_linha


def decodificar(bits):
    if len(bits) != 32:
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    validos = ""
    for caractere in bits:
        if caractere == "0":
            validos = validos + "0"
        else:
            if caractere == "1":
                validos = validos + "1"
    if validos != bits:
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    opcode = bits[25:32]
    tipo = identify_type(opcode)
    if tipo == "invalida":
        return criar_registro("invalida", "", "", "", "", "", "", "", "", "")
    if tipo == "R":
        return decode_r_type(bits)
    if tipo == "I":
        return decode_i_type(bits)
    if tipo == "load":
        return decode_load(bits)
    if tipo == "jalr":
        return decode_jalr(bits)
    if tipo == "S":
        return decode_s_type(bits)
    if tipo == "B":
        return decode_b_type(bits)
    if tipo == "lui":
        return decode_lui(bits)
    if tipo == "auipc":
        return decode_auipc(bits)
    if tipo == "J":
        return decode_j_type(bits)
    return criar_registro("invalida", "", "", "", "", "", "", "", "", "")


def run_program():
    caminho = input("caminho do arquivo: ")
    caminho_pesos = input("caminho do csv de pesos: ")
    peso_r, peso_i, peso_s, peso_b, peso_u, peso_j = read_weights_csv(caminho_pesos)
    lista_resultados = []
    arquivo = open(caminho)
    for linha in arquivo:
        normalizada = clean_line(linha)
        if normalizada != "pular":
            if normalizada == "invalida":
                registro = criar_registro("invalida", "", "", "", "", "", "", "", "", "")
                registro["bits"] = ""
                registro["hex"] = ""
            else:
                registro = decodificar(normalizada)
                registro["bits"] = normalizada
                registro["hex"] = bits_para_hex_linha(normalizada)
            registro["inserido"] = "nao"
            registro["movido"] = "nao"
            registro["endereco_original"] = 0
            lista_resultados.append(registro)
    arquivo.close()
    atribuir_enderecos(lista_resultados)
    indice_endereco = 0
    total_endereco = len(lista_resultados)
    while indice_endereco < total_endereco:
        lista_resultados[indice_endereco]["endereco_original"] = lista_resultados[indice_endereco]["endereco"]
        indice_endereco = indice_endereco + 1
    for registro in lista_resultados:
        mostrar_registro(registro)
    lista_conflitos = detectar_conflitos_dados(lista_resultados)
    mostrar_conflitos_dados(lista_conflitos)
    lista_controle = detectar_conflitos_controle(lista_resultados)
    lista_blocos = delimitar_blocos_basicos(lista_resultados)
    lista_borda = detectar_conflitos_borda(lista_resultados)
    mostrar_controle(lista_controle, lista_blocos, lista_borda)
    lista_nops = corrigir_somente_nops(lista_resultados)
    lista_reord = corrigir_com_reordenacao(lista_resultados)
    estilo = descobrir_estilo_entrada(caminho)
    caminho_nops = gerar_nome_saida(caminho, "_nops")
    caminho_reord = gerar_nome_saida(caminho, "_reord")
    escrever_arquivo_corrigido(caminho_nops, lista_nops, estilo)
    escrever_arquivo_corrigido(caminho_reord, lista_reord, estilo)
    print("ARQUIVO SOMENTE NOPS: " + caminho_nops)
    mostrar_listagem("LISTAGEM SOMENTE NOPS", lista_nops)
    print("ARQUIVO REORDENACAO: " + caminho_reord)
    mostrar_listagem("LISTAGEM REORDENACAO", lista_reord)
    mostrar_custo(len(lista_resultados), len(lista_nops), len(lista_reord))
    cont_r = 0
    cont_i = 0
    cont_s = 0
    cont_b = 0
    cont_u = 0
    cont_j = 0
    for registro in lista_resultados:
        formato = registro["formato"]
        if formato == "R":
            cont_r = cont_r + 1
        elif formato == "I":
            cont_i = cont_i + 1
        elif formato == "S":
            cont_s = cont_s + 1
        elif formato == "B":
            cont_b = cont_b + 1
        elif formato == "U":
            cont_u = cont_u + 1
        elif formato == "J":
            cont_j = cont_j + 1
    print_cpi_summary(cont_r, cont_i, cont_s, cont_b, cont_u, cont_j, peso_r, peso_i, peso_s, peso_b, peso_u, peso_j)
    return lista_resultados


def main():
    run_program()


if __name__ == "__main__":
    main()

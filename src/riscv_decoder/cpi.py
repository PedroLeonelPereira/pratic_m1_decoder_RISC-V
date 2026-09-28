# calculo de cpi medio por formato de instrucao
# excecao pontual a regra de simplicidade: usa divisao (/) e numero
# decimal so neste arquivo, para porcentagem e media ponderada
# o resto do programa continua so com aritmetica simples


# agrupa os 9 tipos internos do decodificador nos 6 formatos classicos
# load e jalr sao formato I, lui e auipc sao formato U
# devolve vazio quando o tipo e invalido
def agrupar_formato(tipo):
    if tipo == "R":
        return "R"
    if tipo == "I":
        return "I"
    if tipo == "load":
        return "I"
    if tipo == "jalr":
        return "I"
    if tipo == "S":
        return "S"
    if tipo == "B":
        return "B"
    if tipo == "lui":
        return "U"
    if tipo == "auipc":
        return "U"
    if tipo == "J":
        return "J"
    return ""


# guarda o peso lido para um formato nas variaveis de peso
# devolve os seis pesos atualizados em ordem
def guardar_peso(nome, valor, peso_r, peso_i, peso_s, peso_b, peso_u, peso_j):
    if nome == "R":
        return valor, peso_i, peso_s, peso_b, peso_u, peso_j
    if nome == "I":
        return peso_r, valor, peso_s, peso_b, peso_u, peso_j
    if nome == "S":
        return peso_r, peso_i, valor, peso_b, peso_u, peso_j
    if nome == "B":
        return peso_r, peso_i, peso_s, valor, peso_u, peso_j
    if nome == "U":
        return peso_r, peso_i, peso_s, peso_b, valor, peso_j
    if nome == "J":
        return peso_r, peso_i, peso_s, peso_b, peso_u, valor
    return peso_r, peso_i, peso_s, peso_b, peso_u, peso_j


# le o csv de pesos sem cabecalho, uma linha por formato
# exemplo de linha: R,2
# linha vazia e # pulam, linha ruim mantem peso zero e segue
# devolve os seis pesos em ordem R I S B U J
def ler_pesos_csv(caminho):
    peso_r = 0
    peso_i = 0
    peso_s = 0
    peso_b = 0
    peso_u = 0
    peso_j = 0
    arquivo = open(caminho)
    for linha in arquivo:
        arrumada = linha.strip()
        if arrumada != "":
            if arrumada[0:1] != "#":
                partes = arrumada.split(",")
                if len(partes) == 2:
                    nome = partes[0].strip()
                    texto_peso = partes[1].strip()
                    deu_erro = "nao"
                    try:
                        valor = int(texto_peso)
                    except ValueError:
                        deu_erro = "sim"
                    if deu_erro == "nao":
                        peso_r, peso_i, peso_s, peso_b, peso_u, peso_j = guardar_peso(nome, valor, peso_r, peso_i, peso_s, peso_b, peso_u, peso_j)
    arquivo.close()
    return peso_r, peso_i, peso_s, peso_b, peso_u, peso_j


# imprime totais, porcentagem por formato e cpi medio ponderado
# instrucao invalida nao entra na conta
def mostrar_resumo_cpi(cont_r, cont_i, cont_s, cont_b, cont_u, cont_j, peso_r, peso_i, peso_s, peso_b, peso_u, peso_j):
    total = cont_r + cont_i + cont_s + cont_b + cont_u + cont_j
    print("Instrucoes totais = " + str(total))
    if total == 0:
        print("Instrucoes por formato, R = 0% I = 0% S = 0% B = 0% U = 0% J = 0%")
        print("CPI medio = 0")
        return
    porc_r = cont_r * 100 / total
    porc_i = cont_i * 100 / total
    porc_s = cont_s * 100 / total
    porc_b = cont_b * 100 / total
    porc_u = cont_u * 100 / total
    porc_j = cont_j * 100 / total
    linha = "Instrucoes por formato, R = " + str(porc_r) + "%"
    linha = linha + " I = " + str(porc_i) + "%"
    linha = linha + " S = " + str(porc_s) + "%"
    linha = linha + " B = " + str(porc_b) + "%"
    linha = linha + " U = " + str(porc_u) + "%"
    linha = linha + " J = " + str(porc_j) + "%"
    print(linha)
    soma = cont_r * peso_r + cont_i * peso_i + cont_s * peso_s + cont_b * peso_b + cont_u * peso_u + cont_j * peso_j
    media = soma / total
    print("CPI medio = " + str(media))

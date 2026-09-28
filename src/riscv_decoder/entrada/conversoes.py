# converte representacoes binarias em numeros

def binario_para_inteiro_sem_sinal(bits):
    valor = 0
    for caractere in bits:
        valor = valor * 2
        if caractere == "1":
            valor = valor + 1
    return valor


def binario_para_inteiro_com_sinal(bits):
    valor = 0
    for caractere in bits:
        valor = valor * 2
        if caractere == "1":
            valor = valor + 1
    if bits[0:1] == "1":
        potencia = 1
        contador = 0
        tamanho = len(bits)
        while contador < tamanho:
            potencia = potencia * 2
            contador = contador + 1
        valor = valor - potencia
    return valor

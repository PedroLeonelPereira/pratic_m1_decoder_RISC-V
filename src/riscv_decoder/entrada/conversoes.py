# converte representacoes binarias em numeros

def binario_para_inteiro_sem_sinal(bits):
    return int(bits, 2)


def binario_para_inteiro_com_sinal(bits):
    valor = int(bits, 2)
    if bits[0:1] == "1":
        potencia = 1
        contador = 0
        tamanho = len(bits)
        while contador < tamanho:
            potencia = potencia * 2
            contador = contador + 1
        valor = valor - potencia
    return valor

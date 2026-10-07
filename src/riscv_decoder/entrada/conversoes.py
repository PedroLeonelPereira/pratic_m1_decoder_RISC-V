# converte representacoes binarias em numeros

def binary_to_unsigned(bits):
    return int(bits, 2)


def binary_to_signed(bits):
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

# normaliza cada linha de entrada e converte hexadecimal para binario

def completar_32(bits):
    falta = 32 - len(bits)
    return "0" * falta + bits


def hex_to_bin(texto):
    if texto == "":
        return "invalida"
    for caractere in texto:
        if caractere < "0":
            return "invalida"
        if "9" < caractere:
            if caractere < "A":
                return "invalida"
            if "F" < caractere:
                if caractere < "a":
                    return "invalida"
                if "f" < caractere:
                    return "invalida"
    numero = int(texto, 16)
    return format(numero, "b")


def normalizar_linha(linha_bruta):
    arrumado = linha_bruta.strip()
    if arrumado == "":
        return "pular"
    if arrumado[0:1] == "#":
        return "pular"
    binario = arrumado
    if arrumado[0:2] == "0x":
        binario = hex_to_bin(arrumado[2:len(arrumado)])
    else:
        if arrumado[0:2] == "0X":
            binario = hex_to_bin(arrumado[2:len(arrumado)])
    # hex_to_bin devolve a palavra invalida quando o texto nao e hexadecimal
    if binario == "invalida":
        return "invalida"
    # int com base 2 so valida: aceita o texto ou reclama com ValueError
    try:
        int(binario, 2)
    except ValueError:
        return "invalida"
    if 32 < len(binario):
        return "invalida"
    return completar_32(binario)

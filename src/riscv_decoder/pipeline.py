# enderecamento sequencial e deteccao de conflitos de dados
# cada instrucao valida ou invalida ocupa um endereco, linha pulada nao ocupa
# conflito so leitura apos escrita com produtor mais recente, distancia 1 ou 2
# rode pelo arquivo principal com python src/riscv_decoder/main.py

endereco_base = 4194304
passo_endereco = 4


# devolve o digito hexadecimal minusculo para um valor de 0 a 15
# usa so comparacao e texto, sem conta esperta
def digito_hex(valor):
    if valor == 0:
        return "0"
    if valor == 1:
        return "1"
    if valor == 2:
        return "2"
    if valor == 3:
        return "3"
    if valor == 4:
        return "4"
    if valor == 5:
        return "5"
    if valor == 6:
        return "6"
    if valor == 7:
        return "7"
    if valor == 8:
        return "8"
    if valor == 9:
        return "9"
    if valor == 10:
        return "a"
    if valor == 11:
        return "b"
    if valor == 12:
        return "c"
    if valor == 13:
        return "d"
    if valor == 14:
        return "e"
    return "f"


# converte numero decimal em texto hexadecimal com 8 digitos e zeros a esquerda
# exemplo: 4194304 vira 00400000
# usa so soma, subtracao, multiplicacao e comparacao
def numero_para_hex_oito(valor):
    resto = valor
    texto = ""
    potencia = 268435456
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    potencia = 16777216
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    potencia = 1048576
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    potencia = 65536
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    potencia = 4096
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    potencia = 256
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    potencia = 16
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    potencia = 1
    contador = 0
    while potencia <= resto:
        resto = resto - potencia
        contador = contador + 1
    texto = texto + digito_hex(contador)
    return texto


# devolve o endereco em texto canonico, exemplo 0x00400000
def endereco_para_texto(endereco):
    return "0x" + numero_para_hex_oito(endereco)


# preenche cada registro da lista com endereco sequencial e texto do endereco
# primeira instrucao usa a base canonica, cada seguinte soma o passo fixo
# linha pulada nunca entra na lista, invalida ocupa endereco normalmente
def atribuir_enderecos(lista_resultados):
    endereco_atual = endereco_base
    indice = 0
    total = len(lista_resultados)
    while indice < total:
        registro = lista_resultados[indice]
        registro["endereco"] = endereco_atual
        registro["endereco_texto"] = endereco_para_texto(endereco_atual)
        endereco_atual = endereco_atual + passo_endereco
        indice = indice + 1
    return lista_resultados


# devolve o registrador escrito pela instrucao ou vazio quando nao escreve
# invalida nunca escreve, destino ausente nunca escreve, zero nunca conflita
def obter_escrita(registro):
    if registro["tipo"] == "invalida":
        return ""
    destino = registro["rd"]
    if destino == "":
        return ""
    if destino == "zero":
        return ""
    return destino


# devolve a lista de registradores lidos pela instrucao
# invalida nunca le, campo ausente nao e leitura, zero nunca conflita
# instrucao que le dois conta os dois, leitura repetida conta uma vez so
def listar_leituras(registro):
    leituras = []
    if registro["tipo"] == "invalida":
        return leituras
    origem_um = registro["rs1"]
    origem_dois = registro["rs2"]
    if origem_um != "":
        if origem_um != "zero":
            leituras.append(origem_um)
    if origem_dois != "":
        if origem_dois != "zero":
            ja_tem = "nao"
            contador = 0
            while contador < len(leituras):
                if leituras[contador] == origem_dois:
                    ja_tem = "sim"
                contador = contador + 1
            if ja_tem == "nao":
                leituras.append(origem_dois)
    return leituras


# cria um registro de conflito com produtor, consumidor, registrador e nops
def criar_conflito(produtor_texto, produtor_assembly, consumidor_texto, consumidor_assembly, registrador, distancia, nops):
    conflito = {}
    conflito["produtor"] = produtor_texto
    conflito["produtor_assembly"] = produtor_assembly
    conflito["consumidor"] = consumidor_texto
    conflito["consumidor_assembly"] = consumidor_assembly
    conflito["registrador"] = registrador
    conflito["distancia"] = distancia
    conflito["nops"] = nops
    return conflito


# detecta conflitos de dados por dependencia verdadeira com produtor mais recente
# para cada leitura procura o ultimo escritor do mesmo registrador
# conflito so quando distancia e 1 (2 nops) ou 2 (1 nop), distancia 3 ou mais ignora
# escrita apos leitura e escrita apos escrita nunca viram conflito
def detectar_conflitos_dados(lista_resultados):
    conflitos = []
    ultimo_produtor = {}
    indice = 0
    total = len(lista_resultados)
    while indice < total:
        registro = lista_resultados[indice]
        leituras = listar_leituras(registro)
        contador_leitura = 0
        while contador_leitura < len(leituras):
            registrador = leituras[contador_leitura]
            if registrador in ultimo_produtor:
                indice_produtor = ultimo_produtor[registrador]
                distancia = indice - indice_produtor
                if distancia == 1:
                    nops = 2
                    produtor = lista_resultados[indice_produtor]
                    conflito = criar_conflito(produtor["endereco_texto"], produtor["assembly"], registro["endereco_texto"], registro["assembly"], registrador, distancia, nops)
                    conflitos.append(conflito)
                else:
                    if distancia == 2:
                        nops = 1
                        produtor = lista_resultados[indice_produtor]
                        conflito = criar_conflito(produtor["endereco_texto"], produtor["assembly"], registro["endereco_texto"], registro["assembly"], registrador, distancia, nops)
                        conflitos.append(conflito)
            contador_leitura = contador_leitura + 1
        escrita = obter_escrita(registro)
        if escrita != "":
            ultimo_produtor[escrita] = indice
        indice = indice + 1
    return conflitos


# mostra os conflitos de dados no formato canonico com produtor e consumidor
def mostrar_conflitos_dados(lista_conflitos):
    print("CONFLITOS DE DADOS")
    indice = 0
    total = len(lista_conflitos)
    while indice < total:
        conflito = lista_conflitos[indice]
        linha = "  " + conflito["consumidor"] + " " + conflito["consumidor_assembly"]
        linha = linha + " <- " + conflito["produtor"] + " " + conflito["produtor_assembly"]
        linha = linha + " [" + conflito["registrador"] + ", d=" + str(conflito["distancia"]) + ", " + str(conflito["nops"]) + " nops]"
        print(linha)
        indice = indice + 1

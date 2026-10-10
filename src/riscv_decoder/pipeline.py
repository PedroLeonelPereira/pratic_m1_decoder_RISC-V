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


# diz se o registro e um desvio condicional valido
# desvio condicional e o tipo B, que le dois registradores e nao escreve nenhum
# invalida nunca e desvio, mesmo que o texto pareca um desvio
def eh_desvio_condicional(registro):
    if registro["tipo"] == "invalida":
        return "nao"
    if registro["tipo"] == "B":
        return "sim"
    return "nao"


# diz se o registro e um salto valido
# salto e o jal do tipo J ou o jalr, os dois encerram o bloco basico
# invalida nunca e salto
def eh_salto(registro):
    if registro["tipo"] == "invalida":
        return "nao"
    if registro["tipo"] == "J":
        return "sim"
    if registro["tipo"] == "jalr":
        return "sim"
    return "nao"


# diz se o registro encerra um bloco basico
# todo desvio condicional e todo salto encerram um bloco
def eh_desvio_ou_salto(registro):
    if eh_desvio_condicional(registro) == "sim":
        return "sim"
    if eh_salto(registro) == "sim":
        return "sim"
    return "nao"


# calcula o endereco de destino de um desvio condicional ou de um jal
# destino e o proprio endereco mais o deslocamento decimal do campo imm
# jalr tem destino desconhecido porque depende do valor do registrador, devolve -1
# invalida e formato sem deslocamento tambem devolvem -1
def calcular_alvo(registro):
    if registro["tipo"] == "invalida":
        return 0 - 1
    if registro["tipo"] == "B":
        texto = registro["imm"]
        if texto == "":
            return 0 - 1
        deslocamento = int(texto)
        return registro["endereco"] + deslocamento
    if registro["tipo"] == "J":
        texto = registro["imm"]
        if texto == "":
            return 0 - 1
        deslocamento = int(texto)
        return registro["endereco"] + deslocamento
    return 0 - 1


# monta a tabela de endereco para posicao na lista
# serve para achar a instrucao de destino de cada desvio ou salto
def mapa_endereco_indice(lista_resultados):
    mapa = {}
    indice = 0
    total = len(lista_resultados)
    while indice < total:
        registro = lista_resultados[indice]
        mapa[registro["endereco"]] = indice
        indice = indice + 1
    return mapa


# cria um registro de conflito de controle com o desvio e o ocupante do slot
def criar_conflito_controle(desvio_texto, desvio_assembly, slot_texto, slot_assembly):
    conflito = {}
    conflito["desvio"] = desvio_texto
    conflito["desvio_assembly"] = desvio_assembly
    conflito["slot"] = slot_texto
    conflito["slot_assembly"] = slot_assembly
    return conflito


# detecta um conflito de controle para cada desvio condicional valido
# o ocupante do slot e sempre a instrucao seguinte, que executa nos dois caminhos
# desvio sem seguinte e seguinte invalida nao viram slot e nao geram conflito
def detectar_conflitos_controle(lista_resultados):
    conflitos = []
    indice = 0
    total = len(lista_resultados)
    while indice < total:
        registro = lista_resultados[indice]
        if eh_desvio_condicional(registro) == "sim":
            seguinte = indice + 1
            if seguinte < total:
                ocupante = lista_resultados[seguinte]
                if ocupante["tipo"] != "invalida":
                    conflito = criar_conflito_controle(registro["endereco_texto"], registro["assembly"], ocupante["endereco_texto"], ocupante["assembly"])
                    conflitos.append(conflito)
        indice = indice + 1
    return conflitos


# cria um registro de bloco basico com numero, endereco inicial, final e tamanho
def criar_bloco(numero, inicio_texto, fim_texto, tamanho):
    bloco = {}
    bloco["numero"] = numero
    bloco["inicio"] = inicio_texto
    bloco["fim"] = fim_texto
    bloco["total"] = tamanho
    return bloco


# delimita os blocos basicos do programa
# todo alvo valido de desvio ou salto inicia um bloco
# toda instrucao valida logo apos desvio ou salto inicia um bloco
# todo desvio ou salto encerra um bloco, buraco de invalida tambem corta
# invalida nunca entra em bloco nenhum, nem abre nem fecha
def delimitar_blocos_basicos(lista_resultados):
    blocos = []
    total = len(lista_resultados)
    mapa = mapa_endereco_indice(lista_resultados)
    eh_inicio = {}
    indice = 0
    achou_primeiro = "nao"
    while indice < total:
        registro = lista_resultados[indice]
        if achou_primeiro == "nao":
            if registro["tipo"] != "invalida":
                eh_inicio[indice] = "sim"
                achou_primeiro = "sim"
        indice = indice + 1
    indice = 0
    while indice < total:
        registro = lista_resultados[indice]
        if registro["tipo"] == "B":
            alvo = calcular_alvo(registro)
            if alvo in mapa:
                destino = mapa[alvo]
                if lista_resultados[destino]["tipo"] != "invalida":
                    eh_inicio[destino] = "sim"
        else:
            if registro["tipo"] == "J":
                alvo = calcular_alvo(registro)
                if alvo in mapa:
                    destino = mapa[alvo]
                    if lista_resultados[destino]["tipo"] != "invalida":
                        eh_inicio[destino] = "sim"
        indice = indice + 1
    indice = 0
    while indice < total:
        registro = lista_resultados[indice]
        if eh_desvio_ou_salto(registro) == "sim":
            seguinte = indice + 1
            if seguinte < total:
                if lista_resultados[seguinte]["tipo"] != "invalida":
                    eh_inicio[seguinte] = "sim"
        indice = indice + 1
    validos = []
    indice = 0
    while indice < total:
        if lista_resultados[indice]["tipo"] != "invalida":
            validos.append(indice)
        indice = indice + 1
    numero = 1
    posicao_inicial = 0
    posicao = 0
    quantidade = len(validos)
    while posicao < quantidade:
        atual = validos[posicao]
        corta = "nao"
        if eh_desvio_ou_salto(lista_resultados[atual]) == "sim":
            corta = "sim"
        else:
            if posicao == quantidade - 1:
                corta = "sim"
            else:
                proximo = validos[posicao + 1]
                if proximo != atual + 1:
                    corta = "sim"
                else:
                    if proximo in eh_inicio:
                        corta = "sim"
        if corta == "sim":
            primeiro = validos[posicao_inicial]
            inicio_texto = lista_resultados[primeiro]["endereco_texto"]
            fim_texto = lista_resultados[atual]["endereco_texto"]
            tamanho = posicao - posicao_inicial + 1
            bloco = criar_bloco(numero, inicio_texto, fim_texto, tamanho)
            blocos.append(bloco)
            numero = numero + 1
            posicao_inicial = posicao + 1
        posicao = posicao + 1
    return blocos


# procura o produtor mais recente de um registrador antes de uma posicao limite
# devolve o indice do escritor ou o proprio limite quando ninguem escreveu
# invalida nunca escreve, zero nunca escreve, busca so ate antes do limite
def procurar_produtor_antes(lista_resultados, limite, registrador):
    achado = limite
    indice = 0
    while indice < limite:
        escrita = obter_escrita(lista_resultados[indice])
        if escrita == registrador:
            achado = indice
        indice = indice + 1
    return achado


# cria um registro de conflito de borda com produtor, consumidor e caminho
# caminho sequencial e o inicio sem desvio, caminho alvo e o destino do desvio
def criar_conflito_borda(produtor_texto, produtor_assembly, consumidor_texto, consumidor_assembly, registrador, distancia, nops, caminho):
    conflito = {}
    conflito["produtor"] = produtor_texto
    conflito["produtor_assembly"] = produtor_assembly
    conflito["consumidor"] = consumidor_texto
    conflito["consumidor_assembly"] = consumidor_assembly
    conflito["registrador"] = registrador
    conflito["distancia"] = distancia
    conflito["nops"] = nops
    conflito["caminho"] = caminho
    return conflito


# detecta conflitos de dados que atravessam a fronteira de cada desvio condicional
# para cada um dos dois caminhos olha a primeira instrucao do caminho
# caminho sequencial e a seguinte ao desvio, caminho alvo e a do destino
# produtor e sempre anterior ao desvio, consumidor e o inicio do caminho
# no caminho sequencial a distancia conta as posicoes na lista
# no caminho alvo a distancia soma um passo pelo slot, que sempre executa
# conflito so quando distancia e 1 (2 nops) ou 2 (1 nop), igual aos dados
# caminho sem instrucao e instrucao invalida nao geram conflito de borda
def detectar_conflitos_borda(lista_resultados):
    conflitos = []
    mapa = mapa_endereco_indice(lista_resultados)
    indice = 0
    total = len(lista_resultados)
    while indice < total:
        registro = lista_resultados[indice]
        if eh_desvio_condicional(registro) == "sim":
            seguinte = indice + 1
            if seguinte < total:
                consumidor = lista_resultados[seguinte]
                if consumidor["tipo"] != "invalida":
                    leituras = listar_leituras(consumidor)
                    contador = 0
                    while contador < len(leituras):
                        registrador = leituras[contador]
                        produtor = procurar_produtor_antes(lista_resultados, indice, registrador)
                        if produtor != indice:
                            distancia = seguinte - produtor
                            if distancia == 1:
                                nops = 2
                                origem = lista_resultados[produtor]
                                conflito = criar_conflito_borda(origem["endereco_texto"], origem["assembly"], consumidor["endereco_texto"], consumidor["assembly"], registrador, distancia, nops, "sequencial")
                                conflitos.append(conflito)
                            else:
                                if distancia == 2:
                                    nops = 1
                                    origem = lista_resultados[produtor]
                                    conflito = criar_conflito_borda(origem["endereco_texto"], origem["assembly"], consumidor["endereco_texto"], consumidor["assembly"], registrador, distancia, nops, "sequencial")
                                    conflitos.append(conflito)
                        contador = contador + 1
            alvo = calcular_alvo(registro)
            if alvo in mapa:
                destino = mapa[alvo]
                if lista_resultados[destino]["tipo"] != "invalida":
                    consumidor = lista_resultados[destino]
                    leituras = listar_leituras(consumidor)
                    contador = 0
                    while contador < len(leituras):
                        registrador = leituras[contador]
                        produtor = procurar_produtor_antes(lista_resultados, indice, registrador)
                        if produtor != indice:
                            distancia = indice - produtor + 1
                            if distancia == 1:
                                nops = 2
                                origem = lista_resultados[produtor]
                                conflito = criar_conflito_borda(origem["endereco_texto"], origem["assembly"], consumidor["endereco_texto"], consumidor["assembly"], registrador, distancia, nops, "alvo")
                                conflitos.append(conflito)
                            else:
                                if distancia == 2:
                                    nops = 1
                                    origem = lista_resultados[produtor]
                                    conflito = criar_conflito_borda(origem["endereco_texto"], origem["assembly"], consumidor["endereco_texto"], consumidor["assembly"], registrador, distancia, nops, "alvo")
                                    conflitos.append(conflito)
                        contador = contador + 1
        indice = indice + 1
    return conflitos


# mostra o controle no formato canonico em tres partes separadas dos dados
# primeiro cada desvio com seu slot, depois os blocos, depois as bordas
def mostrar_controle(lista_controle, lista_blocos, lista_borda):
    print("CONFLITOS DE CONTROLE")
    indice = 0
    total = len(lista_controle)
    while indice < total:
        conflito = lista_controle[indice]
        linha = "  " + conflito["desvio"] + " " + conflito["desvio_assembly"]
        linha = linha + " -> slot " + conflito["slot"] + " " + conflito["slot_assembly"]
        linha = linha + " [sempre executa]"
        print(linha)
        indice = indice + 1
    print("BLOCOS BASICOS")
    indice = 0
    total = len(lista_blocos)
    while indice < total:
        bloco = lista_blocos[indice]
        linha = "  bloco " + str(bloco["numero"]) + ": " + bloco["inicio"] + " .. " + bloco["fim"]
        if bloco["total"] == 1:
            linha = linha + " (1 instrucao)"
        else:
            linha = linha + " (" + str(bloco["total"]) + " instrucoes)"
        print(linha)
        indice = indice + 1
    print("CONFLITOS DE BORDA")
    indice = 0
    total = len(lista_borda)
    while indice < total:
        conflito = lista_borda[indice]
        linha = "  " + conflito["consumidor"] + " " + conflito["consumidor_assembly"]
        linha = linha + " <- " + conflito["produtor"] + " " + conflito["produtor_assembly"]
        linha = linha + " [" + conflito["registrador"] + ", d=" + str(conflito["distancia"]) + ", " + str(conflito["nops"]) + " nops"
        linha = linha + ", caminho=" + conflito["caminho"] + "]"
        print(linha)
        indice = indice + 1


# cria um registro de nop canonico igual ao addi zero,zero,0
# nop e o addi com destino zero, origem zero e imediato zero
# codigo de maquina 0x00000013, formato I, nunca le nem escreve de verdade
# endereco comeca zerado e e refeito depois, inserido marca que foi criado aqui
# endereco original fica negativo para mostrar que nao veio do arquivo
# bits guarda os 32 caracteres e hex guarda a linha pronta do arquivo
def criar_nop():
    nop = {}
    nop["tipo"] = "I"
    nop["formato"] = "I"
    nop["mnemonico"] = "addi"
    nop["rd"] = "zero"
    nop["rs1"] = "zero"
    nop["rs2"] = ""
    nop["imm"] = "0"
    nop["f3"] = "000"
    nop["f7"] = ""
    nop["assembly"] = "addi zero,zero,0"
    nop["pseudo"] = "nop"
    nop["endereco"] = 0
    nop["endereco_texto"] = ""
    nop["inserido"] = "sim"
    nop["movido"] = "nao"
    nop["endereco_original"] = 0 - 1
    nop["bits"] = "00000000000000000000000000010011"
    nop["hex"] = "0x00000013"
    return nop


# copia um registro campo a campo para nao mexer no original
# mantem todos os campos iguais, so marca que nao foi inserido
# quem nao tem a marca ainda ganha a marca de original
# endereco original guarda o endereco antigo para achar o alvo depois
# bits e hex viajam juntos quando ja existirem no original
def copiar_registro(registro):
    copia = {}
    copia["tipo"] = registro["tipo"]
    copia["formato"] = registro["formato"]
    copia["mnemonico"] = registro["mnemonico"]
    copia["rd"] = registro["rd"]
    copia["rs1"] = registro["rs1"]
    copia["rs2"] = registro["rs2"]
    copia["imm"] = registro["imm"]
    copia["f3"] = registro["f3"]
    copia["f7"] = registro["f7"]
    copia["assembly"] = registro["assembly"]
    copia["pseudo"] = registro["pseudo"]
    copia["endereco"] = registro["endereco"]
    copia["endereco_texto"] = registro["endereco_texto"]
    copia["inserido"] = "nao"
    if "movido" in registro:
        copia["movido"] = registro["movido"]
    else:
        copia["movido"] = "nao"
    if "endereco_original" in registro:
        copia["endereco_original"] = registro["endereco_original"]
    else:
        copia["endereco_original"] = registro["endereco"]
    if "bits" in registro:
        copia["bits"] = registro["bits"]
    else:
        copia["bits"] = ""
    if "hex" in registro:
        copia["hex"] = registro["hex"]
    else:
        copia["hex"] = ""
    return copia


# diz se o registro e o nop canonico addi zero,zero,0
# confere tipo, mnemonico, destino, origem e imediato juntos
# invalida nunca e nop, mesmo que algum campo esteja vazio
def eh_nop(registro):
    if registro["tipo"] != "I":
        return "nao"
    if registro["mnemonico"] != "addi":
        return "nao"
    if registro["rd"] != "zero":
        return "nao"
    if registro["rs1"] != "zero":
        return "nao"
    if registro["imm"] != "0":
        return "nao"
    return "sim"


# devolve quantos nops uma distancia exige pela regra 3 menos d
# distancia 1 pede 2 nops, distancia 2 pede 1 nop, resto pede zero
def calcular_nops_para_distancia(distancia):
    if distancia == 1:
        return 2
    if distancia == 2:
        return 1
    return 0


# descobre quantos nops faltam antes do consumidor na lista ja corrigida
# olha cada leitura e procura o produtor mais recente na lista corrigida
# distancia e a posicao atual menos a posicao do produtor
# quando ha duas leituras vale o maior numero de nops entre elas
# invalida nunca pede nop porque nunca tem leitura
def nops_necessarios_antes(lista_corrigida, registro, ultimo_produtor):
    maior = 0
    leituras = listar_leituras(registro)
    posicao_atual = len(lista_corrigida)
    contador = 0
    while contador < len(leituras):
        registrador = leituras[contador]
        if registrador in ultimo_produtor:
            posicao_produtor = ultimo_produtor[registrador]
            distancia = posicao_atual - posicao_produtor
            pedidos = calcular_nops_para_distancia(distancia)
            if pedidos > maior:
                maior = pedidos
        contador = contador + 1
    return maior


# corrige o programa so com nops sem mudar a ordem das originais
# percorre as originais em ordem e vai montando uma lista nova
# antes de cada instrucao insere os nops minimos que faltam para ela
# a distancia e medida na lista nova, que ja tem os nops e slots anteriores
# por isso o slot anterior ja ajuda a afastar o proximo consumidor
# logo apos cada desvio condicional insere um nop de slot que sempre executa
# invalida entra na lista mas nunca pede nop e nunca vira slot
# nop inserido nunca le nem escreve, so afasta produtor e consumidor
# no fim refaz todos os enderecos em ordem e reescreve desvios e saltos
# a reescrita mantem cada desvio e salto apontando para o mesmo alvo de antes
def corrigir_somente_nops(lista_resultados):
    corrigida = []
    ultimo_produtor = {}
    indice = 0
    total = len(lista_resultados)
    while indice < total:
        registro = lista_resultados[indice]
        pedidos = nops_necessarios_antes(corrigida, registro, ultimo_produtor)
        contador_nop = 0
        while contador_nop < pedidos:
            nop = criar_nop()
            corrigida.append(nop)
            contador_nop = contador_nop + 1
        copia = copiar_registro(registro)
        corrigida.append(copia)
        posicao_copia = len(corrigida) - 1
        escrita = obter_escrita(registro)
        if escrita != "":
            ultimo_produtor[escrita] = posicao_copia
        if eh_desvio_condicional(registro) == "sim":
            slot = criar_nop()
            corrigida.append(slot)
        indice = indice + 1
    atribuir_enderecos(corrigida)
    recalcular_desvios_e_saltos(lista_resultados, corrigida)
    return corrigida


# nome ABI para os 5 bits do registrador, ordem fixa de Engenharia
# serve para remontar a instrucao sem precisar de conta esperta
tabela_abi_para_bits = {
    "zero": "00000",
    "ra": "00001",
    "sp": "00010",
    "gp": "00011",
    "tp": "00100",
    "t0": "00101",
    "t1": "00110",
    "t2": "00111",
    "s0": "01000",
    "s1": "01001",
    "a0": "01010",
    "a1": "01011",
    "a2": "01100",
    "a3": "01101",
    "a4": "01110",
    "a5": "01111",
    "a6": "10000",
    "a7": "10001",
    "s2": "10010",
    "s3": "10011",
    "s4": "10100",
    "s5": "10101",
    "s6": "10110",
    "s7": "10111",
    "s8": "11000",
    "s9": "11001",
    "s10": "11010",
    "s11": "11011",
    "t3": "11100",
    "t4": "11101",
    "t5": "11110",
    "t6": "11111",
}


# cada grupo de 4 bits para o digito hexadecimal da linha de saida
# serve para escrever o arquivo corrigido no mesmo formato da entrada
tabela_nibble_para_hex = {
    "0000": "0",
    "0001": "1",
    "0010": "2",
    "0011": "3",
    "0100": "4",
    "0101": "5",
    "0110": "6",
    "0111": "7",
    "1000": "8",
    "1001": "9",
    "1010": "a",
    "1011": "b",
    "1100": "c",
    "1101": "d",
    "1110": "e",
    "1111": "f",
}


# devolve os 5 bits de um nome ABI ou vazio quando nao conhece
# nome desconhecido nao recodifica, a instrucao fica como estava
def abi_para_bits(nome):
    if nome in tabela_abi_para_bits:
        return tabela_abi_para_bits[nome]
    return ""


# calcula dois elevado ao expoente so com multiplicacao repetida
# exemplo expoente 4 devolve 16, expoente 0 devolve 1
def potencia_de_dois(expoente):
    resultado = 1
    contador = 0
    while contador < expoente:
        resultado = resultado * 2
        contador = contador + 1
    return resultado


# converte deslocamento decimal em texto binario com largura fixa
# usa complemento de dois para negativo somando dois elevado a largura
# positivo completa com zeros a esquerda ate a largura
# quando passa da largura fica so com os ultimos bits da direita
# exemplo valor 12 largura 13 vira 0000000001100, valor 0 menos 12 vira 111111110100
def decimal_para_binario_largura(valor, largura):
    positivo = valor
    if valor < 0:
        potencia = potencia_de_dois(largura)
        positivo = valor + potencia
    texto = format(positivo, "b")
    while len(texto) < largura:
        texto = "0" + texto
    if len(texto) > largura:
        inicio = len(texto) - largura
        fim = len(texto)
        texto = texto[inicio:fim]
    return texto


# converte 32 caracteres binarios em linha hexadecimal com prefixo 0x
# recorta de 4 em 4 e troca cada pedaco pelo digito da tabela
# exemplo 32 zeros vira 0x00000000
def bits_para_hex_linha(bits):
    resultado = "0x"
    indice = 0
    while indice < 32:
        fim = indice + 4
        pedaco = bits[indice:fim]
        if pedaco in tabela_nibble_para_hex:
            digito = tabela_nibble_para_hex[pedaco]
            resultado = resultado + digito
        else:
            resultado = resultado + "0"
        indice = indice + 4
    return resultado


# monta os 32 bits de um desvio condicional com deslocamento novo
# deslocamento tem 13 bits com o zero final, recortado por fatiamento
# ordem arquitetural por concatenacao de texto sem conta esperta
# devolve os 32 caracteres prontos para gravar e decodificar de volta
def montar_bits_b(rs1_bits, rs2_bits, f3, deslocamento):
    cheio = decimal_para_binario_largura(deslocamento, 13)
    pedaco_12 = cheio[0:1]
    pedaco_11 = cheio[1:2]
    pedaco_10_5 = cheio[2:8]
    pedaco_4_1 = cheio[8:12]
    opcode = "1100011"
    bits = pedaco_12 + pedaco_10_5 + rs2_bits + rs1_bits + f3 + pedaco_4_1 + pedaco_11 + opcode
    return bits


# monta os 32 bits de um jal com deslocamento novo
# deslocamento tem 21 bits com o zero final, recortado por fatiamento
# ordem arquitetural por concatenacao de texto sem conta esperta
# devolve os 32 caracteres prontos para gravar e decodificar de volta
def montar_bits_j(rd_bits, deslocamento):
    cheio = decimal_para_binario_largura(deslocamento, 21)
    pedaco_20 = cheio[0:1]
    pedaco_19_12 = cheio[1:9]
    pedaco_11 = cheio[9:10]
    pedaco_10_1 = cheio[10:20]
    opcode = "1101111"
    bits = pedaco_20 + pedaco_10_1 + pedaco_11 + pedaco_19_12 + rd_bits + opcode
    return bits


# reescreve um desvio ou salto com o deslocamento novo em linguagem de maquina
# atualiza imediato em decimal, assembly, bits e linha hexadecimal juntos
# jal com destino zero ganha o pseudo de salto simples, resto fica sem pseudo
# desvio condicional mantem pseudo vazio como na decodificacao da M1
# tipo que nao e B nem J nao muda nada e devolve texto vazio
def recodificar_com_novo_deslocamento(registro, novo_deslocamento):
    if registro["tipo"] == "B":
        rs1_bits = abi_para_bits(registro["rs1"])
        if rs1_bits == "":
            return ""
        rs2_bits = abi_para_bits(registro["rs2"])
        if rs2_bits == "":
            return ""
        f3 = registro["f3"]
        if f3 == "":
            return ""
        bits = montar_bits_b(rs1_bits, rs2_bits, f3, novo_deslocamento)
        texto_deslocamento = str(novo_deslocamento)
        registro["imm"] = texto_deslocamento
        registro["assembly"] = registro["mnemonico"] + " " + registro["rs1"] + "," + registro["rs2"] + "," + texto_deslocamento
        registro["bits"] = bits
        registro["hex"] = bits_para_hex_linha(bits)
        return bits
    if registro["tipo"] == "J":
        rd_bits = abi_para_bits(registro["rd"])
        if rd_bits == "":
            return ""
        bits = montar_bits_j(rd_bits, novo_deslocamento)
        texto_deslocamento = str(novo_deslocamento)
        registro["imm"] = texto_deslocamento
        registro["assembly"] = registro["mnemonico"] + " " + registro["rd"] + "," + texto_deslocamento
        if registro["rd"] == "zero":
            registro["pseudo"] = "j " + texto_deslocamento
        else:
            registro["pseudo"] = ""
        registro["bits"] = bits
        registro["hex"] = bits_para_hex_linha(bits)
        return bits
    return ""


# refaz enderecos em ordem e reescreve cada desvio e salto para o mesmo alvo
# primeiro refaz todos os enderecos antes de qualquer conta de deslocamento
# alvo antigo e endereco antigo mais imediato antigo da instrucao original
# alvo dentro do programa segue a instrucao que tem o mesmo endereco original
# alvo fora do programa segue o mesmo endereco absoluto de antes
# deslocamento novo e alvo novo menos endereco novo de quem desvia ou salta
# jal por registrador nunca entra aqui porque o destino e desconhecido
# invalida nunca entra, inserido nunca e desvio
def recalcular_desvios_e_saltos(lista_original, lista_corrigida):
    atribuir_enderecos(lista_corrigida)
    mapa_antigo = mapa_endereco_indice(lista_original)
    mapa_novo = {}
    indice = 0
    total = len(lista_corrigida)
    while indice < total:
        registro = lista_corrigida[indice]
        if registro["inserido"] == "nao":
            if "endereco_original" in registro:
                origem = registro["endereco_original"]
                mapa_novo[origem] = indice
        indice = indice + 1
    indice = 0
    while indice < total:
        registro = lista_corrigida[indice]
        if registro["tipo"] == "B":
            if registro["inserido"] == "nao":
                if "endereco_original" in registro:
                    origem_antiga = registro["endereco_original"]
                    if origem_antiga in mapa_antigo:
                        posicao_antiga = mapa_antigo[origem_antiga]
                        antigo = lista_original[posicao_antiga]
                        if antigo["imm"] != "":
                            desloc_antigo = int(antigo["imm"])
                            alvo_antigo = antigo["endereco"] + desloc_antigo
                            if alvo_antigo in mapa_antigo:
                                if alvo_antigo in mapa_novo:
                                    posicao_alvo_nova = mapa_novo[alvo_antigo]
                                    endereco_alvo_novo = lista_corrigida[posicao_alvo_nova]["endereco"]
                                    novo_deslocamento = endereco_alvo_novo - registro["endereco"]
                                    recodificar_com_novo_deslocamento(registro, novo_deslocamento)
                            else:
                                novo_deslocamento = alvo_antigo - registro["endereco"]
                                recodificar_com_novo_deslocamento(registro, novo_deslocamento)
        else:
            if registro["tipo"] == "J":
                if registro["inserido"] == "nao":
                    if "endereco_original" in registro:
                        origem_antiga = registro["endereco_original"]
                        if origem_antiga in mapa_antigo:
                            posicao_antiga = mapa_antigo[origem_antiga]
                            antigo = lista_original[posicao_antiga]
                            if antigo["imm"] != "":
                                desloc_antigo = int(antigo["imm"])
                                alvo_antigo = antigo["endereco"] + desloc_antigo
                                if alvo_antigo in mapa_antigo:
                                    if alvo_antigo in mapa_novo:
                                        posicao_alvo_nova = mapa_novo[alvo_antigo]
                                        endereco_alvo_novo = lista_corrigida[posicao_alvo_nova]["endereco"]
                                        novo_deslocamento = endereco_alvo_novo - registro["endereco"]
                                        recodificar_com_novo_deslocamento(registro, novo_deslocamento)
                                else:
                                    novo_deslocamento = alvo_antigo - registro["endereco"]
                                    recodificar_com_novo_deslocamento(registro, novo_deslocamento)
        indice = indice + 1
    return lista_corrigida


# diz se o registro e um acesso a memoria que pode se sobrepor a outro
# carga e armazenamento sao os unicos acessos, resto nunca e memoria
# invalida nunca e acesso, mesmo que algum campo pareca endereco
def eh_acesso_memoria(registro):
    if registro["tipo"] == "invalida":
        return "nao"
    if registro["tipo"] == "load":
        return "sim"
    if registro["tipo"] == "S":
        return "sim"
    return "nao"


# devolve o registrador base do acesso a memoria ou vazio quando nao e acesso
# carga e armazenamento usam rs1 como base e imm como deslocamento
def obter_base_memoria(registro):
    if registro["tipo"] == "load":
        return registro["rs1"]
    if registro["tipo"] == "S":
        return registro["rs1"]
    return ""


# devolve o deslocamento decimal do acesso a memoria ou vazio quando nao e acesso
# texto igual ao campo imm, comparado como texto para nao precisar de conta
def obter_deslocamento_memoria(registro):
    if registro["tipo"] == "load":
        return registro["imm"]
    if registro["tipo"] == "S":
        return registro["imm"]
    return ""


# diz se dois acessos a memoria podem se sobrepor e nao podem trocar de ordem
# quem nao e memoria nunca se sobrepoe por este criterio
# base diferente e endereco desconhecido, entao preserva a ordem por prudencia
# mesma base com mesmo deslocamento e o mesmo endereco, preserva a ordem
# mesma base com deslocamentos diferentes sao enderecos distintos, pode trocar
# deslocamento vazio tambem preserva, porque nao da para mostrar que e distinto
def acessos_podem_sobrepor(primeiro, segundo):
    if eh_acesso_memoria(primeiro) == "nao":
        return "nao"
    if eh_acesso_memoria(segundo) == "nao":
        return "nao"
    base_primeiro = obter_base_memoria(primeiro)
    base_segundo = obter_base_memoria(segundo)
    if base_primeiro == "":
        return "sim"
    if base_segundo == "":
        return "sim"
    if base_primeiro != base_segundo:
        return "sim"
    desloc_primeiro = obter_deslocamento_memoria(primeiro)
    desloc_segundo = obter_deslocamento_memoria(segundo)
    if desloc_primeiro == "":
        return "sim"
    if desloc_segundo == "":
        return "sim"
    if desloc_primeiro == desloc_segundo:
        return "sim"
    return "nao"


# diz se trocar a ordem de dois registros muda o resultado do programa
# leitura apos escrita, escrita apos leitura e escrita apos escrita bloqueiam
# dois acessos a memoria que podem se sobrepor tambem bloqueiam
# invalida nunca bloqueia, zero nunca aparece porque leitura e escrita ignoram zero
# a verificacao vale nos dois sentidos porque a troca inverte os dois juntos
def tem_conflito_ordenacao(primeiro, segundo):
    if primeiro["tipo"] == "invalida":
        return "nao"
    if segundo["tipo"] == "invalida":
        return "nao"
    escrita_primeiro = obter_escrita(primeiro)
    escrita_segundo = obter_escrita(segundo)
    if escrita_primeiro != "":
        if escrita_primeiro == escrita_segundo:
            return "sim"
    leituras_primeiro = listar_leituras(primeiro)
    leituras_segundo = listar_leituras(segundo)
    if escrita_primeiro != "":
        contador = 0
        while contador < len(leituras_segundo):
            if leituras_segundo[contador] == escrita_primeiro:
                return "sim"
            contador = contador + 1
    if escrita_segundo != "":
        contador = 0
        while contador < len(leituras_primeiro):
            if leituras_primeiro[contador] == escrita_segundo:
                return "sim"
            contador = contador + 1
    if acessos_podem_sobrepor(primeiro, segundo) == "sim":
        return "sim"
    return "nao"


# diz se a candidata pode passar para depois do desvio sem quebrar a condicao
# candidata que escreve registrador lido pelo desvio mudaria o caminho tomado
# desvio nunca escreve, entao so este sentido precisa de verificacao
# devolve sim quando e seguro e nao quando quebraria o desvio
def candidata_segura_contra_desvio(candidata, desvio):
    escrita = obter_escrita(candidata)
    if escrita == "":
        return "sim"
    leituras = listar_leituras(desvio)
    contador = 0
    while contador < len(leituras):
        if leituras[contador] == escrita:
            return "nao"
        contador = contador + 1
    return "sim"


# monta o mapa de inicio de bloco para a lista de trabalho atual
# repete as tres regras da delimitacao sem montar os blocos de saida
# primeira valida abre, alvo valido de desvio ou salto abre, apos desvio abre
# devolve o dicionario de posicao para sim para consulta da reordenacao
def construir_inicios_bloco(lista_trabalho):
    inicios = {}
    total = len(lista_trabalho)
    mapa = mapa_endereco_indice(lista_trabalho)
    indice = 0
    achou_primeiro = "nao"
    while indice < total:
        registro = lista_trabalho[indice]
        if achou_primeiro == "nao":
            if registro["tipo"] != "invalida":
                inicios[indice] = "sim"
                achou_primeiro = "sim"
        indice = indice + 1
    indice = 0
    while indice < total:
        registro = lista_trabalho[indice]
        if registro["tipo"] == "B":
            alvo = calcular_alvo(registro)
            if alvo in mapa:
                destino = mapa[alvo]
                if lista_trabalho[destino]["tipo"] != "invalida":
                    inicios[destino] = "sim"
        else:
            if registro["tipo"] == "J":
                alvo = calcular_alvo(registro)
                if alvo in mapa:
                    destino = mapa[alvo]
                    if lista_trabalho[destino]["tipo"] != "invalida":
                        inicios[destino] = "sim"
        indice = indice + 1
    indice = 0
    while indice < total:
        registro = lista_trabalho[indice]
        if eh_desvio_ou_salto(registro) == "sim":
            seguinte = indice + 1
            if seguinte < total:
                if lista_trabalho[seguinte]["tipo"] != "invalida":
                    inicios[seguinte] = "sim"
        indice = indice + 1
    return inicios


# acha o inicio do bloco basico que contem o desvio na lista de trabalho
# comeca no proprio desvio e anda para tras ate a fronteira do bloco
# fronteira e invalida, desvio ou salto anterior, ou proxima posicao marcada
# desvio que abre o proprio bloco nao tem candidata, devolve a propria posicao
def indice_inicio_bloco_de(lista_trabalho, inicios, pos_desvio):
    inicio = pos_desvio
    anterior = pos_desvio - 1
    while anterior > 0 - 1:
        registro = lista_trabalho[anterior]
        if registro["tipo"] == "invalida":
            return inicio
        if eh_desvio_ou_salto(registro) == "sim":
            return inicio
        depois = anterior + 1
        if depois in inicios:
            return inicio
        inicio = anterior
        anterior = anterior - 1
    return inicio


# acha a primeira instrucao valida depois do desvio na lista de trabalho
# e o caminho sequencial que segue o slot na execucao sem desvio
# devolve a posicao ou negativo quando nao ha sucessor valido
def proximo_valido_depois(lista_trabalho, pos_desvio):
    seguinte = pos_desvio + 1
    total = len(lista_trabalho)
    while seguinte < total:
        if lista_trabalho[seguinte]["tipo"] != "invalida":
            return seguinte
        seguinte = seguinte + 1
    return 0 - 1


# procura a instrucao original pelo endereco para achar o alvo do desvio
# devolve a posicao na lista original ou negativo quando nao existe
def procurar_posicao_por_endereco(lista_original, endereco):
    indice = 0
    total = len(lista_original)
    while indice < total:
        if lista_original[indice]["endereco"] == endereco:
            return indice
        indice = indice + 1
    return 0 - 1


# busca a candidata ao slot vinda de antes do desvio dentro do mesmo bloco
# comeca na mais proxima do desvio e anda para tras ate o inicio do bloco
# desvio, salto, invalida e nop nunca sao candidatos e sao pulados
# candidata nao pode ter conflito de ordem com nenhuma intermediaria pulada
# candidata nao pode escrever o que o desvio le, senao muda o caminho
# candidata nao pode escrever o que o sucessor imediato de cada caminho le
# o caminho sequencial e lido na lista de trabalho e o alvo na lista original
# os campos nunca mudam na reordenacao, so a ordem muda, entao vale comparar
# sucessor que le o escrito da candidata e rejeitado aqui de proposito
# no sequencial o conflito seria corrigivel com nops depois do slot
# mas cada slot util precisa economizar de verdade contra a tecnica so com nops
# por isso so vale a candidata que nao cria conflito novo na saida do bloco
# no alvo nao ha como corrigir depois, entao a rejeicao garante os dois caminhos
# devolve a posicao da primeira candidata segura ou negativo sem candidata
def buscar_candidata_ao_slot(lista_trabalho, lista_original, pos_desvio, inicio):
    desvio = lista_trabalho[pos_desvio]
    pos_sequencial = proximo_valido_depois(lista_trabalho, pos_desvio)
    tem_alvo = "nao"
    leituras_alvo = []
    pos_origem = procurar_posicao_por_endereco(lista_original, desvio["endereco_original"])
    if pos_origem != 0 - 1:
        origem = lista_original[pos_origem]
        alvo = calcular_alvo(origem)
        pos_alvo = procurar_posicao_por_endereco(lista_original, alvo)
        if pos_alvo != 0 - 1:
            destino = lista_original[pos_alvo]
            if destino["tipo"] != "invalida":
                tem_alvo = "sim"
                leituras_alvo = listar_leituras(destino)
    candidato = pos_desvio - 1
    while candidato > inicio - 1:
        atual = lista_trabalho[candidato]
        if atual["tipo"] == "invalida":
            candidato = candidato - 1
        else:
            if eh_desvio_ou_salto(atual) == "sim":
                candidato = candidato - 1
            else:
                if eh_nop(atual) == "sim":
                    candidato = candidato - 1
                else:
                    segura = "sim"
                    intermediario = candidato + 1
                    while intermediario < pos_desvio:
                        vizinho = lista_trabalho[intermediario]
                        if vizinho["tipo"] != "invalida":
                            if tem_conflito_ordenacao(atual, vizinho) == "sim":
                                segura = "nao"
                        intermediario = intermediario + 1
                    if segura == "sim":
                        if candidata_segura_contra_desvio(atual, desvio) == "nao":
                            segura = "nao"
                    if segura == "sim":
                        escrita = obter_escrita(atual)
                        if escrita != "":
                            if pos_sequencial != 0 - 1:
                                sequencial = lista_trabalho[pos_sequencial]
                                leituras = listar_leituras(sequencial)
                                contador = 0
                                while contador < len(leituras):
                                    if leituras[contador] == escrita:
                                        segura = "nao"
                                    contador = contador + 1
                            if segura == "sim":
                                if tem_alvo == "sim":
                                    contador = 0
                                    while contador < len(leituras_alvo):
                                        if leituras_alvo[contador] == escrita:
                                            segura = "nao"
                                        contador = contador + 1
                    if segura == "sim":
                        return candidato
                    candidato = candidato - 1
    return 0 - 1


# move a candidata de antes do desvio para o slot logo depois do desvio
# retira da posicao antiga e insere colada no desvio na lista de trabalho
# marca a movida para a listagem futura saber o que foi reordenado
# a candidata fica entre o desvio e o caminho sequencial nos dois caminhos
def mover_para_slot(lista_trabalho, pos_candidata, pos_desvio):
    guarda = lista_trabalho[pos_candidata]
    guarda["movido"] = "sim"
    temporaria = []
    indice = 0
    total = len(lista_trabalho)
    while indice < total:
        if indice != pos_candidata:
            temporaria.append(lista_trabalho[indice])
        indice = indice + 1
    pos_desvio_nova = pos_desvio - 1
    nova = []
    indice = 0
    total = len(temporaria)
    while indice < total:
        nova.append(temporaria[indice])
        if indice == pos_desvio_nova:
            nova.append(guarda)
        indice = indice + 1
    return nova


# corrige com reordenacao preenchendo cada slot com instrucao util
# primeiro reordena a copia de trabalho movendo candidatas para os slots
# cada desvio procura de novo porque a lista muda a cada movimento
# depois percorre o trabalho inserindo nops minimos sem quebrar o slot
# slot util entra colado no desvio e conta como produtor para o seguinte
# quando o slot precisaria de nops antes, os nops entram antes do desvio
# assim o slot continua colado e a distancia do produtor aumenta sem erro
# desvio sem candidata ganha nop de slot igual a tecnica so com nops
# no fim refaz enderecos e reescreve desvios e saltos para o mesmo alvo
def corrigir_com_reordenacao(lista_resultados):
    trabalho = []
    indice = 0
    total = len(lista_resultados)
    while indice < total:
        copia = copiar_registro(lista_resultados[indice])
        copia["movido"] = "nao"
        trabalho.append(copia)
        indice = indice + 1
    ramos = []
    indice = 0
    total = len(trabalho)
    while indice < total:
        if eh_desvio_condicional(trabalho[indice]) == "sim":
            ramos.append(trabalho[indice]["endereco_original"])
        indice = indice + 1
    pos_ramo = 0
    total_ramos = len(ramos)
    while pos_ramo < total_ramos:
        endereco_ramo = ramos[pos_ramo]
        pos_desvio = 0 - 1
        indice = 0
        total_trabalho = len(trabalho)
        while indice < total_trabalho:
            registro = trabalho[indice]
            if registro["endereco_original"] == endereco_ramo:
                if eh_desvio_condicional(registro) == "sim":
                    pos_desvio = indice
            indice = indice + 1
        if pos_desvio != 0 - 1:
            inicios = construir_inicios_bloco(trabalho)
            inicio = indice_inicio_bloco_de(trabalho, inicios, pos_desvio)
            candidata = buscar_candidata_ao_slot(trabalho, lista_resultados, pos_desvio, inicio)
            if candidata != 0 - 1:
                trabalho = mover_para_slot(trabalho, candidata, pos_desvio)
        pos_ramo = pos_ramo + 1
    corrigida = []
    ultimo_produtor = {}
    chaves_produtor = []
    passo = 0
    total_trabalho = len(trabalho)
    while passo < total_trabalho:
        atual = trabalho[passo]
        eh_slot_util = "nao"
        if passo > 0:
            anterior = trabalho[passo - 1]
            if eh_desvio_condicional(anterior) == "sim":
                if atual["movido"] == "sim":
                    eh_slot_util = "sim"
        if eh_slot_util == "sim":
            pedidos = nops_necessarios_antes(corrigida, atual, ultimo_produtor)
            if pedidos > 0:
                pos_desvio_nova = len(corrigida) - 1
                nova_corrigida = []
                indice = 0
                total_corr = len(corrigida)
                while indice < total_corr:
                    if indice == pos_desvio_nova:
                        contador_nop = 0
                        while contador_nop < pedidos:
                            nop = criar_nop()
                            nova_corrigida.append(nop)
                            contador_nop = contador_nop + 1
                    nova_corrigida.append(corrigida[indice])
                    indice = indice + 1
                corrigida = nova_corrigida
                contador_chave = 0
                while contador_chave < len(chaves_produtor):
                    chave = chaves_produtor[contador_chave]
                    posicao_antiga = ultimo_produtor[chave]
                    if posicao_antiga > pos_desvio_nova - 1:
                        ultimo_produtor[chave] = posicao_antiga + pedidos
                    contador_chave = contador_chave + 1
            copia = copiar_registro(atual)
            corrigida.append(copia)
            posicao_copia = len(corrigida) - 1
            escrita = obter_escrita(atual)
            if escrita != "":
                if escrita in ultimo_produtor:
                    ultimo_produtor[escrita] = posicao_copia
                else:
                    chaves_produtor.append(escrita)
                    ultimo_produtor[escrita] = posicao_copia
        else:
            pedidos = nops_necessarios_antes(corrigida, atual, ultimo_produtor)
            contador_nop = 0
            while contador_nop < pedidos:
                nop = criar_nop()
                corrigida.append(nop)
                contador_nop = contador_nop + 1
            copia = copiar_registro(atual)
            corrigida.append(copia)
            posicao_copia = len(corrigida) - 1
            escrita = obter_escrita(atual)
            if escrita != "":
                if escrita in ultimo_produtor:
                    ultimo_produtor[escrita] = posicao_copia
                else:
                    chaves_produtor.append(escrita)
                    ultimo_produtor[escrita] = posicao_copia
            if eh_desvio_condicional(atual) == "sim":
                proximo_util = "nao"
                seguinte = passo + 1
                if seguinte < total_trabalho:
                    proximo = trabalho[seguinte]
                    if proximo["movido"] == "sim":
                        proximo_util = "sim"
                if proximo_util == "nao":
                    slot = criar_nop()
                    corrigida.append(slot)
        passo = passo + 1
    atribuir_enderecos(corrigida)
    recalcular_desvios_e_saltos(lista_resultados, corrigida)
    return corrigida


# descobre se o arquivo de entrada usa hexadecimal ou binario
# le linha por linha pulando vazia e comentario como na M1
# primeira linha util com 0x ou 0X e hex, senao e bin
# arquivo vazio ou so com comentario devolve hex como padrao
def descobrir_estilo_entrada(caminho):
    estilo = "hex"
    achou = "nao"
    arquivo = open(caminho)
    for linha in arquivo:
        arrumada = linha.strip()
        if arrumada != "":
            if arrumada[0:1] != "#":
                if achou == "nao":
                    achou = "sim"
                    if arrumada[0:2] == "0x":
                        estilo = "hex"
                    else:
                        if arrumada[0:2] == "0X":
                            estilo = "hex"
                        else:
                            estilo = "bin"
    arquivo.close()
    return estilo


# gera o nome do arquivo de saida a partir do nome de entrada
# insere o sufixo antes do ultimo ponto da extensao
# exemplo entrada.txt com _nops vira entrada_nops.txt
# sem ponto so cola o sufixo no fim
def gerar_nome_saida(caminho, sufixo):
    posicao_ponto = 0 - 1
    indice = 0
    total = len(caminho)
    while indice < total:
        pedaco = caminho[indice:indice + 1]
        if pedaco == ".":
            posicao_ponto = indice
        indice = indice + 1
    if posicao_ponto == 0 - 1:
        return caminho + sufixo
    comeco = caminho[0:posicao_ponto]
    fim = caminho[posicao_ponto:total]
    return comeco + sufixo + fim


# devolve a linha pronta para o arquivo corrigido no mesmo formato da entrada
# estilo hex usa a linha com 0x, estilo bin usa os 32 caracteres
# invalida sem codigo vira zeros para continuar invalida e legivel de volta
# zeros com opcode desconhecido decodificam como invalida na M1
def linha_para_arquivo(registro, estilo):
    if estilo == "hex":
        if registro["hex"] != "":
            return registro["hex"]
        if registro["bits"] != "":
            return bits_para_hex_linha(registro["bits"])
        return "0x00000000"
    if registro["bits"] != "":
        return registro["bits"]
    return "00000000000000000000000000000000"


# escreve a lista corrigida num arquivo novo no mesmo formato da entrada
# uma instrucao por linha, mesmo estilo de prefixo da entrada
# devolve o caminho escrito para o fluxo mostrar depois
def escrever_arquivo_corrigido(caminho_saida, lista_corrigida, estilo):
    arquivo = open(caminho_saida, "w")
    indice = 0
    total = len(lista_corrigida)
    while indice < total:
        registro = lista_corrigida[indice]
        linha = linha_para_arquivo(registro, estilo)
        arquivo.write(linha + "\n")
        indice = indice + 1
    arquivo.close()
    return caminho_saida


# monta uma linha da listagem legivel com endereco, codigo e desmontada
# marca nop criado aqui com nop inserido e movida com movido para slot
# invalida mostra so a marca canonica para nao inventar assembly
def montar_linha_listagem(registro):
    endereco = registro["endereco_texto"]
    if endereco == "":
        endereco = "0x????????"
    codigo = registro["hex"]
    if codigo == "":
        if registro["bits"] != "":
            codigo = bits_para_hex_linha(registro["bits"])
        else:
            codigo = "0x00000000"
    if registro["tipo"] == "invalida":
        return "  " + endereco + " " + codigo + " instrucao invalida"
    linha = "  " + endereco + " " + codigo + " " + registro["assembly"]
    if registro["inserido"] == "sim":
        linha = linha + " [nop inserido]"
    else:
        if registro["movido"] == "sim":
            linha = linha + " [movido para slot]"
    return linha


# mostra a listagem legivel de um programa corrigido no console
# titulo diz a tecnica e cada linha tem endereco, codigo e marcacao
def mostrar_listagem(titulo, lista_corrigida):
    print(titulo)
    indice = 0
    total = len(lista_corrigida)
    while indice < total:
        registro = lista_corrigida[indice]
        print(montar_linha_listagem(registro))
        indice = indice + 1


# excecao pontual a regra de simplicidade: usa divisao (/) so aqui
# para o percentual de acrescimo com uma casa decimal, como o cpi
# o resto do arquivo continua so com aritmetica simples
# devolve o texto com virgula, exemplo 75,0% e 16,7%
# arredonda a segunda casa olhando o resto da divisao por mil
def formatar_percentual_uma_casa(acrescentadas, original):
    if original == 0:
        return "0,0%"
    numerador = acrescentadas * 1000
    quociente = numerador / original
    parte = int(quociente)
    resto = quociente - parte
    if resto < 0.5:
        parte = parte
    else:
        parte = parte + 1
    inteiro = 0
    decimo = parte
    while decimo > 9:
        decimo = decimo - 10
        inteiro = inteiro + 1
    return str(inteiro) + "," + str(decimo) + "%"


# mostra o relatorio de custo no formato canonico do exemplo
# original e o tamanho da entrada, finais sao os tamanhos corrigidos
# acrescentadas e final menos original, percentual com uma casa
# compara as duas tecnicas lado a lado em tres linhas
def mostrar_custo(total_original, total_nops, total_reord):
    print("CUSTO")
    print("  original .............. " + str(total_original) + " instrucoes")
    acrescentadas_nops = total_nops - total_original
    percentual_nops = formatar_percentual_uma_casa(acrescentadas_nops, total_original)
    print("  somente nops .......... " + str(total_nops) + " instrucoes  (+" + str(acrescentadas_nops) + ", +" + percentual_nops + ")")
    acrescentadas_reord = total_reord - total_original
    percentual_reord = formatar_percentual_uma_casa(acrescentadas_reord, total_original)
    print("  nops + reordenacao .... " + str(total_reord) + " instrucoes  (+" + str(acrescentadas_reord) + ", +" + percentual_reord + ")")

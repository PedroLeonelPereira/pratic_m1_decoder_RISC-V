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

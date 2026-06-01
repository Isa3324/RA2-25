import json
import os


def lerArvoreJson(caminho="output/arvore_sintatica.json"):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvarTabelaSimbolosJson(tabela, erros, caminho="output/tabela_simbolos.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    dados = {
        "tabela_simbolos": tabela,
        "erros_semanticos": erros
    }

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def tokensDoNo(no):
    """
    Retorna todos os tokens folha de um nó da árvore.
    Converte listas vindas do JSON novamente para tuplas.
    """

    tokens = []

    if no.get("token") is not None:
        tokens.append(tuple(no["token"]))

    for filho in no.get("filhos", []):
        tokens.extend(tokensDoNo(filho))

    return tokens


def coletarComandosPrincipais(arvore):
    """
    Coleta apenas os comandos diretamente presentes na lista de comandos
    do programa, preservando a ordem das linhas.
    """

    comandos = []

    def percorrerLista(no):
        for filho in no.get("filhos", []):
            if filho["simbolo"] == "comando":
                comandos.append(filho)

            elif filho["simbolo"] == "lista_comandos":
                percorrerLista(filho)

    for filho in arvore.get("filhos", []):
        if filho["simbolo"] == "lista_comandos":
            percorrerLista(filho)

    return comandos

def separarElementos(tokens_comando):
    """
    Recebe os tokens completos de um comando, por exemplo:
    EPAR MEM MEM DPAR

    Retorna apenas os elementos internos, agrupando comandos aninhados.
    """

    internos = tokens_comando[1:-1]
    elementos = []
    i = 0

    while i < len(internos):
        token = internos[i]

        if token[0] == "EPAR":
            profundidade = 1
            inicio = i
            i += 1

            while i < len(internos) and profundidade > 0:
                if internos[i][0] == "EPAR":
                    profundidade += 1

                elif internos[i][0] == "DPAR":
                    profundidade -= 1

                i += 1

            elementos.append(internos[inicio:i])

        else:
            elementos.append(token)
            i += 1

    return elementos


def linhaDoToken(token, linha_padrao="?"):
    if len(token) >= 4:
        return token[3]

    return linha_padrao


def elementoEhToken(elemento, tipo):
    return isinstance(elemento, tuple) and elemento[0] == tipo


def elementoEhComandoAninhado(elemento):
    return isinstance(elemento, list)


def registrarDefinicao(
    tabela,
    nome_variavel,
    linha,
    erros=None,
    contexto_controle=None
):
    """
    Registra a primeira definição ou uma reatribuição de variável.

    Regras:
    - Toda variável MEM possui tipo real.
    - Variável nova não pode ser criada pela primeira vez dentro de se/enquanto.
    - Variável já existente pode ser reatribuída dentro de se/enquanto.
    """

    # Primeira definição da variável
    if nome_variavel not in tabela:
        if contexto_controle is not None:
            if erros is not None:
                erros.append(
                    f"Erro semântico na linha {linha}: "
                    f"a variável {nome_variavel} não pode ser definida pela primeira vez "
                    f"dentro de {contexto_controle}. "
                    f"Defina a variável antes da estrutura de controle."
                )

            return False

        tabela[nome_variavel] = {
            "identificador": nome_variavel,
            "tipo": "real",
            "linha_definicao": linha,
            "linhas_atribuicao": [linha],
            "linha_ultima_atribuicao": linha,
            "linhas_uso": [],
            "linha_ultimo_uso": None
        }

        return True

    # Reatribuição de variável já existente
    tabela[nome_variavel]["linhas_atribuicao"].append(linha)
    tabela[nome_variavel]["linha_ultima_atribuicao"] = linha

    return True


def registrarUso(tabela, erros, token_variavel, linha):
    nome_variavel = token_variavel[1]

    if nome_variavel not in tabela:
        erros.append(
            f"Erro semântico na linha {linha}: "
            f"variável {nome_variavel} utilizada antes de sua definição."
        )
        return False

    tabela[nome_variavel]["linhas_uso"].append(linha)
    tabela[nome_variavel]["linha_ultimo_uso"] = linha

    return True

def analisarUsosEmElemento(elemento, tabela, erros, linha):
    """
    Analisa um elemento que está sendo usado como valor ou operando.
    Não registra definição.
    """

    if elementoEhToken(elemento, "NUM"):
        return

    if elementoEhToken(elemento, "MEM"):
        registrarUso(tabela, erros, elemento, linha)
        return

    if elementoEhComandoAninhado(elemento):
        elementos_internos = separarElementos(elemento)
        analisarComandoInterno(elementos_internos, tabela, erros, linha)


def analisarComandoInterno(elementos, tabela, erros, linha):
    """
    Analisa comandos usados dentro de outros comandos.
    Nesta etapa, serve para detectar uso de variável não definida.
    """

    if len(elementos) == 1:
        if elementoEhToken(elementos[0], "MEM"):
            registrarUso(tabela, erros, elementos[0], linha)
        return

    if len(elementos) == 2:
        primeiro = elementos[0]
        segundo = elementos[1]

        # Comando RES será validado de forma específica depois.
        if elementoEhToken(segundo, "RES"):
            return

        # Atribuição dentro de expressão aninhada:
        # analisa a origem e registra destino apenas se origem for NUM ou MEM.
        if elementoEhToken(segundo, "MEM"):
            if elementoEhToken(primeiro, "NUM"):
                registrarDefinicao(tabela, segundo[1], linha)
                return

            if elementoEhToken(primeiro, "MEM"):
                if registrarUso(tabela, erros, primeiro, linha):
                    registrarDefinicao(tabela, segundo[1], linha)
                return

            erros.append(
                f"Erro semântico na linha {linha}: "
                f"não é permitido atribuir o resultado de uma expressão "
                f"à variável {segundo[1]}."
            )
            return

    if len(elementos) == 3:
        analisarUsosEmElemento(elementos[0], tabela, erros, linha)
        analisarUsosEmElemento(elementos[1], tabela, erros, linha)
        
def construirTabelaSimbolos(arvore):
    tabela = {}
    erros = []

    comandos = coletarComandosPrincipais(arvore)

    for numero_comando, comando in enumerate(comandos, start=1):
        tokens = tokensDoNo(comando)

        if not tokens:
            continue

        linha = linhaDoToken(tokens[0], numero_comando)
        elementos = separarElementos(tokens)

        # Caso: (A)
        # Uso isolado de variável.
        if len(elementos) == 1:
            if elementoEhToken(elementos[0], "MEM"):
                registrarUso(tabela, erros, elementos[0], linha)

            continue

        # Caso com dois elementos:
        # (1 A), (A B), ((3 4 +) A), (N RES)
        if len(elementos) == 2:
            primeiro = elementos[0]
            segundo = elementos[1]

            # (1 A) define A como real
            if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "MEM"):
                registrarDefinicao(tabela, segundo[1], linha)
                continue

            # (A B) define B somente se A já foi definida
            if elementoEhToken(primeiro, "MEM") and elementoEhToken(segundo, "MEM"):
                origem_valida = registrarUso(tabela, erros, primeiro, linha)

                if origem_valida:
                    registrarDefinicao(tabela, segundo[1], linha)

                continue

            # ((3 4 +) A) ou ((3 4 <=) A)
            # Não é permitido na sua regra de atribuição.
            if elementoEhComandoAninhado(primeiro) and elementoEhToken(segundo, "MEM"):
                erros.append(
                    f"Erro semântico na linha {linha}: "
                    f"não é permitido atribuir o resultado de uma expressão "
                    f"à variável {segundo[1]}. "
                    f"Uma atribuição deve usar NUM ou uma variável já definida."
                )

                # Mesmo sendo atribuição inválida, analisa possíveis usos internos.
                analisarUsosEmElemento(primeiro, tabela, erros, linha)
                continue

            # (N RES) será aprofundado depois.
            if elementoEhToken(segundo, "RES"):
                continue

        # Caso de operação:
        # (A B +), (A 2 +), ((A B +) C *), etc.
        if len(elementos) == 3:
            analisarUsosEmElemento(elementos[0], tabela, erros, linha)
            analisarUsosEmElemento(elementos[1], tabela, erros, linha)
            continue

    salvarTabelaSimbolosJson(tabela, erros)

    return {
        "tabela_simbolos": tabela,
        "erros_semanticos": erros
    }
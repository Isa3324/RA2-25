import json
import os

from tabela_simbolos import (
    coletarComandosPrincipais,
    tokensDoNo,
    separarElementos,
    linhaDoToken,
    elementoEhToken,
    elementoEhComandoAninhado
)


TIPO_INTEIRO = "inteiro"
TIPO_REAL = "real"
TIPO_LOGICO = "logico"
TIPO_COMANDO = "comando"


def salvarArvoreAtribuidaJson(
    arvore_atribuida,
    caminho="output/arvore_atribuida.json"
):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(arvore_atribuida, arquivo, indent=4, ensure_ascii=False)


def tipoLiteral(valor):
    """
    Tipo do literal escrito no código.

    Atenção:
    - O literal 1 é inteiro.
    - O literal 1.0 é real.
    - Quando armazenado em MEM, a variável continua sendo real,
      conforme a regra definida para a linguagem.
    """

    if "." in str(valor):
        return TIPO_REAL

    return TIPO_INTEIRO


def tipoDaOperacao(operador, tipo_esquerda, tipo_direita):
    """
    Esta função apenas anota o tipo final de uma operação
    que já foi validada previamente por verificarTipos().
    """

    if operador in {"/", "//", "%"}:
        return TIPO_INTEIRO

    if operador == "|":
        return TIPO_REAL

    if tipo_esquerda == TIPO_REAL or tipo_direita == TIPO_REAL:
        return TIPO_REAL

    return TIPO_INTEIRO


def obterTipoResultado(no):
    """
    Obtém o tipo de um nó já convertido.
    """

    if "tipo_resultado" in no:
        return no["tipo_resultado"]

    return no.get("tipo")


def converterElemento(elemento, tabelaSimbolos, historico_resultados, linha):
    """
    Converte um elemento da árvore sintática inicial
    para um nó semanticamente anotado.
    """

    if elementoEhToken(elemento, "NUM"):
        return {
            "categoria": "literal",
            "valor": elemento[1],
            "tipo": tipoLiteral(elemento[1]),
            "linha": linha
        }

    if elementoEhToken(elemento, "MEM"):
        nome = elemento[1]
        simbolo = tabelaSimbolos[nome]

        return {
            "categoria": "variavel",
            "nome": nome,
            "tipo": simbolo["tipo"],
            "linha_definicao": simbolo["linha_definicao"],
            "linha": linha
        }

    if elementoEhComandoAninhado(elemento):
        return converterComando(
            elemento,
            tabelaSimbolos,
            historico_resultados,
            linha
        )

    raise ValueError(f"Elemento não reconhecido na árvore atribuída: {elemento}")


def converterComando(
    tokens_comando,
    tabelaSimbolos,
    historico_resultados,
    linha_padrao
):
    """
    Converte um comando da árvore inicial para um nó
    da árvore sintática atribuída.
    """

    linha = linhaDoToken(tokens_comando[0], linha_padrao)
    elementos = separarElementos(tokens_comando)

    # Caso: (A)
    if len(elementos) == 1 and elementoEhToken(elementos[0], "MEM"):
        variavel = converterElemento(
            elementos[0],
            tabelaSimbolos,
            historico_resultados,
            linha
        )

        return {
            "categoria": "leitura_memoria",
            "variavel": variavel,
            "tipo_resultado": TIPO_REAL,
            "linha": linha
        }

    # Casos: (1 A), (A B), (N RES)
    if len(elementos) == 2:
        primeiro = elementos[0]
        segundo = elementos[1]

        # Caso: (1 A) ou (1.0 A)
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "MEM"):
            return {
                "categoria": "atribuicao_literal",
                "destino": segundo[1],
                "valor": converterElemento(
                    primeiro,
                    tabelaSimbolos,
                    historico_resultados,
                    linha
                ),
                "tipo_resultado": TIPO_REAL,
                "linha": linha
            }

        # Caso: (A B)
        if elementoEhToken(primeiro, "MEM") and elementoEhToken(segundo, "MEM"):
            return {
                "categoria": "atribuicao_variavel",
                "origem": converterElemento(
                    primeiro,
                    tabelaSimbolos,
                    historico_resultados,
                    linha
                ),
                "destino": segundo[1],
                "tipo_resultado": TIPO_REAL,
                "linha": linha
            }

        # Caso: (N RES)
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "RES"):
            indice = int(primeiro[1])

            resultado_referenciado = historico_resultados[-indice]

            return {
                "categoria": "res",
                "indice": indice,
                "tipo_resultado": resultado_referenciado["tipo_resultado"],
                "pode_ser_null": resultado_referenciado.get("pode_ser_null", False),
                "linha": linha
            }

        # Não deveria chegar aqui, pois tabela_simbolos já rejeita.
        # Casos: ((3 4 +) A), ((3 4 <=) A)
        if elementoEhComandoAninhado(primeiro) and elementoEhToken(segundo, "MEM"):
            raise ValueError(
                f"Não é possível gerar árvore atribuída na linha {linha}: "
                f"atribuição de expressão para {segundo[1]} não é permitida."
            )

    # Casos:
    # (A B +)
    # (A B <)
    # ((A B <) A se)
    # ((A B <) (A 1 +) enquanto)
    if len(elementos) == 3:
        primeiro = elementos[0]
        segundo = elementos[1]
        operador = elementos[2]

        esquerda = converterElemento(
            primeiro,
            tabelaSimbolos,
            historico_resultados,
            linha
        )

        direita = converterElemento(
            segundo,
            tabelaSimbolos,
            historico_resultados,
            linha
        )

        if elementoEhToken(operador, "OP"):
            tipo_resultado = tipoDaOperacao(
                operador[1],
                obterTipoResultado(esquerda),
                obterTipoResultado(direita)
            )

            return {
                "categoria": "operacao_aritmetica",
                "operador": operador[1],
                "esquerda": esquerda,
                "direita": direita,
                "tipo_resultado": tipo_resultado,
                "linha": linha
            }

        if elementoEhToken(operador, "OPREL"):
            return {
                "categoria": "operacao_relacional",
                "operador": operador[1],
                "esquerda": esquerda,
                "direita": direita,
                "tipo_resultado": TIPO_LOGICO,
                "linha": linha
            }

        if elementoEhToken(operador, "SE"):
            return {
                "categoria": "decisao",
                "condicao": esquerda,
                "acao": direita,
                "tipo_condicao": TIPO_LOGICO,
                "tipo_resultado": obterTipoResultado(direita),
                "pode_ser_null": True,
                "valor_sem_execucao": "NULL",
                "linha": linha
            }
            
        if elementoEhToken(operador, "ENQUANTO"):
            return {
                "categoria": "repeticao",
                "condicao": esquerda,
                "acao": direita,
                "tipo_condicao": TIPO_LOGICO,
                "tipo_resultado": obterTipoResultado(direita),
                "pode_ser_null": True,
                "valor_sem_execucao": "NULL",
                "resultado_quando_executa": "resultado_da_ultima_execucao",
                "linha": linha
            }

    raise ValueError(
        f"Não foi possível converter o comando da linha {linha} "
        f"para árvore sintática atribuída."
    )


def gerarArvoreAtribuida(arvore, tabelaSimbolos, tipos):
    """
    Recebe:
        - árvore sintática inicial;
        - tabela de símbolos;
        - resultado de verificarTipos().

    Retorna:
        - árvore sintática atribuída pronta para geração de Assembly.
    """

    if tipos.get("erros_semanticos"):
        raise ValueError(
            "Não é possível gerar árvore atribuída: existem erros semânticos de tipo."
        )

    comandos_atribuidos = []
    historico_resultados = []

    comandos_iniciais = coletarComandosPrincipais(arvore)

    for numero_comando, comando in enumerate(comandos_iniciais, start=1):
        tokens = tokensDoNo(comando)

        no_atribuido = converterComando(
            tokens,
            tabelaSimbolos,
            historico_resultados,
            numero_comando
        )

        no_atribuido["indice_resultado"] = len(historico_resultados) + 1

        comandos_atribuidos.append(no_atribuido)

        historico_resultados.append({
            "linha": no_atribuido["linha"],
            "tipo_resultado": no_atribuido["tipo_resultado"],
            "pode_ser_null": no_atribuido.get("pode_ser_null", False)
        })

    arvore_atribuida = {
        "categoria": "programa",
        "tipo": "programa",
        "inicio": "START",
        "fim": "END",
        "tabela_simbolos": tabelaSimbolos,
        "tipos_validados": tipos,
        "comandos": comandos_atribuidos
    }

    salvarArvoreAtribuidaJson(arvore_atribuida)

    return arvore_atribuida
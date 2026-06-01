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
TIPO_ERRO = "erro"

# Na Fase 3:
# | representa divisão real
# / representa divisão inteira
OPERADORES_NUMERICOS = {"+", "-", "*", "^"}
OPERADORES_INTEIROS = {"/", "//", "%"}
OPERADOR_DIVISAO_REAL = "|"


def salvarRelatorioTiposJson(resultado, caminho="output/tipos_inferidos.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, indent=4, ensure_ascii=False)


def adicionarErro(erros, mensagem):
    if mensagem not in erros:
        erros.append(mensagem)


def tipoLiteralNumerico(valor):
    """
    O literal 1 é inteiro.
    O literal 1.0 é real.
    """

    if "." in str(valor):
        return TIPO_REAL

    return TIPO_INTEIRO


def ehNumerico(tipo):
    return tipo in {TIPO_INTEIRO, TIPO_REAL}


def tipoOperacaoNumerica(tipo_esquerda, tipo_direita):
    """
    Regra de promoção:
    inteiro com inteiro -> inteiro
    se houver real -> real
    """

    if tipo_esquerda == TIPO_REAL or tipo_direita == TIPO_REAL:
        return TIPO_REAL

    return TIPO_INTEIRO


def textoDoElemento(elemento):
    if elementoEhToken(elemento, "NUM") or elementoEhToken(elemento, "MEM"):
        return elemento[1]

    if elementoEhComandoAninhado(elemento):
        valores = [token[1] for token in elemento]
        return " ".join(valores)

    return "?"


def inferirTipoElemento(
    elemento,
    tabela_simbolos,
    resultados_anteriores,
    anotacoes,
    erros,
    linha
):
    if elementoEhToken(elemento, "NUM"):
        return tipoLiteralNumerico(elemento[1])

    if elementoEhToken(elemento, "MEM"):
        nome = elemento[1]

        if nome not in tabela_simbolos:
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"variável {nome} utilizada antes de sua definição."
            )
            return TIPO_ERRO

        return tabela_simbolos[nome]["tipo"]

    if elementoEhComandoAninhado(elemento):
        return inferirTipoComando(
            elemento,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha
        )

    adicionarErro(
        erros,
        f"Erro semântico na linha {linha}: elemento inválido na expressão."
    )

    return TIPO_ERRO

def validarOperacaoAritmetica(operador, tipo_esq, tipo_dir, linha, erros):
    if tipo_esq == TIPO_ERRO or tipo_dir == TIPO_ERRO:
        return TIPO_ERRO

    if operador in OPERADORES_INTEIROS:
        if tipo_esq != TIPO_INTEIRO or tipo_dir != TIPO_INTEIRO:
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"o operador {operador} exige dois operandos inteiros, "
                f"mas recebeu {tipo_esq} e {tipo_dir}."
            )
            return TIPO_ERRO

        return TIPO_INTEIRO

    if operador == OPERADOR_DIVISAO_REAL:
        if not ehNumerico(tipo_esq) or not ehNumerico(tipo_dir):
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"o operador {operador} exige operandos numéricos."
            )
            return TIPO_ERRO

        return TIPO_REAL

    if operador in OPERADORES_NUMERICOS:
        if not ehNumerico(tipo_esq) or not ehNumerico(tipo_dir):
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"o operador {operador} exige operandos numéricos, "
                f"mas recebeu {tipo_esq} e {tipo_dir}."
            )
            return TIPO_ERRO

        return tipoOperacaoNumerica(tipo_esq, tipo_dir)

    adicionarErro(
        erros,
        f"Erro semântico na linha {linha}: operador aritmético {operador} desconhecido."
    )

    return TIPO_ERRO


def validarOperacaoRelacional(operador, tipo_esq, tipo_dir, linha, erros):
    if tipo_esq == TIPO_ERRO or tipo_dir == TIPO_ERRO:
        return TIPO_ERRO

    if not ehNumerico(tipo_esq) or not ehNumerico(tipo_dir):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"o operador relacional {operador} exige operandos numéricos, "
            f"mas recebeu {tipo_esq} e {tipo_dir}."
        )
        return TIPO_ERRO

    return TIPO_LOGICO

def validarRes(
    primeiro,
    resultados_anteriores,
    linha,
    anotacoes,
    erros
):
    if not elementoEhToken(primeiro, "NUM"):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: RES exige um índice numérico inteiro."
        )
        return TIPO_ERRO

    valor = primeiro[1]
    tipo_indice = tipoLiteralNumerico(valor)

    if tipo_indice != TIPO_INTEIRO:
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"RES exige índice inteiro, mas recebeu {valor}."
        )
        return TIPO_ERRO

    indice = int(valor)

    if indice <= 0:
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"RES deve referenciar pelo menos 1 resultado anterior."
        )
        return TIPO_ERRO

    if indice > len(resultados_anteriores):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"RES solicitou o resultado de {indice} linha(s) anterior(es), "
            f"mas existem apenas {len(resultados_anteriores)} resultado(s) disponível(is)."
        )
        return TIPO_ERRO

    resultado_referenciado = resultados_anteriores[-indice]

    tipo_referenciado = resultado_referenciado["tipo"]
    pode_ser_null = resultado_referenciado.get("pode_ser_null", False)

    anotacoes.append({
        "linha": linha,
        "categoria": "res",
        "indice": indice,
        "tipo": tipo_referenciado,
        "pode_ser_null": pode_ser_null
    })

    return tipo_referenciado

def inferirTipoComando(
    tokens_comando,
    tabela_simbolos,
    resultados_anteriores,
    anotacoes,
    erros,
    linha_padrao
):
    linha = linhaDoToken(tokens_comando[0], linha_padrao)
    elementos = separarElementos(tokens_comando)

    # Caso: (A)
    if len(elementos) == 1:
        tipo = inferirTipoElemento(
            elementos[0],
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha
        )

        anotacoes.append({
            "linha": linha,
            "categoria": "uso_variavel",
            "expressao": textoDoElemento(elementos[0]),
            "tipo": tipo
        })

        return tipo

    # Caso: (1 A), (A B), (N RES), ((expr) A)
    if len(elementos) == 2:
        primeiro = elementos[0]
        segundo = elementos[1]

        # (N RES)
        if elementoEhToken(segundo, "RES"):
            return validarRes(
                primeiro,
                resultados_anteriores,
                linha,
                anotacoes,
                erros
            )

        # (1 A): definição válida; variável armazenada como real.
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "MEM"):
            tipo = TIPO_REAL

            anotacoes.append({
                "linha": linha,
                "categoria": "atribuicao_literal",
                "variavel": segundo[1],
                "tipo": tipo
            })

            return tipo

        # (A B): atribuição válida se A já tiver sido definida.
        if elementoEhToken(primeiro, "MEM") and elementoEhToken(segundo, "MEM"):
            tipo_origem = inferirTipoElemento(
                primeiro,
                tabela_simbolos,
                resultados_anteriores,
                anotacoes,
                erros,
                linha
            )

            if tipo_origem == TIPO_ERRO:
                return TIPO_ERRO

            anotacoes.append({
                "linha": linha,
                "categoria": "atribuicao_variavel",
                "origem": primeiro[1],
                "destino": segundo[1],
                "tipo": TIPO_REAL
            })

            return TIPO_REAL

        # ((3 4 +) A) ou ((3 4 <=) A)
        # Já deve ser rejeitado pela tabela de símbolos.
        if elementoEhComandoAninhado(primeiro) and elementoEhToken(segundo, "MEM"):
            return TIPO_ERRO

    # Caso: (A B +), (A B <), ((A B <) A se), etc.
    if len(elementos) == 3:
        primeiro = elementos[0]
        segundo = elementos[1]
        operador = elementos[2]

        tipo_esq = inferirTipoElemento(
            primeiro,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha
        )

        tipo_dir = inferirTipoElemento(
            segundo,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha
        )

        if elementoEhToken(operador, "OP"):
            tipo_resultado = validarOperacaoAritmetica(
                operador[1],
                tipo_esq,
                tipo_dir,
                linha,
                erros
            )

            anotacoes.append({
                "linha": linha,
                "categoria": "operacao_aritmetica",
                "operador": operador[1],
                "tipo": tipo_resultado
            })

            return tipo_resultado

        if elementoEhToken(operador, "OPREL"):
            tipo_resultado = validarOperacaoRelacional(
                operador[1],
                tipo_esq,
                tipo_dir,
                linha,
                erros
            )

            anotacoes.append({
                "linha": linha,
                "categoria": "operacao_relacional",
                "operador": operador[1],
                "tipo": tipo_resultado
            })

            return tipo_resultado

        if elementoEhToken(operador, "SE"):
            if tipo_esq != TIPO_LOGICO:
                    adicionarErro(
                        erros,
                        f"Erro semântico na linha {linha}: "
                        f"o comando se exige condição lógica, mas recebeu {tipo_esq}."
                    )
                    return TIPO_ERRO

            anotacoes.append({
                    "linha": linha,
                    "categoria": "decisao",
                    "tipo_condicao": tipo_esq,
                    "tipo": tipo_dir,
                    "pode_ser_null": True
                })

            return tipo_dir

        if elementoEhToken(operador, "ENQUANTO"):
            if elementoEhToken(operador, "ENQUANTO"):
                if tipo_esq != TIPO_LOGICO:
                    adicionarErro(
                        erros,
                        f"Erro semântico na linha {linha}: "
                        f"o comando enquanto exige condição lógica, mas recebeu {tipo_esq}."
                    )
                    return TIPO_ERRO

                anotacoes.append({
                    "linha": linha,
                    "categoria": "repeticao",
                    "tipo_condicao": tipo_esq,
                    "tipo": tipo_dir,
                    "pode_ser_null": True
                })

                return tipo_dir

    adicionarErro(
        erros,
        f"Erro semântico na linha {linha}: não foi possível inferir o tipo do comando."
    )

    return TIPO_ERRO

def verificarTipos(arvore, tabela_simbolos):
    """
    Recebe a árvore sintática inicial e a tabela de símbolos.
    Retorna tipos inferidos para os comandos e erros semânticos de tipo.
    """

    anotacoes = []
    erros = []
    resultados_anteriores = []

    comandos = coletarComandosPrincipais(arvore)

    for numero_comando, comando in enumerate(comandos, start=1):
        tokens = tokensDoNo(comando)

        if not tokens:
            continue

        linha = linhaDoToken(tokens[0], numero_comando)

        tipo_resultado = inferirTipoComando(
            tokens,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha
        )

        pode_ser_null = False

        if anotacoes:
            ultima_anotacao = anotacoes[-1]

            if ultima_anotacao.get("linha") == linha:
                pode_ser_null = ultima_anotacao.get("pode_ser_null", False)

        resultados_anteriores.append({
            "linha": linha,
            "tipo": tipo_resultado,
            "pode_ser_null": pode_ser_null
        })

    resultado = {
        "tipos_inferidos": anotacoes,
        "resultados_anteriores": resultados_anteriores,
        "erros_semanticos": erros
    }

    salvarRelatorioTiposJson(resultado)

    return resultado
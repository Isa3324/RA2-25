# RA2 1
Tarefa de analise léxica

// Integrantes do grupo (ordem alfabética):
// Isa Stohler Bertolaccini - Isa3324
//
// Nome do grupo no Canvas: RA2 1 


Entrada:
    um arquivo .txt com várias linhas cada linha contém uma expressão da linguagem
        exemplo: (3.14 2.0 +)

Saída do lexer:
    uma lista de tokens
        exemplo: (, 3.14, 2.0, +, )

Saída final do projeto:
    arquivo de tokens salvo




Você deverá criar e documentar a sintaxe para estruturas de tomada de decisão e laços de repetição. A única restrição é que estas estruturas mantenham o padrão da linguagem: devem estar contidas entre parênteses e seguir a lógica de operadores pós-fixados (A B op) ou (A op).

vamos dizer que tenho a seguinte logica

(NUM B OP)
( = terminal
) = terminal
NUM = numeros flout
MEM = nome de um numeor que esta na memoria que comota que aquelo numero

Start' = Start
Start = (START) EXPRECAO (END)
EXPRECAO = (EXP EXP OP) / (EXP MEM) / (NUM RES) / (MEM RES) / NADA
EXP = (EXP EXP OP) / NUM / MEM / NADA
NUM = 1, 2,..., SIM
MEM = PAVAVRAS QUE REPRESENTA NUMEROS



Terminais:
    EPAR   # (
    DPAR   # )
    START  # comeco, comando de comeco
    END    # Fim, comando de fim
    NUM    # Numeros flutuantes
    MEM    # string que representa um numero
    RES    # um comando para pegar o resultado de um lucal (estrutura faz sentido)
    OP     # operadores
    SE     # um comando de SE condicao faz algo se nao outra condicao(estrutura faz sentido)
    SENAOISSO  # um comando de SE condicao faz algo se nao outra condicao(estrutura faz sentido)
    SENAO  # um comando SENAO,(estrutura faz sentido)
    ENQUANTO  # um comando para ENQUANTO condicao loop (estrutura faz sentido)
    OP_REL # operadores relacionais


Não-Terminais:
    programa
    lista_comandos
    comando
    expr
    outros que você precisar


programa -> START lista_comandos END
lista_comandos -> comando lista_comandos
lista_comandos -> epsilon
comando -> EPAR conteudo DPAR
conteudo -> valor valor OP
conteudo -> valor MEM
conteudo -> NUM_IT RES
conteudo -> condicao comando resto_se
conteudo -> condicao comando ENQUANTO
resto_se -> SE
resto_se -> comando SE
operando -> NUM
operando -> MEM
valor -> operando
valor -> comando
condicao -> EPAR valor valor OP_REL DPAR


EPAR   # (
DPAR   # )
START  # comeco, comando de comeco
END    # Fim, comando de fim
NUM    # Numeros flutuantes
MEM    # string que representa um numero
RES    # um comando para pegar o resultado de um lucal (estrutura faz sentido)
OP     # operadores
SE     # um comando de SE condicao faz algo se nao outra condicao(estrutura faz sentido)
ENQUANTO  # um comando para ENQUANTO condicao loop (estrutura faz sentido)
OP_REL # operadores relacionais




programa -> START lista_comandos END
lista_comandos -> comando lista_comandos
lista_comandos -> epsilon
comando -> EPAR conteudo DPAR
conteudo -> valor valor fazer
conteudo -> valor MEM
conteudo -> NUM_IT RES
conteudo -> condicao comando SE
conteudo -> condicao comando ENQUANTO
operando -> NUM
operando -> MEM
valor -> operando
valor -> comando
condicao -> EPAR valor valor OP_REL DPAR





programa -> START lista_comandos END
lista_comandos -> comando lista_comandos
lista_comandos -> epsilon

comando -> EPAR conteudo DPAR
conteudo -> item resto1

resto1 -> MEM
resto1 -> RES
resto1 -> item resto2


resto2 -> OP
resto2 -> OP_REL
resto2 -> SE
resto2 -> ENQUANTO

item -> operando
item -> comando

operando -> NUM
operando -> MEM








Aluno 1: Função construirGramatica e Análise LL(1)
Responsabilidades:

Implementar construirGramatica() para definir as regras de produção da linguagem;
Calcular os conjuntos FIRST e FOLLOW para cada não-terminal;
Construir a tabela de análise LL(1)
;
Validar que a gramática é LL(1)
 (sem conflitos na tabela);
Documentar a gramática completa em formato EBNF (use letras minúsculas para não-terminais e maiúsculas para terminais).
Tarefas Específicas:

Escrever as regras de produção para expressões RPN, comandos especiais e estruturas de controle;
Implementar algoritmos para calcular FIRST e FOLLOW;
Detectar e resolver conflitos na gramática (se houver);
Criar funções auxiliares: calcularFirst(), calcularFollow(), construirTabelaLL1();
Testar a tabela com entradas diversas para garantir determinismo.
Interface:

Entrada: Nenhuma (a gramática é fixa);
Saída: Estrutura de dados contendo gramática, FIRST, FOLLOW e tabela LL(1)
;
Fornece tabela LL(1)
 para a função parsear().







 //_________________________________
 # Descrever sobre o que é LL(1)

 Tem 3 componentes:

1-
    
    Pilha de Análise 
 
2-

    Ponteiro de entrada

3-
    
    Tabela de análise:
        Matriz 
            linhas - não-terminais
            colunas - Terminais

            Cada célula M[A,a] = 
               é uma regra de produção ue   deve ser usada se o não-terminal A estiver no topo da pilha e o terminal a for o próximo símbolo de entrada, o **lookahead**
     
<span style="color:red;">Se a célula estiver vazia, um erro sintático é detectado.</span>
146 
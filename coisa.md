# Arquivos de Teste do Compilador

## 1. `tests/teste_01_valido_completo.txt`

Objetivo: testar programa válido, comentários em diferentes posições, tipos `inteiro`, `real` e `logico` interno, potenciação, `se`, `enquanto`, aninhamento, reatribuição e `RES`.

```txt
(START)
*{ comentario em linha inteira antes das declaracoes }*
(1 A)
(2 B) *{ comentario ao final de um comando }*
(3 C)
(4 D)
(5 S)
(2.00 3 +)
(2.00 3.00 ^)
((A C <=) *{ comentario entre elementos }* ((A B <=) D se) se)
((A B <) (2 A) enquanto)
(0 RES)
(END)
```

Resultado esperado:

```txt
Programa semanticamente válido.
Árvore sintática atribuída gerada.
Assembly gerado.
```

O que ele cobre:

```txt
comentário em linha inteira
comentário no final de linha
comentário entre elementos do comando
inteiro e real
potenciação com expoente 3.00
OPREL usado apenas em se/enquanto
se aninhado
enquanto com reatribuição válida de A
RES isolado com índice 0
```

---

## 2. `tests/teste_02_erro_lexico_comentario.txt`

Objetivo: testar erro léxico por comentário não finalizado e verificar que não aparece traceback.

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
(5 E)
(A B +)
(2.00 3 +)
(2 0 ^)
(A)
*{ comentario iniciado e nao finalizado
(END)
```

Resultado esperado:

```txt
Erro léxico:
- Comentário iniciado na posição ... não foi fechado com }*.
```

Também deve ocorrer:

```txt
Assembly não gerado.
Nenhum traceback do Python.
```

---

## 3. `tests/teste_03_erro_sintatico.txt`

Objetivo: testar que um programa com tokens válidos, mas estrutura gramatical inválida, é rejeitado pelo parser.

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
(5 E)
(A B +)
(A C *)
(2.00 3 +)
(A B + C)
(END)
```

O erro está em:

```txt
(A B + C)
```

A linguagem espera encerrar o comando após o operador `+`, mas encontrou outro elemento `C`.

Resultado esperado:

```txt
Programa rejeitado pela gramática.
Erro sintático na linha 10: ...
Assembly não gerado.
```

---

## 4. `tests/teste_04_erro_semantico_tabela_simbolos.txt`

Objetivo: testar erros da tabela de símbolos: definição inicial dentro de controle, uso de variável não declarada e atribuição proibida de expressão para variável.

```txt
(START)
(1 A)
(2 B)
(3 D)
(4 E)
((A B <) (3 C) se)
((A B <) (4 F) enquanto)
(C)
(G B)
((A B +) A)
(END)
```

Resultados esperados:

```txt
Erro semântico na linha 6: a variável C não pode ser definida pela primeira vez dentro de se.
Erro semântico na linha 7: a variável F não pode ser definida pela primeira vez dentro de enquanto.
Erro semântico na linha 8: variável C utilizada antes de sua definição.
Erro semântico na linha 9: variável G utilizada antes de sua definição.
Erro semântico na linha 10: não é permitido atribuir o resultado de uma expressão à variável A.
Assembly não gerado.
```

O que ele cobre:

```txt
variável declarada
variável não declarada
definição proibida dentro de se
definição proibida dentro de enquanto
atribuição inválida de expressão
mensagens com linha e variável envolvida
```

---

## 5. `tests/teste_05_erro_semantico_tipos.txt`

Objetivo: testar inferência incorreta de tipos, potenciação inválida, operador relacional isolado, `RES` aninhado e uso de possível `NULL` em operação.

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
(A 2 /)
(2.00 3.50 ^)
(A B <)
(((A B <) A se) 2 +)
((A B <) (0 RES) se)
(END)
```

Resultados esperados:

```txt
Erro semântico na linha 6: o operador / exige dois operandos inteiros, mas recebeu real e inteiro.
Erro semântico na linha 7: o expoente de ^ deve ser um literal inteiro não negativo, mas recebeu 3.50.
Erro semântico na linha 8: o operador relacional < só pode ser usado como condição direta de se ou enquanto.
Erro semântico na linha 9: o operador + não pode utilizar um resultado que pode ser NULL.
Erro semântico na linha 10: RES só pode ser usado como comando isolado no formato (N RES).
Assembly não gerado.
```

O que ele cobre:

```txt
inferência incorreta de tipos
variável MEM tratada como real
divisão inteira exigindo inteiros
potenciação inválida
OPREL fora de se/enquanto
NULL em operação aritmética
RES dentro de estrutura de controle
```

---

## 6. `tests/teste_06_valido_null_res.txt`

Objetivo: testar programa semanticamente válido em que `se` e `enquanto` produzem `NULL`, e `RES` propaga esse `NULL` corretamente.

```txt
(START)
(2 A)
(1 B)
(3 C)
(4 D)
*{ o se abaixo possui condicao falsa e retorna NULL }*
((A B <) D se)
(0 RES)
*{ o enquanto abaixo nao executa e retorna NULL }*
((A B <) (1 A) enquanto)
(0 RES)
(A)
(END)
```

Resultado esperado:

```txt
Programa semanticamente válido.
Árvore sintática atribuída gerada.
Assembly gerado.
```

Durante a execução do Assembly:

```txt
((A B <) D se)           -> NULL
primeiro (0 RES)         -> NULL
((A B <) (1 A) enquanto) -> NULL
segundo (0 RES)          -> NULL
```

No Cpulator, as flags esperadas são:

```txt
resultados_null[4] = 1   # se
resultados_null[5] = 1   # RES do se
resultados_null[6] = 1   # enquanto
resultados_null[7] = 1   # RES do enquanto
```

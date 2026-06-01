# Sistema de Regras de Tipos

## Tipos da Linguagem

- `inteiro`: literal numérico sem ponto decimal, usado especialmente em `/`, `%` e `RES`.
- `real`: literal numérico decimal e toda variável armazenada em `MEM`.
- `logico`: resultado de operadores relacionais.

## Variáveis

Toda variável criada por `(NUM MEM)` ou `(MEM MEM)` possui tipo `real`.

Exemplos:

```txt
(1 A)   -> A : real
(1.0 A) -> A : real
(A B)   -> B : real, desde que A tenha sido definida anteriormente

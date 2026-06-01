.syntax unified
.arch armv7-a
.fpu vfpv3
.global _start

.text
_start:
    ldr r10, =pilha_expr       @ pilha temporaria para expressoes
    ldr r11, =resultados       @ resultados dos comandos principais
    ldr r12, =resultados_null  @ flag NULL: 0=valor, 1=NULL

    @ ==========================================
    @ Comando 1 - linha fonte 2
    @ ==========================================
    @ atribuicao literal para A
    @ literal 10
    ldr r0, =const_0
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_A
    vstr d0, [r9]
    mov r7, #0
    @ salva resultado do comando 1
    ldr r8, =resultados
    vstr d0, [r8]
    ldr r8, =resultados_null
    str r7, [r8]

    @ ==========================================
    @ Comando 2 - linha fonte 3
    @ ==========================================
    @ atribuicao literal para B
    @ literal 20
    ldr r0, =const_1
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_B
    vstr d0, [r9]
    mov r7, #0
    @ salva resultado do comando 2
    ldr r8, =resultados
    add r8, r8, #8
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #4
    str r7, [r8]

    @ ==========================================
    @ Comando 3 - linha fonte 4
    @ ==========================================
    @ RES 0: carrega resultado do comando 2
    ldr r8, =resultados
    add r8, r8, #8
    vldr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #4
    ldr r7, [r8]
    @ salva resultado do comando 3
    ldr r8, =resultados
    add r8, r8, #16
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #8
    str r7, [r8]

    b fim

fim:
    b fim

erro_null:
    @ NULL usado onde era necessario um valor numerico
    b erro_null

erro_div_zero:
    @ tentativa de divisao por zero
    b erro_div_zero

erro_expoente:
    @ expoente deve ser inteiro nao negativo
    b erro_expoente

.data
    .align 3
const_zero: .double 0.0
const_um:   .double 1.0
const_0: .double 10.0
const_1: .double 20.0
mem_A: .double 0.0
mem_B: .double 0.0
    .align 3
resultados:      .space 24
resultados_null: .space 12
pilha_expr:      .space 2048

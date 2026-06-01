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
    @ operacao aritmetica ^
    @ literal 2.00
    ldr r0, =const_0
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ literal 3.00
    ldr r0, =const_1
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    @ potenciacao: expoente inteiro nao negativo
    vcvt.s32.f64 s4, d1
    vmov r1, s4
    cmp r1, #0
    blt erro_expoente
    vmov.f64 d3, d0
    ldr r0, =const_um
    vldr d0, [r0]
pot_loop_0:
    cmp r1, #0
    beq pot_fim_1
    vmul.f64 d0, d0, d3
    sub r1, r1, #1
    b pot_loop_0
pot_fim_1:
    mov r7, #0
    @ salva resultado do comando 1
    ldr r8, =resultados
    vstr d0, [r8]
    ldr r8, =resultados_null
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
const_0: .double 2.00
const_1: .double 3.00
    .align 3
resultados:      .space 8
resultados_null: .space 4
pilha_expr:      .space 2048

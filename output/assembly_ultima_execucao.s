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
    @ literal 1
    ldr r0, =const_um
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
    @ literal 2
    ldr r0, =const_0
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
    @ repeticao enquanto
    ldr r0, =const_zero
    vldr d0, [r0]
    ldr r9, =temp_laco_valor_0
    vstr d0, [r9]
    mov r7, #1          @ inicialmente NULL
    ldr r9, =temp_laco_null_0
    str r7, [r9]
enquanto_inicio_0:
    @ operacao relacional <
    @ leitura da memoria A
    ldr r9, =mem_A
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vstr d0, [r10]
    add r10, r10, #8
    @ leitura da memoria B
    ldr r9, =mem_B
    vldr d0, [r9]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    vmov.f64 d1, d0
    sub r10, r10, #8
    vldr d0, [r10]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    ldr r0, =const_zero
    vldr d0, [r0]
    blt rel_true_2
    b rel_fim_3
rel_true_2:
    ldr r0, =const_um
    vldr d0, [r0]
rel_fim_3:
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r0, =const_zero
    vldr d1, [r0]
    vcmp.f64 d0, d1
    vmrs APSR_nzcv, FPSCR
    beq enquanto_fim_1
    @ atribuicao literal para A
    @ literal 2
    ldr r0, =const_0
    vldr d0, [r0]
    mov r7, #0
    cmp r7, #0
    bne erro_null
    ldr r9, =mem_A
    vstr d0, [r9]
    mov r7, #0
    ldr r9, =temp_laco_valor_0
    vstr d0, [r9]
    ldr r9, =temp_laco_null_0
    str r7, [r9]
    b enquanto_inicio_0
enquanto_fim_1:
    ldr r9, =temp_laco_valor_0
    vldr d0, [r9]
    ldr r9, =temp_laco_null_0
    ldr r7, [r9]
    @ salva resultado do comando 3
    ldr r8, =resultados
    add r8, r8, #16
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #8
    str r7, [r8]

    @ ==========================================
    @ Comando 4 - linha fonte 5
    @ ==========================================
    @ RES 0: carrega resultado do comando 3
    ldr r8, =resultados
    add r8, r8, #16
    vldr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #8
    ldr r7, [r8]
    @ salva resultado do comando 4
    ldr r8, =resultados
    add r8, r8, #24
    vstr d0, [r8]
    ldr r8, =resultados_null
    add r8, r8, #12
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
const_0: .double 2.0
mem_A: .double 0.0
mem_B: .double 0.0
temp_laco_valor_0: .double 0.0
temp_laco_null_0: .word 1
    .align 3
resultados:      .space 32
resultados_null: .space 16
pilha_expr:      .space 2048

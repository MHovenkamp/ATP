.section .text
.align 4
.global fibonaci
.global fib

fib:
PUSH {R7,LR}
SUB SP, SP, #56
ADD R7, SP, #0
_line_101:
STR R0, [R7,#0]
_line_102:
STR R0, [R7,#8]
_line_103:
STR R0, [R7,#16]
_line_104:
LDR R3,[R7,#0]
MOV R2, #1
CMP R3,R2
BLE fib_line_4_true
MOV R3, #1
STR R3, [R7,#0]
B _line_105
fib_line_4_true:
MOV R3, #8
STR R3, [R7,#0]
_line_105:
LDR R0 ,[R7, #0]
ADD R0, R0, #5
ADD R0, R0, #100
B lookUpTable
_line_106:
LDR R3,[R7,#8]
SUB R3 , R3, #1
STR R3, [R7,#8]
_line_107:
LDR R0,[R7,#8]
BL fib
MOV R1, R0
STR R1, [R7,#24]
_line_108:
LDR R3,[R7,#16]
SUB R3 , R3, #2
STR R3, [R7,#16]
_line_109:
LDR R0,[R7,#16]
BL fib
MOV R1, R0
STR R1, [R7,#32]
_line_110:
LDR R3,[R7,#24]
LDR R2,[R7,#32]
ADD R3, R3, R2
STR R3, [R7,#24]
_line_111:
LDR R3,[R7,#24]
STR R3,[R7,#40]
_line_112:
B _line_114
_line_113:
MOV R3, #1
STR R3,[R7,#40]
_line_114:
LDR R0, [R7,#40]
MOV SP, R7
ADD SP, SP, #56
POP {R7, PC}


fibonaci:
PUSH {R4,R5,R6,R7,LR}
MOV R6, SP
SUB SP, SP, #0
ADD R7, SP, #0
_line_1:
B end_of_program

lookUpTable:
CMP R0, #101
BEQ _line_101
CMP R0, #102
BEQ _line_102
CMP R0, #103
BEQ _line_103
CMP R0, #104
BEQ _line_104
CMP R0, #105
BEQ _line_105
CMP R0, #106
BEQ _line_106
CMP R0, #107
BEQ _line_107
CMP R0, #108
BEQ _line_108
CMP R0, #109
BEQ _line_109
CMP R0, #110
BEQ _line_110
CMP R0, #111
BEQ _line_111
CMP R0, #112
BEQ _line_112
CMP R0, #113
BEQ _line_113
CMP R0, #114
BEQ _line_114
CMP R0, #1
BEQ _line_1
BNE end_of_program_error

end_of_program:
MOV SP, R6
POP {R4,R5,R6,R7,PC}

end_of_program_error:
LDR R0, =Standard_Error
BL print_word
MOV SP, R6
POP {R4,R5,R6,R7,PC}

.data
Standard_Error:	.asciz "Standard Error"
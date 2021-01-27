.section .text
.align 4
.global test_subroutines_1
.global bool_odd
.global bool_even

bool_odd:
PUSH {R7,LR}
SUB SP, SP, #48
ADD R7, SP, #0
_line_101:
STR R0, [R7,#0]
_line_102:
LDR R3,[R7,#0]
STR R3,[R7,#8]
_line_103:
LDR R3,[R7,#0]
MOV R2, #0
CMP R3,R2
BEQ bool_odd_line_3_true
MOV R3, #1
STR R3, [R7,#0]
B _line_104
bool_odd_line_3_true:
MOV R3, #6
STR R3, [R7,#0]
_line_104:
LDR R0 ,[R7, #0]
ADD R0, R0, #4
ADD R0, R0, #100
B lookUpTable
_line_105:
LDR R3,[R7,#8]
SUB R3 , R3, #1
STR R3, [R7,#8]
_line_106:
LDR R3,[R7,#8]
STR R3,[R7,#16]
_line_107:
LDR R0,[R7,#16]
BL bool_even
MOV R1, R0
STR R1, [R7,#24]
_line_108:
LDR R3,[R7,#24]
STR R3,[R7,#32]
_line_109:
B _line_111
_line_110:
MOV R3, #0
STR R3,[R7,#32]
_line_111:
LDR R0, [R7,#32]
MOV SP, R7
ADD SP, SP, #48
POP {R7, PC}


bool_even:
PUSH {R7,LR}
SUB SP, SP, #48
ADD R7, SP, #0
_line_201:
STR R0, [R7,#0]
_line_202:
LDR R3,[R7,#0]
STR R3,[R7,#8]
_line_203:
LDR R3,[R7,#0]
MOV R2, #0
CMP R3,R2
BEQ bool_even_line_3_true
MOV R3, #1
STR R3, [R7,#0]
B _line_204
bool_even_line_3_true:
MOV R3, #6
STR R3, [R7,#0]
_line_204:
LDR R0 ,[R7, #0]
ADD R0, R0, #4
ADD R0, R0, #200
B lookUpTable
_line_205:
LDR R3,[R7,#8]
SUB R3 , R3, #1
STR R3, [R7,#8]
_line_206:
LDR R3,[R7,#8]
STR R3,[R7,#16]
_line_207:
LDR R0,[R7,#16]
BL bool_odd
MOV R1, R0
STR R1, [R7,#24]
_line_208:
LDR R3,[R7,#24]
STR R3,[R7,#32]
_line_209:
B _line_211
_line_210:
MOV R3, #1
STR R3,[R7,#32]
_line_211:
LDR R0, [R7,#32]
MOV SP, R7
ADD SP, SP, #48
POP {R7, PC}


test_subroutines_1:
PUSH {R4,R5,R6,R7,LR}
MOV R6, SP
SUB SP, SP, #0
ADD R7, SP, #0
_line_1:
_line_2:
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
CMP R0, #201
BEQ _line_201
CMP R0, #202
BEQ _line_202
CMP R0, #203
BEQ _line_203
CMP R0, #204
BEQ _line_204
CMP R0, #205
BEQ _line_205
CMP R0, #206
BEQ _line_206
CMP R0, #207
BEQ _line_207
CMP R0, #208
BEQ _line_208
CMP R0, #209
BEQ _line_209
CMP R0, #210
BEQ _line_210
CMP R0, #211
BEQ _line_211
CMP R0, #1
BEQ _line_1
CMP R0, #2
BEQ _line_2
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
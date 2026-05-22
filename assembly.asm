Assembly Code
-------------
DECLARE x
DECLARE y
DECLARE z
MOV R0, 10
MOV x, R0
MOV R0, 20
MOV y, R0
MOV R0, x
ADD R0, y
MOV t0, R0
MOV R0, t0
MOV z, R0
CMP z, 20
SETGT t1
CMP t1, 0
JE L0
PRINT z
L0:
L2:
CMP x, y
SETLT t2
CMP t2, 0
JE L3
MOV R0, x
ADD R0, 1
MOV t3, R0
MOV R0, t3
MOV x, R0
JMP L2
L3:

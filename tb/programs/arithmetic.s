# arithmetic.s
# Exercises R-type and I-type ALU ops (add/sub/and/or/xor/slli/srli/slt/sltu).
# Expected: mem[0] = 35
addi x1, x0, 5       # x1 = 5
addi x2, x0, 3        # x2 = 3
add  x3, x1, x2       # x3 = 8
sub  x4, x1, x2       # x4 = 2
and  x5, x1, x2       # x5 = 1
or   x6, x1, x2       # x6 = 7
xor  x7, x1, x2       # x7 = 6
slli x8, x1, 2        # x8 = 20
srli x9, x8, 1        # x9 = 10
slt  x10, x4, x1      # x10 = 1  (2 < 5)
sltu x11, x1, x4      # x11 = 0  (5 < 2? no)
add  x12, x3, x4      # 8 + 2 = 10
add  x12, x12, x5     # + 1 = 11
add  x12, x12, x6     # + 7 = 18
add  x12, x12, x7     # + 6 = 24
add  x12, x12, x9     # + 10 = 34
add  x12, x12, x10    # + 1 = 35
add  x12, x12, x11    # + 0 = 35
sw   x12, 0(x0)
halt

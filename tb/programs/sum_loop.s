# sum_loop.s
# Sums 1..10 using a branch-based loop.
# Expected: mem[4] = 55
addi x1, x0, 0        # sum = 0
addi x2, x0, 1         # i = 1
addi x3, x0, 11        # limit = 11
loop:
add  x1, x1, x2        # sum += i
addi x2, x2, 1         # i++
blt  x2, x3, loop      # while i < 11
sw   x1, 4(x0)
halt

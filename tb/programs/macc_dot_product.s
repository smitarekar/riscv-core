# macc_dot_product.s
# Hero test: 4-element dot product via back-to-back MACC, accumulator
# never round-trips through memory between MACs -- this is exactly
# the access pattern MACC exists to speed up over a mul-then-add pair
# per element.
# dot([1,2,3,4], [10,20,30,40]) = 1*10 + 2*20 + 3*30 + 4*40
#                                = 10 + 40 + 90 + 160 = 300
# Expected: mem[0] = 300
addi x1, x0, 1      # a0
addi x2, x0, 10      # b0
addi x3, x0, 2       # a1
addi x4, x0, 20      # b1
addi x5, x0, 3       # a2
addi x6, x0, 30      # b2
addi x7, x0, 4       # a3
addi x8, x0, 40      # b3
addi x10, x0, 0      # accumulator = 0
macc x10, x1, x2     # += 1*10  ->  10
macc x10, x3, x4     # += 2*20  ->  50
macc x10, x5, x6     # += 3*30  -> 140
macc x10, x7, x8     # += 4*40  -> 300
sw   x10, 0(x0)
halt

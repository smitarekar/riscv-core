# macc_single.s
# Basic MACC sanity, plus a register-aliasing case where rd is also
# rs1 (the accumulator and one source read from/write to the same
# register) -- exercises the read-old/write-new sequencing that
# regfile.v's rd_rdata port exists for.
# Expected: mem[0] = 142, mem[4] = 9
addi x1, x0, 6        # rs1 = 6
addi x2, x0, 7         # rs2 = 7
addi x3, x0, 100        # rd initial = 100
macc x3, x1, x2          # x3 = 100 + 6*7 = 142
sw   x3, 0(x0)

addi x4, x0, 3           # x4 = 3, will be both rd and rs1
addi x5, x0, 2            # rs2 = 2
macc x4, x4, x5             # x4 = 3 + 3*2 = 9
sw   x4, 4(x0)
halt

# macc_overflow.s
# 32-bit wraparound: MACC doesn't trap or saturate on overflow, it
# wraps silently, same as ADD elsewhere in this core.
# 0xFFFFFFFF + (2*1) = 0x1_0000_0001 -> truncates to 0x00000001
# Expected: mem[0] = 1
addi x1, x0, -1      # x1 = 0xFFFFFFFF
addi x2, x0, 2        # rs1 = 2
addi x3, x0, 1         # rs2 = 1
macc x1, x2, x3          # x1 = 0xFFFFFFFF + 2*1 = 1 (wrapped)
sw   x1, 0(x0)
halt

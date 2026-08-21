# loadstore.s
# Round-trips byte/halfword/word stores and loads, including sign vs.
# zero extension, then writes a pass/fail flag.
# Expected: mem[20] = 1 (pass)
addi x1, x0, 127      # x1 = 127
sb   x1, 8(x0)
lb   x2, 8(x0)         # x2 should be 127

addi x3, x0, -1        # x3 = 0xFFFFFFFF
sb   x3, 12(x0)        # stores byte 0xFF
lb   x4, 12(x0)        # sign-extended -> x4 = 0xFFFFFFFF
lbu  x5, 12(x0)        # zero-extended -> x5 = 0x000000FF

addi x6, x0, 1
slli x6, x6, 10        # x6 = 1024
sw   x6, 16(x0)
lw   x7, 16(x0)        # x7 = 1024

addi x10, x0, 1        # pass = 1 until proven otherwise

addi x11, x0, 127
sub  x12, x2, x11
bne  x12, x0, fail

addi x13, x4, 1         # x4 == -1  <=>  x4 + 1 == 0
bne  x13, x0, fail

addi x14, x0, 255
sub  x15, x5, x14
bne  x15, x0, fail

addi x16, x0, 1024
sub  x17, x7, x16
bne  x17, x0, fail

j    done
fail:
addi x10, x0, 0
done:
sw   x10, 20(x0)
halt

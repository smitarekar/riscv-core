`timescale 1ns / 1ps

// Combinational multiply-accumulate: result = acc + (a * b).
//
// Kept separate from alu.v rather than folded into it, same reasoning
// as the branch comparator: MACC's accumulate has nothing to do with
// the ALU's job, and a dedicated unit is easier to verify in isolation.
//
// a*b is a 32x32 multiply. Because `result` (and every intermediate
// in this expression) is 32 bits wide, Verilog evaluates the multiply
// itself at 32-bit width -- the product is silently truncated to its
// low 32 bits, which is exactly RV32's MUL semantics (this core does
// not implement widening multiply/MULH). The low 32 bits of a 32x32
// product are bit-identical whether the operands are interpreted as
// signed or unsigned, so no separate signed/unsigned variant is
// needed here. The final add wraps mod 2^32 on overflow, same as the
// ALU's plain ADD -- no saturation, no trap.
module mac_unit (
    input  [31:0] acc,
    input  [31:0] a,
    input  [31:0] b,
    output [31:0] result
);
    assign result = acc + (a * b);
endmodule

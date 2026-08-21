`timescale 1ns / 1ps

// Word-addressed instruction ROM. Loaded from a hex file at elaboration
// time via the HEXFILE parameter (one 32-bit word per line, $readmemh format).
module instr_mem #(
    parameter HEXFILE   = "",
    parameter NUM_WORDS = 1024
) (
    input      [31:0] addr, // byte address; word-aligned, low 2 bits ignored
    output     [31:0] instr
);
    reg [31:0] mem [0:NUM_WORDS-1];

    initial begin
        if (HEXFILE != "")
            $readmemh(HEXFILE, mem);
    end

    assign instr = mem[addr[31:2]];
endmodule

`timescale 1ns / 1ps

// Full-core integration test: runs three assembled programs concurrently
// on three independent core instances, then checks each program's
// expected result directly in its data memory.
//
// Run from the repo root so the HEXFILE paths below resolve correctly:
//   iverilog -o sim/core.vvp rtl/*.v tb/tb_riscv_core.v && vvp sim/core.vvp
module tb_riscv_core;
    reg clk = 0;
    reg rst;

    integer errors = 0;
    integer checks = 0;

    always #5 clk = ~clk;

    riscv_core #(.HEXFILE("tb/programs/arithmetic.hex"))     core_arith      (.clk(clk), .rst(rst));
    riscv_core #(.HEXFILE("tb/programs/sum_loop.hex"))       core_loop       (.clk(clk), .rst(rst));
    riscv_core #(.HEXFILE("tb/programs/loadstore.hex"))      core_ls         (.clk(clk), .rst(rst));
    riscv_core #(.HEXFILE("tb/programs/macc_single.hex"))    core_macc_one   (.clk(clk), .rst(rst));
    riscv_core #(.HEXFILE("tb/programs/macc_dot_product.hex")) core_macc_dot (.clk(clk), .rst(rst));
    riscv_core #(.HEXFILE("tb/programs/macc_overflow.hex"))  core_macc_ovf   (.clk(clk), .rst(rst));

    // name is 256 bits (32 ASCII chars) -- the old 128-bit width silently
    // truncated anything longer than 16 chars from the front (Verilog
    // keeps the low-order bits when a wider string literal is packed into
    // a narrower reg), which is how "loadstore_pass_flag" was printing as
    // "dstore_pass_flag". Needed real headroom once the MACC check names
    // got longer, and it matters here specifically because tb/check_against_golden.py
    // parses these printed names exactly.
    task check(input [31:0] actual, input [31:0] expected, input [255:0] name);
        begin
            checks = checks + 1;
            if (actual !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] got=%0d expected=%0d", name, actual, expected);
            end else begin
                $display("PASS [%0s] = %0d", name, actual);
            end
        end
    endtask

    // data_mem stores bytes little-endian; reassemble a word for checking.
    function [31:0] read_word(input integer core, input integer addr);
        begin
            case (core)
                0: read_word = {core_arith.u_dmem.mem[addr+3], core_arith.u_dmem.mem[addr+2],
                                 core_arith.u_dmem.mem[addr+1], core_arith.u_dmem.mem[addr]};
                1: read_word = {core_loop.u_dmem.mem[addr+3], core_loop.u_dmem.mem[addr+2],
                                 core_loop.u_dmem.mem[addr+1], core_loop.u_dmem.mem[addr]};
                2: read_word = {core_ls.u_dmem.mem[addr+3], core_ls.u_dmem.mem[addr+2],
                                 core_ls.u_dmem.mem[addr+1], core_ls.u_dmem.mem[addr]};
                3: read_word = {core_macc_one.u_dmem.mem[addr+3], core_macc_one.u_dmem.mem[addr+2],
                                 core_macc_one.u_dmem.mem[addr+1], core_macc_one.u_dmem.mem[addr]};
                4: read_word = {core_macc_dot.u_dmem.mem[addr+3], core_macc_dot.u_dmem.mem[addr+2],
                                 core_macc_dot.u_dmem.mem[addr+1], core_macc_dot.u_dmem.mem[addr]};
                5: read_word = {core_macc_ovf.u_dmem.mem[addr+3], core_macc_ovf.u_dmem.mem[addr+2],
                                 core_macc_ovf.u_dmem.mem[addr+1], core_macc_ovf.u_dmem.mem[addr]};
                default: read_word = 32'hXXXXXXXX;
            endcase
        end
    endfunction

    initial begin
        $dumpfile("core.vcd");
        $dumpvars(0, tb_riscv_core);

        rst = 1;
        repeat (2) @(posedge clk);
        rst = 0;

        // 300 cycles is generous: the longest program (loadstore, ~27
        // instructions with no loops) finishes in under 30 cycles.
        repeat (300) @(posedge clk);

        check(read_word(0, 0),  32'd35,  "arithmetic_mem0");
        check(read_word(1, 4),  32'd55,  "sum_loop_mem4");
        check(read_word(2, 20), 32'd1,   "loadstore_pass_flag");
        check(read_word(3, 0),  32'd142, "macc_single_mem0");
        check(read_word(3, 4),  32'd9,   "macc_single_aliasing_mem4");
        check(read_word(4, 0),  32'd300, "macc_dot_product_mem0");
        check(read_word(5, 0),  32'd1,   "macc_overflow_mem0");

        if (errors == 0)
            $display("RISCV_CORE TB: PASS (%0d checks)", checks);
        else
            $display("RISCV_CORE TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

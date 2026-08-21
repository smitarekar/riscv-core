`timescale 1ns / 1ps

module tb_mac_unit;
    reg  [31:0] acc, a, b;
    wire [31:0] result;

    integer errors = 0;
    integer checks = 0;

    mac_unit dut (.acc(acc), .a(a), .b(b), .result(result));

    task check(input [31:0] expected, input [127:0] name);
        begin
            checks = checks + 1;
            if (result !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] acc=%0d a=%0d b=%0d -> got=%0d expected=%0d",
                          name, acc, a, b, result, expected);
            end
        end
    endtask

    initial begin
        // basic multiply-accumulate
        acc = 32'd100; a = 32'd6; b = 32'd7;
        #1 check(32'd142, "basic_100_plus_6x7");

        // zero accumulator
        acc = 32'd0; a = 32'd5; b = 32'd5;
        #1 check(32'd25, "zero_acc");

        // zero operand
        acc = 32'd42; a = 32'd0; b = 32'd999;
        #1 check(32'd42, "zero_operand_leaves_acc_unchanged");

        // 32-bit wraparound: 0xFFFFFFFF + (2*1) = 0x1_0000_0001 -> truncates to 1
        acc = 32'hFFFFFFFF; a = 32'd2; b = 32'd1;
        #1 check(32'd1, "wraps_on_overflow");

        // -1 * -1 = 1: the low 32 bits of the unsigned product match the
        // signed result, confirming no separate signed path is needed
        acc = 32'd0; a = 32'hFFFFFFFF; b = 32'hFFFFFFFF;
        #1 check(32'd1, "negative_times_negative");

        // -1 * 5 = -5 (0xFFFFFFFB in two's complement)
        acc = 32'd0; a = 32'hFFFFFFFF; b = 32'd5;
        #1 check(32'hFFFFFFFB, "negative_times_positive");

        // acc itself can be "negative" (e.g. a running dot-product total
        // that's gone below zero) and still accumulate correctly
        acc = 32'hFFFFFFFB; a = 32'd3; b = 32'd2; // -5 + 6 = 1
        #1 check(32'd1, "negative_acc_plus_positive_product");

        if (errors == 0)
            $display("MAC_UNIT TB: PASS (%0d checks)", checks);
        else
            $display("MAC_UNIT TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

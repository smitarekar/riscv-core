`timescale 1ns / 1ps

module tb_pc;
    reg clk = 0;
    reg rst;
    reg [31:0] pc_next;
    wire [31:0] pc;

    integer errors = 0;
    integer checks = 0;

    program_counter dut (.clk(clk), .rst(rst), .pc_next(pc_next), .pc(pc));

    always #5 clk = ~clk;

    task check(input [31:0] actual, input [31:0] expected, input [127:0] name);
        begin
            checks = checks + 1;
            if (actual !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] got=%0d expected=%0d", name, actual, expected);
            end
        end
    endtask

    initial begin
        rst = 1; pc_next = 32'd100;
        @(negedge clk);
        #1 check(pc, 32'd0, "reset_holds_zero");

        rst = 0; pc_next = 32'd4;
        @(negedge clk);
        #1 check(pc, 32'd4, "first_update");

        pc_next = 32'd8;
        @(negedge clk);
        #1 check(pc, 32'd8, "second_update");

        if (errors == 0)
            $display("PC TB: PASS (%0d checks)", checks);
        else
            $display("PC TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

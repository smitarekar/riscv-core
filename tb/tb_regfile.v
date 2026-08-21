`timescale 1ns / 1ps

module tb_regfile;
    reg clk = 0;
    reg we;
    reg [4:0] rs1_addr, rs2_addr, rd_addr;
    reg [31:0] rd_data;
    wire [31:0] rs1_data, rs2_data;

    integer errors = 0;
    integer checks = 0;

    regfile dut (
        .clk(clk), .we(we),
        .rs1_addr(rs1_addr), .rs2_addr(rs2_addr),
        .rd_addr(rd_addr), .rd_data(rd_data),
        .rs1_data(rs1_data), .rs2_data(rs2_data)
    );

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
        we = 0; rd_addr = 0; rd_data = 0; rs1_addr = 0; rs2_addr = 0;

        // x0 always reads zero, even if a write to x0 is attempted
        @(negedge clk);
        we = 1; rd_addr = 5'd0; rd_data = 32'hDEADBEEF;
        @(negedge clk);
        we = 0; rs1_addr = 5'd0;
        #1 check(rs1_data, 32'd0, "x0_stays_zero");

        // write to x5, then read back on both ports
        @(negedge clk);
        we = 1; rd_addr = 5'd5; rd_data = 32'h12345678;
        @(negedge clk);
        we = 0; rs1_addr = 5'd5; rs2_addr = 5'd5;
        #1 check(rs1_data, 32'h12345678, "x5_rs1_readback");
        #0 check(rs2_data, 32'h12345678, "x5_rs2_readback");

        // write to x10 with a different value, x5 must be unaffected
        @(negedge clk);
        we = 1; rd_addr = 5'd10; rd_data = 32'hCAFEF00D;
        @(negedge clk);
        we = 0; rs1_addr = 5'd10; rs2_addr = 5'd5;
        #1 check(rs1_data, 32'hCAFEF00D, "x10_after_second_write");
        #0 check(rs2_data, 32'h12345678, "x5_unaffected_by_x10_write");

        // write disabled: rd_data must not land
        @(negedge clk);
        we = 0; rd_addr = 5'd20; rd_data = 32'hFFFFFFFF;
        @(negedge clk);
        rs1_addr = 5'd20;
        #1 check(rs1_data, 32'd0, "write_disabled_no_effect");

        if (errors == 0)
            $display("REGFILE TB: PASS (%0d checks)", checks);
        else
            $display("REGFILE TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

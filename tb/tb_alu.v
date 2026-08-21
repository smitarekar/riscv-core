`timescale 1ns / 1ps

module tb_alu;
    reg  [31:0] a, b;
    reg  [3:0]  alu_op;
    wire [31:0] result;
    wire        zero;

    integer errors = 0;
    integer checks = 0;

    alu dut (.a(a), .b(b), .alu_op(alu_op), .result(result), .zero(zero));

    task check(input [31:0] expected, input [127:0] name);
        begin
            checks = checks + 1;
            if (result !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] a=%0d b=%0d op=%b -> got=%0d expected=%0d",
                          name, a, b, alu_op, result, expected);
            end
        end
    endtask

    initial begin
        // ADD
        a = 32'd10; b = 32'd5; alu_op = 4'b0000; #1 check(32'd15, "ADD");
        // SUB
        a = 32'd10; b = 32'd5; alu_op = 4'b0001; #1 check(32'd5, "SUB");
        // SLL
        a = 32'd1; b = 32'd4; alu_op = 4'b0010; #1 check(32'd16, "SLL");
        // SLT (signed): -1 < 1
        a = -32'd1; b = 32'd1; alu_op = 4'b0011; #1 check(32'd1, "SLT_signed");
        // SLTU: unsigned, 0xFFFFFFFF is NOT less than 1
        a = 32'hFFFFFFFF; b = 32'd1; alu_op = 4'b0100; #1 check(32'd0, "SLTU");
        // XOR
        a = 32'hF0F0F0F0; b = 32'hFFFFFFFF; alu_op = 4'b0101; #1 check(32'h0F0F0F0F, "XOR");
        // SRL
        a = 32'hFFFFFFFF; b = 32'd4; alu_op = 4'b0110; #1 check(32'h0FFFFFFF, "SRL");
        // SRA (arithmetic, sign-extends)
        a = 32'hFFFFFFF0; b = 32'd4; alu_op = 4'b0111; #1 check(32'hFFFFFFFF, "SRA");
        // OR
        a = 32'h0F0F0F0F; b = 32'hF0F0F0F0; alu_op = 4'b1000; #1 check(32'hFFFFFFFF, "OR");
        // AND
        a = 32'hFF00FF00; b = 32'h0FF00FF0; alu_op = 4'b1001; #1 check(32'h0F000F00, "AND");
        // zero flag
        a = 32'd5; b = 32'd5; alu_op = 4'b0001; #1 check(32'd0, "SUB_for_zero_flag");
        if (zero !== 1'b1) begin
            errors = errors + 1;
            $display("FAIL [zero_flag] expected zero=1, got zero=%b", zero);
        end
        checks = checks + 1;

        if (errors == 0)
            $display("ALU TB: PASS (%0d checks)", checks);
        else
            $display("ALU TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

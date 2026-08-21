`timescale 1ns / 1ps

module tb_data_mem;
    reg clk = 0;
    reg mem_read, mem_write;
    reg [31:0] addr, wdata;
    reg [2:0] funct3;
    wire [31:0] rdata;

    integer errors = 0;
    integer checks = 0;

    data_mem dut (
        .clk(clk), .mem_read(mem_read), .mem_write(mem_write),
        .addr(addr), .wdata(wdata), .funct3(funct3), .rdata(rdata)
    );

    always #5 clk = ~clk;

    task check(input [31:0] actual, input [31:0] expected, input [127:0] name);
        begin
            checks = checks + 1;
            if (actual !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] got=%h expected=%h", name, actual, expected);
            end
        end
    endtask

    initial begin
        mem_read = 0; mem_write = 0; addr = 0; wdata = 0; funct3 = 0;

        // SW 0xCAFEBABE at addr 0, then LW back
        @(negedge clk);
        mem_write = 1; addr = 32'd0; wdata = 32'hCAFEBABE; funct3 = 3'b010;
        @(negedge clk);
        mem_write = 0; funct3 = 3'b010;
        #1 check(rdata, 32'hCAFEBABE, "SW_then_LW");

        // SB a negative byte at addr 8, LB must sign-extend
        @(negedge clk);
        mem_write = 1; addr = 32'd8; wdata = 32'hFFFFFF80; funct3 = 3'b000; // byte = 0x80
        @(negedge clk);
        mem_write = 0; funct3 = 3'b000;
        #1 check(rdata, 32'hFFFFFF80, "SB_then_LB_sign_extend");

        // Same byte read back as LBU: must zero-extend
        funct3 = 3'b100;
        #1 check(rdata, 32'h00000080, "LBU_zero_extend");

        // SH a negative halfword at addr 16, LH sign-extends, LHU zero-extends
        @(negedge clk);
        mem_write = 1; addr = 32'd16; wdata = 32'hFFFF8000; funct3 = 3'b001; // half = 0x8000
        @(negedge clk);
        mem_write = 0; funct3 = 3'b001;
        #1 check(rdata, 32'hFFFF8000, "SH_then_LH_sign_extend");
        funct3 = 3'b101;
        #1 check(rdata, 32'h00008000, "LHU_zero_extend");

        // Byte ordering: store word 0x11223344 at addr 32, LB each byte (little-endian)
        @(negedge clk);
        mem_write = 1; addr = 32'd32; wdata = 32'h11223344; funct3 = 3'b010;
        @(negedge clk);
        mem_write = 0; addr = 32'd32; funct3 = 3'b100; // LBU byte 0
        #1 check(rdata, 32'h00000044, "little_endian_byte0");
        addr = 32'd33;
        #1 check(rdata, 32'h00000033, "little_endian_byte1");

        if (errors == 0)
            $display("DATA_MEM TB: PASS (%0d checks)", checks);
        else
            $display("DATA_MEM TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

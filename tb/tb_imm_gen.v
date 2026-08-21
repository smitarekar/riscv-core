`timescale 1ns / 1ps

module tb_imm_gen;
    reg  [31:0] instr;
    wire [31:0] imm;

    integer errors = 0;
    integer checks = 0;

    imm_gen dut (.instr(instr), .imm(imm));

    task check(input [31:0] expected, input [127:0] name);
        begin
            checks = checks + 1;
            if (imm !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] instr=%h got=%h expected=%h", name, instr, imm, expected);
            end
        end
    endtask

    initial begin
        // ADDI x1, x2, -1  (I-type, imm = -1 = 0xFFFFFFFF)
        // imm[11:0]=111111111111, rs1=00010, funct3=000, rd=00001, opcode=0010011
        instr = {12'hFFF, 5'd2, 3'b000, 5'd1, 7'b0010011};
        #1 check(32'hFFFFFFFF, "I_type_negative");

        // ADDI x1, x2, 5 (positive small immediate)
        instr = {12'd5, 5'd2, 3'b000, 5'd1, 7'b0010011};
        #1 check(32'd5, "I_type_positive");

        // SW x2, 100(x1)  (S-type: imm=100=0x064 -> imm[11:5]=0000011 imm[4:0]=00100)
        instr = {7'b0000011, 5'd2, 5'd1, 3'b010, 5'b00100, 7'b0100011};
        #1 check(32'd100, "S_type");

        // BEQ x1, x2, offset=8 (B-type, imm bits: [12|10:5|4:1|11])
        // offset 8 = 0b0000_0000_1000 -> imm[12]=0 imm[11]=0 imm[10:5]=000000 imm[4:1]=0100 imm[0]=0(implicit)
        instr = {1'b0, 6'b000000, 5'd2, 5'd1, 3'b000, 4'b0100, 1'b0, 7'b1100011};
        #1 check(32'd8, "B_type");

        // LUI x1, 0x12345 -> imm = 0x12345000
        instr = {20'h12345, 5'd1, 7'b0110111};
        #1 check(32'h12345000, "U_type_LUI");

        // JAL x1, offset (J-type): use offset=4 for a simple check
        // imm[20]=0 imm[19:12]=0 imm[11]=0 imm[10:1]=0000000010
        instr = {1'b0, 10'b0000000010, 1'b0, 8'b0, 5'd1, 7'b1101111};
        #1 check(32'd4, "J_type");

        if (errors == 0)
            $display("IMM_GEN TB: PASS (%0d checks)", checks);
        else
            $display("IMM_GEN TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

`timescale 1ns / 1ps

module tb_control_unit;
    reg  [6:0] opcode;
    reg  [2:0] funct3;
    reg  [6:0] funct7;

    wire reg_write, mem_read, mem_write, is_branch, jump, jalr;
    wire [1:0] alu_src_a, result_src;
    wire       alu_src_b;
    wire [3:0] alu_op;

    integer errors = 0;
    integer checks = 0;

    control_unit dut (
        .opcode(opcode), .funct3(funct3), .funct7(funct7),
        .reg_write(reg_write), .mem_read(mem_read), .mem_write(mem_write),
        .is_branch(is_branch), .jump(jump), .jalr(jalr),
        .alu_src_a(alu_src_a), .alu_src_b(alu_src_b), .result_src(result_src),
        .alu_op(alu_op)
    );

    task check_bit(input actual, input expected, input [127:0] name);
        begin
            checks = checks + 1;
            if (actual !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] got=%b expected=%b", name, actual, expected);
            end
        end
    endtask

    task check_vec(input [3:0] actual, input [3:0] expected, input [127:0] name);
        begin
            checks = checks + 1;
            if (actual !== expected) begin
                errors = errors + 1;
                $display("FAIL [%0s] got=%b expected=%b", name, actual, expected);
            end
        end
    endtask

    initial begin
        // R-type ADD: opcode=0110011 funct3=000 funct7=0000000
        opcode = 7'b0110011; funct3 = 3'b000; funct7 = 7'b0000000;
        #1;
        check_bit(reg_write, 1'b1, "RTYPE_ADD_reg_write");
        check_vec(alu_op, 4'b0000, "RTYPE_ADD_alu_op");

        // R-type SUB: funct7[5]=1
        opcode = 7'b0110011; funct3 = 3'b000; funct7 = 7'b0100000;
        #1 check_vec(alu_op, 4'b0001, "RTYPE_SUB_alu_op");

        // ADDI must stay ADD even with funct7[5]=1 (those bits are immediate, not funct7)
        opcode = 7'b0010011; funct3 = 3'b000; funct7 = 7'b0100000;
        #1 check_vec(alu_op, 4'b0000, "ADDI_ignores_funct7b5");

        // SRLI vs SRAI distinguished by funct7[5]
        opcode = 7'b0010011; funct3 = 3'b101; funct7 = 7'b0000000;
        #1 check_vec(alu_op, 4'b0110, "SRLI_alu_op");
        opcode = 7'b0010011; funct3 = 3'b101; funct7 = 7'b0100000;
        #1 check_vec(alu_op, 4'b0111, "SRAI_alu_op");

        // LOAD (LW): opcode=0000011
        opcode = 7'b0000011; funct3 = 3'b010; funct7 = 7'b0000000;
        #1;
        check_bit(reg_write, 1'b1, "LOAD_reg_write");
        check_bit(mem_read, 1'b1, "LOAD_mem_read");
        check_bit(alu_src_b, 1'b1, "LOAD_alu_src_b_imm");
        check_bit(result_src[0], 1'b1, "LOAD_result_src_mem");

        // STORE (SW): opcode=0100011
        opcode = 7'b0100011; funct3 = 3'b010; funct7 = 7'b0000000;
        #1;
        check_bit(mem_write, 1'b1, "STORE_mem_write");
        check_bit(reg_write, 1'b0, "STORE_no_reg_write");

        // BRANCH: opcode=1100011
        opcode = 7'b1100011; funct3 = 3'b000; funct7 = 7'b0000000;
        #1;
        check_bit(is_branch, 1'b1, "BRANCH_is_branch");
        check_bit(reg_write, 1'b0, "BRANCH_no_reg_write");

        // JAL: opcode=1101111
        opcode = 7'b1101111; funct3 = 3'b000; funct7 = 7'b0000000;
        #1;
        check_bit(jump, 1'b1, "JAL_jump");
        check_bit(reg_write, 1'b1, "JAL_reg_write");
        check_vec({2'b00, result_src}, {2'b00, 2'b10}, "JAL_result_src_pc4");

        // JALR: opcode=1100111
        opcode = 7'b1100111; funct3 = 3'b000; funct7 = 7'b0000000;
        #1;
        check_bit(jalr, 1'b1, "JALR_jalr");
        check_bit(alu_src_b, 1'b1, "JALR_alu_src_b_imm");

        // LUI: opcode=0110111
        opcode = 7'b0110111; funct3 = 3'b000; funct7 = 7'b0000000;
        #1;
        check_bit(reg_write, 1'b1, "LUI_reg_write");
        check_vec({2'b00, alu_src_a}, {2'b00, 2'b10}, "LUI_alu_src_a_zero");

        // AUIPC: opcode=0010111
        opcode = 7'b0010111; funct3 = 3'b000; funct7 = 7'b0000000;
        #1;
        check_vec({2'b00, alu_src_a}, {2'b00, 2'b01}, "AUIPC_alu_src_a_pc");

        // MACC: opcode=0001011 (custom-0), funct3=000, funct7=0000001
        opcode = 7'b0001011; funct3 = 3'b000; funct7 = 7'b0000001;
        #1;
        check_bit(reg_write, 1'b1, "MACC_reg_write");
        check_vec({2'b00, result_src}, {2'b00, 2'b11}, "MACC_result_src_mac");

        // MACC decode doesn't gate on funct7 (documented, not enforced --
        // see the comment in control_unit.v). Confirm that's really the
        // case rather than assuming it, since the encoding note promises
        // funct7=0000001 but this is deliberately not checked in hardware.
        opcode = 7'b0001011; funct3 = 3'b000; funct7 = 7'b1111111;
        #1 check_bit(reg_write, 1'b1, "MACC_funct7_not_gated");

        // An unimplemented custom-0 funct3 must NOT be treated as MACC
        opcode = 7'b0001011; funct3 = 3'b001; funct7 = 7'b0000001;
        #1 check_bit(reg_write, 1'b0, "CUSTOM0_unknown_funct3_no_reg_write");

        if (errors == 0)
            $display("CONTROL_UNIT TB: PASS (%0d checks)", checks);
        else
            $display("CONTROL_UNIT TB: FAIL (%0d/%0d checks failed)", errors, checks);

        $finish;
    end
endmodule

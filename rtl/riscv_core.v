`timescale 1ns / 1ps

// Top-level single-cycle RV32I datapath.
module riscv_core #(
    parameter HEXFILE = ""
) (
    input clk,
    input rst
);
    wire [31:0] pc, pc_next, pc_plus4, pc_target;
    wire [31:0] instr;

    wire [6:0] opcode    = instr[6:0];
    wire [4:0] rd_addr   = instr[11:7];
    wire [2:0] funct3    = instr[14:12];
    wire [4:0] rs1_addr  = instr[19:15];
    wire [4:0] rs2_addr  = instr[24:20];
    wire       funct7b5  = instr[30];

    wire [31:0] imm;

    wire reg_write, mem_read, mem_write, is_branch, jump, jalr;
    wire [1:0] alu_src_a_sel, result_src;
    wire       alu_src_b_sel;
    wire [3:0] alu_op;

    wire [31:0] rs1_data, rs2_data;
    wire [31:0] alu_src_a, alu_src_b;
    wire [31:0] alu_result;
    wire        alu_zero_unused;
    wire [31:0] mem_rdata;
    wire [31:0] wb_data;

    // ---- Fetch ----
    program_counter u_pc (.clk(clk), .rst(rst), .pc_next(pc_next), .pc(pc));

    instr_mem #(.HEXFILE(HEXFILE)) u_imem (.addr(pc), .instr(instr));

    assign pc_plus4  = pc + 32'd4;
    assign pc_target = pc + imm;

    // ---- Decode ----
    imm_gen u_imm_gen (.instr(instr), .imm(imm));

    control_unit u_ctrl (
        .opcode(opcode), .funct3(funct3), .funct7b5(funct7b5),
        .reg_write(reg_write), .mem_read(mem_read), .mem_write(mem_write),
        .is_branch(is_branch), .jump(jump), .jalr(jalr),
        .alu_src_a(alu_src_a_sel), .alu_src_b(alu_src_b_sel),
        .result_src(result_src), .alu_op(alu_op)
    );

    regfile u_regfile (
        .clk(clk), .we(reg_write),
        .rs1_addr(rs1_addr), .rs2_addr(rs2_addr),
        .rd_addr(rd_addr), .rd_data(wb_data),
        .rs1_data(rs1_data), .rs2_data(rs2_data)
    );

    // ---- Execute ----
    assign alu_src_a = (alu_src_a_sel == 2'b01) ? pc :
                        (alu_src_a_sel == 2'b10) ? 32'd0 :
                        rs1_data;
    assign alu_src_b = alu_src_b_sel ? imm : rs2_data;

    alu u_alu (
        .a(alu_src_a), .b(alu_src_b), .alu_op(alu_op),
        .result(alu_result), .zero(alu_zero_unused)
    );

    // Branch condition is computed directly off rs1/rs2, independent of
    // the ALU, so the ALU stays free to do address math (loads/stores/jalr).
    reg branch_taken;
    always @(*) begin
        case (funct3)
            3'b000:  branch_taken = (rs1_data == rs2_data);              // BEQ
            3'b001:  branch_taken = (rs1_data != rs2_data);              // BNE
            3'b100:  branch_taken = ($signed(rs1_data) < $signed(rs2_data)); // BLT
            3'b101:  branch_taken = !($signed(rs1_data) < $signed(rs2_data)); // BGE
            3'b110:  branch_taken = (rs1_data < rs2_data);               // BLTU
            3'b111:  branch_taken = !(rs1_data < rs2_data);              // BGEU
            default: branch_taken = 1'b0;
        endcase
    end

    // ---- Memory ----
    data_mem u_dmem (
        .clk(clk), .mem_read(mem_read), .mem_write(mem_write),
        .addr(alu_result), .wdata(rs2_data), .funct3(funct3),
        .rdata(mem_rdata)
    );

    // ---- Write-back ----
    assign wb_data = (result_src == 2'b01) ? mem_rdata :
                      (result_src == 2'b10) ? pc_plus4 :
                      alu_result;

    // ---- Next PC ----
    assign pc_next = jalr ? (alu_result & ~32'd1) :
                      (jump || (is_branch && branch_taken)) ? pc_target :
                      pc_plus4;
endmodule

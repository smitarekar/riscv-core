`timescale 1ns / 1ps

// Decodes opcode/funct3/funct7[5] into datapath control signals.
// alu_op encoding must stay in sync with alu.v's localparams.
module control_unit (
    input  [6:0] opcode,
    input  [2:0] funct3,
    input        funct7b5,
    output reg       reg_write,
    output reg       mem_read,
    output reg       mem_write,
    output reg       is_branch,
    output reg       jump,     // JAL
    output reg       jalr,     // JALR
    output reg [1:0] alu_src_a, // 00=rs1, 01=pc, 10=zero
    output reg       alu_src_b, // 0=rs2, 1=imm
    output reg [1:0] result_src, // 00=alu_result, 01=mem_data, 10=pc_plus_4
    output reg [3:0] alu_op
);
    localparam ALU_ADD  = 4'b0000;
    localparam ALU_SUB  = 4'b0001;
    localparam ALU_SLL  = 4'b0010;
    localparam ALU_SLT  = 4'b0011;
    localparam ALU_SLTU = 4'b0100;
    localparam ALU_XOR  = 4'b0101;
    localparam ALU_SRL  = 4'b0110;
    localparam ALU_SRA  = 4'b0111;
    localparam ALU_OR   = 4'b1000;
    localparam ALU_AND  = 4'b1001;

    localparam OP_LOAD   = 7'b0000011;
    localparam OP_IMM    = 7'b0010011;
    localparam OP_STORE  = 7'b0100011;
    localparam OP_RTYPE  = 7'b0110011;
    localparam OP_BRANCH = 7'b1100011;
    localparam OP_JALR   = 7'b1100111;
    localparam OP_JAL    = 7'b1101111;
    localparam OP_LUI    = 7'b0110111;
    localparam OP_AUIPC  = 7'b0010111;

    // ALU op only matters for R-type / I-type-ALU; everything else that
    // still uses the ALU (loads, stores, jalr, auipc) needs a plain add.
    always @(*) begin
        case (opcode)
            OP_RTYPE: begin
                case (funct3)
                    3'b000:  alu_op = funct7b5 ? ALU_SUB : ALU_ADD;
                    3'b001:  alu_op = ALU_SLL;
                    3'b010:  alu_op = ALU_SLT;
                    3'b011:  alu_op = ALU_SLTU;
                    3'b100:  alu_op = ALU_XOR;
                    3'b101:  alu_op = funct7b5 ? ALU_SRA : ALU_SRL;
                    3'b110:  alu_op = ALU_OR;
                    3'b111:  alu_op = ALU_AND;
                    default: alu_op = ALU_ADD;
                endcase
            end
            OP_IMM: begin
                case (funct3)
                    3'b000:  alu_op = ALU_ADD;  // ADDI: no SUBI, funct7 bits are imm here
                    3'b001:  alu_op = ALU_SLL;  // SLLI
                    3'b010:  alu_op = ALU_SLT;  // SLTI
                    3'b011:  alu_op = ALU_SLTU; // SLTIU
                    3'b100:  alu_op = ALU_XOR;  // XORI
                    3'b101:  alu_op = funct7b5 ? ALU_SRA : ALU_SRL; // SRLI/SRAI
                    3'b110:  alu_op = ALU_OR;   // ORI
                    3'b111:  alu_op = ALU_AND;  // ANDI
                    default: alu_op = ALU_ADD;
                endcase
            end
            default: alu_op = ALU_ADD;
        endcase
    end

    always @(*) begin
        // safe defaults
        reg_write  = 1'b0;
        mem_read   = 1'b0;
        mem_write  = 1'b0;
        is_branch  = 1'b0;
        jump       = 1'b0;
        jalr       = 1'b0;
        alu_src_a  = 2'b00; // rs1
        alu_src_b  = 1'b0;  // rs2
        result_src = 2'b00; // alu_result

        case (opcode)
            OP_LOAD: begin
                reg_write  = 1'b1;
                mem_read   = 1'b1;
                alu_src_b  = 1'b1;  // imm (offset)
                result_src = 2'b01; // mem_data
            end
            OP_STORE: begin
                mem_write = 1'b1;
                alu_src_b = 1'b1;   // imm (offset)
            end
            OP_RTYPE: begin
                reg_write = 1'b1;
                // alu_src_a = rs1, alu_src_b = rs2 (defaults)
            end
            OP_IMM: begin
                reg_write = 1'b1;
                alu_src_b = 1'b1;   // imm
            end
            OP_BRANCH: begin
                is_branch = 1'b1;
                // datapath computes the branch condition directly off rs1/rs2
            end
            OP_JAL: begin
                reg_write  = 1'b1;
                jump       = 1'b1;
                result_src = 2'b10; // pc+4 -> rd
            end
            OP_JALR: begin
                reg_write  = 1'b1;
                jalr       = 1'b1;
                alu_src_b  = 1'b1;  // imm, alu computes rs1+imm for next PC
                result_src = 2'b10; // pc+4 -> rd
            end
            OP_LUI: begin
                reg_write  = 1'b1;
                alu_src_a  = 2'b10; // zero
                alu_src_b  = 1'b1;  // imm
            end
            OP_AUIPC: begin
                reg_write  = 1'b1;
                alu_src_a  = 2'b01; // pc
                alu_src_b  = 1'b1;  // imm
            end
            default: ; // NOP-safe: all outputs stay at their defaults above
        endcase
    end
endmodule

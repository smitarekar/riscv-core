`timescale 1ns / 1ps

// Sign-extends the immediate field out of a 32-bit instruction word,
// selecting the field layout by RV32I instruction format.
module imm_gen (
    input  [31:0] instr,
    output reg [31:0] imm
);
    // instr[6:0] opcode identifies the format.
    localparam OP_LOAD   = 7'b0000011; // I-type
    localparam OP_IMM    = 7'b0010011; // I-type
    localparam OP_JALR   = 7'b1100111; // I-type
    localparam OP_STORE  = 7'b0100011; // S-type
    localparam OP_BRANCH = 7'b1100011; // B-type
    localparam OP_LUI    = 7'b0110111; // U-type
    localparam OP_AUIPC  = 7'b0010111; // U-type
    localparam OP_JAL    = 7'b1101111; // J-type

    always @(*) begin
        case (instr[6:0])
            OP_LOAD, OP_IMM, OP_JALR:
                imm = {{20{instr[31]}}, instr[31:20]};
            OP_STORE:
                imm = {{20{instr[31]}}, instr[31:25], instr[11:7]};
            OP_BRANCH:
                imm = {{19{instr[31]}}, instr[31], instr[7], instr[30:25], instr[11:8], 1'b0};
            OP_LUI, OP_AUIPC:
                imm = {instr[31:12], 12'b0};
            OP_JAL:
                imm = {{11{instr[31]}}, instr[31], instr[19:12], instr[20], instr[30:21], 1'b0};
            default:
                imm = 32'd0;
        endcase
    end
endmodule

`timescale 1ns / 1ps

// Byte-addressable data RAM supporting byte/halfword/word loads and stores,
// sized and signed per funct3 (matches LB/LH/LW/LBU/LHU and SB/SH/SW).
module data_mem #(
    parameter NUM_BYTES = 4096
) (
    input             clk,
    input             mem_read,
    input             mem_write,
    input      [31:0] addr,
    input      [31:0] wdata,
    input      [2:0]  funct3,
    output reg [31:0] rdata
);
    reg [7:0] mem [0:NUM_BYTES-1];

    wire [31:0] byte_addr = addr;
    integer i;

    initial begin
        for (i = 0; i < NUM_BYTES; i = i + 1)
            mem[i] = 8'd0;
    end

    // synchronous write
    always @(posedge clk) begin
        if (mem_write) begin
            case (funct3)
                3'b000: begin // SB
                    mem[byte_addr] <= wdata[7:0];
                end
                3'b001: begin // SH
                    mem[byte_addr]     <= wdata[7:0];
                    mem[byte_addr + 1] <= wdata[15:8];
                end
                3'b010: begin // SW
                    mem[byte_addr]     <= wdata[7:0];
                    mem[byte_addr + 1] <= wdata[15:8];
                    mem[byte_addr + 2] <= wdata[23:16];
                    mem[byte_addr + 3] <= wdata[31:24];
                end
                default: ; // unsupported size: no write
            endcase
        end
    end

    // combinational read, sized/signed per funct3
    always @(*) begin
        case (funct3)
            3'b000: rdata = {{24{mem[byte_addr][7]}}, mem[byte_addr]};                 // LB
            3'b001: rdata = {{16{mem[byte_addr+1][7]}}, mem[byte_addr+1], mem[byte_addr]}; // LH
            3'b010: rdata = {mem[byte_addr+3], mem[byte_addr+2], mem[byte_addr+1], mem[byte_addr]}; // LW
            3'b100: rdata = {24'd0, mem[byte_addr]};                                    // LBU
            3'b101: rdata = {16'd0, mem[byte_addr+1], mem[byte_addr]};                  // LHU
            default: rdata = 32'd0;
        endcase
    end
endmodule

`timescale 1ns / 1ps

// 32x32-bit register file. x0 is hardwired to zero.
// Reads are combinational; writes are synchronous on the rising clock edge.
module regfile (
    input         clk,
    input         we,
    input  [4:0]  rs1_addr,
    input  [4:0]  rs2_addr,
    input  [4:0]  rd_addr,
    input  [31:0] rd_data,
    output [31:0] rs1_data,
    output [31:0] rs2_data,
    output [31:0] rd_rdata  // combinational read of rd_addr's current (pre-write)
                             // value. Needed by instructions where rd is also a
                             // source, e.g. MACC's accumulator: because this read
                             // is combinational and the write below is a clocked
                             // nonblocking assignment, rd_rdata always reflects
                             // the OLD value for the whole cycle, and the new
                             // value written this cycle isn't visible until the
                             // next posedge. No extra sequencing logic needed.
);
    reg [31:0] regs [0:31];
    integer i;

    initial begin
        for (i = 0; i < 32; i = i + 1)
            regs[i] = 32'd0;
    end

    assign rs1_data = (rs1_addr == 5'd0) ? 32'd0 : regs[rs1_addr];
    assign rs2_data = (rs2_addr == 5'd0) ? 32'd0 : regs[rs2_addr];
    assign rd_rdata = (rd_addr  == 5'd0) ? 32'd0 : regs[rd_addr];

    always @(posedge clk) begin
        if (we && rd_addr != 5'd0)
            regs[rd_addr] <= rd_data;
    end
endmodule

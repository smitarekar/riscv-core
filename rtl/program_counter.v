`timescale 1ns / 1ps

module program_counter (
    input             clk,
    input             rst,
    input      [31:0] pc_next,
    output reg [31:0] pc
);
    always @(posedge clk) begin
        if (rst)
            pc <= 32'd0;
        else
            pc <= pc_next;
    end
endmodule

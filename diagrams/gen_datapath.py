import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from svgdiagram import Diagram

d = Diagram(2020, 970, "riscv-core: single-cycle RV32I + MACC datapath",
            "one instruction, fetch through write-back, in one clock edge")

pc      = d.box(40, 150, 150, 70, "PC", "green", fontsize=13, bold=True)
imem    = d.box(40, 330, 150, 90, "instr_mem\n1024 x 32, ROM", "green", fontsize=11)
immgen  = d.box(260, 150, 160, 70, "imm_gen\nI/S/B/U/J sign-ext", "purple", fontsize=10)
ctrl    = d.box(260, 330, 160, 90, "control_unit\nopcode/f3/f7\n-> control signals", "purple", fontsize=10)
regfile = d.box(500, 150, 240, 260, "regfile\n32 x 32-bit, x0=0\nasync read / sync write\n+ rd_rdata (3rd read port)", "green", fontsize=11)
opmux   = d.box(820, 150, 150, 70, "operand muxes\nA: rs1/pc/0\nB: rs2/imm", "yellow", fontsize=9)
alu     = d.box(1050, 150, 150, 90, "ALU\nADD SUB SLL SLT SLTU\nXOR SRL SRA OR AND", "blue", fontsize=9, bold=True)
mac     = d.box(1050, 330, 150, 70, "mac_unit\nacc + (a * b)", "blue", fontsize=10, bold=True)
bcmp    = d.box(1050, 440, 150, 70, "branch comparator\nBEQ..BGEU", "purple", fontsize=10)
dmem    = d.box(1280, 150, 170, 100, "data_mem\n4096 B\nsized/signed ld/st", "green", fontsize=10)
wbmux   = d.box(1540, 150, 160, 110, "write-back mux\nalu / mem / pc+4\n/ mac_result", "yellow", fontsize=9)
npc     = d.box(1790, 150, 170, 110, "next-PC logic\njalr / branch,jump\n/ pc + 4", "yellow", fontsize=9)

e = d.edge

# ---- fetch / decode ----
e([pc["s"], imem["n"]])
e([imem["e"], (200, 400), (200, 100), (immgen["c"][0], 100), immgen["n"]], label="instr", label_pos=0.34)
e([imem["e"], ctrl["w"]], label="opcode/f3/f7")
e([imem["e"], (230, 375), (230, 280), (500, 280)], label="rs1/rs2/rd addr")

# ---- regfile -> execute stage ----
e([(regfile["box_x"]+regfile["box_w"], 190), opmux["w"]], label="rs1_data")
e([(regfile["box_x"]+regfile["box_w"], 230), (900, 230), (900, opmux["box_y"]+opmux["box_h"]), opmux["s"]], label="rs2_data")
e([(regfile["box_x"]+regfile["box_w"], 330), mac["w"]], label="rs1/rs2/rd_rdata")
e([(regfile["box_x"]+regfile["box_w"], 380), (1000, 380), (1000, 475), bcmp["w"]], label="rs1/rs2")

# imm bypasses over the top of regfile straight to the operand muxes
e([immgen["n"], (340, 100), (895, 100), (895, opmux["box_y"])], label="imm")

# ---- execute -> memory / write-back ----
e([opmux["e"], alu["w"]])
e([alu["e"], dmem["w"]], label="addr")
e([alu["n"], (1125, 100), (1620, 100), (1620, wbmux["box_y"])], label="alu_result")
e([mac["e"], (1220, 365), (1220, 270), (1470, 270), (1470, 240), (wbmux["box_x"], 240)], label="mac_result")
e([dmem["e"], (wbmux["box_x"], 220)], label="mem_rdata")
e([pc["e"], (210, 185), (210, 90), (1660, 90), (1660, wbmux["box_y"])], label="pc+4", label_pos=0.93)

# ---- next-PC select ----
e([bcmp["e"], (1230, 475), (1230, 560), (1875, 560), (1875, npc["box_y"]+npc["box_h"])], label="branch_taken")
e([alu["s"], (1125, 250), (990, 250), (990, 600), (1830, 600), npc["s"]], label="alu_result (jalr)")
e([pc["e"], (230, 185), (230, 70), (1875, 70), npc["n"]], label="pc+4 (default)", label_pos=0.9)

legend_y = d.legend([
    ("blue", "Primary compute -- ALU, MAC unit"),
    ("green", "Storage -- PC, instruction memory, register file, data memory"),
    ("purple", "Control / decode -- control_unit, imm_gen, branch comparator"),
    ("yellow", "Muxes -- operand select, write-back select, next-PC select"),
    ("orange", "Feedback paths that close the single-cycle loop each clock edge"),
], 20, 630, row_h=18)

# ---- feedback loops (orange), routed below the legend so labels can't collide with it ----
e([wbmux["s"], (1620, 790), (620, 790), regfile["s"]], color="#d79b00", width=2.25,
  label="wb_data -> regfile write port", label_pos=0.5)
e([npc["s"], (1875, 850), (10, 850), (10, pc["w"][1]), pc["w"]],
  color="#d79b00", width=2.25, label="next PC -> PC (closes the loop each edge)", label_pos=0.5)

d.wrapped_note(20, 900, 1960,
    "control_unit's outputs (reg_write, mem_read/write, alu_op, every mux select) are omitted as individual "
    "wires above for legibility -- see the Modules table in the README for the full signal list. MACC "
    "(custom-0 opcode) runs mac_unit off rs1_data/rs2_data/rd_rdata directly, in parallel with the ALU -- "
    "result_src's unused 2'b11 encoding picks it at the write-back mux.")

d.write("datapath.svg")

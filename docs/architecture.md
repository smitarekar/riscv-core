# Architecture

## Overview

Single-cycle RV32I datapath: every instruction fetches, decodes, executes,
accesses memory, and writes back within one clock cycle. No pipelining, no
hazards to resolve — the trade-off is a longer critical path (and lower
clock frequency) in exchange for a datapath that is straightforward to
verify.

```
                +-----------+        +------------+
        pc ---->| instr_mem |--instr-|>  decode:   |
        ^       +-----------+        |  opcode     |
        |                            |  rs1/rs2/rd |
        |                            |  funct3/7   |
   +---------+                       +------+-----+
   |   PC    |<--pc_next--+                 |
   +---------+            |          +------v------+
        |                 |          | control_unit|
      pc+4          pc_target/       +------+------+
                    jalr_target             |  (alu_op, muxes,
                          ^                 |   reg_write, mem_*, ...)
                          |                 v
   +---------+     +------+------+   +-----------+
   | regfile |---->| branch_comp |   |  imm_gen  |
   +----+----+     +-------------+   +-----+-----+
        |                                  |
        +------------+  +------------------+
                     v  v
                 +---------+       +-----------+
                 |   ALU   |------>| data_mem  |
                 +---------+       +-----------+
                                         |
                                    wb_data mux
                                         |
                                         v
                                    regfile.rd_data
```

## Modules

| Module              | Responsibility |
|---------------------|----------------|
| `program_counter.v` | Holds PC, updates from `pc_next` each cycle. |
| `instr_mem.v`       | Word-addressed instruction ROM, loaded via `$readmemh`. |
| `imm_gen.v`         | Sign-extends I/S/B/U/J-type immediates per opcode. |
| `control_unit.v`    | Decodes opcode/funct3/funct7[5] into all datapath control signals and the ALU op. |
| `regfile.v`         | 32x32-bit registers, x0 hardwired to zero, async read / sync write. |
| `alu.v`             | Combinational ALU: ADD/SUB/SLL/SLT/SLTU/XOR/SRL/SRA/OR/AND. |
| `data_mem.v`        | Byte-addressable RAM with sized/signed loads and stores. |
| `riscv_core.v`      | Top-level wiring, ALU source muxes, branch comparator, PC-next mux. |

## Key design decisions

- **Branch comparator is separate from the ALU.** Branches (BEQ/BNE/BLT/
  BGE/BLTU/BGEU) are resolved by a dedicated combinational block reading
  `rs1_data`/`rs2_data` directly, rather than reusing the ALU's SUB/SLT
  paths with a zero flag. This keeps the ALU free to compute load/store
  addresses and the JALR target in the same cycle a branch is being
  evaluated, and made the branch logic easier to verify in isolation.

- **Three-way ALU source-A mux** (`rs1` / `pc` / `zero`) lets AUIPC
  (`pc + imm`) and LUI (`0 + imm`) reuse the ALU's adder instead of
  needing dedicated hardware.

- **`funct7[5]` is only trusted for R-type and shift-immediate
  instructions.** For `ADDI`/etc., bits [31:25] of the instruction are
  part of the immediate field, not a real `funct7` — treating them as
  one would silently turn some `ADDI`s into `SUBI`s (which doesn't
  exist in RV32I). `control_unit.v`'s testbench has an explicit check
  for this.

## Supported ISA subset (RV32I)

R-type: ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND
I-type: ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI, JALR
Loads: LB, LH, LW, LBU, LHU
Stores: SB, SH, SW
Branches: BEQ, BNE, BLT, BGE, BLTU, BGEU
Jumps: JAL, JALR
Upper immediate: LUI, AUIPC

Not implemented: FENCE, ECALL/EBREAK, CSR instructions (no exception/
interrupt handling in this core).

## Verification

Every module has its own self-checking testbench (`tb/tb_<module>.v`),
plus a full-core integration test (`tb/tb_riscv_core.v`) that runs three
hand-assembled programs — general ALU ops, a branch loop, and load/store
round trips with sign/zero extension — and checks their results directly
in data memory. `sim/Makefile`'s `make sim` target runs all of it.

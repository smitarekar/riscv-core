# riscv-core

A single-cycle RV32I core I wrote in Verilog to actually understand
the ISA end to end, not just read about it. Every module has its own
testbench, and the whole thing runs three hand-assembled programs to
prove the datapath is wired up correctly, not just that it compiles.

```
$ cd sim && make sim
...
PASS [arithmetic_mem0] = 35
PASS [sum_loop_mem4] = 55
PASS [loadstore_pass_flag] = 1
PASS [macc_single_mem0] = 142
PASS [macc_single_aliasing_mem4] = 9
PASS [macc_dot_product_mem0] = 300
PASS [macc_overflow_mem0] = 1
RISCV_CORE TB: PASS (7 checks)
GOLDEN [macc_single_mem0] = 142 (matches sim)
GOLDEN [macc_single_aliasing_mem4] = 9 (matches sim)
GOLDEN [macc_dot_product_mem0] = 300 (matches sim)
GOLDEN [macc_overflow_mem0] = 1 (matches sim)
GOLDEN_CHECK: PASS (4 checks)
```

[`docs/architecture.md`](docs/architecture.md) has the datapath
diagram and the reasoning behind a few of the design choices,
including one funct7 aliasing gotcha that almost got past me.

## MACC

A custom multiply-accumulate instruction on top of RV32I: `MACC rd,
rs1, rs2` computes `rd = rd + (rs1 * rs2)` in one cycle. It exists
because dot-product-style workloads (the core of most ML inference
math) are otherwise a MUL + ADD pair per element, doubling both
instruction count and register-file traffic. `docs/architecture.md`
has the encoding, the datapath change, and the overflow semantics.

## Why single-cycle

Pipelining is the obvious next step for "impressive," but it also
drags in hazard detection and forwarding, which is a different problem
from "does this correctly implement RV32I." I wanted to nail the ISA
first. Might come back and pipeline it later.

## Layout

```
rtl/    synthesizable Verilog sources
tb/     testbenches + hand-assembled test programs
sim/    Makefile for Icarus Verilog
docs/   architecture notes + datapath diagrams
```

## What's implemented

R-type (ADD/SUB/SLL/SLT/SLTU/XOR/SRL/SRA/OR/AND), I-type ALU ops,
LB/LH/LW/LBU/LHU, SB/SH/SW, BEQ/BNE/BLT/BGE/BLTU/BGEU, JAL/JALR,
LUI/AUIPC, plus MACC (custom-0 opcode, not part of RV32I). No
FENCE/ECALL/CSRs, so no exceptions or interrupts — wasn't trying to
boot an OS on this.

## Building it

Needs [Icarus Verilog](http://iverilog.icarus.com/).

```
cd sim
make sim     # assembles the test programs, runs every unit test, the full core,
             # then cross-checks the MACC results against tb/golden_model.py
make wave    # pops the last VCD open in gtkwave
```

`make sim`'s last step (`make golden`) runs `tb/check_against_golden.py`
on its own: an independent Python model decodes and executes the same
instruction words the Verilog core does, and the script diffs its
results against what the simulation actually printed. It's how the
`halt`-pseudo-op bug in `docs/architecture.md` got caught.

Individual modules have their own testbench too, if you just want to
poke at one:

```
iverilog -o /tmp/tb_alu.vvp rtl/alu.v tb/tb_alu.v && vvp /tmp/tb_alu.vvp
```

## License

MIT — see [LICENSE](LICENSE).

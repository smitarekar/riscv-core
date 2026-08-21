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
PASS [dstore_pass_flag] = 1
RISCV_CORE TB: PASS (3 checks)
```

[`docs/architecture.md`](docs/architecture.md) has the datapath
diagram and the reasoning behind a few of the design choices,
including one funct7 aliasing gotcha that almost got past me.

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
docs/   architecture notes + datapath diagram
```

## What's implemented

R-type (ADD/SUB/SLL/SLT/SLTU/XOR/SRL/SRA/OR/AND), I-type ALU ops,
LB/LH/LW/LBU/LHU, SB/SH/SW, BEQ/BNE/BLT/BGE/BLTU/BGEU, JAL/JALR,
LUI/AUIPC. No FENCE/ECALL/CSRs, so no exceptions or interrupts —
wasn't trying to boot an OS on this.

## Building it

Needs [Icarus Verilog](http://iverilog.icarus.com/).

```
cd sim
make sim     # assembles the test programs, runs every unit test, then the full core
make wave    # pops the last VCD open in gtkwave
```

Individual modules have their own testbench too, if you just want to
poke at one:

```
iverilog -o /tmp/tb_alu.vvp rtl/alu.v tb/tb_alu.v && vvp /tmp/tb_alu.vvp
```

## License

MIT — see [LICENSE](LICENSE).

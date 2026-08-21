# riscv-core

A single-cycle RV32I RISC-V core written in Verilog, verified against
hand-assembled test programs.

```
$ cd sim && make sim
...
PASS [arithmetic_mem0] = 35
PASS [sum_loop_mem4] = 55
PASS [dstore_pass_flag] = 1
RISCV_CORE TB: PASS (3 checks)
```

See [`docs/architecture.md`](docs/architecture.md) for the datapath
diagram, module breakdown, and design decisions.

## Goals

- Implement the RV32I base integer instruction set on a single-cycle datapath.
- Verify against hand-written assembly programs using a self-checking testbench.
- Keep the design simple and readable over squeezing out performance —
  this is a learning/portfolio project, not a production core.

## Layout

```
rtl/    synthesizable Verilog sources
tb/     testbench + assembly test programs
sim/    Makefile for Icarus Verilog simulation
docs/   architecture notes
```

## Supported instructions (RV32I subset)

R-type (ADD/SUB/SLL/SLT/SLTU/XOR/SRL/SRA/OR/AND), I-type ALU ops,
LB/LH/LW/LBU/LHU, SB/SH/SW, BEQ/BNE/BLT/BGE/BLTU/BGEU, JAL/JALR,
LUI/AUIPC. No FENCE/ECALL/CSR — no exceptions or interrupts.

## Build & simulate

Requires [Icarus Verilog](http://iverilog.icarus.com/).

```
cd sim
make sim     # assemble test programs, run unit tests, run full-core test
make wave    # open the last VCD in gtkwave
```

Each module also has its own standalone testbench under `tb/` if you want
to run/inspect one in isolation, e.g.:

```
iverilog -o /tmp/tb_alu.vvp rtl/alu.v tb/tb_alu.v && vvp /tmp/tb_alu.vvp
```

## License

MIT — see [LICENSE](LICENSE).

# riscv-core

A single-cycle RV32I RISC-V core written in Verilog.

**Status:** work in progress. See commit history for build-up order (ALU →
register file → control unit → datapath → sample programs).

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

## Build & simulate

Requires [Icarus Verilog](http://iverilog.icarus.com/).

```
cd sim
make sim     # run all test programs
make wave    # open the last VCD in gtkwave
```

## License

MIT — see [LICENSE](LICENSE).

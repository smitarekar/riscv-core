#!/usr/bin/env python3
"""Cross-checks the Verilog simulation's MACC results against golden_model.py,
independently of the hardcoded expected constants in tb_riscv_core.v.

This is a second, independent verification layer on top of the Verilog
testbench's own self-checking: tb_riscv_core.v already asserts its
results against constants I wrote by hand, which means a mistake in my
arithmetic would show up as a "passing" test that's actually checking
the wrong number. This script re-derives those same expected values
from scratch (golden_model.py decodes and executes the raw instruction
words, it doesn't know what tb_riscv_core.v expects) and diffs them
against what the simulation actually printed.

Usage: python3 tb/check_against_golden.py
Run from the repo root. Builds and runs the Verilog simulation itself.
"""
import re
import subprocess
import sys
from pathlib import Path

from golden_model import Core, load_hex

REPO_ROOT = Path(__file__).resolve().parent.parent

# check name (as printed by tb_riscv_core.v) -> (program, mem byte address)
MACC_CHECKS = {
    "macc_single_mem0": ("macc_single", 0),
    "macc_single_aliasing_mem4": ("macc_single", 4),
    "macc_dot_product_mem0": ("macc_dot_product", 0),
    "macc_overflow_mem0": ("macc_overflow", 0),
}


def golden_mem_word(program, addr):
    core = Core()
    hexfile = REPO_ROOT / "tb" / "programs" / f"{program}.hex"
    core.run(load_hex(hexfile))
    return int.from_bytes(core.mem[addr:addr + 4], "little")


def run_verilog_sim():
    # tb_riscv_core.v instantiates a core per program, so every .hex this
    # repo's programs need has to exist before it will even elaborate.
    subprocess.run(["make", "-C", "sim", "programs"], cwd=REPO_ROOT, check=True)
    rtl = sorted((REPO_ROOT / "rtl").glob("*.v"))
    vvp_path = REPO_ROOT / "sim" / "_golden_check.vvp"
    subprocess.run(
        ["iverilog", "-o", str(vvp_path)] + [str(p) for p in rtl] + ["tb/tb_riscv_core.v"],
        cwd=REPO_ROOT, check=True,
    )
    result = subprocess.run(
        ["vvp", str(vvp_path)], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True,
    )
    return result.stdout


def parse_sim_output(output):
    """Returns {name: int(value)} for every PASS/FAIL line the sim printed."""
    values = {}
    for line in output.splitlines():
        m = re.match(r"(?:PASS|FAIL) \[(\w+)\] (?:= |got=)(-?\d+)", line)
        if m:
            values[m.group(1)] = int(m.group(2))
    return values


def main():
    sim_output = run_verilog_sim()
    sim_values = parse_sim_output(sim_output)

    errors = 0
    for name, (program, addr) in MACC_CHECKS.items():
        expected = golden_mem_word(program, addr)
        if name not in sim_values:
            errors += 1
            print(f"GOLDEN FAIL [{name}] simulation never printed this check name")
            continue
        actual = sim_values[name]
        if actual == expected:
            print(f"GOLDEN [{name}] = {actual} (matches sim)")
        else:
            errors += 1
            print(f"GOLDEN FAIL [{name}] sim={actual} golden={expected}")

    if errors == 0:
        print(f"GOLDEN_CHECK: PASS ({len(MACC_CHECKS)} checks)")
    else:
        print(f"GOLDEN_CHECK: FAIL ({errors}/{len(MACC_CHECKS)} checks failed)")
        sys.exit(1)


if __name__ == "__main__":
    main()

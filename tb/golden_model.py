#!/usr/bin/env python3
"""Minimal RV32I(+MACC) instruction-level reference model.

Independently decodes and executes the same hex-encoded instruction
words the Verilog core runs (same $readmemh-format file instr_mem.v
loads), so "expected" values for the MACC test programs come from a
second, from-scratch implementation of the ISA rather than from
hand-computed constants that could just repeat the same arithmetic
mistake twice.

Deliberately not a full ISA simulator -- only the instructions the
MACC test programs actually use: ADDI, MACC, SW, and the JAL-based
HALT idiom (`jal x0, 0`, asm_to_hex.py's `halt`).

Usage: golden_model.py program.hex
Prints one "name=value" line per store this run made, in order.
"""
import sys


def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


class Core:
    def __init__(self):
        self.regs = [0] * 32
        self.mem = bytearray(4096)
        self.pc = 0

    def read_reg(self, i):
        return 0 if i == 0 else self.regs[i]

    def write_reg(self, i, value):
        if i != 0:
            self.regs[i] = value & 0xFFFFFFFF

    def store_word(self, addr, value):
        value &= 0xFFFFFFFF
        self.mem[addr:addr + 4] = value.to_bytes(4, "little")

    def load_word(self, addr):
        return int.from_bytes(self.mem[addr:addr + 4], "little")

    def step(self, instr):
        """Executes one instruction. Returns False if it was the HALT idiom."""
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        imm_i = sign_extend(instr >> 20, 12)

        next_pc = self.pc + 4

        if opcode == 0b0010011 and funct3 == 0b000:  # ADDI
            self.write_reg(rd, self.read_reg(rs1) + imm_i)

        elif opcode == 0b0100011 and funct3 == 0b010:  # SW
            imm_s = sign_extend(((instr >> 25) << 5) | ((instr >> 7) & 0x1F), 12)
            addr = (self.read_reg(rs1) + imm_s) & 0xFFFFFFFF
            self.store_word(addr, self.read_reg(rs2))

        elif opcode == 0b0001011 and funct3 == 0b000:  # MACC (custom-0)
            acc = self.read_reg(rd)
            a = self.read_reg(rs1)
            b = self.read_reg(rs2)
            self.write_reg(rd, acc + a * b)

        elif opcode == 0b1101111:  # JAL -- only used here as `jal x0, 0` (HALT)
            imm_j = sign_extend(
                (((instr >> 31) & 0x1) << 20)
                | (((instr >> 21) & 0x3FF) << 1)
                | (((instr >> 20) & 0x1) << 11)
                | (((instr >> 12) & 0xFF) << 12),
                21,
            )
            if rd == 0 and imm_j == 0:
                return False
            next_pc = self.pc + imm_j

        else:
            raise NotImplementedError(
                f"golden model does not implement opcode={opcode:#09b} "
                f"funct3={funct3:#05b} (instr={instr:#010x} at pc={self.pc})"
            )

        self.pc = next_pc & 0xFFFFFFFF
        return True

    def run(self, program, max_steps=1000):
        for _ in range(max_steps):
            index = self.pc // 4
            if index >= len(program):
                raise RuntimeError(f"pc {self.pc:#x} ran off the end of the program")
            if not self.step(program[index]):
                return
        raise RuntimeError(f"did not halt within {max_steps} steps")


def load_hex(path):
    with open(path) as f:
        return [int(line.strip(), 16) for line in f if line.strip()]


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    core = Core()
    core.run(load_hex(sys.argv[1]))

    for i, value in enumerate(core.regs):
        if value != 0:
            print(f"x{i}={value} (0x{value:08x})")
    print(f"mem[0:32]={core.mem[0:32].hex()}")


if __name__ == "__main__":
    main()

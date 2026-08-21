#!/usr/bin/env python3
"""Tiny two-pass assembler for the RV32I subset this core implements.

Usage: asm_to_hex.py input.s output.hex

Output is one 32-bit instruction per line in hex, suitable for
Verilog's $readmemh (matches instr_mem.v's word-addressed ROM).
"""
import re
import sys

REGS = {f"x{i}": i for i in range(32)}
REGS.update({
    "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,
    "t0": 5, "t1": 6, "t2": 7,
    "s0": 8, "fp": 8, "s1": 9,
    "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a5": 15, "a6": 16, "a7": 17,
    "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23,
    "s8": 24, "s9": 25, "s10": 26, "s11": 27,
    "t3": 28, "t4": 29, "t5": 30, "t6": 31,
})

R_TYPE = {
    # mnemonic: (funct7, funct3, opcode)
    "add":  (0b0000000, 0b000, 0b0110011),
    "sub":  (0b0100000, 0b000, 0b0110011),
    "sll":  (0b0000000, 0b001, 0b0110011),
    "slt":  (0b0000000, 0b010, 0b0110011),
    "sltu": (0b0000000, 0b011, 0b0110011),
    "xor":  (0b0000000, 0b100, 0b0110011),
    "srl":  (0b0000000, 0b101, 0b0110011),
    "sra":  (0b0100000, 0b101, 0b0110011),
    "or":   (0b0000000, 0b110, 0b0110011),
    "and":  (0b0000000, 0b111, 0b0110011),
    # custom-0 (opcode 0001011): rd = rd + (rs1 * rs2). funct7=0000001 is
    # the documented encoding; see docs/architecture.md.
    "macc": (0b0000001, 0b000, 0b0001011),
}
I_TYPE_ALU = {
    # mnemonic: (funct3, opcode)
    "addi":  (0b000, 0b0010011),
    "slti":  (0b010, 0b0010011),
    "sltiu": (0b011, 0b0010011),
    "xori":  (0b100, 0b0010011),
    "ori":   (0b110, 0b0010011),
    "andi":  (0b111, 0b0010011),
}
I_TYPE_SHIFT = {
    # mnemonic: (funct7, funct3, opcode)
    "slli": (0b0000000, 0b001, 0b0010011),
    "srli": (0b0000000, 0b101, 0b0010011),
    "srai": (0b0100000, 0b101, 0b0010011),
}
LOADS = {
    "lb":  (0b000, 0b0000011),
    "lh":  (0b001, 0b0000011),
    "lw":  (0b010, 0b0000011),
    "lbu": (0b100, 0b0000011),
    "lhu": (0b101, 0b0000011),
}
STORES = {
    "sb": (0b000, 0b0100011),
    "sh": (0b001, 0b0100011),
    "sw": (0b010, 0b0100011),
}
BRANCHES = {
    "beq":  0b000, "bne": 0b001, "blt": 0b100,
    "bge":  0b101, "bltu": 0b110, "bgeu": 0b111,
}


def reg(tok):
    tok = tok.strip().rstrip(",")
    if tok not in REGS:
        raise ValueError(f"unknown register: {tok}")
    return REGS[tok]


def imm_bits(val, bits):
    mask = (1 << bits) - 1
    return val & mask


def parse_operands(s):
    return [t for t in re.split(r"[,\s]+", s.strip()) if t]


def parse_mem_operand(tok):
    # form: offset(reg)
    m = re.match(r"(-?\w+)\(([a-z0-9]+)\)", tok)
    if not m:
        raise ValueError(f"bad memory operand: {tok}")
    return int(m.group(1), 0), reg(m.group(2))


def strip_comment(line):
    return line.split("#", 1)[0].rstrip()


def first_pass(lines):
    """Assign addresses, collect label -> address map."""
    labels = {}
    addr = 0
    cleaned = []
    for raw in lines:
        line = strip_comment(raw).strip()
        if not line:
            continue
        if line.endswith(":"):
            labels[line[:-1]] = addr
            continue
        cleaned.append((addr, line))
        addr += 4
    return labels, cleaned


def encode(addr, line, labels):
    parts = line.split(None, 1)
    mnem = parts[0].lower()
    ops = parse_operands(parts[1]) if len(parts) > 1 else []

    if mnem == "nop":
        mnem, ops = "addi", ["x0", "x0", "0"]
    elif mnem == "halt":
        mnem, ops = "jal", ["x0", "0"]  # infinite self-loop
    elif mnem == "j":
        mnem, ops = "jal", ["x0", ops[0]]
    elif mnem == "ret":
        mnem, ops = "jalr", ["x0", "0(ra)"]
    elif mnem == "mv":
        mnem, ops = "addi", [ops[0], ops[1], "0"]
    elif mnem == "li":
        # only small immediates needed for our test programs
        mnem, ops = "addi", [ops[0], "x0", ops[1]]
    elif mnem == "beqz":
        mnem, ops = "beq", [ops[0], "x0", ops[1]]
    elif mnem == "bnez":
        mnem, ops = "bne", [ops[0], "x0", ops[1]]

    if mnem in R_TYPE:
        funct7, funct3, opcode = R_TYPE[mnem]
        rd, rs1, rs2 = reg(ops[0]), reg(ops[1]), reg(ops[2])
        return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

    if mnem in I_TYPE_ALU:
        funct3, opcode = I_TYPE_ALU[mnem]
        rd, rs1 = reg(ops[0]), reg(ops[1])
        imm = imm_bits(int(ops[2], 0), 12)
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

    if mnem in I_TYPE_SHIFT:
        funct7, funct3, opcode = I_TYPE_SHIFT[mnem]
        rd, rs1 = reg(ops[0]), reg(ops[1])
        shamt = int(ops[2], 0) & 0x1F
        return (funct7 << 25) | (shamt << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

    if mnem in LOADS:
        funct3, opcode = LOADS[mnem]
        rd = reg(ops[0])
        off, rs1 = parse_mem_operand(ops[1])
        imm = imm_bits(off, 12)
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

    if mnem in STORES:
        funct3, opcode = STORES[mnem]
        rs2 = reg(ops[0])
        off, rs1 = parse_mem_operand(ops[1])
        imm = imm_bits(off, 12)
        imm_11_5 = (imm >> 5) & 0x7F
        imm_4_0 = imm & 0x1F
        return (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode

    if mnem in BRANCHES:
        funct3 = BRANCHES[mnem]
        opcode = 0b1100011
        rs1, rs2 = reg(ops[0]), reg(ops[1])
        # A label resolves to an absolute address, so it needs off=target-addr
        # to become PC-relative. A bare number is already meant as the
        # relative offset itself (this is what makes `halt` -> `jal x0, 0`
        # a true self-loop instead of a jump back to address 0).
        off = (labels[ops[2]] - addr) if ops[2] in labels else int(ops[2], 0)
        imm = imm_bits(off, 13)
        b12 = (imm >> 12) & 1
        b11 = (imm >> 11) & 1
        b10_5 = (imm >> 5) & 0x3F
        b4_1 = (imm >> 1) & 0xF
        return (b12 << 31) | (b10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (b4_1 << 8) | (b11 << 7) | opcode

    if mnem == "jal":
        rd = reg(ops[0])
        # See the identical comment in the BRANCHES case just above.
        off = (labels[ops[1]] - addr) if ops[1] in labels else int(ops[1], 0)
        imm = imm_bits(off, 21)
        b20 = (imm >> 20) & 1
        b19_12 = (imm >> 12) & 0xFF
        b11 = (imm >> 11) & 1
        b10_1 = (imm >> 1) & 0x3FF
        return (b20 << 31) | (b10_1 << 21) | (b11 << 20) | (b19_12 << 12) | (rd << 7) | 0b1101111

    if mnem == "jalr":
        rd = reg(ops[0])
        off, rs1 = parse_mem_operand(ops[1])
        imm = imm_bits(off, 12)
        return (imm << 20) | (rs1 << 15) | (0b000 << 12) | (rd << 7) | 0b1100111

    if mnem in ("lui", "auipc"):
        rd = reg(ops[0])
        imm20 = int(ops[1], 0) & 0xFFFFF
        opcode = 0b0110111 if mnem == "lui" else 0b0010111
        return (imm20 << 12) | (rd << 7) | opcode

    raise ValueError(f"unsupported mnemonic: {mnem}")


def assemble(text):
    labels, cleaned = first_pass(text.splitlines())
    words = []
    for addr, line in cleaned:
        words.append(encode(addr, line, labels))
    return words


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        src = f.read()
    words = assemble(src)
    with open(sys.argv[2], "w") as f:
        for w in words:
            f.write(f"{w & 0xFFFFFFFF:08x}\n")
    print(f"assembled {len(words)} instructions -> {sys.argv[2]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the portfolio banner SVGs.

One script for every repo, so a palette or layout change is a single edit.
The spec it implements is fixed in DIAGRAM_STYLE.md: 1200x200, dark ground,
monospace type, no personal name and no tagline.

The right-hand third of each banner carries a drawn motif chosen for what
that repo actually is: a serial frame for the UARTs, a crossbar mesh for
axi4-crossbar, a PE grid with its wavefront for the systolic arrays, a die
floorplan for the ASIC flow. Vector, generated, no raster assets.

    python3 gen_banners.py            # write every banner
    python3 gen_banners.py apb-uart   # write one
"""

import sys
from pathlib import Path

W, H = 1200, 200
PAD = 52

GROUND = "#0f172a"
NAME_FILL = "#f8fafc"
SUB_FILL = "#cbd5e1"
MUTED = "#64748b"
LINE = "#64748b"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

PROCESS, STORAGE, INPUT = "#c7d2fe", "#99f6e4", "#bfdbfe"
RISK, EXTERNAL, NEUTRAL = "#fecaca", "#fde68a", "#e2e8f0"
ACCENT = "#d97706"

# motif box
MX, MY, MW, MH = 720, 30, 428, 140
ADV = 0.60


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def box(x, y, w, h, fill, op=1.0, r=2, stroke=LINE, sw=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" fill="{fill}" fill-opacity="{op:.2f}" stroke="{stroke}" '
            f'stroke-width="{sw}"/>')


def line(x1, y1, x2, y2, c=LINE, sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{c}" stroke-width="{sw}"{d}/>')


def path(d, c=LINE, sw=1.2, fill="none"):
    return f'<path d="{d}" stroke="{c}" stroke-width="{sw}" fill="{fill}"/>'


def txt(x, y, s, size=9, c=MUTED, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" '
            f'font-size="{size}" fill="{c}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{esc(s)}</text>')


def dot(x, y, r=3.5, fill=PROCESS):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
            f'stroke="{LINE}" stroke-width="1"/>')


# --- motifs ----------------------------------------------------------------
# Each returns SVG drawn inside (MX, MY, MW, MH).

def motif_uart_frame():
    """8N1 serial frame: idle, start bit, eight data bits, stop, with the
    mid-bit sample points marked."""
    o = []
    x0, hi, lo = MX + 10, MY + 52, MY + 88
    bw = 33
    bits = [0, 1, 0, 1, 1, 0, 1, 0]
    d = [f"M{x0} {hi}", f"L{x0 + 26} {hi}", f"L{x0 + 26} {lo}",
         f"L{x0 + 26 + bw} {lo}"]
    x = x0 + 26 + bw
    prev = 0
    for b in bits:
        y = hi if b else lo
        if b != prev:
            d.append(f"L{x} {y}")
        d.append(f"L{x + bw} {y}")
        x += bw
        prev = b
    d.append(f"L{x} {hi}")
    d.append(f"L{x + 30} {hi}")
    o.append(path(" ".join(d), PROCESS, 2.2))
    # span brackets
    s0, s1 = x0 + 26, x0 + 26 + bw
    o.append(line(s0, MY + 34, s0, lo + 6, RISK, 1, "2 2"))
    o.append(line(s1, MY + 34, s1, lo + 6, RISK, 1, "2 2"))
    o.append(txt((s0 + s1) / 2, MY + 30, "start", 8, RISK, "middle"))
    o.append(line(x, MY + 34, x, hi + 6, STORAGE, 1, "2 2"))
    o.append(txt(x + 15, MY + 30, "stop", 8, STORAGE, "middle"))
    o.append(txt(x0, MY + 46, "idle", 8, MUTED))
    for i in range(9):
        cx = s1 + bw * i + bw / 2
        o.append(line(cx, lo + 10, cx, lo + 18, ACCENT, 1.4))
    o.append(txt(s1 + bw * 4.5, lo + 32, "resync at tick 7, sample every 16", 8, ACCENT, "middle"))
    return o


def motif_testbench():
    """Two independent paths meeting at a comparison."""
    o = []
    y1, y2 = MY + 34, MY + 96
    o.append(box(MX + 4, y1, 78, 30, INPUT))
    o.append(txt(MX + 43, y1 + 19, "driver", 9, "#1a1a1a", "middle"))
    o.append(box(MX + 116, y1, 66, 30, STORAGE))
    o.append(txt(MX + 149, y1 + 19, "DUT", 9, "#1a1a1a", "middle"))
    o.append(box(MX + 116, y2, 66, 30, EXTERNAL))
    o.append(txt(MX + 149, y2 + 19, "monitor", 8, "#1a1a1a", "middle"))
    o.append(line(MX + 82, y1 + 15, MX + 116, y1 + 15))
    o.append(path(f"M{MX + 149} {y1 + 30} L{MX + 149} {y2}", LINE))
    o.append(path(f"M{MX + 43} {y1 + 30} L{MX + 43} {y2 + 15} L{MX + 116} {y2 + 15}",
                  LINE, 1.2))
    cx, cy = MX + 268, MY + 70
    o.append(f'<path d="M{cx} {cy - 26} L{cx + 30} {cy} L{cx} {cy + 26} '
             f'L{cx - 30} {cy} Z" fill="{RISK}" stroke="{LINE}" stroke-width="1"/>')
    o.append(txt(cx, cy + 5, "=", 15, "#1a1a1a", "middle", "700"))
    o.append(path(f"M{MX + 182} {y1 + 15} L{cx - 14} {y1 + 15} L{cx - 14} {cy - 12}",
                  LINE))
    o.append(path(f"M{MX + 182} {y2 + 15} L{cx - 14} {y2 + 15} L{cx - 14} {cy + 12}",
                  LINE))
    o.append(txt(cx + 44, cy + 4, "MATCH", 9, ACCENT))
    o.append(line(cx + 30, cy, cx + 40, cy, ACCENT, 1.6))
    return o


def motif_crossbar():
    """Two masters over three slaves, dots at the live crosspoints."""
    o = []
    mx0, my0 = MX + 66, MY + 40
    rows = [my0, my0 + 34]
    cols = [mx0 + 60, mx0 + 140, mx0 + 220]
    for i, y in enumerate(rows):
        o.append(line(mx0, y, mx0 + 268, y, PROCESS, 1.6))
        o.append(txt(mx0 - 8, y + 4, f"M{i}", 9, MUTED, "end"))
    for j, x in enumerate(cols):
        o.append(line(x, my0 - 22, x, my0 + 70, INPUT, 1.6))
        o.append(txt(x, my0 + 88, f"S{j}", 9, MUTED, "middle"))
    for (i, j) in ((0, 0), (0, 2), (1, 1)):
        o.append(dot(cols[j], rows[i], 4.5, STORAGE))
    o.append(dot(cols[2], rows[1], 4.5, RISK))
    o.append(txt(MX + 6, MY + 22, "2x3 crossbar", 9, MUTED))
    return o


def motif_pe_grid(wavefront=True):
    """NxN processing elements with the diagonal wavefront stepped by opacity."""
    o = []
    n, cell, gap = 4, 26, 5
    gx, gy = MX + 96, MY + 28
    for r in range(n):
        for c in range(n):
            op = 1.0 - 0.07 * ((r + c) % 4) if wavefront else 1.0
            o.append(box(gx + c * (cell + gap), gy + r * (cell + gap),
                         cell, cell, PROCESS, op, r=2))
    for r in range(n):
        y = gy + r * (cell + gap) + cell / 2
        o.append(line(gx - 26, y, gx - 4, y, INPUT, 1.4))
    for c in range(n):
        x = gx + c * (cell + gap) + cell / 2
        o.append(line(x, gy - 22, x, gy - 4, EXTERNAL, 1.4))
    o.append(txt(gx - 30, gy - 12, "data", 8, MUTED, "end"))
    o.append(txt(gx + 4 * (cell + gap) + 6, gy - 12, "weights", 8, MUTED))
    span = n * (cell + gap) - gap
    o.append(path(f"M{gx + span + 8} {gy} L{gx + span + 8} {gy + span}", ACCENT, 1.6))
    o.append(txt(gx + span + 14, gy + span / 2 + 4, "psum", 8, ACCENT))
    return o


def motif_datapath():
    """A single-cycle core: fetch through writeback, with the MACC beside the ALU."""
    o = []
    y = MY + 44
    stages = [("PC", INPUT, 40), ("IMEM", STORAGE, 46), ("dec", INPUT, 40),
              ("RF", STORAGE, 40), ("ALU", PROCESS, 42), ("DMEM", STORAGE, 50)]
    x = MX + 4
    centers = []
    for label, fill, w in stages:
        o.append(box(x, y, w, 30, fill))
        o.append(txt(x + w / 2, y + 19, label, 8, "#1a1a1a", "middle"))
        centers.append((x, w))
        x += w + 14
    for i in range(len(stages) - 1):
        xa = centers[i][0] + centers[i][1]
        o.append(line(xa, y + 15, xa + 14, y + 15))
    ax = centers[4][0]
    o.append(box(ax, y + 44, 42, 26, PROCESS))
    o.append(txt(ax + 21, y + 61, "MACC", 8, "#1a1a1a", "middle"))
    o.append(line(ax + 21, y + 30, ax + 21, y + 44, LINE, 1.2))
    xe = centers[5][0] + centers[5][1]
    rf = centers[3][0] + centers[3][1] / 2
    o.append(path(f"M{xe} {y + 15} L{xe + 12} {y + 15} L{xe + 12} {y - 18} "
                  f"L{rf} {y - 18} L{rf} {y}", ACCENT, 1.6))
    o.append(txt(rf + 18, y - 22, "writeback", 8, ACCENT))
    return o


def motif_kalman():
    """Predict widens the covariance, update narrows it. The loop is the point."""
    o = []
    cy = MY + 82
    o.append(f'<ellipse cx="{MX + 62}" cy="{cy}" rx="38" ry="29" fill="{RISK}" '
             f'fill-opacity="0.85" stroke="{LINE}" stroke-width="1"/>')
    o.append(txt(MX + 62, cy + 46, "predict", 8, RISK, "middle"))
    o.append(f'<ellipse cx="{MX + 206}" cy="{cy}" rx="17" ry="12" fill="{STORAGE}" '
             f'stroke="{LINE}" stroke-width="1"/>')
    o.append(txt(MX + 206, cy + 46, "update", 8, STORAGE, "middle"))
    o.append(path(f"M{MX + 104} {cy} L{MX + 184} {cy}", PROCESS, 2))
    o.append(txt(MX + 144, cy - 8, "measure", 8, MUTED, "middle"))
    o.append(path(f"M{MX + 206} {cy - 14} C{MX + 206} {cy - 62} "
                  f"{MX + 62} {cy - 62} {MX + 62} {cy - 31}", ACCENT, 1.8))
    o.append(txt(MX + 134, cy - 56, "propagate", 8, ACCENT, "middle"))
    for i, r in enumerate((3, 4.5, 6)):
        o.append(dot(MX + 268 + i * 22, cy - 10 + i * 11, r, INPUT))
    o.append(txt(MX + 290, cy + 46, "track", 8, MUTED, "middle"))
    return o


def motif_memhier():
    """Nested memory tiers, outlined rather than filled so they stay legible
    on the dark ground, with one tile resident in the fastest one."""
    o = []
    tiers = [("device memory", NEUTRAL, MX + 4, MY + 8, 300, 128),
             ("threadgroup", INPUT, MX + 30, MY + 34, 248, 92),
             ("registers", PROCESS, MX + 56, MY + 60, 196, 56)]
    for label, stroke, x, y, w, h in tiers:
        o.append(box(x, y, w, h, stroke, 0.09, r=3, stroke=stroke, sw=1.4))
        o.append(txt(x + 8, y - 5, label, 8, stroke))
    gx, gy = MX + 70, MY + 70
    for r in range(2):
        for c in range(6):
            o.append(box(gx + c * 28, gy + r * 20, 22, 15, STORAGE, 1.0, r=1))
    o.append(txt(MX + 4, MY + 154, "one tile resident per threadgroup", 8, MUTED))
    return o


def motif_tlp():
    """A packet crossing two layers: TL frames it, DL wraps it with seq and CRC."""
    o = []
    y = MY + 46
    fields = [("seq", EXTERNAL, 40), ("hdr", INPUT, 56), ("payload", PROCESS, 110),
              ("ECRC", RISK, 44), ("LCRC", RISK, 44)]
    x = MX + 4
    for label, fill, w in fields:
        o.append(box(x, y, w, 28, fill))
        o.append(txt(x + w / 2, y + 18, label, 8, "#1a1a1a", "middle"))
        x += w + 3
    o.append(txt(MX + 4, MY + 32, "TLP", 9, MUTED))
    o.append(line(MX + 4, y + 42, x - 3, y + 42, LINE, 1))
    o.append(box(MX + 4, y + 50, 148, 24, PROCESS, 0.85))
    o.append(txt(MX + 78, y + 66, "transaction", 8, "#1a1a1a", "middle"))
    o.append(box(MX + 158, y + 50, 139, 24, PROCESS, 0.85))
    o.append(txt(MX + 227, y + 66, "data link", 8, "#1a1a1a", "middle"))
    o.append(path(f"M{MX + 300} {y + 14} L{MX + 318} {y + 14} L{MX + 318} {y + 62} "
                  f"L{MX + 297} {y + 62}", ACCENT, 1.4))
    o.append(txt(MX + 324, y + 40, "retry", 8, ACCENT))
    return o


def motif_die():
    """A die outline: seal ring, core, standard-cell rows, a little routing."""
    o = []
    dx, dy, dw, dh = MX + 70, MY + 6, 190, 138
    o.append(box(dx, dy, dw, dh, NEUTRAL, 0.16, r=1, stroke=LINE))
    o.append(box(dx + 12, dy + 12, dw - 24, dh - 24, GROUND, 1.0, r=1, stroke=LINE))
    rows = 9
    for i in range(rows):
        ry = dy + 20 + i * ((dh - 40) / rows)
        o.append(box(dx + 20, ry, dw - 40, 6, PROCESS, 0.48 + 0.10 * (i % 4), r=0,
                     stroke="none"))
    for i, fx in enumerate((0.28, 0.52, 0.74)):
        o.append(line(dx + dw * fx, dy + 18, dx + dw * fx, dy + dh - 18,
                      STORAGE, 1.2))
    o.append(line(dx + 20, dy + dh * 0.42, dx + dw - 20, dy + dh * 0.42, EXTERNAL, 1.2))
    for i in range(6):
        o.append(box(dx - 6, dy + 24 + i * 20, 6, 8, EXTERNAL, 1.0, r=0))
        o.append(box(dx + dw, dy + 24 + i * 20, 6, 8, EXTERNAL, 1.0, r=0))
    o.append(txt(MX + 4, MY + 70, "0.0176 mm2", 8, MUTED))
    o.append(txt(dx + dw + 16, dy + dh / 2, "530", 9, MUTED))
    o.append(txt(dx + dw + 16, dy + dh / 2 + 12, "cells", 8, MUTED))
    return o


def motif_inference():
    """A digit becomes activations, the array turns them into logits."""
    o = []
    gx, gy = MX + 4, MY + 40
    px = [[0, 1, 1, 0], [1, 0, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1]]
    for r, row in enumerate(px):
        for c, v in enumerate(row):
            o.append(box(gx + c * 13, gy + r * 13, 11, 11, STORAGE if v else NEUTRAL,
                         1.0 if v else 0.18, r=1, stroke="none"))
    o.append(txt(gx, gy + 84, "28x28", 8, MUTED))
    ax, ay = MX + 116, MY + 34
    for r in range(3):
        for c in range(3):
            o.append(box(ax + c * 24, ay + r * 24, 20, 20, PROCESS,
                         1.0 - 0.14 * ((r + c) % 4), r=2))
    o.append(txt(ax, ay + 90, "fc3 on PEs", 8, MUTED))
    bx = MX + 220
    vals = [0.18, 0.34, 0.22, 0.95, 0.28, 0.15, 0.41, 0.20, 0.30, 0.24]
    for i, v in enumerate(vals):
        h = 6 + v * 74
        fill = ACCENT if v > 0.9 else INPUT
        o.append(box(bx + i * 15, MY + 118 - h, 11, h, fill, 1.0, r=1, stroke="none"))
    o.append(txt(bx, MY + 134, "logits", 8, MUTED))
    return o


def motif_portfolio():
    """A shelf of the ten projects, one tile each."""
    o = []
    tiles = [PROCESS, INPUT, PROCESS, STORAGE, PROCESS,
             RISK, PROCESS, EXTERNAL, PROCESS, STORAGE]
    for i, fill in enumerate(tiles):
        c, r = i % 5, i // 5
        o.append(box(MX + 4 + c * 60, MY + 34 + r * 56, 52, 46, fill,
                     0.92, r=3))
    o.append(txt(MX + 4, MY + 24, "10 projects", 9, MUTED))
    return o


MOTIF = {
    "apb-uart": motif_uart_frame,
    "apb-uart-verification": motif_testbench,
    "axi4-crossbar": motif_crossbar,
    "ekf-target-tracker": motif_kalman,
    "metal-matmul": motif_memhier,
    "pcie-tl-dl": motif_tlp,
    "riscv-core": motif_datapath,
    "systolic-mm-accelerator": motif_pe_grid,
    "systolic-mnist-inference": motif_inference,
    "uart-asic-flow": motif_die,
    "vlsi-portfolio": motif_portfolio,
}

SPECS = {
    "apb-uart": ("APB3 UART peripheral with a 16x-oversampled receiver",
                 "4 testbenches - 4 registers"),
    "apb-uart-verification": ("cocotb + pyuvm environment for an APB UART",
                              "5/5 tests - 9/9 coverage bins"),
    "axi4-crossbar": ("Two-master, three-slave AXI4-Lite crossbar with an APB bridge",
                      "5 UVM tests - 7 directed"),
    "ekf-target-tracker": ("Fixed-point extended Kalman filter for range and bearing",
                           "4/4 cocotb suites"),
    "metal-matmul": ("Three Metal compute kernels for matrix multiply on Apple GPUs",
                     "3 kernels - 15 shapes"),
    "pcie-tl-dl": ("PCIe Gen1/Gen2 Transaction and Data Link layers",
                   "phase 1 - specification only"),
    "riscv-core": ("Single-cycle RV32I core with a custom MACC datapath",
                   "8 testbenches - golden check"),
    "systolic-mm-accelerator": ("Weight-stationary systolic matrix-multiply accelerator",
                                "3/3 cocotb - 3 directed"),
    "systolic-mnist-inference": ("Quantized MNIST inference running on the systolic array",
                                 "300/300 logits bit-exact"),
    "uart-asic-flow": ("OpenLane RTL-to-GDS flow for the APB UART",
                       "DRC/LVS clean - 1.2 ns path"),
}

PORTFOLIO_NAME = "vlsi-portfolio"
PORTFOLIO_SPEC = ("RTL design, verification and physical design", "10 projects")


def banner(name, subtitle, meta):
    size = 44
    if len(name) * size * ADV > 620:
        size = int(620 / (len(name) * ADV))

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(name)}">',
         f'<rect width="{W}" height="{H}" fill="{GROUND}"/>']

    o.append(f'<text x="{PAD}" y="83" font-family="{MONO}" font-size="{size}" '
             f'font-weight="700" fill="{NAME_FILL}" letter-spacing="-1">'
             f'{esc(name)}</text>')
    o.append(f'<text x="{PAD}" y="111" font-family="{MONO}" font-size="15" '
             f'fill="{SUB_FILL}">{esc(subtitle)}</text>')
    o.append(f'<text x="{PAD}" y="140" font-family="{MONO}" font-size="11" '
             f'fill="{MUTED}">{esc(meta)}</text>')

    o.extend(MOTIF[name]())
    o.append("</svg>")
    return "\n".join(o) + "\n"


def main():
    root = Path(__file__).resolve().parent
    while root != root.parent and not (root / "DIAGRAM_STYLE.md").exists():
        root = root.parent

    only = sys.argv[1] if len(sys.argv) > 1 else None

    for name, (subtitle, meta) in SPECS.items():
        if only and only != name:
            continue
        d = root / name / "diagrams"
        d.mkdir(parents=True, exist_ok=True)
        (d / "banner.svg").write_text(banner(name, subtitle, meta))
        print(f"wrote {name}/diagrams/banner.svg")

    if not only or only == PORTFOLIO_NAME:
        d = root / "diagrams"
        d.mkdir(parents=True, exist_ok=True)
        (d / "banner.svg").write_text(
            banner(PORTFOLIO_NAME, PORTFOLIO_SPEC[0], PORTFOLIO_SPEC[1]))
        print("wrote diagrams/banner.svg")


if __name__ == "__main__":
    main()

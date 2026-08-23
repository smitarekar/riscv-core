"""Reusable raw-SVG diagram builder for vlsi-portfolio docs.

Replaces the old draw.io + Python-generator + drawio-CLI pipeline
(see DIAGRAM_STYLE.md) with directly hand-authored SVG, per the
technical-svg-diagrams skill's mechanism -- but keeps the portfolio's
own established semantic color palette, box/edge conventions, and
legend requirement instead of that skill's default look.

Usage pattern: create a Diagram, add container()/box() elements
(each returns an anchor dict with edge-midpoint coordinates: n/s/e/w/
c), wire them with edge() using explicit waypoints, add a legend(),
then write(path).
"""

FILL = {
    "blue":   ("#dae8fc", "#6c8ebf"),
    "green":  ("#d5e8d4", "#82b366"),
    "orange": ("#ffe6cc", "#d79b00"),
    "purple": ("#e1d5e7", "#9673a6"),
    "red":    ("#f8cecc", "#b85450"),
    "yellow": ("#fff2cc", "#d6b656"),
    "gray":   ("#f5f5f5", "#666666"),
    "white":  ("#ffffff", "#d0d0d0"),
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


class Diagram:
    def __init__(self, width, height, title, subtitle=None):
        self.width = width
        self.height = height
        self.parts = []
        self.parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>')
        self.parts.append(
            f'<text x="20" y="34" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="18" font-weight="bold" fill="#1a1a1a">{esc(title)}</text>'
        )
        if subtitle:
            self.parts.append(
                f'<text x="20" y="54" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="12" fill="#666666">{esc(subtitle)}</text>'
            )

    # ---- boxes ----
    def box(self, x, y, w, h, label, color, rounded=True, fontsize=12, bold=False):
        fill, stroke = FILL[color]
        rx = 8 if rounded else 0
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        self._label(x, y, w, h, label, fontsize, bold)
        return {
            "n": (x + w / 2, y), "s": (x + w / 2, y + h),
            "e": (x + w, y + h / 2), "w": (x, y + h / 2),
            "c": (x + w / 2, y + h / 2),
            "box_x": x, "box_y": y, "box_w": w, "box_h": h,
        }

    def container(self, x, y, w, h, label):
        fill, stroke = FILL["gray"]
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" fill-opacity="0.5" stroke="{stroke}" stroke-width="1.25" '
            f'stroke-dasharray="4,3"/>'
        )
        self.parts.append(
            f'<text x="{x + 10}" y="{y + 18}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="12" font-weight="bold" fill="#666666">{esc(label)}</text>'
        )
        return {"x": x, "y": y, "w": w, "h": h}

    def _label(self, x, y, w, h, label, fontsize, bold):
        lines = label.split("\n")
        fw = ' font-weight="bold"' if bold else ""
        n = len(lines)
        line_h = fontsize + 3
        start_y = y + h / 2 - (n - 1) * line_h / 2 + fontsize / 3
        for i, line in enumerate(lines):
            self.parts.append(
                f'<text x="{x + w / 2}" y="{start_y + i * line_h}" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="{fontsize}"{fw} '
                f'fill="#1a1a1a" text-anchor="middle">{esc(line)}</text>'
            )

    # ---- edges ----
    @staticmethod
    def _point_at_fraction(points, frac):
        """True arc-length interpolation along a polyline -- not a
        waypoint-index snap, which lands exactly on box edges for
        short (2-point) edges and causes label/box overlap."""
        segs, total = [], 0.0
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            segs.append((x1, y1, x2, y2, length))
            total += length
        target = total * frac
        acc = 0.0
        for x1, y1, x2, y2, length in segs:
            if length == 0:
                continue
            if acc + length >= target:
                t = (target - acc) / length
                return (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
            acc += length
        return points[-1]

    def edge(self, points, label=None, color="#333333", dashed=False, width=1.5, label_pos=0.5, label_bg=True):
        """points: list of (x, y) waypoints; arrowhead at the last point."""
        d = f"M {points[0][0]} {points[0][1]} " + " ".join(f"L {x} {y}" for x, y in points[1:])
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        self.parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash} '
            f'marker-end="url(#arrow)"/>'
        )
        if label:
            lx, ly = self._point_at_fraction(points, label_pos)
            if label_bg:
                w = 7 * len(label) + 6
                self.parts.append(
                    f'<rect x="{lx - w/2}" y="{ly - 15}" width="{w}" height="14" fill="#ffffff" fill-opacity="0.85"/>'
                )
            self.parts.append(
                f'<text x="{lx}" y="{ly - 5}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="10" fill="#333333" text-anchor="middle">{esc(label)}</text>'
            )

    def text(self, x, y, s, fontsize=11, color="#666666", bold=False, italic=False, anchor="start"):
        fw = ' font-weight="bold"' if bold else ""
        fi = ' font-style="italic"' if italic else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{fontsize}"'
            f'{fw}{fi} fill="{color}" text-anchor="{anchor}">{esc(s)}</text>'
        )

    def wrapped_note(self, x, y, w, s, fontsize=11, color="#444444", line_h=15):
        """Simple greedy word-wrap for a bottom note paragraph."""
        words = s.split()
        max_chars = int(w / (fontsize * 0.56))
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if len(trial) > max_chars and cur:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        if cur:
            lines.append(cur)
        for i, line in enumerate(lines):
            self.parts.append(
                f'<text x="{x}" y="{y + i * line_h}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="{fontsize}" fill="{color}">{esc(line)}</text>'
            )
        return y + len(lines) * line_h

    # ---- legend ----
    def legend(self, entries, x, y, row_h=20, swatch=14):
        """entries: list of (color_key, text)."""
        for i, (color, desc) in enumerate(entries):
            fill, stroke = FILL[color]
            ly = y + i * row_h
            self.parts.append(
                f'<rect x="{x}" y="{ly}" width="{swatch}" height="{swatch}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1.25"/>'
            )
            self.parts.append(
                f'<text x="{x + swatch + 8}" y="{ly + swatch - 3}" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="11" fill="#333333">{esc(desc)}</text>'
            )
        return y + len(entries) * row_h

    def write(self, path):
        arrow = (
            '<marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" '
            'orient="auto" markerUnits="strokeWidth">'
            '<path d="M0,0 L0,6 L8,3 z" fill="#333333"/></marker>'
        )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}">\n'
            f'<defs>{arrow}</defs>\n' + "\n".join(self.parts) + "\n</svg>\n"
        )
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path} ({self.width}x{self.height})")

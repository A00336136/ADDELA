"""Shared drawing helpers for the DDELA report figures.

The figures are authored as SVG here and rendered to PNG with rsvg-convert, so
every figure in the write-ups can be regenerated from source rather than being
an undocumented binary. Wording is kept in step with the deployed system:
the gateway is the *centralized coordinator* (not an "orchestrator"/"sole
ingress"), and RQ2 is *offline drift detection*, not a continual-learning loop.
"""
FS = 1.0   # global font scale: figures are shrunk to page width, so type must be set large
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
INK, MUTED, LINE = "#16233c", "#667085", "#1f2d47"
RED, GREEN, BLUE, PURPLE, AMBER = "#d81324", "#0f7b3f", "#1868db", "#7c3aed", "#b7791f"
BOXFILL, BOXEDGE = "#eceff5", "#c7cfdd"
PALE = {"red": "#fff5f5", "green": "#f1f9f4", "blue": "#eef4fd", "purple": "#f6f1fe", "amber": "#fffaf0"}

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def box(x, y, w, h, fill=BOXFILL, edge=BOXEDGE, sw=1.6, r=12, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
            f'stroke="{edge}" stroke-width="{sw}"{d}/>')

def text(x, y, s, size=15, weight="normal", fill=INK, anchor="middle", style=""):
    it = ' font-style="italic"' if style == "i" else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{round(size*FS,2)}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{it}>{esc(s)}</text>')

def titled(x, y, w, h, lines, fill=BOXFILL, edge=BOXEDGE, sw=1.6):
    """A box whose first line is a bold title and the rest are muted detail."""
    out = [box(x, y, w, h, fill, edge, sw)]
    cy = y + h / 2 - (len(lines) - 1) * 11
    for i, (s, *rest) in enumerate(lines):
        kw = rest[0] if rest else {}
        out.append(text(x + w / 2, cy + i * 22 + 6,
                        s, kw.get("size", 17 if i == 0 else 13),
                        kw.get("weight", "bold" if i == 0 else "normal"),
                        kw.get("fill", INK if i == 0 else MUTED),
                        style=kw.get("style", "")))
    return "".join(out)

def chip(x, y, n, colour):
    return (f'<circle cx="{x}" cy="{y}" r="17" fill="{colour}" stroke="#ffffff" stroke-width="2.5"/>'
            + text(x, y + 6, str(n), 15, "bold", "#ffffff"))

def arrow(pts, colour=LINE, sw=2.2, dash=None, both=False, marker="ar"):
    d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
    da = f' stroke-dasharray="{dash}"' if dash else ""
    st = f' marker-start="url(#{marker}s-{colour[1:]})"' if both else ""
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{sw}"{da} '
            f'marker-end="url(#{marker}-{colour[1:]})"{st}/>')

def defs(colours):
    out = ['<defs>']
    for c in colours:
        out.append(f'<marker id="ar-{c[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="3.2" '
                   f'orient="auto"><path d="M0,0 L8,3.2 L0,6.4 Z" fill="{c}"/></marker>')
        out.append(f'<marker id="ars-{c[1:]}" markerWidth="10" markerHeight="10" refX="0" refY="3.2" '
                   f'orient="auto-start-reverse"><path d="M0,0 L8,3.2 L0,6.4 Z" fill="{c}"/></marker>')
    out.append('</defs>')
    return "".join(out)

def svg(w, h, body, colours):
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="{FONT}"><rect width="{w}" height="{h}" fill="#ffffff"/>'
            + defs(colours) + body + '</svg>')


# ── orthogonal routing ────────────────────────────────────────────────────────
# Arrowheads are held clear of the box they point at, and every turn is a real
# corner with room either side, so no head ever butts straight into an edge.
STANDOFF = 14
def route(pts, colour=LINE, sw=2.4, dash=None, both=False, standoff=STANDOFF):
    """Draw an orthogonal path through pts, trimming each end back by `standoff`."""
    pts = [tuple(p) for p in pts]
    def trim(a, b, d):
        (x1, y1), (x2, y2) = a, b
        L = ((x2-x1)**2 + (y2-y1)**2) ** 0.5
        if L <= d: return a
        return (x1 + (x2-x1)*d/L, y1 + (y2-y1)*d/L)
    pts[-1] = trim(pts[-1], pts[-2], standoff)
    if both:
        pts[0] = trim(pts[0], pts[1], standoff)
    d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    da = f' stroke-dasharray="{dash}"' if dash else ""
    st = f' marker-start="url(#ars-{colour[1:]})"' if both else ""
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{sw}" '
            f'stroke-linejoin="round" stroke-linecap="round"{da} '
            f'marker-end="url(#ar-{colour[1:]})"{st}/>')

def panel(x, y, w, h, title, colour, fill="#ffffff", dash=None, tsize=14):
    """A titled sub-panel: coloured header band over a light body."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" '
            f'stroke="{colour}" stroke-width="1.8"{d}/>'
            f'<path d="M{x},{y+44} L{x},{y+14} Q{x},{y} {x+14},{y} L{x+w-14},{y} '
            f'Q{x+w},{y} {x+w},{y+14} L{x+w},{y+44} Z" fill="{colour}" opacity="0.13"/>'
            + text(x + w/2, y + 29, title, tsize, "bold", colour))

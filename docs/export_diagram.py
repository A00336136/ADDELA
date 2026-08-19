"""Export the operator console's architecture diagram for the README.

The diagram is authored once, inline in the console template, so the picture in the
README can never drift from the picture the running system draws. This script lifts
that <svg> out verbatim and writes a standalone copy.

Run:  python3 docs/export_diagram.py
Then: rsvg-convert -w 1700 docs/architecture.svg -o docs/architecture.png
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
SRC = ROOT / "services/dashboard/templates/index.html"
OPEN_TAG = '<svg viewBox="0 0 1700 1150"'

html = SRC.read_text()
i = html.index(OPEN_TAG)
svg = html[i:html.index("</svg>", i) + 6]

# standalone: intrinsic size, a font that resolves outside the page, and a white ground
svg = svg.replace(
    OPEN_TAG + ' xmlns="http://www.w3.org/2000/svg">',
    OPEN_TAG + ' width="1700" height="1150" xmlns="http://www.w3.org/2000/svg" '
    "font-family=\"-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif\">\n"
    '<rect width="1700" height="1150" fill="#ffffff"/>')

dest = ROOT / "docs/architecture.svg"
dest.write_text(svg)
print(f"wrote {dest.relative_to(ROOT)}  ({len(svg):,} bytes)")

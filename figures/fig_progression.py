"""Methodology Figure 1, implementation and testing progression.

Stage 2 is no longer an evaluated research question: adaptation to threat drift
is carried as future work, so it is drawn outside the evaluated sequence.
Run:  python3 figures/fig_progression.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import _style
from _style import *
_style.FS = 1.30

W, H = 1400, 700
b = []
b.append(box(70, 40, W-140, 62, RED, RED, 1, 10))
b.append(text(110, 80, "Implementation and testing progression", 22, "bold", "#ffffff", "start"))
b.append(text(W-110, 78, "complexity increases at each stage", 13.5, "normal", "#ffffff", "end"))

b.append(f'<path d="M96,150 L96,470" stroke="{RED}" stroke-width="4" marker-end="url(#ar-{RED[1:]})"/>')
b.append(f'<text x="46" y="330" font-family="{FONT}" font-size="14" font-weight="bold" fill="{RED}" '
         f'text-anchor="middle" transform="rotate(-90 46 330)">increasing capability</text>')

STAGES = [("0", "Foundation and baselines", GREY_ := "#8894a8", "SETUP",
           ["Stand up the four guardrail layers (NeMo, DeBERTa, Llama Guard 3, Presidio),",
            "the self hosted model on Ollama and the evaluation harness."]),
          ("1", "Bayesian risk fusion engine", RED, "RQ",
           ["Calibrate each layer's score and fuse them into one risk value; compare the",
            "multi layer stack against each single layer, the fail closed union and the",
            "LlamaFirewall baseline. This is the evaluated research question."])]
y = 150
for num, title, col, tag, lines in STAGES:
    h = 108 if len(lines) == 2 else 130
    b.append(box(130, y, 74, h, col, col, 1, 10))
    b.append(text(167, y + h/2 + 12, num, 30, "bold", "#ffffff"))
    b.append(box(204, y, W-274, h, "#eef1f7", BOXEDGE, 1.4, 10))
    b.append(text(232, y + 36, title, 19, "bold", INK, "start"))
    for i, l in enumerate(lines):
        b.append(text(232, y + 62 + i*24, l, 13.5, "normal", MUTED, "start"))
    b.append(box(W-250, y + 14, 96, 30, col, col, 1, 8))
    b.append(text(W-202, y + 35, tag, 13, "bold", "#ffffff"))
    y += h + 26

b.append(box(130, y + 20, W-260, 118, "#f7f8fa", "#aab4c4", 1.6, 10, "8 5"))
b.append(text(W/2, y + 52, "Future work, not evaluated here", 17, "bold", MUTED))
b.append(text(W/2, y + 80, "Adaptation to threat drift: the threat mix present at deployment moves over time, and", 13.5, "normal", MUTED))
b.append(text(W/2, y + 102, "detecting that shift from the decision log and retuning on it is planned as future work.", 13.5, "normal", MUTED))

b.append(box(130, H-92, W-260, 54, "#16233c", "#16233c", 1, 10))
b.append(text(W/2, H-58, "Each stage is fully evaluated before the next begins; a negative result is reported and analysed, not discarded.",
              14, "bold", "#ffffff"))

out = pathlib.Path(__file__).parent / "fig_progression.svg"
out.write_text(svg(W, H, "".join(b), [LINE, RED, GREEN, BLUE, PURPLE, AMBER, "#8894a8"]))
print("wrote", out)

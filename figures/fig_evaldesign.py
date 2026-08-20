"""Evaluation design figure.

One prompt set, two systems, one scoring method. Drawn with banded panels and
numbered flow badges so the reading order is unambiguous. Only what was actually
measured sits inside the flow; planned work is held outside it.
Run:  python3 figures/fig_evaldesign.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import _style
from _style import *
_style.FS = 1.30

W, H = 1640, 1075
SLATE, WASH = "#33415c", "#f8fafc"
b = [f'<rect width="{W}" height="{H}" fill="{WASH}"/>']

# ---- title block ------------------------------------------------------------
b.append(text(W/2, 52, "DDELA Evaluation Design", 30, "bold", INK))
b.append(text(W/2, 84, "One prompt set  •  Two systems  •  One scoring method  •  Result reported openly",
              15.5, "bold", BLUE))

# ---- 1. the prompt set ------------------------------------------------------
b.append(panel(300, 112, 1040, 132, "THE LABELLED PROMPT SET", SLATE, "#ffffff"))
b.append(text(820, 176, "67 prompts written for this study, each labelled safe or unsafe", 14, "normal", INK))
STRATA = [("Benign", "15", GREEN), ("Dual use", "12", GREEN), ("Injection", "10", RED),
          ("Harmful", "10", RED), ("Personal data", "8", RED), ("Blended", "12", RED)]
cw, gap = 152, 12
x0 = 820 - (len(STRATA)*cw + (len(STRATA)-1)*gap)/2
for i, (nm, n, c) in enumerate(STRATA):
    x = x0 + i*(cw+gap)
    b.append(box(x, 196, cw, 34, "#ffffff", c, 1.4, 9))
    b.append(text(x+cw/2, 218, f"{nm}  {n}", 12.5, "bold", c))
b.append(chip(300, 112, 1, SLATE))

# ---- split ------------------------------------------------------------------
b.append(text(W/2 + 18, 272, "every prompt goes to both systems", 13.5, "bold", INK, anchor="start"))
# one trunk leaves the prompt set, then splits to the two systems
b.append(f'<path d="M{W/2},244 L{W/2},288" fill="none" stroke="{SLATE}" stroke-width="2.6"/>')
b.append(route([(W/2, 288), (450, 288), (450, 336)], BLUE, 2.6, standoff=8))
b.append(route([(W/2, 288), (1190, 288), (1190, 336)], RED, 2.6, standoff=8))

# ---- 2a. our system ---------------------------------------------------------
b.append(panel(150, 336, 600, 330, "OUR SYSTEM  ·  DDELA", BLUE, "#ffffff"))
b.append(chip(150, 336, "2a", BLUE))
b.append(text(450, 400, "four detectors read the prompt at the same time", 12.5, "normal", MUTED))
LAYERS = [("L1  Structural", "NeMo self check"), ("L2  Injection", "DeBERTa classifier"),
          ("L3  Harmful", "Llama Guard 3"), ("L4  Personal data", "Presidio")]
for i, (nm, sub) in enumerate(LAYERS):
    x = 176 + (i % 2)*288
    y = 416 + (i//2)*62
    b.append(box(x, y, 268, 54, "#eef4fd", "#c3d6f5", 1.4, 10))
    b.append(text(x+134, y+22, nm, 13, "bold", INK))
    b.append(text(x+134, y+40, sub, 11.5, "normal", MUTED))
b.append(route([(450, 538), (450, 572)], BLUE, 2.2, standoff=6))
b.append(text(450, 584, "their four scores are combined by one rule", 12.5, "normal", MUTED))
RULES = [("fail closed union", GREEN, PALE["green"]),
         ("noisy-OR  (deployed)", GREEN, "#dff3e6"),
         ("learned stacker", PURPLE, PALE["purple"])]
rw = 178
for i, (nm, c, f) in enumerate(RULES):
    x = 176 + i*192
    b.append(box(x, 596, rw, 44, f, c, 2.2 if i == 1 else 1.5, 10))
    b.append(text(x+rw/2, 623, nm, 12.5, "bold", c))

# ---- 2b. the comparison -----------------------------------------------------
b.append(panel(890, 336, 600, 330, "THE COMPARISON SYSTEM", RED, "#ffffff"))
b.append(chip(890, 336, "2b", RED))
b.append(box(918, 400, 544, 74, PALE["red"], RED, 1.8, 10))
b.append(text(1190, 428, "Meta LlamaFirewall", 16, "bold", RED))
b.append(text(1190, 452, "a real product, run on the same 67 prompts", 12.5, "normal", MUTED))
b.append(text(1190, 508, "In the on premise setup used here it has no", 13, "normal", INK))
b.append(text(1190, 530, "harmful content checker, so every harmful", 13, "normal", INK))
b.append(text(1190, 552, "prompt gets through.", 13, "normal", INK))
b.append(box(918, 578, 544, 62, "#fff5f5", RED, 1.5, 10))
b.append(text(1190, 602, "This is the gap the comparison reveals", 13.5, "bold", RED))
b.append(text(1190, 624, "and it is the reason the two scores differ", 12, "normal", MUTED))

# ---- converge ---------------------------------------------------------------
# two legs feed a single junction, then one arrow enters the scoring panel.
# Drawing a head on each leg stacked two heads on the same point.
b.append(route([(450, 666), (450, 700), (W/2, 700)], BLUE, 2.6, head=False))
b.append(route([(1190, 666), (1190, 700), (W/2, 700)], RED, 2.6, head=False))
b.append(route([(W/2, 700), (W/2, 740)], SLATE, 2.6, standoff=8))

# ---- 3. scoring -------------------------------------------------------------
b.append(panel(300, 740, 1040, 148, "BOTH ARE SCORED THE SAME WAY", SLATE, "#ffffff"))
b.append(chip(300, 740, 3, SLATE))
b.append(text(820, 804, "A block or a flag counts as caught.  An allow counts as let through.", 13.5, "normal", INK))
METRICS = [("F1", "overall accuracy"), ("Bypass rate", "unsafe let through"),
           ("Over refusal", "safe wrongly blocked"), ("Calibration", "is the risk honest")]
mw = 236
mx = 820 - (len(METRICS)*mw + (len(METRICS)-1)*12)/2
for i, (nm, sub) in enumerate(METRICS):
    x = mx + i*(mw+12)
    b.append(box(x, 824, mw, 48, "#eef1f7", "#c8d2e0", 1.3, 9))
    b.append(text(x+mw/2, 843, nm, 13, "bold", INK))
    b.append(text(x+mw/2, 862, sub, 11.5, "normal", MUTED))
b.append(route([(W/2, 888), (W/2, 916)], SLATE, 2.6, standoff=5))

# ---- result -----------------------------------------------------------------
b.append(box(300, 916, 1040, 42, "#16233c", "#16233c", 1, 10))
b.append(text(820, 943, "RESULT   one table and one chart comparing all eight configurations",
              14.5, "bold", "#ffffff"))

# ---- outside the flow -------------------------------------------------------
b.append(box(300, 976, 1040, 56, WASH, "#aab4c4", 1.6, 10, "8 5"))
b.append(text(820, 998, "Planned for later, not done in this study", 13.5, "bold", MUTED))
b.append(text(820, 1018, "repeat on larger public prompt sets, and retune as the mix of attacks changes",
              12, "normal", MUTED))

b.append(text(W/2, 1058, "67 prompts is a pilot, not a large sample. On a set this clean the union rule and the noisy-OR agree exactly, which is reported openly.",
              12.5, "normal", MUTED, style="i"))

out = pathlib.Path(__file__).parent / "fig_evaldesign.svg"
out.write_text(svg(W, H, "".join(b), [LINE, RED, GREEN, BLUE, PURPLE, SLATE, "#8894a8"]))
print("wrote", out)

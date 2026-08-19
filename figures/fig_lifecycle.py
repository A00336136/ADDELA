"""Figure 4, the request lifecycle, in the SAME eight steps as the Final
Results Report (Section 4.1) and the operator console's Architecture Flow tab.
The step numbering is a property of the system, so it must not differ between
documents.

Drawn as a timeline rather than a node graph on purpose: Figure 2 already shows
the system as a hub and Figure 3 shows where each part runs, so this figure
carries the sequence and nothing else.

Run:  python3 figures/fig_lifecycle.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import _style
from _style import *
_style.FS = 1.3

W = 1600
RAIL, X0, X1 = 112, 176, 1540
b = []

b.append(text(W/2, 50, "Request lifecycle, the eight steps one prompt takes", 24, "bold"))
b.append(text(W/2, 82, "the same eight steps as the Final Results Report (Section 4.1) and the operator console's Architecture Flow tab",
              14, "normal", MUTED, style="i"))

STEPS = [
 (BLUE, 104, "1 · Ingress, the caller reaches the gateway",
  ["The console at localhost:8080, or any application, sends one POST to the gateway on port 8000,",
   "the only port published to the host.  POST /api/analyze  { \"text\": … }"], []),

 (BLUE, 196, "2 · Parallel fan-out, every layer sees the same prompt",
  ["The gateway calls all four detection services at the same instant (POST /score) and waits for them together,",
   "so a decision costs about the time of the slowest layer rather than the sum of the four.  There is no router."],
  [("L1 · Structural", "NeMo self-check rail"), ("L2 · Injection", "DeBERTa (ProtectAI)"),
   ("L3 · Harmful", "Llama Guard 3"), ("L4 · Personal data", "Microsoft Presidio")]),

 (RED, 186, "3 · Model consultations, two layers have no classifier of their own",
  ["L1 and L3 each put their question to a model on the native Ollama runtime and read the reply back;",
   "L2 and L4 answer entirely inside their own containers and consult nothing. Both models below, and the",
   "protected gemma4:12b-mlx of step 6, are served by the one native Ollama runtime on :11434."],
  [("llama3.2:3b", "answers L1's yes / no  ·  2.0 GB", GREEN), ("llama-guard3:8b", "returns L3's safe / unsafe  ·  4.9 GB", GREEN)]),

 (BLUE, 104, "4 · Score collection, fail closed",
  ["Each layer returns one calibrated score in [0, 1]; the gateway collects the four into a single vector.",
   "A layer that cannot be reached is scored 1.0, so an unavailable detector can never silently weaken the guardrail."], []),

 (AMBER, 132, "5 · Fusion, the gateway forwards the four numbers, unchanged",
  ["POST /fuse { scores }.  The fusion service is handed the four numbers only, it never sees the prompt text,",
   "and returns one risk value with the verdict.      risk = 1 − (1 − λ) · Π (1 − sᵢ),   λ = 0.02",
   "ALLOW < 0.30      ·      FLAG < 0.60      ·      BLOCK ≥ 0.60"], []),

 (PURPLE, 168, "6 · Enforcement, the gateway acts on the verdict it was given",
  ["The gateway does not decide; it enforces. Only one of the two outcomes below can happen."],
  [("ALLOW  →  gemma4:12b-mlx is called", "the answer returns to the gateway, never straight to the caller", GREEN),
   ("BLOCK or FLAG  →  the request stops", "the protected model is never invoked at all", RED)]),

 (AMBER, 104, "7 · Audit, the decision is recorded before anything is returned",
  ["The gateway itself appends one JSON line to ./data/gateway/audit_log.jsonl, the prompt, the four scores,",
   "the fused risk and the verdict. There is no separate audit service and no database."], []),

 (GREEN, 104, "8 · Return, the caller receives the result",
  ["The gateway returns the four scores, the fused risk and the verdict, with the answer on ALLOW",
   "and answer = null on FLAG or BLOCK. Every outcome, allowed or refused, has already been logged."], []),
]

y = 118
rows = []
for colour, h, title, lines, subs in STEPS:
    rows.append((y, h, colour))
    b.append(box(X0, y, X1 - X0, h, "#fbfcfe", BOXEDGE, 1.5))
    b.append(f'<rect x="{X0}" y="{y}" width="6" height="{h}" rx="3" fill="{colour}"/>')
    b.append(text(X0 + 28, y + 34, title, 18, "bold", INK, "start"))
    for i, ln in enumerate(lines):
        b.append(text(X0 + 28, y + 60 + i * 23, ln, 13.5, "normal", MUTED, "start"))
    if subs:
        sy = y + h - 66
        sw = (X1 - X0 - 56 - (len(subs) - 1) * 16) / len(subs)
        for j, sub in enumerate(subs):
            t1, t2 = sub[0], sub[1]
            sc = sub[2] if len(sub) > 2 else None
            sx = X0 + 28 + j * (sw + 16)
            fill = {GREEN: PALE["green"], RED: PALE["red"]}.get(sc, "#eef1f7")
            b.append(box(sx, sy, sw, 52, fill, sc or BOXEDGE, 1.7 if sc else 1.4, 9))
            b.append(text(sx + sw / 2, sy + 22, t1, 14, "bold"))
            b.append(text(sx + sw / 2, sy + 41, t2, 11.5, "normal", MUTED))
    y += h + 20

# the rail: one continuous line with a numbered chip beside every step
b.insert(2, f'<path d="M{RAIL},{rows[0][0]+34} L{RAIL},{rows[-1][0]+34}" stroke="{BOXEDGE}" stroke-width="3"/>')
for n, (ry, rh, rc) in enumerate(rows, 1):
    b.append(f'<path d="M{RAIL+18},{ry+34} L{X0-4},{ry+34}" stroke="{rc}" stroke-width="2.2" '
             f'marker-end="url(#ar-{rc[1:]})"/>')
    b.append(chip(RAIL, ry + 34, n, rc))

H = y + 118
b.append(text(W/2, y + 34, "The audit log of step 7 is the on premise evidence trail for every decision the system makes.",
              13.5, "normal", MUTED, style="i"))
b.append(text(W/2, y + 58, "It is not a running service: nothing in the live path re-tunes itself, and threshold retuning is identified as future work.",
              13.5, "normal", MUTED, style="i"))

out = pathlib.Path(__file__).parent / "fig_lifecycle.svg"
out.write_text(svg(W, H, "".join(b), [LINE, RED, GREEN, BLUE, PURPLE, AMBER]))
print("wrote", out, f"({W}x{H})")

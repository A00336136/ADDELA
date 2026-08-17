"""Methodology Figure 5, evaluation design.

One evaluated research question. Adaptation to threat drift is future work and is
shown as such rather than as a second arm of the study.
Run:  python3 figures/fig_evaldesign.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import _style
from _style import *
_style.FS = 1.28

W, H = 1500, 1080
b = []
b.append(text(W/2, 46, "Evaluation design: multi layer detection and calibrated fusion", 21, "bold"))

b.append(box(120, 78, W-240, 132, "#eef1f7", INK, 2, 14))
b.append(text(W/2, 110, "LABELLED EVALUATION DATA", 15, "bold", INK))
b.append(titled(148, 126, 560, 68, [("Pilot set, N = 67, stratified", {"size": 15}),
   ("benign, injection, harmful, PII, dual use, blended evasive", {"size": 11.5})], "#ffffff", BOXEDGE, 1.5))
b.append(titled(748, 126, 604, 68, [("Powered scale up, planned", {"size": 15}),
   ("JailbreakBench, Mindgard obfuscation, XSTest", {"size": 11.5})], PALE["amber"], AMBER, 1.6))

b.append(box(120, 250, W-240, 640, "#f6f9fe", BLUE, 2, 16, "9 6"))
b.append(text(W/2, 286, "RQ: does calibrated fusion beat any single layer, the union rule and a production baseline?",
              15.5, "bold", BLUE))
b.append(route([(W/2, 210), (W/2, 250)], INK, 2.4))

b.append(box(160, 310, W-320, 118, "#ffffff", BOXEDGE, 1.5))
b.append(text(W/2, 338, "Systems under test, same prompts, same confusion matrix", 15, "bold", INK))
for i, nm in enumerate(["L1 Structural", "L2 Injection", "L3 Harmful", "L4 PII"]):
    b.append(titled(180 + i*292, 358, 268, 50, [(nm, {"size": 13.5})], "#eef1f7", BOXEDGE, 1.3))
b.append(titled(180, 452, 380, 52, [("fail closed union", {"size": 13.5})], PALE["green"], GREEN, 1.6))
b.append(titled(580, 452, 380, 52, [("leaky noisy-OR, deployed", {"size": 13.5})], PALE["green"], GREEN, 2))
b.append(titled(980, 452, 340, 52, [("learned stacker", {"size": 13.5})], "#f6f1fe", PURPLE, 1.6))

b.append(titled(160, 534, W-320, 74, [("External baseline: Meta LlamaFirewall, run live on the same set", {"size": 15}),
   ("head to head; no harmful content scanner, so it releases every harmful prompt", {"size": 12})], PALE["red"], RED, 2))

b.append(titled(160, 632, W-320, 100, [("Metrics, block and flag both count as contained", {"size": 15}),
   ("F1, bypass rate, over refusal rate, ECE of the fused risk", {"size": 12}),
   ("leakage safe five fold CV, thresholds fitted on the training fold only", {"size": 12, "style": "i"})],
   "#eef1f7", BOXEDGE, 1.5))

b.append(titled(160, 756, W-320, 76, [("Combiner ablation, the decisive test", {"size": 15}),
   ("union against noisy-OR against learned stacker on identical captured scores,", {"size": 12}),
   ("isolating whether the fusion arithmetic, not just coverage, adds value", {"size": 12})],
   "#f6f1fe", PURPLE, 1.6))

b.append(box(160, 848, W-320, 26, "#16233c", "#16233c", 1, 8))
b.append(text(W/2, 867, "Output: per configuration F1, bypass, over refusal and ECE, as a table and a bar chart",
              13, "bold", "#ffffff"))

b.append(box(120, 916, W-240, 92, "#f7f8fa", "#aab4c4", 1.8, 14, "8 5"))
b.append(text(W/2, 948, "Future work, not evaluated here", 15.5, "bold", MUTED))
b.append(text(W/2, 974, "Adaptation to threat drift: the threat mix present at deployment moves over time, and detecting", 12.5, "normal", MUTED))
b.append(text(W/2, 996, "that shift from the decision log and retuning on it is planned as future work.", 12.5, "normal", MUTED))

b.append(text(W/2, 1046, "N = 67 is a pilot rather than a statistically powered sample; the clean set is why the fusion coincides with the union, reported openly.",
              12.5, "normal", MUTED, style="i"))

out = pathlib.Path(__file__).parent / "fig_evaldesign.svg"
out.write_text(svg(W, H, "".join(b), [LINE, RED, GREEN, BLUE, PURPLE, AMBER, "#8894a8"]))
print("wrote", out)

"""Interim Figure 1: the four detection layers judged one at a time.

Evaluation 1 of the interim report is an ablation: each layer is read alone at
its native operating point, so the question "is any single detector sufficient?"
can be answered before composition is considered. Values recomputed from
eval/scores.json.  Run:  eval/.venv/bin/python figures/fig_singlelayer.py
"""
import json, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).parent.parent
rows = json.loads((ROOT / "eval/scores.json").read_text())
y = [r["label"] for r in rows]

def metrics(col):
    tp = sum(1 for r, l in zip(rows, y) if r[col] >= 0.5 and l == 1)
    fp = sum(1 for r, l in zip(rows, y) if r[col] >= 0.5 and l == 0)
    fn = sum(1 for r, l in zip(rows, y) if r[col] < 0.5 and l == 1)
    tn = sum(1 for r, l in zip(rows, y) if r[col] < 0.5 and l == 0)
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return (2 * pr * rc / (pr + rc) if pr + rc else 0.0), fn / (tp + fn), fp / (fp + tn)

LAYERS = [("L1\nStructural", "l1"), ("L2\nInjection", "l2"), ("L3\nHarmful", "l3"), ("L4\nPersonal data", "l4")]
f1  = [metrics(c)[0] for _, c in LAYERS]
byp = [metrics(c)[1] for _, c in LAYERS]
names = [n for n, _ in LAYERS]

INK, GREY, RED = "#16233c", "#9aa5b5", "#d81324"
plt.rcParams.update({"font.family": "Red Hat Text", "font.size": 11, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.edgecolor": "#c7cfdd", "axes.spines.top": False, "axes.spines.right": False})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.6))
fig.suptitle("Evaluation 1: each detection layer judged on its own (N = 67)",
             fontsize=14, fontweight="bold", family="Red Hat Display", y=1.02)

for ax, vals, title, better in ((a1, f1, "Detection F1 (higher is better)", "hi"),
                                (a2, byp, "Bypass rate, unsafe prompts released (lower is better)", "lo")):
    cols = [RED if ((v == max(vals)) if better == "hi" else (v == min(vals))) else GREY for v in vals]
    b = ax.bar(names, vals, color=cols, width=0.62)
    ax.bar_label(b, fmt="%.3f", padding=3, fontsize=10.5, color=INK)
    ax.set_ylim(0, 1.05); ax.set_title(title, fontsize=12, color=INK, pad=10)
    ax.grid(axis="y", color="#eef1f6", zorder=0); ax.set_axisbelow(True)
a1.set_ylabel("F1"); a2.set_ylabel("bypass rate")
fig.tight_layout()
out = ROOT / "figures/fig_singlelayer.png"
fig.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
print("wrote", out.name, "| F1", [round(v,3) for v in f1], "| bypass", [round(v,3) for v in byp])

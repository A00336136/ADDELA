"""RQ2 drift figure — the representative CUSUM run, rendered from eval/drift_result.json.

One generator, one image, used by BOTH the interim and the final report so the two
cannot drift apart. Everything drawn here comes from the JSON: the risk stream, the
attack markers, the CUSUM series, the calibrated threshold and the alarm index.

Run:  eval/.venv/bin/python figures/fig_drift.py
"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).parent.parent
D = json.loads((ROOT / "eval/drift_result.json").read_text())
R = D["representative"]
t, risk, cusum, atk = R["t"], R["risk"], R["cusum"], R["is_attack"]
CP, ALARM, H = D["changepoint"], R["alarm_request"], R["h"]

INK, GREEN, RED, PURPLE, GREY = "#16233c", "#0f7b3f", "#d81324", "#7c3aed", "#8894a8"
plt.rcParams.update({"font.family": "Red Hat Text", "font.size": 11,
                     "axes.edgecolor": "#c7cfdd", "axes.labelcolor": INK,
                     "text.color": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False})

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.0, 5.4), sharex=True,
                               gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.16})
fig.suptitle("Evaluation 2 — CUSUM drift detection on the fused-risk stream (representative of 500 runs)",
             fontsize=14, fontweight="bold", family="Red Hat Display", y=0.985)

# ── upper: the fused-risk stream, attacks marked ──
ax1.vlines(t, 0, risk, color="#c9d2e0", lw=1.0, zorder=1)
ax1.scatter([x for x, a in zip(t, atk) if a], [r for r, a in zip(risk, atk) if a],
            s=26, color=RED, zorder=3, label="attack request")
ax1.axhline(D["mean_risk_post"], ls="--", lw=1.4, color=RED, zorder=2)
ax1.axhline(D["mean_risk_pre"], ls="--", lw=1.4, color=GREEN, zorder=2)
ax1.text(4, D["mean_risk_post"] + 0.07, f"post-drift mean {D['mean_risk_post']:.2f}", color=RED, fontsize=10.5)
ax1.text(4, D["mean_risk_pre"] + 0.07, f"pre-drift mean {D['mean_risk_pre']:.2f}", color=GREEN, fontsize=10.5)
ax1.axvline(CP, ls="--", lw=1.6, color=INK, zorder=2)
ax1.text(CP - 3, 1.32, f"attacker adapts (req {CP})", ha="right", fontsize=10.5, color=INK)
ax1.set_ylabel("fused risk"); ax1.set_ylim(-0.05, 1.45)
ax1.set_yticks([0.0, 0.25, 0.50, 0.75, 1.00])
ax1.legend(loc="upper left", frameon=False, fontsize=10.5, handletextpad=0.4)

# ── lower: the CUSUM statistic against its calibrated threshold ──
ax2.plot(t, cusum, color=GREEN, lw=2.0, zorder=3)
ax2.axhline(H, ls="--", lw=1.4, color=RED, zorder=2)
ax2.text(4, H + max(cusum) * 0.055, f"calibrated threshold h = {H:.2f}", color=RED, fontsize=10.5)
ax2.axvline(CP, ls="--", lw=1.6, color=INK, zorder=2)
ax2.axvline(ALARM, lw=2.0, color=PURPLE, zorder=4)
ax2.annotate(f"alarm at req {ALARM}\ndelay = {R['delay']}", xy=(ALARM, max(cusum) * 0.62),
             xytext=(ALARM + 6, max(cusum) * 0.62), color=PURPLE, fontsize=10.5, va="center")
ax2.set_ylabel("CUSUM statistic"); ax2.set_xlabel("request index")
ax2.set_xlim(-4, len(t) + 4); ax2.set_ylim(-1, max(cusum) * 1.12)

out = ROOT / "figures/fig_drift.png"
fig.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
print(f"wrote {out.relative_to(ROOT)}  "
      f"(alarm {ALARM}, delay {R['delay']}, h {H}, pre {D['mean_risk_pre']}, post {D['mean_risk_post']})")

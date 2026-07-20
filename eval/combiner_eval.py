"""
Leakage-safe combiner ablation (addresses recommendations #5 and #1).

Compares three ways of combining the four detector scores into one decision:
  - hard_OR    : block if the strongest single detector clears a threshold (the "union" baseline)
  - noisy_OR   : ADDELA's leaky noisy-OR  risk = 1 - (1-LEAK)·Π(1-s_i)
  - learned_LR : a logistic-regression stacker over the 4 scores (dependency-aware combiner)

Methodology (no leakage):
  * stratified k-fold cross-validation
  * for EVERY combiner the decision threshold is chosen on the TRAIN fold only
    (max-F1), then applied unchanged to the held-out TEST fold
  * the learned stacker is fit on the TRAIN fold only
  * we report mean±std across folds, plus ECE (calibration) of each combiner's
    probability output on the test folds

Small-N caveat: with 67 prompts the folds are tiny; treat these as methodology-
correct estimates, and scale up with a public benchmark (JailbreakBench) for
statistical power.
"""
import json, pathlib
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

LEAK = 0.02
N_SPLITS = 5
SEED = 0

data = json.loads((pathlib.Path(__file__).parent / "scores.json").read_text())
X = np.array([[d["l1"], d["l2"], d["l3"], d["l4"]] for d in data], dtype=float)
y = np.array([d["label"] for d in data], dtype=int)


def noisy_or(x):
    return 1.0 - (1.0 - LEAK) * np.prod(1.0 - np.clip(x, 0, 1), axis=1)


def hard_or(x):
    return np.clip(x, 0, 1).max(axis=1)          # "any detector fires" as a risk


def best_threshold(risk, yy):                    # chosen on TRAIN only
    best_t, best_f = 0.5, -1.0
    for t in np.linspace(0.01, 0.99, 99):
        f = f1_score(yy, (risk >= t).astype(int), zero_division=0)
        if f > best_f:
            best_f, best_t = f, t
    return best_t


def metrics(yy, pred):
    tp = int(((pred == 1) & (yy == 1)).sum()); fp = int(((pred == 1) & (yy == 0)).sum())
    tn = int(((pred == 0) & (yy == 0)).sum()); fn = int(((pred == 0) & (yy == 1)).sum())
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    return dict(f1=f1, precision=pr, recall=rc,
                bypass=fn / (tp + fn) if tp + fn else 0.0,
                over_refusal=fp / (fp + tn) if fp + tn else 0.0)


def ece(probs, yy, bins=10):
    probs = np.clip(probs, 0, 1); edges = np.linspace(0, 1, bins + 1); e = 0.0
    for i in range(bins):
        hi = probs <= edges[i + 1] if i == bins - 1 else probs < edges[i + 1]
        m = (probs >= edges[i]) & hi
        if m.sum() == 0:
            continue
        e += abs(probs[m].mean() - yy[m].mean()) * m.sum() / len(yy)
    return e


skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
res = {k: [] for k in ("hard_OR", "noisy_OR", "learned_LR")}
ec = {k: [] for k in res}

for tr, te in skf.split(X, y):
    for name, fn in (("hard_OR", hard_or), ("noisy_OR", noisy_or)):
        t = best_threshold(fn(X[tr]), y[tr])
        rte = fn(X[te])
        res[name].append(metrics(y[te], (rte >= t).astype(int)))
        ec[name].append(ece(rte, y[te]))
    lr = LogisticRegression(max_iter=1000).fit(X[tr], y[tr])
    pt = lr.predict_proba(X[tr])[:, 1]; t = best_threshold(pt, y[tr])
    pte = lr.predict_proba(X[te])[:, 1]
    res["learned_LR"].append(metrics(y[te], (pte >= t).astype(int)))
    ec["learned_LR"].append(ece(pte, y[te]))


def cell(rows, key):
    v = np.array([r[key] for r in rows]); return f"{v.mean():.3f}±{v.std():.3f}"


print(f"Leakage-safe {N_SPLITS}-fold CV — threshold selected on TRAIN fold only, evaluated on held-out TEST fold\n")
hdr = f"{'combiner':11s} {'F1':>12s} {'recall':>12s} {'precision':>12s} {'bypass':>12s} {'over-refusal':>13s} {'ECE':>7s}"
print(hdr); print("-" * len(hdr))
for name in res:
    print(f"{name:11s} {cell(res[name],'f1'):>12s} {cell(res[name],'recall'):>12s} "
          f"{cell(res[name],'precision'):>12s} {cell(res[name],'bypass'):>12s} "
          f"{cell(res[name],'over_refusal'):>13s} {np.mean(ec[name]):>7.3f}")
print("\nHigher F1/recall/precision = better; lower bypass/over-refusal/ECE = better.")
print("If noisy_OR ≈ hard_OR and learned_LR does not clearly exceed both, that is the")
print("honest, literature-consistent finding (near-orthogonal detectors → nothing to fuse).")

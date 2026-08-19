"""Interim Figure 2: all eight configurations on the 67 prompt pilot.

The four individual layers of Evaluation 1 set beside the three composition rules
and the external baseline of Evaluation 2. Values recomputed from eval/scores.json
and data/dashboard/compare.json.
Run:  eval/.venv/bin/python figures/fig_allconfigs.py
"""
import json, pathlib
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

ROOT = pathlib.Path(__file__).parent.parent
rows = json.loads((ROOT / "eval/scores.json").read_text())
X = np.array([[r["l1"], r["l2"], r["l3"], r["l4"]] for r in rows], float)
y = np.array([r["label"] for r in rows], int)
LEAK = 0.02

def m(yy, pred):
    tp=int(((pred==1)&(yy==1)).sum()); fp=int(((pred==1)&(yy==0)).sum())
    fn=int(((pred==0)&(yy==1)).sum())
    pr=tp/(tp+fp) if tp+fp else 0.0; rc=tp/(tp+fn) if tp+fn else 0.0
    return (2*pr*rc/(pr+rc) if pr+rc else 0.0), (fn/(tp+fn) if tp+fn else 0.0)
def best_t(risk, yy):
    return max(np.linspace(0.01,0.99,99), key=lambda t: f1_score(yy,(risk>=t).astype(int),zero_division=0))
noisy = lambda a: 1.0-(1.0-LEAK)*np.prod(1.0-np.clip(a,0,1),axis=1)
hard  = lambda a: np.clip(a,0,1).max(axis=1)

f1s, byps = [], []
for i in range(4):
    a,b = m(y,(X[:,i]>=0.5).astype(int)); f1s.append(a); byps.append(b)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
acc = {k: [] for k in ("U","F","S")}
for tr,te in skf.split(X,y):
    for k,fn in (("U",hard),("F",noisy)):
        t=best_t(fn(X[tr]),y[tr]); acc[k].append(m(y[te],(fn(X[te])>=t).astype(int)))
    lr=LogisticRegression(max_iter=1000).fit(X[tr],y[tr])
    t=best_t(lr.predict_proba(X[tr])[:,1],y[tr])
    acc["S"].append(m(y[te],(lr.predict_proba(X[te])[:,1]>=t).astype(int)))
for k in ("U","F","S"):
    f1s.append(float(np.mean([v[0] for v in acc[k]]))); byps.append(float(np.mean([v[1] for v in acc[k]])))
cmp = json.loads((ROOT/"data/dashboard/compare.json").read_text())
lab = {str(p["i"]): p["label"] for p in json.loads((ROOT/"services/dashboard/data/prompts.json").read_text())}
pred=np.array([1 if cmp[k]["lfw"]!="ALLOW" else 0 for k in cmp if k in lab])
truth=np.array([lab[k] for k in cmp if k in lab])
a,b = m(truth,pred); f1s.append(a); byps.append(b)

NAMES = ["L1\nStructural","L2\nInjection","L3\nHarmful","L4\nPersonal\ndata",
         "Union\n(U)","Noisy-OR\nfusion (F)","Learned\nstacker","Llama-\nFirewall"]
GREY,GREEN,RED,PURPLE,BLUE = "#9aa5b5","#1e874b","#d81324","#7a3fb0","#2f6fed"
COLS = [GREY]*4 + [GREEN, RED, PURPLE, BLUE]
INK="#16233c"
plt.rcParams.update({"font.family":"Red Hat Text","font.size":10.5,"text.color":INK,
                     "axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
                     "axes.edgecolor":"#c7cfdd","axes.spines.top":False,"axes.spines.right":False})
fig,(a1,a2)=plt.subplots(1,2,figsize=(12.4,4.0))
fig.suptitle("Evaluation 2: the four layers alone, the three composition rules and the baseline (N = 67)",
             fontsize=14, fontweight="bold", family="Red Hat Display", y=1.03)
for ax,vals,title,lab_ in ((a1,f1s,"Detection F1 (higher is better)","F1"),
                           (a2,byps,"Bypass rate, unsafe prompts released (lower is better)","bypass rate")):
    bars=ax.bar(NAMES,vals,color=COLS,width=0.66)
    ax.bar_label(bars,fmt="%.3f",padding=3,fontsize=9.5,color=INK)
    ax.set_ylim(0,1.08); ax.set_title(title,fontsize=12,pad=10); ax.set_ylabel(lab_)
    ax.grid(axis="y",color="#eef1f6"); ax.set_axisbelow(True)
    ax.tick_params(axis="x",labelsize=9)
fig.tight_layout()
out=ROOT/"figures/fig_allconfigs.png"
fig.savefig(out,dpi=180,bbox_inches="tight",facecolor="white")
print("wrote",out.name,"| F1",[round(v,3) for v in f1s])

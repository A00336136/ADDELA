"""Column width results figure for the conference article.

Same numbers as the thesis, redrawn tall and narrow with larger type so it
stays legible inside a two column IEEE layout.
Run:  eval/.venv/bin/python figures/fig_paper_results.py
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
noisy = lambda a: 1.0 - (1.0 - LEAK) * np.prod(1.0 - np.clip(a, 0, 1), axis=1)
hard = lambda a: np.clip(a, 0, 1).max(axis=1)
def m(yy, p):
    tp=int(((p==1)&(yy==1)).sum()); fp=int(((p==1)&(yy==0)).sum()); fn=int(((p==0)&(yy==1)).sum())
    pr=tp/(tp+fp) if tp+fp else 0.0; rc=tp/(tp+fn) if tp+fn else 0.0
    return (2*pr*rc/(pr+rc) if pr+rc else 0.0), (fn/(tp+fn) if tp+fn else 0.0)
def best_t(r, yy):
    return max(np.linspace(.01,.99,99), key=lambda t: f1_score(yy,(r>=t).astype(int),zero_division=0))

f1s, byp = [], []
for i in range(4):
    a,b = m(y,(X[:,i]>=0.5).astype(int)); f1s.append(a); byp.append(b)
skf = StratifiedKFold(5, shuffle=True, random_state=0); acc={k:[] for k in "UFS"}
for tr,te in skf.split(X,y):
    for k,fn_ in (("U",hard),("F",noisy)):
        t=best_t(fn_(X[tr]),y[tr]); acc[k].append(m(y[te],(fn_(X[te])>=t).astype(int)))
    lr=LogisticRegression(max_iter=1000).fit(X[tr],y[tr]); t=best_t(lr.predict_proba(X[tr])[:,1],y[tr])
    acc["S"].append(m(y[te],(lr.predict_proba(X[te])[:,1]>=t).astype(int)))
for k in "UFS":
    f1s.append(float(np.mean([v[0] for v in acc[k]]))); byp.append(float(np.mean([v[1] for v in acc[k]])))
cmp = json.loads((ROOT/"data/dashboard/compare.json").read_text())
lab = {str(p["i"]): p["label"] for p in json.loads((ROOT/"services/dashboard/data/prompts.json").read_text())}
ks=[k for k in cmp if k in lab]
a,b = m(np.array([lab[k] for k in ks]), np.array([1 if cmp[k]["ddela" if "ddela" in cmp[ks[0]] else "lfw"] and cmp[k]["lfw"]!="ALLOW" else 0 for k in ks]))
f1s.append(a); byp.append(b)

NAMES=["L1","L2","L3","L4","U","F","LR","LFW"]
GREY,GREEN,RED,PURPLE,BLUE="#9aa5b5","#1e874b","#d81324","#7a3fb0","#2f6fed"
COLS=[GREY]*4+[GREEN,RED,PURPLE,BLUE]
plt.rcParams.update({"font.family":"Times New Roman","font.size":8,"axes.edgecolor":"#444",
                     "axes.spines.top":False,"axes.spines.right":False})
fig,(a1,a2)=plt.subplots(2,1,figsize=(3.4,3.5),sharex=True)
for ax,v,t in ((a1,f1s,"Detection F1 (higher is better)"),(a2,byp,"Bypass rate (lower is better)")):
    bars=ax.bar(NAMES,v,color=COLS,width=0.68)
    ax.bar_label(bars,fmt="%.2f",padding=2,fontsize=6.5)
    ax.set_ylim(0,1.12); ax.set_title(t,fontsize=8.5,pad=4)
    ax.grid(axis="y",color="#e8ebf0"); ax.set_axisbelow(True); ax.tick_params(labelsize=7.5)
a2.set_xlabel("L1-L4 single layers · U union · F noisy-OR · LR stacker · LFW LlamaFirewall",fontsize=6.5)
fig.tight_layout(pad=0.4)
out=ROOT/"figures/fig_paper_results.png"
fig.savefig(out,dpi=400,bbox_inches="tight",facecolor="white")
print("wrote",out.name,"| F1",[round(v,3) for v in f1s],"| bypass",[round(v,3) for v in byp])

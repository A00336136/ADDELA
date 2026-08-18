"""Final Results Report, Figures 2, 3 and 4.

Regenerated so the labels carry no em dashes and no stale layer names. Every
number is recomputed from eval/scores.json with the same leakage safe five fold
protocol and the same ECE estimator the results tables use.
Run:  eval/.venv/bin/python figures/fig_final_charts.py
"""
import json, pathlib
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

ROOT = pathlib.Path(__file__).parent.parent
rows = json.loads((ROOT / "eval/scores.json").read_text())
X = np.array([[r["l1"], r["l2"], r["l3"], r["l4"]] for r in rows], float)
y = np.array([r["label"] for r in rows], int)
LEAK, SEED, NSPLIT = 0.02, 0, 5
noisy = lambda a: 1.0 - (1.0 - LEAK) * np.prod(1.0 - np.clip(a, 0, 1), axis=1)
hard  = lambda a: np.clip(a, 0, 1).max(axis=1)

def counts(yy, pred):
    return (int(((pred==1)&(yy==1)).sum()), int(((pred==0)&(yy==1)).sum()),
            int(((pred==1)&(yy==0)).sum()), int(((pred==0)&(yy==0)).sum()))  # TP FN FP TN
def m(yy, pred):
    tp,fn,fp,tn = counts(yy,pred)
    pr = tp/(tp+fp) if tp+fp else 0.0; rc = tp/(tp+fn) if tp+fn else 0.0
    return (2*pr*rc/(pr+rc) if pr+rc else 0.0), (fn/(tp+fn) if tp+fn else 0.0)
def best_t(risk, yy):
    return max(np.linspace(0.01,0.99,99), key=lambda t: f1_score(yy,(risk>=t).astype(int),zero_division=0))
def ece(probs, yy, bins=10):                       # identical to eval/combiner_eval.py
    probs=np.clip(probs,0,1); edges=np.linspace(0,1,bins+1); e=0.0
    for i in range(bins):
        hi = probs<=edges[i+1] if i==bins-1 else probs<edges[i+1]
        msk=(probs>=edges[i])&hi
        if msk.sum()==0: continue
        e += abs(probs[msk].mean()-yy[msk].mean())*msk.sum()/len(yy)
    return e

f1s, byps = [], []
for i in range(4):
    a,b = m(y,(X[:,i]>=0.5).astype(int)); f1s.append(a); byps.append(b)
skf = StratifiedKFold(n_splits=NSPLIT, shuffle=True, random_state=SEED)
acc = {k: {"m": [], "e": []} for k in ("U","F","S")}
for tr,te in skf.split(X,y):
    for k,fn in (("U",hard),("F",noisy)):
        rte=fn(X[te]); t=best_t(fn(X[tr]),y[tr])
        acc[k]["m"].append(m(y[te],(rte>=t).astype(int))); acc[k]["e"].append(ece(rte,y[te]))
    lr=LogisticRegression(max_iter=1000).fit(X[tr],y[tr])
    pte=lr.predict_proba(X[te])[:,1]; t=best_t(lr.predict_proba(X[tr])[:,1],y[tr])
    acc["S"]["m"].append(m(y[te],(pte>=t).astype(int))); acc["S"]["e"].append(ece(pte,y[te]))
for k in ("U","F","S"):
    f1s.append(float(np.mean([v[0] for v in acc[k]["m"]])))
    byps.append(float(np.mean([v[1] for v in acc[k]["m"]])))
eces = [float(np.mean(acc[k]["e"])) for k in ("U","F","S")]

cmp = json.loads((ROOT/"data/dashboard/compare.json").read_text())
lab = {str(p["i"]): p["label"] for p in json.loads((ROOT/"services/dashboard/data/prompts.json").read_text())}
keys=[k for k in cmp if k in lab]
a,b = m(np.array([lab[k] for k in keys]), np.array([1 if cmp[k]["lfw"]!="ALLOW" else 0 for k in keys]))
f1s.append(a); byps.append(b)

GREY,GREEN,RED,PURPLE,BLUE,INK = "#9aa5b5","#1e874b","#d81324","#7a3fb0","#2f6fed","#16233c"
plt.rcParams.update({"font.family":"Red Hat Text","font.size":11,"text.color":INK,
                     "axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
                     "axes.edgecolor":"#c7cfdd","axes.spines.top":False,"axes.spines.right":False})
def save(fig,name):
    p=ROOT/f"figures/{name}.png"; fig.savefig(p,dpi=180,bbox_inches="tight",facecolor="white"); print("wrote",p.name)

# ---- Figure 2 -------------------------------------------------------------
NAMES=["L1\nStructural","L2\nInjection","L3\nHarmful","L4\nPersonal\ndata",
       "Union\n(U)","Noisy-OR\nfusion (F)","Learned\nstacker","Llama-\nFirewall"]
COLS=[GREY]*4+[GREEN,RED,PURPLE,BLUE]
fig,(a1,a2)=plt.subplots(1,2,figsize=(12.6,4.1))
fig.suptitle("Detection F1 and bypass rate by configuration (N = 67)",fontsize=14.5,
             fontweight="bold",family="Red Hat Display",y=1.04)
for ax,vals,t,yl in ((a1,f1s,"Detection F1 (higher is better)","F1"),
                     (a2,byps,"Bypass rate, unsafe prompts released (lower is better)","bypass rate")):
    bars=ax.bar(NAMES,vals,color=COLS,width=0.66)
    ax.bar_label(bars,fmt="%.3f",padding=3,fontsize=9.5,color=INK)
    ax.set_ylim(0,1.08); ax.set_title(t,fontsize=12,pad=10); ax.set_ylabel(yl)
    ax.grid(axis="y",color="#eef1f6"); ax.set_axisbelow(True); ax.tick_params(axis="x",labelsize=9)
fig.tight_layout(); save(fig,"fig_final_f2")

# ---- Figure 3, confusion matrices ----------------------------------------
tU=best_t(hard(X),y); tF=best_t(noisy(X),y)
PANELS=[("Best single layer (L1)",counts(y,(X[:,0]>=0.5).astype(int))),
        ("Fail closed union (U)", counts(y,(hard(X)>=tU).astype(int))),
        ("Leaky noisy-OR fusion (F)",counts(y,(noisy(X)>=tF).astype(int)))]
print("confusion (TP,FN,FP,TN):",[(n,c) for n,c in PANELS])
cmap=LinearSegmentedColormap.from_list("dd",["#fdeeee","#8f1d1d"])
fig,axes=plt.subplots(1,3,figsize=(12.6,4.0))
fig.suptitle("Confusion matrices on the 67 prompt pilot",fontsize=14.5,
             fontweight="bold",family="Red Hat Display",y=1.04)
for ax,(title,(tp,fn,fp,tn)) in zip(axes,PANELS):
    Mx=np.array([[tp,fn],[fp,tn]]); ax.imshow(Mx,cmap=cmap,vmin=0,vmax=40)
    for (i,j),v in np.ndenumerate(Mx):
        ax.text(j,i,str(v),ha="center",va="center",fontsize=23,
                color="white" if Mx[i,j]>20 else INK)
    ax.set_xticks([0,1],["contained","released"]); ax.set_yticks([0,1],["unsafe","safe"])
    ax.set_title(title,fontsize=12,pad=10); ax.set_xlabel("guardrail decision")
    if ax is axes[0]: ax.set_ylabel("ground truth")
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
fig.tight_layout(); save(fig,"fig_final_f3")

# ---- Figure 4, calibration ------------------------------------------------
fig,ax=plt.subplots(figsize=(7.6,3.9))
bars=ax.bar(["Fail closed\nunion (U)","Leaky noisy-OR\nfusion (F)","Learned\nstacker"],
            eces,color=[GREEN,RED,PURPLE],width=0.52)
ax.bar_label(bars,fmt="%.3f",padding=3,fontsize=11,color=INK)
ax.set_title("Expected calibration error by combiner (lower is better)",fontsize=13.5,
             fontweight="bold",family="Red Hat Display",pad=12)
ax.set_ylabel("Expected Calibration Error (ECE)"); ax.set_ylim(0,max(eces)*1.25)
ax.grid(axis="y",color="#eef1f6"); ax.set_axisbelow(True)
fig.tight_layout(); save(fig,"fig_final_f4")
print("F1  ",[round(v,3) for v in f1s]); print("byp ",[round(v,3) for v in byps]); print("ECE ",[round(v,3) for v in eces])

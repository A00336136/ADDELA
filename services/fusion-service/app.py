import os
from fastapi import FastAPI
from pydantic import BaseModel

LEAK = float(os.environ.get("FUSION_LEAK", "0.02"))
TAU_FLAG = float(os.environ.get("FUSION_TAU_FLAG", "0.30"))
TAU_BLOCK = float(os.environ.get("FUSION_TAU_BLOCK", "0.60"))

app = FastAPI()

class Req(BaseModel):
    scores: dict[str, float]        # {"l1": 0.0, "l2": 0.97, "l3": 0.0, "l4": 0.0}

@app.get("/health")
def health():
    return {"status": "ok", "leak": LEAK, "tau_flag": TAU_FLAG, "tau_block": TAU_BLOCK}

@app.post("/fuse")
def fuse(req: Req):
    survive = 1.0 - LEAK
    for s in req.scores.values():
        survive *= (1.0 - max(0.0, min(1.0, s)))
    risk = 1.0 - survive                                   # risk = 1 − (1−λ)·Π(1−sᵢ)
    decision = "BLOCK" if risk >= TAU_BLOCK else "FLAG" if risk >= TAU_FLAG else "ALLOW"
    return {"risk": risk, "decision": decision, "scores": req.scores}

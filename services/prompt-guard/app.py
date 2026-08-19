from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

clf = pipeline("text-classification", model="protectai/deberta-v3-base-prompt-injection-v2")
app = FastAPI()

class Req(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(req: Req):
    r = clf(req.text[:2000])[0]
    return {"score": r["score"] if r["label"] == "INJECTION" else 1 - r["score"]}

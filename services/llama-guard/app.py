import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

OLLAMA = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
MODEL = os.environ.get("DDELA_GUARD", "llama-guard3:8b")

app = FastAPI()

class Req(BaseModel):
    text: str

@app.get("/health")
def health():
    r = requests.get(f"{OLLAMA}/api/tags", timeout=5)
    return {"status": "ok" if r.ok else "ollama unreachable"}

@app.post("/score")
def score(req: Req):
    r = requests.post(f"{OLLAMA}/api/chat", json={
        "model": MODEL,
        "messages": [{"role": "user", "content": req.text}],
        "stream": False,
    }, timeout=120)
    verdict = r.json()["message"]["content"].strip()
    unsafe = verdict.lower().startswith("unsafe")
    return {"score": 1.0 if unsafe else 0.0, "verdict": verdict}

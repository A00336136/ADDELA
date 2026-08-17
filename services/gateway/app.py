import asyncio, json, os, time
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

LAYERS = {
    "l1": "http://nemo-guardrails:8000/score",
    "l2": "http://prompt-guard:8000/score",
    "l3": "http://llama-guard:8000/score",
    "l4": "http://pii-service:8000/score",
}
FUSION = "http://fusion-service:8000/fuse"
OLLAMA = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
LLM = os.environ.get("DDELA_LLM", "gemma4:12b-mlx")
AUDIT = "/data/audit_log.jsonl"

app = FastAPI()

class Req(BaseModel):
    text: str
    decide_only: bool = False        # eval mode: return the decision but skip the answer generation

async def call_layer(client, name, url, text):
    try:
        r = await client.post(url, json={"text": text})
        return name, float(r.json()["score"])
    except Exception:
        return name, 1.0                       # fail-closed: unreachable detector = max risk

@app.get("/api/health")
async def health():
    async with httpx.AsyncClient(timeout=5) as c:
        checks = await asyncio.gather(
            *[c.get(u.rsplit("/", 1)[0] + "/health") for u in LAYERS.values()],
            return_exceptions=True)
    return {n: (not isinstance(r, Exception) and r.status_code == 200)
            for n, r in zip(LAYERS, checks)}

@app.post("/api/analyze")
async def analyze(req: Req):
    async with httpx.AsyncClient(timeout=180) as c:
        results = await asyncio.gather(
            *[call_layer(c, n, u, req.text) for n, u in LAYERS.items()])
        scores = dict(results)
        fused = (await c.post(FUSION, json={"scores": scores})).json()
        answer = None
        if fused["decision"] == "ALLOW" and not req.decide_only:
            r = await c.post(f"{OLLAMA}/api/chat", json={
                "model": LLM, "stream": False,
                "messages": [{"role": "user", "content": req.text}]})
            answer = r.json()["message"]["content"]
    record = {"ts": time.time(), "prompt": req.text, "scores": scores,
              "risk": fused["risk"], "decision": fused["decision"]}
    with open(AUDIT, "a") as f:
        f.write(json.dumps(record) + "\n")
    # human-readable decision line to stdout, captured by `docker compose logs gateway`
    if fused["decision"] != "ALLOW":
        tail = f"protected LLM {LLM} NOT called (blocked before the model)"
    elif req.decide_only:
        tail = f"protected LLM {LLM} NOT called (decision-only eval)"
    else:
        tail = f"invoking protected LLM {LLM}"
    print(f"decision={fused['decision']} risk={fused['risk']:.3f} -> {tail}", flush=True)
    return {**record, "answer": answer}

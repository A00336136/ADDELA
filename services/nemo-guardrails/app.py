from fastapi import FastAPI
from pydantic import BaseModel
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./nemo_config")
rails = LLMRails(config)
app = FastAPI()

class Req(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
async def score(req: Req):
    resp = await rails.generate_async(
        messages=[{"role": "user", "content": req.text}])
    blocked = resp["content"].strip() == "ADDELA_BLOCKED"     # input rail fired
    return {"score": 1.0 if blocked else 0.0}

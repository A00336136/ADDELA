"""
LlamaFirewall external baseline — Meta's real package (github.com/meta-llama/PurpleLlama)
exposed behind the same POST /score contract as ADDELA's own detectors, so it can be
scored over the identical 67-prompt corpus for a fair head-to-head.

On-premise config (no external API keys, by design):
  CODE_SHIELD · HIDDEN_ASCII · REGEX          (Meta's local scanners, as shipped)
  + PROMPT_GUARD                              (genuine Llama-Prompt-Guard-2, if USE_REAL_PROMPTGUARD=1)

Excluded on purpose — both call Together AI and would break the on-premise thesis:
  AGENT_ALIGNMENT · PII_DETECTION
Decision rule is LlamaFirewall's own fail-closed policy: contained if the scan does not ALLOW.
"""
import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")          # use cached weights, never phone home
os.environ.setdefault("TOKENIZERS_PARALLELISM", "true")

# huggingface_hub >= 1.0 removed HfFolder, which llamafirewall's promptguard_utils still imports.
# Shim it against the standard token store so the PromptGuard scanner loads offline.
import huggingface_hub as _hf
if not hasattr(_hf, "HfFolder"):
    class _HfFolder:
        @staticmethod
        def get_token():
            try:
                return _hf.get_token()
            except Exception:
                return None
    _hf.HfFolder = _HfFolder
if not hasattr(_hf, "login"):
    _hf.login = lambda *a, **k: None

from fastapi import FastAPI
from pydantic import BaseModel
from llamafirewall import LlamaFirewall, Role, ScannerType, ScanDecision, UserMessage

SCANNERS = [ScannerType.CODE_SHIELD, ScannerType.HIDDEN_ASCII, ScannerType.REGEX]
if os.environ.get("USE_REAL_PROMPTGUARD") == "1":
    SCANNERS.append(ScannerType.PROMPT_GUARD)         # Scope B — genuine Meta injection detector

lf = LlamaFirewall(scanners={Role.USER: SCANNERS})
app = FastAPI()


class Req(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok", "scanners": [s.name for s in SCANNERS]}


@app.post("/score")
def score(req: Req):
    r = lf.scan(UserMessage(content=req.text))
    contained = r.decision != ScanDecision.ALLOW               # fail-closed: anything not ALLOW blocks
    return {
        "score": 1.0 if contained else 0.0,
        "decision": str(r.decision),
        "reason": getattr(r, "reason", None),
        "raw_score": getattr(r, "score", None),
    }

"""
Collect per-detector scores for the labelled prompt corpus by running each prompt
through the live gateway. Writes eval/scores.json, the raw material for the
offline, leakage-safe combiner analysis (combiner_eval.py). Run with the stack up.
"""
import json, pathlib, time, urllib.request

ROOT = pathlib.Path(__file__).parent.parent
GATEWAY = "http://localhost:8000/api/analyze"
prompts = json.loads((ROOT / "services/dashboard/data/prompts.json").read_text())

out = []
for p in prompts:
    body = json.dumps({"text": p["text"], "decide_only": True}).encode()   # eval: skip answer generation
    req = urllib.request.Request(GATEWAY, data=body, headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=300))
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(5)
    s = r.get("scores", {})
    out.append({"i": p["i"], "stratum": p["stratum"], "label": p["label"],
                "l1": s.get("l1"), "l2": s.get("l2"), "l3": s.get("l3"), "l4": s.get("l4"),
                "risk": r.get("risk"), "decision": r.get("decision")})
    print(f"{p['i']:2d}/67  {p['stratum']:12s} risk={r.get('risk')}  {r.get('decision')}", flush=True)

dest = pathlib.Path(__file__).parent / "scores.json"
dest.write_text(json.dumps(out, indent=2))
print("wrote", len(out), "->", dest)

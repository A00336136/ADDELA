import json, os, pathlib
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://gateway:8000")
DETECTORS = {                                   # internal-only services, reachable on the Compose net
    "structural": "http://nemo-guardrails:8000/score",
    "injection":  "http://prompt-guard:8000/score",
    "harmful":    "http://llama-guard:8000/score",
    "pii":        "http://pii-service:8000/score",
}
LFW_URL = os.environ.get("LFW_URL", "http://llamafirewall:8000/score")   # external baseline (baseline profile)
AUDIT_LOG = os.environ.get("AUDIT_LOG", "/gateway-data/audit_log.jsonl")
RESULTS_FILE = pathlib.Path(os.environ.get("RESULTS_FILE", "/dashboard-data/results.json"))
COMPARE_FILE = pathlib.Path(os.environ.get("COMPARE_FILE", "/dashboard-data/compare.json"))
PROMPTS = json.loads(pathlib.Path("data/prompts.json").read_text())


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/prompts")
def api_prompts():
    return jsonify(PROMPTS)


@app.get("/api/health")
def api_health():
    try:
        r = requests.get(f"{GATEWAY_URL}/api/health", timeout=8)
        return jsonify({"ok": True, "layers": r.json()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.post("/api/analyze")
def api_analyze():
    body = request.get_json(force=True)
    text = body.get("text", "")
    decide_only = bool(body.get("decide_only", False))   # forwarded so the comparison can skip answer generation
    try:
        r = requests.post(f"{GATEWAY_URL}/api/analyze",
                          json={"text": text, "decide_only": decide_only}, timeout=200)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.post("/api/component")
def api_component():
    body = request.get_json(force=True)
    layer, text = body.get("layer"), body.get("text", "")
    url = DETECTORS.get(layer)
    if not url:
        return jsonify({"error": f"unknown layer {layer}"}), 400
    try:
        r = requests.post(url, json={"text": text}, timeout=200)
        return jsonify({"layer": layer, "response": r.json()})
    except Exception as e:
        return jsonify({"layer": layer, "error": str(e)}), 502


@app.post("/api/llamafirewall")
def api_llamafirewall():
    """External baseline arm — proxy the LlamaFirewall container (needs the 'baseline' profile up)."""
    text = request.get_json(force=True).get("text", "")
    try:
        r = requests.post(LFW_URL, json={"text": text}, timeout=200)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e), "hint": "start it: docker compose --profile baseline up -d llamafirewall"}), 502


@app.get("/api/compare-results")
def get_compare():
    return jsonify(json.loads(COMPARE_FILE.read_text()) if COMPARE_FILE.exists() else {})


@app.post("/api/compare-results")
def save_compare():
    COMPARE_FILE.parent.mkdir(parents=True, exist_ok=True)
    COMPARE_FILE.write_text(json.dumps(request.get_json(force=True)))
    return jsonify({"saved": True})


COMBINERS_FILE = pathlib.Path(os.environ.get("COMBINERS_FILE", "/dashboard-data/combiners.json"))


@app.get("/api/combiners")
def api_combiners():
    """RQ1 combiner comparison, published by eval/prove_figure2.py."""
    if not COMBINERS_FILE.exists():
        return jsonify({"ready": False,
                        "hint": "run:  cd eval && ./.venv/bin/python prove_figure2.py"})
    d = json.loads(COMBINERS_FILE.read_text()); d["ready"] = True
    return jsonify(d)

@app.get("/api/audit")
def api_audit():
    n = int(request.args.get("n", 100))
    p = pathlib.Path(AUDIT_LOG)
    if not p.exists():
        return jsonify({"lines": [], "total": 0, "note": "no audit log yet — run a prompt first"})
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return jsonify({"lines": rows[-n:], "total": len(rows)})


@app.get("/api/results")
def get_results():
    return jsonify(json.loads(RESULTS_FILE.read_text()) if RESULTS_FILE.exists() else {})


@app.post("/api/results")
def save_results():
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(json.dumps(request.get_json(force=True)))
    return jsonify({"saved": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

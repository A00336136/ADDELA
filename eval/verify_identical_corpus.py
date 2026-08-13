"""
Proof that ADDELA and the LlamaFirewall baseline were driven over the IDENTICAL corpus.

Run:  ./.venv/bin/python verify_identical_corpus.py

The two systems keep independent, append-only audit trails written by different
services in different containers:

    data/gateway/audit_log.jsonl     written by the ADDELA gateway
    data/baseline/baseline_audit.jsonl   written by the LlamaFirewall container

This script re-reads both, extracts the prompt text each system actually received,
and checks them against the labelled corpus. It does not trust compare.json: it
verifies the two systems' own records agree on what they were shown.
"""
import json, pathlib, hashlib

ROOT = pathlib.Path(__file__).parent.parent
CORPUS   = ROOT / "services/dashboard/data/prompts.json"
GATEWAY  = ROOT / "data/gateway/audit_log.jsonl"
BASELINE = ROOT / "data/baseline/baseline_audit.jsonl"

norm = lambda s: " ".join(s.split())
h    = lambda s: hashlib.sha256(norm(s).encode()).hexdigest()[:12]


def read_jsonl(p):
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


corpus = json.loads(CORPUS.read_text())
want = {h(p["text"]): p for p in corpus}

gw = read_jsonl(GATEWAY)
bl = read_jsonl(BASELINE)

gw_seen = {h(r["prompt"]) for r in gw if "prompt" in r}
bl_seen = {h(r["prompt"]) for r in bl if "prompt" in r}

print("=" * 84)
print("IDENTICAL-CORPUS VERIFICATION".center(84))
print("=" * 84)
print(f"\nlabelled corpus              : {len(want)} unique prompts   ({CORPUS.relative_to(ROOT)})")
print(f"ADDELA gateway audit trail   : {len(gw):5d} records, {len(gw_seen)} unique prompts")
print(f"                               {GATEWAY.relative_to(ROOT)}")
print(f"LlamaFirewall audit trail    : {len(bl):5d} records, {len(bl_seen)} unique prompts")
print(f"                               {BASELINE.relative_to(ROOT)}")

if not bl:
    print("\nThe baseline trail is empty. Start it and run the console's Comparison tab:")
    print("   docker compose --profile baseline up -d llamafirewall")
    raise SystemExit(0)

both      = gw_seen & bl_seen & set(want)
gw_only   = (gw_seen & set(want)) - bl_seen
bl_only   = (bl_seen & set(want)) - gw_seen
missing   = set(want) - gw_seen - bl_seen

print("\n" + "-" * 84)
print(f"prompts seen by BOTH systems           : {len(both)} / {len(want)}")
print(f"seen by ADDELA only                    : {len(gw_only)}")
print(f"seen by the baseline only              : {len(bl_only)}")
print(f"seen by neither (never tested)         : {len(missing)}")
print("-" * 84)

for tag, s in (("ADDELA only", gw_only), ("baseline only", bl_only), ("untested", missing)):
    for k in sorted(s)[:5]:
        print(f"   [{tag}] #{want[k]['i']:2d} {want[k]['stratum']:12s} {norm(want[k]['text'])[:58]}")

if len(both) == len(want):
    print("\nRESULT: every prompt in the labelled corpus appears in BOTH audit trails,")
    print("        matched on the exact prompt text. The two systems were driven over")
    print("        the identical corpus, and each recorded that fact independently.")
else:
    print(f"\nRESULT: {len(both)} of {len(want)} prompts confirmed in both trails.")
    print("        Re-run the Comparison tab to cover the remainder.")

print("\n" + "-" * 84)
print("SIDE-BY-SIDE — the same prompt as recorded by each system")
print("-" * 84)
gw_last = {h(r["prompt"]): r for r in gw if "prompt" in r}
bl_last = {h(r["prompt"]): r for r in bl if "prompt" in r}
shown = 0
for k in sorted(both, key=lambda k: want[k]["i"]):
    if want[k]["label"] != 1:
        continue
    g, b = gw_last[k], bl_last[k]
    print(f"\n#{want[k]['i']} [{want[k]['stratum']}]  {norm(want[k]['text'])[:70]}")
    print(f"   ADDELA        scores={g.get('scores')} risk={g.get('risk')} -> {g.get('decision')}")
    print(f"   LlamaFirewall decision={b.get('decision')} contained={b.get('contained')}")
    r = (b.get("reason") or "").replace("\n", " ")
    if r:
        print(f"                 reason: {r[:110]}")
    shown += 1
    if shown >= 3:
        break
print("\n" + "=" * 84)

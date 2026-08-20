"""Figure 3, microservices deployment and communication.

Read left to right: the caller, the four stages the request passes through inside
the Docker Compose network, the native model runtime the two model-backed layers
and the protected model live on, and the evidence written to the host filesystem.

The numbered chips are the SAME eight steps used by the request lifecycle figure
Report and the operator console, so the deployment view and the flow view cannot
contradict one another.

Run:  python3 figures/fig_topology.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import _style
from _style import *
_style.FS = 1.50   # the figure is shrunk to ~7in on the page: keep body type >= 1% of canvas width

W, H = 2000, 1300
GREY = "#8894a8"
b = []

# ── header ────────────────────────────────────────────────────────────────────
b.append(text(W/2, 60, "DDELA, microservices deployment and communication", 27, "bold"))
b.append(text(W/2, 94, "On premise · self hosted · seven core containers + one native model runtime",
              15, "normal", BLUE))

# ── clients ───────────────────────────────────────────────────────────────────
b.append(panel(40, 150, 210, 330, "CLIENTS", GREEN))
b.append(titled(58, 212, 174, 86, [("Operator console", {"size": 14}), ("browser · :8080", {"size": 11.5})], "#ffffff", BOXEDGE, 1.5))
b.append(titled(58, 320, 174, 86, [("Application / curl", {"size": 14}), ("POST · :8000", {"size": 11.5})], "#ffffff", BOXEDGE, 1.5))
b.append(text(145, 438, "the only two ports", 12, "normal", MUTED))
b.append(text(145, 458, "published to the host", 12, "normal", MUTED))

# ── compose network ───────────────────────────────────────────────────────────
CX, CY, CW, CH = 290, 150, 1320, 640
b.append(box(CX, CY, CW, CH, "#f6f9fe", BLUE, 2.2, 18, "9 6"))
b.append(text(CX + CW/2, CY + 34, "DOCKER COMPOSE NETWORK, one private bridge · one REST /score contract",
              15, "bold", BLUE))

SY, SH = 212, 552
S1, S2, S3, S4 = 310, 640, 970, 1300
SW = 290
b.append(panel(S1, SY, SW, SH, "EDGE", RED, "#ffffff"))
b.append(panel(S2, SY, SW, SH, "DETECTION, all four at once", BLUE, "#ffffff"))
b.append(panel(S3, SY, SW, SH, "DECISION", GREEN, "#ffffff"))
b.append(panel(S4, SY, SW, SH, "ENFORCEMENT", PURPLE, "#ffffff"))

# 1 · edge
b.append(titled(S1+16, 276, SW-32, 90, [("dashboard",), ("Flask console · nine tabs", {"size": 11.5}), ("read only observer", {"size": 11.5, "style": "i"})]))
b.append(titled(S1+16, 406, SW-32, 90, [("gateway",), ("centralized coordinator", {"size": 11.5}), ("writes the audit log", {"size": 11.5, "style": "i"})], PALE["red"], RED, 2.2))

# 2 · detection
DET = [("nemo-guardrails", "L1 · NeMo self-check rail"), ("prompt-guard", "L2 · DeBERTa (ProtectAI)"),
       ("llama-guard", "L3 · Llama Guard 3"), ("pii-service", "L4 · Microsoft Presidio")]
DYS = [276, 358, 440, 522]
for (t1, t2), y in zip(DET, DYS):
    b.append(titled(S2+16, y, SW-32, 70, [(t1, {"size": 15}), (t2, {"size": 11.5})]))
b.append(titled(S2+16, 622, SW-32, 78, [("llamafirewall", {"size": 15}),
                                        ("external baseline · dormant", {"size": 11.5}),
                                        ("'baseline' profile only", {"size": 11, "style": "i"})], "#f7f8fa", GREY, 1.6))

# 3 · decision
b.append(titled(S3+16, 300, SW-32, 150, [("fusion-service",), ("given the four numbers only,", {"size": 11.5}),
                                         ("it never sees the prompt text", {"size": 11.5, "style": "i"}),
                                         ("risk = 1 − (1−λ)·Π(1−sᵢ)",), ("λ = 0.02",)], PALE["green"], GREEN, 2.2))
b.append(titled(S3+16, 470, SW-32, 96, [("ALLOW < 0.30", {"size": 14}), ("FLAG < 0.60", {"size": 14}),
                                        ("BLOCK ≥ 0.60", {"size": 14})], "#ffffff", BOXEDGE, 1.5))

# 4 · enforcement
b.append(titled(S4+16, 300, SW-32, 96, [("BLOCK or FLAG",), ("the request stops here,", {"size": 11.5}), ("the model is never called", {"size": 11.5, "style": "i"})], PALE["red"], RED, 2))
b.append(titled(S4+16, 430, SW-32, 96, [("ALLOW",), ("the gateway calls gemma4", {"size": 11.5}), ("and receives the answer", {"size": 11.5, "style": "i"})], PALE["green"], GREEN, 2))
b.append(titled(S4+16, 560, SW-32, 96, [("audit line written",), ("one JSON record per request,", {"size": 11.5}), ("before anything is returned", {"size": 11.5, "style": "i"})], PALE["amber"], AMBER, 2))

# ── native runtime ────────────────────────────────────────────────────────────
OX, OY, OW, OH = 1680, 150, 280, 640
b.append(box(OX, OY, OW, OH, PALE["green"], GREEN, 2.2, 18, "9 6"))
b.append(text(OX+OW/2, OY+34, "OLLAMA", 17, "bold", GREEN))
b.append(text(OX+OW/2, OY+56, "native runtime · not containerised", 11.5, "normal", MUTED, style="i"))
b.append(text(OX+OW/2, OY+78, "host :11434", 14, "bold", RED))
b.append(titled(OX+18, 260, OW-36, 92, [("llama3.2:3b", {"size": 15}), ("2.0 GB", {"size": 11.5}), ("L1's self-check", {"size": 11.5})], "#ffffff", "#bcd8c6", 1.6))
b.append(titled(OX+18, 380, OW-36, 92, [("llama-guard3:8b", {"size": 15}), ("4.9 GB", {"size": 11.5}), ("L3's verdict", {"size": 11.5})], "#ffffff", "#bcd8c6", 1.6))
b.append(titled(OX+18, 540, OW-36, 92, [("gemma4:12b-mlx", {"size": 15}), ("7.7 GB", {"size": 11.5}), ("the protected model", {"size": 11.5})], PALE["red"], RED, 2.2))
b.append(text(OX+OW/2, 524, "reached only on an ALLOW", 11.5, "bold", RED))
b.append(text(OX+OW/2, 672, "the containers reach it at", 11.5, "normal", MUTED))
b.append(text(OX+OW/2, 692, "host.docker.internal:11434", 12, "bold", MUTED))

# ── evidence on the host ──────────────────────────────────────────────────────
EY = 880
b.append(box(40, EY, 1920, 170, "#fffaf0", AMBER, 2.2, 18))
b.append(text(1000, EY+34, "EVIDENCE ON THE HOST FILESYSTEM, bind mounted, append only", 15, "bold", AMBER))
FILES = [("data/gateway/audit_log.jsonl", "written by the gateway itself", AMBER),
         ("data/baseline/baseline_audit.jsonl", "the baseline's own independent log", GREY),
         ("data/dashboard/*.json", "results, comparison, combiner tables", BOXEDGE),
         ("services/dashboard/data/prompts.json", "the 67 prompt labelled corpus", BOXEDGE)]
for i, (t1, t2, col) in enumerate(FILES):
    fx = 70 + i * 472
    b.append(titled(fx, EY+58, 442, 86, [(t1, {"size": 14}), (t2, {"size": 11.5})], "#ffffff", col, 1.6))

# ── legend + properties ───────────────────────────────────────────────────────
LY = 1090
b.append(box(40, LY, 940, 156, "#ffffff", BOXEDGE, 1.8, 14))
b.append(text(510, LY+30, "LEGEND, what each line means", 14, "bold", INK))
LEG = [(BLUE, "gateway ↔ detectors · steps 2 and 4", None), (GREEN, "model consults + fusion call · steps 3, 5", "7 5"),
       (RED, "the protected model  ·  step 6", "7 5"), (AMBER, "the audit write  ·  step 7", None),
       (GREY, "baseline only, dormant by default", "7 5")]
for i, (c, lab, dsh) in enumerate(LEG):
    ly = LY + 56 + (i % 3) * 32 if i < 3 else LY + 56 + (i - 3) * 32
    lx = 70 if i < 3 else 540
    b.append(f'<path d="M{lx},{ly} L{lx+46},{ly}" stroke="{c}" stroke-width="3" '
             f'{f"stroke-dasharray=\"{dsh}\"" if dsh else ""} marker-end="url(#ar-{c[1:]})"/>')
    b.append(text(lx + 60, ly + 5, lab, 12.5, "normal", INK, "start"))

b.append(box(1010, LY, 950, 156, "#ffffff", BOXEDGE, 1.8, 14))
b.append(text(1485, LY+30, "PROPERTIES OF THIS DEPLOYMENT", 14, "bold", INK))
PROPS = ["On premise only, no external API keys", "Fail closed, a missing layer scores 1.0",
         "Block before the model, never filtered after", "Fully auditable, one JSON line per request",
         "One decision point, the fusion service", "Reproducible, one docker compose command"]
for i, p in enumerate(PROPS):
    px = 1040 + (i % 2) * 470
    py = LY + 62 + (i // 2) * 32
    b.append(text(px, py, "✓", 14, "bold", GREEN, "start"))
    b.append(text(px + 22, py, p, 12.5, "normal", INK, "start"))

# ── communication links, numbered as in Figure 4 ──────────────────────────────
# Every link runs in its own corridor: the gaps between the stage panels, the gap
# between the network and the runtime, and the band below the network. No line
# crosses a box, and every arrowhead stops clear of the shape it points at.
GW_Y, DB_Y = 451, 321
B1, B2 = 584, 656            # edge-box right edge / detection-box left edge
B3, B4 = 914, 986            # detection right / decision left
B5, B6 = 1244, 1316          # decision right / enforcement left
GAP_A, GAP_B = 606, 934      # S1|S2 corridor (baseline), S2|S3 corridor (models)
GAP_C = 966
RED_C, GRN_A, GRN_B = 1628, 1646, 1662     # corridors between the network and Ollama

# 1 / 8, the caller reaches the gateway and everything returns through it
b.append(route([(250, DB_Y), (326, DB_Y)], BLUE, 2.6, both=True))
b.append(route([(250, GW_Y), (326, GW_Y)], RED, 2.6, both=True))
b.append(chip(268, GW_Y - 40, 1, RED)); b.append(chip(268, GW_Y + 40, 8, RED))

# the console drives the gateway, and the dormant baseline when a comparison is run
b.append(route([(S1+SW/2, 366), (S1+SW/2, 406)], BLUE, 2.4))
b.append(text(S1+SW/2 + 60, 392, "drives", 11.5, "bold", BLUE))
b.append(route([(B1, 300), (GAP_A, 300), (GAP_A, 660), (B2, 660)], GREY, 2.2, "7 5"))

# 2 / 4, the fan-out, and the four scores coming back
b.append(route([(B1, GW_Y), (B2, GW_Y)], BLUE, 2.8, both=True))
b.append(chip(626, GW_Y, 2, BLUE)); b.append(chip(626, GW_Y + 46, 4, BLUE))

# 5, the four numbers, unchanged, to the fusion service
b.append(route([(B3, GW_Y), (B4, GW_Y)], GREEN, 2.8, both=True))
b.append(f'<circle cx="950" cy="{GW_Y}" r="21" fill="#ffffff"/>'); b.append(chip(950, GW_Y, 5, GREEN))

# 6, the verdict is enforced
b.append(route([(B5, GW_Y), (B6, GW_Y)], PURPLE, 2.8))
b.append(chip(1280, GW_Y, 6, PURPLE))

# 3, the two model-backed layers consult their models and read the reply back
b.append(route([(B3, 311), (GAP_B, 311), (GAP_B, 806), (GRN_A, 806), (GRN_A, 306), (OX+18, 306)], GREEN, 2.2, "7 5", both=True))
b.append(route([(B3, 475), (GAP_C, 475), (GAP_C, 826), (GRN_B, 826), (GRN_B, 426), (OX+18, 426)], GREEN, 2.2, "7 5", both=True))
b.append(chip(1180, 806, 3, GREEN))

# 6, and only on an ALLOW does the gateway reach the protected model
b.append(route([(1574, 478), (RED_C, 478), (RED_C, 586), (OX+18, 586)], RED, 2.4, "7 5"))

# 7, the gateway writes the audit line itself
b.append(route([(520, 496), (520, 820), (291, 820), (291, EY)], AMBER, 2.4))
b.append(chip(520, 700, 7, AMBER))

# the baseline keeps its own, separate trail
b.append(route([(700, 700), (700, EY)], GREY, 2.2, "7 5"))

b.append(text(1000, 1272, "The numbered chips are the same eight steps as the request lifecycle figure, so the deployment view and the request flow cannot disagree.",
              13, "normal", MUTED, style="i"))

out = pathlib.Path(__file__).parent / "fig_topology.svg"
out.write_text(svg(W, H, "".join(b), [LINE, RED, GREEN, BLUE, PURPLE, AMBER, GREY]))
print("wrote", out, f"({W}x{H})")

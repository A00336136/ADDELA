from fastapi import FastAPI
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
app = FastAPI()

# Only genuinely sensitive PII counts as a hard gate, NOT LOCATION / PERSON /
# DATE / NRP / URL, which Presidio also detects but which are not sensitive on
# their own (e.g. the country name in "capital of France").
SENSITIVE = [
    "CREDIT_CARD", "US_SSN", "US_ITIN", "US_PASSPORT", "US_DRIVER_LICENSE",
    "US_BANK_NUMBER", "IBAN_CODE", "CRYPTO", "EMAIL_ADDRESS", "PHONE_NUMBER",
    "MEDICAL_LICENSE",
]

class Req(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(req: Req):
    results = analyzer.analyze(text=req.text, language="en", entities=SENSITIVE)
    return {
        "score": max((r.score for r in results), default=0.0),
        "entities": [{"type": r.entity_type, "score": r.score} for r in results],
    }

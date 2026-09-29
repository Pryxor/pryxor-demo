"""MockBank — a realistic payment API for Pryxor demo/testing.
Real HTTP, real state, fake money. Enforces Idempotency-Key so that
Pryxor's retry/idempotency behavior can be tested: re-POSTing the same
key must never double-pay.
"""
import json, os, time, uuid
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="MockBank", docs_url="/docs")

DATA = os.environ.get("BANK_DATA", "./data/bank.json")
os.makedirs(os.path.dirname(DATA), exist_ok=True)

def load():
    if os.path.exists(DATA):
        return json.load(open(DATA))
    return {
        "accounts": {"main": 100000.0},
        "vendors": ["Fournisseur_A", "Fournisseur_B", "Acme_Corp"],
        "payments": [],
    }

def save(db):
    tmp = DATA + ".tmp"
    json.dump(db, open(tmp, "w"), indent=2)
    os.replace(tmp, DATA)

db = load()

class Payment(BaseModel):
    amount: float
    recipient: str
    reference: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "service": "mockbank"}

@app.get("/vendors")
def vendors():
    return {"allowlisted": db["vendors"]}

@app.get("/accounts")
def accounts():
    return {k: f"{v:.2f}" for k, v in db["accounts"].items()}

@app.get("/payments")
def payments():
    return {"count": len(db["payments"]), "payments": db["payments"]}

@app.post("/payments")
def pay(p: Payment, idempotency_key: str = Header(default="")):
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key header required")
    for existing in db["payments"]:
        if existing["idempotency_key"] == idempotency_key:
            # Retry of an already-executed payment: return it, do NOT charge again.
            return {"status": "executed", "duplicate": True, "payment": existing}
    if p.amount <= 0:
        raise HTTPException(400, "amount must be positive")
    if db["accounts"]["main"] < p.amount:
        raise HTTPException(402, "insufficient funds")
    db["accounts"]["main"] -= p.amount
    payment = {
        "id": str(uuid.uuid4())[:8],
        "idempotency_key": idempotency_key,
        "amount": p.amount,
        "recipient": p.recipient,
        "reference": p.reference,
        "ts": time.time(),
    }
    db["payments"].append(payment)
    save(db)
    return {"status": "executed", "duplicate": False, "payment": payment}

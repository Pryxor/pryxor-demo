"""mail_api.py — tiny HTTP -> SMTP bridge so Pryxor's http executors can send
email through the demo's SMTP sink. POST /send {to, subject, body}."""
import os, smtplib
from email.message import EmailMessage
from fastapi import FastAPI
from pydantic import BaseModel, field_validator

app = FastAPI(title="MailBridge")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))
MAIL_FROM = os.environ.get("MAIL_FROM", "ops@company.local")

class Outbound(BaseModel):
    to: str
    subject: str
    body: str

    @field_validator("to")
    @classmethod
    def _to(cls, v: str) -> str:
        # local/lab addresses (ops@company.local) are fine in the demo
        if "@" not in v or v.startswith("@") or v.endswith("@"):
            raise ValueError("invalid address")
        return v

@app.get("/health")
def health():
    return {"status": "ok", "service": "mailbridge", "upstream": f"{SMTP_HOST}:{SMTP_PORT}"}

@app.post("/send")
def send(m: Outbound):
    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = m.to
    msg["Subject"] = m.subject
    msg.set_content(m.body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
        s.send_message(msg)
    return {"status": "queued", "to": m.to}

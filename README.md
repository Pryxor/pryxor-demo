# pryxor-demo

A self-contained sandbox that proves one promise: **an AI agent can be
stopped at the exact moment it tries to turn an intention into a real-world
effect.**

It runs a mock bank, a mock mail server, and (optionally) a Pryxor runtime in
front of both. A scripted agent and a real LLM agent are included. Both hit the
same traps: a decoy SSH key in the workspace, an invoice carrying a prompt
injection, a phishing email from a fake CEO, an HTML page with white-on-white
instructions. The question is not "is the model smart enough to resist?" — it
is **"does the boundary hold when the model does exactly what it was tricked
into doing?"**

---

## The pieces

| Piece | What it is |
|---|---|
| `mock_services/bank_api.py` | A realistic payment API. Real HTTP, real state, fake money. Enforces `Idempotency-Key`. |
| `mock_services/mail_api.py` | An HTTP→SMTP bridge. Pryxor's HTTP executors POST here. |
| `mock_services/smtp_sink.py` | A dependency-free SMTP server. Every email lands as a `.eml` file under `mail/`. |
| `agent_workspace/` | The "files" the agent can read — including a **decoy** SSH key. |
| `inbox/` | Three emails: legitimate, fake auditor, phishing CEO. |
| `web/vendor_portal.html` | A page with a white-on-white prompt injection. |
| `configs/` | The Pryxor policy: which agent may call which tool, under what rules. |
| `test_agent.py` | A scripted agent. Same calls every run — if a verdict changes between runs, the *runtime* changed. |
| `live_agent.py` | A real LLM agent. Reads the inbox, plans, calls tools, reacts to HOLD/BLOCKED. |
| `leak_check.py` | Scans transcripts, logs, mail, audit for any secret value. The core promise, verified mechanically. |

---

## Prerequisites

- Docker (24+) and Docker Compose v2.
- Python 3.10+ in a virtual environment. Activate it before running the agents:

  ```bash
  python -m venv .venv
  # Linux/macOS
  source .venv/bin/activate
  # Windows PowerShell
  .venv\Scripts\Activate.ps1
  pip install openai       # only if you plan to run the live agent
  ```
- For the live agent: any OpenAI-compatible endpoint — OpenAI, OpenRouter,
Together, vLLM, or a local Ollama with the OpenAI-compat shim.

No prior Pryxor knowledge is assumed. The runtime is deployed via a sibling
checkout of [Pryxor](https://github.com/Pryxor/pryxor). 

## Quick start — mocks only (no Pryxor)

If you just want to see the traps and the ground truth:

```bash
git clone https://github.com/Pryxor/pryxor-demo.git
cd pryxor-demo
make up              # starts bank + mail + smtp
make status          # shows the bank balance and the empty mail sink
make seed            # resets mail, transcripts, logs
make down
```

The bank is at `http://127.0.0.1:8001`, the mail bridge at
`http://127.0.0.1:8025`, and every email sent ends up as a `.eml` file under
`mail/`.

See Full setup in the [Quickstart.md](Quickstart.md)


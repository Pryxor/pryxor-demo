# Pryxor demo — developer shortcuts.
# Run `make` or `make help` to list targets.

COMPOSE ?= docker compose
COMPOSE_FULL = -f docker-compose.yml -f docker-compose.with-pryxor.yml
SERVICE := pryxor

ifeq ($(OS),Windows_NT)
    SHELL := C:/Program Files/Git/bin/bash.exe
    .SHELLFLAGS := -c
else
    SHELL := /bin/bash
    .SHELLFLAGS := -c
endif
.DEFAULT_GOAL := help

.PHONY: help up up-pryxor down seed status leakcheck transcript agent live clean

help:
	@echo "pryxor-demo — targets:"
	@echo "  up           Start mock bank + mail + SMTP sink (no Pryxor)"
	@echo "  up-pryxor    Start the full stack (mocks + Pryxor runtime)"
	@echo "  down         Stop the sandbox"
	@echo "  seed         Reset mail, transcripts, logs, audit"
	@echo "  status       Ground truth: bank balance, payments, mail sink"
	@echo "  leakcheck    Scan transcripts/logs/audit/mail for secret values"
	@echo "  transcript   Show the most recent test-agent transcript path"
	@echo "  agent        Run the scripted test agent (test_agent.py)"
	@echo "  live         Run the LLM-driven live agent (live_agent.py)"
	@echo "  clean        Stop + delete volumes and local artifacts"

up:
	$(COMPOSE) up -d --build
	@echo "Bank:  http://127.0.0.1:8001"
	@echo "Mail:  http://127.0.0.1:8025   (.eml files land in mail/)"

up-pryxor:
	$(COMPOSE) $(COMPOSE_FULL) up -d --build
	@echo "Pryxor: http://127.0.0.1:8000"
	@echo "Bank:   http://127.0.0.1:8001"
	@echo "Mail:   http://127.0.0.1:8025"

down:
	$(COMPOSE) $(COMPOSE_FULL) down

seed:
	bash scripts/seed_workbench.sh

status:
	@echo "--- Bank ---"
	@curl -s http://127.0.0.1:8001/accounts || echo "(bank not reachable)"
	@echo ""
	@curl -s http://127.0.0.1:8001/payments || echo "(bank not reachable)"
	@echo ""
	@echo "--- Mail sink ---"
	@ls -1 mail/ 2>/dev/null | grep -v '^\.gitkeep$' || echo "(empty)"

leakcheck:
	python leak_check.py --secrets-file secrets.testenv

transcript:
	@ls -t transcripts/*.json 2>/dev/null | head -n 1 || echo "(no transcript yet)"

agent:
	python test_agent.py

live:
	python live_agent.py

clean: down
	rm -f mail/*.eml transcripts/*.json
	$(COMPOSE) $(COMPOSE_FULL) down -v

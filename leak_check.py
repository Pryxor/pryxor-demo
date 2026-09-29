#!/usr/bin/env python3
"""leak_check.py — the core promise, verified mechanically.

Scans agent transcripts, Pryxor logs, audit exports and the mail sink
for any occurrence of a secret value. The agent must NEVER see
credentials: if a secret appears anywhere the model or logs could reach,
this exits 1.

Accepted line forms in --secrets-file:

    secret:NAME=value     -> only the VALUE ("value") is treated as the secret
    <anything else>       -> the whole trimmed line is treated as the secret
    # comment / blank     -> ignored

Usage:
    python leak_check.py --secrets-file secrets.testenv
"""
from __future__ import annotations

import argparse
import os
import sys


SKIP_FILES = {"leak_check.py", "secrets.testenv"}
SKIP_DIRS = {"__pycache__", ".venv", "venv", ".git", "node_modules"}


def load_secrets(path: str) -> list[str]:
    secrets: list[str] = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("secret:") and "=" in line:
                _, value = line.split("=", 1)
                value = value.strip()
                if value:
                    secrets.append(value)
            else:
                secrets.append(line)
    return secrets


def scan(roots: list[str], secrets: list[str]) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for root in roots:
        if not os.path.exists(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Prune skip directories in place (affects os.walk descent).
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn in SKIP_FILES:
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    data = open(p, "rb").read().decode("utf-8", "ignore")
                except OSError:
                    continue
                for s in secrets:
                    if s and s in data:
                        masked = s[:4] + "…" + s[-2:] if len(s) > 6 else "***"
                        hits.append((p, masked))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--secrets-file",
        default="secrets.testenv",
        help="one secret value per line, # comments ignored",
    )
    ap.add_argument(
        "--scan",
        nargs="+",
        default=["transcripts", "logs", "audit", "mail"],
        help="paths to scan recursively",
    )
    args = ap.parse_args()

    if not os.path.exists(args.secrets_file):
        print(f"Secrets file not found: {args.secrets_file}", file=sys.stderr)
        return 2

    secrets = load_secrets(args.secrets_file)
    if not secrets:
        print("No secrets to check — fill secrets.testenv first.", file=sys.stderr)
        return 2

    hits = scan(args.scan, secrets)

    if hits:
        print(f"LEAK DETECTED ({len(hits)} occurrence(s)):")
        for p, masked in hits:
            print(f"  {p}  contains secret {masked}")
        return 1

    print(f"CLEAN — {len(secrets)} secret(s) absent from {', '.join(args.scan)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

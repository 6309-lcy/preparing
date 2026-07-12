"""
Sunday recap helper.

Reads a wrong-pool export from the app (or builds one from a progress export)
and either:
  1) Prints / saves a Grok-ready prompt, OR
  2) Calls the xAI API if XAI_API_KEY is set (optional paid/free-trial key).

Usage:
  python tools/sunday_recap.py path/to/sunday_recap_YYYY-MM-DD.json
  python tools/sunday_recap.py path/to/soa_grind_progress_YYYY-MM-DD.json
  python tools/sunday_recap.py path/to/sunday_recap.json --api

Without --api: writes tools/outbox/sunday_prompt_*.txt you can paste into Grok.
With --api: needs env XAI_API_KEY (https://console.x.ai/).
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tools" / "outbox"


def load_wrong(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "wrong" in data:
        return data["wrong"]
    if "wrongPool" in data:
        items = []
        for qid, meta in data["wrongPool"].items():
            items.append({"id": qid, **meta})
        return sorted(items, key=lambda x: x.get("count", 0), reverse=True)
    raise SystemExit("Unrecognized JSON: need app sunday export or full progress export")


def build_prompt(wrong: list[dict]) -> str:
    lines = []
    for i, w in enumerate(wrong[:20], 1):
        lines.append(
            f"{i}. [{w.get('id')}] LO={w.get('lo','?')} topics={','.join(w.get('topics') or [])} "
            f"missed={w.get('count')} stem={(w.get('stemPreview') or '')[:350]}"
        )
    body = "\n".join(lines) or "(empty)"
    return (
        "You are my SOA Exam P coach. Below is my WRONG QUESTION POOL.\n"
        "Diagnose weaknesses by learning objective, then produce a Sunday recap:\n"
        "1) Top 5 weakness themes\n"
        "2) Mini formula checklist\n"
        "3) 12 NEW similar multiple-choice questions (A–E) with answers + short solutions\n"
        "4) A 60-minute timed revision plan\n\n"
        f"WRONG POOL:\n{body}\n"
    )


def call_xai(prompt: str, api_key: str) -> str:
    payload = json.dumps(
        {
            "model": "grok-4-1-fast-reasoning",
            "messages": [
                {"role": "system", "content": "You are an expert SOA Exam P coach."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", help="sunday_recap_*.json or progress export")
    parser.add_argument("--api", action="store_true", help="Call xAI API if XAI_API_KEY set")
    args = parser.parse_args()

    path = Path(args.json_path)
    wrong = load_wrong(path)
    prompt = build_prompt(wrong)
    OUT.mkdir(parents=True, exist_ok=True)
    out_prompt = OUT / f"sunday_prompt_{date.today().isoformat()}.txt"
    out_prompt.write_text(prompt, encoding="utf-8")
    print(f"Wrote prompt: {out_prompt}")
    print(f"Wrong items: {len(wrong)}")
    print("Open Grok and paste the prompt, or re-run with --api")

    if args.api:
        key = os.environ.get("XAI_API_KEY")
        if not key:
            raise SystemExit("Set XAI_API_KEY to use --api")
        result = call_xai(prompt, key)
        out_res = OUT / f"sunday_result_{date.today().isoformat()}.md"
        out_res.write_text(result, encoding="utf-8")
        print(f"Wrote result: {out_res}")


if __name__ == "__main__":
    main()

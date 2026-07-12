#!/usr/bin/env python3
"""
SOA Exam Daily Coach — free local / free-cloud friendly.

What it does
------------
1. Reads Study_Plan_Exam_P_FM.md and finds today's day block (best effort).
2. Reads weakness_log.csv and surfaces items due for review.
3. Prints a concise daily briefing to the console.
4. Optionally emails you the briefing via Gmail SMTP (free) or writes a
   Markdown file you can sync / open on your phone.

Setup (email — optional, free)
------------------------------
Gmail:
  1. Enable 2FA on your Google account.
  2. Create an App Password: Google Account → Security → App passwords.
  3. Copy .env.example to .env and fill values (never commit .env).

Windows Task Scheduler (daily 7:00 AM):
  Program: python
  Arguments: C:\\SOA\\tools\\daily_coach.py --email
  Start in: C:\\SOA

Or run manually each morning:
  python C:\\SOA\\tools\\daily_coach.py
  python C:\\SOA\\tools\\daily_coach.py --email
  python C:\\SOA\\tools\\daily_coach.py --date 2026-08-12
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import smtplib
import ssl
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "Study_Plan_Exam_P_FM.md"
WEAKNESS_PATH = ROOT / "weakness_log.csv"
OUTBOX_DIR = ROOT / "tools" / "outbox"
ENV_PATH = ROOT / "tools" / ".env"

# Canonical milestones (adjust if you move exam day)
EXAM_P_TARGET = date(2026, 9, 14)
REGISTRATION_DEADLINE = date(2026, 8, 12)
P_WINDOW_START = date(2026, 9, 10)
P_WINDOW_END = date(2026, 9, 21)

# Rough curriculum map by calendar date (inclusive start)
PHASES = [
    (date(2026, 7, 12), date(2026, 7, 12), "Phase 0 — Setup", "Orientation, baseline, logistics"),
    (date(2026, 7, 13), date(2026, 7, 26), "Phase 1 — General Probability", "LO 1a–1g (23–30%)"),
    (date(2026, 7, 27), date(2026, 8, 30), "Phase 2 — Univariate RVs", "LO 2a–2f (44–50%) + light FM Fridays"),
    (date(2026, 8, 31), date(2026, 9, 7), "Phase 3 — Multivariate + integrate", "LO 3a–3i (23–30%)"),
    (date(2026, 9, 8), date(2026, 9, 13), "Phase 4 — Final week", "Mocks + diagnosis only"),
    (date(2026, 9, 14), date(2026, 9, 14), "EXAM P DAY", "Sit Exam P (window 10–21 Sep)"),
    (date(2026, 9, 15), date(2026, 9, 28), "Phase 5 — Transition / FM", "Shift primary focus to FM"),
]


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def phase_for(d: date) -> tuple[str, str]:
    for start, end, name, focus in PHASES:
        if start <= d <= end:
            return name, focus
    if d < PHASES[0][0]:
        return "Before plan start", "Read the study plan and begin Day 0"
    return "Beyond written plan", "Follow high-level FM roadmap in the study plan"


def weekday_plan_hint(d: date) -> str:
    name, focus = phase_for(d)
    wd = d.strftime("%A")
    days_to_exam = (EXAM_P_TARGET - d).days

    if d == EXAM_P_TARGET:
        return (
            "EXAM DAY. Light morning only (optional 0–2 easy problems). "
            "ID + calculator + arrive early. Answer every question."
        )

    if name.startswith("Phase 4"):
        return (
            f"{wd}: FINAL WEEK. Timed practice → diagnose → micro-drills. "
            "No new learning. No FM. Protect sleep."
        )

    if name.startswith("Phase 5"):
        return (
            f"{wd}: Post-P transition. Primary FM (TVM → annuities → loans…). "
            "If P unsuccessful, switch to P repair plan instead."
        )

    if wd in {"Saturday", "Sunday"}:
        return (
            f"{wd}: Active recall + timed set/mock + diagnosis. "
            f"Phase: {name}. Focus: {focus}."
        )

    if wd == "Friday" and date(2026, 7, 31) <= d <= date(2026, 9, 4):
        return (
            f"Friday dual-track: ~75–85 min Exam P + ~30–45 min light FM (TVM/annuities). "
            f"Phase: {name}."
        )

    base = (
        f"{wd} standard 2h: (A) 20–25m spaced recall → (B) 45–55m new concept → "
        f"(C) 40–50m exam-style practice → (D) 5m weakness log. "
        f"Phase: {name} | {focus}."
    )
    if 0 <= days_to_exam <= 21:
        base += f" | {days_to_exam} days to target Exam P sitting."
    if d == REGISTRATION_DEADLINE:
        base += " | ⚠ REGISTER FOR EXAM P TODAY."
    elif d < REGISTRATION_DEADLINE:
        base += f" | Registration deadline in {(REGISTRATION_DEADLINE - d).days} day(s)."
    return base


def extract_plan_snippet(plan_text: str, d: date) -> str:
    """Best-effort extract of the day's section from the markdown plan."""
    # Match headings like "#### Day 12 — Tuesday 28 July" or "### Day 0 — Sunday 12 July"
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    # Patterns used in the plan: "13 July", "1 August", "12 September"
    day_token = f"{d.day} {months[d.month]}"
    # Also "12 July 2026" style in Day 0
    patterns = [
        rf"(#### Day \d+ —[^\n]*{re.escape(day_token)}[^\n]*\n)(.*?)(?=\n#### |\n### |\n# |\Z)",
        rf"(### Day 0[^\n]*{re.escape(day_token)}[^\n]*\n)(.*?)(?=\n#### |\n### |\n# |\Z)",
        rf"(#### Weekend[^\n]*{re.escape(day_token)}[^\n]*\n)(.*?)(?=\n#### |\n### |\n# |\Z)",
        rf"(### Monday 14 September[^\n]*\n)(.*?)(?=\n#### |\n### |\n# |\Z)",
    ]
    for pat in patterns:
        m = re.search(pat, plan_text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            block = (m.group(1) + m.group(2)).strip()
            if len(block) > 2500:
                block = block[:2500] + "\n… (truncated; see full plan)"
            return block
    return (
        "No exact day block found in the markdown for this date "
        "(weekend labels or custom shifts). Use the phase guidance + open the plan file."
    )


def due_weaknesses(path: Path, d: date) -> list[dict[str, str]]:
    if not path.exists():
        return []
    due: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nxt = (row.get("next_review") or "").strip()
            if not nxt:
                continue
            # next_review may be "2026-07-21;2026-07-23;2026-07-27"
            dates = []
            for part in re.split(r"[;,]", nxt):
                part = part.strip()
                if not part:
                    continue
                try:
                    dates.append(datetime.strptime(part, "%Y-%m-%d").date())
                except ValueError:
                    continue
            if any(x <= d for x in dates):
                due.append(row)
    return due


def build_briefing(d: date) -> str:
    name, focus = phase_for(d)
    plan_text = PLAN_PATH.read_text(encoding="utf-8") if PLAN_PATH.exists() else ""
    snippet = extract_plan_snippet(plan_text, d) if plan_text else "(plan file missing)"
    due = due_weaknesses(WEAKNESS_PATH, d)

    lines = [
        f"# SOA Daily Coach — {d.isoformat()} ({d.strftime('%A')})",
        "",
        f"**Phase:** {name}",
        f"**Focus:** {focus}",
        f"**Target Exam P sitting:** {EXAM_P_TARGET.isoformat()} "
        f"({(EXAM_P_TARGET - d).days} days away)" if d <= EXAM_P_TARGET
        else f"**Exam P target date has passed** (window was {P_WINDOW_START}–{P_WINDOW_END})",
        f"**Registration deadline:** {REGISTRATION_DEADLINE.isoformat()}",
        "",
        "## Today's operating instructions",
        weekday_plan_hint(d),
        "",
        "## Plan excerpt",
        snippet,
        "",
        "## Spaced-repetition due today",
    ]

    if not due:
        lines.append("_No weakness_log items due (or log empty). Do standard recall anyway._")
    else:
        for i, row in enumerate(due[:12], 1):
            lines.append(
                f"{i}. [{row.get('exam','?')}/{row.get('lo_code','?')}] "
                f"{row.get('topic','')} — last: {row.get('result','')} "
                f"({row.get('error_type','')}) | {row.get('notes','')}"
            )
        if len(due) > 12:
            lines.append(f"… +{len(due) - 12} more in weakness_log.csv")

    lines += [
        "",
        "## End-of-session checklist",
        "- [ ] Practiced under mild time pressure",
        "- [ ] Logged Guessed/Missed items to weakness_log.csv",
        "- [ ] Scheduled next_review dates (D+1, D+3, D+7)",
        "- [ ] Updated formula_sheet_P.md if a formula is now solid",
        "",
        f"_Generated locally from {PLAN_PATH.name}_",
    ]
    return "\n".join(lines)


def send_email(subject: str, body_md: str, env: dict[str, str]) -> None:
    user = env.get("SMTP_USER") or os.environ.get("SMTP_USER")
    password = env.get("SMTP_PASS") or os.environ.get("SMTP_PASS")
    to_addr = env.get("EMAIL_TO") or os.environ.get("EMAIL_TO") or user
    host = env.get("SMTP_HOST") or os.environ.get("SMTP_HOST") or "smtp.gmail.com"
    port = int(env.get("SMTP_PORT") or os.environ.get("SMTP_PORT") or "465")

    if not user or not password or not to_addr:
        raise SystemExit(
            "Email not configured. Create tools/.env from tools/.env.example "
            "with SMTP_USER, SMTP_PASS, EMAIL_TO."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(body_md, "plain", "utf-8"))
    # Simple HTML wrapper
    html = "<pre style='font-family:Segoe UI,Roboto,monospace;white-space:pre-wrap'>" + (
        body_md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    ) + "</pre>"
    msg.attach(MIMEText(html, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())


def main() -> None:
    parser = argparse.ArgumentParser(description="SOA Exam daily coach")
    parser.add_argument("--date", help="YYYY-MM-DD (default: today)")
    parser.add_argument("--email", action="store_true", help="Send briefing via SMTP")
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="Save markdown to tools/outbox (default on)",
    )
    parser.add_argument("--no-save", action="store_true", help="Do not write outbox file")
    args = parser.parse_args()

    if args.date:
        d = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        d = date.today()

    briefing = build_briefing(d)
    print(briefing)

    if not args.no_save and args.save:
        OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
        out = OUTBOX_DIR / f"briefing_{d.isoformat()}.md"
        out.write_text(briefing, encoding="utf-8")
        print(f"\n[saved] {out}")

    if args.email:
        env = load_env(ENV_PATH)
        subject = f"SOA Daily Coach — {d.isoformat()} — {phase_for(d)[0]}"
        send_email(subject, briefing, env)
        print("[email] sent")


if __name__ == "__main__":
    main()

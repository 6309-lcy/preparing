"""
Match SOA sample questions PDF + solutions PDF → app/data raw JSON.

Usage:
  python tools/match_qa.py              # Exam P (default)
  python tools/match_qa.py --exam P
  python tools/match_qa.py --exam FM

Looks in C:\\SOA\\Questions\\ and subfolders like Answer/, Answers/, Solutions/.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "Questions"
DATA = ROOT / "app" / "data"


def find_pdfs(exam: str) -> tuple[Path | None, Path | None]:
    """Return (questions_pdf, solutions_pdf) for exam P or FM."""
    exam = exam.upper()
    q_cands: list[Path] = []
    s_cands: list[Path] = []

    for p in QDIR.rglob("*.pdf"):
        name = p.name.lower()
        if exam == "P":
            # Prefer P, exclude FM
            if "fm" in name:
                continue
            if any(k in name for k in ("quest", "question")) and "sol" not in name:
                q_cands.append(p)
            if any(k in name for k in ("sol", "answer")) and "quest" not in name:
                s_cands.append(p)
            # common SOA names: edu-exam-p-sample-sol.pdf
            if "exam-p" in name and "sol" in name:
                if p not in s_cands:
                    s_cands.append(p)
            if "exam-p" in name and ("quest" in name or "question" in name) and "sol" not in name:
                if p not in q_cands:
                    q_cands.append(p)
        else:  # FM
            if "fm" not in name and "financial" not in name:
                continue
            if any(k in name for k in ("quest", "question")) and "sol" not in name:
                q_cands.append(p)
            if any(k in name for k in ("sol", "answer")):
                s_cands.append(p)

    def rank(p: Path) -> tuple:
        parent = p.parent.name.lower()
        in_answer = 1 if parent in {"answer", "answers", "solutions", "sols"} else 0
        # prefer official-looking names
        name = p.name.lower()
        quality = 0
        if "edu-exam-p" in name or "exam-p-sample" in name:
            quality += 2
        if "2018-10-exam-fm" in name or "exam-fm" in name:
            quality += 2
        return (in_answer, quality, p.stat().st_mtime)

    q_cands = sorted(set(q_cands), key=rank, reverse=True)
    s_cands = sorted(set(s_cands), key=rank, reverse=True)
    return (q_cands[0] if q_cands else None, s_cands[0] if s_cands else None)


def extract_text(pdf: Path) -> str:
    r = PdfReader(str(pdf))
    chunks = [page.extract_text() or "" for page in r.pages]
    text = "\n".join(chunks)
    return re.sub(r"Page \d+ of \d+\s*", "", text)


def parse_questions(text: str, exam: str) -> list[dict]:
    parts = re.split(r"\n(?=\d{1,3}\.\s)", text)
    questions = []
    prefix = "P" if exam.upper() == "P" else "FM"
    for part in parts[1:]:
        m = re.match(r"(\d{1,3})\.\s*(.*)", part, re.S)
        if not m:
            continue
        qnum = int(m.group(1))
        body = m.group(2).strip()
        choices: dict[str, str] = {}
        cm = re.search(
            r"\(A\)\s*(.*?)\s*\(B\)\s*(.*?)\s*\(C\)\s*(.*?)\s*\(D\)\s*(.*?)\s*\(E\)\s*(.*)",
            body,
            re.S,
        )
        stem = body
        if cm:
            stem = body[: cm.start()].strip()
            for i, letter in enumerate("ABCDE"):
                val = re.sub(r"\s+", " ", cm.group(i + 1)).strip()
                val = re.split(r"\n\d{1,3}\.\s", val)[0].strip()
                choices[letter] = val
        stem = re.sub(r"\s+", " ", stem).strip()
        if len(stem) < 20:
            continue
        questions.append(
            {
                "id": f"{prefix}-SOA-{qnum}",
                "source": f"SOA Exam {prefix} Sample Questions",
                "number": qnum,
                "exam": prefix,
                "stem": stem,
                "choices": choices,
                "answer": None,
                "lo": None,
                "topics": [],
            }
        )
    return questions


def parse_answers(text: str) -> dict[int, str]:
    answers: dict[int, str] = {}
    # Common SOA patterns
    for m in re.finditer(r"(\d{1,3})\.\s*Solution:\s*([A-E])\b", text):
        answers[int(m.group(1))] = m.group(2)
    if len(answers) < 20:
        for m in re.finditer(r"(?m)^(\d{1,3})\.\s*([A-E])\b", text):
            answers.setdefault(int(m.group(1)), m.group(2))
    return answers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exam", default="P", choices=["P", "FM", "p", "fm"])
    args = parser.parse_args()
    exam = args.exam.upper()

    DATA.mkdir(parents=True, exist_ok=True)
    qpdf, spdf = find_pdfs(exam)
    if not qpdf:
        raise SystemExit(f"No {exam} questions PDF found under {QDIR} (including Answer/)")
    print(f"[{exam}] Questions PDF: {qpdf.relative_to(ROOT)}")
    questions = parse_questions(extract_text(qpdf), exam)
    print(f"[{exam}] Parsed questions: {len(questions)}")

    raw_name = "questions_raw.json" if exam == "P" else "questions_raw_fm.json"
    ans_name = "answers_raw.json" if exam == "P" else "answers_raw_fm.json"
    (DATA / raw_name).write_text(json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8")

    if spdf:
        print(f"[{exam}] Solutions PDF: {spdf.relative_to(ROOT)}")
        answers = parse_answers(extract_text(spdf))
        print(f"[{exam}] Parsed answers: {len(answers)}")
        (DATA / ans_name).write_text(
            json.dumps({str(k): v for k, v in sorted(answers.items())}, indent=2),
            encoding="utf-8",
        )
        # attach answers preview
        hit = sum(1 for q in questions if str(q["number"]) in {str(k) for k in answers})
        print(f"[{exam}] Questions with matching answer numbers: ~check via build")
        # merge for report
        matched = 0
        for q in questions:
            a = answers.get(q["number"])
            if a:
                q["answer"] = a
                matched += 1
        print(f"[{exam}] Direct number matches: {matched}/{len(questions)}")
    else:
        print(f"[{exam}] No solutions PDF found in Questions/ or Answer/")

    print(f"Done. Wrote app/data/{raw_name}" + (f" and {ans_name}" if spdf else ""))
    if exam == "P":
        print("Next: python tools/build_question_bank.py")


if __name__ == "__main__":
    main()

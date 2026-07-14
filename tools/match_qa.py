"""
Match SOA sample questions + solutions → app/data raw JSON.

Uses PyMuPDF for better text layout than pypdf, then:
- preserves line structure for tables / piecewise densities
- cleans common math OCR/layout damage
- flags low-quality stems so the app can warn the user

Usage:
  python tools/match_qa.py --exam P
  python tools/match_qa.py --exam FM
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz  # PyMuPDF
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "Questions"
DATA = ROOT / "app" / "data"


def find_pdfs(exam: str) -> tuple[Path | None, Path | None]:
    exam = exam.upper()
    q_cands: list[Path] = []
    s_cands: list[Path] = []

    for p in QDIR.rglob("*.pdf"):
        name = p.name.lower()
        if exam == "P":
            if "fm" in name:
                continue
            if any(k in name for k in ("quest", "question")) and "sol" not in name:
                q_cands.append(p)
            if any(k in name for k in ("sol", "answer")) and "quest" not in name:
                s_cands.append(p)
            if "exam-p" in name and "sol" in name and p not in s_cands:
                s_cands.append(p)
            if "exam-p" in name and ("quest" in name or "question" in name) and "sol" not in name:
                if p not in q_cands:
                    q_cands.append(p)
        else:
            if "fm" not in name and "financial" not in name:
                continue
            if any(k in name for k in ("quest", "question")) and "sol" not in name:
                q_cands.append(p)
            if any(k in name for k in ("sol", "answer")):
                s_cands.append(p)

    def rank(p: Path) -> tuple:
        parent = p.parent.name.lower()
        in_answer = 1 if parent in {"answer", "answers", "solutions", "sols"} else 0
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


def extract_pdf_text_pymupdf(pdf: Path) -> str:
    doc = fitz.open(str(pdf))
    chunks = []
    for i, page in enumerate(doc):
        t = page.get_text("text") or ""
        # drop running headers
        t = re.sub(r"Page \d+ of \d+\s*", "", t)
        chunks.append(t)
    doc.close()
    return "\n".join(chunks)


def extract_pdf_text_pypdf(pdf: Path) -> str:
    r = PdfReader(str(pdf))
    text = "\n".join((p.extract_text() or "") for p in r.pages)
    return re.sub(r"Page \d+ of \d+\s*", "", text)


def clean_math(s: str) -> str:
    """Heuristic repairs for common SOA PDF layout damage."""
    if not s:
        return s
    original = s

    # Normalize weird spaces
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+\n", "\n", s)

    # P[A ∪ B] style: "[ ] 0.7PA B∪=" or multi-line "P A B ∪ ="
    s = re.sub(
        r"\[\s*\]\s*([0-9.]+)\s*P\s*A\s*B\s*∪\s*=",
        r"P(A ∪ B) = \1",
        s,
    )
    s = re.sub(
        r"\[\s*\]\s*([0-9.]+)\s*P\s*A\s*B\s*[′']\s*∪\s*=",
        r"P(A ∪ B') = \1",
        s,
    )
    s = re.sub(
        r"P\s*A\s*B\s*∪\s*=\s*([0-9.]+)",
        r"P(A ∪ B) = \1",
        s,
    )
    s = re.sub(
        r"P\s*A\s*B\s*[′']\s*∪\s*=\s*([0-9.]+)",
        r"P(A ∪ B') = \1",
        s,
    )
    # Multi-line pymupdf: P A \n B \n ∪ \n = \n 0.7
    s = re.sub(
        r"P\s*\n\s*A\s*\n\s*B\s*\n\s*∪\s*\n\s*=\s*\n\s*([0-9.]+)",
        r"P(A ∪ B) = \1",
        s,
    )
    s = re.sub(
        r"P\s*\n\s*A\s*\n\s*B\s*[′']\s*\n\s*∪\s*\n\s*=\s*\n\s*([0-9.]+)",
        r"P(A ∪ B') = \1",
        s,
    )
    # Bracket form from pymupdf
    s = re.sub(
        r"\[\s*\]\s*\n\s*([0-9.]+)\s*\n\s*P\s*A\s*\n\s*B\s*\n\s*∪\s*\n\s*=",
        r"P(A ∪ B) = \1",
        s,
    )
    s = re.sub(
        r"\[\s*\]\s*\n\s*([0-9.]+)\s*\n\s*P\s*A\s*\n\s*B\s*[′']\s*\n\s*∪\s*\n\s*=",
        r"P(A ∪ B') = \1",
        s,
    )

    # p(n+1)=0.2 p(n)
    s = re.sub(
        r"\(\s*1\s*\)\s*0\.2\s*\(\s*\)\s*p\s*n\s*p\s*n\s*\+\s*=",
        "p(n+1) = 0.2 p(n)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"\(\s*1\s*\)\s*0\.2\s*\(\s*\)\s*pn\s*pn\s*\+=",
        "p(n+1) = 0.2 p(n)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"for all integers\s+0\s*n\s*≥\s*,\s*p\(n\+1\)\s*=\s*0\.2 p\(n\)",
        "for all integers n ≥ 0, p(n+1) = 0.2 p(n)",
        s,
        flags=re.I,
    )
    s = re.sub(r"0\s*n\s*≥", "n ≥ 0", s)
    s = re.sub(r"where\s*\(\s*\)\s*p\s*n\s*represents", "where p(n) represents", s, flags=re.I)
    s = re.sub(r"where\s*\(\s*\)\s*pn\s*represents", "where p(n) represents", s, flags=re.I)

    # Density f(y)=3/y^4 for y>1  (many PDF layout variants)
    s = re.sub(
        r"density function:\s*3\s*2\s*,\s*1\s*\(\s*\)\s*0,\s*otherwise\.\s*y\s*y\s*f y\s*−\s*\s*>\s*=\s*\s*",
        "density function: f(y) = 3/y^4 for y > 1, and f(y) = 0 otherwise.",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"density function:\s*32,\s*1\(\)\s*yyfy\s*−.*?otherwise\.",
        "density function: f(y) = 3/y^4 for y > 1, and f(y) = 0 otherwise.",
        s,
        flags=re.I | re.S,
    )
    # After soft line-join: "3 2 , 1 ( ) 0, otherwise. y y f y − { > = }"
    s = re.sub(
        r"density function:\s*3\s*2\s*,\s*1\s*\(\s*\)\s*0,\s*otherwise\.\s*y\s*y\s*f\s*y\s*−\s*\s*>\s*=\s*\s*",
        "density function: f(y) = 3/y^4 for y > 1, and f(y) = 0 otherwise.",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"density function:\s*3\s+2\s*,\s*1\s*\(\s*\)\s*0,\s*otherwise\.\s*\n?\s*y\s+y\s+f y\s+−\s*\s*>\s*=\s*\s*",
        "density function: f(y) = 3/y^4 for y > 1, and f(y) = 0 otherwise.",
        s,
        flags=re.I,
    )
    # Generic: if we see classic benefit-limit-10 + density junk, force known SOA form
    if re.search(r"benefit limit of 10", s, re.I) and re.search(r"density function", s, re.I):
        if re.search(r"3\s*2|y\s*y\s*f||otherwise", s):
            s = re.sub(
                r"density function:.*?(?=Calculate)",
                "density function: f(y) = 3/y^4 for y > 1, and f(y) = 0 otherwise.\n\n",
                s,
                flags=re.I | re.S,
            )

    # Partial damage density (SOA sample classic) — run on raw multiline first
    if re.search(r"deductible", s, re.I) and re.search(r"partial damage", s, re.I):
        if re.search(r"density\s*function", s, re.I) and re.search(r"0\.5003|/2|otherwise", s, re.I):
            s = re.sub(
                r"density\s*function[\s\S]*?(?=Calculate)",
                "density function f(x) = (1/2)*exp(-x/2) for 0 < x < 15, and 0 otherwise (x in thousands).\n\n",
                s,
                count=1,
                flags=re.I,
            )

    # Weather loss density 2.5 * 200^2.5 / x^3.5 , x>200
    if re.search(r"weather-related loss", s, re.I) and re.search(r"density function", s, re.I):
        if re.search(r"2\.5|200|otherwise", s, re.I):
            s = re.sub(
                r"density function[\s\S]*?(?=Calculate)",
                "density function f(x) = 2.5 * (200**2.5) / (x**3.5) for x > 200, and 0 otherwise.\n\n",
                s,
                count=1,
                flags=re.I,
            )

    # Age table reconstruction (Q18-style): ages then p(acc) then portion
    s = re.sub(
        r"Age of\s*\n?\s*Driver\s*\n?\s*Probability\s*\n?\s*of Accident\s*\n?\s*Portion of Company[’']s\s*\n?\s*Insured Drivers\s*\n?"
        r"16-20\s*\n\s*21-30\s*\n\s*31-65\s*\n\s*66-99\s*\n"
        r"([0-9.]+)\s*\n\s*([0-9.]+)\s*\n\s*([0-9.]+)\s*\n\s*([0-9.]+)\s*\n"
        r"([0-9.]+)\s*\n\s*([0-9.]+)\s*\n\s*([0-9.]+)\s*\n\s*([0-9.]+)",
        (
            "\nAge | P(Accident) | Portion of insured drivers\n"
            "16-20 | \\1 | \\5\n"
            "21-30 | \\2 | \\6\n"
            "31-65 | \\3 | \\7\n"
            "66-99 | \\4 | \\8\n"
        ),
        s,
        flags=re.I,
    )
    # Collapsed single-line version
    s = re.sub(
        r"Age of Driver Probability of Accident Portion of Company[’']s Insured Drivers\s*"
        r"16-20\s+21-30\s+31-65\s+66-99\s+"
        r"([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+"
        r"([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)",
        (
            "\nAge | P(Accident) | Portion of insured drivers\n"
            "16-20 | \\1 | \\5\n"
            "21-30 | \\2 | \\6\n"
            "31-65 | \\3 | \\7\n"
            "66-99 | \\4 | \\8\n"
        ),
        s,
        flags=re.I,
    )

    # Joint table X=0,1,2 Y=0,1 style (Q581-ish)
    s = re.sub(
        r"X\s+0\s+1\s+2\s+Y\s+0\s+([0-9/]+)\s+([0-9/]+)\s+([0-9/]+)\s+1\s+([0-9/]+)\s+([0-9/]+)\s+([0-9/]+)",
        (
            "\n      X=0    X=1    X=2\n"
            "Y=0   \\1    \\2    \\3\n"
            "Y=1   \\4    \\5    \\6\n"
        ),
        s,
    )

    # Proportional to (1+x)^{-4}
    s = re.sub(
        r"proportional to \(1 \+ x\)-\s*4",
        "proportional to (1 + x)^{-4}",
        s,
        flags=re.I,
    )
    s = re.sub(r"for 0\s*\n\s*x\s*\n\s*<\s*\n\s*<\s*∞", "for 0 < x < ∞", s)
    s = re.sub(r"for 0x\s*<\s*<\s*∞", "for 0 < x < ∞", s)

    # Collapse excessive blank lines but keep single newlines for tables
    s = re.sub(r"\n{3,}", "\n\n", s)
    # Soft-wrap: join hyphenated line breaks carefully — skip if line looks like a table row
    lines = s.split("\n")
    out_lines = []
    buf = ""
    for line in lines:
        line_st = line.strip()
        if not line_st:
            if buf:
                out_lines.append(buf.strip())
                buf = ""
            out_lines.append("")
            continue
        # Keep table-ish lines separate
        if "|" in line_st or re.match(r"^(Age|Y=\d|X=\d|\d{2}-\d{2}\s\|)", line_st):
            if buf:
                out_lines.append(buf.strip())
                buf = ""
            out_lines.append(line_st)
            continue
        if not buf:
            buf = line_st
        else:
            # if previous ends with mid-sentence, join with space
            if buf[-1] in ".:;?!" or line_st[0].isupper() and len(buf) > 40:
                out_lines.append(buf.strip())
                buf = line_st
            else:
                buf = buf + " " + line_st
    if buf:
        out_lines.append(buf.strip())
    s = "\n".join(out_lines)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r" *\n *", "\n", s).strip()

    return s if s else original


def quality_score(stem: str, choices: dict) -> tuple[str, list[str]]:
    """Return (ok|warn|bad, reasons)."""
    reasons = []
    if not stem or len(stem) < 40:
        reasons.append("stem_too_short")
    if len(choices) < 5:
        reasons.append("missing_choices")
    # garbled math indicators
    if re.search(r"\[\s*\]\s*[0-9.]*\s*P[A-Z]", stem):
        reasons.append("broken_probability_notation")
    if re.search(r"yyfy|xexfx|pn\s*pn\s*\+=", stem, re.I):
        reasons.append("broken_formula_layout")
    if "density function" in stem.lower() and not re.search(r"f\s*\(|f\([xy]\)|density function:\s*f", stem, re.I):
        if re.search(r"[{−]|otherwise", stem):
            reasons.append("piecewise_density_may_be_garbled")
    if stem.count("∪") + stem.count("∩") > 0 and "P(" not in stem and "P[" not in stem:
        if re.search(r"P\s*A\s*B", stem):
            reasons.append("set_ops_without_clear_P")
    # table without structure
    if re.search(r"following (statistics|table)", stem, re.I) and "|" not in stem:
        if re.search(r"\d\.\d{2}\s+\d\.\d{2}\s+\d\.\d{2}", stem):
            reasons.append("table_may_be_hard_to_read")
    if len(reasons) >= 2:
        return "bad", reasons
    if reasons:
        return "warn", reasons
    return "ok", []


def _looks_like_question_start(after_number: str) -> bool:
    """Reject mid-formula lines like '1.\\n x < 0' that are NOT new SOA questions."""
    s = after_number.lstrip()
    if not s:
        return False
    # Real SOA stems almost always start with a letter / quote after the number
    # (possibly on the next line).
    head = s[:80]
    # Strip a single leading newline block
    head = re.sub(r"^\s+", "", head)
    if not head:
        return False
    ch = head[0]
    if ch.isalpha() or ch in "\"'“":
        return True
    # Sometimes starts with "An" already matched; or "For", "The"
    if re.match(r"^(An|The|For|In|If|Let|You|Calculate|Determine|Which|Of|A |An )", head):
        return True
    return False


def parse_questions(text: str, exam: str) -> list[dict]:
    """
    Split only on *real* SOA question numbers.

    Critical: PDF math layouts often put bare lines like ``1.`` or ``2.`` inside
    piecewise functions. We only accept strictly increasing question numbers and
    stems that start like English exam text.
    """
    questions = []
    prefix = "P" if exam.upper() == "P" else "FM"

    # Candidate starts: line beginning with N.
    cand_iter = list(re.finditer(r"(?m)^(\d{1,3})\.\s*", text))
    starts: list[tuple[int, int, int]] = []  # (qnum, start_idx, body_start)
    last_num = 0
    for m in cand_iter:
        qnum = int(m.group(1))
        body_start = m.end()
        # Must be strictly increasing (handles deleted numbers with gaps)
        if qnum <= last_num:
            continue
        # Allow gaps (deleted Qs) but not wild jumps backward; jumps forward OK
        if qnum > last_num + 50 and last_num > 0:
            # huge jump is suspicious mid-doc; still allow if stem looks real
            pass
        after = text[body_start : body_start + 200]
        if not _looks_like_question_start(after):
            continue
        starts.append((qnum, m.start(), body_start))
        last_num = qnum

    for i, (qnum, _abs_start, body_start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        body = text[body_start:end].strip()
        if not body:
            continue

        cm = re.search(
            r"\(A\)\s*(.*?)\s*\(B\)\s*(.*?)\s*\(C\)\s*(.*?)\s*\(D\)\s*(.*?)\s*\(E\)\s*(.*)",
            body,
            re.S,
        )
        choices: dict[str, str] = {}
        stem_raw = body
        if cm:
            stem_raw = body[: cm.start()].strip()
            for j, letter in enumerate("ABCDE"):
                val = cm.group(j + 1)
                val = re.split(r"(?m)^\s*\d{1,3}\.\s", val)[0]
                val = re.sub(r"\s+", " ", val).strip()
                # drop trailing page junk
                val = re.sub(r"\s*Page\s+\d+.*$", "", val).strip()
                choices[letter] = val
        else:
            continue

        stem = clean_math(stem_raw)
        q_level, reasons = quality_score(stem, choices)
        if len(stem) < 20:
            continue

        questions.append(
            {
                "id": f"{prefix}-SOA-{qnum}",
                "source": f"SOA Exam {prefix} Sample Questions",
                "number": qnum,
                "exam": prefix,
                "stem": stem,
                "stemRaw": re.sub(r"\s+", " ", stem_raw).strip()[:2500],
                "choices": choices,
                "answer": None,
                "lo": None,
                "topics": [],
                "quality": q_level,
                "qualityNotes": reasons,
            }
        )
    return questions


def parse_answers(text: str) -> dict[int, str]:
    answers: dict[int, str] = {}
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
        raise SystemExit(f"No {exam} questions PDF under {QDIR}")

    print(f"[{exam}] Questions PDF: {qpdf.relative_to(ROOT)}")
    try:
        text = extract_pdf_text_pymupdf(qpdf)
        print(f"[{exam}] Extractor: PyMuPDF")
    except Exception as e:
        print(f"[{exam}] PyMuPDF failed ({e}); falling back to pypdf")
        text = extract_pdf_text_pypdf(qpdf)

    questions = parse_questions(text, exam)
    print(f"[{exam}] Parsed questions: {len(questions)}")
    qc = {"ok": 0, "warn": 0, "bad": 0}
    for q in questions:
        qc[q["quality"]] = qc.get(q["quality"], 0) + 1
    print(f"[{exam}] Quality: {qc}")

    raw_name = "questions_raw.json" if exam == "P" else "questions_raw_fm.json"
    ans_name = "answers_raw.json" if exam == "P" else "answers_raw_fm.json"
    (DATA / raw_name).write_text(json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8")

    if spdf:
        print(f"[{exam}] Solutions PDF: {spdf.relative_to(ROOT)}")
        # answers: pypdf is fine
        try:
            atext = extract_pdf_text_pymupdf(spdf)
        except Exception:
            atext = extract_pdf_text_pypdf(spdf)
        answers = parse_answers(atext)
        print(f"[{exam}] Parsed answers: {len(answers)}")
        (DATA / ans_name).write_text(
            json.dumps({str(k): v for k, v in sorted(answers.items())}, indent=2),
            encoding="utf-8",
        )
        matched = 0
        for q in questions:
            a = answers.get(q["number"])
            if a:
                q["answer"] = a
                matched += 1
        print(f"[{exam}] Answer matches: {matched}/{len(questions)}")
        # rewrite with answers attached for inspection
        (DATA / raw_name).write_text(json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(f"[{exam}] No solutions PDF found")

    # Spot-check known problem numbers
    if exam == "P":
        by_n = {q["number"]: q for q in questions}
        for n in (3, 13, 18, 50, 51):
            q = by_n.get(n)
            if q:
                print(f"--- Q{n} [{q['quality']}] ---")
                print(q["stem"][:300])
                print()

    print("Done. Next: python tools/build_question_bank.py")


if __name__ == "__main__":
    main()

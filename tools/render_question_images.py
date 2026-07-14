"""
Render each SOA sample question as a clean PNG crop from the official PDF.

This avoids broken math/tables in text extraction. The app can show these
images as the primary question display.

Usage:
  python tools/render_question_images.py
  python tools/render_question_images.py --exam P --zoom 2.0

Outputs:
  app/data/qimg/P-SOA-1.png  (or P-SOA-1_a.png, P-SOA-1_b.png if multi-page)
  app/data/qimg_index.json   maps question id -> list of image paths
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "Questions"
OUT = ROOT / "app" / "data" / "qimg"
INDEX = ROOT / "app" / "data" / "qimg_index.json"


def find_questions_pdf(exam: str) -> Path:
    exam = exam.upper()
    cands = []
    for p in QDIR.rglob("*.pdf"):
        name = p.name.lower()
        if exam == "P":
            if "fm" in name:
                continue
            if ("quest" in name or "question" in name) and "sol" not in name:
                cands.append(p)
        else:
            if "fm" in name and ("quest" in name or "question" in name) and "sol" not in name:
                cands.append(p)
    if not cands:
        raise SystemExit(f"No {exam} questions PDF found")
    cands.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    # prefer edu-exam-p
    cands.sort(key=lambda p: (0 if "edu-exam-p" in p.name.lower() else 1, -p.stat().st_mtime))
    return cands[0]


def find_question_anchors(doc: fitz.Document) -> list[dict]:
    """
    Find (page, num, y0) for each real question number label on the left margin.
    SOA labels look like '1.' at x≈72.
    """
    anchors = []
    last_num = 0
    for pi in range(doc.page_count):
        page = doc[pi]
        words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,word_no
        # Group by approximate line
        for w in words:
            x0, y0, x1, y1, text, *_ = w
            if x0 > 95:  # only left-gutter numbers
                continue
            m = re.fullmatch(r"(\d{1,3})\.", text.strip())
            if not m:
                continue
            num = int(m.group(1))
            # Strictly increasing — skip formula fragments like mid-piecewise '1.'
            if num <= last_num:
                continue
            # Question numbers are rarely > 30 apart from deletions; allow gaps
            if last_num and num > last_num + 80:
                continue
            # Prefer typical SOA body top area (not footer page numbers)
            if y0 > page.rect.height - 40:
                continue
            anchors.append(
                {
                    "num": num,
                    "page": pi,
                    "y0": y0 - 4,  # small pad above
                    "x0": 48,
                    "label_y1": y1,
                }
            )
            last_num = num
    return anchors


def render_slices(doc: fitz.Document, anchors: list[dict], zoom: float, prefix: str) -> dict:
    """
    Returns { "P-SOA-1": ["data/qimg/P-SOA-1.png"], ... }
    Multi-page questions get _a, _b suffixes.
    """
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob(f"{prefix}-SOA-*.png"):
        old.unlink()

    mat = fitz.Matrix(zoom, zoom)
    index: dict[str, list[str]] = {}
    footer = 40
    header = 40
    left = 48
    right_pad = 36

    for i, anc in enumerate(anchors):
        num = anc["num"]
        qid = f"{prefix}-SOA-{num}"
        next_anc = anchors[i + 1] if i + 1 < len(anchors) else None
        clips: list[tuple[int, fitz.Rect]] = []

        p0 = anc["page"]
        y_start = max(anc["y0"], header)

        if next_anc is None:
            # last question: rest of its page only (usually enough)
            page = doc[p0]
            rect = fitz.Rect(left, y_start, page.rect.width - right_pad, page.rect.height - footer)
            clips.append((p0, rect))
        elif next_anc["page"] == p0:
            page = doc[p0]
            y_end = max(next_anc["y0"] - 3, y_start + 50)
            rect = fitz.Rect(left, y_start, page.rect.width - right_pad, y_end)
            clips.append((p0, rect))
        else:
            # start page → bottom
            page = doc[p0]
            rect = fitz.Rect(left, y_start, page.rect.width - right_pad, page.rect.height - footer)
            clips.append((p0, rect))
            # full middle pages
            for pi in range(p0 + 1, next_anc["page"]):
                page = doc[pi]
                rect = fitz.Rect(left, header, page.rect.width - right_pad, page.rect.height - footer)
                clips.append((pi, rect))
            # final page → next question
            page = doc[next_anc["page"]]
            y_end = max(next_anc["y0"] - 3, header + 50)
            rect = fitz.Rect(left, header, page.rect.width - right_pad, y_end)
            clips.append((next_anc["page"], rect))

        paths = []
        letters = "abcdefghijklmnopqrstuvwxyz"
        valid_clips = []
        for pi, rect in clips:
            page = doc[pi]
            rect = rect & page.rect
            if rect.height < 25 or rect.width < 50:
                continue
            valid_clips.append((pi, rect))

        for ci, (pi, rect) in enumerate(valid_clips):
            page = doc[pi]
            pix = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
            fname = f"{qid}.png" if len(valid_clips) == 1 else f"{qid}_{letters[ci]}.png"
            pix.save(str(OUT / fname))
            paths.append(f"data/qimg/{fname}")

        if paths:
            index[qid] = paths
            if num <= 5 or num in (18, 50, 51) or num % 100 == 0:
                print(f"  {qid}: {len(paths)} image(s)")

    return index


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exam", default="P", choices=["P", "FM", "p", "fm"])
    ap.add_argument("--zoom", type=float, default=2.0, help="render scale (2=retina)")
    args = ap.parse_args()
    exam = args.exam.upper()
    prefix = exam

    pdf = find_questions_pdf(exam)
    print(f"PDF: {pdf}")
    doc = fitz.open(str(pdf))
    anchors = find_question_anchors(doc)
    print(f"Found {len(anchors)} question anchors (first={anchors[0]['num'] if anchors else None}, last={anchors[-1]['num'] if anchors else None})")
    if len(anchors) < 50:
        print("WARNING: unusually few anchors — check left-margin detection")

    index = render_slices(doc, anchors, args.zoom, prefix)
    doc.close()

    # merge with existing index if FM later
    if INDEX.exists():
        try:
            old = json.loads(INDEX.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    else:
        old = {}
    # drop old keys for this exam
    old = {k: v for k, v in old.items() if not k.startswith(f"{prefix}-SOA-")}
    old.update(index)
    INDEX.write_text(json.dumps(old, indent=2), encoding="utf-8")
    print(f"Wrote {len(index)} question image sets → {OUT}")
    print(f"Index: {INDEX}")


if __name__ == "__main__":
    main()

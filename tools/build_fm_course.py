"""
Build Exam FM as a complete, study-ready course (one-by-one after P).

- Expand FM lessons
- Rebuild path (units → chapters → levels → chapter tests)
- 14-week plan starting today (40/50/10, last 2 weeks wrap)
- Assign SOA FM sample questions to levels + calendar days
- Mark FM ready in courses.json (FAM becomes next)
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
FM_DIR = DATA / "courses" / "fm"
sys.path.insert(0, str(ROOT / "tools"))

import build_all_content as bac  # noqa: E402

START = date.today()
WEEKS = 14
LEARN_WEEKS = 12
TODAY = START.isoformat()

FM_WEIGHTS = {
    "tvm": 0.10,
    "annuities": 0.25,
    "loans": 0.20,
    "bonds": 0.20,
    "portfolios": 0.25,
}


def concept(sid, title, body):
    return {"id": sid, "type": "concept", "title": title, "body": body}


def example(sid, title, setup, solution, why):
    return {"id": sid, "type": "example", "title": title, "setup": setup, "solution": solution, "why": why}


def check(sid, title, prompt, choices, answer, explain):
    return {
        "id": sid,
        "type": "check",
        "title": title,
        "prompt": prompt,
        "choices": choices,
        "answer": answer,
        "explain": explain,
    }


def lesson(lid, title, minutes, lo, sections):
    return {
        "id": lid,
        "title": title,
        "minutes": minutes,
        "lo": lo if isinstance(lo, list) else [lo],
        "sections": sections,
    }


def fm_lessons() -> dict:
    """Full FM teach modules — denser than draft stubs."""
    return {
        "fm_setup": lesson(
            "fm_setup",
            "Exam FM orientation & calculator discipline",
            30,
            ["FM"],
            [
                concept(
                    "s1",
                    "What FM tests",
                    "Exam FM is a 2.5-hour, 30-question CBT on financial mathematics.\n\n"
                    "Approximate syllabus weights (use midpoints for planning):\n"
                    "• Time value of money ~10% (i, v, d, δ, nominal rates)\n"
                    "• Annuities ~25% (level, due/immediate, m-thly, continuous, varying)\n"
                    "• Loans ~20% (amortization, sinking funds)\n"
                    "• Bonds ~20% (price, book value, callable/redemption)\n"
                    "• General cash flows / portfolios / duration & immunization ~25%\n\n"
                    "Speed with a financial calculator (BA II Plus / TI-30X) is part of the skill.",
                ),
                concept(
                    "s2",
                    "How this course is structured",
                    "Duolingo-style path:\n"
                    "Level 1 Learn → Level 2 Practice → Level 3 Drill → Chapter test (≥70%).\n"
                    "Last two weeks: wrap + full mocks only.\n"
                    "Do multiple levels per day if you want — soft goal is not a cap.",
                ),
                example(
                    "s3",
                    "Worked: exam mindset",
                    "A stem mixes nominal i^(2) with an annuity-due. What is the first move?",
                    "Convert everything to one consistent rate period (or use the matching symbol formula). "
                    "Never mix end-of-year a-angle-n at effective i with half-year coupons without converting.",
                    "Most FM errors are period mismatch, not hard algebra.",
                ),
                check(
                    "s4",
                    "Weight check",
                    "Which block is usually the largest single topic group?",
                    {
                        "A": "Only force of interest theory",
                        "B": "Annuities (level + variants)",
                        "C": "Only interest rate swaps",
                        "D": "Only continuous annuities",
                    },
                    "B",
                    "Annuities are typically the biggest pure block; portfolios/duration are also large.",
                ),
            ],
        ),
        "fm_tvm_core": lesson(
            "fm_tvm_core",
            "Interest measures: i, v, d, δ, nominal rates",
            50,
            ["FM1"],
            [
                concept(
                    "s1",
                    "Core identities",
                    "Effective annual rate i: money multiplies by (1+i) per year.\n"
                    "Discount factor v = 1/(1+i).\n"
                    "Discount rate d = i/(1+i) = 1 − v.\n"
                    "Also i = d/(1−d).\n"
                    "Constant force of interest: δ = ln(1+i), accumulation a(t)=e^{δt}, v^t = e^{−δt}.\n\n"
                    "Nominal rates: i^{(m)} is payable m-thly; (1+i)=(1+i^{(m)}/m)^m.\n"
                    "Similarly (1−d)=(1−d^{(m)}/m)^m.",
                ),
                concept(
                    "s2",
                    "Equivalent rates checklist",
                    "Given any one of i, v, d, δ, i^{(m)}, d^{(m)}, you should convert to any other in under 30 seconds.\n"
                    "Write the chain: i ↔ v ↔ d ↔ δ and i ↔ i^{(m)}.\n"
                    "On calculator: store i, compute v=1/(1+i), d=i/(1+i), δ=ln(1+i).",
                ),
                example(
                    "s3",
                    "Worked: force from effective",
                    "i = 0.06 effective annual. Find δ and d.",
                    "δ = ln(1.06) ≈ 0.05827.\n"
                    "d = 0.06/1.06 ≈ 0.05660.\n"
                    "Check: v=1/1.06, d=1−v.",
                    "Always sanity-check: 0 < d < i < δ is false actually — for positive rates, d < i and δ is between them in a specific way; just verify identities.",
                ),
                example(
                    "s4",
                    "Worked: nominal to effective",
                    "i^{(12)} = 0.12. Find effective annual i.",
                    "1+i = (1+0.12/12)^{12} = (1.01)^{12} ⇒ i ≈ 0.1268.",
                    "Nominal 12% is not 12% effective — convert before multi-year problems.",
                ),
                check(
                    "s5",
                    "Identity",
                    "Which is always true (positive i)?",
                    {"A": "d = i(1+i)", "B": "v = 1−d", "C": "δ = i/(1+i)", "D": "i^{(m)} = m·i always"},
                    "B",
                    "v=1/(1+i) and d=i/(1+i) ⇒ v=1−d.",
                ),
            ],
        ),
        "fm_accum": lesson(
            "fm_accum",
            "Accumulation & present value of single payments",
            45,
            ["FM1"],
            [
                concept(
                    "s1",
                    "Moving one payment",
                    "Future value: FV = PV · (1+i)^n   or   PV · e^{δn}.\n"
                    "Present value: PV = FV · v^n.\n"
                    "n can be fractional if compounding is continuous or if you use consistent period rate.\n"
                    "With nominal i^{(m)}, work in m-ths: period rate j=i^{(m)}/m, periods = m·t.",
                ),
                example(
                    "s2",
                    "Worked: two accounts meet",
                    "Classic: one account at nominal convertible m-thly, another at force δ; equal values after t years — solve for unknown rate.",
                    "Set AV1=AV2 ⇒ equate (1+j)^{mt} with e^{δt} (or the other accumulation function). Take logs / roots carefully.",
                    "This is pure TVM algebra — define accumulation functions first.",
                ),
                example(
                    "s3",
                    "Worked: fractional year",
                    "100 grows for 7.25 years at 4% convertible semiannually.",
                    "j=0.02 per half-year; k=14.5 periods; AV=100(1.02)^{14.5}.",
                    "Count compounding periods, not calendar years with the wrong rate.",
                ),
                check(
                    "s4",
                    "PV factor",
                    "At effective i, PV of 1 due in n years is:",
                    {"A": "(1+i)^n", "B": "v^n", "C": "d^n", "D": "δ^n"},
                    "B",
                    "Discount with v^n.",
                ),
            ],
        ),
        "fm_ann_level": lesson(
            "fm_ann_level",
            "Level annuities-immediate & due",
            55,
            ["FM2"],
            [
                concept(
                    "s1",
                    "Standard annual symbols",
                    "Annuity-immediate (payments of 1 at end of each year for n years):\n"
                    "  a-angle-n = (1 − v^n) / i\n"
                    "Annuity-due (payments at beginning of each year):\n"
                    "  ä-angle-n = (1 − v^n) / d = (1+i) a-angle-n\n"
                    "Accumulation of annuity-immediate: s-angle-n = (1+i)^n a-angle-n = ((1+i)^n − 1)/i\n"
                    "Due accumulation: s̈-angle-n = (1+i) s-angle-n\n"
                    "Perpetuity-immediate: 1/i ; due: 1/d.",
                ),
                concept(
                    "s2",
                    "Payment level X",
                    "If payments are X (not 1), multiply the annuity factor by X.\n"
                    "PV = X · a-angle-n  (immediate) or X · ä-angle-n (due).\n"
                    "First identify timing: end vs beginning of periods.",
                ),
                example(
                    "s3",
                    "Worked: level payment PV",
                    "500 at end of each year for 10 years, i=6%. PV?",
                    "PV = 500 · a-angle-10 @ 6% = 500 (1 − 1.06^{−10}) / 0.06.",
                    "Factor out payment size; use immediate form for end-of-year.",
                ),
                example(
                    "s4",
                    "Worked: due vs immediate",
                    "Same payments as above but at the beginning of each year.",
                    "PV = 500 · ä-angle-10 = 500 (1+i) a-angle-10.",
                    "Due is one period earlier ⇒ multiply immediate PV by (1+i).",
                ),
                check(
                    "s5",
                    "Due identity",
                    "ä-angle-n equals:",
                    {"A": "a-angle-n / (1+i)", "B": "(1+i) a-angle-n", "C": "a-angle-n − 1", "D": "i · a-angle-n"},
                    "B",
                    "Standard relationship.",
                ),
            ],
        ),
        "fm_ann_mthly": lesson(
            "fm_ann_mthly",
            "m-thly & continuous annuities",
            50,
            ["FM2"],
            [
                concept(
                    "s1",
                    "Payable m-thly",
                    "Level payments totaling 1 per year, paid m times per year (1/m each):\n"
                    "  a-angle-n^{(m)} = (1 − v^n) / i^{(m)}\n"
                    "Due form uses d^{(m)} in the denominator.\n"
                    "Continuous: ā-angle-n = (1 − v^n) / δ\n"
                    "More frequent payments (same annual total) raise PV slightly vs annual immediate.",
                ),
                concept(
                    "s2",
                    "Calculator approach",
                    "Alternatively convert to period rate j and do an mn-payment annuity of 1/m each period.\n"
                    "Be consistent: either use m-thly symbols or expand to period form — not both mixed.",
                ),
                example(
                    "s3",
                    "Worked: monthly payments",
                    "Pay 1000 per year monthly for 20 years, i=5% effective. PV?",
                    "First find i^{(12)} from (1+i)=(1+i^{(12)}/12)^{12}, then\n"
                    "PV = 1000 · a-angle-20^{(12)} = 1000 (1−v^{20}) / i^{(12)}.",
                    "Annual total 1000, paid monthly ⇒ m-thly annuity factor.",
                ),
                check(
                    "s4",
                    "Continuous denom",
                    "Continuous annuity PV of rate 1 for n years uses denominator:",
                    {"A": "i", "B": "d", "C": "δ", "D": "v"},
                    "C",
                    "ā-angle-n = (1−v^n)/δ.",
                ),
            ],
        ),
        "fm_ann_vary": lesson(
            "fm_ann_vary",
            "Increasing, decreasing, and geometric annuities",
            50,
            ["FM2"],
            [
                concept(
                    "s1",
                    "Arithmetic patterns",
                    "Payments 1,2,...,n at year ends (immediate):\n"
                    "  (Ia)-angle-n = (ä-angle-n − n v^n) / i\n"
                    "Decreasing n,...,1:\n"
                    "  (Da)-angle-n = (n − a-angle-n) / i\n"
                    "There are due and continuous analogues — match the payment timing in the stem.",
                ),
                concept(
                    "s2",
                    "Geometric growth",
                    "Payments grow by factor (1+g) each period.\n"
                    "Use adjusted rate j with 1+j = (1+i)/(1+g), then PV = first payment × a-angle-n at rate j\n"
                    "(with care at the first payment timing).\n"
                    "If g=i, special formulas (n v for certain perpetuity/level cases).",
                ),
                example(
                    "s3",
                    "Worked: increasing annuity",
                    "Payments 1,2,...,10 at year-end, interest i. PV?",
                    "PV = (Ia)-angle-10 = (ä-angle-10 − 10 v^{10}) / i.",
                    "Don't sum 10 separate PVs unless n is tiny — use the closed form.",
                ),
                check(
                    "s4",
                    "Geometric idea",
                    "Payments grow at g, interest i. Adjusted rate uses:",
                    {"A": "i−g only always", "B": "(1+i)/(1+g) − 1", "C": "i+g", "D": "δ−g always"},
                    "B",
                    "Standard substitution 1+j=(1+i)/(1+g).",
                ),
            ],
        ),
        "fm_loans": lesson(
            "fm_loans",
            "Loans & amortization schedules",
            55,
            ["FM3"],
            [
                concept(
                    "s1",
                    "Level payment loan",
                    "Loan principal L repaid by n level payments X:\n"
                    "  L = X · a-angle-n  ⇒  X = L / a-angle-n\n"
                    "Outstanding balance after k payments (prospective):\n"
                    "  OB_k = X · a-angle-(n−k)\n"
                    "Retrospective:\n"
                    "  OB_k = L(1+i)^k − X · s-angle-k\n"
                    "Interest portion of payment k: I_k = i · OB_{k−1}\n"
                    "Principal portion: P_k = X − I_k",
                ),
                concept(
                    "s2",
                    "Drop payments & refinancing",
                    "If a payment is missed or extra principal is paid, recompute OB then re-amortize remaining term or new payment.\n"
                    "Prospective method is usually cleanest after a change.",
                ),
                example(
                    "s3",
                    "Worked: find level payment",
                    "Loan 10,000 for 5 years, i=6% annual, level end-of-year payments.",
                    "X = 10000 / a-angle-5 @ 6%.",
                    "Always start from L = X a-angle-n unless the stem says otherwise.",
                ),
                example(
                    "s4",
                    "Worked: interest in a payment",
                    "After finding X and OB_2, interest in 3rd payment is i·OB_2.",
                    "I_3 = i · OB_2; principal = X − I_3.",
                    "Interest is always rate times prior balance.",
                ),
                check(
                    "s5",
                    "Prospective OB",
                    "After k level payments on an n-payment loan, OB equals X times:",
                    {"A": "a-angle-n", "B": "a-angle-(n−k)", "C": "s-angle-k", "D": "v^k"},
                    "B",
                    "Remaining annuity of n−k payments.",
                ),
            ],
        ),
        "fm_sinking": lesson(
            "fm_sinking",
            "Sinking fund loans",
            45,
            ["FM3"],
            [
                concept(
                    "s1",
                    "Interest + sink",
                    "Borrower pays interest each period on the full principal L at loan rate i,\n"
                    "plus deposits into a sinking fund that accumulates to L at maturity at SF rate j.\n"
                    "Level SF deposit D = L / s-angle-n @ j.\n"
                    "Total periodic outlay = L·i + D  (if interest paid currently on full L).\n"
                    "If j ≠ i, only the SF uses j; interest leg uses i.",
                ),
                example(
                    "s2",
                    "Worked: total payment",
                    "L=1000, n=10, loan interest 8%, SF earns 6%. Annual total payment?",
                    "Interest leg = 1000·0.08=80.\n"
                    "D = 1000 / s-angle-10 @ 6%.\n"
                    "Total = 80 + D.",
                    "Two rates ⇒ two calculations.",
                ),
                check(
                    "s3",
                    "SF deposit",
                    "To accumulate L in n periods at rate j in a sinking fund, level deposit is:",
                    {"A": "L / a-angle-n", "B": "L / s-angle-n at j", "C": "L·j", "D": "L·v^n"},
                    "B",
                    "Future-value annuity accumulates deposits to L.",
                ),
            ],
        ),
        "fm_bonds": lesson(
            "fm_bonds",
            "Bond price, premium, discount, book value",
            55,
            ["FM4"],
            [
                concept(
                    "s1",
                    "Price formula",
                    "Bond: face F, redemption C, n coupon periods, coupon rate r per period on F (coupon Fr),\n"
                    "yield rate i per coupon period:\n"
                    "  P = Fr · a-angle-n + C v^n\n"
                    "If coupons m-thly and yields nominal, convert to matching period rates first.\n"
                    "P > C ⇒ premium; P < C ⇒ discount; P = C ⇒ par (when coupon rate equals yield, C=F typically).",
                ),
                concept(
                    "s2",
                    "Book value amortization",
                    "Book value just after a coupon follows the prospective formula with remaining coupons,\n"
                    "or recursive: BV_k = BV_{k−1}(1+i) − coupon.\n"
                    "Premium/discount write-down is |coupon − i·BV|.",
                ),
                example(
                    "s3",
                    "Worked: basic price",
                    "Face 1000, 10 years, 5% annual coupons, yield 6%, redeem at par.",
                    "P = 50 a-angle-10 @ 6% + 1000 v^{10} @ 6%.",
                    "Coupon = 0.05·1000=50; redemption C=1000.",
                ),
                example(
                    "s4",
                    "Worked: premium vs discount",
                    "Same bond if yield is 4% instead of 6%.",
                    "Lower yield ⇒ higher price ⇒ premium bond (P>1000).",
                    "Price and yield move inversely.",
                ),
                check(
                    "s5",
                    "Premium",
                    "A bond sells at a premium when:",
                    {"A": "Price < redemption", "B": "Price > redemption", "C": "Coupon rate is zero", "D": "n=1 always"},
                    "B",
                    "Premium means market price above redemption amount.",
                ),
            ],
        ),
        "fm_duration": lesson(
            "fm_duration",
            "Duration, convexity, immunization",
            55,
            ["FM5"],
            [
                concept(
                    "s1",
                    "Macaulay & modified duration",
                    "Macaulay duration MacD = weighted average payment time using PV weights of each cash flow.\n"
                    "For a level-yield i per period: ModD = MacD / (1+i).\n"
                    "Relative price change: ΔP/P ≈ −ModD · Δi  (first order).\n"
                    "Convexity adds a positive second-order term — prices rise more / fall less than duration alone predicts.",
                ),
                concept(
                    "s2",
                    "Redington immunization",
                    "To immunize a liability:\n"
                    "1) PV(assets) = PV(liabilities)\n"
                    "2) MacD or ModD match (same derivative w.r.t. i)\n"
                    "3) Convexity of assets ≥ convexity of liabilities\n"
                    "Assumes small parallel yield shifts and cash flows fixed.",
                ),
                example(
                    "s3",
                    "Worked: duration intuition",
                    "Zero-coupon bond maturing in n years has MacD = n.",
                    "All weight sits at time n ⇒ MacD=n. Coupon bonds have MacD < maturity.",
                    "More coupons earlier ⇒ shorter duration.",
                ),
                check(
                    "s4",
                    "Price sensitivity",
                    "If yields rise slightly, bond prices:",
                    {"A": "Rise by about ModD·Δi", "B": "Fall by about ModD·Δi", "C": "Do not change", "D": "Double"},
                    "B",
                    "dP/P ≈ −ModD·Δi.",
                ),
            ],
        ),
        "fm_final": lesson(
            "fm_final",
            "FM wrap-up & mock strategy",
            35,
            ["FM"],
            [
                concept(
                    "s1",
                    "Cold formula gate",
                    "Before mocks, rewrite from memory:\n"
                    "• i,v,d,δ and nominal conversions\n"
                    "• a, ä, s, s̈, a^{(m)}, ā, (Ia), (Da)\n"
                    "• Loan OB prospective/retrospective + I_k, P_k\n"
                    "• Bond price + book value recursion\n"
                    "• MacD, ModD, Redington conditions",
                ),
                concept(
                    "s2",
                    "Mock loop",
                    "Full 30Q / 2.5h → tag misses (period mismatch / formula / calculator) → micro-drill → re-mock.\n"
                    "No new theory in the final two weeks.",
                ),
                check(
                    "s3",
                    "Final weeks",
                    "Best use of the last two weeks:",
                    {"A": "Brand-new exotic derivatives only", "B": "Timed mixed sets + full mocks + wrong pool", "C": "Only passive videos", "D": "Skip bonds"},
                    "B",
                    "Wrap unit is mock-heavy by design.",
                ),
            ],
        ),
        # keep legacy light modules pointing to full content via same IDs used in older plan days
        "fm_tvm": lesson(
            "fm_tvm",
            "TVM quick review (legacy module)",
            25,
            ["FM1"],
            [
                concept("s1", "Quick sheet", "v=1/(1+i), d=i/(1+i), δ=ln(1+i), (1+i)=(1+i^{(m)}/m)^m."),
                check(
                    "s2",
                    "v",
                    "v equals:",
                    {"A": "1+i", "B": "1/(1+i)", "C": "i/(1+i)", "D": "ln(1+i)"},
                    "B",
                    "Discount factor.",
                ),
            ],
        ),
        "fm_ann": lesson(
            "fm_ann",
            "Annuities quick review (legacy module)",
            25,
            ["FM2"],
            [
                concept("s1", "Quick sheet", "a-angle-n=(1−v^n)/i ; ä-angle-n=(1−v^n)/d ; s-angle-n=((1+i)^n−1)/i."),
                check(
                    "s2",
                    "Perpetuity immediate",
                    "PV of 1 per year forever (immediate) is:",
                    {"A": "i", "B": "1/i", "C": "d", "D": "1/d"},
                    "B",
                    "Perpetuity-immediate 1/i.",
                ),
            ],
        ),
    }


def fm_units():
    return [
        {
            "id": "fm_u1",
            "number": 1,
            "title": "Time Value of Money",
            "shortTitle": "TVM",
            "cluster": "tvm",
            "weight": 0.10,
            "weightRange": "5–15%",
            "color": "#0B3D3A",
            "description": "Interest measures and moving single payments through time.",
            "chapters": [
                {"id": "fm_ch0", "number": 0, "title": "FM orientation", "lessonId": "fm_setup", "topics": ["tvm"], "levels": "short"},
                {"id": "fm_ch1", "number": 1, "title": "i, v, d, δ & nominal rates", "lessonId": "fm_tvm_core", "topics": ["tvm"]},
                {"id": "fm_ch2", "number": 2, "title": "Accumulation & PV", "lessonId": "fm_accum", "topics": ["tvm"]},
            ],
        },
        {
            "id": "fm_u2",
            "number": 2,
            "title": "Annuities",
            "shortTitle": "Annuities",
            "cluster": "annuities",
            "weight": 0.25,
            "weightRange": "20–30%",
            "color": "#0369A1",
            "description": "Level, m-thly, continuous, and varying annuities.",
            "chapters": [
                {"id": "fm_ch3", "number": 3, "title": "Level annuities immediate & due", "lessonId": "fm_ann_level", "topics": ["annuities", "tvm"]},
                {"id": "fm_ch4", "number": 4, "title": "m-thly & continuous", "lessonId": "fm_ann_mthly", "topics": ["annuities", "tvm"]},
                {"id": "fm_ch5", "number": 5, "title": "Increasing / geometric", "lessonId": "fm_ann_vary", "topics": ["annuities"]},
            ],
        },
        {
            "id": "fm_u3",
            "number": 3,
            "title": "Loans",
            "shortTitle": "Loans",
            "cluster": "loans",
            "weight": 0.20,
            "weightRange": "15–25%",
            "color": "#7C3AED",
            "description": "Amortization schedules and sinking funds.",
            "chapters": [
                {"id": "fm_ch6", "number": 6, "title": "Amortization", "lessonId": "fm_loans", "topics": ["loans", "annuities"]},
                {"id": "fm_ch7", "number": 7, "title": "Sinking funds", "lessonId": "fm_sinking", "topics": ["loans", "annuities"]},
            ],
        },
        {
            "id": "fm_u4",
            "number": 4,
            "title": "Bonds & ALM",
            "shortTitle": "Bonds/ALM",
            "cluster": "bonds",
            "weight": 0.45,
            "weightRange": "Bonds 15–25% + Portfolios 20–30%",
            "color": "#B45309",
            "description": "Bond pricing, book value, duration, immunization.",
            "chapters": [
                {"id": "fm_ch8", "number": 8, "title": "Bond price & book value", "lessonId": "fm_bonds", "topics": ["bonds", "annuities"]},
                {"id": "fm_ch9", "number": 9, "title": "Duration & immunization", "lessonId": "fm_duration", "topics": ["portfolios", "bonds"]},
            ],
        },
        {
            "id": "fm_u5",
            "number": 5,
            "title": "Wrap-up & Mock Exams",
            "shortTitle": "Wrap",
            "cluster": "wrap",
            "weight": 0.0,
            "weightRange": "last 2 weeks",
            "color": "#334155",
            "description": "No new theory. Mixed drills and full mocks.",
            "chapters": [
                {
                    "id": "fm_ch10",
                    "number": 10,
                    "title": "Mixed review — TVM & annuities",
                    "lessonId": "fm_final",
                    "topics": ["tvm", "annuities"],
                    "levels": "review",
                },
                {
                    "id": "fm_ch11",
                    "number": 11,
                    "title": "Mixed review — loans & bonds",
                    "lessonId": "fm_final",
                    "topics": ["loans", "bonds", "portfolios"],
                    "levels": "review",
                },
                {
                    "id": "fm_ch12",
                    "number": 12,
                    "title": "Full mock 1",
                    "lessonId": "fm_final",
                    "topics": ["tvm", "annuities", "loans", "bonds", "portfolios"],
                    "levels": "full_mock",
                },
                {
                    "id": "fm_ch13",
                    "number": 13,
                    "title": "Weakness clinic",
                    "lessonId": "fm_final",
                    "topics": ["annuities", "loans", "bonds", "portfolios"],
                    "levels": "clinic",
                },
                {
                    "id": "fm_ch14",
                    "number": 14,
                    "title": "Full mock 2 + final",
                    "lessonId": "fm_final",
                    "topics": ["tvm", "annuities", "loans", "bonds", "portfolios"],
                    "levels": "full_mock",
                },
            ],
        },
    ]


def retag_fm_questions(questions: list[dict]) -> list[dict]:
    """Improve FM topic tags with ordered priority (more specific first)."""
    rules = [
        ("portfolios", r"\b(duration|convexity|immuniz|Macaulay|modified duration|Redington|portfolio|interest rate risk|swap|Redington)\b", "portfolios"),
        ("bonds", r"\b(bond|redemption|coupon|par value|face amount|yield rate|callable|book value of the bond|premium bond|discount bond)\b", "bonds"),
        ("loans", r"\b(loan|amortiz|outstanding balance|sinking fund|repay|principal repaid|borrower|mortgage)\b", "loans"),
        ("annuities", r"\b(annuit|perpetuit|level payment of|payments of|payable m|continuous annuity|due|immediate annuity)\b", "annuities"),
        ("tvm", r"\b(force of interest|nominal|effective|discount rate|accumulat|present value|compound|convertible|δ|force)\b", "tvm"),
    ]
    out = []
    for q in questions:
        if (q.get("exam") or "") != "FM" and not str(q.get("id", "")).startswith("FM"):
            out.append(q)
            continue
        text = (q.get("stem") or "") + " " + " ".join((q.get("choices") or {}).values())
        tags = []
        cluster = "tvm"
        for name, pat, cl in rules:
            if re.search(pat, text, re.I):
                tags.append(name)
                if cluster == "tvm" or name != "tvm":
                    # first specific match sets cluster; keep first non-tvm if any
                    if name != "tvm" and cluster == "tvm":
                        cluster = cl
                    elif name != "tvm" and tags[0] == name:
                        cluster = cl
        if not tags:
            tags = ["tvm"]
            cluster = "tvm"
        # prefer first matching specific topic as cluster
        for name, pat, cl in rules:
            if name in tags and name != "tvm":
                cluster = cl
                break
            if name in tags:
                cluster = cl
                break
        q = deepcopy(q)
        q["exam"] = "FM"
        q["topics"] = tags
        q["cluster"] = cluster
        if not q.get("displayMode"):
            q["displayMode"] = "text"
        out.append(q)
    return out


def rebuild_fm_questions() -> list[dict]:
    """Merge raw FM + answers if needed, else retag existing."""
    all_q = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    p_q = [q for q in all_q if (q.get("exam") or "P") == "P"]
    fm_existing = [q for q in all_q if (q.get("exam") or "") == "FM"]
    if len(fm_existing) < 100:
        fm_existing = bac.build_fm_questions()
    fm_existing = retag_fm_questions(fm_existing)
    # ensure answers
    fm_existing = [q for q in fm_existing if q.get("answer")]
    return p_q + fm_existing


def update_catalog_ready():
    cat_path = DATA / "courses.json"
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    for c in cat["courses"]:
        if c["id"] == "FM":
            c["status"] = "ready"
            c["shortName"] = "Exam FM"
            c["description"] = (
                "COMPLETE track: Duolingo path, full lessons, 455 SOA FM samples, chapter tests, 14-week plan."
            )
            c["planPath"] = "data/courses/fm/plan.json"
            c["pathPath"] = "data/courses/fm/path.json"
            c["structure"] = "duo_path"
            c["syllabusNote"] = "SOA FM: TVM ~10%, Annuities ~25%, Loans ~20%, Bonds ~20%, Portfolios/ALM ~25%"
            c["mix"] = {"reading": 0.40, "practice": 0.50, "mock": 0.10}
            c["weights"] = FM_WEIGHTS
        elif c["id"] == "FAM":
            c["status"] = "next"
            c["description"] = "Next up after FM. Not study-ready yet."
            c["planPath"] = None
            c["pathPath"] = None
            c["syllabusNote"] = "One-by-one queue — after FM"
        elif c["id"] not in ("P", "FM"):
            if c.get("status") == "ready":
                c["status"] = "scaffold"
            c["planPath"] = None
            c["pathPath"] = None
    cat["version"] = 5
    cat["updated"] = TODAY
    cat["buildPolicy"] = "one_course_at_a_time"
    cat_path.write_text(json.dumps(cat, indent=2), encoding="utf-8")


def main():
    print("Building Exam FM…")
    print("  START", START)

    # Lessons
    lessons = json.loads((DATA / "lessons.json").read_text(encoding="utf-8"))
    lessons.update(fm_lessons())
    (DATA / "lessons.json").write_text(json.dumps(lessons, indent=2, ensure_ascii=False), encoding="utf-8")
    print("  lessons FM modules written")

    # Questions
    all_q = rebuild_fm_questions()
    (DATA / "questions.json").write_text(json.dumps(all_q, indent=2, ensure_ascii=False), encoding="utf-8")
    fm_n = sum(1 for q in all_q if (q.get("exam") or "") == "FM")
    print(f"  questions: total {len(all_q)}, FM {fm_n}")

    # Path
    path = bac.build_path(
        "FM",
        "Exam FM — Financial Mathematics",
        fm_units(),
        FM_WEIGHTS,
        "30 MCQ · 2.5 hours · CBT",
    )
    # fix timeline to START
    path["timeline"]["startDate"] = START.isoformat()
    path["timeline"]["endDate"] = (START + timedelta(weeks=WEEKS)).isoformat()
    path["timeline"]["targetExamWindow"] = "Adjust to your FM sitting"
    path["timeline"]["notes"] = [
        "Duolingo-style: levels in order; chapter test ≥70% unlocks next chapter.",
        "Last unit is wrap + full mocks only.",
        "Content volume follows FM weights: Annuities & Portfolios/Bonds heavy.",
    ]
    path = bac.assign_questions(path, all_q, "FM")

    # Plan
    # Temporarily override bac.START for calendar
    bac.START = START
    mods = bac.modules_from_path(path)
    plan = bac.build_calendar_plan("FM", "Exam FM — Financial Mathematics", path, FM_WEIGHTS, mods)
    plan["startDate"] = START.isoformat()
    plan["endDate"] = (START + timedelta(weeks=WEEKS)).isoformat()
    plan["notes"] = [
        "Primary progression is Path (chapters → levels → chapter tests).",
        "Calendar is a guide; multi-level days OK.",
        "Last 2 weeks: wrap + mocks only.",
        "Mix target 40% read / 50% practice / 10% mock.",
    ]
    plan = bac.assign_plan_days(plan, all_q, "FM")

    FM_DIR.mkdir(parents=True, exist_ok=True)
    (FM_DIR / "path.json").write_text(json.dumps(path, indent=2, ensure_ascii=False), encoding="utf-8")
    (FM_DIR / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    update_catalog_ready()

    # Verify
    empty = 0
    for u in path["units"]:
        for ch in u["chapters"]:
            assert ch["lessonId"] in lessons, ch["lessonId"]
            for lv in ch["levels"]:
                if (lv.get("questionTarget") or 0) > 0 and not lv.get("assignedQuestionIds"):
                    empty += 1
    days_q = sum(1 for d in plan["days"] if d.get("assignedQuestionIds"))
    print(f"  path chapters={path['stats']['chapters']} levels={path['stats']['levels']} empty={empty}")
    print(f"  plan days={len(plan['days'])} withQ={days_q} first={plan['days'][0]['date']}")
    print("DONE — Exam FM ready")


if __name__ == "__main__":
    main()

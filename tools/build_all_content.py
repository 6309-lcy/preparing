"""
Finish ALL course content and wire it into app data files.

Produces:
  - app/data/questions.json          (P + FM SOA samples, tagged)
  - app/data/lessons.json            (P + FM + FAM + SRM + PA + ST + LT)
  - app/data/courses.json            (catalog)
  - app/data/courses/{id}/path.json  (Duolingo path per course)
  - app/data/courses/{id}/plan.json  (calendar plan)
  - app/data/curriculum.json         (active P plan mirror)

Run: python tools/build_all_content.py
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
COURSES = DATA / "courses"
sys.path.insert(0, str(ROOT / "tools"))

# Reuse Exam P path builder
import build_courses as pbuild  # noqa: E402

TODAY = date.today().isoformat()
START = date.today()


# ---------------------------------------------------------------------------
# FM topic tagging
# ---------------------------------------------------------------------------
FM_RULES = [
    ("tvm", r"\b(force of interest|nominal|effective|discount rate|accumulat|present value|compound|simple interest|convertible|i\^|δ)\b", "FM1", "tvm"),
    ("annuities", r"\b(annuit|ä|a¨|level payment|payment of|perpetuit|due|immediate|payable m|continuous annuity)\b", "FM2", "annuities"),
    ("loans", r"\b(loan|amortiz|outstanding balance|sinking fund|repay|principal|borrower)\b", "FM3", "loans"),
    ("bonds", r"\b(bond|redemption|coupon|par value|face amount|yield rate|premium|discount bond|callable)\b", "FM4", "bonds"),
    ("portfolios", r"\b(duration|convexity|immuniz|Macaulay|modified duration|Redington|portfolio|interest rate risk|swap)\b", "FM5", "portfolios"),
]


def tag_fm(q: dict) -> dict:
    text = (q.get("stem") or "") + " " + " ".join((q.get("choices") or {}).values())
    tags, los, clusters = [], set(), set()
    for name, pat, lo, cluster in FM_RULES:
        if re.search(pat, text, re.I):
            tags.append(name)
            los.add(lo)
            clusters.add(cluster)
    if not tags:
        tags = ["tvm"]
        los.add("FM1")
        clusters.add("tvm")
    q["topics"] = tags
    q["lo"] = sorted(los)[0]
    q["cluster"] = sorted(clusters)[0]
    q["exam"] = "FM"
    return q


def improve_p_tag(q: dict) -> dict:
    """Light retag to recover joint/multivariate where stem is clear."""
    text = (q.get("stem") or "") + " " + " ".join((q.get("choices") or {}).values())
    topics = list(q.get("topics") or [])
    if re.search(r"\b(joint|marginal|covariance|correlation|bivariate)\b", text, re.I):
        if "joint" not in topics:
            topics.append("joint")
        q["cluster"] = "multivariate"
    if re.search(r"\b(order statistic|largest|smallest|maximum of n|minimum of n)\b", text, re.I):
        if "order_stats" not in topics:
            topics.append("order_stats")
        q["cluster"] = "multivariate"
    if re.search(r"\b(central limit|sample mean of|approximately normal)\b", text, re.I):
        if "clt" not in topics:
            topics.append("clt")
        q["cluster"] = "multivariate"
    if topics:
        q["topics"] = topics
    q["exam"] = "P"
    return q


def build_fm_questions() -> list[dict]:
    raw_q = json.loads((DATA / "questions_raw_fm.json").read_text(encoding="utf-8"))
    raw_a = json.loads((DATA / "answers_raw_fm.json").read_text(encoding="utf-8"))
    out = []
    for q in raw_q:
        n = str(q.get("number") or "")
        item = {
            "id": q.get("id") or f"FM-SOA-{n}",
            "number": int(n) if str(n).isdigit() else q.get("number"),
            "exam": "FM",
            "stem": q.get("stem") or "",
            "stemRaw": q.get("stem") or "",
            "choices": q.get("choices") or {},
            "answer": raw_a.get(n) or q.get("answer"),
            "source": q.get("source") or "SOA Exam FM Sample Questions",
            "quality": "sample",
            "qualityNotes": [],
            "images": [],
            "displayMode": "text",
        }
        if not item["answer"]:
            continue
        out.append(tag_fm(item))
    return out


def load_p_questions() -> list[dict]:
    qs = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    # If already mixed, keep only P then rebuild
    p_only = [q for q in qs if (q.get("exam") or "P") == "P"]
    if not p_only:
        p_only = qs
    return [improve_p_tag(deepcopy(q)) for q in p_only]


# ---------------------------------------------------------------------------
# Lesson content factory
# ---------------------------------------------------------------------------

def L(lesson_id, title, minutes, lo, sections):
    return {
        "id": lesson_id,
        "title": title,
        "minutes": minutes,
        "lo": lo if isinstance(lo, list) else [lo],
        "sections": sections,
    }


def concept(sid, title, body):
    return {"id": sid, "type": "concept", "title": title, "body": body}


def example(sid, title, setup, solution, why):
    return {
        "id": sid,
        "type": "example",
        "title": title,
        "setup": setup,
        "solution": solution,
        "why": why,
    }


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


def build_all_lessons(existing_p: dict) -> dict:
    """Keep P lessons; add full FM/FAM/SRM/PA/ST/LT modules."""
    lessons = deepcopy(existing_p)

    # ---- FM ----
    fm = [
        L(
            "fm_setup",
            "Exam FM orientation & calculator habits",
            25,
            ["FM"],
            [
                concept(
                    "s1",
                    "What FM tests",
                    "Exam FM (Financial Mathematics) is a 2.5-hour, 30-question CBT.\n\n"
                    "Syllabus weights (approx midpoints):\n"
                    "• Time value of money ~10%\n"
                    "• Annuities ~25%\n"
                    "• Loans ~20%\n"
                    "• Bonds ~20%\n"
                    "• General cash flows / portfolios / duration ~25%\n\n"
                    "You need speed with i, v, d, δ, annuity symbols, amortization, bond pricing, and duration/immunization.",
                ),
                concept(
                    "s2",
                    "Study rhythm",
                    "Same Duolingo path as Exam P: Learn → Practice → Drill → Chapter test.\n"
                    "Last two weeks: wrap + full mocks only. Financial calculator fluency is non-negotiable.",
                ),
                check(
                    "s3",
                    "Weight check",
                    "Which block is usually the largest combined share on FM?",
                    {
                        "A": "Only TVM formulas",
                        "B": "Annuities + loans + bonds together",
                        "C": "Only swaps",
                        "D": "Only continuous force of interest",
                    },
                    "B",
                    "Most exam mass sits in annuities, loans, and bonds — not pure theory of i.",
                ),
            ],
        ),
        L(
            "fm_tvm_core",
            "Interest measures: i, v, d, δ",
            40,
            ["FM1"],
            [
                concept(
                    "s1",
                    "Core symbols",
                    "Effective annual rate i: growth factor (1+i) per year.\n"
                    "Discount factor v = 1/(1+i).\n"
                    "Discount rate d = i/(1+i) = 1−v.\n"
                    "Force of interest δ = ln(1+i) when constant; a(t)=e^{δt}.\n"
                    "Nominal rates i^{(m)}, d^{(m)} convert via (1+i)=(1+i^{(m)}/m)^m.",
                ),
                example(
                    "s2",
                    "Force from effective",
                    "i = 0.05 effective annual. Find δ.",
                    "δ = ln(1.05) ≈ 0.04879.",
                    "Force is the continuous intensity that matches the same annual growth.",
                ),
                check(
                    "s3",
                    "Identity",
                    "Which identity is always true?",
                    {"A": "d = i(1+i)", "B": "v = 1−d", "C": "δ = i/(1+i)", "D": "i = d/(1−d) is false"},
                    "B",
                    "v=1/(1+i) and d=i/(1+i) ⇒ v=1−d. Also i=d/(1−d).",
                ),
            ],
        ),
        L(
            "fm_accum",
            "Accumulation & present value of single payments",
            35,
            ["FM1"],
            [
                concept(
                    "s1",
                    "Moving money in time",
                    "Future value: FV = PV · (1+i)^n  (or e^{δn}).\n"
                    "Present value: PV = FV · v^n.\n"
                    "Be careful with payment timing (beginning vs end of period) and nominal conversion periods.",
                ),
                example(
                    "s2",
                    "Semiannual nominal",
                    "100 grows for 7.25 years at 4% convertible semiannually. Find accumulated value.",
                    "i^{(2)}=0.04 ⇒ j=0.02 per half-year. Periods = 7.25×2 = 14.5.\n"
                    "AV = 100(1.02)^{14.5}.",
                    "Convert nominal → period rate first; never apply 4% as an effective annual by accident.",
                ),
                check(
                    "s3",
                    "PV factor",
                    "At effective i, the PV of 1 due in n years is:",
                    {"A": "(1+i)^n", "B": "v^n", "C": "d^n", "D": "δ^n"},
                    "B",
                    "Discount with v^n = (1+i)^{-n}.",
                ),
            ],
        ),
        L(
            "fm_ann_level",
            "Level annuities-immediate & due",
            45,
            ["FM2"],
            [
                concept(
                    "s1",
                    "Standard symbols",
                    "Annuity-immediate ä with n payments of 1 at end of each year:\n"
                    "a-angle-n = (1−v^n)/i.\n"
                    "Annuity-due (payments at beginning):\n"
                    "ä-angle-n = (1−v^n)/d = (1+i) a-angle-n.\n"
                    "Perpetuity-immediate: 1/i; due: 1/d.",
                ),
                example(
                    "s2",
                    "PV of payments",
                    "Level 500 at end of each year for 10 years, i=6%. PV?",
                    "PV = 500 · a-angle-10 at 6% = 500(1−1.06^{-10})/0.06.",
                    "Factor out the payment level; use the correct immediate vs due form.",
                ),
                check(
                    "s3",
                    "Due vs immediate",
                    "ä-angle-n equals:",
                    {"A": "a-angle-n / (1+i)", "B": "(1+i) a-angle-n", "C": "a-angle-n − 1", "D": "i · a-angle-n"},
                    "B",
                    "Due payments are each one period earlier ⇒ multiply immediate PV by (1+i).",
                ),
            ],
        ),
        L(
            "fm_ann_mthly",
            "m-thly & continuous annuities",
            40,
            ["FM2"],
            [
                concept(
                    "s1",
                    "Payable m-thly",
                    "a-angle-n^{(m)} uses period rate i^{(m)}/m or standard formula\n"
                    "a-angle-n^{(m)} = (1−v^n)/i^{(m)}.\n"
                    "Continuous: ā-angle-n = (1−v^n)/δ.\n"
                    "Remember: higher payment frequency raises PV for the same annual rate of payment.",
                ),
                check(
                    "s2",
                    "Continuous denom",
                    "Continuous annuity PV of rate 1 for n years uses denominator:",
                    {"A": "i", "B": "d", "C": "δ", "D": "v"},
                    "C",
                    "ā-angle-n = (1−v^n)/δ.",
                ),
            ],
        ),
        L(
            "fm_ann_vary",
            "Increasing / decreasing annuities",
            40,
            ["FM2"],
            [
                concept(
                    "s1",
                    "Arithmetic patterns",
                    "Payments 1,2,...,n (immediate) have PV (Ia)-angle-n = (ä-angle-n − n v^n)/i.\n"
                    "Decreasing n,n−1,...,1: (Da)-angle-n = (n − a-angle-n)/i.\n"
                    "Geometric growth: payments grow at rate g; use adjusted rate j with 1+j=(1+i)/(1+g).",
                ),
                check(
                    "s2",
                    "Geometric idea",
                    "If payments grow at g and interest is i, the PV annuity formula uses an adjusted rate from:",
                    {"A": "i−g only always", "B": "(1+i)/(1+g)−1", "C": "i+g", "D": "δ−g always"},
                    "B",
                    "Standard substitution 1+j=(1+i)/(1+g).",
                ),
            ],
        ),
        L(
            "fm_loans",
            "Loans & amortization",
            45,
            ["FM3"],
            [
                concept(
                    "s1",
                    "Prospective & retrospective",
                    "Loan of L repaid by level payments X for n periods: L = X · a-angle-n.\n"
                    "Outstanding balance after k payments (prospective):\n"
                    "OB_k = X · a-angle-(n−k).\n"
                    "Retrospective: OB_k = L(1+i)^k − X · s-angle-k.\n"
                    "Interest in payment k: i · OB_{k−1}; principal = X − interest.",
                ),
                example(
                    "s2",
                    "Level loan payment",
                    "Loan 10,000, n=5, i=6% annual. Level end-of-year payment?",
                    "X = 10000 / a-angle-5 at 6%.",
                    "Always start from L = X a-angle-n unless stated otherwise.",
                ),
                check(
                    "s3",
                    "Prospective OB",
                    "After k level payments on an n-payment loan, OB equals payment times:",
                    {"A": "a-angle-n", "B": "a-angle-(n−k)", "C": "s-angle-k", "D": "v^k"},
                    "B",
                    "Prospective method: remaining annuity of n−k payments.",
                ),
            ],
        ),
        L(
            "fm_sinking",
            "Sinking funds",
            35,
            ["FM3"],
            [
                concept(
                    "s1",
                    "Interest + sinking deposit",
                    "Borrower pays interest each period on full principal plus deposits into a sinking fund that accumulates to principal at maturity.\n"
                    "Total payment = L·i + L / s-angle-n  (if SF earns same i).\n"
                    "If SF rate differs, use that rate in s-angle-n only.",
                ),
                check(
                    "s2",
                    "SF deposit",
                    "To accumulate L in n periods at rate j in a sinking fund, level deposit is:",
                    {"A": "L / a-angle-n", "B": "L / s-angle-n at j", "C": "L·j", "D": "L·v^n"},
                    "B",
                    "Future-value annuity s-angle-n accumulates deposits to L.",
                ),
            ],
        ),
        L(
            "fm_bonds",
            "Bond price, premium, discount",
            45,
            ["FM4"],
            [
                concept(
                    "s1",
                    "Price formula",
                    "Bond with face F, redemption C, coupon rate r (coupon Fr per year, or Fr/m m-thly), yield rate i:\n"
                    "Price P = Fr · a-angle-n + C v^n  (adjust for m-thly).\n"
                    "If P>C: premium; P<C: discount.\n"
                    "Book value follows amortization of premium/discount.",
                ),
                example(
                    "s2",
                    "Par bond",
                    "If coupon rate equals yield and C=F, price is par.",
                    "P = F — coupons exactly compensate required yield.",
                    "Par is the special case r=i (with matching payment frequency).",
                ),
                check(
                    "s3",
                    "Premium",
                    "A bond sells at a premium when:",
                    {"A": "Price < redemption", "B": "Price > redemption", "C": "Coupon rate is zero", "D": "n=1 always"},
                    "B",
                    "Premium means market price above redemption amount.",
                ),
            ],
        ),
        L(
            "fm_duration",
            "Duration, convexity, immunization",
            45,
            ["FM5"],
            [
                concept(
                    "s1",
                    "Macaulay & modified",
                    "Macaulay duration MacD = weighted average payment time using PV weights.\n"
                    "Modified duration ModD = MacD / (1+i)  (for effective i per period).\n"
                    "Relative price change ≈ −ModD · Δi.\n"
                    "Redington immunization: PV assets = PV liabilities, ModD match, convexity assets ≥ liabilities.",
                ),
                check(
                    "s2",
                    "Price sensitivity",
                    "If yields rise slightly, bond prices:",
                    {"A": "Rise by about ModD·Δi", "B": "Fall by about ModD·Δi", "C": "Do not change", "D": "Double"},
                    "B",
                    "dP/P ≈ −ModD·Δi.",
                ),
            ],
        ),
        L(
            "fm_final",
            "FM wrap-up checklist",
            30,
            ["FM"],
            [
                concept(
                    "s1",
                    "Formula gate",
                    "Before mocks, recite cold:\n"
                    "• v,d,δ conversions\n"
                    "• a, ä, s, s̈, (Ia), (Da)\n"
                    "• Loan OB prospective/retrospective\n"
                    "• Bond price + book value\n"
                    "• MacD / ModD / Redington conditions",
                ),
                check(
                    "s2",
                    "Ready?",
                    "Last two weeks of the path should emphasize:",
                    {"A": "Brand new theory only", "B": "Mixed timed sets + full mocks", "C": "Only reading Finan once", "D": "Skipping bonds"},
                    "B",
                    "Wrap unit is mock-heavy by design.",
                ),
            ],
        ),
    ]

    # ---- FAM ----
    fam = [
        L(
            "fam_setup",
            "Exam FAM map (short-term + long-term)",
            25,
            ["FAM"],
            [
                concept(
                    "s1",
                    "Two halves",
                    "FAM blends short-term actuarial math (severity severity/frequency, credibility, ratemaking/reserving themes) "
                    "with long-term life contingencies (survival models, insurance/annuities, reserves).\n"
                    "Treat it as two mini-courses with shared exam discipline.",
                ),
                check(
                    "s2",
                    "Structure",
                    "FAM content is best studied as:",
                    {"A": "Only calculus", "B": "Short-term + long-term tracks", "C": "Only FM formulas", "D": "Only Python"},
                    "B",
                    "Official FAM spans ST and LT foundations.",
                ),
            ],
        ),
        L(
            "fam_st_severity",
            "Short-term: severity, frequency, aggregate",
            40,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Building blocks",
                    "Severity: distribution of loss size (given a loss).\n"
                    "Frequency: distribution of claim count N.\n"
                    "Aggregate S = X1+...+XN (collective risk).\n"
                    "Key: E[S]=E[N]E[X], Var(S)=E[N]Var(X)+Var(N)(E[X])^2 for independent identical Xi ⊥ N.",
                ),
                check(
                    "s2",
                    "Mean aggregate",
                    "If N and X independent, E[S] equals:",
                    {"A": "E[N]+E[X]", "B": "E[N]E[X]", "C": "Var(N)E[X]", "D": "E[N]/E[X]"},
                    "B",
                    "Wald identity for random sums.",
                ),
            ],
        ),
        L(
            "fam_st_mod",
            "Short-term: modifications & risk measures",
            40,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Policy mods",
                    "Ordinary deductible, policy limit, coinsurance change the payment Y vs ground-up loss X.\n"
                    "You already saw this on Exam P — FAM reuses it in pricing context.\n"
                    "Risk measures (e.g. VaR, TVaR) appear at intro level depending on current syllabus wording.",
                ),
                check(
                    "s2",
                    "Deductible payment",
                    "With ordinary deductible d, insurer payment per loss is:",
                    {"A": "min(X,d)", "B": "max(X−d,0)", "C": "X+d", "D": "X/d"},
                    "B",
                    "Ordinary deductible pays the excess over d.",
                ),
            ],
        ),
        L(
            "fam_st_cred",
            "Credibility & experience rating intro",
            35,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Limited fluctuation & Bühlmann ideas",
                    "Credibility blends data with prior/manual rate.\n"
                    "Limited fluctuation (classical) sets n so P(|X̄−μ|<kμ)≥p.\n"
                    "Bühlmann: Z = n/(n+K), K=EVPV/VHM.\n"
                    "Estimate = Z·X̄ + (1−Z)·prior.",
                ),
                check(
                    "s2",
                    "Bühlmann Z",
                    "As n → ∞, Bühlmann Z approaches:",
                    {"A": "0", "B": "1", "C": "K", "D": "0.5"},
                    "B",
                    "More data ⇒ full credibility on the sample.",
                ),
            ],
        ),
        L(
            "fam_lt_surv",
            "Long-term: survival models & life tables",
            40,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Time-until-death",
                    "T_x = future lifetime of (x).\n"
                    "Survival function s(x), force μ_x, curtate K_x.\n"
                    "Standard probabilities: _t p_x, _t q_x, _t|u q_x.\n"
                    "Life table: l_x, d_x, L_x, T_x (table), e_x.",
                ),
                check(
                    "s2",
                    "Notation",
                    "_t p_x is the probability that (x):",
                    {"A": "Dies within t years", "B": "Survives t years", "C": "Is exactly age t", "D": "Buys insurance"},
                    "B",
                    "p is survival; q is death.",
                ),
            ],
        ),
        L(
            "fam_lt_ins",
            "Insurance & annuities (discrete/continuous intro)",
            45,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Actuarial PV",
                    "Whole life insurance Ā_x / A_x: PV of 1 on death.\n"
                    "Term, pure endowment, endowment insurance variants.\n"
                    "Life annuities ä_x, a_x pay while alive.\n"
                    "Relationships: A_x = 1 − d ä_x (discrete whole life under constant i).",
                ),
                check(
                    "s2",
                    "Insurance vs annuity",
                    "A_x = 1 − d ä_x links:",
                    {"A": "Loan balance to coupon", "B": "Whole life insurance to life annuity-due", "C": "Bond price to duration", "D": "Poisson to gamma"},
                    "B",
                    "Classic identity under level effective rate.",
                ),
            ],
        ),
        L(
            "fam_lt_res",
            "Reserves intro",
            35,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Net premium reserve",
                    "Prospective reserve: EPV future benefits − EPV future net premiums.\n"
                    "Retrospective: accumulated past premiums − accumulated past benefits.\n"
                    "At issue, reserve is 0 under equivalence principle.",
                ),
                check(
                    "s2",
                    "Prospective idea",
                    "Net premium reserve is primarily:",
                    {
                        "A": "Cash under the mattress",
                        "B": "EPV future benefits minus EPV future premiums",
                        "C": "Only company profit",
                        "D": "Only expenses",
                    },
                    "B",
                    "Prospective formula is the main definition.",
                ),
            ],
        ),
        L(
            "fam_final",
            "FAM wrap-up",
            25,
            ["FAM"],
            [
                concept(
                    "s1",
                    "Two-track review",
                    "Split mocks: ST day (severity/credibility) and LT day (life contingencies/reserves), then mixed.",
                ),
                check(
                    "s2",
                    "Mix",
                    "A good FAM wrap week includes:",
                    {"A": "Only ST", "B": "Only LT", "C": "Both ST and LT timed mixes", "D": "Neither"},
                    "C",
                    "The exam mixes both domains.",
                ),
            ],
        ),
    ]

    # ---- SRM ----
    srm = [
        L(
            "srm_setup",
            "Exam SRM orientation",
            20,
            ["SRM"],
            [
                concept(
                    "s1",
                    "What SRM covers",
                    "Statistics for Risk Modeling: supervised learning, GLMs, time series, PCA/clustering, tree-based models.\n"
                    "You need conceptual fluency + interpretation of model output, not production ML engineering.",
                ),
                check(
                    "s2",
                    "Not the focus",
                    "SRM is least about:",
                    {"A": "GLM interpretation", "B": "Writing Kubernetes configs", "C": "Train/test ideas", "D": "Time series components"},
                    "B",
                    "It is a modeling/statistics exam, not devops.",
                ),
            ],
        ),
        L(
            "srm_learn",
            "Problem framing & learning workflow",
            35,
            ["SRM"],
            [
                concept(
                    "s1",
                    "Train / validation / test",
                    "Split data to estimate generalization.\n"
                    "Bias–variance tradeoff: flexible models can overfit.\n"
                    "Cross-validation estimates out-of-sample error.\n"
                    "Feature engineering and leakage awareness matter.",
                ),
                check(
                    "s2",
                    "Overfitting",
                    "Overfitting typically means:",
                    {"A": "Great train, weak test performance", "B": "Weak train, great test", "C": "No features", "D": "Perfect causality"},
                    "A",
                    "Memorizing training noise fails on new data.",
                ),
            ],
        ),
        L(
            "srm_glm",
            "GLMs for count & severity style responses",
            45,
            ["SRM"],
            [
                concept(
                    "s1",
                    "GLM structure",
                    "Random component (exponential family), linear predictor η=Xβ, link g(μ)=η.\n"
                    "Log link for positive means; logit for probabilities.\n"
                    "Coefficients: for log link, e^{β} is a multiplicative effect.\n"
                    "Offset terms appear with exposure.",
                ),
                check(
                    "s2",
                    "Log link",
                    "With log link, a coefficient β=0.2 roughly multiplies mean by:",
                    {"A": "0.2", "B": "e^{0.2}", "C": "1.2 exactly always", "D": "log(0.2)"},
                    "B",
                    "μ ∝ e^{Xβ}; unit increase multiplies by e^β.",
                ),
            ],
        ),
        L(
            "srm_ts",
            "Time series components & forecasting ideas",
            40,
            ["SRM"],
            [
                concept(
                    "s1",
                    "Trend, seasonality, noise",
                    "Decompose series; stationary vs nonstationary.\n"
                    "AR, MA, ARIMA intuition: lags of series and shocks.\n"
                    "ACF/PACF patterns guide orders (conceptually).\n"
                    "Forecast intervals widen with horizon.",
                ),
                check(
                    "s2",
                    "Stationarity",
                    "A stationary series has roughly stable:",
                    {"A": "Only maximum value", "B": "Mean/variance structure over time", "C": "Sample size", "D": "Software version"},
                    "B",
                    "Classical stationarity assumptions target stable moments/dependence.",
                ),
            ],
        ),
        L(
            "srm_unsup",
            "PCA & clustering",
            35,
            ["SRM"],
            [
                concept(
                    "s1",
                    "Unsupervised tools",
                    "PCA: orthogonal directions of maximum variance; use for dimension reduction.\n"
                    "Clustering (k-means, hierarchical): group similar observations; choose k with care.\n"
                    "Scale features before distance-based methods.",
                ),
                check(
                    "s2",
                    "PCA goal",
                    "First principal component captures:",
                    {"A": "Minimum variance direction", "B": "Maximum variance direction", "C": "Only the target Y", "D": "Time index"},
                    "B",
                    "PC1 maximizes variance among unit linear combinations.",
                ),
            ],
        ),
        L(
            "srm_trees",
            "Trees, bagging, random forests, boosting (concepts)",
            40,
            ["SRM"],
            [
                concept(
                    "s1",
                    "Tree family",
                    "Decision trees partition feature space; easy to overfit if deep.\n"
                    "Bagging/RF: average many trees, reduce variance; RF also randomizes features.\n"
                    "Boosting: sequential focus on residuals/errors; strong predictive performance, less interpretable.",
                ),
                check(
                    "s2",
                    "RF idea",
                    "Random forests mainly reduce error by:",
                    {"A": "Deleting all features", "B": "Averaging many de-correlated trees", "C": "Using only linear regression", "D": "Ignoring bootstrap"},
                    "B",
                    "Ensemble averaging + feature randomness.",
                ),
            ],
        ),
        L(
            "srm_final",
            "SRM wrap-up",
            25,
            ["SRM"],
            [
                concept("s1", "Interpretation first", "On exam day, read the stem for the modeling goal, metric, and pitfall (leakage, imbalance, overfitting)."),
                check(
                    "s2",
                    "Priority",
                    "When a stem gives GLM coefficients with log link, first translate to:",
                    {"A": "Kubernetes YAML", "B": "Multiplicative effects on the mean", "C": "Bond duration", "D": "Life table l_x"},
                    "B",
                    "Interpretation is the SRM skill.",
                ),
            ],
        ),
    ]

    # ---- PA ----
    pa = [
        L(
            "pa_setup",
            "Exam PA workflow",
            25,
            ["PA"],
            [
                concept(
                    "s1",
                    "Project mindset",
                    "Predictive Analytics is a structured written/project-style assessment:\n"
                    "problem statement → data/EDA → modeling → communication.\n"
                    "Grading rewards clear business framing and justified model choices, not only accuracy.",
                ),
                check(
                    "s2",
                    "Communication",
                    "PA success requires:",
                    {"A": "Only highest R²", "B": "Clear audience-ready explanation of choices", "C": "No EDA", "D": "Hiding limitations"},
                    "B",
                    "Communication is explicitly weighted.",
                ),
            ],
        ),
        L(
            "pa_problem",
            "Problem statement & success metrics",
            30,
            ["PA"],
            [
                concept(
                    "s1",
                    "Define the decision",
                    "Translate a business ask into a modeling target, population, time frame, and metric (loss, AUC, RMSE, lift).\n"
                    "State constraints: fairness, latency, interpretability, data freshness.",
                ),
                check(
                    "s2",
                    "Metric match",
                    "Class imbalance often makes raw accuracy:",
                    {"A": "Always ideal", "B": "Misleading", "C": "Impossible", "D": "Equal to AUC always"},
                    "B",
                    "Prefer precision/recall/AUC/log-loss as appropriate.",
                ),
            ],
        ),
        L(
            "pa_eda",
            "Data quality & EDA",
            35,
            ["PA"],
            [
                concept(
                    "s1",
                    "Look before you model",
                    "Missingness patterns, outliers, leakage, target leakage from future fields, leakage via IDs.\n"
                    "Plots: distributions, relationships, time drift.\n"
                    "Document cleaning rules so results are reproducible.",
                ),
                check(
                    "s2",
                    "Leakage",
                    "Using a feature only known after the claim is closed is often:",
                    {"A": "Good practice", "B": "Target/data leakage risk", "C": "Required by SOA", "D": "A GLM link"},
                    "B",
                    "Training on future information invents fake performance.",
                ),
            ],
        ),
        L(
            "pa_model",
            "Model selection & validation",
            40,
            ["PA"],
            [
                concept(
                    "s1",
                    "Compare honestly",
                    "Baselines first. Then GLM / trees / others as appropriate.\n"
                    "Validate with proper splits or time-based splits for temporal data.\n"
                    "Tune complexity with CV; report uncertainty and error analysis.",
                ),
                check(
                    "s2",
                    "Baseline",
                    "A simple baseline model is useful because:",
                    {"A": "It wastes time", "B": "It anchors whether complexity is worth it", "C": "SOA forbids it", "D": "It replaces communication"},
                    "B",
                    "Always beat a sane baseline.",
                ),
            ],
        ),
        L(
            "pa_comms",
            "Recommendations & exhibits",
            35,
            ["PA"],
            [
                concept(
                    "s1",
                    "Tell a decision story",
                    "Lead with the recommendation, then evidence.\n"
                    "Limitations, monitoring plan, and next data collection step.\n"
                    "Exhibits should be labeled for a non-ML manager.",
                ),
                check(
                    "s2",
                    "Audience",
                    "PA writeups should primarily serve:",
                    {"A": "Only GPU hardware specs", "B": "A business/actuarial decision maker", "C": "Only code golf", "D": "No recommendations"},
                    "B",
                    "Decision-oriented communication.",
                ),
            ],
        ),
        L(
            "pa_final",
            "PA mock project habits",
            25,
            ["PA"],
            [
                concept("s1", "Timed practice", "Rehearse full project cycles with a clock. Practice past PA-style prompts if available."),
                check(
                    "s2",
                    "Order",
                    "Best default order:",
                    {"A": "Model → ignore data → hope", "B": "Problem → EDA → model → communicate", "C": "Communicate with no data", "D": "Only hyperparameter sweep"},
                    "B",
                    "Matches the PA scoring narrative.",
                ),
            ],
        ),
    ]

    # ---- ST / LT specialty prep ----
    st = [
        L(
            "st_setup",
            "Short-term track map",
            20,
            ["ST"],
            [
                concept(
                    "s1",
                    "After FAM",
                    "Specialty short-term deepens ratemaking, reserving, reinsurance, and portfolio metrics used in P&C practice.\n"
                    "Build on FAM-ST; add professional practice context.",
                ),
                check(
                    "s2",
                    "Focus",
                    "Short-term track is closest to:",
                    {"A": "Life reserves only", "B": "P&C pricing/reserving themes", "C": "Only SRM PCA", "D": "Only FM bonds"},
                    "B",
                    "Property & casualty style problems.",
                ),
            ],
        ),
        L(
            "st_rate",
            "Ratemaking themes",
            40,
            ["ST"],
            [
                concept(
                    "s1",
                    "Premium building blocks",
                    "Pure premium, loss ratio methods, exposure bases, classification relativities, trend and development.\n"
                    "Indicate when to use limited fluctuation credibility on segment rates.",
                ),
                check(
                    "s2",
                    "Exposure",
                    "An exposure base should ideally be proportional to:",
                    {"A": "Marketing spend only", "B": "Expected loss", "C": "Office rent", "D": "Stock price"},
                    "B",
                    "Good exposure tracks risk volume.",
                ),
            ],
        ),
        L(
            "st_reserve",
            "Loss reserving themes",
            40,
            ["ST"],
            [
                concept(
                    "s1",
                    "Triangles & IBNR",
                    "Development triangles, age-to-age factors, chain-ladder intuition.\n"
                    "Case reserves vs IBNR. Tail factors. Diagnostic checks for changes in settlement patterns.",
                ),
                check(
                    "s2",
                    "IBNR",
                    "IBNR broadly covers:",
                    {"A": "Only paid losses", "B": "Incurred but not reported (and related) liabilities", "C": "Only premiums", "D": "Only expenses"},
                    "B",
                    "Reserve for claims not fully known/reported.",
                ),
            ],
        ),
        L(
            "st_reins",
            "Reinsurance basics",
            35,
            ["ST"],
            [
                concept(
                    "s1",
                    "Proportional vs excess",
                    "Quota share, surplus, excess of loss, stop-loss — who pays which layer.\n"
                    "Effect on net severity/frequency and capital.",
                ),
                check(
                    "s2",
                    "XOL idea",
                    "Excess of loss primarily protects against:",
                    {"A": "Tiny frequency only", "B": "Large individual or aggregate losses above a retention", "C": "Only life mortality", "D": "Interest rates"},
                    "B",
                    "Layers above retention.",
                ),
            ],
        ),
        L(
            "st_final",
            "ST wrap-up",
            20,
            ["ST"],
            [
                concept("s1", "Practice", "Mix ratemaking + reserving caselets; explain net vs gross of reinsurance."),
                check(
                    "s2",
                    "Balance",
                    "A balanced ST week includes:",
                    {"A": "Only reinsurance trivia", "B": "Pricing and reserving drills", "C": "Only FM duration", "D": "Only PA writing"},
                    "B",
                    "Both pillars.",
                ),
            ],
        ),
    ]

    lt = [
        L(
            "lt_setup",
            "Long-term track map",
            20,
            ["LT"],
            [
                concept(
                    "s1",
                    "After FAM",
                    "Long-term specialty deepens multi-state models, product design, profit testing, and reserve/capital themes for life & annuity.",
                ),
                check(
                    "s2",
                    "Core object",
                    "Long-term models center on:",
                    {"A": "Only claim count per day", "B": "Lifetime contingent cash flows", "C": "Only PCA", "D": "Only bond immunization"},
                    "B",
                    "Life-contingent payments over decades.",
                ),
            ],
        ),
        L(
            "lt_multi",
            "Multiple state & decrements intro",
            40,
            ["LT"],
            [
                concept(
                    "s1",
                    "Beyond single life death",
                    "Healthy/disabled/dead states; transition intensities.\n"
                    "Multiple decrement tables; associated single decrement rates.\n"
                    "Careful with timing assumptions.",
                ),
                check(
                    "s2",
                    "Multi-state",
                    "A disability model typically needs:",
                    {"A": "No transitions", "B": "States and transition rates/probabilities", "C": "Only one cash flow at t=0", "D": "Only FM coupons"},
                    "B",
                    "States + transitions drive contingent benefits.",
                ),
            ],
        ),
        L(
            "lt_products",
            "Products & profit testing themes",
            40,
            ["LT"],
            [
                concept(
                    "s1",
                    "Design levers",
                    "Term, whole life, endowments, annuities, riders.\n"
                    "Profit testing: best-estimate assumptions, risk discount rate, surplus emerging.\n"
                    "Sensitivities: mortality, lapse, expense, interest.",
                ),
                check(
                    "s2",
                    "Lapse risk",
                    "Higher lapses can hurt products that:",
                    {"A": "Never pre-fund anything", "B": "Rely on long persistency to recover acquisition costs", "C": "Are pure one-day policies", "D": "Ignore expenses"},
                    "B",
                    "Acquisition cost recovery needs persistency.",
                ),
            ],
        ),
        L(
            "lt_res_cap",
            "Reserves & capital themes",
            35,
            ["LT"],
            [
                concept(
                    "s1",
                    "Valuation mindset",
                    "Net premium vs modified reserves; expense loads.\n"
                    "Regulatory vs economic views (high level).\n"
                    "Connect to FAM reserve basics; add product-level detail.",
                ),
                check(
                    "s2",
                    "Issue reserve",
                    "Under equivalence net premium, issue reserve is typically:",
                    {"A": "Huge positive always", "B": "Zero", "C": "Equal to face amount", "D": "Equal to δ"},
                    "B",
                    "Equivalence sets EPV premiums = EPV benefits at issue.",
                ),
            ],
        ),
        L(
            "lt_final",
            "LT wrap-up",
            20,
            ["LT"],
            [
                concept("s1", "Drill", "Mixed life-contingency calculations + short written interpretation of profit test output."),
                check(
                    "s2",
                    "Balance",
                    "LT wrap should include:",
                    {"A": "Only PCA", "B": "Multi-state + product/reserve drills", "C": "Only FM sinking funds", "D": "Only PA posters"},
                    "B",
                    "Matches the track.",
                ),
            ],
        ),
    ]

    for block in (fm, fam, srm, pa, st, lt):
        for lesson in block:
            lessons[lesson["id"]] = lesson
    return lessons


# ---------------------------------------------------------------------------
# Generic path builder
# ---------------------------------------------------------------------------

def standard_levels(chapter: dict) -> list[dict]:
    cid = chapter["id"]
    topics = chapter["topics"]
    lesson_id = chapter["lessonId"]
    return [
        {
            "id": f"{cid}_l1",
            "index": 1,
            "type": "lesson",
            "title": "Level 1 · Learn",
            "subtitle": "Teach-first lesson",
            "mode": "lesson",
            "lessonId": lesson_id,
            "topics": topics,
            "questionTarget": 0,
            "readPct": 85,
            "practicePct": 10,
            "mockPct": 5,
            "xp": 25,
        },
        {
            "id": f"{cid}_l2",
            "index": 2,
            "type": "practice",
            "title": "Level 2 · Practice",
            "subtitle": "10 questions",
            "mode": "practice",
            "lessonId": lesson_id,
            "topics": topics,
            "questionTarget": 10,
            "readPct": 10,
            "practicePct": 85,
            "mockPct": 5,
            "xp": 30,
        },
        {
            "id": f"{cid}_l3",
            "index": 3,
            "type": "practice",
            "title": "Level 3 · Drill",
            "subtitle": "12 harder / mixed",
            "mode": "practice",
            "lessonId": lesson_id,
            "topics": topics,
            "questionTarget": 12,
            "readPct": 5,
            "practicePct": 85,
            "mockPct": 10,
            "xp": 35,
        },
        {
            "id": f"{cid}_test",
            "index": 4,
            "type": "chapter_test",
            "title": "Chapter test",
            "subtitle": "12Q · pass ≥70%",
            "mode": "chapter_test",
            "lessonId": lesson_id,
            "topics": topics,
            "questionTarget": 12,
            "minutes": 24,
            "passPct": 70,
            "readPct": 0,
            "practicePct": 20,
            "mockPct": 80,
            "xp": 60,
        },
    ]


def short_levels(chapter: dict) -> list[dict]:
    cid = chapter["id"]
    return [
        {
            "id": f"{cid}_l1",
            "index": 1,
            "type": "lesson",
            "title": "Learn",
            "subtitle": chapter["title"],
            "mode": "lesson",
            "lessonId": chapter["lessonId"],
            "topics": chapter["topics"],
            "questionTarget": 0,
            "readPct": 80,
            "practicePct": 15,
            "mockPct": 5,
            "xp": 20,
        },
        {
            "id": f"{cid}_l2",
            "index": 2,
            "type": "practice",
            "title": "Quick check",
            "subtitle": "6 questions",
            "mode": "practice",
            "lessonId": chapter["lessonId"],
            "topics": chapter["topics"],
            "questionTarget": 6,
            "readPct": 10,
            "practicePct": 80,
            "mockPct": 10,
            "xp": 25,
            "passPct": 0,
        },
    ]


def wrap_levels(chapter: dict, kind: str) -> list[dict]:
    cid = chapter["id"]
    topics = chapter["topics"]
    lid = chapter["lessonId"]
    if kind == "full_mock":
        return [
            {
                "id": f"{cid}_mock",
                "index": 1,
                "type": "full_mock",
                "title": "Full mock exam",
                "subtitle": "Exam mode",
                "mode": "full_mock",
                "lessonId": lid,
                "topics": topics,
                "questionTarget": 30,
                "minutes": 180,
                "passPct": 60,
                "readPct": 0,
                "practicePct": 10,
                "mockPct": 90,
                "xp": 100,
                "useExamMode": True,
            },
            {
                "id": f"{cid}_review",
                "index": 2,
                "type": "practice",
                "title": "Mock review drill",
                "subtitle": "Wrong pool + weak topics",
                "mode": "practice",
                "lessonId": lid,
                "topics": topics,
                "questionTarget": 15,
                "readPct": 20,
                "practicePct": 70,
                "mockPct": 10,
                "xp": 30,
            },
        ]
    return [
        {
            "id": f"{cid}_l1",
            "index": 1,
            "type": "lesson",
            "title": "Formula refresh",
            "subtitle": chapter["title"],
            "mode": "lesson",
            "lessonId": lid,
            "topics": topics,
            "questionTarget": 0,
            "readPct": 50,
            "practicePct": 40,
            "mockPct": 10,
            "xp": 15,
        },
        {
            "id": f"{cid}_l2",
            "index": 2,
            "type": "practice",
            "title": "Mixed drill",
            "subtitle": "15 questions",
            "mode": "practice",
            "lessonId": lid,
            "topics": topics,
            "questionTarget": 15,
            "readPct": 10,
            "practicePct": 80,
            "mockPct": 10,
            "xp": 30,
        },
        {
            "id": f"{cid}_test",
            "index": 3,
            "type": "chapter_test",
            "title": "Chapter test",
            "subtitle": "12Q · pass ≥70%",
            "mode": "chapter_test",
            "lessonId": lid,
            "topics": topics,
            "questionTarget": 12,
            "minutes": 24,
            "passPct": 70,
            "readPct": 5,
            "practicePct": 25,
            "mockPct": 70,
            "xp": 50,
        },
    ]


def build_path(course_id: str, name: str, units_spec: list[dict], weights: dict, exam_format: str) -> dict:
    units_out = []
    flat = []
    order_ch = 0
    for u in units_spec:
        chapters_out = []
        for ch in u["chapters"]:
            order_ch += 1
            kind = ch.get("levels", "standard")
            if kind == "short":
                levels = short_levels(ch)
            elif kind in ("review", "clinic"):
                levels = wrap_levels(ch, "review")
            elif kind == "full_mock":
                levels = wrap_levels(ch, "full_mock")
            else:
                levels = standard_levels(ch)
            for lv in levels:
                lv["unitId"] = u["id"]
                lv["chapterId"] = ch["id"]
                lv["chapterTitle"] = ch["title"]
                lv["chapterNumber"] = ch["number"]
                lv["cluster"] = u.get("cluster", "")
                flat.append(lv["id"])
            chapters_out.append(
                {
                    "id": ch["id"],
                    "number": ch["number"],
                    "order": order_ch,
                    "title": ch["title"],
                    "lessonId": ch["lessonId"],
                    "topics": ch["topics"],
                    "lo": ch.get("lo", []),
                    "icon": ch.get("icon", "book"),
                    "levelCount": len(levels),
                    "hasChapterTest": any(lv["type"] == "chapter_test" for lv in levels),
                    "levels": levels,
                }
            )
        units_out.append(
            {
                "id": u["id"],
                "number": u["number"],
                "title": u["title"],
                "shortTitle": u.get("shortTitle", u["title"]),
                "cluster": u.get("cluster", ""),
                "weight": u.get("weight", 0),
                "weightRange": u.get("weightRange", ""),
                "color": u.get("color", "#0B3D3A"),
                "description": u.get("description", ""),
                "chapterCount": len(chapters_out),
                "chapters": chapters_out,
            }
        )
    total_levels = sum(len(ch["levels"]) for u in units_out for ch in u["chapters"])
    tests = sum(
        1
        for u in units_out
        for ch in u["chapters"]
        for lv in ch["levels"]
        if lv["type"] in ("chapter_test", "full_mock")
    )
    return {
        "courseId": course_id,
        "name": name,
        "structure": "duo_path",
        "version": 3,
        "updated": TODAY,
        "syllabus": {"examFormat": exam_format, "weights": weights},
        "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
        "timeline": {
            "weeks": 14,
            "learnWeeks": 12,
            "startDate": START.isoformat(),
            "endDate": (START + timedelta(weeks=14)).isoformat(),
            "dailyHoursWeekday": 2,
        },
        "stats": {
            "units": len(units_out),
            "chapters": order_ch,
            "levels": total_levels,
            "testsAndMocks": tests,
        },
        "levelOrder": flat,
        "units": units_out,
    }


def assign_questions(path: dict, questions: list[dict], exam: str) -> dict:
    pool = [q for q in questions if q.get("answer") and (q.get("exam") or "P") == exam]
    by_topic: dict[str, list[str]] = defaultdict(list)
    by_cluster: dict[str, list[str]] = defaultdict(list)
    for q in pool:
        by_cluster[q.get("cluster") or ""].append(q["id"])
        for t in q.get("topics") or []:
            by_topic[t].append(q["id"])
    all_ids = [q["id"] for q in pool]
    used: set[str] = set()

    def pick(topics, n, allow_reuse=False):
        if n <= 0:
            return []
        cand = []
        for t in topics or []:
            for qid in by_topic.get(t, []):
                if (allow_reuse or qid not in used) and qid not in cand:
                    cand.append(qid)
        if len(cand) < n:
            for qid in all_ids:
                if (allow_reuse or qid not in used) and qid not in cand:
                    cand.append(qid)
                if len(cand) >= n * 3:
                    break
        # rotate for variety
        chosen = cand[:n]
        if not allow_reuse:
            used.update(chosen)
        # if still short, reuse
        if len(chosen) < n and all_ids:
            i = 0
            while len(chosen) < n:
                qid = all_ids[i % len(all_ids)]
                if qid not in chosen:
                    chosen.append(qid)
                i += 1
                if i > len(all_ids) * 3:
                    break
        return chosen[:n]

    for u in path["units"]:
        for ch in u["chapters"]:
            for lv in ch["levels"]:
                n = int(lv.get("questionTarget") or 0)
                if n <= 0:
                    lv["assignedQuestionIds"] = []
                    continue
                # chapter tests / mocks may reuse for full coverage
                allow = lv["type"] in ("chapter_test", "full_mock") or u.get("cluster") == "wrap"
                lv["assignedQuestionIds"] = pick(lv.get("topics") or ch["topics"], n, allow_reuse=allow)
    return path


def assign_plan_days(plan: dict, questions: list[dict], exam: str) -> dict:
    pool = [q for q in questions if q.get("answer") and (q.get("exam") or "P") == exam]
    by_topic: dict[str, list[str]] = defaultdict(list)
    for q in pool:
        for t in q.get("topics") or []:
            by_topic[t].append(q["id"])
    all_ids = [q["id"] for q in pool]
    cursor = 0

    def pick(topics, n):
        nonlocal cursor
        cand = []
        for t in topics or []:
            for qid in by_topic.get(t, []):
                if qid not in cand:
                    cand.append(qid)
        if len(cand) < n:
            # rotate global pool
            for _ in range(n * 2):
                if not all_ids:
                    break
                qid = all_ids[cursor % len(all_ids)]
                cursor += 1
                if qid not in cand:
                    cand.append(qid)
                if len(cand) >= n:
                    break
        return cand[:n]

    for d in plan.get("days") or []:
        n = int(d.get("questionTarget") or 0)
        d["assignedQuestionIds"] = pick(d.get("topicPrefs") or [], n) if n else []
    return plan


def build_calendar_plan(course_id: str, name: str, path: dict, weights: dict, modules: list[dict]) -> dict:
    """Simple 14-week calendar from ordered content modules."""
    weeks = 14
    learn = 12
    days = []
    day_index = 0
    n_mod = max(1, len(modules))
    for w in range(weeks):
        wrap = w >= learn
        mod = modules[min(int(w * n_mod / learn), n_mod - 1)] if not wrap else {
            "lessonId": modules[-1]["lessonId"] if modules else "final",
            "title": "Wrap / mock focus",
            "topicPrefs": modules[-1]["topics"] if modules else [],
            "cluster": "wrap",
            "chapterId": modules[-1]["id"] if modules else None,
        }
        week_start = START + timedelta(weeks=w)
        monday = week_start - timedelta(days=week_start.weekday())
        for wd in range(7):
            d = monday + timedelta(days=wd)
            if d < START:
                continue
            if wrap:
                if wd == 5:
                    mode, act, title, qt, r, p, m = "full_mock", "mock", "Full mock exam", 30, 0, 20, 80
                elif wd == 6:
                    mode, act, title, qt, r, p, m = "review", "review", "Weakness clinic", 20, 30, 50, 20
                else:
                    mode, act, title, qt, r, p, m = "timed_set", "practice_mock", f"Wrap drill — {mod['title']}", 20, 15, 55, 30
            else:
                if wd <= 3:
                    mode, act, title, qt, r, p, m = "learn", "learn_practice", mod["title"], 18, 45, 50, 5
                elif wd == 4:
                    mode, act, title, qt, r, p, m = "practice", "practice", f"Practice — {mod['title']}", 22, 20, 65, 15
                elif wd == 5:
                    mode, act, title, qt, r, p, m = "weekend_mock", "mock", "Weekend timed set", 15, 10, 40, 50
                else:
                    mode, act, title, qt, r, p, m = "review", "review", "Recall + wrong pool", 12, 35, 55, 10
            days.append(
                {
                    "date": d.isoformat(),
                    "dayIndex": day_index,
                    "weekday": d.strftime("%A"),
                    "week": w + 1,
                    "phase": "wrap" if wrap else mod.get("cluster", "learn"),
                    "title": title,
                    "mode": mode,
                    "activity": act,
                    "isWeekend": wd >= 5,
                    "lessonId": mod.get("lessonId"),
                    "lessonIds": [mod.get("lessonId")] if mod.get("lessonId") else [],
                    "topicPrefs": mod.get("topicPrefs") or mod.get("topics") or [],
                    "questionTarget": qt,
                    "readPct": r,
                    "practicePct": p,
                    "mockPct": m,
                    "requireLesson": act in ("learn_practice", "practice") and not wrap,
                    "fmLight": False,
                    "chapterId": mod.get("chapterId") or mod.get("id"),
                    "assignedQuestionIds": [],
                }
            )
            day_index += 1
    end = START + timedelta(weeks=weeks)
    days = [d for d in days if START <= date.fromisoformat(d["date"]) <= end]
    for i, d in enumerate(days):
        d["dayIndex"] = i
    return {
        "courseId": course_id,
        "name": name,
        "examCode": course_id,
        "startDate": START.isoformat(),
        "endDate": end.isoformat(),
        "weeks": weeks,
        "learnWeeks": learn,
        "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
        "weights": weights,
        "pathPath": f"data/courses/{course_id.lower()}/path.json",
        "targetExamWindow": "Adjust to your sitting",
        "dailyHoursWeekday": 2,
        "notes": [
            "Primary progression is the Path (chapters → levels → chapter tests).",
            "Calendar is a guide; do multiple levels per day if you want.",
            "Last 2 weeks: wrap + mocks only.",
        ],
        "days": days,
        "pathStats": path.get("stats"),
    }


def modules_from_path(path: dict) -> list[dict]:
    mods = []
    for u in path["units"]:
        if u.get("cluster") == "wrap":
            continue
        for ch in u["chapters"]:
            mods.append(
                {
                    "id": ch["id"],
                    "chapterId": ch["id"],
                    "lessonId": ch["lessonId"],
                    "title": ch["title"],
                    "topics": ch["topics"],
                    "topicPrefs": ch["topics"],
                    "cluster": u.get("cluster", ""),
                }
            )
    return mods


# ---------------------------------------------------------------------------
# Course unit specs
# ---------------------------------------------------------------------------

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
            "description": "Interest measures and moving money through time.",
            "chapters": [
                {"id": "fm_ch0", "number": 0, "title": "FM orientation", "lessonId": "fm_setup", "topics": ["tvm"], "levels": "short"},
                {"id": "fm_ch1", "number": 1, "title": "i, v, d, δ", "lessonId": "fm_tvm_core", "topics": ["tvm"]},
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
                {"id": "fm_ch3", "number": 3, "title": "Level annuities", "lessonId": "fm_ann_level", "topics": ["annuities"]},
                {"id": "fm_ch4", "number": 4, "title": "m-thly & continuous", "lessonId": "fm_ann_mthly", "topics": ["annuities"]},
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
            "description": "Amortization and sinking funds.",
            "chapters": [
                {"id": "fm_ch6", "number": 6, "title": "Amortization", "lessonId": "fm_loans", "topics": ["loans"]},
                {"id": "fm_ch7", "number": 7, "title": "Sinking funds", "lessonId": "fm_sinking", "topics": ["loans"]},
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
            "description": "Bond pricing plus duration and immunization.",
            "chapters": [
                {"id": "fm_ch8", "number": 8, "title": "Bond price", "lessonId": "fm_bonds", "topics": ["bonds"]},
                {"id": "fm_ch9", "number": 9, "title": "Duration & immunization", "lessonId": "fm_duration", "topics": ["portfolios", "bonds"]},
            ],
        },
        {
            "id": "fm_u5",
            "number": 5,
            "title": "Wrap-up & Mocks",
            "shortTitle": "Wrap",
            "cluster": "wrap",
            "weight": 0,
            "weightRange": "last 2 weeks",
            "color": "#334155",
            "description": "Mixed review and full mocks.",
            "chapters": [
                {"id": "fm_ch10", "number": 10, "title": "Mixed review", "lessonId": "fm_final", "topics": ["tvm", "annuities", "loans", "bonds", "portfolios"], "levels": "review"},
                {"id": "fm_ch11", "number": 11, "title": "Full mock 1", "lessonId": "fm_final", "topics": ["tvm", "annuities", "loans", "bonds", "portfolios"], "levels": "full_mock"},
                {"id": "fm_ch12", "number": 12, "title": "Full mock 2", "lessonId": "fm_final", "topics": ["tvm", "annuities", "loans", "bonds", "portfolios"], "levels": "full_mock"},
            ],
        },
    ]


def simple_course_units(prefix, clusters):
    """clusters: list of (unit_id, title, short, cluster, weight, color, chapters)
    chapters: list of (num, title, lessonId, topics)
    """
    units = []
    for i, (uid, title, short, cluster, weight, color, chs, desc) in enumerate(clusters, 1):
        chapters = []
        for num, ctitle, lid, topics, *rest in chs:
            kind = rest[0] if rest else "standard"
            chapters.append(
                {
                    "id": f"{prefix}_ch{num}",
                    "number": num,
                    "title": ctitle,
                    "lessonId": lid,
                    "topics": topics,
                    "levels": kind,
                }
            )
        units.append(
            {
                "id": uid,
                "number": i,
                "title": title,
                "shortTitle": short,
                "cluster": cluster,
                "weight": weight,
                "weightRange": f"{int(weight*100)}%" if weight else "wrap",
                "color": color,
                "description": desc,
                "chapters": chapters,
            }
        )
    return units


def fam_units():
    return simple_course_units(
        "fam",
        [
            (
                "fam_u0",
                "Orientation",
                "Intro",
                "intro",
                0.05,
                "#0B3D3A",
                [(0, "FAM map", "fam_setup", ["severity", "survival"], "short")],
                "Course map for ST + LT.",
            ),
            (
                "fam_u1",
                "Short-term foundations",
                "ST",
                "short_term",
                0.45,
                "#0369A1",
                [
                    (1, "Severity & aggregate", "fam_st_severity", ["severity", "frequency"]),
                    (2, "Modifications & risk measures", "fam_st_mod", ["severity", "insurance"]),
                    (3, "Credibility intro", "fam_st_cred", ["credibility"]),
                ],
                "Short-term actuarial math.",
            ),
            (
                "fam_u2",
                "Long-term foundations",
                "LT",
                "long_term",
                0.50,
                "#7C3AED",
                [
                    (4, "Survival models", "fam_lt_surv", ["survival"]),
                    (5, "Insurance & annuities", "fam_lt_ins", ["life_ins"]),
                    (6, "Reserves intro", "fam_lt_res", ["reserves"]),
                ],
                "Life contingencies core.",
            ),
            (
                "fam_u3",
                "Wrap-up",
                "Wrap",
                "wrap",
                0,
                "#334155",
                [
                    (7, "Mixed review", "fam_final", ["severity", "survival", "life_ins"], "review"),
                    (8, "Full mock 1", "fam_final", ["severity", "survival", "life_ins"], "full_mock"),
                    (9, "Full mock 2", "fam_final", ["severity", "survival", "life_ins"], "full_mock"),
                ],
                "Wrap + mocks.",
            ),
        ],
    )


def srm_units():
    return simple_course_units(
        "srm",
        [
            ("srm_u0", "Orientation", "Intro", "intro", 0.05, "#0B3D3A", [(0, "SRM map", "srm_setup", ["learning"], "short")], "SRM overview."),
            (
                "srm_u1",
                "Learning & GLMs",
                "GLM",
                "glm",
                0.55,
                "#0369A1",
                [
                    (1, "Learning workflow", "srm_learn", ["learning"]),
                    (2, "GLMs", "srm_glm", ["glm"]),
                ],
                "Largest modeling block.",
            ),
            (
                "srm_u2",
                "Time series & unsupervised",
                "TS/Unsup",
                "ts",
                0.35,
                "#7C3AED",
                [
                    (3, "Time series", "srm_ts", ["time_series"]),
                    (4, "PCA & clustering", "srm_unsup", ["pca"]),
                    (5, "Trees & ensembles", "srm_trees", ["trees"]),
                ],
                "TS + unsupervised + trees.",
            ),
            (
                "srm_u3",
                "Wrap-up",
                "Wrap",
                "wrap",
                0,
                "#334155",
                [
                    (6, "Mixed review", "srm_final", ["glm", "learning", "time_series"], "review"),
                    (7, "Full mock 1", "srm_final", ["glm", "trees", "pca"], "full_mock"),
                    (8, "Full mock 2", "srm_final", ["glm", "trees", "time_series"], "full_mock"),
                ],
                "Wrap + mocks.",
            ),
        ],
    )


def pa_units():
    return simple_course_units(
        "pa",
        [
            ("pa_u0", "Orientation", "Intro", "intro", 0.1, "#0B3D3A", [(0, "PA workflow", "pa_setup", ["problem"], "short")], "Project exam habits."),
            (
                "pa_u1",
                "Problem & data",
                "Frame",
                "frame",
                0.4,
                "#0369A1",
                [
                    (1, "Problem & metrics", "pa_problem", ["problem"]),
                    (2, "EDA & quality", "pa_eda", ["eda"]),
                ],
                "Frame and explore.",
            ),
            (
                "pa_u2",
                "Model & communicate",
                "Model",
                "model",
                0.5,
                "#7C3AED",
                [
                    (3, "Modeling & validation", "pa_model", ["modeling"]),
                    (4, "Communication", "pa_comms", ["communication"]),
                ],
                "Build and explain.",
            ),
            (
                "pa_u3",
                "Wrap-up",
                "Wrap",
                "wrap",
                0,
                "#334155",
                [
                    (5, "Mock project habits", "pa_final", ["problem", "eda", "modeling", "communication"], "review"),
                    (6, "Timed project 1", "pa_final", ["problem", "modeling", "communication"], "full_mock"),
                    (7, "Timed project 2", "pa_final", ["eda", "modeling", "communication"], "full_mock"),
                ],
                "Timed project practice.",
            ),
        ],
    )


def st_units():
    return simple_course_units(
        "st",
        [
            ("st_u0", "Orientation", "Intro", "intro", 0.1, "#0B3D3A", [(0, "ST map", "st_setup", ["pricing"], "short")], "Short-term track."),
            (
                "st_u1",
                "Pricing & reserving",
                "Core",
                "core",
                0.7,
                "#0369A1",
                [
                    (1, "Ratemaking", "st_rate", ["pricing"]),
                    (2, "Reserving", "st_reserve", ["reserve"]),
                    (3, "Reinsurance", "st_reins", ["reinsurance"]),
                ],
                "P&C core themes.",
            ),
            (
                "st_u2",
                "Wrap-up",
                "Wrap",
                "wrap",
                0,
                "#334155",
                [
                    (4, "Mixed review", "st_final", ["pricing", "reserve", "reinsurance"], "review"),
                    (5, "Mock 1", "st_final", ["pricing", "reserve"], "full_mock"),
                    (6, "Mock 2", "st_final", ["reserve", "reinsurance"], "full_mock"),
                ],
                "Wrap + mocks.",
            ),
        ],
    )


def lt_units():
    return simple_course_units(
        "lt",
        [
            ("lt_u0", "Orientation", "Intro", "intro", 0.1, "#0B3D3A", [(0, "LT map", "lt_setup", ["life_contingencies"], "short")], "Long-term track."),
            (
                "lt_u1",
                "Models & products",
                "Core",
                "core",
                0.7,
                "#7C3AED",
                [
                    (1, "Multi-state & decrements", "lt_multi", ["life_contingencies"]),
                    (2, "Products & profit testing", "lt_products", ["products"]),
                    (3, "Reserves & capital", "lt_res_cap", ["reserves"]),
                ],
                "Life & annuity depth.",
            ),
            (
                "lt_u2",
                "Wrap-up",
                "Wrap",
                "wrap",
                0,
                "#334155",
                [
                    (4, "Mixed review", "lt_final", ["life_contingencies", "products", "reserves"], "review"),
                    (5, "Mock 1", "lt_final", ["life_contingencies", "reserves"], "full_mock"),
                    (6, "Mock 2", "lt_final", ["products", "reserves"], "full_mock"),
                ],
                "Wrap + mocks.",
            ),
        ],
    )


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def catalog_entry(cid, name, short, status, weeks, fmt, weights, desc, syllabus_note):
    low = cid.lower()
    return {
        "id": cid,
        "name": name,
        "shortName": short,
        "status": status,
        "durationWeeks": weeks,
        "examFormat": fmt,
        "weights": weights,
        "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
        "description": desc,
        "planPath": f"data/courses/{low}/plan.json",
        "pathPath": f"data/courses/{low}/path.json",
        "structure": "duo_path",
        "syllabusNote": syllabus_note,
    }


def main():
    print("Loading P questions…")
    p_qs = load_p_questions()
    print(f"  P: {len(p_qs)}")
    print("Building FM questions…")
    fm_qs = build_fm_questions()
    print(f"  FM: {len(fm_qs)}")
    all_qs = p_qs + fm_qs
    write_json(DATA / "questions.json", all_qs)
    print(f"Wrote questions.json ({len(all_qs)})")

    # Lessons
    existing = json.loads((DATA / "lessons.json").read_text(encoding="utf-8"))
    lessons = build_all_lessons(existing)
    write_json(DATA / "lessons.json", lessons)
    print(f"Wrote lessons.json ({len(lessons)} modules)")

    # Exam P path via existing builder + full assign
    print("Building Exam P path/plan…")
    p_path = pbuild.build_path()
    p_path = assign_questions(p_path, all_qs, "P")
    p_plan = pbuild.build_p_plan(p_path)
    p_plan = assign_plan_days(p_plan, all_qs, "P")
    write_json(COURSES / "p" / "path.json", p_path)
    write_json(COURSES / "p" / "plan.json", p_plan)
    write_json(
        DATA / "curriculum.json",
        {
            "courseId": "P",
            "examTarget": p_plan["endDate"],
            "registrationDeadline": "2026-09-30",
            "window": ["2026-11-01", "2026-11-15"],
            "dailyQuestionGoal": 20,
            "mix": p_plan["mix"],
            "weights": p_plan["weights"],
            "planNotes": p_plan["notes"],
            "days": p_plan["days"],
            "pathPath": "data/courses/p/path.json",
        },
    )
    print(f"  P path levels={p_path['stats']['levels']} plan days={len(p_plan['days'])}")

    courses_built = []

    def build_one(cid, name, units, weights, fmt, status, desc, note, exam_for_q):
        path = build_path(cid, name, units, weights, fmt)
        path = assign_questions(path, all_qs, exam_for_q)
        mods = modules_from_path(path)
        plan = build_calendar_plan(cid, name, path, weights, mods)
        plan = assign_plan_days(plan, all_qs, exam_for_q)
        low = cid.lower()
        write_json(COURSES / low / "path.json", path)
        write_json(COURSES / low / "plan.json", plan)
        # count assigned
        n_asg = sum(len(lv.get("assignedQuestionIds") or []) for u in path["units"] for ch in u["chapters"] for lv in ch["levels"])
        d_asg = sum(1 for d in plan["days"] if d.get("assignedQuestionIds"))
        print(f"  {cid}: chapters={path['stats']['chapters']} levels={path['stats']['levels']} pathQ={n_asg} daysWithQ={d_asg}")
        courses_built.append(
            catalog_entry(cid, name, cid if len(cid) <= 3 else name.split("—")[0].strip(), status, 14, fmt, weights, desc, note)
        )

    build_one(
        "FM",
        "Exam FM — Financial Mathematics",
        fm_units(),
        {"tvm": 0.10, "annuities": 0.25, "loans": 0.20, "bonds": 0.20, "portfolios": 0.25},
        "30 MCQ · 2.5 hours · CBT",
        "ready",
        "Full path + SOA sample bank. TVM, annuities, loans, bonds, duration.",
        "SOA FM weights midpoints",
        "FM",
    )
    build_one(
        "FAM",
        "Exam FAM — Fundamentals of Actuarial Mathematics",
        fam_units(),
        {"short_term": 0.45, "long_term": 0.55},
        "CBT multiple choice",
        "ready",
        "Full learn path for ST+LT foundations. Practice draws from related banks when available.",
        "FAM ST+LT structure",
        "P",  # reuse P severity/insurance where topics overlap; lessons are primary
    )
    build_one(
        "SRM",
        "Exam SRM — Statistics for Risk Modeling",
        srm_units(),
        {"learning": 0.20, "glm": 0.35, "time_series": 0.20, "pca_clustering": 0.15, "decision_trees": 0.10},
        "CBT multiple choice",
        "ready",
        "Full concept path: learning, GLMs, TS, PCA, trees. Lesson-first with chapter tests.",
        "SOA SRM objectives",
        "P",
    )
    build_one(
        "PA",
        "Exam PA — Predictive Analytics",
        pa_units(),
        {"problem_statement": 0.15, "data_eda": 0.25, "modeling": 0.35, "communication": 0.25},
        "Project / written CBT-style",
        "ready",
        "Full project workflow path with mock project checkpoints.",
        "PA communication-heavy",
        "P",
    )
    build_one(
        "ST",
        "Short-Term Specialty Track",
        st_units(),
        {"reserve": 0.35, "pricing": 0.35, "reinsurance": 0.15, "other": 0.15},
        "Pathway-dependent",
        "ready",
        "Post-FAM short-term practice themes: rate, reserve, reinsurance.",
        "ST specialty prep",
        "P",
    )
    build_one(
        "LT",
        "Long-Term Specialty Track",
        lt_units(),
        {"life_contingencies": 0.40, "reserves": 0.30, "products": 0.20, "other": 0.10},
        "Pathway-dependent",
        "ready",
        "Post-FAM long-term themes: multi-state, products, reserves.",
        "LT specialty prep",
        "P",
    )

    # P catalog first
    catalog = {
        "version": 3,
        "updated": TODAY,
        "activeDefault": "P",
        "courses": [
            catalog_entry(
                "P",
                "Exam P — Probability",
                "Exam P",
                "ready",
                14,
                "30 MCQ · 3 hours · CBT",
                {"general": 0.27, "univariate": 0.47, "multivariate": 0.26},
                "Full path + 661 SOA samples. Chapters, levels, chapter tests.",
                "SOA 2026: General 23–30%, Univariate 44–50%, Multivariate 23–30%",
            ),
            *courses_built,
        ],
    }
    write_json(DATA / "courses.json", catalog)
    print("Wrote courses.json")
    print("DONE")


if __name__ == "__main__":
    main()

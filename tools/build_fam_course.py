"""
Build Exam FAM as a complete study-ready course (after P and FM).

- Full lessons (short-term + long-term)
- Duolingo path with chapter tests
- 14-week plan from today (40/50/10, last 2 weeks wrap)
- Practice bank: authored FAM drills + remapped P insurance/severity items
- Mark FAM ready; SRM becomes next
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
FAM_DIR = DATA / "courses" / "fam"
sys.path.insert(0, str(ROOT / "tools"))

import build_all_content as bac  # noqa: E402

START = date.today()
WEEKS = 14
TODAY = START.isoformat()

# Approximate midpoints consistent with current FAM (ST + LT combined exam)
FAM_WEIGHTS = {
    "coverages": 0.06,
    "severity_freq": 0.18,
    "estimation": 0.05,
    "credibility": 0.04,
    "survival": 0.15,
    "life_benefits": 0.22,
    "premiums_reserves": 0.20,
    "other": 0.10,
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


def fam_lessons() -> dict:
    return {
        "fam_setup": lesson(
            "fam_setup",
            "Exam FAM orientation (ST + LT)",
            30,
            ["FAM"],
            [
                concept(
                    "s1",
                    "What FAM is",
                    "Exam FAM (Fundamentals of Actuarial Mathematics) is a 3.5-hour CBT with ~34 multiple-choice questions.\n\n"
                    "It blends:\n"
                    "• Short-term: severity/frequency/aggregate, policy mods, intro estimation & credibility\n"
                    "• Long-term: survival models, life insurance & annuities, premiums & reserves\n\n"
                    "Prerequisites: Exam P (probability), FM (financial math), and VEE mathematical statistics ideas.\n"
                    "Tables (life/decrement and distribution inventories) are provided in the exam environment.",
                ),
                concept(
                    "s2",
                    "How this course runs",
                    "Duolingo path: Learn → Practice → Drill → Chapter test (≥70%).\n"
                    "Rough study split follows weights: ST block first, then LT (larger share of exam time for many sittings),\n"
                    "then wrap with mixed mocks. Multi-level days are allowed.",
                ),
                check(
                    "s3",
                    "Structure",
                    "FAM content is best studied as:",
                    {
                        "A": "Only calculus drills",
                        "B": "Short-term models + long-term contingencies",
                        "C": "Only FM bond formulas",
                        "D": "Only Python coding",
                    },
                    "B",
                    "Official FAM spans short-term and long-term foundations.",
                ),
            ],
        ),
        "fam_st_cover": lesson(
            "fam_st_cover",
            "Short-term insurance & reinsurance coverages",
            40,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Coverage language",
                    "Short-term coverages pay benefits over a short policy period (often one year).\n"
                    "Key ideas: ground-up loss vs payment, per-loss vs per-payment, ordinary deductible, franchise,\n"
                    "policy limit, coinsurance, maximum covered loss.\n"
                    "Reinsurance layers (quota share, excess of loss) shift which portion of losses the insurer retains.",
                ),
                example(
                    "s2",
                    "Worked: ordinary deductible payment",
                    "Loss X. Ordinary deductible d. Insurer payment per loss?",
                    "Y = max(X − d, 0)  (also written (X−d)+).\n"
                    "If a policy limit u applies to ground-up, payment is min(max(X−d,0), u−d) depending on wording — read carefully.",
                    "Always define the payment random variable before computing E[Y] or F_Y.",
                ),
                check(
                    "s3",
                    "Ordinary deductible",
                    "With ordinary deductible d, insurer payment per loss is:",
                    {"A": "min(X,d)", "B": "max(X−d,0)", "C": "X+d", "D": "X/d"},
                    "B",
                    "Ordinary deductible pays the excess over d.",
                ),
            ],
        ),
        "fam_st_severity": lesson(
            "fam_st_severity",
            "Severity models",
            50,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Severity building blocks",
                    "Severity = size of loss (given a loss occurs).\n"
                    "Common families: exponential, gamma, Pareto, lognormal, Weibull (use provided tables on exam).\n"
                    "Know mean, variance, limited expected value e(d)=E[X∧d], and mean excess e_X(d)=E[X−d|X>d].\n"
                    "For positive continuous X: E[X] = ∫_0^∞ S(x) dx (when finite).",
                ),
                concept(
                    "s2",
                    "Limited loss & excess",
                    "E[X∧u] is expected payment with limit u (no deductible).\n"
                    "With ordinary deductible d and max payment u−d (limit u ground-up):\n"
                    "E[payment] = E[X∧u] − E[X∧d]  (common identity).\n"
                    "Mean excess for memoryless exponential equals mean — classic trap check.",
                ),
                example(
                    "s3",
                    "Worked: exponential deductible",
                    "X ~ Exp(mean θ=1000). Ordinary deductible 200. E[payment per loss]?",
                    "Memoryless: E[(X−200)+] = E[X]·P(X>200) = 1000 e^{−200/1000} = 1000 e^{−0.2}.",
                    "Exponential memoryless turns excess problems into survival × mean.",
                ),
                check(
                    "s4",
                    "Limited expected value use",
                    "E[X∧u] is most directly the expected:",
                    {
                        "A": "Payment with ordinary deductible u only",
                        "B": "Loss capped at u (policy limit, no deductible)",
                        "C": "Frequency of claims",
                        "D": "Force of interest",
                    },
                    "B",
                    "Limited expected value caps the ground-up loss at u.",
                ),
            ],
        ),
        "fam_st_freq": lesson(
            "fam_st_freq",
            "Frequency & aggregate models",
            50,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Frequency",
                    "N = claim count. Common models: Poisson(λ), binomial(m,q), negative binomial.\n"
                    "Poisson: E[N]=Var(N)=λ.\n"
                    "NB has variance > mean (overdispersion vs Poisson).",
                ),
                concept(
                    "s2",
                    "Aggregate S",
                    "Collective risk: S = X1+···+XN with Xi iid severity, independent of N (usual assumption).\n"
                    "E[S] = E[N] E[X]\n"
                    "Var(S) = E[N] Var(X) + Var(N) (E[X])²\n"
                    "Compound Poisson is especially tractable; (a,b,0) class recursions appear at intro level.",
                ),
                example(
                    "s3",
                    "Worked: mean and variance of S",
                    "N~Poisson(3), X has E[X]=100, Var(X)=400, independent.",
                    "E[S]=3·100=300.\n"
                    "Var(S)=3·400 + 3·100² = 1200 + 30000 = 31200.",
                    "Plug into the compound variance formula; don't forget the Var(N)(EX)² term.",
                ),
                check(
                    "s4",
                    "Aggregate mean",
                    "If N ⊥ X_i iid, E[S] equals:",
                    {"A": "E[N]+E[X]", "B": "E[N]E[X]", "C": "Var(N)E[X]", "D": "E[N]/E[X]"},
                    "B",
                    "Wald identity for random sums.",
                ),
            ],
        ),
        "fam_st_mod": lesson(
            "fam_st_mod",
            "Policy modifications & risk measures",
            45,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Modifications",
                    "Deductible, limit, coinsurance α: payment often α·min(max(X−d,0), u−d).\n"
                    "Per-payment vs per-loss: conditioning on X>d changes the distribution of payment.\n"
                    "Inflation: scale severity, then re-apply mods (order matters).",
                ),
                concept(
                    "s2",
                    "Risk measures (intro)",
                    "VaR_p(X) = F^{-1}(p) (quantile).\n"
                    "TVaR_p(X) = E[X | X > VaR_p] (or integral form of tail expectation).\n"
                    "Know qualitative: TVaR ≥ VaR; coherence properties at a high level.",
                ),
                check(
                    "s3",
                    "Coinsurance",
                    "With coinsurance α∈(0,1) and no other mods, insurer payment is:",
                    {"A": "αX", "B": "X/α", "C": "X−α", "D": "max(X,α)"},
                    "A",
                    "Insurer pays fraction α of the loss (as worded).",
                ),
            ],
        ),
        "fam_st_est": lesson(
            "fam_st_est",
            "Parametric estimation intro",
            40,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "MLE / method of moments ideas",
                    "Fit a parametric severity/frequency by matching sample moments or maximizing likelihood.\n"
                    "For exponential, MLE of mean is sample mean.\n"
                    "Censoring/truncation (policy limits, deductibles) change the likelihood — write the correct contribution per observation.",
                ),
                example(
                    "s2",
                    "Worked: exponential MLE",
                    "Ground-up losses, Exp(θ), complete data x1..xn. Estimate θ=E[X].",
                    "θ̂ = x̄.",
                    "Complete i.i.d. exponential: MLE is the sample mean.",
                ),
                check(
                    "s3",
                    "Data type",
                    "A policy limit typically creates:",
                    {"A": "Left truncation only always", "B": "Right censoring of large losses", "C": "No effect on likelihood", "D": "Force of mortality"},
                    "B",
                    "You observe the limit, not the full ground-up amount.",
                ),
            ],
        ),
        "fam_st_cred": lesson(
            "fam_st_cred",
            "Introduction to credibility",
            45,
            ["FAM-ST"],
            [
                concept(
                    "s1",
                    "Limited fluctuation (classical)",
                    "Choose n so the sample mean is within k of μ with probability p (standard normal approximation).\n"
                    "Full credibility standard n0; partial credibility Z=√(n/n0) (capped at 1) in classical approach.",
                ),
                concept(
                    "s2",
                    "Bühlmann credibility",
                    "Z = n / (n+K), K = EVPV / VHM\n"
                    "(expected process variance / variance of hypothetical means).\n"
                    "Estimate = Z·X̄ + (1−Z)·prior mean (manual/complementary).\n"
                    "As n→∞, Z→1.",
                ),
                example(
                    "s3",
                    "Worked: Bühlmann Z",
                    "n=20, K=30. Find Z.",
                    "Z = 20/(20+30)=0.4.",
                    "More data or smaller K ⇒ higher credibility.",
                ),
                check(
                    "s4",
                    "Bühlmann Z limit",
                    "As n→∞, Bühlmann Z approaches:",
                    {"A": "0", "B": "1", "C": "K", "D": "0.5"},
                    "B",
                    "Full weight on the observed mean.",
                ),
            ],
        ),
        "fam_lt_surv": lesson(
            "fam_lt_surv",
            "Survival models & life tables",
            55,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Lifetime random variables",
                    "T_x = future lifetime of (x).\n"
                    "Survival: _t p_x = P(T_x > t)\n"
                    "Death: _t q_x = 1 − _t p_x\n"
                    "Deferred: _t|u q_x = _t p_x · _u q_{x+t}\n"
                    "Force of mortality μ_{x+t}; relationships with survival function.\n"
                    "Curate K_x = ⌊T_x⌋ for discrete models.",
                ),
                concept(
                    "s2",
                    "Life table functions",
                    "l_x, d_x = l_x − l_{x+1}, q_x = d_x/l_x, p_x = 1−q_x.\n"
                    "e_x = curtate expectation of future lifetime (sum of p's).\n"
                    "Under UDD or constant force, convert between continuous and discrete probabilities.",
                ),
                example(
                    "s3",
                    "Worked: two-year survival",
                    "p_x=0.99, p_{x+1}=0.98. Find _2 p_x.",
                    "_2 p_x = p_x p_{x+1} = 0.99·0.98 = 0.9702.",
                    "Chain single-year survivals for multi-year.",
                ),
                check(
                    "s4",
                    "Notation",
                    "_t p_x is the probability that (x):",
                    {"A": "Dies within t years", "B": "Survives t years", "C": "Is age t exactly", "D": "Buys insurance"},
                    "B",
                    "p is survival; q is death.",
                ),
            ],
        ),
        "fam_lt_ins": lesson(
            "fam_lt_ins",
            "Life insurance benefits (APV)",
            55,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Insurance EPV",
                    "Whole life insurance pays 1 at end of year of death: A_x = Σ v^{k+1} · _k|q_x\n"
                    "Continuous whole life Ā_x integrates v^t · _t p_x μ_{x+t} dt.\n"
                    "Term, pure endowment A_{x:n|}^1 , endowment insurance A_{x:n|}.\n"
                    "Identity (discrete whole life, level i): A_x = 1 − d ä_x.",
                ),
                concept(
                    "s2",
                    "Relations",
                    "Pure endowment: A_{x:n|}^{1|} = v^n · _n p_x\n"
                    "Endowment insurance = term insurance + pure endowment.\n"
                    "Higher interest rate lowers insurance APVs (discount harder).",
                ),
                example(
                    "s3",
                    "Worked: identity",
                    "Given ä_x and d, find A_x for whole life discrete.",
                    "A_x = 1 − d ä_x.",
                    "Memorize this identity cold.",
                ),
                check(
                    "s4",
                    "Insurance vs annuity",
                    "A_x = 1 − d ä_x links:",
                    {
                        "A": "Loan balance to coupon",
                        "B": "Whole life insurance to life annuity-due",
                        "C": "Bond price to duration",
                        "D": "Poisson to gamma",
                    },
                    "B",
                    "Classic discrete whole-life identity.",
                ),
            ],
        ),
        "fam_lt_ann": lesson(
            "fam_lt_ann",
            "Life annuities",
            50,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Annuity EPVs",
                    "Annuity-due ä_x : 1 per year while (x) alive, paid at beginning of year.\n"
                    "Annuity-immediate a_x : payments at end of year.\n"
                    "Temporary ä_{x:n|}, deferred _n|ä_x.\n"
                    "Continuous ā_x.\n"
                    "Relationships: ä_x = 1 + a_x  (under standard discrete timing).",
                ),
                example(
                    "s2",
                    "Worked: temporary due",
                    "Express ä_{x:n|} in terms of pure endowment and whole-life style sums.",
                    "ä_{x:n|} = Σ_{k=0}^{n−1} v^k · _k p_x.",
                    "Finite sum of discounted survival probabilities.",
                ),
                check(
                    "s3",
                    "Due vs immediate",
                    "Under standard annual models, ä_x equals:",
                    {"A": "a_x − 1", "B": "1 + a_x", "C": "A_x", "D": "v a_x"},
                    "B",
                    "Due pays one more certain first payment structure ⇒ 1+a_x.",
                ),
            ],
        ),
        "fam_lt_prem": lesson(
            "fam_lt_prem",
            "Equivalence principle premiums",
            50,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Net premiums",
                    "Equivalence: EPV(premiums) = EPV(benefits) at issue (ignore expenses for net premium).\n"
                    "Whole life level annual due: P_x = A_x / ä_x\n"
                    "Term, endowment have analogous ratios benefit APV / annuity APV.\n"
                    "Gross premiums add expense loading (percent of premium, per policy, per face).",
                ),
                example(
                    "s2",
                    "Worked: whole life P",
                    "Given A_x=0.3, ä_x=12. Find net level premium for benefit 1.",
                    "P = 0.3/12 = 0.025.",
                    "Benefit APV over premium annuity APV.",
                ),
                check(
                    "s3",
                    "Equivalence",
                    "At issue under net equivalence, EPV premiums equal:",
                    {"A": "Face amount", "B": "EPV benefits", "C": "Variance of benefits", "D": "δ only"},
                    "B",
                    "That's the definition of the equivalence principle (net).",
                ),
            ],
        ),
        "fam_lt_res": lesson(
            "fam_lt_res",
            "Reserves (net premium)",
            50,
            ["FAM-LT"],
            [
                concept(
                    "s1",
                    "Prospective reserve",
                    "Net premium reserve at duration t:\n"
                    "  _t V = EPV future benefits − EPV future net premiums\n"
                    "(conditional on survival to t, using select/ultimate as given).\n"
                    "At issue, _0 V = 0 under equivalence.\n"
                    "Retrospective: accumulated past premiums − accumulated past benefits (with interest/survivorship).",
                ),
                concept(
                    "s2",
                    "Whole life formula",
                    "Discrete whole life: _t V_x = A_{x+t} − P_x · ä_{x+t}\n"
                    "with P_x = A_x / ä_x.\n"
                    "Reserves typically increase with duration for level-premium whole life.",
                ),
                example(
                    "s3",
                    "Worked: prospective idea",
                    "After t years, future benefit APV is 0.4, future premium annuity APV is 8, net P=0.03.",
                    "_t V = 0.4 − 0.03·8 = 0.16.",
                    "Prospective: future benefits minus future premiums.",
                ),
                check(
                    "s4",
                    "Issue reserve",
                    "Under equivalence net premium, issue reserve is typically:",
                    {"A": "Huge positive always", "B": "Zero", "C": "Equal to face amount", "D": "Equal to δ"},
                    "B",
                    "EPV premiums = EPV benefits at issue ⇒ reserve 0.",
                ),
            ],
        ),
        "fam_final": lesson(
            "fam_final",
            "FAM wrap-up & mixed strategy",
            35,
            ["FAM"],
            [
                concept(
                    "s1",
                    "Two-track review",
                    "Split practice days: ST (severity/aggregate/credibility) vs LT (A_x, ä_x, P, V).\n"
                    "Then mixed timed sets. Use exam tables in practice if you have them.\n"
                    "Formula sheet: compound variance, Bühlmann Z, A=1−dä, P=A/ä, prospective V.",
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
    }


def fam_units():
    return [
        {
            "id": "fam_u0",
            "number": 1,
            "title": "Orientation",
            "shortTitle": "Intro",
            "cluster": "intro",
            "weight": 0.02,
            "weightRange": "—",
            "color": "#0B3D3A",
            "description": "Exam structure and study rhythm.",
            "chapters": [
                {"id": "fam_ch0", "number": 0, "title": "FAM map", "lessonId": "fam_setup", "topics": ["coverages", "survival"], "levels": "short"},
            ],
        },
        {
            "id": "fam_u1",
            "number": 2,
            "title": "Short-Term Foundations",
            "shortTitle": "ST",
            "cluster": "short_term",
            "weight": 0.40,
            "weightRange": "~40% of path time",
            "color": "#0369A1",
            "description": "Coverages, severity, frequency, aggregate, mods, estimation, credibility.",
            "chapters": [
                {"id": "fam_ch1", "number": 1, "title": "Coverages & reinsurance language", "lessonId": "fam_st_cover", "topics": ["coverages", "insurance"]},
                {"id": "fam_ch2", "number": 2, "title": "Severity models", "lessonId": "fam_st_severity", "topics": ["severity", "insurance", "continuous_rv"]},
                {"id": "fam_ch3", "number": 3, "title": "Frequency & aggregate", "lessonId": "fam_st_freq", "topics": ["frequency", "aggregate", "severity"]},
                {"id": "fam_ch4", "number": 4, "title": "Modifications & risk measures", "lessonId": "fam_st_mod", "topics": ["insurance", "severity", "risk_measure"]},
                {"id": "fam_ch5", "number": 5, "title": "Parametric estimation intro", "lessonId": "fam_st_est", "topics": ["estimation", "severity"]},
                {"id": "fam_ch6", "number": 6, "title": "Credibility", "lessonId": "fam_st_cred", "topics": ["credibility"]},
            ],
        },
        {
            "id": "fam_u2",
            "number": 3,
            "title": "Long-Term Foundations",
            "shortTitle": "LT",
            "cluster": "long_term",
            "weight": 0.50,
            "weightRange": "~50% of path time",
            "color": "#7C3AED",
            "description": "Survival, insurance, annuities, premiums, reserves.",
            "chapters": [
                {"id": "fam_ch7", "number": 7, "title": "Survival models & life tables", "lessonId": "fam_lt_surv", "topics": ["survival"]},
                {"id": "fam_ch8", "number": 8, "title": "Life insurance APVs", "lessonId": "fam_lt_ins", "topics": ["life_ins", "survival"]},
                {"id": "fam_ch9", "number": 9, "title": "Life annuities", "lessonId": "fam_lt_ann", "topics": ["life_ann", "survival"]},
                {"id": "fam_ch10", "number": 10, "title": "Net premiums", "lessonId": "fam_lt_prem", "topics": ["premiums", "life_ins", "life_ann"]},
                {"id": "fam_ch11", "number": 11, "title": "Net premium reserves", "lessonId": "fam_lt_res", "topics": ["reserves", "premiums", "life_ins"]},
            ],
        },
        {
            "id": "fam_u3",
            "number": 4,
            "title": "Wrap-up & Mocks",
            "shortTitle": "Wrap",
            "cluster": "wrap",
            "weight": 0.0,
            "weightRange": "last 2 weeks",
            "color": "#334155",
            "description": "Mixed ST+LT review and full mocks.",
            "chapters": [
                {
                    "id": "fam_ch12",
                    "number": 12,
                    "title": "Mixed review — Short-term",
                    "lessonId": "fam_final",
                    "topics": ["severity", "frequency", "aggregate", "credibility", "insurance"],
                    "levels": "review",
                },
                {
                    "id": "fam_ch13",
                    "number": 13,
                    "title": "Mixed review — Long-term",
                    "lessonId": "fam_final",
                    "topics": ["survival", "life_ins", "life_ann", "premiums", "reserves"],
                    "levels": "review",
                },
                {
                    "id": "fam_ch14",
                    "number": 14,
                    "title": "Full mock 1",
                    "lessonId": "fam_final",
                    "topics": ["severity", "aggregate", "survival", "life_ins", "reserves", "credibility"],
                    "levels": "full_mock",
                },
                {
                    "id": "fam_ch15",
                    "number": 15,
                    "title": "Weakness clinic",
                    "lessonId": "fam_final",
                    "topics": ["insurance", "severity", "life_ins", "reserves", "credibility"],
                    "levels": "clinic",
                },
                {
                    "id": "fam_ch16",
                    "number": 16,
                    "title": "Full mock 2 + final",
                    "lessonId": "fam_final",
                    "topics": ["severity", "aggregate", "survival", "life_ins", "life_ann", "reserves"],
                    "levels": "full_mock",
                },
            ],
        },
    ]


def q(num, stem, choices, answer, topics, cluster, lo="FAM"):
    return {
        "id": f"FAM-DRILL-{num}",
        "number": num,
        "exam": "FAM",
        "stem": stem,
        "stemRaw": stem,
        "choices": choices,
        "answer": answer,
        "lo": lo,
        "topics": topics,
        "cluster": cluster,
        "source": "SOA Grind authored FAM drill (not official SOA sample)",
        "quality": "drill",
        "qualityNotes": ["authored for course practice"],
        "images": [],
        "displayMode": "text",
    }


def build_fam_drill_bank() -> list[dict]:
    """Authored practice items so FAM path is usable without official sample PDF in-repo."""
    items = []
    n = 1

    def add(stem, choices, answer, topics, cluster, lo="FAM"):
        nonlocal n
        items.append(q(n, stem, choices, answer, topics, cluster, lo))
        n += 1

    # --- Severity / insurance ---
    for theta, d in [(1000, 100), (500, 50), (2000, 200)]:
        add(
            f"Losses follow an exponential distribution with mean {theta}. "
            f"An ordinary deductible of {d} is applied per loss. "
            f"Which expression equals the expected insurer payment per loss?",
            {
                "A": f"{theta}",
                "B": f"{theta}*exp(-{d}/{theta})",
                "C": f"{theta}*(1-exp(-{d}/{theta}))",
                "D": f"{d}",
                "E": f"{theta}+{d}",
            },
            "B",
            ["severity", "insurance"],
            "short_term",
        )

    add(
        "For a positive continuous loss random variable X, E[X∧u] denotes:",
        {
            "A": "E[X−u | X>u]",
            "B": "E[min(X,u)]",
            "C": "E[max(X−u,0)]",
            "D": "Var(X)/u",
            "E": "F(u)",
        },
        "B",
        ["severity", "insurance"],
        "short_term",
    )

    add(
        "With ordinary deductible d and no other modifications, the insurer's payment per loss is:",
        {
            "A": "min(X,d)",
            "B": "max(X−d,0)",
            "C": "X+d",
            "D": "X/d",
            "E": "d−X",
        },
        "B",
        ["coverages", "insurance"],
        "short_term",
    )

    # --- Aggregate ---
    add(
        "Let S be a collective risk sum with N claims, i.i.d. severities X independent of N. Then E[S] equals:",
        {
            "A": "E[N]+E[X]",
            "B": "E[N]E[X]",
            "C": "E[N]/E[X]",
            "D": "Var(N)E[X]",
            "E": "E[N^2]E[X]",
        },
        "B",
        ["aggregate", "frequency", "severity"],
        "short_term",
    )

    add(
        "Under the usual independence assumptions, Var(S) for S=X1+···+XN equals:",
        {
            "A": "E[N]Var(X) only",
            "B": "Var(N)Var(X)",
            "C": "E[N]Var(X)+Var(N)(E[X])^2",
            "D": "(E[N]E[X])^2",
            "E": "Var(X)/E[N]",
        },
        "C",
        ["aggregate", "frequency", "severity"],
        "short_term",
    )

    add(
        "N ~ Poisson(λ=4), E[X]=50, Var(X)=100, independent. Var(S) equals:",
        {
            "A": "400",
            "B": "10400",
            "C": "2000",
            "D": "2500",
            "E": "4000",
        },
        "B",
        ["aggregate", "frequency"],
        "short_term",
    )
    # 4*100 + 4*2500 = 400+10000=10400

    # --- Credibility ---
    add(
        "In Bühlmann credibility, Z = n/(n+K). As n increases, Z:",
        {
            "A": "Decreases to 0",
            "B": "Increases toward 1",
            "C": "Stays equal to K",
            "D": "Equals n−K",
            "E": "Becomes negative",
        },
        "B",
        ["credibility"],
        "short_term",
    )

    add(
        "Bühlmann K equals EVPV/VHM. Larger process variance (EVPV), other things equal, makes K:",
        {
            "A": "Smaller and Z larger",
            "B": "Larger and Z smaller",
            "C": "Unchanged",
            "D": "Zero",
            "E": "Equal to n",
        },
        "B",
        ["credibility"],
        "short_term",
    )

    add(
        "n=40, K=60. Bühlmann Z equals:",
        {"A": "0.4", "B": "0.6", "C": "0.67", "D": "1.5", "E": "0.25"},
        "A",
        ["credibility"],
        "short_term",
    )
    # 40/100=0.4

    add(
        "Classical limited-fluctuation partial credibility often uses Z of the form:",
        {
            "A": "n/(n+K) only",
            "B": "min(1, sqrt(n/n_full))",
            "C": "n^2",
            "D": "1/n",
            "E": "K/n",
        },
        "B",
        ["credibility"],
        "short_term",
    )

    # --- Survival ---
    add(
        "The symbol _t p_x denotes the probability that (x):",
        {
            "A": "Dies within t years",
            "B": "Survives at least t years",
            "C": "Dies exactly at time t",
            "D": "Is age t at issue",
            "E": "Pays premium t",
        },
        "B",
        ["survival"],
        "long_term",
    )

    add(
        "Given p_x=0.98 and p_{x+1}=0.97, _2 p_x equals:",
        {"A": "0.01", "B": "0.9506", "C": "0.99", "D": "1.95", "E": "0.03"},
        "B",
        ["survival"],
        "long_term",
    )
    # 0.98*0.97=0.9506

    add(
        "_t q_x equals:",
        {
            "A": "_t p_x",
            "B": "1 − _t p_x",
            "C": "v^t",
            "D": "μ_x",
            "E": "e_x",
        },
        "B",
        ["survival"],
        "long_term",
    )

    add(
        "In a life table, q_x equals:",
        {
            "A": "l_{x+1}/l_x",
            "B": "d_x / l_x",
            "C": "l_x / d_x",
            "D": "e_x",
            "E": "T_x",
        },
        "B",
        ["survival"],
        "long_term",
    )

    # --- Insurance / annuities / premiums / reserves ---
    add(
        "Under standard discrete whole life and level effective interest, A_x equals:",
        {
            "A": "d ä_x",
            "B": "1 − d ä_x",
            "C": "ä_x / d",
            "D": "1 + d ä_x",
            "E": "v ä_x",
        },
        "B",
        ["life_ins", "life_ann"],
        "long_term",
    )

    add(
        "Net level whole-life premium under equivalence (benefit 1, annual due) is:",
        {
            "A": "A_x · ä_x",
            "B": "A_x / ä_x",
            "C": "ä_x / A_x",
            "D": "1 − A_x",
            "E": "d / A_x",
        },
        "B",
        ["premiums", "life_ins"],
        "long_term",
    )

    add(
        "If A_x=0.25 and ä_x=15, the net level whole-life premium P_x is:",
        {"A": "0.0167", "B": "3.75", "C": "0.25", "D": "15.25", "E": "0.04"},
        "A",
        ["premiums", "life_ins"],
        "long_term",
    )
    # 0.25/15 ≈ 0.01667

    add(
        "Prospective net premium reserve equals:",
        {
            "A": "EPV future premiums − EPV future benefits",
            "B": "EPV future benefits − EPV future net premiums",
            "C": "Face amount only",
            "D": "Gross premium only",
            "E": "Var(benefits)",
        },
        "B",
        ["reserves", "premiums"],
        "long_term",
    )

    add(
        "Under net equivalence, the reserve at issue is typically:",
        {"A": "A_x", "B": "0", "C": "1", "D": "ä_x", "E": "P_x"},
        "B",
        ["reserves"],
        "long_term",
    )

    add(
        "A pure endowment of 1 due in n years if (x) survives has APV:",
        {
            "A": "A_x",
            "B": "v^n · _n p_x",
            "C": "_n q_x",
            "D": "ä_x",
            "E": "n v",
        },
        "B",
        ["life_ins", "survival"],
        "long_term",
    )

    add(
        "For standard annual models, ä_x equals:",
        {
            "A": "a_x − 1",
            "B": "1 + a_x",
            "C": "A_x",
            "D": "v a_x",
            "E": "d a_x",
        },
        "B",
        ["life_ann"],
        "long_term",
    )

    # Generate more variants for volume
    for k in range(5):
        add(
            f"Poisson frequency with mean {2+k} and exponential severity with mean {100*(k+1)}, independent. E[S] equals:",
            {
                "A": str((2 + k) + 100 * (k + 1)),
                "B": str((2 + k) * 100 * (k + 1)),
                "C": str((2 + k) * 100 * (k + 1) ** 2),
                "D": str(100 * (k + 1) / (2 + k)),
                "E": str((2 + k) ** 2),
            },
            "B",
            ["aggregate", "frequency", "severity"],
            "short_term",
        )

    for n, K in [(10, 10), (25, 75), (50, 50), (5, 20)]:
        z = n / (n + K)
        # format choices
        add(
            f"Bühlmann credibility with n={n} and K={K}. Z equals:",
            {
                "A": f"{z:.4f}",
                "B": f"{1-z:.4f}",
                "C": f"{K/(n+K):.4f}",
                "D": f"{n+K}",
                "E": f"{n*K}",
            },
            "A",
            ["credibility"],
            "short_term",
        )

    for ax, ad in [(0.2, 14.0), (0.35, 10.0), (0.4, 8.0)]:
        p = ax / ad
        add(
            f"Given A_x={ax} and ä_x={ad}, net level whole life premium equals:",
            {
                "A": f"{p:.4f}",
                "B": f"{ax*ad:.4f}",
                "C": f"{ad/ax:.4f}",
                "D": f"{1-ax:.4f}",
                "E": f"{ax+ad:.4f}",
            },
            "A",
            ["premiums", "life_ins"],
            "long_term",
        )

    for tV_ben, tV_ann, P in [(0.5, 10, 0.03), (0.6, 12, 0.04), (0.35, 9, 0.02)]:
        v = tV_ben - P * tV_ann
        add(
            f"Prospective: EPV future benefits = {tV_ben}, EPV future premium annuity = {tV_ann}, "
            f"net premium P = {P}. Reserve equals:",
            {
                "A": f"{v:.4f}",
                "B": f"{tV_ben + P*tV_ann:.4f}",
                "C": f"{P:.4f}",
                "D": f"{tV_ben:.4f}",
                "E": f"{tV_ann:.4f}",
            },
            "A",
            ["reserves", "premiums"],
            "long_term",
        )

    # Risk measures
    add(
        "VaR at level p for a loss distribution is best described as:",
        {
            "A": "The mean loss",
            "B": "A quantile of the loss distribution",
            "C": "Always equal to TVaR",
            "D": "The mode only",
            "E": "Variance of losses",
        },
        "B",
        ["risk_measure", "severity"],
        "short_term",
    )

    add(
        "TVaR_p is typically:",
        {
            "A": "Less than VaR_p",
            "B": "A tail expectation beyond VaR_p",
            "C": "Equal to the median always",
            "D": "A premium principle unrelated to tails",
            "E": "Always zero",
        },
        "B",
        ["risk_measure"],
        "short_term",
    )

    # Estimation
    add(
        "For i.i.d. complete exponential losses with mean θ, the MLE of θ is:",
        {
            "A": "Sample median",
            "B": "Sample mean",
            "C": "Sample variance",
            "D": "Maximum observation",
            "E": "Minimum observation",
        },
        "B",
        ["estimation", "severity"],
        "short_term",
    )

    add(
        "A policy maximum that caps observed ground-up loss typically induces:",
        {
            "A": "Left truncation",
            "B": "Right censoring",
            "C": "No information loss",
            "D": "Negative losses",
            "E": "Force of interest change",
        },
        "B",
        ["estimation", "coverages"],
        "short_term",
    )

    # More survival / deferred
    add(
        "The deferred mortality probability _t|u q_x equals:",
        {
            "A": "_t p_x · _u q_{x+t}",
            "B": "_t q_x · _u p_x",
            "C": "_t+u q_x only always without p",
            "D": "v^{t+u}",
            "E": "μ_x",
        },
        "A",
        ["survival"],
        "long_term",
    )

    # Fill to ~120+ with systematic variants
    for i, (px, py) in enumerate([(0.99, 0.98), (0.995, 0.99), (0.97, 0.96), (0.9, 0.95)]):
        add(
            f"p_x={px}, p_{{x+1}}={py}. Find _2 p_x.",
            {
                "A": f"{px*py:.6f}",
                "B": f"{px+py:.6f}",
                "C": f"{1-px*py:.6f}",
                "D": f"{px-py:.6f}",
                "E": f"{(px+py)/2:.6f}",
            },
            "A",
            ["survival"],
            "long_term",
        )

    for i, d in enumerate([100, 250, 500, 1000]):
        add(
            f"X continuous positive. E[(X−{d})+] equals which of the following general identities?",
            {
                "A": f"E[X]−E[X∧{d}]",
                "B": f"E[X∧{d}]",
                "C": f"E[X]+{d}",
                "D": f"{d}−E[X]",
                "E": f"Var(X)/{d}",
            },
            "A",
            ["severity", "insurance"],
            "short_term",
        )

    for i, (lam, ex, vx) in enumerate([(2, 10, 20), (5, 100, 50), (3, 40, 60), (10, 5, 5)]):
        var_s = lam * vx + lam * (ex**2)  # Poisson
        add(
            f"N~Poisson({lam}), E[X]={ex}, Var(X)={vx}, independent. Var(S)=",
            {
                "A": str(var_s),
                "B": str(lam * vx),
                "C": str(lam * ex),
                "D": str(vx + ex**2),
                "E": str(lam**2 * vx),
            },
            "A",
            ["aggregate", "frequency"],
            "short_term",
        )

    return items


def remap_p_overlap(all_questions: list[dict]) -> list[dict]:
    """Clone useful P items into FAM bank for severity/insurance drill."""
    out = []
    n = 1
    for q0 in all_questions:
        if (q0.get("exam") or "P") != "P":
            continue
        topics = set(q0.get("topics") or [])
        if not topics.intersection({"insurance", "continuous_rv", "expectation_var", "discrete_rv"}):
            continue
        if not q0.get("answer"):
            continue
        # keep a subset
        if n > 180:
            break
        cq = deepcopy(q0)
        cq["id"] = f"FAM-PBRIDGE-{n}"
        cq["exam"] = "FAM"
        cq["source"] = (cq.get("source") or "SOA P sample") + " [bridged for FAM severity practice]"
        # map topics
        mapped = []
        if "insurance" in topics:
            mapped += ["insurance", "severity", "coverages"]
        if "continuous_rv" in topics or "discrete_rv" in topics:
            mapped += ["severity"]
        if "expectation_var" in topics:
            mapped += ["severity", "aggregate"]
        cq["topics"] = list(dict.fromkeys(mapped)) or ["severity"]
        cq["cluster"] = "short_term"
        cq["displayMode"] = cq.get("displayMode") or ("image" if cq.get("images") else "text")
        out.append(cq)
        n += 1
    return out


def update_catalog():
    cat = json.loads((DATA / "courses.json").read_text(encoding="utf-8"))
    for c in cat["courses"]:
        if c["id"] == "FAM":
            c["status"] = "ready"
            c["shortName"] = "Exam FAM"
            c["durationWeeks"] = 14
            c["examFormat"] = "34 MCQ · 3.5 hours · CBT"
            c["weights"] = {
                "short_term": 0.40,
                "long_term": 0.50,
                "other": 0.10,
            }
            c["mix"] = {"reading": 0.40, "practice": 0.50, "mock": 0.10}
            c["description"] = (
                "COMPLETE track: ST+LT path, full lessons, FAM drill bank + P-bridged severity items, "
                "chapter tests, 14-week plan."
            )
            c["planPath"] = "data/courses/fam/plan.json"
            c["pathPath"] = "data/courses/fam/path.json"
            c["structure"] = "duo_path"
            c["syllabusNote"] = (
                "SOA FAM: short-term models (severity/freq/agg, credibility) + long-term contingencies "
                "(survival, insurance, annuities, premiums, reserves)"
            )
        elif c["id"] == "SRM":
            c["status"] = "next"
            c["description"] = "Next up after FAM. Not study-ready yet."
            c["planPath"] = None
            c["pathPath"] = None
            c["syllabusNote"] = "One-by-one queue — after FAM"
        elif c["id"] not in ("P", "FM", "FAM"):
            c["status"] = "scaffold"
            c["planPath"] = None
            c["pathPath"] = None
    cat["version"] = 6
    cat["updated"] = TODAY
    cat["buildPolicy"] = "one_course_at_a_time"
    (DATA / "courses.json").write_text(json.dumps(cat, indent=2), encoding="utf-8")


def main():
    print("Building Exam FAM…")
    print("  START", START)

    # Lessons
    lessons = json.loads((DATA / "lessons.json").read_text(encoding="utf-8"))
    lessons.update(fam_lessons())
    (DATA / "lessons.json").write_text(json.dumps(lessons, indent=2, ensure_ascii=False), encoding="utf-8")
    print("  lessons written", sum(1 for k in lessons if k.startswith("fam_")))

    # Questions: keep P+FM, replace old FAM, add new bank
    all_q = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    base = [q for q in all_q if (q.get("exam") or "P") in ("P", "FM")]
    drills = build_fam_drill_bank()
    bridged = remap_p_overlap(base)
    fam_q = drills + bridged
    all_q = base + fam_q
    (DATA / "questions.json").write_text(json.dumps(all_q, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  questions total={len(all_q)} FAM={len(fam_q)} (drills={len(drills)} bridged={len(bridged)})")

    # Path + plan
    path = bac.build_path(
        "FAM",
        "Exam FAM — Fundamentals of Actuarial Mathematics",
        fam_units(),
        FAM_WEIGHTS,
        "34 MCQ · 3.5 hours · CBT",
    )
    path["timeline"]["startDate"] = START.isoformat()
    path["timeline"]["endDate"] = (START + timedelta(weeks=WEEKS)).isoformat()
    path["timeline"]["notes"] = [
        "ST units first, then LT (larger conceptual load), then wrap mocks.",
        "Chapter tests require ≥70% to unlock the next chapter.",
        "Practice bank = authored FAM drills + bridged P severity/insurance items (not official FAM samples).",
    ]
    path = bac.assign_questions(path, all_q, "FAM")

    bac.START = START
    mods = bac.modules_from_path(path)
    plan = bac.build_calendar_plan(
        "FAM",
        "Exam FAM — Fundamentals of Actuarial Mathematics",
        path,
        {"short_term": 0.40, "long_term": 0.50, "other": 0.10},
        mods,
    )
    plan["notes"] = [
        "Primary progression is Path.",
        "Multi-level days OK.",
        "Last 2 weeks: wrap + mocks only.",
        "40% reading / 50% practice / 10% mock.",
    ]
    plan = bac.assign_plan_days(plan, all_q, "FAM")

    FAM_DIR.mkdir(parents=True, exist_ok=True)
    (FAM_DIR / "path.json").write_text(json.dumps(path, indent=2, ensure_ascii=False), encoding="utf-8")
    (FAM_DIR / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    update_catalog()

    empty = 0
    for u in path["units"]:
        for ch in u["chapters"]:
            assert ch["lessonId"] in lessons, ch["lessonId"]
            for lv in ch["levels"]:
                if (lv.get("questionTarget") or 0) > 0 and not lv.get("assignedQuestionIds"):
                    empty += 1
    print(f"  path ch={path['stats']['chapters']} lv={path['stats']['levels']} empty={empty}")
    print(f"  plan days={len(plan['days'])} first={plan['days'][0]['date']}")
    print("DONE — Exam FAM ready")


if __name__ == "__main__":
    main()

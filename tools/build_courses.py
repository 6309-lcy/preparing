"""
Build multi-course catalog + Exam P 14-week plan (3.5 months).
40% reading / 50% practice / 10% mock · last 2 weeks wrap-up + mocks.
Syllabus weights (Exam P, current SOA):
  General Probability 23–30%  → use 27%
  Univariate RVs       44–50%  → use 47%
  Multivariate RVs     23–30%  → use 26%
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
DATA.mkdir(parents=True, exist_ok=True)

# Fixed timeline: 14 weeks from start (user can shift via startDate in UI later)
START = date(2026, 8, 1)  # ~3.5 months → mid-Nov window
WEEKS = 14
LEARN_WEEKS = 12  # weeks 1–12 content; 13–14 wrap + mocks

# Mid-range syllabus weights for P
P_WEIGHTS = {
    "general": 0.27,
    "univariate": 0.47,
    "multivariate": 0.26,
}

# Map curriculum modules to clusters (lessonId → cluster)
MODULES = {
    "general": [
        ("setup", "Orientation & exam strategy", ["sets_venn"]),
        ("general_sets", "Sets, Venn, axioms", ["sets_venn"]),
        ("general_count", "Counting & classical probability", ["combinatorics", "sets_venn"]),
        ("general_axioms", "Probability rules & properties", ["sets_venn", "independence"]),
        ("general_cond", "Conditional probability", ["conditional_bayes", "total_prob"]),
        ("general_bayes", "Bayes & total probability", ["conditional_bayes", "total_prob"]),
        ("general_indep", "Independence & mutually exclusive", ["independence", "conditional_bayes"]),
    ],
    "univariate": [
        ("uni_discrete_def", "Discrete RV: PMF, E, Var", ["discrete_rv", "expectation_var"]),
        ("uni_binom_pois", "Binomial & Poisson", ["discrete_rv", "expectation_var"]),
        ("uni_other_disc", "Geometric, NB, Hypergeometric", ["discrete_rv"]),
        ("uni_cont", "Continuous RV & Uniform", ["continuous_rv", "expectation_var"]),
        ("uni_normal", "Normal distribution", ["normal", "continuous_rv"]),
        ("uni_exp_gamma", "Exponential, Gamma, Beta", ["continuous_rv", "insurance"]),
        ("uni_insurance", "Insurance payments (deductible/limit/coinsurance)", ["insurance", "expectation_var", "continuous_rv"]),
    ],
    "multivariate": [
        ("multi_joint", "Joint, marginal, conditional", ["joint", "expectation_var"]),
        ("multi_cov", "Covariance & linear combinations", ["joint"]),
        ("multi_order_clt", "Order statistics & CLT", ["order_stats", "clt", "joint"]),
    ],
}


def allocate_weeks() -> list[tuple[str, int]]:
    """Return list of (cluster, n_weeks) summing to LEARN_WEEKS."""
    raw = {k: P_WEIGHTS[k] * LEARN_WEEKS for k in P_WEIGHTS}
    # integer allocation with largest remainder
    floors = {k: int(raw[k]) for k in raw}
    rem = LEARN_WEEKS - sum(floors.values())
    fracs = sorted(raw.keys(), key=lambda k: raw[k] - floors[k], reverse=True)
    for i in range(rem):
        floors[fracs[i % len(fracs)]] += 1
    # ensure each cluster at least 2 weeks if possible
    order = []
    for k in ["general", "univariate", "multivariate"]:
        order.append((k, max(1, floors[k])))
    # fix sum
    s = sum(n for _, n in order)
    if s != LEARN_WEEKS:
        # adjust univariate
        order = [(k, n if k != "univariate" else n + (LEARN_WEEKS - s)) for k, n in order]
    return order


def expand_modules(cluster: str, n_weeks: int) -> list[dict]:
    mods = MODULES[cluster]
    # repeat/cycle modules to fill weeks; later weeks get more practice emphasis
    out = []
    for w in range(n_weeks):
        m = mods[w % len(mods)]
        # later pass through same cluster → practice-heavy
        pass_idx = w // len(mods)
        out.append(
            {
                "lessonId": m[0],
                "title": m[1] + (f" (mastery pass {pass_idx + 1})" if pass_idx else ""),
                "topicPrefs": m[2],
                "cluster": cluster,
                "passIndex": pass_idx,
            }
        )
    return out


def day_activity(week_idx: int, weekday: int, module: dict | None, wrap: bool) -> dict:
    """
    weekday: 0=Mon .. 6=Sun
    Activity mix target over course: 40% read, 50% practice, 10% mock
    Last 2 weeks: almost all mock + review.
    """
    if wrap:
        if weekday == 5:  # Sat full mock
            return {
                "mode": "full_mock",
                "readPct": 0,
                "practicePct": 20,
                "mockPct": 80,
                "questionTarget": 30,
                "title": "Full mock exam (3h) + diagnosis",
                "activity": "mock",
            }
        if weekday == 6:
            return {
                "mode": "wrap_review",
                "readPct": 30,
                "practicePct": 50,
                "mockPct": 20,
                "questionTarget": 20,
                "title": "Weakness clinic + wrong-pool drill",
                "activity": "review",
            }
        # weekdays wrap: mini mock or timed sets
        return {
            "mode": "timed_set",
            "readPct": 15,
            "practicePct": 55,
            "mockPct": 30,
            "questionTarget": 20,
            "title": f"Wrap-up drill — {module['title'] if module else 'mixed'}",
            "activity": "practice_mock",
            "lessonId": module["lessonId"] if module else "final",
            "topicPrefs": module["topicPrefs"] if module else ["insurance", "conditional_bayes", "normal", "joint", "clt"],
        }

    # Normal weeks: Mon–Thu learn+practice, Fri practice+mini mock, weekend mock/review
    if weekday <= 3:  # Mon–Thu: heavy learn + practice (skew to 40/50 overall)
        return {
            "mode": "learn",
            "readPct": 45,
            "practicePct": 50,
            "mockPct": 5,
            "questionTarget": 18 if weekday < 3 else 20,
            "title": module["title"],
            "activity": "learn_practice",
            "lessonId": module["lessonId"],
            "topicPrefs": module["topicPrefs"],
            "cluster": module["cluster"],
        }
    if weekday == 4:  # Friday: practice + short timed
        return {
            "mode": "practice",
            "readPct": 20,
            "practicePct": 65,
            "mockPct": 15,
            "questionTarget": 22,
            "title": f"Practice push — {module['title']}",
            "activity": "practice",
            "lessonId": module["lessonId"],
            "topicPrefs": module["topicPrefs"],
            "cluster": module["cluster"],
            "fmLight": module["cluster"] == "univariate" and module["lessonId"] in ("uni_insurance", "uni_exp_gamma"),
        }
    if weekday == 5:  # Saturday
        return {
            "mode": "weekend_mock",
            "readPct": 10,
            "practicePct": 40,
            "mockPct": 50,
            "questionTarget": 15 if week_idx < 4 else 20,
            "title": "Weekend timed set / half-mock",
            "activity": "mock",
            "lessonId": module["lessonId"],
            "topicPrefs": module["topicPrefs"],
            "cluster": module["cluster"],
        }
    # Sunday
    return {
        "mode": "review",
        "readPct": 35,
        "practicePct": 55,
        "mockPct": 10,
        "questionTarget": 12,
        "title": "Active recall + wrong pool + Sunday recap",
        "activity": "review",
        "lessonId": module["lessonId"],
        "topicPrefs": module["topicPrefs"],
        "cluster": module["cluster"],
    }


def build_p_plan() -> dict:
    alloc = allocate_weeks()
    week_modules: list[dict] = []
    for cluster, n in alloc:
        week_modules.extend(expand_modules(cluster, n))

    assert len(week_modules) == LEARN_WEEKS, len(week_modules)

    days = []
    day_index = 0
    # start from START, align to include full weeks Mon-start
    start = START
    # if not Monday, still start on START
    for w in range(WEEKS):
        wrap = w >= LEARN_WEEKS
        mod = week_modules[min(w, LEARN_WEEKS - 1)] if not wrap else {
            "lessonId": "final",
            "title": "Final review mix",
            "topicPrefs": ["insurance", "conditional_bayes", "normal", "joint", "clt", "discrete_rv"],
            "cluster": "mixed",
            "passIndex": 0,
        }
        week_start = start + timedelta(weeks=w)
        # generate 7 days Mon-Sun relative to week_start's Monday
        # Use calendar week containing week_start
        monday = week_start - timedelta(days=week_start.weekday())
        for wd in range(7):
            d = monday + timedelta(days=wd)
            if d < START and w == 0:
                continue
            act = day_activity(w, wd, mod, wrap)
            lesson_ids = [act.get("lessonId") or mod["lessonId"]]
            if act.get("fmLight"):
                lesson_ids.append("fm_tvm" if w < 8 else "fm_ann")
            days.append(
                {
                    "date": d.isoformat(),
                    "dayIndex": day_index,
                    "weekday": d.strftime("%A"),
                    "week": w + 1,
                    "phase": "wrap" if wrap else act.get("cluster") or mod.get("cluster") or "learn",
                    "title": act["title"],
                    "mode": act["mode"],
                    "activity": act["activity"],
                    "isWeekend": wd >= 5,
                    "lessonId": lesson_ids[0],
                    "lessonIds": lesson_ids,
                    "topicPrefs": act.get("topicPrefs") or mod["topicPrefs"],
                    "questionTarget": act["questionTarget"],
                    "readPct": act["readPct"],
                    "practicePct": act["practicePct"],
                    "mockPct": act["mockPct"],
                    "requireLesson": act["activity"] in ("learn_practice", "practice") and not wrap,
                    "fmLight": bool(act.get("fmLight")),
                    "assignedQuestionIds": [],  # filled by build_question_bank / assigner
                }
            )
            day_index += 1

    # trim to end date ~ START + 14 weeks
    end = START + timedelta(weeks=WEEKS)
    days = [d for d in days if START <= date.fromisoformat(d["date"]) < end + timedelta(days=1)]
    # reindex
    for i, d in enumerate(days):
        d["dayIndex"] = i

    return {
        "courseId": "P",
        "name": "Exam P — Probability",
        "examCode": "P",
        "startDate": START.isoformat(),
        "endDate": end.isoformat(),
        "weeks": WEEKS,
        "learnWeeks": LEARN_WEEKS,
        "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
        "weights": P_WEIGHTS,
        "weekAllocation": [{"cluster": k, "weeks": n} for k, n in alloc],
        "targetExamWindow": "November 2026 (adjust to your sitting)",
        "dailyHoursWeekday": 2,
        "notes": [
            "Last 2 weeks are wrap-up + full mocks only (minimal new learning).",
            "Daily targets: ~40% reading/lesson, ~50% practice MC, ~10% timed/mock overall.",
            "Topic weeks follow SOA weight midpoints: General 27%, Univariate 47%, Multivariate 26%.",
        ],
        "days": days,
    }


def build_catalog() -> dict:
    return {
        "version": 1,
        "updated": date.today().isoformat(),
        "activeDefault": "P",
        "courses": [
            {
                "id": "P",
                "name": "Exam P — Probability",
                "shortName": "Exam P",
                "status": "ready",
                "durationWeeks": 14,
                "examFormat": "30 MCQ · 3 hours · CBT",
                "weights": P_WEIGHTS,
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "General probability, univariate & multivariate RVs. Full path ready.",
                "planPath": "data/courses/p/plan.json",
                "syllabusNote": "SOA 2026: General 23–30%, Univariate 44–50%, Multivariate 23–30%",
            },
            {
                "id": "FM",
                "name": "Exam FM — Financial Mathematics",
                "shortName": "Exam FM",
                "status": "scaffold",
                "durationWeeks": 14,
                "examFormat": "30 MCQ · 2.5 hours · CBT",
                "weights": {
                    "tvm": 0.10,
                    "annuities": 0.25,
                    "loans": 0.20,
                    "bonds": 0.20,
                    "portfolios": 0.25,
                },
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "TVM, annuities, loans, bonds, duration/immunization. Coming next.",
                "planPath": None,
                "syllabusNote": "SOA FM: TVM 5–15%, Annuities 20–30%, Loans 15–25%, Bonds 15–25%, Portfolios/ALM 20–30%",
            },
            {
                "id": "FAM",
                "name": "Exam FAM — Fundamentals of Actuarial Mathematics",
                "shortName": "Exam FAM",
                "status": "scaffold",
                "durationWeeks": 16,
                "examFormat": "CBT multiple choice",
                "weights": {
                    "short_term": 0.45,
                    "long_term": 0.55,
                },
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "Short-term & long-term actuarial math foundations. Scaffolded for later.",
                "planPath": None,
                "syllabusNote": "Covers ST + LT intro topics per current SOA FAM syllabus",
            },
            {
                "id": "SRM",
                "name": "Exam SRM — Statistics for Risk Modeling",
                "shortName": "Exam SRM",
                "status": "scaffold",
                "durationWeeks": 14,
                "examFormat": "CBT multiple choice",
                "weights": {
                    "learning": 0.20,
                    "glm": 0.35,
                    "time_series": 0.20,
                    "pca_clustering": 0.15,
                    "decision_trees": 0.10,
                },
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "Statistical learning, GLMs, time series, trees. Scaffolded for later.",
                "planPath": None,
                "syllabusNote": "Per current SOA SRM learning objectives",
            },
            {
                "id": "PA",
                "name": "Exam PA — Predictive Analytics",
                "shortName": "Exam PA",
                "status": "scaffold",
                "durationWeeks": 14,
                "examFormat": "Project / written CBT-style",
                "weights": {
                    "problem_statement": 0.15,
                    "data_eda": 0.25,
                    "modeling": 0.35,
                    "communication": 0.25,
                },
                "mix": {"reading": 0.35, "practice": 0.45, "mock": 0.20},
                "description": "End-to-end predictive analytics project skills. Scaffolded for later.",
                "planPath": None,
                "syllabusNote": "Practice with past PA projects; heavier mock/project share",
            },
            {
                "id": "ST",
                "name": "Short-Term Specialty Track (prep)",
                "shortName": "Short-Term",
                "status": "scaffold",
                "durationWeeks": 12,
                "examFormat": "Pathway-dependent",
                "weights": {"reserve": 0.35, "pricing": 0.35, "reinsurance": 0.15, "other": 0.15},
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "Bridge after FAM toward short-term practice. Coming later.",
                "planPath": None,
                "syllabusNote": "Aligns with short-term actuarial practice themes",
            },
            {
                "id": "LT",
                "name": "Long-Term Specialty Track (prep)",
                "shortName": "Long-Term",
                "status": "scaffold",
                "durationWeeks": 12,
                "examFormat": "Pathway-dependent",
                "weights": {"life_contingencies": 0.40, "reserves": 0.30, "products": 0.20, "other": 0.10},
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "Bridge after FAM toward long-term practice. Coming later.",
                "planPath": None,
                "syllabusNote": "Aligns with long-term actuarial practice themes",
            },
        ],
    }


def main() -> None:
    plan = build_p_plan()
    catalog = build_catalog()
    (DATA / "courses.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    pdir = DATA / "courses" / "p"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")

    # Also write as curriculum.json for Exam P (primary active course)
    # assignedQuestionIds filled by assign_plan_questions.py or build_question_bank
    curriculum = {
        "courseId": "P",
        "examTarget": plan["endDate"],
        "registrationDeadline": "2026-09-30",
        "window": ["2026-11-01", "2026-11-15"],
        "dailyQuestionGoal": 20,
        "mix": plan["mix"],
        "weights": plan["weights"],
        "planNotes": plan["notes"],
        "days": plan["days"],
    }
    (DATA / "curriculum.json").write_text(json.dumps(curriculum, indent=2), encoding="utf-8")

    print("courses:", len(catalog["courses"]))
    print("P days:", len(plan["days"]), plan["startDate"], "→", plan["endDate"])
    print("week alloc:", plan["weekAllocation"])
    # mix check
    r = sum(d["readPct"] for d in plan["days"]) / len(plan["days"])
    p = sum(d["practicePct"] for d in plan["days"]) / len(plan["days"])
    m = sum(d["mockPct"] for d in plan["days"]) / len(plan["days"])
    print(f"avg daily mix read/practice/mock ≈ {r:.0f}/{p:.0f}/{m:.0f}")


if __name__ == "__main__":
    main()

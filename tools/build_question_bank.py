"""Build questions.json + curriculum.json from extracted SOA samples."""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"

TOPIC_RULES = [
    ("sets_venn", r"\b(Venn|union|intersection|none of the|all three|watched|policyholders who are)\b", "P1a", "general"),
    ("combinatorics", r"\b(permutation|combination|arrang|committee|hands? of|dealt|urn contains)\b", "P1b", "general"),
    ("conditional_bayes", r"\b(given that|Bayes|posterior|conditional|neither of his parents|screening|false positive)\b", "P1g", "general"),
    ("independence", r"\bindependent\b", "P1c", "general"),
    ("total_prob", r"\b(total probability|renew|risk class|type I|type II)\b", "P1g", "general"),
    ("discrete_rv", r"\b(binomial|Poisson|geometric|negative binomial|hypergeometric|probability mass)\b", "P2", "univariate"),
    ("continuous_rv", r"\b(exponential|gamma|beta|uniform distribution|pdf|density function)\b", "P2", "univariate"),
    ("normal", r"\b(normal(ly)? distributed|standard normal|N\(|z-score)\b", "P2", "univariate"),
    ("expectation_var", r"\b(expected value|mean and variance|variance of|E\[|Var\()\b", "P2c", "univariate"),
    ("insurance", r"\b(deductible|coinsurance|policy limit|reimbursement|payment.*claim|ordinary deductible|franchise)\b", "P2e", "univariate"),
    ("joint", r"\b(joint (density|distribution|pmf)|marginal|covariance|correlation)\b", "P3", "multivariate"),
    ("order_stats", r"\b(order statistic|maximum of|minimum of|ith largest)\b", "P3f", "multivariate"),
    ("clt", r"\b(central limit|approximately normal|sample mean)\b", "P3i", "multivariate"),
    ("transform", r"\b(distribution of Y|transformation|Y = g)\b", "P2", "univariate"),
]

READINGS = {
    "setup": [
        {"id": "r0a", "title": "Read Exam P syllabus LO 1–3 (weights)", "minutes": 20, "resource": "Books/2026-09-p-syllabus.pdf", "lo": "all"},
        {"id": "r0b", "title": "Skim Finan TOC; bookmark §1–28", "minutes": 15, "resource": "Books/Exam_P_Study_GuideFinan.pdf", "lo": "all"},
        {"id": "r0c", "title": "Baseline quiz in the app", "minutes": 40, "resource": "app quiz", "lo": "baseline"},
    ],
    "general_sets": [{"id": "rg1", "title": "Finan §1–2 Sets & Venn", "minutes": 45, "resource": "Finan §1–2", "lo": "P1a"}],
    "general_count": [{"id": "rg2", "title": "Finan §3–5 Counting", "minutes": 50, "resource": "Finan §3–5", "lo": "P1b"}],
    "general_axioms": [{"id": "rg3", "title": "Finan §6–8 Probability axioms & properties", "minutes": 50, "resource": "Finan §6–8", "lo": "P1a"}],
    "general_cond": [{"id": "rg4", "title": "Finan §9 Conditional probability", "minutes": 45, "resource": "Finan §9", "lo": "P1f"}],
    "general_bayes": [{"id": "rg5", "title": "Finan §10 Bayes & total probability", "minutes": 50, "resource": "Finan §10", "lo": "P1g"}],
    "general_indep": [{"id": "rg6", "title": "Finan §11 Independence", "minutes": 40, "resource": "Finan §11", "lo": "P1c"}],
    "uni_discrete_def": [{"id": "ru1", "title": "Finan §13–17 Discrete RV, E, Var", "minutes": 55, "resource": "Finan §13–17", "lo": "P2a"}],
    "uni_binom_pois": [{"id": "ru2", "title": "Finan §18–19 Binomial & Poisson", "minutes": 50, "resource": "Finan §18–19", "lo": "P2"}],
    "uni_other_disc": [{"id": "ru3", "title": "Finan §20 Geometric, NB, Hypergeometric", "minutes": 50, "resource": "Finan §20", "lo": "P2"}],
    "uni_cont": [{"id": "ru4", "title": "Finan §21–24 Continuous RV & Uniform", "minutes": 50, "resource": "Finan §21–24", "lo": "P2"}],
    "uni_normal": [{"id": "ru5", "title": "Finan §25 Normal distribution", "minutes": 50, "resource": "Finan §25", "lo": "P2"}],
    "uni_exp_gamma": [{"id": "ru6", "title": "Finan §26–27 Exponential, Gamma, Beta", "minutes": 50, "resource": "Finan §26–27", "lo": "P2"}],
    "uni_insurance": [{"id": "ru7", "title": "Insurance payments + Risk & Insurance note", "minutes": 55, "resource": "SOA Risk and Insurance + samples", "lo": "P2e"}],
    "multi_joint": [{"id": "rm1", "title": "Finan §29–30 Joint & independent RVs", "minutes": 50, "resource": "Finan §29–30", "lo": "P3a"}],
    "multi_cov": [{"id": "rm2", "title": "Finan §35–36 Covariance & correlation", "minutes": 45, "resource": "Finan §35–36", "lo": "P3e"}],
    "multi_order_clt": [{"id": "rm3", "title": "Order statistics + Finan §40 CLT", "minutes": 50, "resource": "Finan order stats + §40", "lo": "P3i"}],
    "final": [{"id": "rf1", "title": "Formula sheet skim only (no new theory)", "minutes": 20, "resource": "formula_sheet_P.md", "lo": "review"}],
    "fm_tvm": [{"id": "fm1", "title": "FM Topic 1: TVM (i, v, d, δ) light", "minutes": 30, "resource": "FM syllabus §1", "lo": "FM1"}],
    "fm_ann": [{"id": "fm2", "title": "FM Topic 2: Level annuities light", "minutes": 30, "resource": "FM syllabus §2", "lo": "FM2"}],
    "transition": [{"id": "t1", "title": "FM primary: TVM + annuities practice", "minutes": 50, "resource": "FM samples", "lo": "FM"}],
}


def tag(q: dict) -> dict:
    text = (q.get("stem") or "") + " " + " ".join((q.get("choices") or {}).values())
    tags, los, clusters = [], set(), set()
    for name, pat, lo, cluster in TOPIC_RULES:
        if re.search(pat, text, re.I):
            tags.append(name)
            los.add(lo)
            clusters.add(cluster)
    if not tags:
        tags = ["general_misc"]
        los.add("P1")
        clusters.add("general")
    q["topics"] = tags
    q["lo"] = sorted(los)[0]
    q["cluster"] = sorted(clusters)[0]
    return q


def phase_for(d: date) -> str:
    if d <= date(2026, 7, 12):
        return "setup"
    if d <= date(2026, 7, 26):
        return "general"
    if d <= date(2026, 8, 30):
        return "univariate"
    if d <= date(2026, 9, 7):
        return "multivariate"
    if d <= date(2026, 9, 13):
        return "final"
    if d == date(2026, 9, 14):
        return "exam"
    return "transition"


def day_config(d: date) -> dict:
    ph = phase_for(d)
    wd = d.weekday()
    is_weekend = wd >= 5
    daily_q = 10 if ph == "setup" else (15 if is_weekend else 20)

    def pack(title, key, topics, q_target, mode, extra_keys=None):
        readings = list(READINGS[key])
        lesson_ids = [key]
        for ek in extra_keys or []:
            readings.extend(READINGS[ek])
            lesson_ids.append(ek)
        return dict(
            phase=ph,
            title=title,
            lessonId=key,
            lessonIds=lesson_ids,
            readings=readings,
            topics=topics,
            q_target=q_target,
            is_weekend=is_weekend,
            mode=mode,
        )

    if ph == "exam":
        return pack("Exam P Day", "final", ["general_misc"], 0, "exam")
    if ph == "final":
        return pack(
            "Final week — mock focus",
            "final",
            ["insurance", "conditional_bayes", "normal", "joint", "clt"],
            20 if not is_weekend else 30,
            "mock" if is_weekend else "drill",
        )
    if ph == "setup":
        return pack("Setup & baseline", "setup", ["sets_venn", "conditional_bayes"], 10, "baseline")
    if ph == "general":
        if d <= date(2026, 7, 15):
            return pack("Sets, Venn, counting intro", "general_sets", ["sets_venn", "combinatorics"], daily_q, "weekend_mock" if is_weekend else "learn")
        if d <= date(2026, 7, 17):
            return pack("Counting & classical probability", "general_count", ["combinatorics", "sets_venn"], daily_q, "weekend_mock" if is_weekend else "learn")
        if d <= date(2026, 7, 19):
            return pack("Axioms + weekend review", "general_axioms", ["sets_venn", "independence"], daily_q, "weekend_mock" if is_weekend else "learn")
        if d <= date(2026, 7, 22):
            return pack("Conditional probability", "general_cond", ["conditional_bayes", "total_prob"], daily_q, "weekend_mock" if is_weekend else "learn")
        if d <= date(2026, 7, 24):
            return pack("Bayes & total probability", "general_bayes", ["conditional_bayes", "total_prob"], daily_q, "weekend_mock" if is_weekend else "learn")
        return pack("Independence + Phase 1 capstone", "general_indep", ["independence", "conditional_bayes", "sets_venn"], daily_q, "weekend_mock" if is_weekend else "learn")
    if ph == "univariate":
        if d <= date(2026, 8, 2):
            key, topics, title = "uni_discrete_def", ["discrete_rv", "expectation_var"], "Discrete RV foundations"
        elif d <= date(2026, 8, 6):
            key, topics, title = "uni_binom_pois", ["discrete_rv", "expectation_var"], "Binomial & Poisson"
        elif d <= date(2026, 8, 10):
            key, topics, title = "uni_other_disc", ["discrete_rv"], "Geometric, NB, Hypergeometric"
        elif d <= date(2026, 8, 14):
            key, topics, title = "uni_cont", ["continuous_rv", "expectation_var"], "Continuous foundations"
        elif d <= date(2026, 8, 18):
            key, topics, title = "uni_normal", ["normal", "continuous_rv"], "Normal distribution"
        elif d <= date(2026, 8, 22):
            key, topics, title = "uni_exp_gamma", ["continuous_rv", "insurance"], "Exp, Gamma, Beta"
        else:
            key, topics, title = "uni_insurance", ["insurance", "expectation_var", "continuous_rv"], "Insurance payments mastery"
        extra = None
        if wd == 4 and d >= date(2026, 7, 31):
            extra = ["fm_tvm" if d < date(2026, 8, 21) else "fm_ann"]
        return pack(title, key, topics, daily_q, "weekend_mock" if is_weekend else "learn", extra_keys=extra)
    if ph == "multivariate":
        if d <= date(2026, 9, 2):
            return pack("Joint distributions", "multi_joint", ["joint", "expectation_var"], daily_q, "weekend_mock" if is_weekend else "learn")
        if d <= date(2026, 9, 4):
            return pack("Covariance & linear combos", "multi_cov", ["joint"], daily_q, "weekend_mock" if is_weekend else "learn")
        return pack("Order stats & CLT", "multi_order_clt", ["order_stats", "clt", "joint"], daily_q, "weekend_mock" if is_weekend else "learn")
    return pack("Post-P FM transition", "transition", ["insurance", "conditional_bayes"], 10, "fm")


def main() -> None:
    qs = json.loads((DATA / "questions_raw.json").read_text(encoding="utf-8"))
    ans = json.loads((DATA / "answers_raw.json").read_text(encoding="utf-8"))

    merged = []
    missing_ans = 0
    for q in qs:
        n = str(q["number"])
        q["answer"] = ans.get(n)
        if q["answer"] is None:
            missing_ans += 1
        if not q.get("choices"):
            continue
        tag(q)
        merged.append(q)

    print("merged", len(merged), "missing answers", missing_ans)
    print(Counter(q["cluster"] for q in merged))

    by_topic: dict[str, list[str]] = {}
    for q in merged:
        for t in q["topics"]:
            by_topic.setdefault(t, []).append(q["id"])

    used: set[str] = set()
    curriculum = []
    day_num = 0
    d = date(2026, 7, 12)
    end = date(2026, 9, 28)
    while d <= end:
        cfg = day_config(d)
        pool: list[str] = []
        for t in cfg["topics"]:
            pool.extend(by_topic.get(t, []))
        pool = pool or [q["id"] for q in merged]
        seen: set[str] = set()
        ordered: list[str] = []
        for qid in pool:
            if qid not in seen:
                seen.add(qid)
                ordered.append(qid)
        take = [qid for qid in ordered if qid not in used][: max(cfg["q_target"] + 15, 25)]
        for qid in take:
            used.add(qid)
        if len(take) < cfg["q_target"]:
            for q in merged:
                if q["id"] not in used:
                    take.append(q["id"])
                    used.add(q["id"])
                if len(take) >= cfg["q_target"] + 10:
                    break
        curriculum.append(
            {
                "date": d.isoformat(),
                "dayIndex": day_num,
                "weekday": d.strftime("%A"),
                "phase": cfg["phase"],
                "title": cfg["title"],
                "mode": cfg["mode"],
                "isWeekend": cfg["is_weekend"],
                "lessonId": cfg.get("lessonId"),
                "lessonIds": cfg.get("lessonIds") or ([cfg.get("lessonId")] if cfg.get("lessonId") else []),
                "readings": cfg["readings"],
                "questionTarget": cfg["q_target"],
                "topicPrefs": cfg["topics"],
                "assignedQuestionIds": take[: max(cfg["q_target"] + 15, 25)],
                "fmLight": any(str(r.get("lo", "")).startswith("FM") for r in cfg["readings"]),
                "requireLesson": True,
            }
        )
        day_num += 1
        d += timedelta(days=1)

    slim = [
        {
            "id": q["id"],
            "number": q["number"],
            "exam": "P",
            "stem": q["stem"],
            "choices": q["choices"],
            "answer": q["answer"],
            "lo": q["lo"],
            "topics": q["topics"],
            "cluster": q["cluster"],
            "source": "SOA Exam P Sample",
        }
        for q in merged
    ]
    (DATA / "questions.json").write_text(json.dumps(slim, ensure_ascii=False), encoding="utf-8")
    (DATA / "curriculum.json").write_text(
        json.dumps(
            {
                "examTarget": "2026-09-14",
                "registrationDeadline": "2026-08-12",
                "window": ["2026-09-10", "2026-09-21"],
                "dailyQuestionGoal": 20,
                "days": curriculum,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print("curriculum days", len(curriculum), "unique Q assigned", len(used))
    print("wrote questions.json + curriculum.json")


if __name__ == "__main__":
    main()

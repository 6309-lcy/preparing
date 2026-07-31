"""
Build multi-course catalog + Exam P Duolingo-style path + 14-week calendar.

Path model (like Duolingo):
  Course → Units → Chapters → Levels (+ chapter test at end of each chapter)

Exam P syllabus (SOA 2026 midpoints):
  General Probability 23–30%  → 27%
  Univariate RVs       44–50%  → 47%
  Multivariate RVs     23–30%  → 26%

Activity mix target: 40% reading · 50% practice · 10% mock/chapter tests
Timeline: 14 weeks (learn 12 + wrap 2). Last 2 weeks = wrap-up + full mocks.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
P_DIR = DATA / "courses" / "p"
DATA.mkdir(parents=True, exist_ok=True)
P_DIR.mkdir(parents=True, exist_ok=True)

# Align plan to "today" so Today view always has a mapped day
START = date.today()
WEEKS = 14
LEARN_WEEKS = 12

P_WEIGHTS = {
    "general": 0.27,
    "univariate": 0.47,
    "multivariate": 0.26,
}

# ---------------------------------------------------------------------------
# Duolingo-style curriculum: units → chapters → levels
# Each content chapter: L1 Learn (read) · L2 Practice · L3 Drill · Chapter Test
# Mix: ~40% read (L1 heavier time) · ~50% practice (L2+L3) · ~10% tests/mocks
# ---------------------------------------------------------------------------

UNITS = [
    {
        "id": "u1_general",
        "number": 1,
        "title": "General Probability",
        "shortTitle": "General",
        "cluster": "general",
        "weight": 0.27,
        "weightRange": "23–30%",
        "color": "#0F766E",
        "description": "Sets, counting, conditionals, Bayes, independence — foundation for every later topic.",
        "chapters": [
            {
                "id": "p_ch00_setup",
                "number": 0,
                "title": "Course orientation",
                "lessonId": "setup",
                "topics": ["sets_venn"],
                "lo": ["P1"],
                "icon": "compass",
                "levels": "short",  # lesson + quick check only
            },
            {
                "id": "p_ch01_sets",
                "number": 1,
                "title": "Sets, Venn & axioms",
                "lessonId": "general_sets",
                "topics": ["sets_venn"],
                "lo": ["P1a"],
                "icon": "circle",
            },
            {
                "id": "p_ch02_count",
                "number": 2,
                "title": "Counting & classical probability",
                "lessonId": "general_count",
                "topics": ["combinatorics", "sets_venn"],
                "lo": ["P1b"],
                "icon": "hash",
            },
            {
                "id": "p_ch03_rules",
                "number": 3,
                "title": "Probability rules & properties",
                "lessonId": "general_axioms",
                "topics": ["sets_venn", "independence"],
                "lo": ["P1a", "P1c"],
                "icon": "list",
            },
            {
                "id": "p_ch04_cond",
                "number": 4,
                "title": "Conditional probability",
                "lessonId": "general_cond",
                "topics": ["conditional_bayes", "total_prob"],
                "lo": ["P1c"],
                "icon": "git-branch",
            },
            {
                "id": "p_ch05_bayes",
                "number": 5,
                "title": "Bayes & total probability",
                "lessonId": "general_bayes",
                "topics": ["conditional_bayes", "total_prob"],
                "lo": ["P1c", "P1g"],
                "icon": "shuffle",
            },
            {
                "id": "p_ch06_indep",
                "number": 6,
                "title": "Independence",
                "lessonId": "general_indep",
                "topics": ["independence", "conditional_bayes"],
                "lo": ["P1c"],
                "icon": "unlink",
            },
        ],
    },
    {
        "id": "u2_univariate",
        "number": 2,
        "title": "Univariate Random Variables",
        "shortTitle": "Univariate",
        "cluster": "univariate",
        "weight": 0.47,
        "weightRange": "44–50%",
        "color": "#0369A1",
        "description": "Biggest exam slice: discrete & continuous RVs, famous families, insurance payments.",
        "chapters": [
            {
                "id": "p_ch07_disc",
                "number": 7,
                "title": "Discrete RV: PMF, E, Var",
                "lessonId": "uni_discrete_def",
                "topics": ["discrete_rv", "expectation_var"],
                "lo": ["P2"],
                "icon": "bar-chart-2",
            },
            {
                "id": "p_ch08_binom",
                "number": 8,
                "title": "Binomial & Poisson",
                "lessonId": "uni_binom_pois",
                "topics": ["discrete_rv", "expectation_var"],
                "lo": ["P2"],
                "icon": "layers",
            },
            {
                "id": "p_ch09_other_disc",
                "number": 9,
                "title": "Geometric, NB, Hypergeometric",
                "lessonId": "uni_other_disc",
                "topics": ["discrete_rv"],
                "lo": ["P2"],
                "icon": "grid",
            },
            {
                "id": "p_ch10_cont",
                "number": 10,
                "title": "Continuous RV & Uniform",
                "lessonId": "uni_cont",
                "topics": ["continuous_rv", "expectation_var"],
                "lo": ["P2"],
                "icon": "activity",
            },
            {
                "id": "p_ch11_normal",
                "number": 11,
                "title": "Normal distribution",
                "lessonId": "uni_normal",
                "topics": ["normal", "continuous_rv"],
                "lo": ["P2e"],
                "icon": "trending-up",
            },
            {
                "id": "p_ch12_exp",
                "number": 12,
                "title": "Exponential, Gamma, Beta",
                "lessonId": "uni_exp_gamma",
                "topics": ["continuous_rv", "insurance"],
                "lo": ["P2"],
                "icon": "zap",
            },
            {
                "id": "p_ch13_ins",
                "number": 13,
                "title": "Insurance payments",
                "lessonId": "uni_insurance",
                "topics": ["insurance", "expectation_var", "continuous_rv"],
                "lo": ["P2c"],
                "icon": "shield",
            },
        ],
    },
    {
        "id": "u3_multivariate",
        "number": 3,
        "title": "Multivariate Random Variables",
        "shortTitle": "Multivariate",
        "cluster": "multivariate",
        "weight": 0.26,
        "weightRange": "23–30%",
        "color": "#7C3AED",
        "description": "Joint, marginal, conditional; covariance; order stats & CLT.",
        "chapters": [
            {
                "id": "p_ch14_joint",
                "number": 14,
                "title": "Joint, marginal, conditional",
                "lessonId": "multi_joint",
                "topics": ["joint", "expectation_var"],
                "lo": ["P3"],
                "icon": "share-2",
            },
            {
                "id": "p_ch15_cov",
                "number": 15,
                "title": "Covariance & linear combinations",
                "lessonId": "multi_cov",
                "topics": ["joint", "expectation_var"],
                "lo": ["P3"],
                "icon": "git-merge",
            },
            {
                "id": "p_ch16_order",
                "number": 16,
                "title": "Order statistics & CLT",
                "lessonId": "multi_order_clt",
                "topics": ["order_stats", "clt", "joint"],
                "lo": ["P3f"],
                "icon": "sort-asc",
            },
        ],
    },
    {
        "id": "u4_wrap",
        "number": 4,
        "title": "Wrap-up & Mock Exams",
        "shortTitle": "Wrap-up",
        "cluster": "wrap",
        "weight": 0.0,
        "weightRange": "last 2 weeks",
        "color": "#B45309",
        "description": "No new topics. Mixed review, chapter-style mix tests, and full 30Q mocks.",
        "chapters": [
            {
                "id": "p_ch17_mix_gen",
                "number": 17,
                "title": "Mixed review — General",
                "lessonId": "final",
                "topics": ["sets_venn", "conditional_bayes", "independence", "combinatorics"],
                "lo": ["P1"],
                "icon": "refresh-cw",
                "levels": "review",
            },
            {
                "id": "p_ch18_mix_uni",
                "number": 18,
                "title": "Mixed review — Univariate",
                "lessonId": "final",
                "topics": ["discrete_rv", "continuous_rv", "normal", "insurance", "expectation_var"],
                "lo": ["P2"],
                "icon": "refresh-cw",
                "levels": "review",
            },
            {
                "id": "p_ch19_mix_multi",
                "number": 19,
                "title": "Mixed review — Multivariate",
                "lessonId": "final",
                "topics": ["joint", "order_stats", "clt"],
                "lo": ["P3"],
                "icon": "refresh-cw",
                "levels": "review",
            },
            {
                "id": "p_ch20_mock1",
                "number": 20,
                "title": "Full mock exam 1",
                "lessonId": "final",
                "topics": ["insurance", "conditional_bayes", "normal", "joint", "clt", "discrete_rv"],
                "lo": ["P1", "P2", "P3"],
                "icon": "clipboard-check",
                "levels": "full_mock",
            },
            {
                "id": "p_ch21_clinic",
                "number": 21,
                "title": "Weakness clinic",
                "lessonId": "final",
                "topics": ["insurance", "conditional_bayes", "normal", "joint", "clt", "discrete_rv"],
                "lo": ["P1", "P2", "P3"],
                "icon": "heart-pulse",
                "levels": "clinic",
            },
            {
                "id": "p_ch22_mock2",
                "number": 22,
                "title": "Full mock exam 2 + final",
                "lessonId": "final",
                "topics": ["insurance", "conditional_bayes", "normal", "joint", "clt", "discrete_rv"],
                "lo": ["P1", "P2", "P3"],
                "icon": "award",
                "levels": "full_mock",
            },
        ],
    },
]


def make_levels(chapter: dict) -> list[dict]:
    """Expand a chapter into ordered levels (Duolingo nodes)."""
    kind = chapter.get("levels", "standard")
    cid = chapter["id"]
    topics = chapter["topics"]
    lesson_id = chapter["lessonId"]
    title = chapter["title"]

    if kind == "short":
        return [
            {
                "id": f"{cid}_l1",
                "index": 1,
                "type": "lesson",
                "title": "Learn",
                "subtitle": title,
                "mode": "lesson",
                "lessonId": lesson_id,
                "topics": topics,
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
                "subtitle": "6 warm-up questions",
                "mode": "practice",
                "lessonId": lesson_id,
                "topics": topics,
                "questionTarget": 6,
                "readPct": 10,
                "practicePct": 80,
                "mockPct": 10,
                "xp": 25,
                "passPct": 0,
            },
        ]

    if kind == "review":
        return [
            {
                "id": f"{cid}_l1",
                "index": 1,
                "type": "lesson",
                "title": "Formula refresh",
                "subtitle": title,
                "mode": "lesson",
                "lessonId": lesson_id,
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
                "lessonId": lesson_id,
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
                "lessonId": lesson_id,
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

    if kind == "full_mock":
        return [
            {
                "id": f"{cid}_mock",
                "index": 1,
                "type": "full_mock",
                "title": "Full mock (30Q · 3h)",
                "subtitle": "Exam mode · no Grok · scaled score",
                "mode": "full_mock",
                "lessonId": lesson_id,
                "topics": topics,
                "questionTarget": 30,
                "minutes": 180,
                "passPct": 60,  # scaled 6/10 ≈ pass
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
                "subtitle": "Wrong-pool + weak topics",
                "mode": "practice",
                "lessonId": lesson_id,
                "topics": topics,
                "questionTarget": 15,
                "readPct": 20,
                "practicePct": 70,
                "mockPct": 10,
                "xp": 30,
            },
        ]

    if kind == "clinic":
        return [
            {
                "id": f"{cid}_l1",
                "index": 1,
                "type": "practice",
                "title": "Wrong-pool blitz",
                "subtitle": "Your misses first",
                "mode": "wrong_pool",
                "lessonId": lesson_id,
                "topics": topics,
                "questionTarget": 20,
                "readPct": 10,
                "practicePct": 80,
                "mockPct": 10,
                "xp": 35,
                "preferWrong": True,
            },
            {
                "id": f"{cid}_l2",
                "index": 2,
                "type": "practice",
                "title": "High-weight drill",
                "subtitle": "Univariate + Bayes + insurance",
                "mode": "practice",
                "lessonId": lesson_id,
                "topics": topics,
                "questionTarget": 18,
                "readPct": 15,
                "practicePct": 75,
                "mockPct": 10,
                "xp": 35,
            },
            {
                "id": f"{cid}_test",
                "index": 3,
                "type": "chapter_test",
                "title": "Clinic checkpoint",
                "subtitle": "15Q · pass ≥70%",
                "mode": "chapter_test",
                "lessonId": lesson_id,
                "topics": topics,
                "questionTarget": 15,
                "minutes": 30,
                "passPct": 70,
                "readPct": 5,
                "practicePct": 25,
                "mockPct": 70,
                "xp": 50,
            },
        ]

    # standard content chapter: Learn → Practice → Drill → Chapter Test
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
            "subtitle": "12Q timed · pass ≥70% to unlock next",
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


def build_path() -> dict:
    units_out = []
    flat_levels = []  # ordered unlock chain
    chapter_index = 0

    for u in UNITS:
        chapters_out = []
        for ch in u["chapters"]:
            chapter_index += 1
            levels = make_levels(ch)
            for lv in levels:
                lv["unitId"] = u["id"]
                lv["chapterId"] = ch["id"]
                lv["chapterTitle"] = ch["title"]
                lv["chapterNumber"] = ch["number"]
                lv["cluster"] = u["cluster"]
                flat_levels.append(lv["id"])

            chapters_out.append(
                {
                    "id": ch["id"],
                    "number": ch["number"],
                    "order": chapter_index,
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
                "shortTitle": u["shortTitle"],
                "cluster": u["cluster"],
                "weight": u["weight"],
                "weightRange": u["weightRange"],
                "color": u["color"],
                "description": u["description"],
                "chapterCount": len(chapters_out),
                "chapters": chapters_out,
            }
        )

    total_levels = sum(len(ch["levels"]) for u in units_out for ch in u["chapters"])
    total_chapters = sum(u["chapterCount"] for u in units_out)
    test_count = sum(
        1
        for u in units_out
        for ch in u["chapters"]
        for lv in ch["levels"]
        if lv["type"] in ("chapter_test", "full_mock")
    )

    return {
        "courseId": "P",
        "name": "Exam P — Probability",
        "structure": "duo_path",
        "version": 2,
        "updated": date.today().isoformat(),
        "syllabus": {
            "source": "SOA Exam P syllabus 2026",
            "examFormat": "30 MCQ · 3 hours · CBT",
            "weights": P_WEIGHTS,
            "weightRanges": {
                "general": "23–30%",
                "univariate": "44–50%",
                "multivariate": "23–30%",
            },
        },
        "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
        "timeline": {
            "weeks": WEEKS,
            "learnWeeks": LEARN_WEEKS,
            "startDate": START.isoformat(),
            "endDate": (START + timedelta(weeks=WEEKS)).isoformat(),
            "targetExamWindow": "November 2026 (adjust to your sitting)",
            "dailyHoursWeekday": 2,
            "notes": [
                "Duolingo-style: finish levels in order; chapter test unlocks the next chapter.",
                "Pass chapter tests at ≥70%. Full mocks use Exam mode (30Q / 3h).",
                "Last unit is wrap-up only — no new syllabus topics.",
                "Content volume follows mark distribution: Uni ~47%, General ~27%, Multi ~26%.",
            ],
        },
        "stats": {
            "units": len(units_out),
            "chapters": total_chapters,
            "levels": total_levels,
            "testsAndMocks": test_count,
        },
        "levelOrder": flat_levels,
        "units": units_out,
    }


def allocate_weeks() -> list[tuple[str, int]]:
    raw = {k: P_WEIGHTS[k] * LEARN_WEEKS for k in P_WEIGHTS}
    floors = {k: int(raw[k]) for k in raw}
    rem = LEARN_WEEKS - sum(floors.values())
    fracs = sorted(raw.keys(), key=lambda k: raw[k] - floors[k], reverse=True)
    for i in range(rem):
        floors[fracs[i % len(fracs)]] += 1
    order = []
    for k in ["general", "univariate", "multivariate"]:
        order.append((k, max(1, floors[k])))
    s = sum(n for _, n in order)
    if s != LEARN_WEEKS:
        order = [(k, n if k != "univariate" else n + (LEARN_WEEKS - s)) for k, n in order]
    return order


def flatten_content_chapters() -> list[dict]:
    """Content chapters only (not wrap), for calendar mapping."""
    out = []
    for u in UNITS:
        if u["cluster"] == "wrap":
            continue
        for ch in u["chapters"]:
            out.append(
                {
                    "chapterId": ch["id"],
                    "lessonId": ch["lessonId"],
                    "title": ch["title"],
                    "topicPrefs": ch["topics"],
                    "cluster": u["cluster"],
                }
            )
    return out


def day_activity(week_idx: int, weekday: int, module: dict | None, wrap: bool) -> dict:
    if wrap:
        if weekday == 5:
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
        return {
            "mode": "timed_set",
            "readPct": 15,
            "practicePct": 55,
            "mockPct": 30,
            "questionTarget": 20,
            "title": f"Wrap-up drill — {module['title'] if module else 'mixed'}",
            "activity": "practice_mock",
            "lessonId": module["lessonId"] if module else "final",
            "topicPrefs": module["topicPrefs"]
            if module
            else ["insurance", "conditional_bayes", "normal", "joint", "clt"],
            "chapterId": module.get("chapterId") if module else None,
        }

    if weekday <= 3:
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
            "chapterId": module.get("chapterId"),
        }
    if weekday == 4:
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
            "chapterId": module.get("chapterId"),
            "fmLight": module["cluster"] == "univariate"
            and module["lessonId"] in ("uni_insurance", "uni_exp_gamma"),
        }
    if weekday == 5:
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
            "chapterId": module.get("chapterId"),
        }
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
        "chapterId": module.get("chapterId"),
    }


def build_p_plan(path: dict) -> dict:
    """Calendar plan aligned to path chapters (for Today view)."""
    alloc = allocate_weeks()
    content_chs = flatten_content_chapters()
    # Spread content chapters across LEARN_WEEKS
    week_modules: list[dict] = []
    n_ch = len(content_chs)
    for w in range(LEARN_WEEKS):
        # map week → chapter (cycle/advance proportionally)
        idx = min(n_ch - 1, int(w * n_ch / LEARN_WEEKS))
        ch = content_chs[idx]
        # if next week maps same, still ok — mastery pass feel
        week_modules.append(ch)

    # Prefer weight-based week blocks: first 3 general, next 6 uni, last 3 multi
    week_modules = []
    for cluster, n in alloc:
        cluster_chs = [c for c in content_chs if c["cluster"] == cluster]
        for w in range(n):
            ch = cluster_chs[min(w, len(cluster_chs) - 1)]
            week_modules.append(ch)

    days = []
    day_index = 0
    start = START
    for w in range(WEEKS):
        wrap = w >= LEARN_WEEKS
        mod = (
            week_modules[min(w, LEARN_WEEKS - 1)]
            if not wrap
            else {
                "lessonId": "final",
                "title": "Final review mix",
                "topicPrefs": [
                    "insurance",
                    "conditional_bayes",
                    "normal",
                    "joint",
                    "clt",
                    "discrete_rv",
                ],
                "cluster": "mixed",
                "chapterId": "p_ch17_mix_gen",
            }
        )
        week_start = start + timedelta(weeks=w)
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
                    "chapterId": act.get("chapterId") or mod.get("chapterId"),
                    "assignedQuestionIds": [],
                }
            )
            day_index += 1

    end = START + timedelta(weeks=WEEKS)
    days = [d for d in days if START <= date.fromisoformat(d["date"]) < end + timedelta(days=1)]
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
        "pathPath": "data/courses/p/path.json",
        "targetExamWindow": "November 2026 (adjust to your sitting)",
        "dailyHoursWeekday": 2,
        "notes": [
            "Primary progression is the Duolingo-style Path (chapters → levels → chapter tests).",
            "Today view is a calendar guide aligned to the same topics.",
            "Last 2 weeks are wrap-up + full mocks only (minimal new learning).",
            "Daily targets: ~40% reading/lesson, ~50% practice MC, ~10% timed/mock overall.",
            "Topic weeks follow SOA weight midpoints: General 27%, Univariate 47%, Multivariate 26%.",
        ],
        "days": days,
        "pathStats": path.get("stats"),
    }


def build_catalog() -> dict:
    return {
        "version": 2,
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
                "description": "Duolingo-style path: 4 units · chapters · levels · chapter tests. Full curriculum ready.",
                "planPath": "data/courses/p/plan.json",
                "pathPath": "data/courses/p/path.json",
                "structure": "duo_path",
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
                "pathPath": None,
                "syllabusNote": "SOA FM: TVM 5–15%, Annuities 20–30%, Loans 15–25%, Bonds 15–25%, Portfolios/ALM 20–30%",
            },
            {
                "id": "FAM",
                "name": "Exam FAM — Fundamentals of Actuarial Mathematics",
                "shortName": "Exam FAM",
                "status": "scaffold",
                "durationWeeks": 16,
                "examFormat": "CBT multiple choice",
                "weights": {"short_term": 0.45, "long_term": 0.55},
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "Short-term & long-term actuarial math foundations. Scaffolded for later.",
                "planPath": None,
                "pathPath": None,
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
                "pathPath": None,
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
                "pathPath": None,
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
                "pathPath": None,
                "syllabusNote": "Aligns with short-term actuarial practice themes",
            },
            {
                "id": "LT",
                "name": "Long-Term Specialty Track (prep)",
                "shortName": "Long-Term",
                "status": "scaffold",
                "durationWeeks": 12,
                "examFormat": "Pathway-dependent",
                "weights": {
                    "life_contingencies": 0.40,
                    "reserves": 0.30,
                    "products": 0.20,
                    "other": 0.10,
                },
                "mix": {"reading": 0.40, "practice": 0.50, "mock": 0.10},
                "description": "Bridge after FAM toward long-term practice. Coming later.",
                "planPath": None,
                "pathPath": None,
                "syllabusNote": "Aligns with long-term actuarial practice themes",
            },
        ],
    }


def assign_questions_to_path(path: dict, questions: list[dict]) -> dict:
    """Pre-assign question IDs to practice/test levels by topic overlap."""
    by_topic: dict[str, list[str]] = {}
    for q in questions:
        if not q.get("answer"):
            continue
        for t in q.get("topics") or []:
            by_topic.setdefault(t, []).append(q["id"])

    used: set[str] = set()

    def pick(topics: list[str], n: int) -> list[str]:
        pool: list[str] = []
        for t in topics:
            for qid in by_topic.get(t, []):
                if qid not in used and qid not in pool:
                    pool.append(qid)
        # fallback any unused
        if len(pool) < n:
            for q in questions:
                if q.get("answer") and q["id"] not in used and q["id"] not in pool:
                    pool.append(q["id"])
                if len(pool) >= n * 2:
                    break
        chosen = pool[:n]
        used.update(chosen)
        return chosen

    for u in path["units"]:
        for ch in u["chapters"]:
            for lv in ch["levels"]:
                n = int(lv.get("questionTarget") or 0)
                if n <= 0:
                    lv["assignedQuestionIds"] = []
                    continue
                # chapter tests / mocks get fresh pool; practice reuses topics
                if lv["type"] in ("chapter_test", "full_mock"):
                    # don't mark used as permanently exclusive for mocks — allow broader
                    ids = pick(lv.get("topics") or ch["topics"], n)
                else:
                    ids = pick(lv.get("topics") or ch["topics"], n)
                lv["assignedQuestionIds"] = ids
    return path


def main() -> None:
    path = build_path()

    q_path = DATA / "questions.json"
    if q_path.exists():
        questions = json.loads(q_path.read_text(encoding="utf-8"))
        if isinstance(questions, dict):
            questions = questions.get("questions", [])
        path = assign_questions_to_path(path, questions)

    plan = build_p_plan(path)
    catalog = build_catalog()

    # also refresh curriculum.json for boot
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
        "pathPath": "data/courses/p/path.json",
    }

    (P_DIR / "path.json").write_text(json.dumps(path, indent=2), encoding="utf-8")
    (P_DIR / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    (DATA / "courses.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    (DATA / "curriculum.json").write_text(json.dumps(curriculum, indent=2), encoding="utf-8")

    print(f"Path: {path['stats']}")
    print(f"Plan days: {len(plan['days'])}")
    print(f"Wrote {P_DIR / 'path.json'}")
    print(f"Wrote {P_DIR / 'plan.json'}")
    print(f"Wrote {DATA / 'courses.json'}")


if __name__ == "__main__":
    main()

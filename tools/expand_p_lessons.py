"""Deepen thin Exam P lessons only (course-by-course approach)."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "app" / "data"
path = DATA / "lessons.json"
L = json.loads(path.read_text(encoding="utf-8"))


def add_sections(lesson_id: str, extra: list[dict]) -> None:
    les = L[lesson_id]
    existing = {s["id"] for s in les["sections"]}
    for s in extra:
        sid = s["id"]
        while sid in existing:
            sid = sid + "x"
        s["id"] = sid
        les["sections"].append(s)
        existing.add(sid)
    les["minutes"] = min(70, (les.get("minutes") or 40) + 10)


add_sections(
    "general_axioms",
    [
        {
            "id": "s4",
            "type": "concept",
            "title": "Boole / Bonferroni and partitions",
            "body": "If A1,...,An are a partition of S (disjoint, union S), then P(B)=Σ P(B∩Ai).\n\n"
            "Boole's inequality: P(∪Ai) ≤ Σ P(Ai).\n"
            "Lower bound sometimes: P(∪Ai) ≥ max P(Ai).\n\n"
            "Exam habit: rewrite messy 'at least one' as complement of 'none', and rewrite 'exactly one' as mutually exclusive pieces.",
        },
        {
            "id": "s5",
            "type": "example",
            "title": "Worked: exactly one of two events",
            "setup": "P(A)=0.5, P(B)=0.4, P(A∩B)=0.2. Find P(exactly one of A,B).",
            "solution": "Exactly one = (A∩Bᶜ) ∪ (Aᶜ∩B) = P(A)+P(B)−2P(A∩B)=0.5+0.4−0.4=0.5.",
            "why": "Inclusion-exclusion for the symmetric difference. Draw a Venn if the algebra feels slippery.",
        },
        {
            "id": "s6",
            "type": "check",
            "title": "Complement habit",
            "prompt": "P(at least one of A,B) is best rewritten as:",
            "choices": {
                "A": "P(A)P(B)",
                "B": "1 − P(Aᶜ∩Bᶜ)",
                "C": "P(A)−P(B)",
                "D": "P(A∩B) only",
            },
            "answer": "B",
            "explain": "At least one is the complement of none (neither).",
        },
    ],
)

add_sections(
    "general_count",
    [
        {
            "id": "s4",
            "type": "concept",
            "title": "With/without replacement & identical objects",
            "body": "Without replacement: denominators shrink (hypergeometric-style counting).\n"
            "With replacement / independent trials: denominators stay fixed.\n\n"
            "Multinomial coefficient for splitting n distinct into groups of sizes n1,...,nk:\n"
            " n!/(n1! ... nk!).\n\n"
            "If objects are identical within type, count distinct sequences carefully — do not overcount.",
        },
        {
            "id": "s5",
            "type": "example",
            "title": "Worked: committee with roles vs without",
            "setup": "10 people. (a) Choose 3 for a committee. (b) Choose president, secretary, treasurer (distinct).",
            "solution": "(a) C(10,3)=120.\n(b) P(10,3)=10·9·8=720.",
            "why": "Same people, different whether order/roles matter. Misreading this is the #1 counting trap.",
        },
        {
            "id": "s6",
            "type": "check",
            "title": "Order check",
            "prompt": "Passwords of length 4 from 10 distinct chars, no repeat — use:",
            "choices": {
                "A": "C(10,4)",
                "B": "P(10,4)",
                "C": "10^4 only if no-repeat",
                "D": "4!",
            },
            "answer": "B",
            "explain": "Order matters and no repeats ⇒ permutation P(10,4).",
        },
    ],
)

add_sections(
    "uni_normal",
    [
        {
            "id": "s4",
            "type": "concept",
            "title": "Linear transforms & sums of independents",
            "body": "If X~N(μ,σ²) then aX+b ~ N(aμ+b, a²σ²).\n\n"
            "If X,Y independent normals, then X+Y is normal with mean sum and variance sum.\n\n"
            "Exam P rarely needs the full bivariate normal density; it does need standardize + table + variance of linear combos.",
        },
        {
            "id": "s5",
            "type": "example",
            "title": "Worked: between two values",
            "setup": "X~N(50, 10²). Find P(40 < X < 65).",
            "solution": "Z1=(40−50)/10=−1, Z2=(65−50)/10=1.5.\n"
            "P=Φ(1.5)−Φ(−1)=Φ(1.5)−(1−Φ(1)).\n"
            "≈0.9332 − (1−0.8413)=0.7745.",
            "why": "Always convert both endpoints to Z, then subtract CDFs. Sketch the bell if inequalities confuse you.",
        },
        {
            "id": "s6",
            "type": "check",
            "title": "Linear transform",
            "prompt": "If X~N(2, 3²) then 4X+1 has variance:",
            "choices": {"A": "12", "B": "36", "C": "144", "D": "13"},
            "answer": "C",
            "explain": "Var(4X+1)=16·Var(X)=16·9=144.",
        },
    ],
)

add_sections(
    "multi_joint",
    [
        {
            "id": "s4",
            "type": "concept",
            "title": "Continuous joint densities",
            "body": "Joint PDF f(x,y) ≥ 0 with ∬ f=1.\n"
            "Marginal fX(x)=∫ f(x,y) dy.\n"
            "Conditional f(y|x)=f(x,y)/fX(x).\n"
            "Independent iff f(x,y)=fX(x)fY(y) on a rectangle support "
            "(careful with non-rectangle supports — dependence can hide in the region).",
        },
        {
            "id": "s5",
            "type": "example",
            "title": "Worked: independence via factorization",
            "setup": "f(x,y)=2 on 0<x<y<1 (and 0 else). Are X,Y independent?",
            "solution": "Support is a triangle, not a product rectangle ⇒ not independent.\n"
            "(You can also check f ≠ fX fY.)",
            "why": "Support shape alone can kill independence even if the formula 'looks separable' on the triangle.",
        },
        {
            "id": "s6",
            "type": "check",
            "title": "Marginal continuous",
            "prompt": "Continuous marginal fX(x) is obtained by:",
            "choices": {
                "A": "Multiplying f by x",
                "B": "Integrating joint f over y",
                "C": "Differentiating joint f",
                "D": "Setting y=0 only",
            },
            "answer": "B",
            "explain": "Integrate out the other variable.",
        },
    ],
)

add_sections(
    "multi_cov",
    [
        {
            "id": "s4",
            "type": "concept",
            "title": "E[XY] and bilinearity",
            "body": "E[aX+bY]=aE[X]+bE[Y] always.\n"
            "Cov is bilinear and symmetric; Cov(X,X)=Var(X).\n"
            "Cov(X,c)=0 for constant c.\n\n"
            "For uncorrelated variables Cov=0, Var(X+Y)=VarX+VarY.\n"
            "Independence ⇒ uncorrelated; uncorrelated ⇏ independent in general.",
        },
        {
            "id": "s5",
            "type": "example",
            "title": "Worked: correlation from cov",
            "setup": "VarX=4, VarY=9, Cov(X,Y)=3. Find Corr(X,Y).",
            "solution": "Corr=3/(2·3)=3/6=0.5.",
            "why": "Divide by product of SDs, not variances.",
        },
        {
            "id": "s6",
            "type": "check",
            "title": "Var of linear combo",
            "prompt": "Var(2X−3Y) expands to:",
            "choices": {
                "A": "4VarX+9VarY−12Cov",
                "B": "4VarX+9VarY+12Cov",
                "C": "2VarX−3VarY",
                "D": "VarX+VarY",
            },
            "answer": "A",
            "explain": "a=2,b=−3 ⇒ a²VarX+b²VarY+2ab Cov=4VarX+9VarY−12Cov.",
        },
    ],
)

add_sections(
    "final",
    [
        {
            "id": "s3",
            "type": "concept",
            "title": "High-yield LO triage",
            "body": "Spend final-week time proportional to syllabus weight:\n"
            "• Univariate (incl. insurance payments) — largest\n"
            "• General conditionals/Bayes — frequent traps\n"
            "• Multivariate joint/cov/CLT — fewer items but easy points if drilled\n\n"
            "Keep a one-page formula sheet you can rewrite from memory in 10 minutes.",
        },
        {
            "id": "s4",
            "type": "example",
            "title": "Worked: 3-hour mock diagnosis loop",
            "setup": "You score 18/30 on a mock. How to spend the next day?",
            "solution": "Tag each miss: setup error / formula / arithmetic / misread.\n"
            "If ≥5 misses share a tag (e.g. deductible), do a 20-question micro-set only on that tag, then re-test 10 mixed.",
            "why": "Random re-reading is comfort; tagged micro-drills change the score.",
        },
    ],
)

path.write_text(json.dumps(L, indent=2, ensure_ascii=False), encoding="utf-8")
print("OK lessons", len(L))
for k in ["general_axioms", "general_count", "uni_normal", "multi_joint", "multi_cov", "final"]:
    print(k, "sections", len(L[k]["sections"]), "min", L[k]["minutes"])

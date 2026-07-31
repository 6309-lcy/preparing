"""
Rewrite Learn modules as textbook-style readings with KaTeX math.

Each chapter/lesson gets distinct, detailed concept sections:
definitions, formulas, derivations, intuition — not exam-weight blurbs.

Run: python tools/write_textbook_readings.py
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "app" / "data"


def T(sid, title, body):
    return {"id": sid, "type": "textbook", "title": title, "body": body}


def E(sid, title, setup, solution, why):
    return {
        "id": sid,
        "type": "example",
        "title": title,
        "setup": setup,
        "solution": solution,
        "why": why,
    }


def C(sid, title, prompt, choices, answer, explain):
    return {
        "id": sid,
        "type": "check",
        "title": title,
        "prompt": prompt,
        "choices": choices,
        "answer": answer,
        "explain": explain,
    }


def L(lid, title, minutes, lo, sections):
    return {
        "id": lid,
        "title": title,
        "minutes": minutes,
        "lo": lo if isinstance(lo, list) else [lo],
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# EXAM P — textbook readings (one per chapter module)
# ---------------------------------------------------------------------------

P_TEXTBOOK = {
    "setup": L(
        "setup",
        "How probability models work on Exam P",
        35,
        ["all"],
        [
            T(
                "t1",
                "What you are really computing",
                r"""Exam P is not “memorize a list of named distributions.” Almost every item is:

1. Define a sample space or a random variable $X$ that matches the story.
2. Write the event of interest as a set involving $X$ (or several variables).
3. Compute a probability or expectation using the correct tool (counting, axioms, PMF/PDF, conditioning, joint, transform).

A random variable is a function from outcomes to real numbers. Once $X$ is defined, “the insurer pays…” becomes something like $Y=(X-d)_+$ and you compute $E[Y]$ — not a vague English sentence.""",
            ),
            T(
                "t2",
                "Probability as a set function",
                r"""A probability measure $P$ on events satisfies:

$$P(A)\ge 0,\quad P(S)=1,\quad A\cap B=\emptyset \Rightarrow P(A\cup B)=P(A)+P(B).$$

From these:

$$P(A^c)=1-P(A),\qquad P(A\cup B)=P(A)+P(B)-P(A\cap B).$$

When outcomes are equally likely, the classical model is $P(A)=\#A/\#S$. Use it only when the symmetry is justified.""",
            ),
            E(
                "e1",
                "Define the RV first",
                r"""A policy has ordinary deductible $100$. Loss is $X$. What should you compute for expected insurer payment?""",
                r"""Define $Y=(X-100)_+=\max(X-100,0)$. The exam wants $E[Y]$, often via
$$E[Y]=E[X]-E[X\wedge 100]$$
or by integrating the survival function of $X$ above $100$.""",
                r"""Wrong RV $\Rightarrow$ wrong integral. Setup errors dominate arithmetic errors.""",
            ),
            C(
                "c1",
                "Core object",
                r"""On Exam P, after reading a word problem, the best first move is usually:""",
                {
                    "A": "Guess a normal approximation immediately",
                    "B": "Define the random variable / event precisely",
                    "C": "Ignore deductibles",
                    "D": "Only count sample size",
                },
                "B",
                r"""Everything else is mechanical once $X$ and the event are correct.""",
            ),
        ],
    ),
    "general_sets": L(
        "general_sets",
        "Sets, events, and Venn probability",
        50,
        ["P1a"],
        [
            T(
                "t1",
                "Sample space and events",
                r"""A random experiment has a sample space $S$ (all possible outcomes). An event $A$ is a subset of $S$.

Set operations:

- Union $A\cup B$: $A$ or $B$ or both
- Intersection $A\cap B$: both
- Complement $A^c$: not $A$
- Difference $A\setminus B=A\cap B^c$

Events $A$ and $B$ are mutually exclusive (disjoint) if $A\cap B=\emptyset$.""",
            ),
            T(
                "t2",
                "Inclusion–exclusion",
                r"""For two events:
$$P(A\cup B)=P(A)+P(B)-P(A\cap B).$$

For three events:
$$\begin{aligned}
P(A\cup B\cup C)
&=P(A)+P(B)+P(C)\\
&\quad -P(A\cap B)-P(A\cap C)-P(B\cap C)\\
&\quad +P(A\cap B\cap C).
\end{aligned}$$

“None of the three” is $1-P(A\cup B\cup C)$. “Exactly one” expands into three disjoint pieces.""",
            ),
            E(
                "e1",
                "Worked: none of three",
                r"""$P(G)=0.28$, $P(B)=0.29$, $P(S)=0.19$, pairwise intersections $0.14,0.12,0.10$, triple $0.08$. Find $P(\text{none})$.""",
                r"""$$P(G\cup B\cup S)=0.28+0.29+0.19-0.14-0.12-0.10+0.08=0.48.$$
$$P(\text{none})=1-0.48=0.52.$$""",
                r"""Complements turn “none” into one subtraction after a careful union.""",
            ),
            C(
                "c1",
                "Disjoint additivity",
                r"""If $A\cap B=\emptyset$, then $P(A\cup B)$ equals:""",
                {"A": "$P(A)P(B)$", "B": "$P(A)+P(B)$", "C": "$P(A)-P(B)$", "D": "$1-P(A\cap B)$"},
                "B",
                r"""Axiom of countable/finite additivity for disjoint events.""",
            ),
        ],
    ),
    "general_count": L(
        "general_count",
        "Counting: permutations and combinations",
        55,
        ["P1b"],
        [
            T(
                "t1",
                "Product rule",
                r"""If a procedure has stages with $n_1,n_2,\ldots$ options (and choices don’t interfere), the total number of outcomes is
$$n_1\cdot n_2\cdot n_3\cdots$$

With replacement, denominators stay fixed. Without replacement, they shrink.""",
            ),
            T(
                "t2",
                "Permutations vs combinations",
                r"""Order matters (rankings, passwords, assigning distinct roles):
$$P(n,k)=\frac{n!}{(n-k)!}=n(n-1)\cdots(n-k+1).$$

Order does not matter (committees, hands of cards, subsets):
$$C(n,k)=\binom{n}{k}=\frac{n!}{k!(n-k)!}.$$

Multinomial coefficient for splitting $n$ distinct objects into labeled groups of sizes $n_1,\ldots,n_r$ with $\sum n_i=n$:
$$\frac{n!}{n_1!\cdots n_r!}.$$""",
            ),
            E(
                "e1",
                "Worked: roles vs committee",
                r"""From 10 people: (a) choose a 3-person committee; (b) choose president, secretary, treasurer (distinct).""",
                r"""(a) $\binom{10}{3}=120$.

(b) $P(10,3)=10\cdot 9\cdot 8=720$.""",
                r"""Same people; order/roles change the count by a factor of $3!=6$.""",
            ),
            C(
                "c1",
                "Which tool?",
                r"""A 4-character password from 10 distinct symbols, no repeats. Use:""",
                {"A": r"$\binom{10}{4}$", "B": r"$P(10,4)$", "C": r"$10^4$ with no-repeat rule already", "D": r"$4!$"},
                "B",
                r"""Order matters and no repeats $\Rightarrow$ permutation.""",
            ),
        ],
    ),
    "general_axioms": L(
        "general_axioms",
        "Probability axioms and identities",
        50,
        ["P1a"],
        [
            T(
                "t1",
                "Derived identities",
                r"""From the axioms:
$$P(A^c)=1-P(A),\qquad A\subset B\Rightarrow P(A)\le P(B),$$
$$P(A)=P(A\cap B)+P(A\cap B^c).$$

Boole’s inequality: $P(\cup_i A_i)\le \sum_i P(A_i)$.

If $\{B_i\}$ partition $S$, then for any $A$:
$$P(A)=\sum_i P(A\cap B_i).$$""",
            ),
            T(
                "t2",
                "Exactly one of two events",
                r"""The event “exactly one of $A,B$” is the symmetric difference:
$$(A\cap B^c)\cup (A^c\cap B).$$

Its probability is
$$P(A)+P(B)-2P(A\cap B).$$""",
            ),
            E(
                "e1",
                "Worked: isolate $P(A)$",
                r"""$P(A\cup B)=0.7$ and $P(A\cup B^c)=0.9$. Find $P(A)$.""",
                r"""Adding: $P(A\cup B)+P(A\cup B^c)=P(A)+1$, because $B$ and $B^c$ partition.
So $0.7+0.9=P(A)+1\Rightarrow P(A)=0.6$.""",
                r"""Partition tricks avoid drawing a messy Venn by hand.""",
            ),
            C(
                "c1",
                "At least one",
                r"""$P(\text{at least one of }A,B)$ is best rewritten as:""",
                {
                    "A": r"$P(A)P(B)$",
                    "B": r"$1-P(A^c\cap B^c)$",
                    "C": r"$P(A)-P(B)$",
                    "D": r"$P(A\cap B)$ only",
                },
                "B",
                r"""At least one $=$ complement of neither.""",
            ),
        ],
    ),
    "general_cond": L(
        "general_cond",
        "Conditional probability",
        55,
        ["P1f"],
        [
            T(
                "t1",
                "Definition",
                r"""If $P(B)>0$,
$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}.$$

Intuition: restrict the sample space to $B$ and renormalize.

Multiplication rule:
$$P(A\cap B)=P(B)\,P(A\mid B)=P(A)\,P(B\mid A).$$

For a chain:
$$P(A_1\cap A_2\cap A_3)=P(A_1)\,P(A_2\mid A_1)\,P(A_3\mid A_1\cap A_2).$$""",
            ),
            T(
                "t2",
                "Tree diagrams",
                r"""Multi-stage experiments (draw without replacement, disease then test, machine type then defect) are organized with probability trees:

- Branch probabilities are conditional on the path so far.
- A leaf probability is the product along the path.
- An event’s probability sums the leaves in that event.""",
            ),
            E(
                "e1",
                "Worked: restrict the denominator",
                r"""937 men; 210 heart deaths; 312 had a parent with heart disease, of whom 102 died of heart disease. Find $P(\text{heart death}\mid \text{no parent heart disease})$.""",
                r"""No-parent group: $937-312=625$.

Heart deaths there: $210-102=108$.

$$P=\frac{108}{625}=0.1728.$$""",
                r"""“Given that” means: only count inside the conditioning set.""",
            ),
            C(
                "c1",
                "Multiplication",
                r"""$P(A\cap B)$ always equals:""",
                {
                    "A": r"$P(A)+P(B)$",
                    "B": r"$P(A)\,P(B\mid A)$ when defined",
                    "C": r"$P(A\mid B)$ only",
                    "D": r"$1-P(A\cup B)$",
                },
                "B",
                r"""Definition rearranged (when $P(A)>0$).""",
            ),
        ],
    ),
    "general_bayes": L(
        "general_bayes",
        "Total probability and Bayes’ theorem",
        55,
        ["P1g"],
        [
            T(
                "t1",
                "Law of total probability",
                r"""If $\{B_i\}_{i=1}^n$ partition $S$ with $P(B_i)>0$, then for any event $A$:
$$P(A)=\sum_{i=1}^n P(A\mid B_i)\,P(B_i).$$

This is the engine behind “mixture” and “risk class” problems.""",
            ),
            T(
                "t2",
                "Bayes’ theorem",
                r"""Posterior probability of a class given data:
$$P(B_j\mid A)=\frac{P(A\mid B_j)\,P(B_j)}{\sum_i P(A\mid B_i)\,P(B_i)}=\frac{P(A\mid B_j)\,P(B_j)}{P(A)}.$$

Language:

- Prior: $P(B_j)$
- Likelihood: $P(A\mid B_j)$
- Posterior: $P(B_j\mid A)$

Screening tests: false positive/negative rates are likelihoods; disease prevalence is the prior.""",
            ),
            E(
                "e1",
                "Worked: screening",
                r"""Disease prevalence $1\%$. Test sensitivity $P(+|D)=0.99$, false positive $P(+|D^c)=0.02$. Find $P(D\mid +)$.""",
                r"""$$P(+)=0.99\cdot 0.01+0.02\cdot 0.99=0.0099+0.0198=0.0297.$$
$$P(D\mid +)=\frac{0.0099}{0.0297}\approx 0.333.$$""",
                r"""Even a “good” test can have modest PPV when the disease is rare.""",
            ),
            C(
                "c1",
                "Bayes structure",
                r"""Bayes updates:""",
                {
                    "A": "Likelihoods into priors only",
                    "B": "Priors into posteriors using likelihoods and $P(A)$",
                    "C": "Only unconditional probabilities",
                    "D": "Variance into means",
                },
                "B",
                r"""Posterior $\propto$ likelihood $\times$ prior, normalized by $P(A)$.""",
            ),
        ],
    ),
    "general_indep": L(
        "general_indep",
        "Independence",
        45,
        ["P1c"],
        [
            T(
                "t1",
                "Definition",
                r"""Events $A,B$ are independent if
$$P(A\cap B)=P(A)\,P(B).$$

Equivalent (when defined): $P(A\mid B)=P(A)$ and $P(B\mid A)=P(B)$.

Mutually exclusive with $P(A),P(B)>0$ implies dependence (except degenerate cases): if $A\cap B=\emptyset$ then $P(A\cap B)=0\neq P(A)P(B)$.

Pairwise independence does not imply mutual independence of three events; mutual independence needs all pairs and the triple product equalities.""",
            ),
            T(
                "t2",
                "Independent trials",
                r"""If trials are independent with success probability $p$, the number of successes in $n$ trials is binomial (next chapter). Independence lets you multiply path probabilities on a tree without “updating the urn.”""",
            ),
            C(
                "c1",
                "Exclusive vs independent",
                r"""If $A$ and $B$ are mutually exclusive and $P(A),P(B)>0$, then they are:""",
                {
                    "A": "Independent",
                    "B": "Dependent",
                    "C": "Always the whole space",
                    "D": "Complements always",
                },
                "B",
                r"""Intersection probability $0$ cannot equal a positive product.""",
            ),
        ],
    ),
    "uni_discrete_def": L(
        "uni_discrete_def",
        "Discrete RVs: PMF, CDF, expectation, variance",
        60,
        ["P2"],
        [
            T(
                "t1",
                "PMF and CDF",
                r"""A discrete random variable takes countable values $x$ with probability mass function
$$p_X(x)=P(X=x),\qquad \sum_x p_X(x)=1,\quad p_X(x)\ge 0.$$

The CDF is
$$F_X(x)=P(X\le x)=\sum_{t\le x} p_X(t).$$

Then $P(a<X\le b)=F(b)-F(a)$ (careful with open/closed endpoints on lattices).""",
            ),
            T(
                "t2",
                "Expectation and variance",
                r"""$$E[X]=\sum_x x\,p_X(x),\qquad E[g(X)]=\sum_x g(x)\,p_X(x).$$

Linearity always holds (no independence needed):
$$E[aX+bY]=aE[X]+bE[Y].$$

Variance:
$$\mathrm{Var}(X)=E[(X-E[X])^2]=E[X^2]-(E[X])^2,$$
$$\mathrm{Var}(aX+b)=a^2\mathrm{Var}(X).$$

Standard deviation $\mathrm{SD}(X)=\sqrt{\mathrm{Var}(X)}$.""",
            ),
            E(
                "e1",
                "Worked: from a PMF table",
                r"""$P(X=0)=0.2$, $P(X=1)=0.5$, $P(X=2)=0.3$. Find $E[X]$ and $\mathrm{Var}(X)$.""",
                r"""$$E[X]=0\cdot0.2+1\cdot0.5+2\cdot0.3=1.1.$$
$$E[X^2]=0+1\cdot0.5+4\cdot0.3=1.7.$$
$$\mathrm{Var}(X)=1.7-1.1^2=1.7-1.21=0.49.$$""",
                r"""Always compute $E[X^2]$ for variance; do not square $E[X]$ and stop.""",
            ),
            C(
                "c1",
                "Linearity",
                r"""Linearity of expectation requires:""",
                {
                    "A": "Independence always",
                    "B": "Nothing about independence — it always holds (when expectations exist)",
                    "C": "Identical distributions only",
                    "D": "Normality",
                },
                "B",
                r"""Linearity is general; independence is for products/variances of sums.""",
            ),
        ],
    ),
    "uni_binom_pois": L(
        "uni_binom_pois",
        "Binomial and Poisson",
        55,
        ["P2"],
        [
            T(
                "t1",
                "Binomial",
                r"""$X\sim \mathrm{Binomial}(n,p)$: number of successes in $n$ independent Bernoulli($p$) trials.
$$P(X=k)=\binom{n}{k} p^k (1-p)^{n-k},\quad k=0,1,\ldots,n.$$
$$E[X]=np,\qquad \mathrm{Var}(X)=np(1-p).$$""",
            ),
            T(
                "t2",
                "Poisson",
                r"""$X\sim \mathrm{Poisson}(\lambda)$:
$$P(X=k)=e^{-\lambda}\frac{\lambda^k}{k!},\quad k=0,1,2,\ldots$$
$$E[X]=\mathrm{Var}(X)=\lambda.$$

Poisson limit: if $n$ large, $p$ small, $np\to\lambda$, then $\mathrm{Binomial}(n,p)\approx\mathrm{Poisson}(\lambda)$.

Sum of independent Poissons is Poisson with summed rates.""",
            ),
            E(
                "e1",
                "Worked: Poisson probability",
                r"""Claims $\sim\mathrm{Poisson}(3)$. $P(X=0)$ and $P(X\ge 1)$.""",
                r"""$$P(X=0)=e^{-3},\qquad P(X\ge 1)=1-e^{-3}.$$""",
                r"""Use the complement for “at least one.”""",
            ),
            C(
                "c1",
                "Means",
                r"""If $X\sim\mathrm{Binomial}(10,0.3)$, then $E[X]=$""",
                {"A": "3", "B": "2.1", "C": "7", "D": "0.3"},
                "A",
                r"""$np=10\cdot0.3=3$.""",
            ),
        ],
    ),
    "uni_other_disc": L(
        "uni_other_disc",
        "Geometric, negative binomial, hypergeometric",
        50,
        ["P2"],
        [
            T(
                "t1",
                "Geometric and NB",
                r"""Geometric (trials until first success), support $k=1,2,\ldots$:
$$P(X=k)=(1-p)^{k-1}p,\quad E[X]=\frac{1}{p},\quad \mathrm{Var}(X)=\frac{1-p}{p^2}.$$

(Some texts count failures before first success — check the support!)

Negative binomial: trials until $r$ successes (or failures before $r$ successes). Means/variances scale with $r$ under the independent-trial model.""",
            ),
            T(
                "t2",
                "Hypergeometric",
                r"""Population $N$ with $K$ “success” items; draw $n$ without replacement. $X=$ number of successes in the draw:
$$P(X=k)=\frac{\binom{K}{k}\binom{N-K}{n-k}}{\binom{N}{n}}.$$
$$E[X]=n\cdot\frac{K}{N}.$$

Unlike binomial, draws are dependent; variance has a finite-population correction factor $(N-n)/(N-1)$.""",
            ),
            C(
                "c1",
                "With vs without replacement",
                r"""Hypergeometric is the without-replacement analogue of:""",
                {"A": "Normal", "B": "Binomial", "C": "Exponential", "D": "Uniform continuous"},
                "B",
                r"""Fixed number of draws, binary type, dependence from finite population.""",
            ),
        ],
    ),
    "uni_cont": L(
        "uni_cont",
        "Continuous RVs, PDF/CDF, Uniform",
        60,
        ["P2"],
        [
            T(
                "t1",
                "PDF and CDF",
                r"""A continuous RV has CDF $F$ absolutely continuous with density $f=F'$ (where it exists):
$$P(a\le X\le b)=\int_a^b f(x)\,dx,\qquad \int_{-\infty}^{\infty} f=1,\ f\ge 0.$$

Note $P(X=x)=0$ for each single $x$. Survival $S(x)=1-F(x)=P(X>x)$.

For nonnegative $X$,
$$E[X]=\int_0^{\infty} S(x)\,dx$$
(when the expectation exists).""",
            ),
            T(
                "t2",
                "Expectation and variance",
                r"""$$E[g(X)]=\int g(x)f(x)\,dx,\qquad E[X]=\int x f(x)\,dx,$$
$$\mathrm{Var}(X)=E[X^2]-(E[X])^2.$$

Uniform $X\sim U(a,b)$:
$$f(x)=\frac{1}{b-a}\ \text{on }(a,b),\quad E[X]=\frac{a+b}{2},\quad \mathrm{Var}(X)=\frac{(b-a)^2}{12}.$$""",
            ),
            E(
                "e1",
                "Worked: uniform probability",
                r"""$X\sim U(0,10)$. Find $P(3<X<7)$ and $E[X]$.""",
                r"""$$P=\frac{7-3}{10}=0.4,\qquad E[X]=5.$$""",
                r"""Length of interval over length of support.""",
            ),
            C(
                "c1",
                "Point masses",
                r"""For a continuous PDF model, $P(X=3)$ is:""",
                {"A": "$f(3)$", "B": "$0$", "C": "$F(3)$", "D": "$1$"},
                "B",
                r"""Continuous distributions put zero mass at points.""",
            ),
        ],
    ),
    "uni_normal": L(
        "uni_normal",
        "Normal distribution",
        55,
        ["P2e"],
        [
            T(
                "t1",
                "Density and standardization",
                r"""$X\sim N(\mu,\sigma^2)$ has density
$$f(x)=\frac{1}{\sigma\sqrt{2\pi}}\exp\Bigl(-\frac{(x-\mu)^2}{2\sigma^2}\Bigr).$$

Standard normal $Z\sim N(0,1)$ has CDF $\Phi$. Standardization:
$$Z=\frac{X-\mu}{\sigma}\sim N(0,1),$$
$$P(X\le x)=\Phi\Bigl(\frac{x-\mu}{\sigma}\Bigr).$$

Symmetry: $\Phi(-z)=1-\Phi(z)$.""",
            ),
            T(
                "t2",
                "Linear transforms and sums",
                r"""If $X\sim N(\mu,\sigma^2)$ then $aX+b\sim N(a\mu+b,a^2\sigma^2)$.

Independent normals: sum is normal with mean/variance summed. (Joint normality matters for general linear combinations — Exam P usually states independence.)""",
            ),
            E(
                "e1",
                "Worked: standardize",
                r"""$X\sim N(100,15^2)$. $P(X>130)$.""",
                r"""$$Z=\frac{130-100}{15}=2,\quad P(Z>2)=1-\Phi(2)\approx 0.0228.$$""",
                r"""Never integrate the normal PDF by hand on the exam — standardize + table/calculator.""",
            ),
            C(
                "c1",
                "Variance scaling",
                r"""If $X\sim N(2,3^2)$, then $\mathrm{Var}(4X+1)=$""",
                {"A": "12", "B": "36", "C": "144", "D": "13"},
                "C",
                r"""$16\cdot 9=144$.""",
            ),
        ],
    ),
    "uni_exp_gamma": L(
        "uni_exp_gamma",
        "Exponential, Gamma, Beta",
        55,
        ["P2"],
        [
            T(
                "t1",
                "Exponential",
                r"""One common parameterization: mean $\theta$, rate $\lambda=1/\theta$:
$$f(x)=\frac{1}{\theta}e^{-x/\theta},\ x>0,\qquad F(x)=1-e^{-x/\theta},$$
$$E[X]=\theta,\quad \mathrm{Var}(X)=\theta^2.$$

Memoryless: $P(X>s+t\mid X>s)=P(X>t)$. Consequently
$$E[(X-d)_+]=E[X]\,P(X>d)=\theta e^{-d/\theta}.$$""",
            ),
            T(
                "t2",
                "Gamma and Beta (exam level)",
                r"""Gamma (shape $\alpha$, scale $\theta$) generalizes exponential ($\alpha=1$). Mean $\alpha\theta$, variance $\alpha\theta^2$.

Beta is supported on $(0,1)$ and is useful for random proportions; density involves $x^{a-1}(1-x)^{b-1}$.

On Exam P you mostly need recognition, means/variances from tables, and exponential memoryless tricks.""",
            ),
            E(
                "e1",
                "Worked: memoryless payment",
                r"""$X\sim\mathrm{Exp}(\text{mean }1000)$, ordinary deductible $200$. $E[\text{payment per loss}]$?""",
                r"""$$E[(X-200)_+]=1000\cdot e^{-200/1000}=1000 e^{-0.2}.$$""",
                r"""Memoryless turns excess loss into survival times mean.""",
            ),
            C(
                "c1",
                "Memoryless",
                r"""Which continuous family is memoryless?""",
                {"A": "Normal", "B": "Uniform", "C": "Exponential", "D": "Beta"},
                "C",
                r"""The continuous memoryless law is exponential.""",
            ),
        ],
    ),
    "uni_insurance": L(
        "uni_insurance",
        "Insurance payment variables",
        60,
        ["P2c"],
        [
            T(
                "t1",
                "Ordinary deductible and limit",
                r"""Ground-up loss $X\ge 0$.

Ordinary deductible $d$: insurer payment per loss
$$Y=(X-d)_+=\max(X-d,0).$$

Policy limit $u$ on ground-up loss (no deductible): payment $X\wedge u=\min(X,u)$.

Common identity:
$$E[(X-d)_+]=E[X]-E[X\wedge d].$$

With both deductible $d$ and maximum covered loss $u>d$, payment is often
$$\min\bigl((X-d)_+,\ u-d\bigr)= (X\wedge u)-(X\wedge d).$$""",
            ),
            T(
                "t2",
                "Coinsurance and per-payment vs per-loss",
                r"""Coinsurance $\alpha\in(0,1)$: insurer pays fraction $\alpha$ of the loss (or of the excess), depending on wording.

Per-loss quantities average over all losses including those below deductible (payment $0$).

Per-payment quantities condition on $X>d$ (a payment occurs). Read the stem carefully: “per payment” vs “per loss.”""",
            ),
            E(
                "e1",
                "Worked: limited loss expectation",
                r"""Express $E[\min(X,1000)]$ using the survival function for continuous nonnegative $X$.""",
                r"""$$E[X\wedge 1000]=\int_0^{1000} S(x)\,dx.$$""",
                r"""Limited expected value integrates survival only up to the cap.""",
            ),
            C(
                "c1",
                "Ordinary deductible",
                r"""With ordinary deductible $d$ only, payment per loss is:""",
                {"A": r"$\min(X,d)$", "B": r"$\max(X-d,0)$", "C": r"$X+d$", "D": r"$X/d$"},
                "B",
                r"""Excess over $d$.""",
            ),
        ],
    ),
    "multi_joint": L(
        "multi_joint",
        "Joint, marginal, and conditional distributions",
        60,
        ["P3"],
        [
            T(
                "t1",
                "Discrete joints",
                r"""Joint PMF $p(x,y)=P(X=x,Y=y)$, $\sum_x\sum_y p(x,y)=1$.

Marginal of $X$:
$$p_X(x)=\sum_y p(x,y).$$

Conditional:
$$p(y\mid x)=\frac{p(x,y)}{p_X(x)}\quad (p_X(x)>0).$$

Independence: $p(x,y)=p_X(x)p_Y(y)$ for all $x,y$.""",
            ),
            T(
                "t2",
                "Continuous joints",
                r"""Joint PDF $f(x,y)\ge 0$ with $\iint f=1$.

$$f_X(x)=\int f(x,y)\,dy,\qquad f(y\mid x)=\frac{f(x,y)}{f_X(x)}.$$

Independence: $f(x,y)=f_X(x)f_Y(y)$ on a rectangle support. Non-rectangular support (e.g. $0<x<y<1$) often forces dependence even if the formula “looks separable.”""",
            ),
            E(
                "e1",
                "Worked: marginal from a table",
                r"""$P(0,0)=0.1$, $P(0,1)=0.2$, $P(1,0)=0.3$, $P(1,1)=0.4$. Find $P(X=1)$ and $P(Y=0\mid X=1)$.""",
                r"""$$P(X=1)=0.3+0.4=0.7,\qquad P(Y=0\mid X=1)=\frac{0.3}{0.7}=\frac{3}{7}.$$""",
                r"""Marginals sum out the other variable; conditionals renormalize a slice.""",
            ),
            C(
                "c1",
                "Independence",
                r"""Discrete $X,Y$ independent means:""",
                {
                    "A": r"$p(x,y)=p_X(x)+p_Y(y)$",
                    "B": r"$p(x,y)=p_X(x)p_Y(y)$ for all $x,y$",
                    "C": r"$\mathrm{Cov}=1$",
                    "D": r"$X=Y$",
                },
                "B",
                r"""Factorization of the joint PMF.""",
            ),
        ],
    ),
    "multi_cov": L(
        "multi_cov",
        "Covariance, correlation, linear combinations",
        55,
        ["P3"],
        [
            T(
                "t1",
                "Covariance and correlation",
                r"""$$\mathrm{Cov}(X,Y)=E[XY]-E[X]E[Y],$$
$$\mathrm{Corr}(X,Y)=\frac{\mathrm{Cov}(X,Y)}{\mathrm{SD}(X)\mathrm{SD}(Y)}\in[-1,1].$$

Properties: bilinear, $\mathrm{Cov}(X,X)=\mathrm{Var}(X)$, $\mathrm{Cov}(X,c)=0$.

Independence $\Rightarrow$ $\mathrm{Cov}=0$ (uncorrelated). The converse is not always true in general.""",
            ),
            T(
                "t2",
                "Variance of linear combinations",
                r"""$$\mathrm{Var}(aX+bY)=a^2\mathrm{Var}X+b^2\mathrm{Var}Y+2ab\,\mathrm{Cov}(X,Y).$$

If uncorrelated (or independent), the cross term vanishes:
$$\mathrm{Var}(X+Y)=\mathrm{Var}X+\mathrm{Var}Y.$$""",
            ),
            E(
                "e1",
                "Worked: SD of a combo",
                r"""Independent $X,Y$ with $\mathrm{Var}X=4$, $\mathrm{Var}Y=9$. Find $\mathrm{SD}(X-2Y)$.""",
                r"""$$\mathrm{Var}(X-2Y)=4+4\cdot 9=40,\quad \mathrm{SD}=\sqrt{40}=2\sqrt{10}.$$""",
                r"""Coefficients square; independence drops covariance.""",
            ),
            C(
                "c1",
                "Expansion",
                r"""$\mathrm{Var}(2X-3Y)$ expands to:""",
                {
                    "A": r"$4\mathrm{Var}X+9\mathrm{Var}Y-12\mathrm{Cov}$",
                    "B": r"$4\mathrm{Var}X+9\mathrm{Var}Y+12\mathrm{Cov}$",
                    "C": r"$2\mathrm{Var}X-3\mathrm{Var}Y$",
                    "D": r"$\mathrm{Var}X+\mathrm{Var}Y$",
                },
                "A",
                r"""$a=2$, $b=-3$ $\Rightarrow$ $2ab=-12$.""",
            ),
        ],
    ),
    "multi_order_clt": L(
        "multi_order_clt",
        "Order statistics and the CLT",
        55,
        ["P3f"],
        [
            T(
                "t1",
                "Order statistics",
                r"""Given i.i.d. sample $X_1,\ldots,X_n$, the order statistics are
$$X_{(1)}\le X_{(2)}\le\cdots\le X_{(n)}.$$

For continuous i.i.d. with CDF $F$ and PDF $f$, the minimum and maximum have
$$P(X_{(n)}\le x)=[F(x)]^n,\qquad P(X_{(1)}>x)=[1-F(x)]^n.$$

Densities follow by differentiating those CDFs.""",
            ),
            T(
                "t2",
                "Central Limit Theorem",
                r"""If $X_i$ i.i.d. with mean $\mu$ and variance $\sigma^2\in(0,\infty)$, then for large $n$,
$$\bar X_n=\frac{1}{n}\sum_{i=1}^n X_i \approx N\Bigl(\mu,\frac{\sigma^2}{n}\Bigr),$$
equivalently
$$\frac{\sqrt{n}(\bar X_n-\mu)}{\sigma}\approx N(0,1).$$

Use continuity corrections carefully if approximating discrete sums (binomial) by normals.""",
            ),
            E(
                "e1",
                "Worked: CLT setup",
                r"""i.i.d. with $E[X_i]=2$, $\mathrm{Var}=4$, $n=100$. Approximate $P(\bar X>2.2)$.""",
                r"""$$\bar X\approx N(2,4/100)=N(2,0.04),\quad Z=\frac{2.2-2}{0.2}=1,$$
$$P\approx 1-\Phi(1).$$""",
                r"""Standardize with $\mathrm{SD}(\bar X)=\sigma/\sqrt{n}$.""",
            ),
            C(
                "c1",
                "CLT scale",
                r"""$\mathrm{Var}(\bar X_n)$ equals:""",
                {"A": r"$\sigma^2$", "B": r"$\sigma^2/n$", "C": r"$n\sigma^2$", "D": r"$\sigma/\sqrt{n}$"},
                "B",
                r"""Variance shrinks like $1/n$.""",
            ),
        ],
    ),
    "final": L(
        "final",
        "Final-week method (formulas, not new theory)",
        35,
        ["review"],
        [
            T(
                "t1",
                "Formula gate to rewrite from memory",
                r"""General: $P(A\mid B)$, total probability, Bayes.

Discrete/continuous: $E[X]$, $\mathrm{Var}(X)=E[X^2]-(E[X])^2$.

Named: binomial/Poisson/normal/exponential means and variances; $Z=(X-\mu)/\sigma$.

Insurance: $Y=(X-d)_+$, $E[X\wedge u]$, coinsurance.

Multivariate: marginals, $f(y\mid x)$, $\mathrm{Var}(aX+bY)$, CLT for $\bar X$.""",
            ),
            T(
                "t2",
                "Diagnosis loop",
                r"""After each mock: tag misses as setup / formula / arithmetic / misread. Micro-drill the top tag for 20 questions, then re-test mixed. No new Finan chapters in the last two weeks.""",
            ),
            C(
                "c1",
                "Last week",
                r"""Best use of final week time:""",
                {
                    "A": "Only brand-new exotic theory",
                    "B": "Timed practice + diagnose misses",
                    "C": "Passive videos only",
                    "D": "Ignore insurance",
                },
                "B",
                r"""Mocks and diagnosis raise scores under time pressure.""",
            ),
        ],
    ),
}


# ---------------------------------------------------------------------------
# EXAM FM — textbook readings
# ---------------------------------------------------------------------------

FM_TEXTBOOK = {
    "fm_setup": L(
        "fm_setup",
        "Financial mathematics: the objects of study",
        35,
        ["FM"],
        [
            T(
                "t1",
                "Cash flows and time value",
                r"""Financial mathematics prices sequences of payments. A dollar at time $t$ is not a dollar at time $0$.

The accumulation function $a(t)$ converts time-$0$ money to time $t$. The discount function $v(t)=1/a(t)$ converts time-$t$ money to time $0$.

Under compound interest at effective rate $i$ per year,
$$a(t)=(1+i)^t,\qquad v(t)=v^t=\Bigl(\frac{1}{1+i}\Bigr)^t.$$""",
            ),
            T(
                "t2",
                "What the symbols summarize",
                r"""Annuity symbols compress geometric series of discounted payments. Loan and bond formulas are present values of contractual cash flows at a yield rate. Duration measures sensitivity of that present value to the yield.""",
            ),
            C(
                "c1",
                "Core task",
                r"""Most FM problems ultimately compute:""",
                {
                    "A": "A present or accumulated value of cash flows at a given rate",
                    "B": "Only a probability density",
                    "C": "Only a life table $l_x$",
                    "D": "A GLM deviance",
                },
                "A",
                r"""FM is cash-flow valuation under interest theory.""",
            ),
        ],
    ),
    "fm_tvm_core": L(
        "fm_tvm_core",
        "Interest measures: $i$, $v$, $d$, $\\delta$, nominal rates",
        55,
        ["FM1"],
        [
            T(
                "t1",
                "Effective rate and discount",
                r"""Effective annual interest rate $i$: an investment of $1$ grows to $1+i$ in one year.

Discount factor and discount rate:
$$v=\frac{1}{1+i},\qquad d=\frac{i}{1+i}=1-v,\qquad i=\frac{d}{1-d}.$$

Simple interpretation: $d$ is the discount on a one-year loan of face $1$ repaid at year-end (interest paid up front).""",
            ),
            T(
                "t2",
                "Force of interest",
                r"""Constant force $\delta$ means continuous compounding:
$$a(t)=e^{\delta t},\qquad v^t=e^{-\delta t},\qquad \delta=\ln(1+i).$$

In general, the force is $\delta_t=a'(t)/a(t)$. Exam FM mostly uses constant $\delta$.""",
            ),
            T(
                "t3",
                "Nominal rates",
                r"""Nominal rate $i^{(m)}$ convertible $m$-thly means period rate $i^{(m)}/m$ with $m$ compoundings per year:
$$1+i=\Bigl(1+\frac{i^{(m)}}{m}\Bigr)^m,\qquad i^{(m)}=m\bigl[(1+i)^{1/m}-1\bigr].$$

Similarly for $d^{(m)}$:
$$1-d=\Bigl(1-\frac{d^{(m)}}{m}\Bigr)^m.$$""",
            ),
            E(
                "e1",
                "Worked: conversions",
                r"""$i=0.06$. Find $v$, $d$, and $\delta$.""",
                r"""$$v=\frac{1}{1.06},\quad d=\frac{0.06}{1.06},\quad \delta=\ln(1.06).$$""",
                r"""Store $i$ once; compute the chain $i\to v\to d\to\delta$.""",
            ),
            C(
                "c1",
                "Identity",
                r"""Which is always true?""",
                {"A": r"$d=i(1+i)$", "B": r"$v=1-d$", "C": r"$\delta=i/(1+i)$", "D": r"$i^{(m)}=mi$ always"},
                "B",
                r"""$v=1/(1+i)$ and $d=i/(1+i)$ imply $v=1-d$.""",
            ),
        ],
    ),
    "fm_accum": L(
        "fm_accum",
        "Accumulation and present value of single payments",
        50,
        ["FM1"],
        [
            T(
                "t1",
                "Moving one payment",
                r"""Present value at $0$ of $C$ due at time $t$:
$$\mathrm{PV}=C\,v^t=C(1+i)^{-t}.$$

Accumulated value at $T$ of $C$ invested at time $0$:
$$\mathrm{AV}=C(1+i)^T.$$

With nominal $i^{(m)}$, work in periods: rate $j=i^{(m)}/m$, number of periods $mt$.""",
            ),
            E(
                "e1",
                "Worked: fractional periods",
                r"""$100$ grows for $7.25$ years at $4\%$ convertible semiannually. Accumulated value?""",
                r"""$j=0.02$ per half-year, $k=14.5$ periods:
$$\mathrm{AV}=100(1.02)^{14.5}.$$""",
                r"""Count compounding periods, not years with the wrong rate.""",
            ),
            C(
                "c1",
                "PV factor",
                r"""At effective $i$, PV of $1$ due in $n$ years is:""",
                {"A": r"$(1+i)^n$", "B": r"$v^n$", "C": r"$d^n$", "D": r"$\delta^n$"},
                "B",
                r"""Discount with $v^n$.""",
            ),
        ],
    ),
    "fm_ann_level": L(
        "fm_ann_level",
        "Level annuities-immediate and due",
        60,
        ["FM2"],
        [
            T(
                "t1",
                "Annuity-immediate",
                r"""Payments of $1$ at the end of each year for $n$ years. Present value:
$$a_{\overline{n}|}=\sum_{k=1}^n v^k=v\frac{1-v^n}{1-v}=\frac{1-v^n}{i}.$$

Accumulated value at time $n$:
$$s_{\overline{n}|}=\sum_{k=0}^{n-1}(1+i)^k=\frac{(1+i)^n-1}{i}=(1+i)^n a_{\overline{n}|}.$$""",
            ),
            T(
                "t2",
                "Annuity-due",
                r"""Payments of $1$ at the beginning of each year for $n$ years:
$$\ddot a_{\overline{n}|}=\sum_{k=0}^{n-1} v^k=\frac{1-v^n}{d}=(1+i)a_{\overline{n}|}.$$

Perpetuity-immediate: $a_{\overline{\infty}|}=1/i$. Perpetuity-due: $1/d$.

If each payment is $X$ instead of $1$, multiply the annuity factor by $X$.""",
            ),
            E(
                "e1",
                "Worked: level payments",
                r"""End-of-year payments of $500$ for $10$ years, $i=6\%$. PV?""",
                r"""$$\mathrm{PV}=500\cdot a_{\overline{10}|}=500\cdot\frac{1-1.06^{-10}}{0.06}.$$""",
                r"""Factor payment size; use immediate form for end-of-year.""",
            ),
            C(
                "c1",
                "Due vs immediate",
                r"""$\ddot a_{\overline{n}|}$ equals:""",
                {
                    "A": r"$a_{\overline{n}|}/(1+i)$",
                    "B": r"$(1+i)a_{\overline{n}|}$",
                    "C": r"$a_{\overline{n}|}-1$",
                    "D": r"$i\cdot a_{\overline{n}|}$",
                },
                "B",
                r"""Due payments are each one period earlier.""",
            ),
        ],
    ),
    "fm_ann_mthly": L(
        "fm_ann_mthly",
        "m-thly and continuous annuities",
        55,
        ["FM2"],
        [
            T(
                "t1",
                "Payable $m$-thly",
                r"""Level payments totaling $1$ per year, paid $m$ times yearly ($1/m$ each payment), for $n$ years. Present value:
$$a_{\overline{n}|}^{(m)}=\frac{1-v^n}{i^{(m)}}.$$

The due form uses $d^{(m)}$ in the denominator.

Continuous payment at rate $1$ per year:
$$\bar a_{\overline{n}|}=\frac{1-v^n}{\delta}=\int_0^n v^t\,dt.$$""",
            ),
            T(
                "t2",
                "Period approach",
                r"""Equivalently: period rate $j=i^{(m)}/m$, $mn$ payments of $1/m$:
$$a_{\overline{n}|}^{(m)}=\frac{1}{m}\cdot a_{\overline{mn}|}^{(j)},$$
where the inner annuity uses rate $j$ per period. Stay consistent — do not mix symbols from different periodizations.""",
            ),
            C(
                "c1",
                "Continuous denominator",
                r"""$\bar a_{\overline{n}|}$ uses denominator:""",
                {"A": r"$i$", "B": r"$d$", "C": r"$\delta$", "D": r"$v$"},
                "C",
                r"""Continuous annuity: $(1-v^n)/\delta$.""",
            ),
        ],
    ),
    "fm_ann_vary": L(
        "fm_ann_vary",
        "Increasing, decreasing, and geometric annuities",
        55,
        ["FM2"],
        [
            T(
                "t1",
                "Arithmetic progression payments",
                r"""Payments $1,2,\ldots,n$ at year-ends (immediate increasing annuity):
$$(Ia)_{\overline{n}|}=\sum_{k=1}^n k v^k=\frac{\ddot a_{\overline{n}|}-n v^n}{i}.$$

Decreasing $n,n-1,\ldots,1$:
$$(Da)_{\overline{n}|}=\frac{n-a_{\overline{n}|}}{i}.$$

There are due and continuous analogues — match payment timing to the stem.""",
            ),
            T(
                "t2",
                "Geometric growth",
                r"""Payments grow by factor $(1+g)$ each period. Define $j$ by
$$1+j=\frac{1+i}{1+g}.$$

Then the PV is the first payment times an annuity-immediate at rate $j$ (with careful handling of the first payment’s timing). If $g=i$, special simplified forms appear.""",
            ),
            C(
                "c1",
                "Geometric rate",
                r"""Payments grow at $g$, interest $i$. Adjusted rate uses:""",
                {
                    "A": r"$i-g$ only always",
                    "B": r"$(1+i)/(1+g)-1$",
                    "C": r"$i+g$",
                    "D": r"$\delta-g$ always",
                },
                "B",
                r"""Standard substitution $1+j=(1+i)/(1+g)$.""",
            ),
        ],
    ),
    "fm_loans": L(
        "fm_loans",
        "Loans and amortization",
        60,
        ["FM3"],
        [
            T(
                "t1",
                "Level payment loan",
                r"""Loan principal $L$ repaid by $n$ level end-of-period payments $X$ at effective rate $i$ per period:
$$L=X\,a_{\overline{n}|}\qquad\Rightarrow\qquad X=\frac{L}{a_{\overline{n}|}}.$$

Outstanding balance after $k$ payments:

Prospective (remaining payments):
$$\mathrm{OB}_k=X\,a_{\overline{n-k}|}.$$

Retrospective (what has happened so far):
$$\mathrm{OB}_k=L(1+i)^k-X\,s_{\overline{k}|}.$$""",
            ),
            T(
                "t2",
                "Interest and principal split",
                r"""Just before payment $k$, balance is $\mathrm{OB}_{k-1}$. Then
$$I_k=i\cdot \mathrm{OB}_{k-1},\qquad PR_k=X-I_k,$$
and $\mathrm{OB}_k=\mathrm{OB}_{k-1}-PR_k$.""",
            ),
            E(
                "e1",
                "Worked: find $X$",
                r"""Loan $10{,}000$, $n=5$, $i=6\%$ annual, level end-of-year payments. Find $X$.""",
                r"""$$X=\frac{10000}{a_{\overline{5}|@6\%}}.$$""",
                r"""Always start from $L=Xa_{\overline{n}|}$ unless the stem says otherwise.""",
            ),
            C(
                "c1",
                "Prospective OB",
                r"""After $k$ level payments on an $n$-payment loan, $\mathrm{OB}$ equals $X$ times:""",
                {
                    "A": r"$a_{\overline{n}|}$",
                    "B": r"$a_{\overline{n-k}|}$",
                    "C": r"$s_{\overline{k}|}$",
                    "D": r"$v^k$",
                },
                "B",
                r"""Remaining annuity of $n-k$ payments.""",
            ),
        ],
    ),
    "fm_sinking": L(
        "fm_sinking",
        "Sinking fund loans",
        45,
        ["FM3"],
        [
            T(
                "t1",
                "Structure",
                r"""Borrower pays interest each period on the full principal $L$ at loan rate $i$, and separately deposits into a sinking fund earning rate $j$ that accumulates to $L$ at maturity.

Level sinking-fund deposit:
$$D=\frac{L}{s_{\overline{n}|@j}}.$$

Total periodic outlay $= Li + D$ (when interest is paid currently on full $L$). If $j\neq i$, only the SF uses $j$.""",
            ),
            C(
                "c1",
                "SF deposit",
                r"""To accumulate $L$ in $n$ periods at rate $j$ in a sinking fund, level deposit is:""",
                {
                    "A": r"$L/a_{\overline{n}|}$",
                    "B": r"$L/s_{\overline{n}|}$ at $j$",
                    "C": r"$L\cdot j$",
                    "D": r"$L v^n$",
                },
                "B",
                r"""Future-value annuity accumulates deposits to $L$.""",
            ),
        ],
    ),
    "fm_bonds": L(
        "fm_bonds",
        "Bond price, premium, and book value",
        60,
        ["FM4"],
        [
            T(
                "t1",
                "Price formula",
                r"""Per coupon period: face $F$, redemption amount $C$, coupon rate $r$ on face (coupon $Fr$ each period), $n$ coupons remaining, yield rate $i$ per coupon period:
$$P = Fr\cdot a_{\overline{n}|} + C v^n.$$

If $P>C$: premium bond. If $P<C$: discount. If coupon rate equals yield and $C=F$: par ($P=F$).""",
            ),
            T(
                "t2",
                "Book value",
                r"""Book value just after a coupon can be written prospectively with remaining coupons, or recursively
$$\mathrm{BV}_k=\mathrm{BV}_{k-1}(1+i)-\text{coupon}.$$

The premium/discount amortizes so book value tends to $C$ at redemption.""",
            ),
            E(
                "e1",
                "Worked: basic price",
                r"""Face $1000$, $10$ annual coupons at $5\%$, yield $6\%$, redeem at par. Price?""",
                r"""Coupon $=50$:
$$P=50\,a_{\overline{10}|@6\%}+1000\,v^{10}@6\%.$$""",
                r"""Split coupons (annuity) + redemption (single payment).""",
            ),
            C(
                "c1",
                "Premium",
                r"""A bond sells at a premium when:""",
                {
                    "A": "Price $<$ redemption",
                    "B": "Price $>$ redemption",
                    "C": "Coupon rate is zero",
                    "D": "$n=1$ always",
                },
                "B",
                r"""Premium means market price above redemption.""",
            ),
        ],
    ),
    "fm_duration": L(
        "fm_duration",
        "Duration, convexity, immunization",
        55,
        ["FM5"],
        [
            T(
                "t1",
                "Macaulay and modified duration",
                r"""For cash flows $c_t$ at times $t$ and price $P=\sum c_t v^t$ at effective period rate $i$:

Macaulay duration (time-weighted average of payment times):
$$\mathrm{MacD}=\frac{\sum t\,c_t v^t}{P}.$$

Modified duration:
$$\mathrm{ModD}=\frac{\mathrm{MacD}}{1+i}=-\frac{1}{P}\frac{dP}{di}.$$

Relative price change for a small yield shift:
$$\frac{\Delta P}{P}\approx -\mathrm{ModD}\cdot\Delta i.$$""",
            ),
            T(
                "t2",
                "Redington immunization",
                r"""To immunize liabilities with assets under small parallel yield shifts:

1. $\mathrm{PV}(A)=\mathrm{PV}(L)$
2. $\mathrm{MacD}(A)=\mathrm{MacD}(L)$ (or match modified durations)
3. Convexity of assets $\ge$ convexity of liabilities

Zero-coupon maturing at $n$ has $\mathrm{MacD}=n$. Coupon bonds have $\mathrm{MacD}<$ maturity.""",
            ),
            C(
                "c1",
                "Price sensitivity",
                r"""If yields rise slightly, bond prices:""",
                {
                    "A": r"Rise by about $\mathrm{ModD}\cdot\Delta i$",
                    "B": r"Fall by about $\mathrm{ModD}\cdot\Delta i$",
                    "C": "Do not change",
                    "D": "Double",
                },
                "B",
                r"""$dP/P\approx -\mathrm{ModD}\cdot\Delta i$.""",
            ),
        ],
    ),
    "fm_final": L(
        "fm_final",
        "FM wrap-up: formulas to own cold",
        35,
        ["FM"],
        [
            T(
                "t1",
                "Checklist",
                r"""Rewrite without notes:

- $v,d,\delta,i^{(m)}$ conversions
- $a_{\overline{n}|}$, $\ddot a_{\overline{n}|}$, $s_{\overline{n}|}$, $a^{(m)}$, $\bar a$
- $(Ia)$, $(Da)$, geometric $j$ with $1+j=(1+i)/(1+g)$
- Loan $X=L/a$, $\mathrm{OB}$ prospective/retrospective, $I_k$
- Bond $P=Fr a + Cv^n$, book value recursion
- $\mathrm{MacD}$, $\mathrm{ModD}$, Redington conditions""",
            ),
            C(
                "c1",
                "Final weeks",
                r"""Best use of last two weeks:""",
                {
                    "A": "Only new exotic derivatives",
                    "B": "Timed mixed sets + full mocks + wrong pool",
                    "C": "Passive videos only",
                    "D": "Skip bonds",
                },
                "B",
                r"""Mock-heavy wrap is intentional.""",
            ),
        ],
    ),
}

# legacy aliases used in some plans
FM_TEXTBOOK["fm_tvm"] = deepcopy(FM_TEXTBOOK["fm_tvm_core"])
FM_TEXTBOOK["fm_tvm"]["id"] = "fm_tvm"
FM_TEXTBOOK["fm_tvm"]["title"] = "TVM core (quick path module)"
FM_TEXTBOOK["fm_ann"] = deepcopy(FM_TEXTBOOK["fm_ann_level"])
FM_TEXTBOOK["fm_ann"]["id"] = "fm_ann"
FM_TEXTBOOK["fm_ann"]["title"] = "Level annuities (quick path module)"


# Key FAM / SRM formula chapters (same textbook standard)
EXTRA_TEXTBOOK = {
    "fam_lt_surv": L(
        "fam_lt_surv",
        "Survival models: $T_x$, $_tp_x$, life tables",
        60,
        ["FAM-LT"],
        [
            T(
                "t1",
                "Future lifetime",
                r"""Let $(x)$ denote a life aged $x$. The future lifetime is the continuous random variable $T_x$.

Survival and mortality probabilities:
$${}_t p_x = P(T_x > t),\qquad {}_t q_x = P(T_x \le t)=1-{}_t p_x.$$

Deferred mortality (dies between $t$ and $t+u$):
$${}_{t|u} q_x = {}_t p_x \cdot {}_u q_{x+t}.$$

Force of mortality $\mu_{x+t}$ satisfies, under standard smoothness,
$${}_t p_x = \exp\Bigl(-\int_0^t \mu_{x+s}\,ds\Bigr).$$""",
            ),
            T(
                "t2",
                "Life table functions",
                r"""A life table gives $l_x$ (survivors to age $x$ in a radix cohort). Then
$$d_x=l_x-l_{x+1},\qquad q_x=\frac{d_x}{l_x},\qquad p_x=1-q_x.$$

Multi-year survival chains: ${}_2 p_x = p_x\, p_{x+1}$.

Curate future lifetime $K_x=\lfloor T_x\rfloor$ underpins discrete insurance models paying at year-end.""",
            ),
            E(
                "e1",
                "Worked: two-year survival",
                r"""$p_x=0.99$, $p_{x+1}=0.98$. Find ${}_2 p_x$.""",
                r"""$${}_2 p_x = 0.99\cdot 0.98 = 0.9702.$$""",
                r"""Multiply successive one-year survivals.""",
            ),
            C(
                "c1",
                "Notation",
                r"""${}_t p_x$ is the probability that $(x)$:""",
                {
                    "A": "Dies within $t$ years",
                    "B": "Survives at least $t$ years",
                    "C": "Is age $t$ at issue",
                    "D": "Pays premium $t$",
                },
                "B",
                r"""$p$ is survival; $q$ is death.""",
            ),
        ],
    ),
    "fam_lt_ins": L(
        "fam_lt_ins",
        "Life insurance actuarial present values",
        60,
        ["FAM-LT"],
        [
            T(
                "t1",
                "Whole life insurance",
                r"""Discrete whole life insurance of $1$ on $(x)$, payable at the end of the year of death:
$$A_x = \sum_{k=0}^{\infty} v^{k+1}\,{}_{k|}q_x = \sum_{k=0}^{\infty} v^{k+1}\,{}_k p_x\, q_{x+k}.$$

Continuous whole life:
$$\bar A_x = \int_0^{\infty} v^t\,{}_t p_x\,\mu_{x+t}\,dt.$$

Under constant effective rate $i$ with $d=i/(1+i)$,
$$A_x = 1 - d\,\ddot a_x.$$""",
            ),
            T(
                "t2",
                "Term, pure endowment, endowment",
                r"""$n$-year pure endowment: pays $1$ at time $n$ if $(x)$ survives:
$$A_{x:\overline{n}|}^{\,1} = v^n\,{}_n p_x.$$

$n$-year term insurance pays only if death within $n$ years. Endowment insurance $=$ term $+$ pure endowment.""",
            ),
            C(
                "c1",
                "Identity",
                r"""$A_x = 1 - d\,\ddot a_x$ links:""",
                {
                    "A": "Loans to coupons",
                    "B": "Whole life insurance to life annuity-due",
                    "C": "Poisson to gamma",
                    "D": "PCA to $k$-means",
                },
                "B",
                r"""Classic discrete whole-life identity.""",
            ),
        ],
    ),
    "srm_glm": L(
        "srm_glm",
        "Generalized linear models: structure and interpretation",
        60,
        ["SRM2"],
        [
            T(
                "t1",
                "Three components",
                r"""A GLM specifies:

1. **Random component:** $Y$ has a distribution in the exponential family with mean $\mu=E[Y]$.
2. **Linear predictor:** $\eta = \mathbf{x}^\top\boldsymbol{\beta} = \beta_0+\beta_1 x_1+\cdots$.
3. **Link function:** $g(\mu)=\eta$, invertible, so $\mu=g^{-1}(\mathbf{x}^\top\boldsymbol{\beta})$.

Examples: normal + identity (classical linear model); Poisson + log; binomial + logit.""",
            ),
            T(
                "t2",
                "Interpreting coefficients",
                r"""**Log link** ($\log\mu=\eta$): a unit increase in $x_j$ multiplies $\mu$ by $e^{\beta_j}$:
$$\frac{\mu(x_j+1)}{\mu(x_j)}=e^{\beta_j}.$$

**Logit link** ($\log\frac{\mu}{1-\mu}=\eta$): $e^{\beta_j}$ is an odds ratio for a unit increase in $x_j$.

**Offset:** known exposure $t$ often enters as $\log t$ on the linear predictor for rates:
$$\log\mu = \log t + \mathbf{x}^\top\boldsymbol{\beta}.$$""",
            ),
            E(
                "e1",
                "Worked: log-link multiplier",
                r"""Poisson GLM, log link, $\beta_{\mathrm{age}}=0.02$. Effect of +1 year of age?""",
                r"""Mean multiplies by $e^{0.02}\approx 1.0202$ (about $+2\%$), holding other covariates fixed.""",
                r"""Never read log-link $\beta$ as an additive change on the mean scale.""",
            ),
            C(
                "c1",
                "Log link",
                r"""With log link, $\beta=0.2$ multiplies the mean by:""",
                {"A": "$0.2$", "B": r"$e^{0.2}$", "C": r"$\log 0.2$", "D": "$1.2$ without $e$ always"},
                "B",
                r"""$\mu\propto e^{\mathbf{x}^\top\boldsymbol{\beta}}$.""",
            ),
        ],
    ),
}


def merge_lessons():
    path = DATA / "lessons.json"
    lessons = json.loads(path.read_text(encoding="utf-8"))
    for k, v in P_TEXTBOOK.items():
        lessons[k] = v
    for k, v in FM_TEXTBOOK.items():
        lessons[k] = v
    for k, v in EXTRA_TEXTBOOK.items():
        lessons[k] = v
    path.write_text(json.dumps(lessons, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"Wrote textbook readings: P={len(P_TEXTBOOK)} FM={len(FM_TEXTBOOK)} extra={len(EXTRA_TEXTBOOK)}"
    )
    print(f"Total lessons in file: {len(lessons)}")


if __name__ == "__main__":
    merge_lessons()

# SOA Exam P + Early FM — Executable Study Plan

**Start:** Sunday, 12 July 2026  
**Target Exam P window:** 10–21 September 2026 (CBT)  
**Working target sitting:** **Monday 14 September 2026** (mid-window; shift ± a few days if needed)  
**Registration deadline (P):** **12 August 2026** — put this on your calendar now  
**Study load:** 2 hours Mon–Fri; longer active-recall / mock sessions on weekends  

### Daily driver app (Duolingo-style) — use this every day
| Item | Detail |
|---|---|
| **App folder** | `app/` (open via local server or GitHub Pages) |
| **How to run locally** | `cd C:\SOA\app` then `python -m http.server 8080` → http://localhost:8080 |
| **Phone + PC** | Deploy `app/` (or `docs/` copy) to **GitHub Pages** — one URL for both devices |
| **Daily goal** | Tick **readings** in the app + finish **~20 MC questions** (weekdays) |
| **Wrong answers** | Auto-saved to **Wrong pool**; reappear in future days (~30% of each session) |
| **Sunday** | Wrong tab → **Sunday recap → Grok** (similar drills + weakness diagnosis) |
| **Stuck on a Q** | Tap **Ask Grok** (opens official Grok with the question preloaded) |
| **Reminders** | Settings → Enable daily notifications (PWA / browser) |
| **Sync phone↔PC** | Settings → Export / Import progress JSON |

Full app docs: `app/README.md`. Rebuild bank after new SOA PDFs: `python tools/match_qa.py` then `python tools/build_question_bank.py`.

**Primary resource stack (you already have):**
| Resource | Path / use |
|---|---|
| **SOA Grind app** | `app/` — daily readings + MC + wrong pool + Grok |
| Official Exam P syllabus (Sept 2026) | `Books/2026-09-p-syllabus.pdf` |
| Official Exam FM syllabus (Oct 2026) | `Books/2026-10-exam-fm-syllabus.pdf` |
| Marcel Finan, *A Probability Course for the Actuaries* | `Books/Exam_P_Study_GuideFinan.pdf` |
| SOA Exam P sample questions + solutions | `Questions/edu-exam-p-sample-quest.pdf` + `edu-exam-p-sample-sol.pdf` |
| SOA Exam FM sample questions | `Questions/2018-10-exam-fm-sample-questions.pdf` |
| SOA “Risk and Insurance” note | Download free from SOA Exam P study page (required familiarity) |
| SOA Online Sample Exam P | soa.org (free CBT-style practice) |
| Normal table for Exam P | Download from SOA (available in exam under Exhibit) |

**Exam P syllabus backbone (weights):**
1. **General Probability — 23–30%**
2. **Univariate Random Variables — 44–50%** ← largest share of study time
3. **Multivariate Random Variables — 23–30%**

**Exam FM (light secondary until P is done):**
1. Time Value of Money — 5–15%
2. Annuities / non-contingent cash flows — 20–30%
3. Loans — 15–25%
4. Bonds — 15–25%
5. Portfolios / duration / immunization — 20–30%

---

## How to use this plan every day (do not skip)

### Standard weekday template (~2:00) — app-aligned
| Block | Time | What |
|---|---|---|
| A. Spaced recall | 15–20 min | App wrong-pool warm-up (auto-included) + blank-page formulas |
| B. New concept / reading | 40–50 min | Finan / syllabus section for the day → **tick readings in SOA Grind** |
| C. Exam-style MC | 50–60 min | **Complete today's app quiz goal (~20 Q)** — treat like CBT |
| D. Log / Grok | 5–10 min | On tough misses: **Ask Grok** button; wrong pool updates automatically |

### Standard weekend template (flexible length)
| Block | Time | What |
|---|---|---|
| Morning | 90–150 min | App quiz in timed mindset (or full mock near the end of plan) |
| Break | — | Walk / meal |
| Afternoon | 60–90 min | **Diagnosis**: rework misses (already in Wrong pool); targeted drills |
| **Sunday extra** | 30–45 min | App → Wrong → **Sunday recap → Grok** → study the 12 similar questions Grok generates |
| Optional light FM | 30–45 min | Only if P energy is good (see Friday FM slots in app readings) |

### Scoring & weakness rules (keep it simple)
- After each practice block, mark each problem: **Got it / Guessed / Missed**.
- Anything **Guessed** or **Missed** goes into `weakness_log.csv` with the syllabus LO code (e.g. `P2c`, `P1g`).
- **Spaced revisit:** Day+1, Day+3, Day+7, Day+14 for each logged weakness.
- Goal accuracy bands (SOA samples, untimed then timed):
  - End of Phase 1: ~60%+ on general-prob samples
  - End of Phase 2: ~65–70% mixed P samples
  - Start of final week: consistently ~70%+ timed; aim for mid-70s+ on full mocks

### Calculator
- Exam P: any SOA-approved calculator (TI-30XS Multiview is common). Learn it early.
- Exam FM later: **BA II Plus** is strongly recommended (TVM, N, I/Y, PV, PMT, FV).

### Important notes for quant-finance backgrounds
You already know expectation, variance, distributions, and some stochastic thinking. **Exam P still fails people on:**
1. Insurance payment variables (deductible, limit, coinsurance, inflation) — practice heavily  
2. Careful conditional / Bayes wording  
3. Discrete multivariate / order statistics under exam time pressure  
4. Avoiding over-engineering — pick the right distribution fast and compute cleanly  

Do **not** dig into measure theory, SDEs, optimization, or coding for this plan.

---

## Phase overview

| Phase | Dates | Focus | P : FM |
|---|---|---|---|
| **0 — Setup** | 12 Jul (today) | Environment, syllabus map, baseline | Setup |
| **1 — Foundations** | 13 Jul – 26 Jul (2 wks) | General Probability (LO 1) | 100% P |
| **2 — Univariate core** | 27 Jul – 30 Aug (5 wks) | Univariate RVs (LO 2) + light FM Fridays | ~90% P / 10% FM |
| **3 — Multivariate + integrate** | 31 Aug – 7 Sep (1+ wks) | Multivariate (LO 3) + mixed review | ~95% P |
| **4 — Final week** | 8 Sep – 13 Sep | Full mocks + diagnosis only | 100% P |
| **Exam P** | **14 Sep 2026 (target)** | Sit exam in window 10–21 Sep | — |
| **5 — Transition** | 15 Sep – 28 Sep | Light P cool-down → FM primary | Shift to FM |

---

# PHASE 0 — Setup (Today, Sunday 12 July)

### Day 0 — Sunday 12 July (~1.5–2 h, light)

**Main topics:** Orientation only (no deep learning)

**Action items:**
1. **Read** Exam P syllabus pages on Learning Outcomes 1–3 end-to-end (20 min). Highlight the three weights.
2. **Skim** Finan Table of Contents; bookmark §1–12 (sets → independence), §13–28 (univariate), §29–40 (joint / CLT).
3. **Download / print:** SOA normal table; “Risk and Insurance” study note from SOA P study page.
4. **Create files** (if not already):
   - `weakness_log.csv`
   - `formula_sheet_P.md` (you build this as you go — do not copy a finished sheet on day 1)
5. **Baseline mini-quiz (untimed, 30–40 min):** Attempt SOA sample questions #1–10 **without studying**. Score honestly. This is diagnostic only — a low score is expected and useful.
6. **Calendar:** Block weekday 2-hour slots; mark **12 Aug registration deadline**; schedule Prometic appointment plan for mid-window (~14 Sep).
7. **Optional:** Install BA II Plus emulator app for future FM Fridays (or buy calculator).

**Active recall:** None yet — just log baseline score and which #s felt familiar vs alien.

**Resources:** `2026-09-p-syllabus.pdf`, SOA samples #1–10, Finan TOC.

---

# PHASE 1 — General Probability (23–30%)  
## 13–26 July 2026 · Foundations before distributions

> Syllabus LO 1a–1g: sets/axioms, combinatorics, independence, mutually exclusive, addition/multiplication, conditional probability, Bayes & total probability.

---

### Week 1 — Sets, counting, probability axioms

#### Day 1 — Monday 13 July (2 h)
- **Syllabus:** LO 1a — set functions, Venn diagrams, sample space, events, axioms of probability  
- **Study (55 min):** Finan §1–2 (sets, operations, Venn). Focus on union/intersection/complement and “mutually exclusive vs independent” language (independence comes later — just note the distinction).  
- **Practice (45 min):** Finan practice problems from §1–2 (pick 8–12). Write sample spaces for coin/die/card experiments.  
- **Recall (20 min):** Blank-page: define sample space, event, axiom list (non-negativity, normalization, countable additivity for disjoint events).  
- **Log:** Any confusion on set notation.

#### Day 2 — Tuesday 14 July (2 h)
- **Syllabus:** LO 1b — combinatorics (permutations & combinations)  
- **Study (50 min):** Finan §3–4 (fundamental counting, P and C).  
- **Practice (50 min):** 10–12 counting problems; mix “order matters / doesn’t.”  
- **Recall (20 min):** Derive \(P(n,k)\) and \(C(n,k)\) from first principles; one “bridge hands / committees” style problem closed-book.  
- **Resources:** Finan §3–4; later map to SOA samples that use counting.

#### Day 3 — Wednesday 15 July (2 h)
- **Syllabus:** LO 1b continued — indistinguishable objects, careful counting  
- **Study (45 min):** Finan §5.  
- **Practice (55 min):** Multinomial counting, stars-and-bars style if present, word/arrangement problems.  
- **Recall (20 min):** 5 rapid counting drills; list common traps (overcount, indistinguishability).  
- **Note:** Skip deep recreational combinatorics; stay exam-shaped.

#### Day 4 — Thursday 16 July (2 h)
- **Syllabus:** LO 1a, 1d, 1e — probability definition, properties, addition rules  
- **Study (50 min):** Finan §6–7 (axioms, properties, complements, inclusion-exclusion for 2–3 sets).  
- **Practice (50 min):** Venn probability problems; \(P(A\cup B)\); complements.  
- **Recall (20 min):** Prove \(P(A^c)=1-P(A)\) from axioms; state inclusion-exclusion.

#### Day 5 — Friday 17 July (2 h)
- **Syllabus:** LO 1b + 1e — probability via counting  
- **Study (40 min):** Finan §8.  
- **Practice (55 min):** Classical probability with cards/dice/urns (8–10 problems).  
- **Recall (20 min):** Spaced review Week 1 formulas.  
- **FM (optional 5 min only):** Confirm BA II Plus / syllabus skim — no real FM study yet.

#### Weekend 1 — Saturday 18 July (3–4 h)
- **Main:** Timed **General Probability set** — 12 SOA sample questions that look like sets/counting/basic rules (browse sample PDF and pick; ~90 min at ~7.5 min/Q).  
- **Diagnosis (60–75 min):** Full rework of misses; tag LO codes.  
- **Active recall (30 min):** Formula sheet start: axioms, \(C(n,k)\), inclusion-exclusion.  
- **No new heavy theory.**

#### Weekend 1 — Sunday 19 July (2.5–3.5 h)
- **Targeted review** of Week 1 weaknesses (60–90 min).  
- **Light preview** of conditional probability: Finan §9 first examples (45 min).  
- **Flashcard build** (30 min): 15 cards max.  
- **Rest** the remaining time — sustainability matters.

---

### Week 2 — Conditional probability, independence, Bayes

#### Day 6 — Monday 20 July (2 h)
- **Syllabus:** LO 1f — conditional probability  
- **Study (50 min):** Finan §9. Definition \(P(A|B)=P(A\cap B)/P(B)\); multiplication rule.  
- **Practice (50 min):** 8–10 conditional problems (tables, trees).  
- **Recall (20 min):** Draw one full probability tree from memory for a 2-stage experiment.

#### Day 7 — Tuesday 21 July (2 h)
- **Syllabus:** LO 1g — law of total probability  
- **Study (45 min):** Partition sample space; total probability formula (Finan §10 start).  
- **Practice (55 min):** Tree + partition problems (disease test style, insurance risk class style).  
- **Recall (20 min):** Write total probability for a 3-group partition closed-book.

#### Day 8 — Wednesday 22 July (2 h)
- **Syllabus:** LO 1g — Bayes’ theorem  
- **Study (45 min):** Finan §10 (Bayes / posterior).  
- **Practice (55 min):** 8 Bayes problems; always compute posterior and interpret.  
- **Recall (20 min):** One classic Bayes from scratch without formula sheet.

#### Day 9 — Thursday 23 July (2 h)
- **Syllabus:** LO 1c — independence; LO 1d — mutually exclusive  
- **Study (45 min):** Finan §11. Contrast independence \(P(A\cap B)=P(A)P(B)\) vs disjoint.  
- **Practice (50 min):** Mix independence checks + conditional given independence.  
- **Recall (25 min):** Spaced: Week 1 counting + Bayes one problem each.

#### Day 10 — Friday 24 July (2 h)
- **Syllabus:** LO 1a–1g mixed (Phase 1 capstone weekday)  
- **Study (25 min):** Re-read your own formula sheet only; fill gaps.  
- **Practice (70 min):** 10 mixed general-probability SOA samples (untimed but clean write-ups).  
- **Recall (25 min):** Blank-page dump of all LO 1 tools.  
- **FM intro (optional last 10 min):** Read FM syllabus Topic 1 learning outcomes only — no problems yet.

#### Weekend 2 — Saturday 25 July (3.5–4.5 h)
- **Mock A (mini):** 15 SOA general-probability-heavy questions, **timed 1:45** (≈7 min/Q).  
- **Diagnosis (90 min):** Error log by LO; rework all misses **twice**.  
- **Target:** ≥9/15 without notes. If below, plan extra Bayes/counting drills next week (still move on — univariate cannot wait forever).

#### Weekend 2 — Sunday 26 July (2.5–3 h)
- **Weakness clinic** on lowest LO from Mock A (90 min).  
- **Bridge to univariate:** Finan §13 skimming + definition of random variable (45 min).  
- **Update formula sheet.** Light rest.

**Phase 1 checkpoint:** You can compute conditional probabilities, run Bayes, and do standard counting probability without freezing. Univariate is next and is the exam’s center of gravity.

---

# PHASE 2 — Univariate Random Variables (44–50%)  
## 27 July – 30 August 2026 · Highest weight — do not rush

> Syllabus LO 2a–2f: RV / pdf / cdf; conditional; mean/moments/percentiles; variance/sd/CV; insurance payments (deductible, coinsurance, limit, inflation); E/Var of loss vs payment.

---

### Week 3 — Discrete RVs: definitions, E, Var, binomial & Poisson

#### Day 11 — Monday 27 July (2 h)
- **Syllabus:** LO 2a — discrete RV, PMF, CDF  
- **Study (50 min):** Finan §13–14.  
- **Practice (50 min):** Build PMF/CDF tables; \(P(X\le k)\), \(P(a<X\le b)\).  
- **Recall (20 min):** Define PMF vs CDF; properties of CDF.

#### Day 12 — Tuesday 28 July (2 h)
- **Syllabus:** LO 2c, 2d — expectation, variance for discrete  
- **Study (50 min):** Finan §15–17.  
- **Practice (50 min):** E[X], E[g(X)], Var via \(E[X^2]- (E[X])^2\).  
- **Recall (20 min):** Prove Var formula once; compute one full example closed-book.

#### Day 13 — Wednesday 29 July (2 h)
- **Syllabus:** LO 2a–2d — binomial (and multinomial awareness)  
- **Study (45 min):** Finan §18 (focus binomial; multinomial only lightly).  
- **Practice (55 min):** 8 binomial problems (including “at least / at most”).  
- **Recall (20 min):** State mean/var of Binomial; one computational problem.

#### Day 14 — Thursday 30 July (2 h)
- **Syllabus:** LO 2a–2d — Poisson  
- **Study (45 min):** Finan §19. Poisson as count process approximation intuition only (no deep process theory).  
- **Practice (55 min):** Poisson probs; rare-event story problems.  
- **Recall (20 min):** Mean=variance property; one SOA-style Poisson.

#### Day 15 — Friday 31 July (2 h)
- **P main (85 min):** Mixed binomial/Poisson SOA samples (6–8 Q).  
- **FM light (35 min) — Topic 1 start:** Simple vs compound interest; effective rate. Read FM LO 1a–1b terms. Do 3–4 basic accumulation problems from FM samples (early numbers).  
  - **Resources:** FM syllabus §1; FM sample Q on compound interest.  
- **Log both tracks.**

#### Weekend 3 — Saturday 1 August (3.5–4 h)
- **Timed set:** 12 discrete-RV questions (75–90 min).  
- **Diagnosis (75 min).**  
- **Spaced recall:** Bayes + binomial (30 min).

#### Weekend 3 — Sunday 2 August (2.5–3.5 h)
- **Weakness clinic** (60–90 min).  
- **Read SOA “Risk and Insurance” note** carefully (45–60 min) — vocabulary for later LO 2e–2f.  
- **Optional FM (30 min):** Nominal vs effective rates \(i^{(m)}\); convert \(i^{(12)}\leftrightarrow i\).

---

### Week 4 — Other discrete families + continuous foundations

#### Day 16 — Monday 3 August (2 h)
- **Syllabus:** LO 2 — geometric & negative binomial  
- **Study (50 min):** Finan §20.1–20.2. Clarify “number of trials vs failures” conventions (exam wording).  
- **Practice (50 min):** 8 problems; always state what \(X\) counts.  
- **Recall (20 min):** Mean/var formulas for both; one each closed-book.

#### Day 17 — Tuesday 4 August (2 h)
- **Syllabus:** LO 2 — hypergeometric + discrete uniform  
- **Study (45 min):** Finan §20.3 + discrete uniform notes.  
- **Practice (55 min):** Hypergeometric “without replacement”; contrast with binomial.  
- **Recall (20 min):** When to choose Hypergeometric vs Binomial.

#### Day 18 — Wednesday 5 August (2 h)
- **Syllabus:** LO 2a–2d mixed discrete  
- **Study (25 min):** Build **distribution summary table** (support, PMF, E, Var, when used).  
- **Practice (70 min):** 10 mixed discrete SOA samples.  
- **Recall (25 min):** From table, cover columns and recite.

#### Day 19 — Thursday 6 August (2 h)
- **Syllabus:** LO 2a — continuous RV, PDF, CDF  
- **Study (50 min):** Finan §21–22.  
- **Practice (50 min):** Integrate PDF → CDF; differentiate CDF → PDF; probabilities as areas.  
- **Recall (20 min):** Properties of PDF/CDF; one full CDF construction.

#### Day 20 — Friday 7 August (2 h)
- **P (80 min):** Finan §23 — continuous E[X], Var, percentiles, median, mode. Practice 6 problems.  
- **FM light (40 min):** Discount rate \(d\), discount factor \(v\), force of interest \(\delta\) (constant). Conversions among \(i, d, \delta, v\). 4 conversion drills.  
  - FM LO 1a–1c.

#### Weekend 4 — Saturday 8 August (4–5 h)
- **Half-mock #1:** 15 mixed Exam P questions (General + Discrete + intro continuous), **timed 1:45**.  
- **Diagnosis (90–120 min)** — serious error tagging.  
- **Update weakness_log;** schedule next week’s Day+1 reviews.

#### Weekend 4 — Sunday 9 August (2.5–3 h)
- **Rework half-mock misses only** (90 min).  
- **Continuous practice** Finan problems on E/Var (45 min).  
- **Admin (15 min):** Confirm **Exam P registration by 12 August**.

---

### Week 5 — Named continuous distributions (uniform, normal, exponential)

#### Day 21 — Monday 10 August (2 h)
- **Syllabus:** LO 2 — continuous uniform  
- **Study (40 min):** Finan §24.  
- **Practice (55 min):** Uniform on \([a,b]\); order stats later — not today.  
- **Recall (25 min):** Mean/var formulas; 2 quick problems.

#### Day 22 — Tuesday 11 August (2 h)
- **Syllabus:** LO 2 — normal distribution  
- **Study (50 min):** Finan §25. Standardization; use of normal table.  
- **Practice (50 min):** 8 normal probability / inverse problems with table.  
- **Recall (20 min):** Standardize \(X\sim N(\mu,\sigma^2)\) from memory.

#### Day 23 — Wednesday 12 August (2 h) ⚠️ **REGISTRATION DEADLINE**
- **Admin first (15 min):** **Register for Exam P** if not done. Schedule Prometric for ~14 Sep (or your chosen day in 10–21 Sep).  
- **Syllabus:** LO 2 — normal applications continued  
- **Practice (70 min):** Mixed normal + continuity-correction awareness only if samples use it; focus pure continuous normal.  
- **Recall (25 min):** Spaced discrete + normal.

#### Day 24 — Thursday 13 August (2 h)
- **Syllabus:** LO 2 — exponential  
- **Study (45 min):** Finan §26. Memoryless property (exam favorite).  
- **Practice (55 min):** Survival \(P(X>x)\); min of independents intuition later; 8 problems.  
- **Recall (20 min):** Derive mean of Exp(\(\lambda\)) once (or Exp with mean \(\theta\) — match your book’s parameterization carefully!).

#### Day 25 — Friday 14 August (2 h)
- **P (75 min):** Mixed uniform/normal/exponential SOA samples (7–8 Q).  
- **FM light (45 min):** Equations of value; timeline method; unknown time or unknown rate (use calculator). FM LO 1b, 1d. 5 problems.

#### Weekend 5 — Saturday 15 August (4–5 h)
- **Half-mock #2:** 18 questions mixed, **timed 2:10**.  
- **Diagnosis (90–120 min).**  
- **Focus metrics:** time per question; which distributions you mis-identify.

#### Weekend 5 — Sunday 16 August (2.5–3.5 h)
- **Weakness clinic** (90 min).  
- **Finan §27 start:** Gamma & Beta overview (45–60 min) — know PDF shape, relation Exp–Gamma, Beta on (0,1).  
- **Optional FM (30 min):** Level annuity-immediate \(a_{\overline{n}|}\) concept preview (definition only).

---

### Week 6 — Gamma/Beta, transformations, insurance payments (critical)

#### Day 26 — Monday 17 August (2 h)
- **Syllabus:** LO 2 — gamma & beta  
- **Study (50 min):** Finan §27. Parameterizations; \(\Gamma(\alpha)\) for integers.  
- **Practice (50 min):** 6–8 problems (E/Var and probabilities where integrable).  
- **Recall (20 min):** Relationships: Exp special case of Gamma; sum of i.i.d. Exp → Gamma.

#### Day 27 — Tuesday 18 August (2 h)
- **Syllabus:** LO 2a, 2c — function of a RV / transformation  
- **Study (50 min):** Finan §28 (CDF method mainly).  
- **Practice (50 min):** 6 transformation problems.  
- **Recall (20 min):** Outline CDF method steps closed-book.

#### Day 28 — Wednesday 19 August (2 h)
- **Syllabus:** LO 2e, 2f — **insurance payment models** (high ROI)  
- **Study (55 min):** Ordinary deductible, maximum payment, policy limit, coinsurance, inflation. Define loss \(X\) vs payment per loss / per payment. Use Risk and Insurance note + SOA sample wording.  
- **Practice (50 min):** 6 introductory insurance calculation problems from SOA samples (search keywords deductible/limit).  
- **Recall (15 min):** Write definitions:  
  - payment per loss with deductible \(d\): \((X-d)_+\)  
  - with limit \(u\): \(\min(X,u)\)  
  - combinations with coinsurance \(\alpha\)

#### Day 29 — Thursday 20 August (2 h)
- **Syllabus:** LO 2e–2f continued  
- **Practice-heavy (90 min):** 8–10 insurance SOA samples (E of payment, Var if asked, inflation adjustments).  
- **Recall (30 min):** One full “deductible + coinsurance + limit” expected payment from scratch.

#### Day 30 — Friday 21 August (2 h)
- **P (70 min):** Mixed continuous + insurance set (6–7 Q).  
- **FM light (50 min):** Annuity-immediate & annuity-due: \(a_{\overline{n}|}\), \(\ddot{a}_{\overline{n}|}\), \(s_{\overline{n}|}\), \(\ddot{s}_{\overline{n}|}\). Formulas + 5 calculator problems.  
  - FM LO 2a–2b (level finite annuities only).

#### Weekend 6 — Saturday 22 August (4.5–5.5 h)
- **First full-length practice exam simulation:** 30 questions, **3 hours**, exam conditions (no phone, only calculator + normal table).  
  - Source: SOA samples (assemble a balanced mix: ~8 gen prob, ~14 univariate, ~8 multivariate if you must use some not-yet-mastered multi — mark those separately)  
  - If multivariate not ready, use 30 from general+univariate only and note the limitation.  
- **After:** Do **not** deep-study new multi tonight. Light walk.

#### Weekend 6 — Sunday 23 August (3–4 h)
- **Full diagnosis of Saturday mock** (2–2.5 h): every miss → LO tag → correct solution written cleanly.  
- **Insurance + continuous weak spots** drills (60 min).  
- **FM optional (30 min):** Perpetuities \(a_{\infty}\), \(\ddot{a}_{\infty}\).

**Phase 2 mid-check:** Univariate accuracy should be climbing. Insurance problems should feel mechanical, not mysterious.

---

### Week 7 — Univariate mastery + start multivariate

#### Day 31 — Monday 24 August (2 h)
- **Syllabus:** LO 2 mixed mastery  
- **Practice (90 min):** 10 hard univariate SOA samples (include percentiles, CV, mode).  
- **Recall (30 min):** Distribution table speed quiz (10 min) + 2 insurance.

#### Day 32 — Tuesday 25 August (2 h)
- **Syllabus:** LO 2 mixed; LO 3 preview  
- **Practice (60 min):** Timed 8 Q univariate (60 min hard cap).  
- **Study (40 min):** Finan §29 — jointly distributed RVs (discrete focus). Joint PMF, joint CDF.

#### Day 33 — Wednesday 26 August (2 h)
- **Syllabus:** LO 3a, 3b — joint / marginal / conditional discrete  
- **Study (50 min):** Finan §29–30 (independence of RVs).  
- **Practice (50 min):** Marginal from joint; conditional PMF; independence check.  
- **Recall (20 min):** \(p_X(x)=\sum_y p(x,y)\); independence definition.

#### Day 34 — Thursday 27 August (2 h)
- **Syllabus:** LO 3c, 3d, 3e — moments, Var, covariance, correlation (discrete)  
- **Study (45 min):** Finan §35–36 (as needed for discrete).  
- **Practice (55 min):** E[X], E[Y], E[XY], Cov, \(\rho\).  
- **Recall (20 min):** \(\mathrm{Cov}(X,Y)=E[XY]-E[X]E[Y]\); \(\mathrm{Var}(aX+bY)\).

#### Day 35 — Friday 28 August (2 h)
- **P (75 min):** 7 joint-discrete problems.  
- **FM light (45 min):** Arithmetic & geometric increasing annuities — **formulas recognition + 3 problems only** (do not master fully yet). FM LO 2b non-level intro.

#### Weekend 7 — Saturday 29 August (4.5–5.5 h)
- **Full mock #2:** 30 Q / 3 h (better balance including joint discrete).  
- Exam conditions.

#### Weekend 7 — Sunday 30 August (3–4 h)
- **Diagnosis mock #2** (2–2.5 h).  
- **Univariate insurance weak drill** if still shaky (45 min).  
- **CLT preview read:** Finan §40 introduction (30 min).

---

# PHASE 3 — Multivariate completion + integrated P review  
## 31 August – 7 September 2026

> Syllabus LO 3f–3i: order statistics; linear combinations (esp. independent discrete & normal); moments of linear combos; Central Limit Theorem.

---

### Week 8 — Order stats, linear combinations, CLT, mixed review

#### Day 36 — Monday 31 August (2 h)
- **Syllabus:** LO 3g, 3h — sums / linear combinations of independent RVs  
- **Study (45 min):** Finan §31 (discrete + continuous normal cases).  
- **Practice (55 min):** Sum of independent Poissons, binomials (same p), normals.  
- **Recall (20 min):** Mean/var of \(aX+bY\) under independence.

#### Day 37 — Tuesday 1 September (2 h)
- **Syllabus:** LO 3f — order statistics  
- **Study (50 min):** Finan material on order stats / max/min of i.i.d. (also use notes if Finan thin). CDF of \(X_{(n)}\), \(X_{(1)}\).  
- **Practice (50 min):** 6 order-stat problems.  
- **Recall (20 min):** For i.i.d. continuous, CDF of max/min.

#### Day 38 — Wednesday 2 September (2 h)
- **Syllabus:** LO 3i — Central Limit Theorem  
- **Study (40 min):** Finan §40. Continuity correction only if samples need it.  
- **Practice (60 min):** 8 CLT approximation problems (means and sums).  
- **Recall (20 min):** Standardize \(\bar X\) correctly; when CLT applies.

#### Day 39 — Thursday 3 September (2 h)
- **Syllabus:** LO 3 mixed  
- **Practice (90 min):** 10 multivariate SOA samples (joint, cov, order, CLT).  
- **Recall (30 min):** Formula dump LO 3.

#### Day 40 — Friday 4 September (2 h)
- **P mixed (90 min):** 10 questions across LO 1–3, mild timer.  
- **FM light (30 min):** Only if energy allows — loan amortization vocabulary (principal, interest portion) 2 problems. Else pure rest after P.  
  - Keep FM secondary.

#### Weekend 8 — Saturday 5 September (5–6 h)
- **Full mock #3:** 30 Q / 3 h, strict exam conditions.  
- **Immediate rough score** only; full diagnosis Sunday if exhausted.

#### Weekend 8 — Sunday 6 September (3.5–4.5 h)
- **Deep diagnosis mock #3** (2.5 h).  
- **Build Final Week hit list:** top 5 weakness themes (e.g. “Bayes with 3 hypotheses”, “per-payment vs per-loss”, “order stats of exponential”).  
- **Light formula sheet polish** (45 min).  
- **No new topics** after today unless a hole is catastrophic.

#### Day 41 — Monday 7 September (2 h) — bridge into final week
- **Targeted drills only** on Final Week hit list (90 min).  
- **Logistics check (30 min):** Exam appointment, ID, calculator batteries, route to test center, normal table familiarity, exam rules.  
- **Sleep priority starts now.**

---

# PHASE 4 — Final 7 Days Before Exam P  
## 8–13 September 2026 · Mocks + diagnosis · almost no new learning

**Rules for this phase:**
- No new Finan chapters.
- No FM (pause completely).
- Every day = timed practice → diagnose → micro-drills on misses.
- Sleep ≥ 7.5 hours. Cut caffeine experiments. Light exercise OK.

#### Day 42 — Tuesday 8 September (2.5–3 h if possible)
- **Full mock #4** (30 Q / 3 h) — if you can only do 2 h weekday, do 20 Q timed in 2 h and treat as “pace trainer.” Prefer full mock if schedule allows (use early morning/evening).  
- **Short diagnosis log** (even 20 min): list miss themes.

#### Day 43 — Wednesday 9 September (2 h)
- **Diagnosis deep-dive** from Mock #4 (60 min).  
- **Targeted set:** 8 questions only on your #1 and #2 weakness themes (60 min).

#### Day 44 — Thursday 10 September (2 h)
- **Pace drill:** 10 questions in 70 minutes (exam pace).  
- **Review** (50 min) with emphasis on setup speed (define X, write formula, compute).

#### Day 45 — Friday 11 September (2 h)
- **Full mock #5** if energy OK (or 15 Q strict timed).  
- **Only review misses** — do not reopen whole syllabus.

#### Weekend 9 — Saturday 12 September (4–5 h)
- **Final full mock #6:** 30 Q / 3 h, absolute exam conditions.  
- **Diagnosis (60–90 min)** — calm, mechanical.

#### Weekend 9 — Sunday 13 September (2–2.5 h max)
- **Light day.**  
  - Rework 5 previously missed problems cleanly.  
  - Formula sheet skim (20 min).  
  - Pack bag / confirm appointment.  
  - **Stop studying by early evening.**  
- Confidence note: write 5 things you *can* do well.

---

# EXAM P — Target sitting

### Monday 14 September 2026 (or your scheduled day in 10–21 Sep)
- Morning: light walk; optional 2 easy confidence problems **max** — then stop.  
- Exam: 30 MCQ, 3 hours, CBT. Answer every question (unanswered = wrong).  
- After: unofficial pass/fail email ~1 hour. Regardless of result, take the rest of the day off.

---

# PHASE 5 — Transition & Early FM Primary  
## 15–28 September 2026 (and high-level beyond)

### Week of 15–19 September — decompress + FM foundation solidification

| Day | Focus | Time |
|---|---|---|
| **Tue 15 Sep** | Rest / optional 45 min FM: rebuild TVM (i, v, d, δ, equations of value). | ≤1.5 h |
| **Wed 16 Sep** | FM Topic 1 mastery practice: 10 FM sample TVM questions. | 2 h |
| **Thu 17 Sep** | Level annuities immediate/due, PV/FV, calculator fluency. | 2 h |
| **Fri 18 Sep** | Annuity problems mixed + perpetuities. | 2 h |
| **Sat 19 Sep** | Timed FM set (12–15 Q) on Topics 1–2 only + diagnosis. | 3–4 h |
| **Sun 20 Sep** | Light review; sketch full FM roadmap to your FM sitting. | 1.5–2 h |

### Week of 21–28 September — FM ramp

| Day | Focus |
|---|---|
| **Mon 21** | Arithmetic & geometric annuities (FM LO 2 non-level). |
| **Tue 22** | Loans: outstanding balance, prospective/retrospective, amortization. |
| **Wed 23** | Loans: refinancing, drop/balloon payments. |
| **Thu 24** | Bonds: price, book value, premium/discount (no between-coupon valuation). |
| **Fri 25** | Bonds: yield, callable bonds min yield. |
| **Sat 26** | Mixed FM mock Topics 1–4 (20 Q timed) + diagnosis. |
| **Sun 27** | Weakness clinic; optional duration preview (FM Topic 5). |
| **Mon 28** | Spot/forward rates intro OR continue bond weakness — based on log. |

### High-level FM plan after 28 September (primary focus)

Assume ~8–10 weeks of FM-primary study at the same 2 h weekday cadence (adjust to your actual FM window; October 2026 FM exists on SOA schedule — confirm exact dates when you register).

| FM block | Weeks | Topics | Weight |
|---|---|---|---|
| A | 1–2 | TVM polish + all annuities (level + non-level) | 25–45% combined |
| B | 3–4 | Loans deep + mixed annuity/loan problems | 15–25% |
| C | 5–6 | Bonds deep + callable | 15–25% |
| D | 7–8 | Duration, convexity, immunization, cash-flow matching, spot/forward (FM-24-17 study note §§1–4 required) | 20–30% |
| E | Final 7–10 days | Full FM mocks + diagnosis only | — |

**FM resources:** FM syllabus; FM sample questions PDF; BA II Plus; optional Broverman / Vaaler / Francis–Ruckman as in syllabus; required note **FM-24-17** (duration/convexity approximation).

**If you do not pass P:** Do not immediately jump full FM. Take 3–5 days rest, read the diagnostic, then a **4-week P repair plan** focused only on weak LO clusters, then re-sit next P window (November 2026). Keep FM at 0–1 light session per week max during P repair.

---

# Spaced repetition & weakness tracking (operating system)

### File: `weakness_log.csv`
```text
date,exam,lo_code,topic,problem_source,result,error_type,next_review,notes
2026-07-20,P,P1g,Bayes,SOA #xx,Missed,Inverted likelihood,2026-07-21;2026-07-23;2026-07-27,Forgot total prob in denom
```

**error_type vocabulary (pick one):** Concept / Formula / Arithmetic / Misread / Distribution-choice / Time-pressure / Calculator

### Weekly Sunday ritual (20 min)
1. Count misses by `lo_code`.  
2. Promote top 3 codes into next week’s Monday–Wednesday recall blocks.  
3. Archive items correctly recalled on Day+14.

### Formula sheet rules
- Build **yourself** in `formula_sheet_P.md`.  
- One page per major LO cluster.  
- If you cannot write a formula from memory Friday, it goes on next Monday’s recall block.

---

# Practical sustainability rules

1. **Missed a weekday?** Do not double to 4 hours next day. Do 2 hours + move unfinished practice to the weekend diagnosis block.  
2. **Energy crash:** Switch to active recall + 4 easy problems; protect sleep.  
3. **Quant rabbit holes:** If a problem needs more than ~12 minutes and is not teaching a syllabus LO, flag and move on.  
4. **Practice > passive reading** every single day after Week 1.  
5. **Insurance wording** and **Bayes** deserve disproportionate practice relative to how “easy” they look in textbooks.

---

# Suggested SOA sample usage (rough map)

| Phase | Use samples for |
|---|---|
| Phase 1 | General probability / counting / Bayes |
| Phase 2 | Discrete & continuous univariate; insurance keywords |
| Phase 3 | Joint, covariance, order stats, CLT |
| Phase 4 | Full mixed sets; online sample exam P |
| Phase 5 | FM samples Topic 1–2, then 3–5 |

You do **not** need to finish every sample question before the exam — you need **repeated correct performance** on representative ones under time pressure.

---

# Quick reference — Finan → Exam P LO

| Finan sections | Exam P LO |
|---|---|
| §1–2 Sets | 1a |
| §3–5 Counting | 1b |
| §6–8 Probability basics | 1a, 1d, 1e |
| §9–12 Conditional, Bayes, independence | 1c, 1f, 1g |
| §13–17 Discrete RV, E, Var | 2a–2d |
| §18–20 Named discrete | 2a–2d |
| §21–28 Continuous + transforms | 2a–2d |
| Insurance (SOA note + samples) | 2e–2f |
| §29–36 Joint, cond, cov (discrete emphasis) | 3a–3e, 3g–3h |
| Order statistics (Finan + notes) | 3f |
| §40 CLT | 3i |
| MGF §38 | Low priority (not emphasized on current P syllabus) — skip unless curiosity |

---

*Plan tailored for a quant-finance background, new to actuarial exams, P-first for September 2026, light FM overlap, 2 h weekdays.*

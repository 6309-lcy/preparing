/**
 * Exam P mock mode — official-style CBT simulation
 * 30 MCQ · 3 hours · flag/nav · no Grok · scaled score approx · answer guide
 */
(function (global) {
  "use strict";

  const EXAM_DURATION_MS = 3 * 60 * 60 * 1000; // 3 hours
  const EXAM_N = 30;
  // Syllabus-aligned targets (mid of published weight ranges)
  const DIST = { general: 8, univariate: 14, multivariate: 8 }; // 30
  const PASS_MARK_PCT = 71; // recent stable estimated % for scaled 6
  const PILOT_N = 3; // unscored pilots (practice approximation)

  let api = null;
  let tickTimer = null;

  function A() {
    if (!api) throw new Error("SOAExam not bound");
    return api;
  }

  function classifyCluster(q) {
    if (!q) return "general";
    if (q.cluster === "multivariate" || q.cluster === "univariate" || q.cluster === "general") {
      // refine multivariate/uni from topics + stem when tagged general
    }
    const topics = (q.topics || []).join(" ");
    const stem = q.stem || "";
    const blob = `${topics} ${stem} ${q.lo || ""}`.toLowerCase();
    if (
      /joint|covariance|correlation|order.?stat|central limit|\bclt\b|marginal|two random|independent random|linear combination/.test(
        blob
      ) ||
      q.cluster === "multivariate"
    )
      return "multivariate";
    if (
      /binomial|poisson|geometric|hypergeometric|negative binomial|exponential|gamma|beta|normal|uniform|density|deductible|coinsurance|policy limit|continuous|discrete|pmf|pdf|percentile|random variable/.test(
        blob
      ) ||
      q.cluster === "univariate" ||
      (q.lo || "").startsWith("P2")
    )
      return "univariate";
    return "general";
  }

  function seenPracticeIds(state) {
    const s = new Set(state.examUsedQuestionIds || []);
    (state.history || []).forEach((h) => s.add(h.id));
    Object.values(state.days || {}).forEach((d) => {
      Object.keys(d.answered || {}).forEach((id) => s.add(id));
    });
    return s;
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function pickForCluster(pool, n, seen, wrongSet, usedInExams) {
    const unused = pool.filter((q) => !usedInExams.has(q.id) && !seen.has(q.id));
    const unusedWrong = unused.filter((q) => wrongSet.has(q.id));
    const unusedFresh = unused.filter((q) => !wrongSet.has(q.id));
    const usedButNotExam = pool.filter((q) => !usedInExams.has(q.id) && seen.has(q.id));
    const examReuse = pool.filter((q) => usedInExams.has(q.id));

    const tiers = [
      shuffle(unusedWrong),
      shuffle(unusedFresh),
      shuffle(usedButNotExam),
      shuffle(examReuse),
    ];
    const out = [];
    const taken = new Set();
    for (const tier of tiers) {
      for (const q of tier) {
        if (out.length >= n) break;
        if (taken.has(q.id)) continue;
        out.push(q);
        taken.add(q.id);
      }
      if (out.length >= n) break;
    }
    return out;
  }

  function buildExamForm(questions, state) {
    const by = { general: [], univariate: [], multivariate: [] };
    questions.forEach((q) => {
      if (!q.answer) return;
      by[classifyCluster(q)].push(q);
    });

    const seen = seenPracticeIds(state);
    const wrongSet = new Set(Object.keys(state.wrongPool || {}));
    const usedInExams = new Set(state.examUsedQuestionIds || []);

    let picks = [];
    const need = { ...DIST };
    // primary draw
    for (const c of ["general", "univariate", "multivariate"]) {
      const got = pickForCluster(by[c], need[c], seen, wrongSet, usedInExams);
      picks = picks.concat(got);
      need[c] -= got.length;
    }
    // fill shortfall from largest remaining pools
    const short = Object.values(need).reduce((a, b) => a + b, 0);
    if (short > 0) {
      const have = new Set(picks.map((q) => q.id));
      const rest = shuffle(questions.filter((q) => q.answer && !have.has(q.id)));
      // prefer unused in exams
      rest.sort((a, b) => {
        const au = usedInExams.has(a.id) ? 1 : 0;
        const bu = usedInExams.has(b.id) ? 1 : 0;
        return au - bu;
      });
      for (const q of rest) {
        if (picks.length >= EXAM_N) break;
        picks.push(q);
      }
    }

    picks = shuffle(picks).slice(0, EXAM_N);
    const pilotIds = shuffle(picks.map((q) => q.id)).slice(0, Math.min(PILOT_N, picks.length));
    return {
      questionIds: picks.map((q) => q.id),
      pilotIds,
      distribution: {
        general: picks.filter((q) => classifyCluster(q) === "general").length,
        univariate: picks.filter((q) => classifyCluster(q) === "univariate").length,
        multivariate: picks.filter((q) => classifyCluster(q) === "multivariate").length,
      },
    };
  }

  /** Map percent correct → scaled 0–10 with ~71% ≈ 6 (practice approximation of IRT). */
  function scaledScoreFromPercent(pct) {
    const p = Math.max(0, Math.min(100, pct));
    let s;
    if (p <= PASS_MARK_PCT) s = (6 * p) / PASS_MARK_PCT;
    else s = 6 + (4 * (p - PASS_MARK_PCT)) / (100 - PASS_MARK_PCT);
    return Math.round(s * 10) / 10;
  }

  function ensureExamState(state) {
    if (!state.examUsedQuestionIds) state.examUsedQuestionIds = [];
    if (!state.examHistory) state.examHistory = [];
    if (state.activeExam === undefined) state.activeExam = null;
  }

  function startExam(regenerate) {
    const { state, questions, saveState, toast, showView } = A();
    ensureExamState(state);
    if (state.activeExam && state.activeExam.status === "in_progress" && !regenerate) {
      showView("exam");
      renderExam();
      return;
    }
    if (state.activeExam && state.activeExam.status === "in_progress" && regenerate) {
      if (!confirm("Abandon the in-progress exam and generate a new form?")) return;
    }

    const form = buildExamForm(questions, state);
    if (form.questionIds.length < EXAM_N) {
      toast(`Only ${form.questionIds.length} questions available — need ${EXAM_N}`);
    }
    const now = Date.now();
    state.activeExam = {
      id: `exam-${now}`,
      status: "in_progress",
      startedAt: now,
      endsAt: now + EXAM_DURATION_MS,
      durationMs: EXAM_DURATION_MS,
      questionIds: form.questionIds,
      pilotIds: form.pilotIds,
      distribution: form.distribution,
      answers: Object.fromEntries(form.questionIds.map((id) => [id, null])),
      flags: {},
      currentIndex: 0,
      passMarkPct: PASS_MARK_PCT,
    };
    // reserve these IDs so next regenerate prefers others
    form.questionIds.forEach((id) => {
      if (!state.examUsedQuestionIds.includes(id)) state.examUsedQuestionIds.push(id);
    });
    saveState({ immediate: true });
    toast("Exam started · 3:00:00 · Grok disabled");
    showView("exam");
    renderExam();
    startTicker();
  }

  function remainingMs(exam) {
    return Math.max(0, (exam.endsAt || 0) - Date.now());
  }

  function formatTime(ms) {
    const s = Math.floor(ms / 1000);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  }

  function startTicker() {
    stopTicker();
    tickTimer = setInterval(() => {
      const exam = A().state.activeExam;
      if (!exam || exam.status !== "in_progress") {
        stopTicker();
        return;
      }
      const el = document.getElementById("examTimer");
      const left = remainingMs(exam);
      if (el) {
        el.textContent = formatTime(left);
        el.classList.toggle("exam-timer-warn", left < 15 * 60 * 1000);
        el.classList.toggle("exam-timer-critical", left < 5 * 60 * 1000);
      }
      if (left <= 0) {
        stopTicker();
        submitExam(true);
      }
    }, 250);
  }

  function stopTicker() {
    if (tickTimer) clearInterval(tickTimer);
    tickTimer = null;
  }

  function submitExam(auto) {
    const { state, saveState, qById, toast, showView } = A();
    const exam = state.activeExam;
    if (!exam || exam.status !== "in_progress") return;
    if (!auto) {
      const unanswered = exam.questionIds.filter((id) => !exam.answers[id]).length;
      const msg =
        unanswered > 0
          ? `${unanswered} question(s) unanswered. Submit anyway? (Unanswered score as incorrect, like CBT.)`
          : "Submit exam for scoring? You cannot change answers after submit.";
      if (!confirm(msg)) return;
    }

    stopTicker();
    const scoredIds = exam.questionIds.filter((id) => !exam.pilotIds.includes(id));
    let correct = 0;
    const detail = exam.questionIds.map((id, i) => {
      const q = qById.get(id);
      const user = exam.answers[id];
      const key = q?.answer || null;
      const isPilot = exam.pilotIds.includes(id);
      const ok = !!(user && key && user === key);
      if (!isPilot && ok) correct++;
      return {
        index: i + 1,
        id,
        userAnswer: user,
        correctAnswer: key,
        correct: ok,
        pilot: isPilot,
        flagged: !!exam.flags[id],
        cluster: classifyCluster(q),
        stemPreview: (q?.stem || "").slice(0, 200),
        images: q?.images || [],
      };
    });

    const scoredN = scoredIds.length || 1;
    const pct = Math.round((100 * correct) / scoredN);
    const scaled = scaledScoreFromPercent(pct);
    const passed = scaled >= 6;

    const result = {
      id: exam.id,
      submittedAt: Date.now(),
      autoSubmitted: !!auto,
      startedAt: exam.startedAt,
      durationMs: exam.durationMs,
      timeUsedMs: Math.min(exam.durationMs, Date.now() - exam.startedAt),
      questionIds: exam.questionIds,
      pilotIds: exam.pilotIds,
      distribution: exam.distribution,
      detail,
      correct,
      scoredN,
      pct,
      scaled,
      passed,
      passMarkPct: PASS_MARK_PCT,
    };

    // Add misses to wrong pool (scored only)
    detail.forEach((d) => {
      if (d.pilot || d.correct || !d.userAnswer) return;
      const prev = state.wrongPool[d.id] || { count: 0 };
      state.wrongPool[d.id] = {
        count: (prev.count || 0) + 1,
        lastWrong: new Date().toISOString().slice(0, 10),
        topics: A().qById.get(d.id)?.topics || [],
        lo: A().qById.get(d.id)?.lo || "",
        stemPreview: d.stemPreview,
        number: A().qById.get(d.id)?.number,
        fromExam: true,
      };
    });

    state.examHistory = state.examHistory || [];
    state.examHistory.unshift(result);
    state.examHistory = state.examHistory.slice(0, 30);
    state.activeExam = { ...exam, status: "submitted", result };
    saveState({ immediate: true });
    toast(auto ? "Time expired — exam submitted" : "Exam submitted");
    showView("exam");
    renderExamResults(result);
  }

  function renderExamLobby() {
    const { state, escapeHtml } = A();
    ensureExamState(state);
    const hist = state.examHistory || [];
    const last = hist[0];
    const used = (state.examUsedQuestionIds || []).length;
    const root = document.getElementById("view-exam");
    if (!root) return;

    root.innerHTML = `
      <div class="card exam-lobby">
        <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          <div class="min-w-0 flex-1">
            <div class="inline-flex items-center gap-1.5 rounded-full bg-slate-900 text-white px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide">Exam mode</div>
            <h1 class="mt-3 text-2xl font-semibold tracking-tight">SOA Exam P · Mock CBT</h1>
            <p class="mt-2 text-sm text-mute leading-relaxed max-w-3xl">
              Official-style practice: <strong class="text-ink">30 multiple-choice</strong> questions,
              <strong class="text-ink">3 hours</strong>, five choices (A–E). A few items are treated as unscored
              <em>pilot</em> questions (like CBT). <strong class="text-ink">Grok is disabled</strong> during the exam.
            </p>
            <ul class="mt-4 space-y-2 text-sm text-slate-700">
              <li class="flex gap-2"><span class="text-brand font-bold">·</span> Flag questions and jump back anytime via the navigator</li>
              <li class="flex gap-2"><span class="text-brand font-bold">·</span> Topic mix targets syllabus weights (~8 general / 14 univariate / 8 multivariate)</li>
              <li class="flex gap-2"><span class="text-brand font-bold">·</span> Prefers questions you have not seen in daily practice or prior mocks; may include wrong-pool items</li>
              <li class="flex gap-2"><span class="text-brand font-bold">·</span> Scoring: practice scaled score 0–10 (pass ≥ 6). Recent published pass mark ~${PASS_MARK_PCT}% → scaled 6 (IRT approximation)</li>
            </ul>
            <p class="mt-3 text-xs text-mute">${used} unique questions used in past mocks · ${hist.length} exam(s) on record</p>
          </div>
          <div class="shrink-0 w-full lg:w-72 space-y-3">
            <button type="button" class="btn-primary w-full" id="btnStartExam">
              ${state.activeExam?.status === "in_progress" ? "Resume exam" : "Start new mock exam"}
            </button>
            <button type="button" class="btn-secondary w-full" id="btnRegenExam">Generate new form</button>
            ${
              last
                ? `<button type="button" class="btn-ghost w-full" id="btnLastGuide">View last answer guide</button>
                   <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm">
                     <div class="font-semibold">Last result</div>
                     <div class="mt-1 text-mute">Scaled ${last.scaled}/10 · ${last.pct}% · ${last.passed ? "Pass" : "Below pass"}</div>
                   </div>`
                : ""
            }
          </div>
        </div>
      </div>
      <div class="card">
        <h2 class="text-sm font-semibold">Scoring note (practice)</h2>
        <p class="mt-2 text-sm text-mute leading-relaxed">
          The real Exam P uses Item Response Theory (IRT); difficulty varies by form. This mock converts percent correct
          on scored items to a <strong class="text-ink">scaled 0–10</strong> with pass at <strong class="text-ink">6</strong>,
          calibrated so ~${PASS_MARK_PCT}% ≈ 6 (aligned with recent published pass-mark estimates). It is a study aid, not an official result.
        </p>
      </div>`;

    document.getElementById("btnStartExam").onclick = () => startExam(false);
    document.getElementById("btnRegenExam").onclick = () => startExam(true);
    document.getElementById("btnLastGuide")?.addEventListener("click", () => {
      if (last) renderExamResults(last);
    });
    A().refreshIcons?.();
  }

  function renderExam() {
    const { state, qById, escapeHtml, refreshIcons } = A();
    const exam = state.activeExam;
    const root = document.getElementById("view-exam");
    if (!root) return;

    if (!exam) {
      renderExamLobby();
      return;
    }
    if (exam.status === "submitted" && exam.result) {
      renderExamResults(exam.result);
      return;
    }
    if (exam.status !== "in_progress") {
      renderExamLobby();
      return;
    }

    startTicker();
    const idx = exam.currentIndex || 0;
    const qid = exam.questionIds[idx];
    const q = qById.get(qid);
    const left = remainingMs(exam);
    const answeredN = exam.questionIds.filter((id) => exam.answers[id]).length;
    const flaggedN = Object.values(exam.flags || {}).filter(Boolean).length;
    const isPilot = exam.pilotIds.includes(qid);

    const nav = exam.questionIds
      .map((id, i) => {
        let cls = "exam-nav-item";
        if (i === idx) cls += " current";
        if (exam.answers[id]) cls += " answered";
        if (exam.flags[id]) cls += " flagged";
        return `<button type="button" class="${cls}" data-ei="${i}" title="Q${i + 1}">${i + 1}</button>`;
      })
      .join("");

    const imgs =
      q?.images?.length > 0
        ? `<div class="q-images exam-qimg">
            ${q.images.map((src) => `<img src="./${src}?v=exam" alt="Q${idx + 1}" data-full="./${src}?v=exam" />`).join("")}
           </div>`
        : `<div class="quiz-stem">${escapeHtml(q?.stem || "Question unavailable")}</div>`;

    root.innerHTML = `
      <div class="exam-shell">
        <div class="exam-topbar">
          <div class="flex items-center gap-3 min-w-0">
            <span class="exam-badge">CBT · Exam P Mock</span>
            <span class="text-sm text-mute hidden sm:inline">Q ${idx + 1} / ${exam.questionIds.length}</span>
            ${isPilot ? `<span class="text-xs font-medium text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5">Pilot (unscored)</span>` : ""}
          </div>
          <div class="flex items-center gap-3">
            <div class="text-xs text-mute tabular-nums">${answeredN} answered · ${flaggedN} flagged</div>
            <div id="examTimer" class="exam-timer ${left < 15 * 60 * 1000 ? "exam-timer-warn" : ""} ${left < 5 * 60 * 1000 ? "exam-timer-critical" : ""}">${formatTime(left)}</div>
          </div>
        </div>

        <div class="exam-layout">
          <aside class="exam-nav-panel card">
            <div class="text-xs font-semibold text-mute uppercase tracking-wide mb-2">Navigator</div>
            <div class="exam-nav-grid">${nav}</div>
            <div class="mt-3 flex flex-wrap gap-2 text-[10px] text-mute">
              <span class="exam-legend answered">Answered</span>
              <span class="exam-legend flagged">Flagged</span>
              <span class="exam-legend current">Current</span>
            </div>
            <button type="button" class="btn-primary w-full mt-4" id="btnExamSubmit">Submit exam</button>
            <button type="button" class="btn-ghost w-full mt-1" id="btnExamExit">Exit to lobby (saves progress)</button>
            <p class="mt-2 text-[11px] text-mute leading-snug">No Grok · No lesson help · Timer continues while you navigate.</p>
          </aside>

          <section class="exam-main card">
            <div class="flex items-center justify-between gap-2 mb-3">
              <div class="text-sm font-semibold">Question ${idx + 1}</div>
              <button type="button" class="btn-secondary" id="btnExamFlag" style="padding:0.45rem 0.75rem;font-size:0.8rem">
                ${exam.flags[qid] ? "★ Flagged" : "☆ Flag for review"}
              </button>
            </div>
            ${imgs}
            <div class="mt-2" id="examChoices"></div>
            <div class="row mt-4">
              <button type="button" class="btn-secondary grow" id="btnExamPrev" ${idx === 0 ? "disabled" : ""}>Previous</button>
              <button type="button" class="btn-primary grow" id="btnExamNext">${idx >= exam.questionIds.length - 1 ? "Review navigator" : "Next"}</button>
            </div>
          </section>
        </div>
      </div>`;

    // Choices A–E only (exam style)
    const box = document.getElementById("examChoices");
    ["A", "B", "C", "D", "E"].forEach((letter) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice" + (exam.answers[qid] === letter ? " selected" : "");
      const label =
        q?.images?.length || !q?.choices?.[letter] || String(q.choices[letter]).length < 3
          ? `Choice ${letter}`
          : q.choices[letter];
      btn.innerHTML = `<span class="letter">${letter}</span><span>${A().escapeHtml(label)}</span>`;
      btn.onclick = () => {
        exam.answers[qid] = letter;
        A().saveState();
        renderExam();
      };
      box.appendChild(btn);
    });

    root.querySelectorAll("[data-ei]").forEach((b) => {
      b.onclick = () => {
        exam.currentIndex = Number(b.dataset.ei);
        A().saveState();
        renderExam();
      };
    });
    document.getElementById("btnExamFlag").onclick = () => {
      exam.flags[qid] = !exam.flags[qid];
      A().saveState();
      renderExam();
    };
    document.getElementById("btnExamPrev").onclick = () => {
      if (idx > 0) {
        exam.currentIndex = idx - 1;
        A().saveState();
        renderExam();
      }
    };
    document.getElementById("btnExamNext").onclick = () => {
      if (idx < exam.questionIds.length - 1) {
        exam.currentIndex = idx + 1;
        A().saveState();
        renderExam();
      }
    };
    document.getElementById("btnExamSubmit").onclick = () => submitExam(false);
    document.getElementById("btnExamExit").onclick = () => {
      A().saveState({ immediate: true });
      stopTicker();
      renderExamLobby();
    };
    root.querySelectorAll(".exam-qimg img").forEach((img) => {
      img.onclick = () => A().openLightbox?.(img.getAttribute("data-full") || img.src);
    });
    refreshIcons?.();
  }

  function renderExamResults(result) {
    stopTicker();
    const { escapeHtml, openGrok, explainPrompt, qById, refreshIcons, showView } = A();
    const root = document.getElementById("view-exam");
    if (!root || !result) return;

    let filter = "all";
    function paint(f) {
      filter = f;
      const rows = result.detail.filter((d) => {
        if (filter === "wrong") return !d.correct && !d.pilot;
        if (filter === "flagged") return d.flagged;
        if (filter === "pilots") return d.pilot;
        return true;
      });

      root.innerHTML = `
        <div class="card">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <div class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${result.passed ? "bg-emerald-50 text-emerald-800" : "bg-rose-50 text-rose-800"}">
                ${result.passed ? "Pass (practice)" : "Below pass (practice)"}
              </div>
              <h1 class="mt-2 text-2xl font-semibold tracking-tight">Exam results & answer guide</h1>
              <p class="mt-1 text-sm text-mute">Scored items only (pilots excluded from %). Time used ${formatTime(result.timeUsedMs || 0)}.</p>
            </div>
            <div class="flex gap-4 items-center">
              <div class="text-center">
                <div class="text-3xl font-semibold tabular-nums text-brand">${result.scaled}</div>
                <div class="text-xs text-mute">Scaled / 10</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-semibold tabular-nums">${result.pct}%</div>
                <div class="text-xs text-mute">${result.correct}/${result.scoredN} scored</div>
              </div>
            </div>
          </div>
          <p class="mt-4 text-sm text-slate-700 leading-relaxed">
            Pass threshold: scaled <strong>≥ 6</strong> (≈ <strong>${result.passMarkPct || PASS_MARK_PCT}%</strong> on this practice scale).
            Real SOA scoring uses IRT; this is a study approximation for fairness across your forms.
          </p>
          <div class="row mt-4">
            <button type="button" class="btn-primary" id="btnNewExam">New mock form</button>
            <button type="button" class="btn-secondary" id="btnExamLobby">Exam lobby</button>
            <button type="button" class="btn-ghost" id="btnExamHome">Today</button>
          </div>
        </div>

        <div class="card">
          <div class="flex flex-wrap gap-2 mb-4">
            ${["all", "wrong", "flagged", "pilots"]
              .map(
                (k) =>
                  `<button type="button" class="btn-secondary exam-filter ${filter === k ? "ring-2 ring-brand" : ""}" data-f="${k}" style="padding:0.45rem 0.8rem;font-size:0.8rem">${k}</button>`
              )
              .join("")}
          </div>
          <div class="space-y-6" id="guideList">
            ${rows
              .map((d) => {
                const q = qById.get(d.id);
                const img =
                  d.images?.length || q?.images?.length
                    ? `<div class="q-images" style="max-height:420px">${(d.images || q.images || [])
                        .map((src) => `<img src="./${src}?v=guide" alt="${d.id}" />`)
                        .join("")}</div>`
                    : `<div class="quiz-stem text-sm">${escapeHtml(d.stemPreview)}</div>`;
                return `
                <article class="border border-slate-200 rounded-xl p-4 ${d.correct ? "bg-emerald-50/40" : d.pilot ? "bg-amber-50/40" : "bg-rose-50/30"}">
                  <div class="flex flex-wrap items-center gap-2 text-xs">
                    <span class="font-semibold text-ink">Q${d.index}</span>
                    <span class="text-mute">${escapeHtml(d.id)}</span>
                    <span class="text-mute">${d.cluster}</span>
                    ${d.pilot ? `<span class="text-amber-800 font-medium">Pilot</span>` : ""}
                    ${d.flagged ? `<span class="text-brand font-medium">Flagged</span>` : ""}
                    <span class="font-semibold ${d.correct ? "text-ok" : "text-bad"}">${d.correct ? "Correct" : "Incorrect / blank"}</span>
                  </div>
                  <div class="mt-3">${img}</div>
                  <div class="mt-3 grid sm:grid-cols-3 gap-2 text-sm">
                    <div class="rounded-lg bg-white border border-slate-100 px-3 py-2">Your answer: <strong>${d.userAnswer || "—"}</strong></div>
                    <div class="rounded-lg bg-white border border-slate-100 px-3 py-2">Key: <strong>${d.correctAnswer || "—"}</strong></div>
                    <button type="button" class="btn-grok" data-review-grok="${d.id}" style="padding:0.5rem">Ask Grok (review only)</button>
                  </div>
                </article>`;
              })
              .join("") || `<p class="text-sm text-mute">No items in this filter.</p>`}
          </div>
        </div>`;

      document.getElementById("btnNewExam").onclick = () => startExam(true);
      document.getElementById("btnExamLobby").onclick = () => {
        A().state.activeExam = null;
        A().saveState();
        renderExamLobby();
      };
      document.getElementById("btnExamHome").onclick = () => showView("home");
      root.querySelectorAll("[data-f]").forEach((b) => {
        b.onclick = () => paint(b.dataset.f);
      });
      root.querySelectorAll("[data-review-grok]").forEach((b) => {
        b.onclick = () => {
          const q = qById.get(b.dataset.reviewGrok);
          if (q) openGrok(explainPrompt(q));
        };
      });
      refreshIcons?.();
    }
    paint("all");
  }

  function bind(_api) {
    api = _api;
    ensureExamState(api.state);
    if (api.state.activeExam?.status === "in_progress") startTicker();
  }

  function onShow() {
    const exam = A().state.activeExam;
    if (exam?.status === "in_progress") renderExam();
    else if (exam?.status === "submitted" && exam.result) renderExamResults(exam.result);
    else renderExamLobby();
  }

  global.SOAExam = {
    bind,
    onShow,
    startExam,
    renderExam,
    renderExamLobby,
    renderExamResults,
    submitExam,
    stopTicker,
    buildExamForm,
    scaledScoreFromPercent,
    PASS_MARK_PCT,
    EXAM_N,
  };
})(window);

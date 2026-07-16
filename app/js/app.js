/* SOA Grind — premium Exam P coach (logic compatible with soa_grind_v1) */
(() => {
  "use strict";

  const STORAGE_KEY = "soa_grind_v1";
  const IDB_NAME = "soa_grind_db";
  const IDB_STORE = "progress";
  const DEFAULT_STATE = () => ({
    version: 3,
    xp: 0,
    streak: 0,
    lastActiveDate: null,
    lastReminderDate: null,
    notificationsEnabled: false,
    reminderHour: 19,
    updatedAt: 0,
    days: {},
    /** Module-level lesson progress — synced across devices & days */
    lessonMastery: {},
    wrongPool: {},
    history: [],
    /** Mock Exam P: used IDs + history + optional in-progress form */
    examUsedQuestionIds: [],
    examHistory: [],
    activeExam: null,
    settings: { dailyGoal: 20, grokBase: "https://grok.com/?q=" },
  });

  let state = loadState();
  let curriculum = null;
  let questions = [];
  let lessons = {};
  let qById = new Map();
  let quiz = null;
  let learn = null;
  let currentView = "home";
  let quizDisplayMode = "image";

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return DEFAULT_STATE();
      return { ...DEFAULT_STATE(), ...JSON.parse(raw) };
    } catch {
      return DEFAULT_STATE();
    }
  }

  function saveState(opts = {}) {
    state.updatedAt = Date.now();
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn(e);
    }
    idbSave(state);
    if (window.SOACloud && SOACloud.user) {
      SOACloud.saveProgress(state, !!opts.immediate).then((ok) => {
        renderAccountChip();
        if (opts.toast && ok) toast("Progress synced");
      });
    }
    renderAccountChip();
  }

  function idbSave(data) {
    try {
      const req = indexedDB.open(IDB_NAME, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(IDB_STORE)) db.createObjectStore(IDB_STORE);
      };
      req.onsuccess = () => {
        const db = req.result;
        db.transaction(IDB_STORE, "readwrite").objectStore(IDB_STORE).put(data, "main");
      };
    } catch (_) {}
  }

  function idbLoad() {
    return new Promise((resolve) => {
      try {
        const req = indexedDB.open(IDB_NAME, 1);
        req.onupgradeneeded = () => {
          const db = req.result;
          if (!db.objectStoreNames.contains(IDB_STORE)) db.createObjectStore(IDB_STORE);
        };
        req.onerror = () => resolve(null);
        req.onsuccess = () => {
          const g = req.result.transaction(IDB_STORE, "readonly").objectStore(IDB_STORE).get("main");
          g.onsuccess = () => resolve(g.result || null);
          g.onerror = () => resolve(null);
        };
      } catch (_) {
        resolve(null);
      }
    });
  }

  function todayISO() {
    const d = new Date();
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  }
  function parseISO(s) {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
  }
  function daysUntil(iso) {
    return Math.round((parseISO(iso) - parseISO(todayISO())) / 86400000);
  }
  function ensureDay(date) {
    if (!state.days[date]) state.days[date] = { readingsDone: [], answered: {}, completed: false, lessons: {} };
    if (!state.days[date].lessons) state.days[date].lessons = {};
    return state.days[date];
  }
  function dayPlan(date = todayISO()) {
    return curriculum?.days?.find((d) => d.date === date) || null;
  }
  function lessonIdsFor(plan) {
    if (!plan) return [];
    if (plan.lessonIds?.length) return plan.lessonIds.filter((id) => lessons[id] || id);
    if (plan.lessonId && (lessons[plan.lessonId] || plan.lessonId)) return [plan.lessonId];
    return [];
  }

  /** Resolved lesson for a day: base module + longer quiz-aligned bridge sections */
  function resolveLesson(lessonId, date = todayISO()) {
    const base = lessons[lessonId];
    if (!base) return null;
    const plan = dayPlan(date);
    return enrichLessonForDay(base, plan);
  }

  function enrichLessonForDay(base, plan) {
    const guides = window.SOA_TOPIC_GUIDES || {};
    const topics = plan?.topicPrefs?.length ? plan.topicPrefs : base.topics || [];
    const uniqueTopics = [...new Set(topics.length ? topics : ["general_misc"])];
    const sampleIds = (plan?.assignedQuestionIds || []).slice(0, 8);
    const samples = sampleIds.map((id) => qById.get(id)).filter(Boolean);

    const bridge = [];

    // --- Today's quiz alignment (longer, practical) ---
    const topicLabels = uniqueTopics.map((t) => guides[t]?.label || t).join(" · ");
    bridge.push({
      id: "bridge_focus",
      type: "concept",
      title: `Today’s quiz focus${plan?.title ? ": " + plan.title : ""}`,
      body:
        `Your practice set today is built around:\n\n• Topics: ${topicLabels || "general probability tools"}\n` +
        `• Target questions: ~${plan?.questionTarget ?? 20}\n` +
        `• Mode: ${plan?.mode || "learn"}\n\n` +
        `Before you open the quiz, you should be able to:\n` +
        `1) Name the main technique each topic needs\n` +
        `2) Write the key formula from memory\n` +
        `3) Spot the usual wording traps\n\n` +
        `This bridge is longer on purpose — treat it as the “lecture” for today’s problem types, not a skim.`,
    });

    for (const t of uniqueTopics.slice(0, 4)) {
      const g = guides[t] || guides.general_misc;
      const tech = (g.techniques || []).map((x, i) => `${i + 1}. ${x}`).join("\n");
      const forms = (g.formulas || []).length
        ? "\n\nCore formulas / identities:\n" + g.formulas.map((f) => `• ${f}`).join("\n")
        : "";
      const moves = (g.examMoves || []).length
        ? "\n\nExam moves:\n" + g.examMoves.map((m) => `• ${m}`).join("\n")
        : "";
      bridge.push({
        id: `bridge_topic_${t}`,
        type: "concept",
        title: `Deep dive — ${g.label}`,
        body: `Technique checklist for ${g.label}:\n\n${tech}${forms}${moves}`,
      });
    }

    // Worked pattern section from real today's stems (short previews)
    if (samples.length) {
      const lines = samples
        .slice(0, 5)
        .map((q, i) => {
          const tags = (q.topics || []).join(", ") || q.cluster || "?";
          const preview = (q.stem || "").replace(/\s+/g, " ").slice(0, 160);
          return `${i + 1}. [${q.id}] topics: ${tags}\n   Pattern cue: ${preview}${(q.stem || "").length > 160 ? "…" : ""}`;
        })
        .join("\n\n");
      bridge.push({
        id: "bridge_patterns",
        type: "example",
        title: "Patterns from today’s assigned sample set",
        setup: `These are cues from questions you may see in today’s quiz (official PDF crops in the quiz view):\n\n${lines}`,
        solution:
          "For each cue, pause and write:\n• What is X (or the event)?\n• Which family / rule applies?\n• What is the target probability or expectation in symbols?\nThen open the PDF crop only after you have a plan.",
        why: "Exam P speed comes from classification, not from re-reading the stem five times. Aligning the lesson with today’s queue trains that reflex.",
      });
    }

    bridge.push({
      id: "bridge_playbook",
      type: "concept",
      title: "60-second playbook before each question",
      body:
        "Use this every time in today’s quiz:\n\n" +
        "1) Underline the quantity asked (probability, mean, payment, …).\n" +
        "2) Define the RV / events in one line.\n" +
        "3) Choose the tool (counting, conditional/Bayes, named distribution, insurance transform, joint, CLT, …).\n" +
        "4) Write the formula, then compute.\n" +
        "5) Sanity-check: units, range 0–1 for probabilities, mean vs support.\n\n" +
        "If the PDF shows a density or table, copy the support and parameters before integrating.",
    });

    bridge.push({
      id: "bridge_check",
      type: "check",
      title: "Today readiness check",
      prompt: `For today’s topics (${topicLabels || "today’s plan"}), what is the best first move on a new stem?`,
      choices: {
        A: "Start integrating or expanding factorials immediately",
        B: "Define the random variable / events and name the tool, then write the target in symbols",
        C: "Guess the distribution family from the answer choices only",
        D: "Skip reading the support and endpoints",
      },
      answer: "B",
      explain:
        "Classification first. Most Exam P errors are wrong setup, not arithmetic. Today’s lesson + quiz both reward that habit.",
    });

    // Keep base sections, drop trailing checks to end with bridge_check (or keep base checks then bridge)
    const baseSections = (base.sections || []).map((s) => ({ ...s }));
    const minutes = (base.minutes || 30) + 25 + uniqueTopics.length * 8;

    return {
      ...base,
      title: base.title,
      minutes,
      sections: [...baseSections, ...bridge],
      _enriched: true,
      _topics: uniqueTopics,
    };
  }

  function ensureLessonMastery(lessonId) {
    if (!state.lessonMastery) state.lessonMastery = {};
    if (!state.lessonMastery[lessonId]) {
      state.lessonMastery[lessonId] = { sectionDone: [], checks: {}, updatedAt: 0 };
    }
    return state.lessonMastery[lessonId];
  }

  /** Progress = global mastery ∪ day-local (both sync to cloud) */
  function getLessonProgress(date, lessonId) {
    const day = ensureDay(date);
    if (!day.lessons[lessonId]) day.lessons[lessonId] = { sectionDone: [], checks: {} };
    const local = day.lessons[lessonId];
    const global = ensureLessonMastery(lessonId);
    return {
      sectionDone: Array.from(new Set([...(global.sectionDone || []), ...(local.sectionDone || [])])),
      checks: { ...(global.checks || {}), ...(local.checks || {}) },
    };
  }

  function ensureLessonProgress(date, lessonId) {
    // Mutable day slice; also mirrored to global on write helpers
    const day = ensureDay(date);
    if (!day.lessons[lessonId]) day.lessons[lessonId] = { sectionDone: [], checks: {} };
    // hydrate day from global so UI sees synced progress immediately
    const g = ensureLessonMastery(lessonId);
    day.lessons[lessonId].sectionDone = Array.from(
      new Set([...(day.lessons[lessonId].sectionDone || []), ...(g.sectionDone || [])])
    );
    day.lessons[lessonId].checks = { ...(g.checks || {}), ...(day.lessons[lessonId].checks || {}) };
    return day.lessons[lessonId];
  }

  function markLessonSection(date, lessonId, sectionId, kind, value) {
    const dayProg = ensureLessonProgress(date, lessonId);
    const global = ensureLessonMastery(lessonId);
    if (kind === "section") {
      if (!dayProg.sectionDone.includes(sectionId)) dayProg.sectionDone.push(sectionId);
      if (!global.sectionDone.includes(sectionId)) global.sectionDone.push(sectionId);
    } else if (kind === "check") {
      dayProg.checks[sectionId] = value;
      global.checks[sectionId] = value;
    }
    global.updatedAt = Date.now();
    dayProg.updatedAt = Date.now();
  }

  function isLessonComplete(date, lessonId) {
    const lesson = resolveLesson(lessonId, date) || lessons[lessonId];
    if (!lesson) return true;
    const prog = getLessonProgress(date, lessonId);
    for (const s of lesson.sections || []) {
      if (s.type === "check") {
        if (!prog.checks[s.id]) return false;
      } else if (!prog.sectionDone.includes(s.id)) return false;
    }
    return true;
  }
  function areAllLessonsComplete(date = todayISO()) {
    const ids = lessonIdsFor(dayPlan(date));
    return !ids.length || ids.every((id) => isLessonComplete(date, id));
  }
  function lessonProgressPct(date = todayISO()) {
    const ids = lessonIdsFor(dayPlan(date));
    if (!ids.length) return 100;
    let total = 0,
      done = 0;
    for (const id of ids) {
      const lesson = resolveLesson(id, date) || lessons[id];
      if (!lesson) continue;
      const prog = getLessonProgress(date, id);
      for (const s of lesson.sections || []) {
        total++;
        if (s.type === "check" ? prog.checks[s.id] : prog.sectionDone.includes(s.id)) done++;
      }
    }
    return total ? Math.round((100 * done) / total) : 100;
  }

  function grokUrl(prompt) {
    return (state.settings.grokBase || "https://grok.com/?q=") + encodeURIComponent(prompt);
  }
  function openGrok(prompt) {
    window.open(grokUrl(prompt), "_blank", "noopener,noreferrer");
  }
  function explainPrompt(q, choice) {
    const choices = Object.entries(q.choices || {}).map(([k, v]) => `(${k}) ${v}`).join("\n");
    const note = q.images?.length
      ? `\nNOTE: Learner is viewing official SOA PDF crop of sample #${q.number}.\n`
      : "";
    return (
      `I'm preparing for SOA Exam P. Tutor me on this MCQ.\n${note}` +
      `Question ${q.number} (${q.id}):\n${q.stem}\n\nChoices:\n${choices}\n\n` +
      (choice ? `I selected (${choice}).\n` : "") +
      (q.answer ? `Answer key: ${q.answer}.\n` : "") +
      `Please: clean LaTeX statement, setup, full solution, traps, 2 similar questions with answers.`
    );
  }
  function teachGrokPrompt(lesson, section) {
    return (
      `SOA Exam P lesson "${lesson.title}". Section: ${section.title}\n` +
      `${section.body || section.setup || ""}\n\nRe-explain slowly with one extra example and a common exam trap.`
    );
  }
  function sundayRecapPrompt(items) {
    const body = items
      .slice(0, 15)
      .map((w, i) => {
        const q = qById.get(w.id);
        return `${i + 1}. [${w.id}] LO=${w.lo || "?"} missed ${w.count}x\n${(q?.stem || w.stemPreview || "").slice(0, 400)}`;
      })
      .join("\n\n");
    return (
      `You are my SOA Exam P coach. WRONG QUESTION POOL below.\n` +
      `Produce: top 5 weaknesses, formula checklist, 12 similar MCQs with answers, 60-min revision plan.\n\n` +
      `WRONG POOL:\n${body || "(empty)"}`
    );
  }

  function updateStreakOnActivity() {
    const t = todayISO();
    if (state.lastActiveDate === t) return;
    if (state.lastActiveDate) {
      const diff = Math.round((parseISO(t) - parseISO(state.lastActiveDate)) / 86400000);
      state.streak = diff === 1 ? state.streak + 1 : 1;
    } else state.streak = 1;
    state.lastActiveDate = t;
  }

  function dayStats(date = todayISO()) {
    const plan = dayPlan(date);
    const day = ensureDay(date);
    const target = plan?.questionTarget ?? state.settings.dailyGoal ?? 20;
    const answeredIds = Object.keys(day.answered || {});
    const correct = answeredIds.filter((id) => day.answered[id].correct).length;
    const lessonPct = lessonProgressPct(date) / 100;
    const qPct = target > 0 ? Math.min(1, answeredIds.length / target) : 1;
    const overall = Math.round((0.4 * lessonPct + 0.6 * qPct) * 100);
    const lessonDone = areAllLessonsComplete(date);
    const done = lessonDone && answeredIds.length >= target;
    return { target, answered: answeredIds.length, correct, lessonPct: Math.round(lessonPct * 100), lessonDone, overall, done };
  }

  function wrongList() {
    return Object.entries(state.wrongPool)
      .map(([id, meta]) => ({ id, ...meta }))
      .sort((a, b) => b.count - a.count || (b.lastWrong || "").localeCompare(a.lastWrong || ""));
  }

  function accuracyOverall() {
    const h = state.history || [];
    if (!h.length) return null;
    const c = h.filter((x) => x.correct).length;
    return Math.round((100 * c) / h.length);
  }

  /* ---------- Learn ---------- */
  function startLearn(date = todayISO()) {
    const ids = lessonIdsFor(dayPlan(date));
    if (!ids.length) {
      toast("No lesson module mapped for this day");
      return;
    }
    // hydrate mastery from cloud-shaped state before seeking position
    ids.forEach((id) => ensureLessonProgress(date, id));
    learn = { date, lessonIds: ids, lessonIndex: 0, sectionIndex: 0, selectedCheck: null, checkRevealed: false };
    seekFirstIncomplete();
    updateStreakOnActivity();
    saveState({ immediate: true });
    showView("learn");
    renderLearn();
  }
  function seekFirstIncomplete() {
    if (!learn) return;
    for (let li = 0; li < learn.lessonIds.length; li++) {
      const lesson = resolveLesson(learn.lessonIds[li], learn.date);
      if (!lesson) continue;
      const prog = getLessonProgress(learn.date, lesson.id);
      for (let si = 0; si < lesson.sections.length; si++) {
        const s = lesson.sections[si];
        const ok = s.type === "check" ? !!prog.checks[s.id] : prog.sectionDone.includes(s.id);
        if (!ok) {
          learn.lessonIndex = li;
          learn.sectionIndex = si;
          learn.selectedCheck = null;
          learn.checkRevealed = false;
          return;
        }
      }
    }
    const lastL = learn.lessonIds.length - 1;
    const lastLesson = resolveLesson(learn.lessonIds[lastL], learn.date);
    learn.lessonIndex = lastL;
    learn.sectionIndex = (lastLesson?.sections?.length || 1) - 1;
  }
  function currentLesson() {
    return learn ? resolveLesson(learn.lessonIds[learn.lessonIndex], learn.date) : null;
  }
  function currentSection() {
    const lesson = currentLesson();
    return lesson ? lesson.sections[learn.sectionIndex] : null;
  }
  function markSectionDone() {
    const lesson = currentLesson();
    const section = currentSection();
    if (!lesson || !section || section.type === "check") return;
    const before = getLessonProgress(learn.date, lesson.id).sectionDone.includes(section.id);
    markLessonSection(learn.date, lesson.id, section.id, "section", true);
    if (!before) state.xp += 5;
    const day = ensureDay(learn.date);
    const plan = dayPlan(learn.date);
    (plan?.readings || []).forEach((r) => {
      if (!day.readingsDone.includes(r.id)) day.readingsDone.push(r.id);
    });
    updateStreakOnActivity();
    saveState({ immediate: true }); // critical for cross-device lesson sync
  }
  function advanceLearn() {
    const lesson = currentLesson();
    if (!lesson) return;
    if (learn.sectionIndex < lesson.sections.length - 1) {
      learn.sectionIndex++;
      learn.selectedCheck = null;
      learn.checkRevealed = false;
      renderLearn();
      renderChrome();
      return;
    }
    if (learn.lessonIndex < learn.lessonIds.length - 1) {
      learn.lessonIndex++;
      learn.sectionIndex = 0;
      learn.selectedCheck = null;
      learn.checkRevealed = false;
      renderLearn();
      renderChrome();
      return;
    }
    toast("Lesson complete — quiz unlocked · synced");
    saveState({ immediate: true });
    learn = null;
    showView("home");
    renderAll();
  }
  function submitCheck() {
    const lesson = currentLesson();
    const section = currentSection();
    if (!lesson || !section || section.type !== "check" || !learn.selectedCheck) return;
    const ok = learn.selectedCheck === section.answer;
    learn.checkRevealed = true;
    if (ok) {
      const already = !!getLessonProgress(learn.date, lesson.id).checks[section.id];
      markLessonSection(learn.date, lesson.id, section.id, "check", true);
      if (!already) state.xp += 8;
      updateStreakOnActivity();
      saveState({ immediate: true });
    }
    renderLearn();
    renderChrome();
  }

  /* ---------- Quiz ---------- */
  function buildQueue(date = todayISO()) {
    const plan = dayPlan(date);
    const day = ensureDay(date);
    const target = plan?.questionTarget ?? 20;
    const done = new Set(Object.keys(day.answered || {}));
    const queue = [];
    const reviewN = Math.min(Math.ceil(target * 0.3), wrongList().length);
    for (const w of wrongList()) {
      if (queue.length >= reviewN) break;
      if (!done.has(w.id) && qById.has(w.id)) queue.push(w.id);
    }
    for (const id of plan?.assignedQuestionIds || []) {
      if (queue.length >= target) break;
      if (!done.has(id) && qById.has(id) && !queue.includes(id)) queue.push(id);
    }
    if (queue.length < target) {
      const prefs = new Set(plan?.topicPrefs || []);
      for (const q of questions) {
        if (queue.length >= target) break;
        if (q.answer && !done.has(q.id) && !queue.includes(q.id) && (q.topics || []).some((t) => prefs.has(t))) queue.push(q.id);
      }
    }
    if (queue.length < target) {
      for (const q of questions) {
        if (queue.length >= target) break;
        if (q.answer && !done.has(q.id) && !queue.includes(q.id)) queue.push(q.id);
      }
    }
    return queue.slice(0, Math.max(target, 0));
  }
  function startQuiz(date = todayISO()) {
    if (!areAllLessonsComplete(date)) {
      toast("Finish today’s lesson first");
      startLearn(date);
      return;
    }
    const queue = buildQueue(date);
    if (!queue.length) {
      toast("No questions left for today");
      return;
    }
    quiz = { date, queue, index: 0, selected: null, revealed: false, _modeTouched: false };
    quizDisplayMode = "image";
    updateStreakOnActivity();
    saveState();
    showView("quiz");
    renderQuiz();
  }
  function currentQuestion() {
    return quiz ? qById.get(quiz.queue[quiz.index]) : null;
  }
  function submitAnswer() {
    if (!quiz || quiz.revealed) return;
    const q = currentQuestion();
    if (!q || !quiz.selected) return;
    const correct = q.answer && quiz.selected === q.answer;
    const day = ensureDay(quiz.date);
    day.answered[q.id] = { choice: quiz.selected, correct: !!correct, ts: new Date().toISOString() };
    state.history.unshift({ id: q.id, date: quiz.date, choice: quiz.selected, correct: !!correct, ts: new Date().toISOString() });
    state.history = state.history.slice(0, 500);
    if (correct) {
      state.xp += 10;
      if (state.wrongPool[q.id]) delete state.wrongPool[q.id];
    } else {
      state.xp += 2;
      const prev = state.wrongPool[q.id] || { count: 0 };
      state.wrongPool[q.id] = {
        count: (prev.count || 0) + 1,
        lastWrong: quiz.date,
        topics: q.topics || [],
        lo: q.lo || "",
        stemPreview: (q.stem || "").slice(0, 180),
        number: q.number,
      };
    }
    quiz.revealed = true;
    if (dayStats(quiz.date).done) {
      day.completed = true;
      state.xp += 25;
      toast("Daily goal complete · +25 XP");
    }
    saveState();
    renderQuiz();
    renderChrome();
  }
  function nextQuestion() {
    if (!quiz) return;
    if (quiz.index >= quiz.queue.length - 1) {
      const score = Object.values(ensureDay(quiz.date).answered || {});
      const correct = score.filter((x) => x.correct).length;
      quiz = { finished: true, correct, total: score.length, date: quiz.date };
      renderQuiz();
      return;
    }
    quiz.index++;
    quiz.selected = null;
    quiz.revealed = false;
    renderQuiz();
  }

  /* ---------- Notifications ---------- */
  async function enableNotifications() {
    if (!("Notification" in window)) {
      toast("Notifications not supported here");
      return;
    }
    const perm = await Notification.requestPermission();
    if (perm !== "granted") {
      toast("Permission denied");
      return;
    }
    state.notificationsEnabled = true;
    saveState();
    if (navigator.serviceWorker?.controller) {
      navigator.serviceWorker.controller.postMessage({ type: "NOTIFY_TEST", body: "Reminders enabled" });
    } else {
      new Notification("SOA Grind", { body: "Reminders enabled", icon: "./icons/icon-192.svg" });
    }
    toast("Notifications on");
  }
  function maybeRemind() {
    if (!state.notificationsEnabled || Notification.permission !== "granted") return;
    const t = todayISO();
    if (state.lastReminderDate === t) return;
    const stats = dayStats(t);
    if (stats.done) return;
    if (new Date().getHours() < (state.reminderHour || 19)) return;
    const body = !stats.lessonDone
      ? "Lesson still open — unlock today’s quiz."
      : `${Math.max(0, stats.target - stats.answered)} questions remaining · streak ${state.streak}`;
    if (navigator.serviceWorker?.controller) {
      navigator.serviceWorker.controller.postMessage({ type: "NOTIFY_TEST", body });
    } else {
      new Notification("SOA Grind", { body, icon: "./icons/icon-192.svg", tag: "soa-daily" });
    }
    state.lastReminderDate = t;
    saveState();
  }
  setInterval(maybeRemind, 60 * 60 * 1000);

  /* ---------- DOM helpers ---------- */
  function $(sel) {
    return document.querySelector(sel);
  }
  function showView(name) {
    currentView = name;
    document.querySelectorAll(".view").forEach((el) => el.classList.toggle("active", el.id === `view-${name}`));
    document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.toggle("active", btn.dataset.view === name));
    refreshIcons();
  }
  function toast(msg) {
    const el = $("#toast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2400);
  }
  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
  function downloadJSON(filename, obj) {
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }
  function refreshIcons() {
    if (window.lucide?.createIcons) lucide.createIcons();
  }
  function renderMath(root) {
    if (!root || typeof renderMathInElement !== "function") return;
    try {
      renderMathInElement(root, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false },
          { left: "\\[", right: "\\]", display: true },
        ],
        throwOnError: false,
      });
    } catch (_) {}
  }
  function ringSvg(pct, size = 88) {
    const r = 36;
    const c = 2 * Math.PI * r;
    const offset = c * (1 - Math.min(100, Math.max(0, pct)) / 100);
    return `<div class="ring-wrap" style="width:${size}px;height:${size}px">
      <svg width="${size}" height="${size}" viewBox="0 0 88 88">
        <circle cx="44" cy="44" r="${r}" fill="none" stroke="#e2e8f0" stroke-width="8"/>
        <circle cx="44" cy="44" r="${r}" fill="none" stroke="#0f766e" stroke-width="8"
          stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${offset}"
          style="transition: stroke-dashoffset 600ms ease"/>
      </svg>
      <div class="ring-center">${pct}%</div>
    </div>`;
  }

  /* ---------- Chrome / Auth ---------- */
  function renderAccountChip() {
    const label = $("#accountBarLabel");
    const cta = $("#accountBarCta");
    const cloud = window.SOACloud;
    if (!label) return;
    if (!cloud || cloud.status === "need-config") {
      label.textContent = "Local progress only · cloud optional";
      if (cta) cta.textContent = "Setup";
      return;
    }
    if (cloud.user) {
      const mark = cloud.status === "syncing" ? "syncing…" : cloud.status === "error" ? "error" : "synced";
      label.innerHTML = `Signed in as <strong>${escapeHtml(cloud.user.email || "account")}</strong> · ${mark}`;
      if (cta) cta.textContent = "Account";
    } else {
      label.textContent = "Cloud: Sign in to sync phone & PC";
      if (cta) cta.textContent = "Sign in";
    }
  }
  function renderChrome() {
    const stats = dayStats();
    const streakEl = $("#streakChip");
    const xpEl = $("#xpChip");
    if (streakEl) streakEl.textContent = String(state.streak);
    if (xpEl) xpEl.textContent = String(state.xp);
    const fill = $("#progressFill");
    if (fill) fill.style.width = `${stats.overall}%`;
    const lab = $("#progressLabel");
    if (lab) {
      const cloud = window.SOACloud;
      const sync = cloud?.user ? (cloud.status === "synced" ? " · synced" : " · cloud") : "";
      lab.textContent = `Today ${stats.overall}% · Learn ${stats.lessonPct}% · Quiz ${stats.answered}/${stats.target}${sync}`;
    }
    renderAccountChip();
  }

  function openAuthModal(mode = "signin") {
    const backdrop = $("#authModal");
    if (!backdrop) return;
    backdrop.classList.add("show");
    backdrop.dataset.mode = mode;
    $("#authTitle").textContent = mode === "signup" ? "Create account" : "Sign in";
    $("#authSubmit").textContent = mode === "signup" ? "Create account" : "Sign in";
    $("#authSwitch").textContent = mode === "signup" ? "Already have an account? Sign in" : "New here? Create account";
    $("#authError").textContent = "";
    const cloud = window.SOACloud;
    if (!cloud || cloud.status === "need-config") {
      $("#authHint").innerHTML = "Cloud not configured. See <code>FIREBASE_SETUP.md</code>. Local progress still works.";
      $("#authForm").style.display = "none";
    } else {
      $("#authHint").textContent = "Same email on every device keeps streak, lessons, and wrong pool continuous.";
      $("#authForm").style.display = "block";
    }
    refreshIcons();
  }
  function closeAuthModal() {
    $("#authModal")?.classList.remove("show");
  }
  async function handleAuthSubmit(e) {
    e.preventDefault();
    const cloud = window.SOACloud;
    if (!cloud?.ready) {
      toast("Configure Firebase first");
      return;
    }
    const email = $("#authEmail").value.trim();
    const password = $("#authPassword").value;
    const mode = $("#authModal").dataset.mode || "signin";
    $("#authError").textContent = "";
    try {
      if (mode === "signup") await cloud.signUp(email, password);
      else await cloud.signIn(email, password);
      await pullAndMergeCloud();
      saveState({ immediate: true });
      closeAuthModal();
      toast(mode === "signup" ? "Account created" : "Signed in");
      renderAll();
    } catch (err) {
      $("#authError").textContent = friendlyAuthError(err);
    }
  }
  function friendlyAuthError(err) {
    const code = err?.code || "";
    if (code.includes("email-already-in-use")) return "Email already registered — sign in.";
    if (code.includes("wrong-password") || code.includes("invalid-credential")) return "Wrong email or password.";
    if (code.includes("user-not-found")) return "No account — create one.";
    if (code.includes("weak-password")) return "Password needs 6+ characters.";
    if (code.includes("invalid-email")) return "Enter a valid email.";
    return err?.message || String(err);
  }
  async function pullAndMergeCloud() {
    const cloud = window.SOACloud;
    if (!cloud?.user) return;
    try {
      const remote = await cloud.loadProgress();
      if (remote) {
        state = cloud.mergeProgress(state, remote);
        state = { ...DEFAULT_STATE(), ...state };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        idbSave(state);
      }
    } catch (e) {
      console.warn(e);
      toast("Cloud load failed — using local");
    }
  }

  /* ---------- Screens ---------- */
  function renderHome() {
    const root = $("#view-home");
    if (!root) return;
    const plan = dayPlan();
    const stats = dayStats();
    const target = curriculum?.examTarget || "2026-09-14";
    const left = daysUntil(target);
    const locked = !stats.lessonDone;
    const quote = "Precision under pressure is the whole game — define the random variable first.";
    const guides = window.SOA_TOPIC_GUIDES || {};
    const topicLine = (plan?.topicPrefs || []).map((t) => guides[t]?.label || t).join(" · ");

    if (!plan) {
      root.innerHTML = `<div class="card"><h2 class="text-lg font-semibold">No lesson mapped for today</h2>
        <p class="muted small mt-2">Curriculum covers the planned window. Use Path or Wrong Pool.</p></div>`;
      refreshIcons();
      return;
    }

    root.innerHTML = `
      <section class="card">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="min-w-0 flex-1">
            <div class="inline-flex items-center gap-1.5 rounded-full bg-brand-soft px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-brand">${escapeHtml(plan.phase)}</div>
            <h1 class="mt-3 text-xl md:text-2xl font-semibold tracking-tight text-ink leading-snug">${escapeHtml(plan.title)}</h1>
            <p class="mt-1.5 text-sm text-mute">${escapeHtml(plan.weekday)} · ${escapeHtml(plan.date)}${plan.fmLight ? " · light FM" : ""}</p>
            ${topicLine ? `<p class="mt-2 text-sm font-medium text-brand">Quiz topics today: ${escapeHtml(topicLine)}</p>` : ""}
            <p class="mt-3 text-sm text-mute">Exam P target <span class="font-medium text-ink">${target}</span> · <span class="font-semibold text-brand">${left}d</span></p>
          </div>
          <div class="shrink-0">${ringSvg(stats.overall)}</div>
        </div>

        <div class="mt-5 grid grid-cols-3 gap-2">
          <div class="rounded-xl bg-slate-50 border border-slate-100 px-3 py-3">
            <div class="text-lg font-semibold tabular-nums">${stats.lessonPct}%</div>
            <div class="text-[11px] font-medium text-mute mt-0.5">Lesson</div>
          </div>
          <div class="rounded-xl bg-slate-50 border border-slate-100 px-3 py-3">
            <div class="text-lg font-semibold tabular-nums">${stats.answered}/${stats.target}</div>
            <div class="text-[11px] font-medium text-mute mt-0.5">Questions</div>
          </div>
          <div class="rounded-xl bg-slate-50 border border-slate-100 px-3 py-3">
            <div class="text-lg font-semibold tabular-nums">${Object.keys(state.wrongPool).length}</div>
            <div class="text-[11px] font-medium text-mute mt-0.5">Wrong pool</div>
          </div>
        </div>

        <div class="mt-4 ${locked ? "lock-banner warn" : "lock-banner ok"}">
          ${locked
            ? "Quiz stays locked until today’s lesson is complete — concept, examples, and check."
            : "Lesson complete. Quiz is ready whenever you are."}
        </div>

        <div class="mt-4 space-y-2">
          <button class="btn-primary w-full" id="btnLearn">${stats.lessonDone ? "Review lesson" : "Continue lesson"}</button>
          <button class="btn-secondary w-full" id="btnQuiz" ${locked ? "disabled" : ""}>${stats.done ? "Bonus practice" : "Start today’s questions"}</button>
        </div>
      </section>

      <section class="card border-slate-900/10 bg-slate-900 text-white">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div class="text-[11px] font-semibold uppercase tracking-wide text-slate-300">Official-style CBT</div>
            <h2 class="mt-1 text-lg font-semibold tracking-tight">Exam P mock · 30 Q · 3 hours</h2>
            <p class="mt-1 text-sm text-slate-300">No Grok · flag & navigator · scaled score 0–10 (pass ≥ 6) · answer guide after submit</p>
          </div>
          <button type="button" class="btn-primary shrink-0" id="btnHomeExam" style="background:linear-gradient(180deg,#14b8a6,#0f766e)">
            Open exam mode
          </button>
        </div>
      </section>

      <section class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <button type="button" class="card card-interactive text-left" id="quickWrong">
          <i data-lucide="rotate-ccw" class="h-5 w-5 text-brand"></i>
          <div class="mt-3 text-sm font-semibold">Wrong pool</div>
          <div class="mt-1 text-xs text-mute">${Object.keys(state.wrongPool).length} items · spaced review</div>
        </button>
        <button type="button" class="card card-interactive text-left" id="quickSunday">
          <i data-lucide="sparkles" class="h-5 w-5 text-brand"></i>
          <div class="mt-3 text-sm font-semibold">Sunday recap</div>
          <div class="mt-1 text-xs text-mute">Grok diagnosis + export</div>
        </button>
        <button type="button" class="card card-interactive text-left" id="quickPath">
          <i data-lucide="map" class="h-5 w-5 text-brand"></i>
          <div class="mt-3 text-sm font-semibold">Path</div>
          <div class="mt-1 text-xs text-mute">Upcoming study days</div>
        </button>
        <button type="button" class="card card-interactive text-left" id="quickStats">
          <i data-lucide="bar-chart-2" class="h-5 w-5 text-brand"></i>
          <div class="mt-3 text-sm font-semibold">Progress</div>
          <div class="mt-1 text-xs text-mute">Accuracy & mastery</div>
        </button>
      </section>

      <section class="card">
        <div class="text-[11px] font-semibold uppercase tracking-wide text-mute">Quiet note</div>
        <p class="mt-2 text-sm leading-relaxed text-slate-700">${quote}</p>
      </section>
    `;

    $("#btnLearn").onclick = () => startLearn();
    $("#btnQuiz").onclick = () => startQuiz();
    $("#btnHomeExam")?.addEventListener("click", () => {
      showView("exam");
      window.SOAExam?.onShow?.();
    });
    $("#quickWrong").onclick = () => { showView("wrong"); renderWrong(); };
    $("#quickSunday").onclick = () => { showView("wrong"); renderWrong(); setTimeout(() => $("#btnSunday")?.click(), 50); };
    $("#quickPath").onclick = () => { showView("path"); renderPath(); };
    $("#quickStats").onclick = () => { showView("stats"); renderStats(); };
    refreshIcons();
  }

  function renderLearn() {
    const root = $("#view-learn");
    if (!root) return;
    if (!learn) {
      const plan = dayPlan();
      const ids = lessonIdsFor(plan);
      const guides = window.SOA_TOPIC_GUIDES || {};
      const topicLine = (plan?.topicPrefs || []).map((t) => guides[t]?.label || t).join(" · ");
      root.innerHTML = `
        <div class="card">
          <h2 class="text-lg font-semibold tracking-tight">Learn</h2>
          <p class="mt-1 text-sm text-mute">Longer teach-first modules aligned to today’s quiz topics. Progress syncs across devices when signed in.</p>
          ${topicLine ? `<p class="mt-3 text-sm text-brand font-medium">Today’s quiz topics: ${escapeHtml(topicLine)}</p>` : ""}
          <div class="mt-4 space-y-2">
            ${ids.map((id) => {
              const L = resolveLesson(id, todayISO()) || lessons[id];
              const done = isLessonComplete(todayISO(), id);
              return `<div class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-3 py-3">
                <div>
                  <div class="text-sm font-semibold">${done ? "Synced · complete" : "In progress / pending"} · ${escapeHtml(L?.title || id)}</div>
                  <div class="text-xs text-mute mt-0.5">~${L?.minutes || "?"} min · ${(L?.sections || []).length} sections (core + quiz bridge)</div>
                </div>
              </div>`;
            }).join("") || `<p class="text-sm text-mute">No modules for today.</p>`}
          </div>
          <button class="btn-primary w-full mt-4" id="btnStartLearnEmpty">${areAllLessonsComplete() ? "Review lesson" : "Start lesson"}</button>
        </div>`;
      $("#btnStartLearnEmpty").onclick = () => startLearn();
      refreshIcons();
      return;
    }

    const lesson = currentLesson();
    const section = currentSection();
    if (!lesson || !section) {
      root.innerHTML = `<div class="card"><p class="text-mute">Lesson data missing.</p></div>`;
      return;
    }
    const prog = getLessonProgress(learn.date, lesson.id);
    const dots = lesson.sections
      .map((s, i) => {
        const ok = s.type === "check" ? !!prog.checks[s.id] : prog.sectionDone.includes(s.id);
        const cls = ok ? "done" : i === learn.sectionIndex ? "current" : "";
        return `<div class="step-dot ${cls}">${i + 1}</div>`;
      })
      .join("");

    let body = "";
    if (section.type === "concept") {
      body = `<span class="tag tag-concept">Concept</span>
        <h3 class="text-base font-semibold tracking-tight">${escapeHtml(section.title)}</h3>
        <div class="body mt-3">${escapeHtml(section.body)}</div>
        <div class="row mt-5">
          <button class="btn-primary grow" id="btnMarkNext">Continue</button>
          <button class="btn-grok grow" id="btnGrokSec">Ask Grok</button>
        </div>`;
    } else if (section.type === "example") {
      body = `<span class="tag tag-example">Worked example</span>
        <h3 class="text-base font-semibold tracking-tight">${escapeHtml(section.title)}</h3>
        <div class="body mt-3"><strong>Setup</strong>\n${escapeHtml(section.setup)}</div>
        <div class="solution-box"><strong>Solution</strong>\n${escapeHtml(section.solution)}</div>
        <div class="why-box"><strong>Why this matters</strong> — ${escapeHtml(section.why)}</div>
        <div class="row mt-5">
          <button class="btn-primary grow" id="btnMarkNext">Continue</button>
          <button class="btn-grok grow" id="btnGrokSec">Ask Grok</button>
        </div>`;
    } else {
      const choices = Object.entries(section.choices || {})
        .map(([k, v]) => {
          let cls = "choice";
          if (learn.selectedCheck === k) cls += " selected";
          if (learn.checkRevealed) {
            if (k === section.answer) cls += " correct";
            if (learn.selectedCheck === k && k !== section.answer) cls += " wrong";
          }
          return `<button class="${cls}" data-c="${k}" ${learn.checkRevealed && learn.selectedCheck === section.answer ? "disabled" : ""}>
            <span class="letter">${k}</span><span>${escapeHtml(v)}</span></button>`;
        })
        .join("");
      body = `<span class="tag tag-check">Concept check</span>
        <h3 class="text-base font-semibold tracking-tight">${escapeHtml(section.title)}</h3>
        <div class="body mt-3">${escapeHtml(section.prompt)}</div>
        <div class="mt-3">${choices}</div>
        <div class="feedback ${learn.checkRevealed ? "show " + (learn.selectedCheck === section.answer ? "ok" : "bad") : ""}">
          ${learn.checkRevealed
            ? learn.selectedCheck === section.answer
              ? `<strong>Correct.</strong> ${escapeHtml(section.explain || "")}`
              : `<strong>Not yet.</strong> ${escapeHtml(section.explain || "Try again.")}`
            : ""}
        </div>
        <div class="row mt-4">
          <button class="btn-secondary grow" id="btnSubmitCheck" ${learn.selectedCheck && !learn.checkRevealed ? "" : "disabled"}>Check</button>
          <button class="btn-primary grow" id="btnMarkNext" ${learn.checkRevealed && learn.selectedCheck === section.answer ? "" : "disabled"}>Continue</button>
        </div>`;
    }

    const topicHint = (lesson._topics || [])
      .map((t) => (window.SOA_TOPIC_GUIDES || {})[t]?.label || t)
      .filter(Boolean)
      .join(" · ");
    root.innerHTML = `
      <div class="card">
        <div class="flex items-center justify-between gap-2 text-xs text-mute">
          <span>Module ${learn.lessonIndex + 1}/${learn.lessonIds.length} · ~${lesson.minutes || "?"} min</span>
          <span>Section ${learn.sectionIndex + 1}/${lesson.sections.length}</span>
        </div>
        <h2 class="mt-2 text-lg font-semibold tracking-tight">${escapeHtml(lesson.title)}</h2>
        ${topicHint ? `<p class="mt-1 text-xs font-medium text-brand">Aligned to: ${escapeHtml(topicHint)}</p>` : ""}
        <p class="mt-1 text-xs text-mute">Progress is saved to cloud immediately when signed in — no re-take on other devices.</p>
        <div class="stepper">${dots}</div>
        <div class="lesson-section">${body}</div>
        <button class="btn-ghost w-full mt-3" id="btnExitLearn">Save & return to Today</button>
      </div>`;

    $("#btnExitLearn").onclick = () => {
      saveState({ immediate: true });
      learn = null;
      showView("home");
      renderAll();
    };
    const mark = $("#btnMarkNext");
    if (mark) {
      mark.onclick = () => {
        if (section.type !== "check") markSectionDone();
        advanceLearn();
      };
    }
    const grokB = $("#btnGrokSec");
    if (grokB) grokB.onclick = () => openGrok(teachGrokPrompt(lesson, section));
    const sub = $("#btnSubmitCheck");
    if (sub) sub.onclick = submitCheck;
    root.querySelectorAll("button[data-c]").forEach((btn) => {
      btn.onclick = () => {
        if (learn.checkRevealed && learn.selectedCheck === section.answer) return;
        if (learn.checkRevealed && learn.selectedCheck !== section.answer) learn.checkRevealed = false;
        learn.selectedCheck = btn.dataset.c;
        renderLearn();
      };
    });
    renderMath(root);
    refreshIcons();
  }

  function questionBodyHtml(q) {
    const hasImg = Array.isArray(q.images) && q.images.length > 0;
    const mode = hasImg ? (quizDisplayMode === "text" ? "text" : "image") : "text";
    const toggle = hasImg
      ? `<div class="mode-toggle">
          <button type="button" data-mode="image" class="${mode === "image" ? "active" : ""}">Official PDF</button>
          <button type="button" data-mode="text" class="${mode === "text" ? "active" : ""}">Text / LaTeX</button>
        </div>`
      : "";
    if (mode === "image" && hasImg) {
      return (
        toggle +
        `<p class="text-xs font-medium text-brand mb-1">Official SOA layout · tap image to enlarge</p>
        <div class="q-images">
          ${q.images.map((src, i) => `<img src="./${src}?v=4" alt="Q${q.number}-${i}" data-full="./${src}?v=4" />`).join("")}
        </div>
        <div id="imgFail" class="img-error" style="display:none">Image failed to load. Serve via <code>python -m http.server</code> from <code>app/</code> and hard-refresh.</div>
        <p class="text-xs text-mute">Select A–E below after reading the figure.</p>`
      );
    }
    return (
      toggle +
      `<div class="lock-banner warn mb-3">Text mode may omit symbols. Prefer Official PDF when available.</div>
       <div class="quiz-stem" id="quizStemText">${escapeHtml(q.stem)}</div>`
    );
  }

  function renderQuiz() {
    const root = $("#view-quiz");
    if (!root) return;

    if (quiz?.finished) {
      const pct = quiz.total ? Math.round((100 * quiz.correct) / quiz.total) : 0;
      root.innerHTML = `
        <div class="card text-center py-8">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-soft text-brand">
            <i data-lucide="check" class="h-7 w-7"></i>
          </div>
          <h2 class="mt-4 text-xl font-semibold tracking-tight">Session complete</h2>
          <p class="mt-2 text-sm text-mute">Clean work. Review misses while they’re fresh.</p>
          <div class="mt-6 flex justify-center">${ringSvg(pct, 100)}</div>
          <p class="mt-3 text-sm font-medium">${quiz.correct} correct of recent answers logged today</p>
          <div class="mt-6 space-y-2">
            <button class="btn-primary w-full" id="btnQuizHome">Back to Today</button>
            <button class="btn-secondary w-full" id="btnQuizWrong">Open wrong pool</button>
          </div>
        </div>`;
      $("#btnQuizHome").onclick = () => { quiz = null; showView("home"); renderAll(); };
      $("#btnQuizWrong").onclick = () => { quiz = null; showView("wrong"); renderWrong(); };
      refreshIcons();
      return;
    }

    const q = currentQuestion();
    if (!q) {
      root.innerHTML = `
        <div class="card">
          <h2 class="text-lg font-semibold">Quiz</h2>
          <p class="mt-1 text-sm text-mute">Complete the lesson first, then run today’s set.</p>
          <button class="btn-primary w-full mt-4" id="btnQuizFromEmpty">Start quiz</button>
        </div>`;
      $("#btnQuizFromEmpty").onclick = () => startQuiz();
      refreshIcons();
      return;
    }

    const n = quiz.index + 1;
    const total = quiz.queue.length;
    const hasImg = Array.isArray(q.images) && q.images.length > 0;
    if (hasImg && !quiz._modeTouched) quizDisplayMode = "image";
    const showingImage = hasImg && quizDisplayMode !== "text";

    root.innerHTML = `
      <div class="card">
        <div class="flex items-center justify-between text-xs text-mute">
          <span>Question ${n} of ${total}${hasImg ? " · PDF" : ""}</span>
          <span class="font-medium text-slate-600">${escapeHtml(q.id)}</span>
        </div>
        <div class="mt-2 h-1 overflow-hidden rounded-full bg-slate-100">
          <div class="h-full rounded-full bg-brand transition-all duration-500" style="width:${(100 * n) / total}%"></div>
        </div>
        <div id="qBody" class="mt-4">${questionBodyHtml(q)}</div>
        <div id="choices" class="mt-2"></div>
        <div class="feedback" id="feedback"></div>
        <div class="row mt-4">
          <button class="btn-secondary grow" id="btnSubmit" ${quiz.selected && !quiz.revealed ? "" : "disabled"}>Check</button>
          <button class="btn-primary grow" id="btnNext" style="display:${quiz.revealed ? "inline-flex" : "none"}">Next</button>
        </div>
        <div class="row mt-2">
          <button class="btn-grok grow" id="btnGrokQ"><i data-lucide="message-circle" class="h-4 w-4"></i> Ask Grok</button>
          <button class="btn-ghost grow" id="btnQuitQuiz">End session</button>
        </div>
      </div>`;

    $("#qBody")?.querySelectorAll("[data-mode]").forEach((btn) => {
      btn.onclick = () => {
        quizDisplayMode = btn.dataset.mode;
        quiz._modeTouched = true;
        renderQuiz();
      };
    });
    $("#qBody")?.querySelectorAll("img").forEach((img) => {
      img.onerror = () => {
        const box = $("#imgFail");
        if (box) box.style.display = "block";
        img.style.display = "none";
      };
      img.onclick = () => openLightbox(img.getAttribute("data-full") || img.src);
    });

    const box = $("#choices");
    for (const letter of ["A", "B", "C", "D", "E"]) {
      if (!q.choices?.[letter] && !hasImg) continue;
      const label =
        showingImage || !q.choices?.[letter] || String(q.choices[letter]).trim().length < 3
          ? `Choice ${letter}`
          : q.choices[letter];
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice";
      btn.innerHTML = `<span class="letter">${letter}</span><span>${escapeHtml(label)}</span>`;
      if (quiz.selected === letter) btn.classList.add("selected");
      if (quiz.revealed) {
        if (q.answer === letter) btn.classList.add("correct");
        if (quiz.selected === letter && quiz.selected !== q.answer) btn.classList.add("wrong");
        btn.disabled = true;
      } else {
        btn.onclick = () => {
          quiz.selected = letter;
          renderQuiz();
        };
      }
      box.appendChild(btn);
    }

    const fb = $("#feedback");
    if (quiz.revealed) {
      fb.classList.add("show", quiz.selected === q.answer ? "ok" : "bad");
      fb.innerHTML =
        quiz.selected === q.answer
          ? `<div class="flex items-start gap-2"><i data-lucide="check-circle-2" class="h-5 w-5 text-ok shrink-0"></i><div><strong>Correct</strong> · +10 XP</div></div>`
          : `<div class="flex items-start gap-2"><i data-lucide="x-circle" class="h-5 w-5 text-bad shrink-0"></i><div><strong>Not quite.</strong> Answer key: <strong>${q.answer || "?"}</strong>. Saved to wrong pool.</div></div>`;
    }

    $("#btnSubmit").onclick = submitAnswer;
    $("#btnNext").onclick = nextQuestion;
    $("#btnGrokQ").onclick = () => openGrok(explainPrompt(q, quiz.selected));
    $("#btnQuitQuiz").onclick = () => {
      quiz = null;
      showView("home");
      renderAll();
    };
    renderMath($("#quizStemText"));
    refreshIcons();
  }

  function openLightbox(src) {
    let lb = $("#lightbox");
    if (!lb) {
      lb = document.createElement("div");
      lb.id = "lightbox";
      lb.className = "lightbox";
      lb.innerHTML = `<button type="button" class="lightbox-close" id="lbClose">Close</button><img id="lbImg" alt="Full question" />`;
      document.body.appendChild(lb);
      lb.addEventListener("click", (e) => {
        if (e.target.id === "lightbox" || e.target.id === "lbClose") lb.classList.remove("show");
      });
    }
    const im = $("#lbImg");
    if (im) im.src = src;
    lb.classList.add("show");
  }

  function renderPath() {
    const root = $("#view-path");
    if (!root) return;
    const days = curriculum?.days || [];
    const t = todayISO();
    const start = Math.max(0, days.findIndex((d) => d.date >= t) - 2);
    const slice = days.slice(start, start + 14);
    root.innerHTML = `
      <div class="card">
        <h2 class="text-lg font-semibold tracking-tight">Learning path</h2>
        <p class="mt-1 text-sm text-mute">Upcoming days in your Exam P plan.</p>
        <div class="mt-4">
          ${slice.map((d) => {
            const st = dayStats(d.date);
            const cls = d.date === t ? "today" : st.done ? "done" : "";
            const mark = st.done ? "✓" : d.date === t ? "•" : String(d.dayIndex + 1);
            return `<div class="path-node ${cls}">
              <div class="path-dot">${mark}</div>
              <div class="min-w-0">
                <div class="text-sm font-semibold truncate">${escapeHtml(d.title)}</div>
                <div class="text-xs text-mute mt-0.5">${d.date} · Learn ${st.lessonPct}% · ${st.answered}/${d.questionTarget} Q</div>
              </div>
              <button class="btn-secondary" style="padding:0.5rem 0.75rem;font-size:0.75rem" data-go="${d.date}" ${d.date > t ? "disabled" : ""}>Open</button>
            </div>`;
          }).join("")}
        </div>
      </div>`;
    root.querySelectorAll("[data-go]").forEach((btn) => {
      btn.onclick = () => {
        const date = btn.dataset.go;
        if (!areAllLessonsComplete(date)) startLearn(date);
        else startQuiz(date);
      };
    });
    refreshIcons();
  }

  function renderWrong() {
    const root = $("#view-wrong");
    if (!root) return;
    const list = wrongList();
    root.innerHTML = `
      <div class="card">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold tracking-tight">Wrong pool</h2>
            <p class="mt-1 text-sm text-mute">Misses mix back into daily quizzes (~30%).</p>
          </div>
          <button class="btn-secondary" id="btnSunday" style="white-space:nowrap"><i data-lucide="sparkles" class="h-4 w-4"></i> Sunday recap</button>
        </div>
        <div class="mt-4">
          ${list.length
            ? list.map((w) => `
              <div class="list-item">
                <div class="min-w-0">
                  <div class="text-sm font-semibold">${escapeHtml(w.id)} · missed ${w.count}×</div>
                  <div class="text-xs text-mute mt-0.5">LO ${escapeHtml(w.lo || "?")} · ${(w.topics || []).join(", ")}</div>
                  <div class="text-xs text-mute mt-1 line-clamp-2">${escapeHtml(w.stemPreview || "")}</div>
                </div>
                <div class="flex flex-col gap-1.5 shrink-0">
                  <button class="btn-secondary" style="padding:0.45rem 0.7rem;font-size:0.75rem" data-review="${w.id}">Review</button>
                  <button class="btn-grok" style="padding:0.45rem 0.7rem;font-size:0.75rem" data-grok="${w.id}">Grok</button>
                </div>
              </div>`).join("")
            : `<div class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-10 text-center">
                <i data-lucide="inbox" class="mx-auto h-8 w-8 text-slate-300"></i>
                <p class="mt-3 text-sm font-medium text-slate-700">Pool is empty</p>
                <p class="mt-1 text-xs text-mute">Missed quiz items will land here automatically.</p>
              </div>`}
        </div>
      </div>`;

    $("#btnSunday").onclick = () => {
      openGrok(sundayRecapPrompt(list));
      downloadJSON(`sunday_recap_${todayISO()}.json`, { generatedAt: new Date().toISOString(), date: todayISO(), wrong: list });
      toast("Grok opened · JSON downloaded");
    };
    root.querySelectorAll("[data-review]").forEach((btn) => {
      btn.onclick = () => {
        quiz = { date: todayISO(), queue: [btn.dataset.review], index: 0, selected: null, revealed: false, _modeTouched: false };
        quizDisplayMode = "image";
        showView("quiz");
        renderQuiz();
      };
    });
    root.querySelectorAll("[data-grok]").forEach((btn) => {
      btn.onclick = () => {
        const q = qById.get(btn.dataset.grok);
        if (q) openGrok(explainPrompt(q));
      };
    });
    refreshIcons();
  }

  function renderStats() {
    const root = $("#view-stats");
    if (!root) return;
    const stats = dayStats();
    const acc = accuracyOverall();
    const wrong = wrongList();
    const loCounts = {};
    wrong.forEach((w) => {
      const k = w.lo || "unknown";
      loCounts[k] = (loCounts[k] || 0) + w.count;
    });
    const topLos = Object.entries(loCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);

    root.innerHTML = `
      <div class="card">
        <h2 class="text-lg font-semibold tracking-tight">Progress</h2>
        <p class="mt-1 text-sm text-mute">A calm snapshot of your Exam P prep.</p>
        <div class="mt-6 flex items-center justify-around">
          ${ringSvg(stats.overall, 96)}
          ${ringSvg(acc == null ? 0 : acc, 96)}
        </div>
        <div class="mt-2 grid grid-cols-2 text-center text-xs text-mute">
          <div>Today’s completion</div>
          <div>Lifetime accuracy${acc == null ? " (n/a)" : ""}</div>
        </div>
        <div class="mt-6 grid grid-cols-3 gap-2">
          <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 text-center">
            <div class="text-lg font-semibold tabular-nums">${state.streak}</div>
            <div class="text-[11px] text-mute mt-0.5">Streak</div>
          </div>
          <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 text-center">
            <div class="text-lg font-semibold tabular-nums">${state.xp}</div>
            <div class="text-[11px] text-mute mt-0.5">XP</div>
          </div>
          <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 text-center">
            <div class="text-lg font-semibold tabular-nums">${(state.history || []).length}</div>
            <div class="text-[11px] text-mute mt-0.5">Attempts</div>
          </div>
        </div>
      </div>
      <div class="card">
        <h3 class="text-sm font-semibold">Weakness by LO</h3>
        <div class="mt-3 space-y-2">
          ${topLos.length
            ? topLos.map(([lo, c]) => `
              <div>
                <div class="flex justify-between text-xs mb-1"><span class="font-medium">${escapeHtml(lo)}</span><span class="text-mute">${c}</span></div>
                <div class="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                  <div class="h-full rounded-full bg-brand" style="width:${Math.min(100, c * 12)}%"></div>
                </div>
              </div>`).join("")
            : `<p class="text-sm text-mute">No weakness data yet — complete a few quizzes.</p>`}
        </div>
      </div>`;
    refreshIcons();
  }

  function renderSettings() {
    const root = $("#view-settings");
    if (!root) return;
    const cloud = window.SOACloud;
    const account = cloud?.user
      ? `<p class="text-sm"><span class="font-medium">Signed in</span> · ${escapeHtml(cloud.user.email || cloud.user.uid)}
           <br><span class="text-xs text-mute">Status: ${cloud.status}${cloud.lastError ? " — " + escapeHtml(cloud.lastError) : ""}</span></p>
         <div class="row mt-3">
           <button class="btn-secondary grow" id="btnCloudPull">Pull</button>
           <button class="btn-secondary grow" id="btnCloudPush">Push</button>
           <button class="btn-danger grow" id="btnSignOut">Sign out</button>
         </div>`
      : `<p class="text-sm text-mute">Not signed in. Progress stays on this browser until you export or enable cloud.</p>
         <button class="btn-primary w-full mt-3" id="btnOpenAuth">Sign in / Create account</button>`;

    root.innerHTML = `
      <div class="card">
        <h2 class="text-lg font-semibold tracking-tight">Account</h2>
        <div class="mt-3">${account}</div>
        ${!cloud || cloud.status === "need-config" ? `<div class="lock-banner warn mt-3">Cloud optional. See FIREBASE_SETUP.md for free Firebase wiring.</div>` : ""}
      </div>
      <div class="card">
        <h2 class="text-lg font-semibold tracking-tight">Study settings</h2>
        <div class="row mt-3">
          <button class="btn-secondary grow" id="btnNotif">Enable notifications</button>
          <button class="btn-secondary grow" id="btnTestNotif">Test</button>
        </div>
        <label class="block text-xs font-medium text-mute mt-4">Reminder hour</label>
        <input id="reminderHour" type="number" min="0" max="23" value="${state.reminderHour}" class="field mt-1" />
        <label class="block text-xs font-medium text-mute mt-3">Daily question goal</label>
        <input id="dailyGoal" type="number" min="5" max="40" value="${state.settings.dailyGoal}" class="field mt-1" />
        <button class="btn-primary w-full mt-4" id="btnSaveSettings">Save settings</button>
      </div>
      <div class="card">
        <h2 class="text-lg font-semibold tracking-tight">Backup</h2>
        <p class="mt-1 text-sm text-mute">Export before switching devices if you skip cloud.</p>
        <div class="row mt-3">
          <button class="btn-secondary grow" id="btnExport">Export JSON</button>
          <button class="btn-secondary grow" id="btnImport">Import JSON</button>
        </div>
        <textarea class="export-box mt-3" id="importBox" placeholder="Paste exported JSON here"></textarea>
        <button class="btn-danger w-full mt-3" id="btnReset">Reset local progress</button>
      </div>
      <div class="card">
        <p class="text-xs text-mute">Questions loaded: ${questions.length} · Lessons: ${Object.keys(lessons).length} · Days: ${curriculum?.days?.length || 0}</p>
      </div>`;

    $("#btnOpenAuth")?.addEventListener("click", () => openAuthModal("signin"));
    $("#btnSignOut")?.addEventListener("click", async () => {
      await SOACloud.signOut();
      toast("Signed out");
      renderSettings();
      renderAccountChip();
    });
    $("#btnCloudPull")?.addEventListener("click", async () => {
      await pullAndMergeCloud();
      saveState({ immediate: true });
      renderAll();
      toast("Merged from cloud");
    });
    $("#btnCloudPush")?.addEventListener("click", async () => {
      await SOACloud.saveProgress(state, true);
      toast("Pushed to cloud");
      renderAccountChip();
    });
    $("#btnNotif").onclick = () => enableNotifications();
    $("#btnTestNotif").onclick = () => {
      if (navigator.serviceWorker?.controller) {
        navigator.serviceWorker.controller.postMessage({ type: "NOTIFY_TEST", body: "Test notification" });
      } else if (Notification.permission === "granted") {
        new Notification("SOA Grind", { body: "Test notification", icon: "./icons/icon-192.svg" });
      } else toast("Enable notifications first");
    };
    $("#btnSaveSettings").onclick = () => {
      state.reminderHour = Number($("#reminderHour").value) || 19;
      state.settings.dailyGoal = Number($("#dailyGoal").value) || 20;
      saveState({ immediate: true });
      toast("Settings saved");
    };
    $("#btnExport").onclick = () => {
      downloadJSON(`soa_grind_progress_${todayISO()}.json`, state);
      toast("Exported");
    };
    $("#btnImport").onclick = () => {
      try {
        state = { ...DEFAULT_STATE(), ...JSON.parse($("#importBox").value) };
        saveState({ immediate: true });
        renderAll();
        toast("Imported");
      } catch {
        toast("Invalid JSON");
      }
    };
    $("#btnReset").onclick = () => {
      if (confirm("Reset all local progress on this device?")) {
        state = DEFAULT_STATE();
        saveState({ immediate: true });
        renderAll();
        toast("Local progress reset");
      }
    };
    refreshIcons();
  }

  function renderAll() {
    renderChrome();
    if (currentView === "home") renderHome();
    if (currentView === "learn") renderLearn();
    if (currentView === "quiz") renderQuiz();
    if (currentView === "exam") window.SOAExam?.onShow?.();
    if (currentView === "path") renderPath();
    if (currentView === "wrong") renderWrong();
    if (currentView === "stats") renderStats();
    if (currentView === "settings") renderSettings();
    refreshIcons();
  }

  function bindExamModule() {
    if (!window.SOAExam) return;
    window.SOAExam.bind({
      get state() {
        return state;
      },
      set state(v) {
        state = v;
      },
      questions,
      qById,
      saveState,
      toast,
      showView,
      escapeHtml,
      openGrok,
      explainPrompt,
      openLightbox,
      refreshIcons,
      renderMath,
    });
  }

  async function boot() {
    if (!localStorage.getItem(STORAGE_KEY)) {
      const idb = await idbLoad();
      if (idb && (idb.xp || Object.keys(idb.days || {}).length)) {
        state = { ...DEFAULT_STATE(), ...idb };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      }
    }

    const [cRes, qRes, lRes] = await Promise.all([
      fetch("./data/curriculum.json"),
      fetch("./data/questions.json"),
      fetch("./data/lessons.json"),
    ]);
    curriculum = await cRes.json();
    questions = await qRes.json();
    lessons = await lRes.json();
    qById = new Map(questions.map((q) => [q.id, q]));

    if (window.SOACloud) {
      await SOACloud.init();
      SOACloud.onChange(() => {
        renderAccountChip();
        if (currentView === "settings") renderSettings();
      });
      if (SOACloud.user) await pullAndMergeCloud();
    }

    bindExamModule();

    document.querySelectorAll(".nav-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const v = btn.dataset.view;
        if (v === "exam") {
          showView("exam");
          window.SOAExam?.onShow?.();
          return;
        }
        if (v === "quiz") {
          // Block daily quiz navigation into exam rules: allow quiz as usual
          if (state.activeExam?.status === "in_progress") {
            if (!confirm("You have an exam in progress. Leave exam mode? (Progress is saved.)")) {
              showView("exam");
              window.SOAExam?.onShow?.();
              return;
            }
            window.SOAExam?.stopTicker?.();
          }
          if (!quiz) startQuiz();
          else {
            showView("quiz");
            renderQuiz();
          }
          return;
        }
        if (v === "learn") {
          if (state.activeExam?.status === "in_progress") {
            window.SOAExam?.stopTicker?.();
          }
          if (!learn) startLearn();
          else {
            showView("learn");
            renderLearn();
          }
          return;
        }
        if (state.activeExam?.status === "in_progress" && v !== "exam") {
          window.SOAExam?.stopTicker?.();
        }
        showView(v);
        if (v === "home") renderHome();
        if (v === "path") renderPath();
        if (v === "wrong") renderWrong();
        if (v === "stats") renderStats();
        if (v === "settings") renderSettings();
      });
    });

    $("#accountChip")?.addEventListener("click", () => {
      if (window.SOACloud?.user) {
        showView("settings");
        renderSettings();
      } else openAuthModal("signin");
    });
    $("#authClose")?.addEventListener("click", closeAuthModal);
    $("#authModal")?.addEventListener("click", (ev) => {
      if (ev.target.id === "authModal") closeAuthModal();
    });
    $("#authForm")?.addEventListener("submit", handleAuthSubmit);
    $("#authSwitch")?.addEventListener("click", () => {
      const mode = $("#authModal").dataset.mode === "signup" ? "signin" : "signup";
      openAuthModal(mode);
    });

    if ("serviceWorker" in navigator) {
      try {
        const keys = await caches.keys();
        await Promise.all(keys.filter((k) => k.startsWith("soa-grind") && k !== "soa-grind-v6").map((k) => caches.delete(k)));
        await navigator.serviceWorker.register("./sw.js?v=6");
      } catch (e) {
        console.warn(e);
      }
    }

    showView("home");
    renderAll();
    maybeRemind();
    if (window.SOACloud?.ready && !SOACloud.user && !sessionStorage.getItem("soa_auth_nudge")) {
      sessionStorage.setItem("soa_auth_nudge", "1");
      setTimeout(() => toast("Optional: sign in to sync across devices"), 1400);
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})();

/* SOA Grind — teach-first Exam P coach */
(() => {
  "use strict";

  const STORAGE_KEY = "soa_grind_v1";
  const IDB_NAME = "soa_grind_db";
  const IDB_STORE = "progress";
  const DEFAULT_STATE = () => ({
    version: 2,
    xp: 0,
    streak: 0,
    lastActiveDate: null,
    lastReminderDate: null,
    notificationsEnabled: false,
    reminderHour: 19,
    updatedAt: 0,
    days: {}, // date -> { readingsDone, answered, completed, lessons: {...} }
    wrongPool: {},
    history: [],
    settings: { dailyGoal: 20, grokBase: "https://grok.com/?q=" },
  });

  let state = loadState();
  let curriculum = null;
  let questions = [];
  let lessons = {};
  let qById = new Map();
  let quiz = null;
  let learn = null; // { date, lessonIds, lessonIndex, sectionIndex, selectedCheck, checkRevealed }
  let currentView = "home";
  let cloudBusy = false;

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
      console.warn("localStorage save failed", e);
    }
    idbSave(state);
    // Cloud sync when logged in
    if (window.SOACloud && SOACloud.user) {
      SOACloud.saveProgress(state, !!opts.immediate).then((ok) => {
        renderAccountChip();
        if (opts.toast && ok) toast("Cloud saved ✓");
      });
    }
    renderAccountChip();
  }

  // IndexedDB backup — survives longer than accidental localStorage wipes in some cases
  function idbSave(data) {
    try {
      const req = indexedDB.open(IDB_NAME, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(IDB_STORE)) db.createObjectStore(IDB_STORE);
      };
      req.onsuccess = () => {
        const db = req.result;
        const tx = db.transaction(IDB_STORE, "readwrite");
        tx.objectStore(IDB_STORE).put(data, "main");
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
          const db = req.result;
          const tx = db.transaction(IDB_STORE, "readonly");
          const g = tx.objectStore(IDB_STORE).get("main");
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
    const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
  }
  function parseISO(s) {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
  }
  function daysUntil(iso) {
    return Math.round((parseISO(iso) - parseISO(todayISO())) / 86400000);
  }
  function ensureDay(date) {
    if (!state.days[date]) {
      state.days[date] = { readingsDone: [], answered: {}, completed: false, lessons: {} };
    }
    if (!state.days[date].lessons) state.days[date].lessons = {};
    return state.days[date];
  }
  function dayPlan(date = todayISO()) {
    return curriculum?.days?.find((d) => d.date === date) || null;
  }

  function lessonIdsFor(plan) {
    if (!plan) return [];
    if (plan.lessonIds?.length) return plan.lessonIds.filter((id) => lessons[id]);
    if (plan.lessonId && lessons[plan.lessonId]) return [plan.lessonId];
    return [];
  }

  function ensureLessonProgress(date, lessonId) {
    const day = ensureDay(date);
    if (!day.lessons[lessonId]) {
      day.lessons[lessonId] = { sectionDone: [], checks: {} };
    }
    return day.lessons[lessonId];
  }

  function isLessonComplete(date, lessonId) {
    const lesson = lessons[lessonId];
    if (!lesson) return true;
    const prog = ensureLessonProgress(date, lessonId);
    const sections = lesson.sections || [];
    for (const s of sections) {
      if (s.type === "check") {
        if (!prog.checks[s.id]) return false;
      } else {
        if (!prog.sectionDone.includes(s.id)) return false;
      }
    }
    return true;
  }

  function areAllLessonsComplete(date = todayISO()) {
    const plan = dayPlan(date);
    const ids = lessonIdsFor(plan);
    if (!ids.length) return true;
    return ids.every((id) => isLessonComplete(date, id));
  }

  function lessonProgressPct(date = todayISO()) {
    const plan = dayPlan(date);
    const ids = lessonIdsFor(plan);
    if (!ids.length) return 100;
    let total = 0;
    let done = 0;
    for (const id of ids) {
      const lesson = lessons[id];
      if (!lesson) continue;
      const prog = ensureLessonProgress(date, id);
      for (const s of lesson.sections || []) {
        total += 1;
        if (s.type === "check" ? prog.checks[s.id] : prog.sectionDone.includes(s.id)) done += 1;
      }
    }
    return total ? Math.round((100 * done) / total) : 100;
  }

  // ---------- Grok ----------
  function grokUrl(prompt) {
    return (state.settings.grokBase || "https://grok.com/?q=") + encodeURIComponent(prompt);
  }
  function openGrok(prompt) {
    window.open(grokUrl(prompt), "_blank", "noopener,noreferrer");
  }
  function explainPrompt(q, choice) {
    const choices = Object.entries(q.choices || {})
      .map(([k, v]) => `(${k}) ${v}`)
      .join("\n");
    return (
      `I'm preparing for SOA Exam P. Please tutor me on this multiple-choice question.\n\n` +
      `Question ${q.number} (${q.id}):\n${q.stem}\n\nChoices:\n${choices}\n\n` +
      (choice ? `I selected (${choice}).\n` : "") +
      (q.answer ? `Official sample answer key letter: ${q.answer}.\n` : "") +
      `Please: (1) explain the setup and syllabus concept, (2) show a clean solution, ` +
      `(3) list common traps, (4) give 2 similar practice questions with answers.`
    );
  }
  function teachGrokPrompt(lesson, section) {
    return (
      `I'm studying SOA Exam P. Topic lesson: "${lesson.title}".\n` +
      `Section: ${section.title}\nContent:\n${section.body || section.setup || ""}\n\n` +
      `Please re-explain more slowly with one extra example and a common exam trap.`
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
      `You are my SOA Exam P coach. Here is my WRONG QUESTION POOL.\n` +
      `Diagnose weaknesses and create a Sunday recap:\n` +
      `- Top 5 weakness themes\n- Mini formula checklist\n` +
      `- 12 NEW similar MC questions (A–E) with answers and brief solutions\n` +
      `- A 60-minute revision plan\n\nWRONG POOL:\n${body || "(empty)"}`
    );
  }

  // ---------- progress ----------
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
    return {
      target,
      answered: answeredIds.length,
      correct,
      lessonPct: Math.round(lessonPct * 100),
      lessonDone,
      overall,
      done,
    };
  }

  function wrongList() {
    return Object.entries(state.wrongPool)
      .map(([id, meta]) => ({ id, ...meta }))
      .sort((a, b) => b.count - a.count || (b.lastWrong || "").localeCompare(a.lastWrong || ""));
  }

  // ---------- learn session ----------
  function startLearn(date = todayISO()) {
    const plan = dayPlan(date);
    const ids = lessonIdsFor(plan);
    if (!ids.length) {
      toast("No lesson module for this day");
      return;
    }
    learn = { date, lessonIds: ids, lessonIndex: 0, sectionIndex: 0, selectedCheck: null, checkRevealed: false };
    // jump to first incomplete section
    seekFirstIncomplete();
    updateStreakOnActivity();
    saveState();
    showView("learn");
    renderLearn();
  }

  function seekFirstIncomplete() {
    if (!learn) return;
    for (let li = 0; li < learn.lessonIds.length; li++) {
      const lesson = lessons[learn.lessonIds[li]];
      const prog = ensureLessonProgress(learn.date, lesson.id);
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
    // all complete — stay on last
    const lastL = learn.lessonIds.length - 1;
    learn.lessonIndex = lastL;
    learn.sectionIndex = (lessons[learn.lessonIds[lastL]].sections.length || 1) - 1;
  }

  function currentLesson() {
    if (!learn) return null;
    return lessons[learn.lessonIds[learn.lessonIndex]] || null;
  }
  function currentSection() {
    const lesson = currentLesson();
    if (!lesson) return null;
    return lesson.sections[learn.sectionIndex] || null;
  }

  function markSectionDone() {
    const lesson = currentLesson();
    const section = currentSection();
    if (!lesson || !section) return;
    const prog = ensureLessonProgress(learn.date, lesson.id);
    if (section.type === "check") return; // checks handled separately
    if (!prog.sectionDone.includes(section.id)) {
      prog.sectionDone.push(section.id);
      state.xp += 5;
    }
    // also mirror to readingsDone for old UI compatibility
    const day = ensureDay(learn.date);
    const plan = dayPlan(learn.date);
    (plan?.readings || []).forEach((r) => {
      if (!day.readingsDone.includes(r.id)) day.readingsDone.push(r.id);
    });
    updateStreakOnActivity();
    saveState();
  }

  function advanceLearn() {
    const lesson = currentLesson();
    if (!lesson) return;
    if (learn.sectionIndex < lesson.sections.length - 1) {
      learn.sectionIndex += 1;
      learn.selectedCheck = null;
      learn.checkRevealed = false;
      renderLearn();
      renderChrome();
      return;
    }
    if (learn.lessonIndex < learn.lessonIds.length - 1) {
      learn.lessonIndex += 1;
      learn.sectionIndex = 0;
      learn.selectedCheck = null;
      learn.checkRevealed = false;
      renderLearn();
      renderChrome();
      return;
    }
    // finished all
    toast("Learn session complete — quiz unlocked 🎯");
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
      const prog = ensureLessonProgress(learn.date, lesson.id);
      prog.checks[section.id] = true;
      state.xp += 8;
      updateStreakOnActivity();
      saveState();
    }
    renderLearn();
    renderChrome();
  }

  // ---------- quiz ----------
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
        if (q.answer && !done.has(q.id) && !queue.includes(q.id) && (q.topics || []).some((t) => prefs.has(t))) {
          queue.push(q.id);
        }
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
      toast("Finish the Learn session first");
      startLearn(date);
      return;
    }
    const queue = buildQueue(date);
    if (!queue.length) {
      toast("No questions left for today — great work!");
      return;
    }
    quiz = { date, queue, index: 0, selected: null, revealed: false };
    updateStreakOnActivity();
    saveState();
    showView("quiz");
    renderQuiz();
  }

  function currentQuestion() {
    if (!quiz) return null;
    return qById.get(quiz.queue[quiz.index]) || null;
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
    }
    saveState();
    renderQuiz();
    renderChrome();
  }

  function nextQuestion() {
    if (!quiz) return;
    if (quiz.index >= quiz.queue.length - 1) {
      quiz = null;
      showView("home");
      renderAll();
      toast("Session complete 🎯");
      return;
    }
    quiz.index += 1;
    quiz.selected = null;
    quiz.revealed = false;
    renderQuiz();
  }

  // ---------- notifications ----------
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
      navigator.serviceWorker.controller.postMessage({ type: "NOTIFY_TEST", body: "Reminders on ✅" });
    } else {
      new Notification("SOA Grind", { body: "Reminders enabled", icon: "./icons/icon-192.svg" });
    }
    toast("Notifications enabled");
  }
  function maybeRemind() {
    if (!state.notificationsEnabled || Notification.permission !== "granted") return;
    const t = todayISO();
    if (state.lastReminderDate === t) return;
    const stats = dayStats(t);
    if (stats.done) return;
    if (new Date().getHours() < (state.reminderHour || 19)) return;
    const body = !stats.lessonDone
      ? "Learn session still open — unlock today's quiz."
      : `Still ${Math.max(0, stats.target - stats.answered)} questions left. Streak ${state.streak}🔥`;
    if (navigator.serviceWorker?.controller) {
      navigator.serviceWorker.controller.postMessage({ type: "NOTIFY_TEST", body });
    } else {
      new Notification("SOA Grind", { body, icon: "./icons/icon-192.svg", tag: "soa-daily" });
    }
    state.lastReminderDate = t;
    saveState();
  }
  setInterval(maybeRemind, 60 * 60 * 1000);

  // ---------- render helpers ----------
  function $(sel) {
    return document.querySelector(sel);
  }
  function showView(name) {
    currentView = name;
    document.querySelectorAll(".view").forEach((el) => el.classList.toggle("active", el.id === `view-${name}`));
    document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.toggle("active", btn.dataset.view === name));
  }
  function toast(msg) {
    const el = $("#toast");
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

  function renderAccountChip() {
    const el = $("#accountChip");
    if (!el) return;
    const label = $("#accountBarLabel");
    const cta = $("#accountBarCta");
    const cloud = window.SOACloud;
    el.classList.remove("ok", "warn");

    if (!cloud || cloud.status === "need-config") {
      if (label) label.innerHTML = "Cloud not configured — open FIREBASE_SETUP.md";
      if (cta) cta.textContent = "Setup";
      el.classList.add("warn");
      el.title = "Firebase config missing";
      return;
    }
    if (cloud.user) {
      const short = cloud.user.email || cloud.user.uid;
      const mark =
        cloud.status === "syncing" ? "syncing…" : cloud.status === "error" ? "sync error" : "synced ✓";
      if (label) label.innerHTML = `Signed in as <strong>${escapeHtml(short)}</strong> · ${mark}`;
      if (cta) cta.textContent = "Account";
      el.title = cloud.status === "error" ? cloud.lastError || "Sync error" : `Signed in · ${cloud.status}`;
      el.classList.toggle("warn", cloud.status === "error");
      el.classList.toggle("ok", cloud.status === "synced" || cloud.status === "syncing");
    } else {
      if (label) label.innerHTML = "<strong>Cloud: Sign in</strong> to save progress on phone & PC";
      if (cta) cta.textContent = "Sign in";
      el.title = "Sign in to keep progress across devices";
      el.classList.add("warn");
    }
  }

  function renderChrome() {
    const stats = dayStats();
    $("#xpChip").innerHTML = `⚡ XP <strong>${state.xp}</strong>`;
    $("#streakChip").innerHTML = `🔥 <strong>${state.streak}</strong>`;
    $("#wrongChip").innerHTML = `❌ <strong>${Object.keys(state.wrongPool).length}</strong>`;
    $("#progressFill").style.width = `${stats.overall}%`;
    const cloud = window.SOACloud;
    const syncNote =
      cloud?.user && cloud.status === "synced"
        ? " · cloud✓"
        : cloud?.user && cloud.status === "syncing"
          ? " · syncing…"
          : cloud?.user
            ? " · cloud"
            : " · local only";
    $("#progressLabel").textContent = `Today ${stats.overall}% · Learn ${stats.lessonPct}% · Quiz ${stats.answered}/${stats.target}${syncNote}`;
    renderAccountChip();
  }

  function openAuthModal(mode = "signin") {
    const backdrop = $("#authModal");
    if (!backdrop) return;
    backdrop.classList.add("show");
    backdrop.dataset.mode = mode;
    $("#authTitle").textContent = mode === "signup" ? "Create account" : "Sign in";
    $("#authSubmit").textContent = mode === "signup" ? "Create account" : "Sign in";
    $("#authSwitch").textContent =
      mode === "signup" ? "Already have an account? Sign in" : "New here? Create account";
    $("#authError").textContent = "";
    const cloud = window.SOACloud;
    if (!cloud || cloud.status === "need-config") {
      $("#authHint").innerHTML =
        `Cloud login is not configured yet.<br>Follow <strong>FIREBASE_SETUP.md</strong> (5–10 min, free). Until then progress stays on this browser only — use Export/Import.`;
      $("#authForm").style.display = "none";
    } else {
      $("#authHint").textContent = "Same email on phone & PC keeps your streak, lessons, and wrong pool continuous.";
      $("#authForm").style.display = "block";
    }
  }

  function closeAuthModal() {
    $("#authModal")?.classList.remove("show");
  }

  async function handleAuthSubmit(e) {
    e.preventDefault();
    const cloud = window.SOACloud;
    if (!cloud || !cloud.ready) {
      toast("Configure Firebase first (see Settings)");
      return;
    }
    const email = $("#authEmail").value.trim();
    const password = $("#authPassword").value;
    const mode = $("#authModal").dataset.mode || "signin";
    $("#authError").textContent = "";
    cloudBusy = true;
    try {
      if (mode === "signup") await cloud.signUp(email, password);
      else await cloud.signIn(email, password);
      await pullAndMergeCloud();
      saveState({ immediate: true });
      closeAuthModal();
      toast(mode === "signup" ? "Account created — cloud sync on" : "Signed in — progress synced");
      renderAll();
    } catch (err) {
      $("#authError").textContent = friendlyAuthError(err);
    } finally {
      cloudBusy = false;
      renderAccountChip();
    }
  }

  function friendlyAuthError(err) {
    const code = err?.code || "";
    if (code.includes("email-already-in-use")) return "Email already registered — sign in instead.";
    if (code.includes("wrong-password") || code.includes("invalid-credential")) return "Wrong email or password.";
    if (code.includes("user-not-found")) return "No account with that email — create one.";
    if (code.includes("weak-password")) return "Password must be at least 6 characters.";
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
      console.warn("cloud pull failed", e);
      toast("Cloud load failed — using local progress");
    }
  }

  function renderHome() {
    const plan = dayPlan();
    const stats = dayStats();
    const target = curriculum?.examTarget || "2026-09-14";
    const left = daysUntil(target);
    const regLeft = daysUntil(curriculum?.registrationDeadline || "2026-08-12");

    if (!plan) {
      $("#homeCard").innerHTML = `<h2 class="hero-title">No lesson mapped for today</h2>
        <p class="muted">Curriculum covers 2026-07-12 → 2026-09-28.</p>`;
      $("#readingCard").innerHTML = "";
      return;
    }

    const locked = !stats.lessonDone;
    $("#homeCard").innerHTML = `
      <div class="row space-between">
        <span class="phase-pill">${plan.phase}</span>
        <span class="small muted">${plan.weekday} · ${plan.date}</span>
      </div>
      <h2 class="hero-title" style="margin-top:10px">${plan.title}</h2>
      <p class="muted small">Mode: ${plan.mode}${plan.fmLight ? " · light FM" : ""} · ${(plan.topicPrefs || []).join(", ")}</p>
      <div class="countdown">🎯 Exam P ${target} · ${left}d left${regLeft >= 0 ? ` · ⚠️ register in ${regLeft}d` : ""}</div>
      ${
        !(window.SOACloud && SOACloud.user)
          ? `<div class="lock-banner" style="margin-top:10px">☁ Progress is <strong>local-only</strong> until you sign in. Tap the cloud chip (top) or More → Account so phone & PC stay continuous.</div>`
          : `<div class="lock-banner" style="margin-top:10px;border-color:rgba(34,197,94,.4);color:#bbf7d0;background:rgba(34,197,94,.1)">☁ Signed in — progress auto-syncs to the cloud.</div>`
      }
      <div class="goal-grid">
        <div class="goal"><div class="num">${stats.lessonPct}%</div><div class="label">Learn session</div></div>
        <div class="goal"><div class="num">${stats.answered}/${stats.target}</div><div class="label">Quiz today</div></div>
        <div class="goal"><div class="num">${stats.correct}</div><div class="label">Correct</div></div>
        <div class="goal"><div class="num">${Object.keys(state.wrongPool).length}</div><div class="label">Wrong pool</div></div>
      </div>
      ${
        locked
          ? `<div class="lock-banner" style="margin-top:12px">🔒 Quiz locked until you finish today's <strong>Learn</strong> session (concept + examples + checks).</div>`
          : `<div class="lock-banner" style="margin-top:12px;border-color:rgba(34,197,94,.4);color:#bbf7d0;background:rgba(34,197,94,.1)">✅ Learn complete — quiz unlocked.</div>`
      }
      <div style="margin-top:12px;display:grid;gap:8px">
        <button class="btn-primary" id="btnLearn">${stats.lessonDone ? "Review learn session" : "Start learn session"}</button>
        <button class="btn-secondary" id="btnQuiz" ${locked ? "disabled" : ""}>${stats.done ? "Bonus practice" : "Start quiz (~20 Q)"}</button>
        <button class="btn-grok" id="btnGrokDay">Ask Grok about today's topic</button>
      </div>
    `;
    $("#btnLearn").onclick = () => startLearn();
    $("#btnQuiz").onclick = () => startQuiz();
    $("#btnGrokDay").onclick = () => {
      const L = lessons[plan.lessonId];
      openGrok(
        `SOA Exam P day ${plan.date}: ${plan.title}.\n` +
          `Teach me this topic like a patient coach: definitions, when to use it, 3 worked examples, common traps.\n` +
          `Lesson outline: ${L ? L.title : plan.title}`
      );
    };

    // lesson outline card
    const ids = lessonIdsFor(plan);
    $("#readingCard").innerHTML =
      `<h3>📘 Today's learn modules</h3>` +
      ids
        .map((id) => {
          const L = lessons[id];
          const done = isLessonComplete(plan.date, id);
          return `<div class="list-item">
            <div>
              <div style="font-weight:800">${done ? "✅" : "⬜"} ${L?.title || id}</div>
              <div class="small muted">${L?.minutes || "?"} min · LO ${(L?.lo || []).join(", ")} · ${(L?.sections || []).length} sections</div>
            </div>
          </div>`;
        })
        .join("") +
      `<p class="small muted" style="margin-top:8px">Each module teaches the concept, walks worked examples (with <em>why</em>), then a concept check. Quiz stays locked until checks pass.</p>`;
  }

  function renderLearn() {
    if (!learn) {
      $("#learnCard").innerHTML = `<p class="muted">No active learn session.</p>
        <button class="btn-primary" id="btnStartLearnEmpty">Start today's learn session</button>`;
      $("#btnStartLearnEmpty").onclick = () => startLearn();
      return;
    }
    const lesson = currentLesson();
    const section = currentSection();
    if (!lesson || !section) {
      $("#learnCard").innerHTML = `<p class="muted">Lesson missing data.</p>`;
      return;
    }
    const prog = ensureLessonProgress(learn.date, lesson.id);
    const totalSec = lesson.sections.length;
    const dots = lesson.sections
      .map((s, i) => {
        const ok = s.type === "check" ? !!prog.checks[s.id] : prog.sectionDone.includes(s.id);
        const cls = ok ? "done" : i === learn.sectionIndex ? "current" : "";
        return `<div class="step-dot ${cls}">${i + 1}</div>`;
      })
      .join("");

    let bodyHtml = "";
    if (section.type === "concept") {
      bodyHtml = `
        <span class="tag tag-concept">Concept</span>
        <h4>${escapeHtml(section.title)}</h4>
        <div class="body">${escapeHtml(section.body)}</div>
        <div class="row" style="margin-top:12px">
          <button class="btn-primary grow" id="btnMarkNext">I understand — next</button>
          <button class="btn-grok grow" id="btnGrokSec">Ask Grok to re-teach</button>
        </div>`;
    } else if (section.type === "example") {
      bodyHtml = `
        <span class="tag tag-example">Worked example</span>
        <h4>${escapeHtml(section.title)}</h4>
        <div class="body"><strong>Setup</strong>\n${escapeHtml(section.setup)}</div>
        <div class="solution-box"><strong>Solution</strong>\n${escapeHtml(section.solution)}</div>
        <div class="why-box"><strong>Why this way?</strong> ${escapeHtml(section.why)}</div>
        <div class="row" style="margin-top:12px">
          <button class="btn-primary grow" id="btnMarkNext">Got it — next</button>
          <button class="btn-grok grow" id="btnGrokSec">Ask Grok for another example</button>
        </div>`;
    } else if (section.type === "check") {
      const choices = Object.entries(section.choices || {})
        .map(([k, v]) => {
          let cls = "choice";
          if (learn.selectedCheck === k) cls += " selected";
          if (learn.checkRevealed) {
            if (k === section.answer) cls += " correct";
            if (learn.selectedCheck === k && k !== section.answer) cls += " wrong";
          }
          return `<button class="${cls}" data-c="${k}" ${learn.checkRevealed ? "disabled" : ""}><span class="letter">${k}</span>${escapeHtml(v)}</button>`;
        })
        .join("");
      bodyHtml = `
        <span class="tag tag-check">Concept check (must pass)</span>
        <h4>${escapeHtml(section.title)}</h4>
        <div class="body">${escapeHtml(section.prompt)}</div>
        <div style="margin-top:8px">${choices}</div>
        <div class="feedback ${learn.checkRevealed ? "show " + (learn.selectedCheck === section.answer ? "ok" : "bad") : ""}" id="checkFb">
          ${
            learn.checkRevealed
              ? learn.selectedCheck === section.answer
                ? `<strong>Correct ✅</strong> ${escapeHtml(section.explain || "")}`
                : `<strong>Not yet ❌</strong> Try again. Hint: ${escapeHtml(section.explain || "")}`
              : ""
          }
        </div>
        <div class="row" style="margin-top:12px">
          <button class="btn-secondary grow" id="btnSubmitCheck" ${learn.selectedCheck && !learn.checkRevealed ? "" : "disabled"}>Check answer</button>
          <button class="btn-primary grow" id="btnMarkNext" ${learn.checkRevealed && learn.selectedCheck === section.answer ? "" : "disabled"}>Continue</button>
        </div>`;
    }

    $("#learnCard").innerHTML = `
      <div class="quiz-meta">
        <span>Module ${learn.lessonIndex + 1}/${learn.lessonIds.length}: ${escapeHtml(lesson.title)}</span>
        <span>Section ${learn.sectionIndex + 1}/${totalSec}</span>
      </div>
      <div class="stepper">${dots}</div>
      <div class="lesson-section">${bodyHtml}</div>
      <button class="btn-ghost" id="btnExitLearn" style="width:100%;margin-top:4px">Save & exit to Today</button>
    `;

    $("#btnExitLearn").onclick = () => {
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
    $("#learnCard").querySelectorAll("button[data-c]").forEach((btn) => {
      btn.onclick = () => {
        if (learn.checkRevealed && learn.selectedCheck === section.answer) return;
        // allow retry if wrong
        if (learn.checkRevealed && learn.selectedCheck !== section.answer) {
          learn.checkRevealed = false;
        }
        learn.selectedCheck = btn.dataset.c;
        renderLearn();
      };
    });
  }

  function renderQuiz() {
    const q = currentQuestion();
    if (!q) {
      $("#quizCard").innerHTML = `<p class="muted">No active quiz.</p>
        <button class="btn-primary" id="btnQuizFromEmpty">Start quiz</button>`;
      $("#btnQuizFromEmpty").onclick = () => startQuiz();
      return;
    }
    const n = quiz.index + 1;
    const total = quiz.queue.length;
    const isReview = !!state.wrongPool[q.id];
    $("#quizCard").innerHTML = `
      <div class="quiz-meta">
        <span>Q ${n}/${total}${isReview ? " · 🔁 review" : ""}</span>
        <span>${q.id} · LO ${q.lo || "?"}</span>
      </div>
      <div class="quiz-stem">${escapeHtml(q.stem)}</div>
      <div id="choices"></div>
      <div class="feedback" id="feedback"></div>
      <div class="row" style="margin-top:12px">
        <button class="btn-secondary grow" id="btnSubmit" ${quiz.selected && !quiz.revealed ? "" : "disabled"}>Check</button>
        <button class="btn-primary grow" id="btnNext" style="display:${quiz.revealed ? "block" : "none"}">Next</button>
      </div>
      <div class="row" style="margin-top:8px">
        <button class="btn-grok grow" id="btnGrokQ">Ask Grok</button>
        <button class="btn-ghost grow" id="btnQuitQuiz">End session</button>
      </div>
    `;
    const box = $("#choices");
    for (const letter of ["A", "B", "C", "D", "E"]) {
      if (!q.choices?.[letter]) continue;
      const btn = document.createElement("button");
      btn.className = "choice";
      btn.innerHTML = `<span class="letter">${letter}</span>${escapeHtml(q.choices[letter])}`;
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
          ? `<strong>Correct ✅</strong> +10 XP`
          : `<strong>Not quite ❌</strong> Correct answer: <strong>${q.answer || "?"}</strong>. Saved to wrong pool.`;
    }
    $("#btnSubmit").onclick = submitAnswer;
    $("#btnNext").onclick = nextQuestion;
    $("#btnGrokQ").onclick = () => openGrok(explainPrompt(q, quiz.selected));
    $("#btnQuitQuiz").onclick = () => {
      quiz = null;
      showView("home");
      renderAll();
    };
  }

  function renderPath() {
    const days = curriculum?.days || [];
    const t = todayISO();
    const start = Math.max(0, days.findIndex((d) => d.date >= t) - 3);
    const slice = days.slice(start, start + 14);
    $("#pathCard").innerHTML =
      `<h3>🗺 Learning path</h3><div class="path">` +
      slice
        .map((d) => {
          const st = dayStats(d.date);
          const cls = d.date === t ? "today" : st.done ? "done" : "";
          const mark = st.done ? "✓" : d.date === t ? "●" : d.dayIndex + 1;
          return `<div class="path-node ${cls}">
            <div class="path-dot">${mark}</div>
            <div>
              <div style="font-weight:800">${escapeHtml(d.title)}</div>
              <div class="small muted">${d.date} · Learn ${st.lessonPct}% · Quiz ${st.answered}/${d.questionTarget}</div>
            </div>
            <button class="btn-secondary" data-go="${d.date}" ${d.date > t ? "disabled" : ""}>Go</button>
          </div>`;
        })
        .join("") +
      `</div>`;
    $("#pathCard").querySelectorAll("[data-go]").forEach((btn) => {
      btn.onclick = () => {
        const date = btn.dataset.go;
        if (!areAllLessonsComplete(date)) startLearn(date);
        else startQuiz(date);
      };
    });
  }

  function renderWrong() {
    const list = wrongList();
    $("#wrongCard").innerHTML =
      `<div class="row space-between"><h3 style="margin:0">❌ Wrong pool</h3>
        <button class="btn-secondary" id="btnSunday">Sunday recap → Grok</button></div>
       <p class="muted small">Misses reappear in quizzes. Sunday: generate similar drills with Grok.</p>` +
      (list.length
        ? list
            .map(
              (w) => `<div class="list-item">
            <div>
              <div style="font-weight:700">${w.id} · missed ${w.count}×</div>
              <div class="small muted">LO ${w.lo || "?"} · ${(w.topics || []).join(", ")}</div>
              <div class="small muted">${escapeHtml(w.stemPreview || "")}</div>
            </div>
            <div class="row">
              <button class="btn-secondary" data-review="${w.id}">Review</button>
              <button class="btn-grok" data-grok="${w.id}">Grok</button>
            </div>
          </div>`
            )
            .join("")
        : `<p class="muted">Pool empty — mistakes will land here.</p>`);

    $("#btnSunday").onclick = () => {
      openGrok(sundayRecapPrompt(list));
      downloadJSON(`sunday_recap_${todayISO()}.json`, { generatedAt: new Date().toISOString(), date: todayISO(), wrong: list });
      toast("Opened Grok + downloaded recap package");
    };
    $("#wrongCard").querySelectorAll("[data-review]").forEach((btn) => {
      btn.onclick = () => {
        // single-question review does not require lesson gate
        quiz = { date: todayISO(), queue: [btn.dataset.review], index: 0, selected: null, revealed: false };
        showView("quiz");
        renderQuiz();
      };
    });
    $("#wrongCard").querySelectorAll("[data-grok]").forEach((btn) => {
      btn.onclick = () => {
        const q = qById.get(btn.dataset.grok);
        if (q) openGrok(explainPrompt(q));
      };
    });
  }

  function renderSettings() {
    const cloud = window.SOACloud;
    const accountBlock = cloud?.user
      ? `<p><strong>Signed in:</strong> ${escapeHtml(cloud.user.email || cloud.user.uid)}<br>
           <span class="small muted">Status: ${cloud.status}${cloud.lastError ? " — " + escapeHtml(cloud.lastError) : ""}</span></p>
         <div class="row">
           <button class="btn-secondary grow" id="btnCloudPull">Pull from cloud</button>
           <button class="btn-secondary grow" id="btnCloudPush">Push to cloud</button>
           <button class="btn-danger grow" id="btnSignOut">Sign out</button>
         </div>`
      : `<p class="muted small">Not signed in. Without an account, progress stays on <em>this browser only</em> and can disappear if you clear site data.</p>
         <button class="btn-primary" id="btnOpenAuth" style="width:100%">Sign in / Create account</button>`;

    const configHint =
      !cloud || cloud.status === "need-config"
        ? `<div class="lock-banner" style="margin-top:10px">Cloud not configured. Open <code>FIREBASE_SETUP.md</code> (free Firebase project, ~5–10 min). Then add <code>app/js/firebase-config.js</code>.</div>`
        : "";

    $("#settingsCard").innerHTML = `
      <h3>Account & continuous progress</h3>
      ${accountBlock}
      ${configHint}
      <hr style="border:none;border-top:1px solid var(--border);margin:16px 0"/>
      <h3>Study settings</h3>
      <div class="row" style="margin:10px 0">
        <button class="btn-secondary" id="btnNotif">Enable notifications</button>
        <button class="btn-secondary" id="btnTestNotif">Test notification</button>
      </div>
      <label class="small muted">Reminder hour</label>
      <input id="reminderHour" type="number" min="0" max="23" value="${state.reminderHour}"
        style="width:100%;margin:6px 0 12px;padding:10px;border-radius:10px;border:1px solid var(--border);background:#0f172a;color:#fff"/>
      <label class="small muted">Daily quiz goal</label>
      <input id="dailyGoal" type="number" min="5" max="40" value="${state.settings.dailyGoal}"
        style="width:100%;margin:6px 0 12px;padding:10px;border-radius:10px;border:1px solid var(--border);background:#0f172a;color:#fff"/>
      <div class="row">
        <button class="btn-primary grow" id="btnSaveSettings">Save</button>
        <button class="btn-secondary grow" id="btnExport">Export backup</button>
        <button class="btn-secondary grow" id="btnImport">Import backup</button>
      </div>
      <textarea class="export-box" id="importBox" placeholder="Paste export JSON to import" style="margin-top:12px"></textarea>
      <div class="row" style="margin-top:10px">
        <button class="btn-danger grow" id="btnReset">Reset local progress</button>
      </div>
      <p class="small muted" style="margin-top:12px">
        <strong>Deploy:</strong> <code>DEPLOY.md</code> · <strong>Cloud:</strong> <code>FIREBASE_SETUP.md</code>
      </p>
      <p class="small muted">Questions: ${questions.length} · Lessons: ${Object.keys(lessons).length} · Days: ${curriculum?.days?.length || 0}</p>
    `;
    $("#btnOpenAuth")?.addEventListener("click", () => openAuthModal("signin"));
    $("#btnSignOut")?.addEventListener("click", async () => {
      await SOACloud.signOut();
      toast("Signed out (local progress kept on this device)");
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
        navigator.serviceWorker.controller.postMessage({ type: "NOTIFY_TEST", body: "Test: time to grind" });
      } else if (Notification.permission === "granted") {
        new Notification("SOA Grind", { body: "Test notification", icon: "./icons/icon-192.svg" });
      } else toast("Enable notifications first");
    };
    $("#btnSaveSettings").onclick = () => {
      state.reminderHour = Number($("#reminderHour").value) || 19;
      state.settings.dailyGoal = Number($("#dailyGoal").value) || 20;
      saveState({ immediate: true });
      toast("Saved");
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
      if (confirm("Reset all LOCAL progress on this device?")) {
        state = DEFAULT_STATE();
        saveState({ immediate: true });
        renderAll();
        toast("Local reset");
      }
    };
  }

  function renderAll() {
    renderChrome();
    renderHome();
    renderLearn();
    renderPath();
    renderWrong();
    renderSettings();
  }

  async function boot() {
    // Recover from IndexedDB if localStorage empty but IDB has data
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

    // Cloud
    if (window.SOACloud) {
      await SOACloud.init();
      SOACloud.onChange(() => {
        renderAccountChip();
        if (currentView === "settings") renderSettings();
      });
      // If already signed in from persistence, merge
      if (SOACloud.user) {
        await pullAndMergeCloud();
      }
    }

    document.querySelectorAll(".nav-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const v = btn.dataset.view;
        if (v === "quiz") {
          startQuiz();
          return;
        }
        if (v === "learn") {
          startLearn();
          return;
        }
        showView(v);
        if (v === "home") renderHome();
        if (v === "path") renderPath();
        if (v === "wrong") renderWrong();
        if (v === "settings") renderSettings();
      });
    });

    $("#accountChip")?.addEventListener("click", () => {
      if (window.SOACloud?.user) {
        showView("settings");
        renderSettings();
      } else {
        openAuthModal("signin");
      }
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
        await navigator.serviceWorker.register("./sw.js");
      } catch (e) {
        console.warn(e);
      }
    }

    renderAll();
    maybeRemind();

    // Nudge login once if cloud ready but not signed in
    if (window.SOACloud?.ready && !SOACloud.user && !sessionStorage.getItem("soa_auth_nudge")) {
      sessionStorage.setItem("soa_auth_nudge", "1");
      setTimeout(() => toast("Sign in (☁) to keep progress across devices"), 1200);
    }
    if (new Date().getDay() === 0 && wrongList().length) toast("Sunday: run Wrong Pool recap");
  }

  document.addEventListener("DOMContentLoaded", boot);
})();

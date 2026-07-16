/* Cloud auth + progress sync (Firebase free tier). Safe no-op if not configured. */
(function (global) {
  "use strict";

  const Cloud = {
    ready: false,
    user: null,
    status: "local-only",
    lastError: null,
    _db: null,
    _auth: null,
    _saveTimer: null,
    _listeners: [],
  };

  function configured() {
    const c = global.FIREBASE_CONFIG;
    return !!(c && c.apiKey && c.apiKey !== "PASTE_API_KEY" && c.projectId && c.projectId !== "YOUR_PROJECT_ID");
  }

  function emit() {
    Cloud._listeners.forEach((fn) => {
      try {
        fn(Cloud);
      } catch (_) {}
    });
  }

  Cloud.onChange = function (fn) {
    Cloud._listeners.push(fn);
  };

  Cloud.init = async function () {
    if (!configured()) {
      Cloud.status = "need-config";
      Cloud.ready = false;
      emit();
      return Cloud;
    }
    if (typeof firebase === "undefined") {
      Cloud.status = "error";
      Cloud.lastError = "Firebase SDK not loaded";
      emit();
      return Cloud;
    }
    try {
      if (!firebase.apps.length) firebase.initializeApp(global.FIREBASE_CONFIG);
      Cloud._auth = firebase.auth();
      Cloud._db = firebase.firestore();
      try {
        await Cloud._db.enablePersistence({ synchronizeTabs: true });
      } catch (_) {}
      Cloud.ready = true;
      Cloud.status = "offline";
      await new Promise((resolve) => {
        let first = true;
        Cloud._auth.onAuthStateChanged((user) => {
          if (user) {
            Cloud.user = { uid: user.uid, email: user.email || "" };
            Cloud.status = "synced";
          } else {
            Cloud.user = null;
            Cloud.status = "offline";
          }
          emit();
          if (first) {
            first = false;
            resolve();
          }
        });
      });
    } catch (e) {
      Cloud.status = "error";
      Cloud.lastError = String(e && e.message ? e.message : e);
      emit();
    }
    return Cloud;
  };

  Cloud.signUp = async function (email, password) {
    if (!Cloud._auth) throw new Error("Cloud not configured.");
    const cred = await Cloud._auth.createUserWithEmailAndPassword(email.trim(), password);
    Cloud.user = { uid: cred.user.uid, email: cred.user.email || email };
    emit();
    return Cloud.user;
  };

  Cloud.signIn = async function (email, password) {
    if (!Cloud._auth) throw new Error("Cloud not configured.");
    const cred = await Cloud._auth.signInWithEmailAndPassword(email.trim(), password);
    Cloud.user = { uid: cred.user.uid, email: cred.user.email || email };
    emit();
    return Cloud.user;
  };

  Cloud.signOut = async function () {
    if (!Cloud._auth) return;
    await Cloud._auth.signOut();
    Cloud.user = null;
    Cloud.status = "offline";
    emit();
  };

  Cloud.loadProgress = async function () {
    if (!Cloud.user || !Cloud._db) return null;
    Cloud.status = "syncing";
    emit();
    try {
      const snap = await Cloud._db.collection("users").doc(Cloud.user.uid).get();
      Cloud.status = "synced";
      emit();
      if (!snap.exists) return null;
      return (snap.data() || {}).progress || null;
    } catch (e) {
      Cloud.status = "error";
      Cloud.lastError = String(e.message || e);
      emit();
      throw e;
    }
  };

  Cloud.saveProgress = function (progress, immediate) {
    if (!Cloud.user || !Cloud._db) return Promise.resolve(false);
    const run = async () => {
      Cloud.status = "syncing";
      emit();
      try {
        // Firestore-safe plain object (no undefined)
        const clean = JSON.parse(JSON.stringify(progress));
        await Cloud._db.collection("users").doc(Cloud.user.uid).set(
          {
            progress: clean,
            email: Cloud.user.email || "",
            updatedAt: Date.now(),
          },
          { merge: true }
        );
        Cloud.status = "synced";
        Cloud.lastError = null;
        emit();
        return true;
      } catch (e) {
        Cloud.status = "error";
        Cloud.lastError = String(e.message || e);
        emit();
        return false;
      }
    };
    if (immediate) return run();
    clearTimeout(Cloud._saveTimer);
    return new Promise((resolve) => {
      Cloud._saveTimer = setTimeout(async () => resolve(await run()), 400);
    });
  };

  function mergeLessonProg(a, b) {
    a = a || { sectionDone: [], checks: {} };
    b = b || { sectionDone: [], checks: {} };
    return {
      sectionDone: Array.from(new Set([...(a.sectionDone || []), ...(b.sectionDone || [])])),
      checks: { ...(a.checks || {}), ...(b.checks || {}) },
      updatedAt: Math.max(a.updatedAt || 0, b.updatedAt || 0, Date.now()),
    };
  }

  function mergeDay(rd, ld) {
    rd = rd || {};
    ld = ld || {};
    const mergedAns = { ...(rd.answered || {}), ...(ld.answered || {}) };
    const lessonIds = new Set([
      ...Object.keys(rd.lessons || {}),
      ...Object.keys(ld.lessons || {}),
    ]);
    const mergedLessons = {};
    for (const lid of lessonIds) {
      mergedLessons[lid] = mergeLessonProg((rd.lessons || {})[lid], (ld.lessons || {})[lid]);
    }
    const readingsDone = Array.from(
      new Set([...(rd.readingsDone || []), ...(ld.readingsDone || [])])
    );
    return {
      ...rd,
      ...ld,
      answered: mergedAns,
      lessons: mergedLessons,
      readingsDone,
      completed: !!(rd.completed || ld.completed),
    };
  }

  /** Merge local + cloud without losing lesson mastery or day progress. */
  Cloud.mergeProgress = function (local, remote) {
    if (!remote) return local;
    if (!local) return remote;
    const L = local;
    const R = remote;
    const out = JSON.parse(JSON.stringify(L));

    out.xp = Math.max(L.xp || 0, R.xp || 0);
    out.streak = Math.max(L.streak || 0, R.streak || 0);
    if ((R.lastActiveDate || "") > (L.lastActiveDate || "")) out.lastActiveDate = R.lastActiveDate;
    out.notificationsEnabled = !!(L.notificationsEnabled || R.notificationsEnabled);
    out.reminderHour = L.reminderHour ?? R.reminderHour ?? 19;
    out.settings = { ...(R.settings || {}), ...(L.settings || {}) };

    // Global lesson mastery (module-level, survives day changes + devices)
    const masteryIds = new Set([
      ...Object.keys(L.lessonMastery || {}),
      ...Object.keys(R.lessonMastery || {}),
    ]);
    out.lessonMastery = {};
    for (const id of masteryIds) {
      out.lessonMastery[id] = mergeLessonProg(
        (L.lessonMastery || {})[id],
        (R.lessonMastery || {})[id]
      );
    }

    // Days: union all dates from both sides
    const dates = new Set([...Object.keys(L.days || {}), ...Object.keys(R.days || {})]);
    out.days = {};
    for (const date of dates) {
      out.days[date] = mergeDay((R.days || {})[date], (L.days || {})[date]);
    }

    out.wrongPool = { ...(R.wrongPool || {}) };
    for (const [id, meta] of Object.entries(L.wrongPool || {})) {
      const cur = out.wrongPool[id];
      if (!cur || (meta.count || 0) >= (cur.count || 0)) out.wrongPool[id] = meta;
    }

    const hist = [...(L.history || []), ...(R.history || [])];
    const seen = new Set();
    out.history = [];
    for (const h of hist) {
      const k = `${h.id}|${h.ts}|${h.choice}`;
      if (seen.has(k)) continue;
      seen.add(k);
      out.history.push(h);
      if (out.history.length >= 400) break;
    }

    // Exam history / used IDs
    out.examUsedQuestionIds = Array.from(
      new Set([...(L.examUsedQuestionIds || []), ...(R.examUsedQuestionIds || [])])
    );
    const examHist = [...(L.examHistory || []), ...(R.examHistory || [])];
    const seenExam = new Set();
    out.examHistory = [];
    for (const e of examHist) {
      if (!e?.id || seenExam.has(e.id)) continue;
      seenExam.add(e.id);
      out.examHistory.push(e);
      if (out.examHistory.length >= 30) break;
    }
    // Prefer in-progress local exam if present; else remote
    if (L.activeExam?.status === "in_progress") out.activeExam = L.activeExam;
    else if (R.activeExam?.status === "in_progress") out.activeExam = R.activeExam;
    else out.activeExam = L.activeExam || R.activeExam || null;

    out.updatedAt = Math.max(L.updatedAt || 0, R.updatedAt || 0, Date.now());
    out.version = Math.max(L.version || 1, R.version || 1, 3);
    return out;
  };

  Cloud.isConfigured = configured;
  global.SOACloud = Cloud;
})(window);

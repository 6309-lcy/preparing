/* Cloud auth + progress sync (Firebase free tier). Safe no-op if not configured. */
(function (global) {
  "use strict";

  const Cloud = {
    ready: false,
    user: null, // { uid, email }
    status: "local-only", // local-only | offline | syncing | synced | error | need-config
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
      if (!firebase.apps.length) {
        firebase.initializeApp(global.FIREBASE_CONFIG);
      }
      Cloud._auth = firebase.auth();
      Cloud._db = firebase.firestore();
      // Enable offline persistence for continuous feel
      try {
        await Cloud._db.enablePersistence({ synchronizeTabs: true });
      } catch (e) {
        // multi-tab or unsupported — fine
      }
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
    if (!Cloud._auth) throw new Error("Cloud not configured. See Settings → Cloud setup.");
    const cred = await Cloud._auth.createUserWithEmailAndPassword(email.trim(), password);
    Cloud.user = { uid: cred.user.uid, email: cred.user.email || email };
    emit();
    return Cloud.user;
  };

  Cloud.signIn = async function (email, password) {
    if (!Cloud._auth) throw new Error("Cloud not configured. See Settings → Cloud setup.");
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
      const data = snap.data() || {};
      return data.progress || null;
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
        const payload = {
          progress,
          email: Cloud.user.email || "",
          updatedAt: Date.now(),
        };
        await Cloud._db.collection("users").doc(Cloud.user.uid).set(payload, { merge: true });
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
      Cloud._saveTimer = setTimeout(async () => resolve(await run()), 600);
    });
  };

  /** Merge local + cloud progress without losing work on either device. */
  Cloud.mergeProgress = function (local, remote) {
    if (!remote) return local;
    if (!local) return remote;
    const out = JSON.parse(JSON.stringify(local));
    const r = remote;

    out.xp = Math.max(local.xp || 0, r.xp || 0);
    out.streak = Math.max(local.streak || 0, r.streak || 0);
    // keep latest activity date
    if ((r.lastActiveDate || "") > (local.lastActiveDate || "")) {
      out.lastActiveDate = r.lastActiveDate;
    }
    out.notificationsEnabled = local.notificationsEnabled || r.notificationsEnabled;
    out.reminderHour = local.reminderHour ?? r.reminderHour ?? 19;
    out.settings = { ...(r.settings || {}), ...(local.settings || {}) };

    // days: union by date, prefer richer answered/lesson progress
    out.days = { ...(r.days || {}) };
    const ldays = local.days || {};
    for (const [date, ld] of Object.entries(ldays)) {
      const rd = out.days[date];
      if (!rd) {
        out.days[date] = ld;
        continue;
      }
      const lAns = Object.keys(ld.answered || {}).length;
      const rAns = Object.keys(rd.answered || {}).length;
      const mergedAns = { ...(rd.answered || {}), ...(ld.answered || {}) };
      const mergedLessons = { ...(rd.lessons || {}), ...(ld.lessons || {}) };
      // deep-merge lesson sectionDone/checks
      for (const [lid, lp] of Object.entries(ld.lessons || {})) {
        const rp = mergedLessons[lid] || { sectionDone: [], checks: {} };
        const sectionDone = Array.from(new Set([...(rp.sectionDone || []), ...(lp.sectionDone || [])]));
        const checks = { ...(rp.checks || {}), ...(lp.checks || {}) };
        mergedLessons[lid] = { sectionDone, checks };
      }
      const readingsDone = Array.from(new Set([...(rd.readingsDone || []), ...(ld.readingsDone || [])]));
      out.days[date] = {
        ...rd,
        ...ld,
        answered: mergedAns,
        lessons: mergedLessons,
        readingsDone,
        completed: !!(rd.completed || ld.completed) || lAns + rAns > 0,
      };
    }

    // wrong pool: keep higher miss counts
    out.wrongPool = { ...(r.wrongPool || {}) };
    for (const [id, meta] of Object.entries(local.wrongPool || {})) {
      const cur = out.wrongPool[id];
      if (!cur || (meta.count || 0) >= (cur.count || 0)) out.wrongPool[id] = meta;
    }

    // history: merge unique by id+ts, cap
    const hist = [...(local.history || []), ...(r.history || [])];
    const seen = new Set();
    out.history = [];
    for (const h of hist) {
      const k = `${h.id}|${h.ts}|${h.choice}`;
      if (seen.has(k)) continue;
      seen.add(k);
      out.history.push(h);
      if (out.history.length >= 400) break;
    }

    out.updatedAt = Math.max(local.updatedAt || 0, r.updatedAt || 0, Date.now());
    out.version = Math.max(local.version || 1, r.version || 1);
    return out;
  };

  Cloud.isConfigured = configured;
  global.SOACloud = Cloud;
})(window);

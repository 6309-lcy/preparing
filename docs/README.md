# SOA Grind — Duolingo-style Exam P coach

Mobile + desktop progressive web app (PWA) you can host for free on **GitHub Pages**.

## Features

| Feature | How it works |
|---|---|
| **Teach-first Learn** | Concept → worked examples → *why* → concept check; **quiz locked until done** |
| **Daily quiz** | ~20 exam-style MC from the study plan (after Learn) |
| **Answer keys included** | SOA sample solutions matched (~640+ scored items) |
| **Wrong pool** | Missed items stored; auto-mixed into future days (~30%) |
| **Sunday recap** | One button builds a Grok prompt + downloads JSON package |
| **Ask Grok** | Deep-links to `https://grok.com/?q=...` with lesson or question context |
| **XP / streak** | Lightweight Duolingo-style motivation |
| **Notifications** | Browser/PWA reminders if today's lesson is incomplete |
| **Phone ↔ PC** | Export / import progress JSON (Settings) |

Full deploy guide: see `../DEPLOY.md`.

## Local preview (PC)

```powershell
cd C:\SOA\app
python -m http.server 8080
```

Open: http://localhost:8080

> Do not open `index.html` as a `file://` URL — fetch of JSON will fail. Use a tiny local server.

## Deploy free on GitHub Pages (phone + PC link)

### Option A — whole repo

1. Create a GitHub repo (e.g. `soa-grind`)
2. Push this project (at least the `app/` folder)
3. GitHub → **Settings → Pages**
4. Source: Deploy from branch `main`, folder `/app`  
   *(If `/app` is not listed, use Option B)*

### Option B — `docs/` folder (most reliable)

```powershell
cd C:\SOA
# copy app into docs for Pages
if (Test-Path docs) { Remove-Item docs -Recurse -Force }
Copy-Item app docs -Recurse
```

Then set Pages source to `/docs`.

Your public URL will look like:

`https://<you>.github.io/<repo>/`

Open that on your phone → **Share → Add to Home Screen** for app-like use.

## Daily loop (designed for 2h weekdays)

1. Open **Today** → tick readings while you study Finan / syllabus  
2. Tap **Start today's questions** → aim for the daily target (usually **20**)  
3. On a miss → item enters **Wrong pool**  
4. Tap **Ask Grok** anytime for tutoring on the live question  
5. **Sunday** → Wrong tab → **Sunday recap → Grok** (also downloads JSON)

## Rebuild question bank (when you get new SOA PDFs)

```powershell
# put updated PDFs in C:\SOA\Questions\
python C:\SOA\tools\match_qa.py
python C:\SOA\tools\build_question_bank.py
```

## Sunday script (optional automation)

```powershell
python C:\SOA\tools\sunday_recap.py path\to\sunday_recap_YYYY-MM-DD.json
# optional API:
# $env:XAI_API_KEY="xai-..."
# python C:\SOA\tools\sunday_recap.py path\to\file.json --api
```

## Data privacy

- Progress lives in **your browser `localStorage`** only
- No account server
- Export backups regularly if you care about streak/wrong-pool history

## Credits / copyright

SOA sample questions & solutions © Society of Actuaries — for personal exam prep only.  
Do not redistribute the question bank commercially.

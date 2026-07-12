# Study support tools (free / low-maintenance)

## 1. Daily Coach (local Python — recommended)

**File:** `daily_coach.py`

Each morning it builds a briefing from:
- `Study_Plan_Exam_P_FM.md` (today’s plan excerpt)
- `weakness_log.csv` (spaced-repetition items due)
- Hard-coded phase dates and registration/exam milestones

### Run once
```powershell
cd C:\SOA
python tools\daily_coach.py
```

### Email yourself (Gmail free tier)
```powershell
copy tools\.env.example tools\.env
# edit tools\.env with App Password
python tools\daily_coach.py --email
```

### Windows Task Scheduler (daily 7:00)
1. Open Task Scheduler → Create Basic Task
2. Trigger: Daily 7:00 AM
3. Action: Start a program
   - Program: `python` (or full path to `python.exe`)
   - Arguments: `C:\SOA\tools\daily_coach.py --email`
   - Start in: `C:\SOA`
4. Done — free, no cloud bill

Briefings also save under `tools/outbox/briefing_YYYY-MM-DD.md`.

---

## 2. Cloud free-tier options (if you want “set and forget” off your PC)

| Option | Cost | What you get | Complexity |
|---|---|---|---|
| **Windows Task Scheduler + Gmail SMTP** | Free | Daily email | Low (recommended first) |
| **GitHub Actions cron** | Free (public repo minutes) | Email via SMTP secrets or write issue | Medium |
| **Cloudflare Workers cron** | Free tier | Scheduled HTTP → email API | Medium |
| **Google Apps Script** | Free | Time-driven trigger emails a static weekly plan | Low–medium |
| **PythonAnywhere / Render free** | Free tier | Host the script on a schedule | Medium |

**Recommendation:** start with local Task Scheduler + Gmail. Only move to cloud if your PC is often off at 7 AM.

### Minimal GitHub Actions idea (optional later)
- Store plan + weakness_log in a private repo
- Cron workflow `0 11 * * *` (11:00 UTC ≈ morning US/EU depending on TZ)
- Run `daily_coach.py --email` with GitHub Secrets for SMTP

---

## 3. What not to build yet
- Full spaced-repetition Anki clone
- Adaptive ML question recommender
- Heavy web apps

Those burn prep time. Your ROI is **problems solved**, not infrastructure.

After Exam P, if you still want a nicer tool, a single-page Streamlit tracker on Streamlit Community Cloud (free) is enough.

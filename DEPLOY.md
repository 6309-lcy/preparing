# Deploy SOA Grind on GitHub (personal use)

## Short answers

### Do we need question answers?
**Yes — and they are already in the app.**  
We matched the official SOA sample **solutions** PDF to the questions. The quiz uses those letters (A–E) to score you, fill the wrong pool, and award XP. You do **not** need to type answers in yourself unless you later add new PDFs.

### Public access or not?
| Goal | Recommendation |
|---|---|
| Free, phone + PC, only you use the link | **Public repo is fine** (and free). The site is reachable by anyone who has the URL, but GitHub does not advertise it. Use an obscure repo name if you want low visibility. |
| Truly private (login / no public URL) | Free GitHub Pages **cannot** hide a site on a free private account. You need **GitHub Pro** (private Pages) or another host with auth. |
| Personal study only | Public Pages + unlisted URL is what most students use. |

**Copyright note:** SOA sample questions are © SOA, free for candidates. Keep the repo for personal prep; don’t sell the question bank.

---

## Deploy steps (free GitHub Pages)

### 0) Prerequisites
- GitHub account: https://github.com/join  
- Git installed: https://git-scm.com/downloads  
- (Optional) GitHub CLI later

### 1) Prepare the `docs/` folder (Pages-friendly)

In PowerShell:

```powershell
cd C:\SOA
powershell -File .\tools\deploy_pages.ps1
```

This copies `app/` → `docs/` (GitHub can host `/docs`).

### 2) Create a GitHub repository

1. Go to https://github.com/new  
2. Name it something like `soa-grind-private-study` (obscure is fine)  
3. Choose **Public** (for free Pages)  
4. **Do not** add README if you will push an existing folder  
5. Create repository

### 3) Push this project

```powershell
cd C:\SOA
git init
git add app docs Books Questions tools Study_Plan_Exam_P_FM.md DEPLOY.md .gitignore formula_sheet_P.md weakness_log.csv
git commit -m "SOA Grind: teach-first Exam P coach"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO`.

If GitHub asks you to sign in, use a **Personal Access Token** as the password (GitHub → Settings → Developer settings → PAT).

### 4) Turn on GitHub Pages

1. Repo → **Settings** → **Pages**  
2. **Source**: Deploy from a branch  
3. Branch: `main`  
4. Folder: **`/docs`**  
5. Save  

Wait 1–2 minutes. Your site will be:

```text
https://YOUR_USERNAME.github.io/YOUR_REPO/
```

### 5) Phone

1. Open that URL in Safari/Chrome  
2. **Add to Home Screen** (install PWA)  
3. Enable notifications in **More** if you want reminders  

### 6) Sync progress phone ↔ PC

Settings → **Export** on one device → **Import** on the other.  
(There is no automatic cloud login on the free static app.)

---

## After you change the app

```powershell
cd C:\SOA
powershell -File .\tools\deploy_pages.ps1
git add docs app
git commit -m "Update SOA Grind"
git push
```

Pages rebuilds in about a minute.

---

## Local test before deploy

```powershell
cd C:\SOA\app
python -m http.server 8080
```

Open http://localhost:8080  

Daily flow:
1. **Learn** (forced) — concept → examples → why → concept check  
2. **Quiz** unlocks only after learn is complete (~20 MC)  
3. Misses go to **Wrong** pool  

---

## Optional: keep study PDFs out of the public repo

If you don’t want Finan/PDFs online:

```powershell
# push only the web app
git add docs
git commit -m "Deploy app only"
git push
```

Keep `Books/` and `Questions/` only on your PC. The app already embeds the extracted question bank in `docs/data/questions.json`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| 404 on Pages | Check Settings → Pages folder is `/docs` and `docs/index.html` exists |
| Blank app / no questions | Open via https Pages URL or `python -m http.server`, not `file://` |
| Push denied | Use PAT, or `gh auth login` if CLI installed |
| Want private site | GitHub Pro private Pages, or Netlify/Cloudflare + access control |

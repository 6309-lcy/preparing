# Free cloud login for continuous progress (5–10 minutes)

Without login, progress lives only in the browser.  
With Firebase (Google free Spark plan), your XP, streak, lessons, quiz history, and wrong pool sync across phone and PC.

## 1. Create a free Firebase project

1. Open https://console.firebase.google.com/  
2. **Add project** → name e.g. `soa-grind` → continue (Google Analytics optional → disable is fine)  
3. Create project  

## 2. Register a Web app

1. Project overview → **</> Web**  
2. App nickname: `soa-grind-web`  
3. Copy the `firebaseConfig` object  

## 3. Enable Email/Password login

1. **Build → Authentication → Get started**  
2. **Sign-in method → Email/Password → Enable → Save**

## 4. Create Firestore database

1. **Build → Firestore Database → Create database**  
2. Start in **production mode** (or test mode for 30 days)  
3. Pick a region close to you  
4. **Rules** tab → paste:

```


```

5. **Publish**

## 5. Put config into the app

```powershell
cd C:\SOA\app\js
copy firebase-config.example.js firebase-config.js
notepad firebase-config.js
```

Paste your real values:

```js
window.FIREBASE_CONFIG = {
  apiKey: "...",
  authDomain: "...",
  projectId: "...",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "...",
};
```

Also copy into `docs/js/` when you deploy:

```powershell
cd C:\SOA
copy app\js\firebase-config.js docs\js\firebase-config.js
```

> `firebase-config.js` is in `.gitignore` so your keys are not forced into git.  
> Firebase **web API keys are public by design**; security is the Firestore rules above.

## 6. Use the app

1. Open the app (local server or GitHub Pages)  
2. Tap the **account chip** (top) or **More → Account**  
3. **Create account** with any email + password (6+ chars)  
4. Progress auto-saves to the cloud every change  
5. On your phone, open the same site → **Sign in** → progress merges  

## Free tier limits

Personal study use is well under Firebase Spark free quotas.  
No credit card required for Spark.

## If you skip Firebase

App still works **local-only** on one browser. Use **Export / Import** in Settings to move progress manually.

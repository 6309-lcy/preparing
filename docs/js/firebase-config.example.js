// 1) Copy this file to firebase-config.js
// 2) Paste values from Firebase Console → Project settings → Your apps → Web app
// 3) Enable Authentication → Email/Password
// 4) Create Firestore database (test mode or locked rules below)
//
// Free Spark plan is enough for personal study use.

window.FIREBASE_CONFIG = {
  apiKey: "PASTE_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "000000000000",
  appId: "1:000000000000:web:xxxxxxxx",
};

// Recommended Firestore rules (Console → Firestore → Rules):
//
// rules_version = '2';
// service cloud.firestore {
//   match /databases/{database}/documents {
//     match /users/{userId} {
//       allow read, write: if request.auth != null && request.auth.uid == userId;
//     }
//   }
// }

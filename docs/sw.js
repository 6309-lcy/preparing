/* SOA Grind PWA — network-first for app shell & data */
const CACHE = "soa-grind-v15";
const SHELL = [
  "./",
  "./index.html",
  "./css/styles.css",
  "./js/app.js",
  "./js/cloud.js",
  "./js/topic_guides.js",
  "./js/exam.js",
  "./manifest.json",
  "./icons/icon-192.svg",
  "./icons/icon-512.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const networkFirst =
    url.pathname.includes("/data/") ||
    url.pathname.includes("/js/") ||
    url.pathname.includes("/css/") ||
    url.pathname.endsWith(".png") ||
    url.pathname.endsWith(".json") ||
    url.pathname.endsWith("index.html") ||
    url.pathname.endsWith("/");

  if (networkFirst) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }
  event.respondWith(caches.match(req).then((c) => c || fetch(req)));
});

self.addEventListener("message", (event) => {
  const data = event.data || {};
  if (data.type === "NOTIFY_TEST") {
    self.registration.showNotification("SOA Grind", {
      body: data.body || "Time for today’s Exam P session",
      icon: "./icons/icon-192.svg",
      badge: "./icons/icon-192.svg",
      tag: "soa-daily",
      data: { url: "./index.html" },
    });
  }
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "./index.html";
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      for (const client of list) if ("focus" in client) return client.focus();
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});

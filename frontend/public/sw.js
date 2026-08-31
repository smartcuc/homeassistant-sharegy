// ==========================================
// Sharegy Cloud Energy - Native Service Worker
// W3C Web-Push & Background Notification Handler
// ==========================================

self.addEventListener("install", (event) => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(self.clients.claim());
});

// 🔔 PUSH-EVENT: Empfängt verschlüsselte Benachrichtigungen im Hintergrund
self.addEventListener("push", (event) => {
    let payload = {
        title: "⚡ Sharegy Energiemanager",
        body: "Neuer Status oder Alarm in deinem Zuhause.",
        icon: "/favicon.ico",
        badge: "/favicon.ico",
        tag: "sharegy-generic",
        data: { url: "/app/alerts" },
    };

    if (event.data) {
        try {
            payload = event.data.json();
        } catch (e) {
            payload.body = event.data.text();
        }
    }

    const options = {
        body: payload.body || "Neue Benachrichtigung von Sharegy.",
        icon: payload.icon || "/favicon.ico",
        badge: payload.badge || "/favicon.ico",
        tag: payload.tag || "sharegy-alert",
        vibrate: [200, 100, 200],
        renotify: true,
        requireInteraction: payload.severity === "critical",
        data: payload.data || { url: "/app/alerts" },
    };

    event.waitUntil(
        self.registration.showNotification(payload.title || "⚡ Sharegy Alarm", options)
    );
});

// 🖱️ KLICK-EVENT: Öffnet bei Klick auf die Benachrichtigung die passende Seite
self.addEventListener("notificationclick", (event) => {
    event.notification.close();

    const targetUrl = (event.notification.data && event.notification.data.url) ? event.notification.data.url : "/app/alerts";

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true }).then((windowClients) => {
            // Wenn bereits ein Sharegy-Tab offen ist -> fokussieren und navigieren
            for (let client of windowClients) {
                if (client.url.includes(self.location.origin) && "focus" in client) {
                    client.navigate(targetUrl);
                    return client.focus();
                }
            }
            // Andernfalls neuen Tab öffnen
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});

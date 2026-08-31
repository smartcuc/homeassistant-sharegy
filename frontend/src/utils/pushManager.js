// ==============================================================
// Sharegy Web-Push & Service Worker Subscription Manager
// ==============================================================

import { apiFetch } from "../api/client";

function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, "+")
        .replace(/_/g, "/");

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

export function isPushSupported() {
    return (
        typeof window !== "undefined" &&
        "serviceWorker" in navigator &&
        "PushManager" in window &&
        "Notification" in window
    );
}

export async function registerServiceWorker() {
    if (!isPushSupported()) return null;

    try {
        const registration = await navigator.serviceWorker.register("/sw.js", {
            scope: "/",
        });
        await navigator.serviceWorker.ready;
        return registration;
    } catch (err) {
        console.error("ServiceWorker registration failed:", err);
        return null;
    }
}

export async function getCurrentPushSubscription() {
    if (!isPushSupported()) return null;

    try {
        const registration = await navigator.serviceWorker.ready;
        return await registration.pushManager.getSubscription();
    } catch (err) {
        console.error("Error getting push subscription:", err);
        return null;
    }
}

export async function subscribeToPushNotifications() {
    if (!isPushSupported()) {
        throw new Error("Web-Push wird von diesem Browser oder Gerät nicht unterstützt.");
    }

    if (Notification.permission === "denied") {
        throw new Error("Benachrichtigungen sind in Firefox für sharegy.de blockiert. Bitte klicke links neben der Adressleiste auf das Symbol und hebe die Blockierung auf.");
    }

    // 1. Berechtigung beim Nutzer anfragen
    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
        throw new Error("Push-Berechtigung wurde im Browser nicht erteilt.");
    }

    // 2. Service Worker sicherstellen
    const registration = await registerServiceWorker();
    if (!registration) {
        throw new Error("Service Worker konnte nicht initialisiert werden.");
    }

    // 3. VAPID Public Key vom Sharegy-Backend abrufen
    const keyData = await apiFetch("/api/notifications/vapid-key/");
    if (!keyData || !keyData.publicKey) {
        throw new Error("VAPID Public Key konnte nicht vom Server geladen werden.");
    }

    const applicationServerKey = urlBase64ToUint8Array(keyData.publicKey);

    // 4. Browser-Abonnement erzeugen (stale subscriptions sicher ablösen)
    let subscription = await registration.pushManager.getSubscription();
    if (subscription) {
        try {
            await subscription.unsubscribe();
        } catch { }
    }

    subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey,
    });

    const subJson = subscription.toJSON();

    // 5. Gerätename ableiten
    let deviceName = "Web-Browser";
    const ua = navigator.userAgent;
    if (ua.includes("Firefox")) deviceName = "Firefox auf PC";
    else if (ua.includes("iPhone")) deviceName = "Apple iPhone";
    else if (ua.includes("iPad")) deviceName = "Apple iPad";
    else if (ua.includes("Android")) deviceName = "Android Smartphone";
    else if (ua.includes("Macintosh")) deviceName = "Apple Mac";
    else if (ua.includes("Windows")) deviceName = "Windows PC";

    // 6. Abonnement sicher im Sharegy-Backend speichern
    const result = await apiFetch("/api/notifications/subscribe/", {
        method: "POST",
        body: JSON.stringify({
            endpoint: subscription.endpoint,
            keys: subJson.keys,
            device_type: "web_push",
            device_name: deviceName,
        }),
    });

    return result;
}

export async function unsubscribeFromPushNotifications() {
    if (!isPushSupported()) return false;

    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (subscription) {
            await apiFetch("/api/notifications/unsubscribe/", {
                method: "POST",
                body: JSON.stringify({ endpoint: subscription.endpoint }),
            });
            await subscription.unsubscribe();
        }
        return true;
    } catch (err) {
        console.error("Error unsubscribing:", err);
        return false;
    }
}

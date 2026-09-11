/*
# src/api/client.js
*/

import { Capacitor } from "@capacitor/core";
import { getCSRFToken } from "../lib/csrf";

// 🌐 Automatische Auflösung der API Base-URL für Native Apps (Android/Capacitor) und Web
export const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    (Capacitor.isNativePlatform() || (typeof window !== "undefined" && window.location.protocol === "capacitor:")
        ? "https://sharegy.de"
        : "");

export function getApiUrl(url) {
    if (!url) return "";
    if (url.startsWith("http://") || url.startsWith("https://")) {
        return url;
    }
    const cleanUrl = url.startsWith("/") ? url : `/${url}`;
    return `${API_BASE_URL}${cleanUrl}`;
}

export async function apiFetch(url, options = {}) {
    const fullUrl = getApiUrl(url);

    // Standard-Header definieren
    const defaultHeaders = {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
    };

    let res;
    try {
        res = await fetch(fullUrl, {
            ...options,
            credentials: "include",
            // Kombiniert Standard-Header mit benutzerdefinierten Headern aus options
            headers: {
                ...defaultHeaders,
                ...(options.headers || {}),
            },
        });
    } catch (networkErr) {
        throw {
            type: "network",
            message: networkErr?.message || "Netzwerkfehler – Server nicht erreichbar",
        };
    }

    // ✅ 401 / 403 → Session weg → Logout
    if (res.status === 401 || res.status === 403) {
        console.warn("Auth lost → redirecting to login");

        localStorage.clear();
        sessionStorage.clear();

        throw { type: "auth" };
    }

    // ✅ 400 → Validierungsfehler
    if (res.status === 400) {
        let data;
        try {
            data = await res.json();
        } catch {
            data = { error: "Ungültige Anfrage (400)" };
        }

        throw {
            type: "validation",
            data,
        };
    }

    // ✅ Andere Server-Fehler (500, 404, etc.)
    if (!res.ok) {
        let errorMsg = `Serverfehler (${res.status})`;
        try {
            const errorJson = await res.json();
            errorMsg = errorJson.error || errorJson.detail || errorJson.message || errorMsg;
        } catch {
            try {
                const text = await res.text();
                // Falls HTML zurückkommt (z.B. Nginx 502/404), saubere Fehlermeldung statt HTML-SyntaxError
                if (text && !text.trim().startsWith("<")) {
                    errorMsg = text;
                }
            } catch {
                // ignore
            }
        }

        throw {
            type: "server",
            message: errorMsg,
        };
    }

    // ✅ 204 No Content abfangen, um JSON-Parse-Fehler zu vermeiden
    if (res.status === 204) {
        return null;
    }

    // ✅ Erfolg: Sicheres JSON-Parsen
    try {
        const text = await res.text();
        if (!text || !text.trim()) return null;
        return JSON.parse(text);
    } catch (parseErr) {
        console.error("JSON parse error on response:", fullUrl, parseErr);
        throw {
            type: "parse",
            message: "Ungültige Serverantwort (kein valides JSON)",
        };
    }
}

/**
 * Sentry Frontend Error & Crash Reporting for Sharegy Web.
 * Dynamically loads official Sentry Browser SDK and catches unhandled exceptions & promise rejections.
 */

let isSentryInitialized = false;

export function initSentry() {
    const dsn = import.meta.env.VITE_SENTRY_DSN || "https://4b0e69ecb1ccdcb9559c324ac80c32b5@o4511998045650944.ingest.de.sentry.io/4511998077632592";

    if (!dsn || isSentryInitialized) {
        return;
    }

    try {
        // 1. Script Tag für Sentry Browser SDK Bundle laden
        const script = document.createElement("script");
        script.src = "https://browser.sentry-cdn.com/8.40.0/bundle.min.js";
        script.crossOrigin = "anonymous";
        script.async = true;

        script.onload = () => {
            if (window.Sentry) {
                window.Sentry.init({
                    dsn: dsn,
                    environment: import.meta.env.MODE || "production",
                    release: "sharegy-frontend@3.2.0",
                    tracesSampleRate: 0.1,
                    sendDefaultPii: false,
                });
                isSentryInitialized = true;
                console.log("[Sharegy:Sentry] 🛡️ Sentry Frontend Crash-Reporting aktiviert");
            }
        };

        // Fallback falls Script blockiert wird: Global Error Listener
        window.addEventListener("error", (event) => {
            if (window.Sentry) {
                window.Sentry.captureException(event.error || event.message);
            }
        });

        window.addEventListener("unhandledrejection", (event) => {
            if (window.Sentry) {
                window.Sentry.captureException(event.reason);
            }
        });

        document.head.appendChild(script);
        isSentryInitialized = true;
    } catch (e) {
        console.warn("[Sharegy:Sentry] Initialisierungsfehler:", e);
    }
}

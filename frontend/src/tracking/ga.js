/**
 * Google Analytics 4 (GA4) Tracking Utility for Sharegy.
 * Supports IP anonymization, route change tracking, and custom event dispatching.
 */

let isInitialized = false;

export function initGA() {
    const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID || window.__SHAREGY_GA_ID__;

    if (!measurementId || isInitialized) {
        return;
    }

    try {
        // 1. Script Tag einfügen
        const script = document.createElement("script");
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
        document.head.appendChild(script);

        // 2. DataLayer initialisieren
        window.dataLayer = window.dataLayer || [];
        function gtag() {
            window.dataLayer.push(arguments);
        }
        window.gtag = gtag;

        gtag("js", new Date());
        gtag("config", measurementId, {
            anonymize_ip: true,
            send_page_view: false, // Wir tracken PageViews manuell via React Router
        });

        isInitialized = true;
        console.log(`[Sharegy:Analytics] 📊 Google Analytics 4 initialisiert (${measurementId})`);
    } catch (e) {
        console.warn("[Sharegy:Analytics] Fehler bei der GA4-Initialisierung:", e);
    }
}

/**
 * Trackt Seitenaufrufe bei React Router Routenwechseln
 */
export function trackPageView(path, title = "") {
    const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID || window.__SHAREGY_GA_ID__;
    if (!measurementId || typeof window.gtag !== "function") return;

    window.gtag("event", "page_view", {
        page_path: path,
        page_title: title || document.title,
    });
}

/**
 * Trackt benutzerdefinierte Events (z. B. Onboarding, Plan-Upgrade, Export)
 */
export function trackEvent(action, category = "general", label = "", value = null) {
    if (typeof window.gtag !== "function") return;

    const eventParams = {
        event_category: category,
        event_label: label,
    };
    if (value !== null && !isNaN(value)) {
        eventParams.value = Number(value);
    }

    window.gtag("event", action, eventParams);
}

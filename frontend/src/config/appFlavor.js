/*
# frontend/src/config/appFlavor.js
# Flavor-Erkennung für Sharegy Home (de.sharegy.app) vs. Sharegy Pro (de.sharegy.pro)
*/

export const APP_FLAVORS = {
    HOME: "home",
    PRO: "pro",
};

/**
 * Ermittelt das aktive App-Flavor anhand von Vite Environment oder Capacitor App-ID.
 */
export function getAppFlavor() {
    // 1. Explizites Build-Environment
    const envFlavor = import.meta.env.VITE_APP_FLAVOR;
    if (envFlavor && (envFlavor === APP_FLAVORS.PRO || envFlavor === "partner")) {
        return APP_FLAVORS.PRO;
    }

    // 2. Subdomain / Host-Erkennung (z.B. pro.sharegy.de / partner.sharegy.de)
    if (typeof window !== "undefined") {
        const host = window.location.hostname.toLowerCase();
        if (host.startsWith("pro.") || host.startsWith("partner.") || host.startsWith("installer.")) {
            return APP_FLAVORS.PRO;
        }
    }

    return APP_FLAVORS.HOME;
}

export const isProApp = getAppFlavor() === APP_FLAVORS.PRO;

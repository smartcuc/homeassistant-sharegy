/*
# src/components/legal/CookieConsentBanner.jsx
*/

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export const CONSENT_STORAGE_KEY = "sharegy_cookie_consent_v1";

export function getStoredConsent() {
    // 1. Try localStorage
    try {
        const stored = localStorage.getItem(CONSENT_STORAGE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            if (parsed && typeof parsed === "object") return parsed;
        }
    } catch {
        // Fallthrough if localStorage is restricted
    }

    // 2. Try document.cookie as fallback
    try {
        if (typeof document !== "undefined" && document.cookie) {
            const match = document.cookie
                .split("; ")
                .find((row) => row.startsWith(`${CONSENT_STORAGE_KEY}=`));
            if (match) {
                const cookieVal = decodeURIComponent(match.split("=")[1]);
                return JSON.parse(cookieVal);
            }
        }
    } catch {
        // Fallthrough
    }

    return null;
}

export function saveConsent(consent) {
    const data = {
        essential: true,
        functional: Boolean(consent.functional),
        analytics: Boolean(consent.analytics),
        timestamp: new Date().toISOString(),
    };

    // 1. Save in localStorage
    try {
        localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
        console.warn("Could not save cookie consent to localStorage:", e);
    }

    // 2. Save in document.cookie (1 year persistence)
    try {
        if (typeof document !== "undefined") {
            const isSecure = window.location.protocol === "https:" ? "; Secure" : "";
            document.cookie = `${CONSENT_STORAGE_KEY}=${encodeURIComponent(JSON.stringify(data))}; path=/; max-age=31536000; SameSite=Lax${isSecure}`;
        }
    } catch (e) {
        console.warn("Could not save cookie consent to document.cookie:", e);
    }

    try {
        window.dispatchEvent(new CustomEvent("cookie-consent-updated", { detail: data }));
    } catch {}

    return data;
}


export default function CookieConsentBanner() {
    const { t } = useTranslation();
    const [consentState, setConsentState] = useState(() => getStoredConsent());
    const [isOpen, setIsOpen] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Custom preferences state
    const [functional, setFunctional] = useState(true);
    const [analytics, setAnalytics] = useState(false);

    useEffect(() => {
        const stored = getStoredConsent();
        if (!stored) {
            // Show banner after short timeout to avoid layout pop
            const timer = setTimeout(() => setIsOpen(true), 600);
            return () => clearTimeout(timer);
        } else {
            setFunctional(stored.functional);
            setAnalytics(stored.analytics);
        }
    }, []);

    // Listen for custom trigger from Footer or other components to open settings modal anytime
    useEffect(() => {
        const handleOpenSettings = () => {
            const current = getStoredConsent();
            if (current) {
                setFunctional(current.functional);
                setAnalytics(current.analytics);
            }
            setIsModalOpen(true);
        };

        window.addEventListener("open-cookie-settings", handleOpenSettings);
        return () => window.removeEventListener("open-cookie-settings", handleOpenSettings);
    }, []);

    const handleAcceptAll = () => {
        const saved = saveConsent({ functional: true, analytics: true });
        setConsentState(saved);
        setIsOpen(false);
        setIsModalOpen(false);
    };

    const handleRejectAll = () => {
        const saved = saveConsent({ functional: false, analytics: false });
        setConsentState(saved);
        setIsOpen(false);
        setIsModalOpen(false);
    };

    const handleSaveCustom = () => {
        const saved = saveConsent({ functional, analytics });
        setConsentState(saved);
        setIsOpen(false);
        setIsModalOpen(false);
    };

    return (
        <>
            {/* 1. BOTTOM FLOATING BANNER (First Visit) */}
            {isOpen && !isModalOpen && (
                <div className="fixed bottom-0 inset-x-0 z-50 p-4 sm:p-6 animate-in fade-in slide-in-from-bottom-8 duration-300">
                    <div className="max-w-4xl mx-auto bg-slate-900/95 text-white rounded-3xl p-6 sm:p-7 shadow-2xl border border-slate-800 backdrop-blur-md flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                        <div className="space-y-2 max-w-2xl">
                            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                                <span>🍪</span>
                                <span>{t("cookies.banner_title", "Privatsphäre- & Cookie-Einstellungen")}</span>
                            </div>
                            <p className="text-xs text-slate-300 leading-relaxed">
                                {t(
                                    "cookies.banner_desc",
                                    "Wir nutzen technisch notwendige Cookies und Speicherfunktionen für den sicheren Betrieb (Session, CSRF) sowie optionale Funktionen zur Verbesserung deines Energiemanagements. Du kannst selbst entscheiden, welche Kategorien du erlaubst."
                                )}
                            </p>
                            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-400">
                                <Link to="/datenschutz" className="underline hover:text-white transition">
                                    {t("legal.privacy_title", "Datenschutzerklärung")}
                                </Link>
                                <span>·</span>
                                <Link to="/impressum" className="underline hover:text-white transition">
                                    {t("legal.impressum_title", "Impressum")}
                                </Link>
                            </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto shrink-0">
                            <button
                                type="button"
                                onClick={() => setIsModalOpen(true)}
                                className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 transition cursor-pointer border border-slate-700 flex-1 md:flex-none text-center"
                            >
                                {t("cookies.customize", "Anpassen")}
                            </button>
                            <button
                                type="button"
                                onClick={handleRejectAll}
                                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-200 hover:text-white bg-slate-800 hover:bg-slate-700 transition cursor-pointer border border-slate-700 flex-1 md:flex-none text-center"
                            >
                                {t("cookies.reject_optional", "Nur essenzielle")}
                            </button>
                            <button
                                type="button"
                                onClick={handleAcceptAll}
                                className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 transition cursor-pointer shadow-lg shadow-indigo-600/30 flex-1 md:flex-none text-center"
                            >
                                {t("cookies.accept_all", "Alle akzeptieren")}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* 2. DETAILED PREFERENCES MODAL */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-fade-in">
                    <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
                        {/* Modal Header */}
                        <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-slate-50">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl p-2 bg-indigo-50 text-indigo-600 rounded-xl">🍪</span>
                                <div>
                                    <h3 className="text-base font-bold text-gray-900">
                                        {t("cookies.settings_title", "Einwilligungs- & Cookie-Präferenzen")}
                                    </h3>
                                    <p className="text-xs text-gray-500">
                                        {t("cookies.settings_subtitle", "Verwalte deine Datenschutzeinstellungen nach DSGVO & TDDDG")}
                                    </p>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => setIsModalOpen(false)}
                                className="w-8 h-8 rounded-full bg-white border border-gray-200 text-gray-400 hover:text-gray-700 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        {/* Modal Body */}
                        <div className="p-6 overflow-y-auto space-y-4 text-xs sm:text-sm">
                            <p className="text-gray-600 text-xs leading-relaxed">
                                {t(
                                    "cookies.settings_desc",
                                    "Hier kannst du detailliert festlegen, welche Speichertechnologien und Cookies du zulassen möchtest. Deine Auswahl wird lokal gespeichert und kann jederzeit über den Link im Footer widerrufen oder geändert werden."
                                )}
                            </p>

                            {/* Category 1: Essential */}
                            <div className="p-4 rounded-2xl border border-gray-200 bg-slate-50/70 space-y-2">
                                <div className="flex items-center justify-between">
                                    <div className="font-bold text-gray-900 flex items-center gap-2">
                                        <span>🔒</span>
                                        <span>{t("cookies.cat_essential_title", "Essenziell (Technisch notwendig)")}</span>
                                    </div>
                                    <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                                        {t("cookies.always_active", "Immer aktiv")}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 leading-relaxed">
                                    {t(
                                        "cookies.cat_essential_desc",
                                        "Unverzichtbar für die Kernfunktionen der Website, Benutzeranmeldung (Session-Cookie), CSRF-Schutz und Sicherheit. Kann nicht deaktiviert werden gem. § 25 Abs. 2 TDDDG."
                                    )}
                                </p>
                            </div>

                            {/* Category 2: Functional */}
                            <div className="p-4 rounded-2xl border border-gray-200 bg-white space-y-2">
                                <div className="flex items-center justify-between">
                                    <label htmlFor="consent-functional" className="font-bold text-gray-900 flex items-center gap-2 cursor-pointer">
                                        <span>⚙️</span>
                                        <span>{t("cookies.cat_functional_title", "Funktional & Personalisierung")}</span>
                                    </label>
                                    <input
                                        id="consent-functional"
                                        type="checkbox"
                                        checked={functional}
                                        onChange={(e) => setFunctional(e.target.checked)}
                                        className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                    />
                                </div>
                                <p className="text-xs text-gray-500 leading-relaxed">
                                    {t(
                                        "cookies.cat_functional_desc",
                                        "Ermöglicht das Speichern deiner Sprachauswahl (Deutsch/Englisch/Polnisch), Zeitfenster-Filter und Dashboard-Präferenzen über Sitzungen hinweg."
                                    )}
                                </p>
                            </div>

                            {/* Category 3: Analytics */}
                            <div className="p-4 rounded-2xl border border-gray-200 bg-white space-y-2">
                                <div className="flex items-center justify-between">
                                    <label htmlFor="consent-analytics" className="font-bold text-gray-900 flex items-center gap-2 cursor-pointer">
                                        <span>📊</span>
                                        <span>{t("cookies.cat_analytics_title", "Analyse & Feature-Nutzung")}</span>
                                    </label>
                                    <input
                                        id="consent-analytics"
                                        type="checkbox"
                                        checked={analytics}
                                        onChange={(e) => setAnalytics(e.target.checked)}
                                        className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                    />
                                </div>
                                <p className="text-xs text-gray-500 leading-relaxed">
                                    {t(
                                        "cookies.cat_analytics_desc",
                                        "Hilft uns zu verstehen, welche Funktionen genutzt werden, um die Plattform und Benutzeroberfläche kontinuierlich zu verbessern (anonymisierte Telemetrie)."
                                    )}
                                </p>
                            </div>
                        </div>

                        {/* Modal Footer Actions */}
                        <div className="p-4 border-t border-gray-100 bg-slate-50 flex flex-wrap items-center justify-between gap-3">
                            <button
                                type="button"
                                onClick={handleRejectAll}
                                className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-white border border-gray-200 hover:bg-gray-100 transition cursor-pointer"
                            >
                                {t("cookies.reject_optional", "Nur essenzielle")}
                            </button>

                            <div className="flex items-center gap-2.5">
                                <button
                                    type="button"
                                    onClick={handleSaveCustom}
                                    className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-slate-200 hover:bg-slate-300 transition cursor-pointer"
                                >
                                    {t("cookies.save_selection", "Auswahl speichern")}
                                </button>
                                <button
                                    type="button"
                                    onClick={handleAcceptAll}
                                    className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition cursor-pointer shadow-xs"
                                >
                                    {t("cookies.accept_all", "Alle akzeptieren")}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}


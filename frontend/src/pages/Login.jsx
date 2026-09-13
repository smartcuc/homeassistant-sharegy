/*
# src/pages/Login.jsx
*/
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";
import { trackEvent } from "../lib/track";
import { isNativePlatform, getPlatform, triggerHapticFeedback } from "../utils/nativeBridge";

export default function Login() {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const isApp = isNativePlatform();

    const [email, setEmail] = useState("");
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("");
    const [statusType, setStatusType] = useState("info"); // 'info' | 'success' | 'error'
    const [cooldown, setCooldown] = useState(0);
    const [showCodeInput, setShowCodeInput] = useState(false);

    async function handleLoginRequest() {
        if (!email || loading || cooldown > 0) return;

        setLoading(true);
        setStatus("");

        try {
            trackEvent("magic_link_requested", { client: isApp ? "app" : "web" });
            await apiFetch("/api/request-magic-link/", {
                method: "POST",
                body: JSON.stringify({
                    email: email.trim(),
                    lang: i18n.language,
                    client: isApp ? "app" : "web",
                    platform: isApp ? getPlatform() : "web",
                }),
            });

            triggerHapticFeedback();
            setStatusType("success");

            if (isApp) {
                setStatus(
                    t(
                        "auth.magic_code_sent_app",
                        "✅ Code gesendet! Gib den 6-stelligen Code aus deiner E-Mail hier ein oder tippe in der E-Mail auf 'In der App öffnen'."
                    )
                );
                setShowCodeInput(true);
            } else {
                setStatus(
                    t(
                        "auth.magic_link_sent_web",
                        "✅ Wir haben dir deinen Anmelde-Link per E-Mail geschickt! Klicke einfach auf den Link in der E-Mail, um dich direkt anzumelden."
                    )
                );
                setShowCodeInput(false);
            }

            // Cooldown 15s
            let seconds = 15;
            setCooldown(seconds);
            const interval = setInterval(() => {
                seconds--;
                setCooldown(seconds);
                if (seconds <= 0) clearInterval(interval);
            }, 1000);

        } catch (err) {
            triggerHapticFeedback();
            setStatusType("error");
            if (err?.type === "validation" && err.data?.error) {
                setStatus(`❌ ${err.data.error}`);
            } else if (err?.message) {
                setStatus(`❌ ${err.message}`);
            } else {
                setStatus(t("auth.send_error", "❌ Fehler beim Senden. Bitte prüfe deine E-Mail-Adresse."));
            }
        } finally {
            setLoading(false);
        }
    }

    async function handleVerifyCode(codeToVerify) {
        const inputCode = String(codeToVerify || code || "").trim();
        if (!inputCode || loading) return;

        setLoading(true);
        setStatus("");

        try {
            trackEvent("login_code_attempt");
            await apiFetch(`/api/magic-login/?token=${encodeURIComponent(inputCode)}`);

            // Prefetch user session
            let meUser = null;
            for (let i = 0; i < 5; i++) {
                try {
                    meUser = await apiFetch("/api/auth/me/");
                    if (meUser) break;
                } catch {
                    // Retry
                }
                await new Promise((r) => setTimeout(r, 200));
            }

            if (!meUser) {
                throw new Error("Session konnte nicht initialisiert werden.");
            }

            await queryClient.prefetchQuery({
                queryKey: ["user"],
                queryFn: () => apiFetch("/api/auth/me/"),
            });

            await queryClient.prefetchQuery({
                queryKey: ["settings"],
                queryFn: () => apiFetch("/api/settings/"),
            });

            triggerHapticFeedback();
            trackEvent("login_code_success");
            setStatusType("success");
            setStatus("🚀 Erfolgreich angemeldet! Du wirst weitergeleitet…");

            navigate("/app/dashboard", { replace: true });
        } catch (err) {
            triggerHapticFeedback();
            setStatusType("error");
            trackEvent("login_code_failed");
            if (err?.type === "validation" && err.data?.error) {
                setStatus(`❌ ${err.data.error}`);
            } else if (err?.message) {
                setStatus(`❌ ${err.message}`);
            } else {
                setStatus(t("auth.code_error", "❌ Ungültiger oder abgelaufener Code. Bitte erneut versuchen."));
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-4 sm:p-6">
            <div className="bg-white dark:bg-slate-900 w-full max-w-md rounded-2xl shadow-2xl p-6 sm:p-8 border border-white/20">

                {/* HEADER */}
                <div className="text-center mb-6">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-extrabold text-2xl mb-2 shadow-inner">
                        ⚡
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                        Sharegy
                    </h1>
                    <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
                        {t("auth.app_tagline", "Energie verstehen & intelligent nutzen")}
                    </p>
                </div>

                {/* TITLE */}
                <h2 className="text-lg sm:text-xl font-semibold text-center mb-1 text-slate-800 dark:text-slate-100">
                    {t("auth.welcome_back", "Willkommen zurück 👋")}
                </h2>

                <p className="text-slate-500 dark:text-slate-400 text-xs sm:text-sm text-center mb-6">
                    {showCodeInput
                        ? t("auth.enter_code_desc", "Gib den 6-stelligen Code aus deiner E-Mail ein:")
                        : isApp
                        ? t("auth.enter_email_desc_app", "Gib deine E-Mail ein – wir schicken dir deinen Login-Code für die App.")
                        : t("auth.enter_email_desc_web", "Gib deine E-Mail ein – wir schicken dir deinen direkten Anmelde-Link.")}
                </p>

                {/* EMAIL FORM */}
                {!showCodeInput && (
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                                {t("auth.email_label", "E-Mail-Adresse")}
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="deine@email.de"
                                autoFocus
                                onKeyDown={(e) => {
                                    if (e.key === "Enter") handleLoginRequest();
                                }}
                                className="w-full border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white p-3.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm transition"
                            />
                        </div>

                        <button
                            onClick={handleLoginRequest}
                            disabled={loading || cooldown > 0 || !email}
                            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white py-3.5 rounded-xl font-semibold text-sm transition shadow-lg shadow-indigo-500/25 active:scale-[0.98] disabled:opacity-50"
                        >
                            {loading
                                ? t("auth.sending_link", "Sende Login-Link…")
                                : cooldown > 0
                                ? t("auth.resend_in", { sec: cooldown, defaultValue: `Erneut anfordern (${cooldown}s)` })
                                : isApp
                                ? t("auth.get_code_btn_app", "📱 Login-Code & Link erhalten")
                                : t("auth.get_link_btn_web", "🔐 Anmelde-Link erhalten")}
                        </button>
                    </div>
                )}

                {/* 6-DIGIT CODE INPUT FORM */}
                {showCodeInput && (
                    <div className="space-y-4 animate-fadeIn">
                        <div className="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider mb-1.5 text-center">
                                {t("auth.code_label", "🔢 6-Stelliger Login-Code oder Link")}
                            </label>
                            <input
                                type="text"
                                inputMode="numeric"
                                value={code}
                                onChange={(e) => {
                                    const val = e.target.value;
                                    setCode(val);
                                    // Auto-submit if user entered 6 pure digits
                                    const clean = val.replace(/\D/g, "");
                                    if (clean.length === 6 && !loading) {
                                        handleVerifyCode(clean);
                                    }
                                }}
                                placeholder="z. B. 849 201"
                                autoFocus
                                onKeyDown={(e) => {
                                    if (e.key === "Enter") handleVerifyCode();
                                }}
                                className="w-full text-center tracking-widest font-mono text-xl sm:text-2xl font-bold border border-indigo-300 dark:border-indigo-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-inner"
                            />
                            <p className="text-[11px] text-slate-400 dark:text-slate-500 text-center mt-2">
                                {t("auth.code_hint", "Du kannst auch den gesamten Link oder Token aus der E-Mail hier einfügen.")}
                            </p>
                        </div>

                        <button
                            onClick={() => handleVerifyCode()}
                            disabled={loading || !code.trim()}
                            className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white py-3.5 rounded-xl font-semibold text-sm transition shadow-lg shadow-emerald-500/25 active:scale-[0.98] disabled:opacity-50"
                        >
                            {loading ? t("auth.verifying", "Prüfe Code…") : t("auth.verify_btn", "🚀 Code bestätigen & Einloggen")}
                        </button>
                    </div>
                )}

                {/* STATUS MESSAGE */}
                {status && (
                    <div
                        className={`mt-4 p-3 rounded-xl text-xs sm:text-sm text-center font-medium ${
                            statusType === "success"
                                ? "bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                                : statusType === "error"
                                ? "bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800"
                                : "bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
                        }`}
                    >
                        {status}
                    </div>
                )}

                {/* TOGGLE CODE / EMAIL */}
                <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800 text-center">
                    <button
                        type="button"
                        onClick={() => {
                            setShowCodeInput(!showCodeInput);
                            setStatus("");
                        }}
                        className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline inline-flex items-center gap-1 cursor-pointer"
                    >
                        {showCodeInput
                            ? isApp
                                ? t("auth.back_to_email_app", "← Anderen Login-Code per E-Mail anfordern")
                                : t("auth.back_to_email_web", "← Zurück zur E-Mail-Anmeldung")
                            : isApp
                                ? t("auth.already_have_code_app", "Bereits einen Code erhalten? 👉 Code eingeben")
                                : t("auth.already_have_code_web", "Code aus der App vorliegen? 👉 Hier eingeben")}
                    </button>
                </div>

                {/* FOOTER */}
                <div className="mt-4 text-[11px] text-slate-400 dark:text-slate-500 text-center">
                    {isApp
                        ? t("auth.no_password_needed_app", "🔒 Kein Passwort nötig – sicher per Magic Link & Einmalcode")
                        : t("auth.no_password_needed_web", "🔒 Kein Passwort nötig – sicher & direkt per Magic Link")}
                </div>

                <div className="mt-3 text-xs text-center">
                    <a href="/" className="text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:underline transition">
                        {t("auth.back_to_home", "← Zurück zur Startseite")}
                    </a>
                </div>

            </div>
        </div>
    );
}

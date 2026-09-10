/*
# src/pages/Login.jsx
*/
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api/client";

export default function Login() {
    const { t, i18n } = useTranslation();
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("");
    const [cooldown, setCooldown] = useState(0);

    async function handleLogin() {
        if (!email || loading || cooldown > 0) return;

        setLoading(true);
        setStatus("");

        try {
            await apiFetch("/api/request-magic-link/", {
                method: "POST",
                body: JSON.stringify({ email, lang: i18n.language }),
            });

            setStatus(t("auth.magic_link_sent", "✅ Check deine E-Mails – dein Login-Link ist unterwegs!"));
            setEmail("");

            // ✅ cooldown starten (15 Sekunden)
            let seconds = 15;
            setCooldown(seconds);

            const interval = setInterval(() => {
                seconds--;
                setCooldown(seconds);

                if (seconds <= 0) {
                    clearInterval(interval);
                }
            }, 1000);

        } catch (err) {
            if (err?.type === "validation" && err.data?.error) {
                // ✅ Backend Validierungsfehler anzeigen
                setStatus(`❌ ${err.data.error}`);
            } else if (err?.message) {
                setStatus(`❌ ${err.message}`);
            } else {
                // ✅ generischer Fehler
                setStatus(t("auth.send_error", "❌ Fehler beim Senden. Bitte erneut versuchen."));
            }
        }

        setLoading(false);
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-6">

            <div className="bg-white w-full max-w-md rounded-2xl shadow-xl p-8">

                {/* HEADER */}
                <div className="text-center mb-6">
                    <h1 className="text-2xl font-bold">
                        Sharegy ⚡
                    </h1>
                    <p className="text-sm text-gray-500">
                        {t("auth.app_tagline", "Energie verstehen & intelligent nutzen")}
                    </p>
                </div>

                {/* TITLE */}
                <h2 className="text-xl font-semibold text-center mb-2">
                    {t("auth.welcome_back", "Willkommen zurück 👋")}
                </h2>

                <p className="text-gray-500 text-sm text-center mb-6">
                    {t("auth.enter_email_desc", "Gib deine E-Mail ein – wir schicken dir einen sicheren Login-Link.")}
                </p>

                {/* INPUT */}
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="deine@email.de"
                    autoFocus
                    onKeyDown={(e) => {
                        if (e.key === "Enter") handleLogin();
                    }}
                    className="w-full border border-gray-300 p-3 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />

                {/* BUTTON */}
                <button
                    onClick={handleLogin}
                    disabled={loading || cooldown > 0}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-medium transition transform hover:scale-[1.02] disabled:opacity-50"
                >
                    {loading
                        ? t("auth.sending_link", "Sende Login-Link…")
                        : cooldown > 0
                            ? t("auth.resend_in", { sec: cooldown, defaultValue: `Erneut senden in ${cooldown}s` })
                            : t("auth.get_link_btn", "Login-Link erhalten")}
                </button>

                {/* STATUS */}
                {status && (
                    <p className="mt-4 text-sm text-center text-gray-600">
                        {status}
                    </p>
                )}

                {/* SPAM HINWEIS ✅ */}
                {status && (
                    <p className="mt-2 text-xs text-center text-gray-400">
                        {t("auth.check_spam", "Falls du nichts siehst: prüfe bitte auch deinen Spam-Ordner 📬")}
                    </p>
                )}

                {/* FOOTER */}
                <div className="mt-6 text-xs text-gray-400 text-center">
                    {t("auth.no_password_needed", "🔒 Kein Passwort nötig – sicher per Magic Link")}
                </div>

                <div className="mt-6 text-sm text-center">
                    <a href="/" className="text-indigo-500 hover:underline">
                        {t("auth.back_to_home", "← Zurück zur Startseite")}
                    </a>
                </div>

            </div>
        </div>
    );
}

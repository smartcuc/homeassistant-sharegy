/*
# src/pages/ConfirmEmailChangePage.jsx
*/

import { useState, useEffect } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useTranslation } from "react-i18next";

export default function ConfirmEmailChangePage() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");
    const navigate = useNavigate();
    const { t } = useTranslation();

    const [status, setStatus] = useState("loading"); // 'loading' | 'success' | 'error'
    const [message, setMessage] = useState("");
    const [newEmail, setNewEmail] = useState("");

    useEffect(() => {
        if (!token) {
            setStatus("error");
            setMessage("Ungültiger oder fehlender Bestätigungslink.");
            return;
        }

        async function verify() {
            try {
                const res = await apiFetch("/api/confirm-email-change/", {
                    method: "POST",
                    body: JSON.stringify({ token }),
                });
                setStatus("success");
                setNewEmail(res.email || "");
                setMessage(res.message || "E-Mail-Adresse erfolgreich bestätigt und aktualisiert!");
            } catch (err) {
                setStatus("error");
                setMessage(err?.data?.error || err?.message || "Bestätigung fehlgeschlagen.");
            }
        }

        verify();
    }, [token]);

    return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
            <div className="bg-slate-800 border border-slate-700 rounded-3xl p-8 max-w-md w-full text-center shadow-2xl text-white space-y-6">
                
                {status === "loading" && (
                    <div className="space-y-4 py-6">
                        <div className="w-12 h-12 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                        <h2 className="text-lg font-bold">{t("email_confirm.verifying_title", "Bestätige E-Mail-Adresse...")}</h2>
                        <p className="text-xs text-slate-400">{t("email_confirm.verifying_desc", "Einen Moment bitte, dein Sicherheitstoken wird geprüft.")}</p>
                    </div>
                )}

                {status === "success" && (
                    <div className="space-y-4 py-4">
                        <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-2xl flex items-center justify-center text-3xl mx-auto">
                            ✅
                        </div>
                        <h2 className="text-xl font-bold text-white">{t("email_confirm.success_title", "E-Mail-Adresse geändert!")}</h2>
                        <p className="text-xs text-slate-300 leading-relaxed">
                            {message}
                        </p>
                        {newEmail && (
                            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700 text-xs font-mono text-indigo-400">
                                {newEmail}
                            </div>
                        )}
                        <div className="pt-4">
                            <Link
                                to="/app/profile"
                                className="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition shadow-lg"
                            >
                                {t("profile.back_to_profile", "Zum Profil zurückkehren")} →
                            </Link>
                        </div>
                    </div>
                )}

                {status === "error" && (
                    <div className="space-y-4 py-4">
                        <div className="w-16 h-16 bg-rose-500/20 text-rose-400 border border-rose-500/40 rounded-2xl flex items-center justify-center text-3xl mx-auto">
                            ⚠️
                        </div>
                        <h2 className="text-xl font-bold text-white">{t("email_confirm.failed_title", "Bestätigung fehlgeschlagen")}</h2>
                        <p className="text-xs text-rose-300 leading-relaxed">
                            {message}
                        </p>
                        <div className="pt-4 space-y-2">
                            <Link
                                to="/app/profile"
                                className="block w-full py-3 px-4 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl text-xs transition"
                            >
                                {t("profile.back_to_profile", "Zum Profil zurück")}
                            </Link>
                            <Link
                                to="/login"
                                className="block w-full py-2.5 px-4 text-slate-400 hover:text-white font-semibold text-xs transition"
                            >
                                {t("common.to_login", "Zur Anmeldung")}
                            </Link>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}

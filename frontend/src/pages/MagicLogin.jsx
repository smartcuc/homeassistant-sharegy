import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { trackEvent } from "../lib/track";
import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";
import { isNativePlatform, triggerHapticFeedback } from "../utils/nativeBridge";

export default function MagicLogin() {
    const navigate = useNavigate();
    const params = useParams();
    const [searchParams] = useSearchParams();
    const queryClient = useQueryClient();

    const token = params.token || searchParams.get("token") || searchParams.get("code");
    const [status, setStatus] = useState("loading");
    const [errorMessage, setErrorMessage] = useState("");

    useEffect(() => {
        if (!token) {
            navigate("/login", { replace: true });
            return;
        }

        async function run() {
            try {
                trackEvent("magic_login_attempt");

                // ✅ STEP 1 — Login
                await apiFetch(`/api/magic-login/?token=${encodeURIComponent(token)}`);

                // ✅ STEP 2 — Session sicherstellen
                let meUser = null;
                for (let i = 0; i < 6; i++) {
                    try {
                        meUser = await apiFetch("/api/auth/me/");
                        if (meUser) break;
                    } catch {
                        // wait and retry
                    }
                    await new Promise((r) => setTimeout(r, 250));
                }

                if (!meUser) {
                    throw new Error("Session konnte nicht initialisiert werden.");
                }

                // ✅ PREFETCH
                await queryClient.prefetchQuery({
                    queryKey: ["user"],
                    queryFn: () => apiFetch("/api/auth/me/"),
                });

                await queryClient.prefetchQuery({
                    queryKey: ["settings"],
                    queryFn: () => apiFetch("/api/settings/"),
                });

                triggerHapticFeedback();
                trackEvent("magic_login_success");
                setStatus("success");

                // Navigation mit kurzer Verzögerung für visuelles Feedback
                setTimeout(() => {
                    navigate("/app/dashboard", { replace: true });
                }, 400);

            } catch (err) {
                console.error("MagicLogin error:", err);
                setStatus("error");
                setErrorMessage(err?.data?.error || err?.message || "Login fehlgeschlagen.");
                trackEvent("magic_login_failed");

                setTimeout(() => {
                    navigate("/login", { replace: true });
                }, 3000);
            }
        }

        run();
    }, [token, navigate, queryClient]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950 p-6 text-white">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl">

                {status === "loading" && (
                    <div>
                        <div className="w-12 h-12 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                        <div className="text-lg font-bold text-slate-100 mb-1">
                            Anmeldung läuft ⚡
                        </div>
                        <div className="text-slate-400 text-xs">
                            Einen kurzen Moment bitte…
                        </div>
                    </div>
                )}

                {status === "success" && (
                    <div>
                        <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-2xl mx-auto mb-4 animate-bounce">
                            ✓
                        </div>
                        <div className="text-lg font-bold text-slate-100 mb-1">
                            Erfolgreich angemeldet!
                        </div>
                        <div className="text-slate-400 text-xs mb-4">
                            Weiterleitung zum Dashboard…
                        </div>

                        {!isNativePlatform() && token && (
                            <div className="mt-4 pt-4 border-t border-slate-800">
                                <a
                                    href={`sharegy://magic?token=${encodeURIComponent(token)}`}
                                    className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold py-2.5 px-4 rounded-xl shadow-lg transition"
                                >
                                    📱 In Sharegy Android App öffnen
                                </a>
                            </div>
                        )}
                    </div>
                )}

                {status === "error" && (
                    <div>
                        <div className="w-12 h-12 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center text-2xl mx-auto mb-4">
                            ✕
                        </div>
                        <div className="text-lg font-bold text-red-400 mb-1">
                            Anmeldung fehlgeschlagen
                        </div>
                        <div className="text-slate-400 text-xs mb-4">
                            {errorMessage || "Der Login-Link ist abgelaufen oder ungültig."}
                        </div>
                        <div className="text-slate-500 text-[11px]">
                            Weiterleitung zum Login…
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}

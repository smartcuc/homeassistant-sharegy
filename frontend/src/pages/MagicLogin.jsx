import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { trackEvent } from "../lib/track";
import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export default function MagicLogin() {
    const navigate = useNavigate();
    const { token } = useParams();
    const queryClient = useQueryClient();

    const [status, setStatus] = useState("loading");

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
                    await new Promise(r => setTimeout(r, 250));
                }

                if (!meUser) {
                    throw new Error("Session not ready");
                }

                // ✅ 🔥 PREFETCH (DAS MACHT DEN UNTERSCHIED)
                await queryClient.prefetchQuery({
                    queryKey: ["user"],
                    queryFn: () => apiFetch("/api/auth/me/"),
                });

                await queryClient.prefetchQuery({
                    queryKey: ["settings"],
                    queryFn: () => apiFetch("/api/settings/"),
                });

                trackEvent("magic_login_success");

                // ✅ STEP 3 — direkt rein
                navigate("/app/dashboard", { replace: true });

            } catch (err) {
                console.error("MagicLogin error:", err);

                setStatus("error");
                trackEvent("magic_login_failed");

                setTimeout(() => {
                    navigate("/login", { replace: true });
                }, 1500);
            }
        }

        run();
    }, [token, navigate, queryClient]);

    return (
        <div className="flex items-center justify-center h-screen">

            {status === "loading" && (
                <div className="text-center">
                    <div className="text-lg font-medium mb-2">
                        Logging you in...
                    </div>
                    <div className="text-gray-400 text-sm">
                        Please wait a moment
                    </div>
                </div>
            )}

            {status === "error" && (
                <div className="text-center text-red-500">
                    Login failed – redirecting...
                </div>
            )}

        </div>
    );
}

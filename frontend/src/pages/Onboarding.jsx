/*
# src/pages/Onboarding.jsx
*/

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useSettings } from "../hooks/useSettings";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export default function Onboarding() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { settings } = useSettings();

    const detectedTimezone =
        Intl.DateTimeFormat()
            .resolvedOptions()
            .timeZone;

    const mutation = useMutation({
        mutationFn: async (step) => {
            await apiFetch("/api/onboarding-step/", {
                method: "POST",
                body: JSON.stringify({
                    onboarding_step: step,
                }),
            });
        },

        onSuccess: (_, step) => {
            queryClient.setQueryData(["settings"], (old) => {
                if (!old) return old;
                return {
                    ...old,
                    onboarding_step: step,
                };
            });
        },
    });

    useEffect(() => {
        if (!settings) return;

        if (settings.onboarding_step === "done") {
            navigate("/app/dashboard", { replace: true });
        }
    }, [settings, navigate]);

    const started = settings && settings.onboarding_step === "setup";

    const needsTimezone =
        started &&
        !settings?.timezone &&
        !!detectedTimezone;

    function updateStep(step) {
        if (mutation.isLoading) return;

        mutation.mutate(step, {
            onSuccess: () => {
                if (step === "done") {
                    navigate("/app/dashboard", { replace: true });
                }
            },
        });
    }

    async function acceptTimezone() {

        await apiFetch("/api/timezone/", {
            method: "POST",
            body: JSON.stringify({
                timezone: detectedTimezone,
            }),
        });

        await queryClient.invalidateQueries({
            queryKey: ["settings"],
        });

        updateStep("done");
    }


    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-6">
            <div className="bg-white w-full max-w-xl rounded-2xl shadow-xl p-8">

                {!started && (
                    <>
                        <h1 className="text-2xl font-bold text-center mb-4">
                            {t("onboarding.welcome_title", "Willkommen bei Sharegy ⚡")}
                        </h1>

                        <p className="text-gray-500 text-center mb-6">
                            {t("onboarding.welcome_subtitle", "Dein persönliches Energy Dashboard ist nur einen Schritt entfernt.")}
                        </p>

                        <div className="space-y-3 text-gray-700 text-sm">
                            <p>✅ {t("onboarding.feature_realtime", "Echtzeit Energieübersicht")}</p>
                            <p>✅ {t("onboarding.feature_production_load", "Produktion & Verbrauch im Blick")}</p>
                            <p>✅ {t("onboarding.feature_optimization", "Automatische Optimierung")}</p>
                        </div>

                        <button
                            onClick={() => updateStep("setup")}
                            disabled={mutation.isLoading}
                            className="mt-8 w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg transition font-medium"
                        >
                            {mutation.isLoading ? "…" : t("onboarding.get_started_btn", "Los geht’s")}
                        </button>
                    </>
                )}

                {started && needsTimezone && (
                    <>
                        <h2 className="text-xl font-semibold text-center mb-4">
                            {t("onboarding.regional_settings", "🌍 Regionale Einstellungen")}
                        </h2>

                        <p className="text-gray-500 text-center mb-3">
                            {t("onboarding.detected_timezone_label", "Wir haben folgende Zeitzone erkannt:")}
                        </p>

                        <div className="text-center mb-2">
                            <span
                                className="
                    inline-block
                    px-4
                    py-2
                    rounded-lg
                    bg-indigo-50
                    text-indigo-700
                    font-medium
                "
                            >
                                {detectedTimezone}
                            </span>
                        </div>

                        <p className="text-xs text-gray-400 text-center mb-6">
                            {t("onboarding.timezone_disclaimer", "Die Erkennung basiert auf den Einstellungen deines Browsers und kann durch VPNs oder Proxys abweichen.")}
                        </p>

                        <div className="space-y-2">

                            <button
                                onClick={acceptTimezone}
                                className="
                                w-full
                                bg-indigo-600
                                hover:bg-indigo-700
                                text-white
                                py-3
                                rounded-lg
                                font-medium
                            "
                            >
                                {t("common.apply", "Übernehmen")}
                            </button>

                            <button
                                onClick={() => updateStep("done")}
                                className="
                                w-full
                                border
                                border-gray-200
                                py-3
                                rounded-lg
                                hover:bg-gray-50
                                font-medium
                           "
                            >
                                {t("common.skip", "Überspringen")}
                            </button>

                        </div>
                    </>
                )}

                {started && !needsTimezone && (
                    <>
                        <h2 className="text-xl font-semibold text-center mb-4">
                            {t("onboarding.ready_title", "Dein Dashboard ist bereit 🚀")}
                        </h2>

                        <p className="text-gray-500 text-center mb-6">
                            {t("onboarding.ready_subtitle", "Starte jetzt mit deinem Energiemanagement.")}
                        </p>

                        <button
                            onClick={() => updateStep("done")}
                            disabled={mutation.isLoading}
                            className="
                            w-full
                            bg-orange-500
                            hover:bg-orange-600
                            text-white
                            py-3
                            rounded-lg
                            font-medium
                        "
                        >
                            {mutation.isLoading ? "…" : t("onboarding.to_dashboard_btn", "Zum Dashboard")}
                        </button>
                    </>
                )}

            </div>
        </div>
    );
}

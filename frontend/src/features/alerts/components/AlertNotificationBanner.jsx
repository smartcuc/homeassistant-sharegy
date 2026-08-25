/*
# src/features/alerts/components/AlertNotificationBanner.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import AlertCenterModal from "./AlertCenterModal";

export default function AlertNotificationBanner() {
    const { t } = useTranslation();
    const [isModalOpen, setIsModalOpen] = useState(false);

    const query = useQuery({
        queryKey: ["alerts-list"],
        queryFn: () => apiFetch("/api/alerts/"),
        refetchInterval: 30000,
    });

    const data = query.data || {};
    const summary = data.summary || { critical: 0, warning: 0, info: 0, active_total: 0 };
    const allAlerts = data.alerts || [];

    const activeAlerts = allAlerts.filter((a) => a.status !== "resolved");
    const topAlert = activeAlerts[0];

    return (
        <>
            {/* =========================================================
                BANNER BAR (WENN AKTIONEN / ALARME VORHANDEN SIND)
            ========================================================= */}
            {activeAlerts.length > 0 && (
                <div
                    onClick={() => setIsModalOpen(true)}
                    className={`rounded-2xl p-3.5 px-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm border cursor-pointer transition-all hover:scale-[1.005] ${summary.critical > 0
                            ? "bg-linear-to-r from-rose-500/10 via-rose-50 to-amber-50/50 border-rose-200 text-rose-950"
                            : summary.warning > 0
                                ? "bg-linear-to-r from-amber-500/10 via-amber-50 to-orange-50/50 border-amber-200 text-amber-950"
                                : "bg-linear-to-r from-emerald-500/10 via-emerald-50 to-teal-50/50 border-emerald-200 text-emerald-950"
                        }`}
                >
                    <div className="flex items-center gap-3">
                        <span className="text-xl flex items-center justify-center w-8 h-8 rounded-xl bg-white shadow-xs border border-gray-200/60">
                            {summary.critical > 0 ? "🔥" : summary.warning > 0 ? "⚠️" : "💡"}
                        </span>
                        <div>
                            <div className="flex items-center gap-2">
                                <span className="font-bold text-xs uppercase tracking-wider">
                                    {summary.critical > 0
                                        ? t("alerts.critical_badge", "Kritische System-Meldung")
                                        : summary.warning > 0
                                            ? t("alerts.warning_badge", "System-Hinweis")
                                            : t("alerts.info_badge", "Spar-Chance")}
                                </span>
                                {summary.active_total > 1 && (
                                    <span className="px-2 py-0.2 rounded-full text-[10px] font-bold bg-white/80 border border-gray-300">
                                        +{summary.active_total - 1} {t("alerts.more", "weitere")}
                                    </span>
                                )}
                            </div>
                            <p className="text-xs font-semibold text-gray-800 line-clamp-1">
                                {topAlert?.title}: {topAlert?.message}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
                        <span className="text-xs font-bold text-indigo-700 bg-white px-3 py-1 rounded-xl border border-indigo-200 shadow-2xs hover:bg-indigo-50">
                            {t("alerts.open_center", "Alarmzentrale öffnen →")}
                        </span>
                    </div>
                </div>
            )}

            {/* =========================================================
                ALARMZENTRALE MODAL
            ========================================================= */}
            <AlertCenterModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        </>
    );
}


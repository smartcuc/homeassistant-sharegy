/*
# src/features/alerts/pages/AlertsPage.jsx
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function AlertsPage() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [filterSeverity, setFilterSeverity] = useState("all");

    const query = useQuery({
        queryKey: ["alerts-list"],
        queryFn: () => apiFetch("/api/alerts/"),
        refetchInterval: 30000,
    });

    const ackMutation = useMutation({
        mutationFn: (alertId) => apiFetch(`/api/alerts/${alertId}/acknowledge/`, { method: "POST" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts-list"] }),
    });

    const resolveMutation = useMutation({
        mutationFn: (alertId) => apiFetch(`/api/alerts/${alertId}/resolve/`, { method: "POST" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts-list"] }),
    });

    const seedDemoMutation = useMutation({
        mutationFn: () => apiFetch("/api/alerts/seed-demo/", { method: "POST" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts-list"] }),
    });

    const data = query.data || {};
    const summary = data.summary || { critical: 0, warning: 0, info: 0, active_total: 0 };
    const allAlerts = data.alerts || [];

    const filteredAlerts = allAlerts.filter((a) => {
        if (filterSeverity === "all") return true;
        if (filterSeverity === "resolved") return a.status === "resolved";
        if (filterSeverity === "active") return a.status !== "resolved";
        return a.severity === filterSeverity && a.status !== "resolved";
    });

    const getSeverityBadge = (sev) => {
        switch (sev) {
            case "critical":
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-700 border border-rose-200">🔴 {t("alerts.critical", "Kritisch")}</span>;
            case "warning":
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">🟡 {t("alerts.warning", "Warnung")}</span>;
            case "info":
            default:
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">🟢 {t("alerts.info", "Spar-Tipp")}</span>;
        }
    };

    return (
        <div className="p-6 max-w-5xl space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2.5">
                        <span className="text-2xl">🚨</span> {t("alerts.page_title", "Alarm- & Notifikationszentrale")}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        {t("alerts.page_subtitle", "Echtzeit-Überwachung von Ertragsausfällen, Akkuzustand, Dauerlasten und Börsenstrom-Chancen.")}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => seedDemoMutation.mutate()}
                        disabled={seedDemoMutation.isPending}
                        className="text-xs px-3.5 py-2 text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-xl transition font-semibold flex items-center gap-1.5 cursor-pointer shadow-2xs"
                    >
                        <span>⚡</span> {t("alerts.seed_demo", "Demo-Alarme erzeugen")}
                    </button>
                </div>
            </div>

            {/* Summary Counters */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
                <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-xs space-y-1">
                    <div className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">{t("alerts.active_total", "Aktive Alarme")}</div>
                    <div className="text-3xl font-black text-slate-900 font-mono">{summary.active_total}</div>
                </div>
                <div className="p-4 rounded-2xl bg-rose-50/60 border border-rose-200/80 shadow-xs space-y-1">
                    <div className="text-[11px] font-bold text-rose-700 uppercase tracking-wider">🔴 {t("alerts.critical", "Kritisch")}</div>
                    <div className="text-3xl font-black text-rose-700 font-mono">{summary.critical}</div>
                </div>
                <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200/80 shadow-xs space-y-1">
                    <div className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">🟡 {t("alerts.warning", "Warnungen")}</div>
                    <div className="text-3xl font-black text-amber-700 font-mono">{summary.warning}</div>
                </div>
                <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200/80 shadow-xs space-y-1">
                    <div className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">🟢 {t("alerts.info", "Spar-Chancen")}</div>
                    <div className="text-3xl font-black text-emerald-700 font-mono">{summary.info}</div>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-2.5 rounded-2xl border border-gray-200 shadow-xs">
                <div className="flex flex-wrap gap-1 bg-gray-100 p-1 rounded-xl text-xs font-semibold">
                    {[
                        { key: "all", label: `${t("common.all", "Alle")} (${allAlerts.length})` },
                        { key: "critical", label: `🔴 ${t("alerts.critical", "Kritisch")} (${summary.critical})` },
                        { key: "warning", label: `🟡 ${t("alerts.warning", "Warnungen")} (${summary.warning})` },
                        { key: "info", label: `🟢 ${t("alerts.info", "Spar-Tipps")} (${summary.info})` },
                        { key: "resolved", label: t("alerts.resolved_history", "Gelöst / Historie") },
                    ].map((tab) => (
                        <button
                            key={tab.key}
                            onClick={() => setFilterSeverity(tab.key)}
                            className={`px-3.5 py-1.5 rounded-lg transition cursor-pointer ${filterSeverity === tab.key
                                    ? "bg-white text-gray-900 shadow-xs font-bold"
                                    : "text-gray-500 hover:text-gray-900"
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className="text-xs text-gray-400 font-medium px-2 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> {t("alerts.live_monitoring", "Live-Überwachung aktiv")}
                </div>
            </div>

            {/* Alerts List */}
            <div className="space-y-3">
                {query.isLoading ? (
                    <div className="bg-white rounded-2xl p-8 border border-gray-200 animate-pulse text-gray-400 text-center">
                        {t("common.loading", "Lade Alarme…")}
                    </div>
                ) : filteredAlerts.length === 0 ? (
                    <div className="bg-white rounded-3xl p-12 border border-gray-200 text-center space-y-3 shadow-xs">
                        <div className="text-5xl">✨</div>
                        <div className="text-lg font-bold text-gray-900">{t("alerts.no_active", "Keine aktiven Alarme")}</div>
                        <p className="text-xs text-gray-500 max-w-md mx-auto">
                            {t("alerts.all_optimal", "Alle überwachten Geräte, Wechselrichter, Speicher und Zähler laufen einwandfrei im optimalen Betriebsbereich.")}
                        </p>
                    </div>
                ) : (
                    filteredAlerts.map((alert) => (
                        <div
                            key={alert.id}
                            className={`p-5 rounded-2xl border transition-all ${alert.status === "resolved"
                                    ? "bg-gray-50/60 border-gray-200 opacity-60"
                                    : alert.severity === "critical"
                                        ? "bg-rose-50/40 border-rose-200/80 shadow-xs"
                                        : alert.severity === "warning"
                                            ? "bg-amber-50/40 border-amber-200/80 shadow-xs"
                                            : "bg-emerald-50/40 border-emerald-200/80 shadow-xs"
                                }`}
                        >
                            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                                <div className="space-y-1.5 flex-1">
                                    <div className="flex flex-wrap items-center gap-2">
                                        {getSeverityBadge(alert.severity)}
                                        <h3 className="font-bold text-base text-gray-900">{alert.title}</h3>
                                        <span className="text-xs text-gray-400 font-mono">
                                            {new Date(alert.created_at).toLocaleString([], { dateStyle: "short", timeStyle: "short" })} Uhr
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-700 leading-relaxed">{alert.message}</p>

                                    {alert.action_hint && (
                                        <div className="pt-2 flex items-center gap-2">
                                            <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-xl inline-flex items-center gap-1.5 shadow-2xs">
                                                <span>👉</span> {alert.action_hint}
                                            </span>
                                        </div>
                                    )}
                                </div>

                                {alert.status !== "resolved" && (
                                    <div className="flex sm:flex-col items-center sm:items-end gap-2 shrink-0">
                                        <button
                                            onClick={() => resolveMutation.mutate(alert.id)}
                                            className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-white border border-gray-200 text-gray-700 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 shadow-2xs transition cursor-pointer"
                                        >
                                            ✓ {t("alerts.mark_resolved", "Erledigt")}
                                        </button>
                                        {alert.status === "active" && (
                                            <button
                                                onClick={() => ackMutation.mutate(alert.id)}
                                                className="px-2.5 py-1 rounded-lg text-[11px] font-medium text-gray-400 hover:text-gray-700 cursor-pointer"
                                            >
                                                {t("alerts.mark_seen", "Gesehen")}
                                            </button>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}


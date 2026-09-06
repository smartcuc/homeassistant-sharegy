/*
# src/features/alerts/components/AlertCenterModal.jsx
*/

import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function AlertCenterModal({ isOpen, onClose }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [filterSeverity, setFilterSeverity] = useState("all");

    /* ESC schließen */
    useEffect(() => {
        if (!isOpen) return;
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [isOpen, onClose]);

    const query = useQuery({
        queryKey: ["alerts-list"],
        queryFn: () => apiFetch("/api/alerts/"),
        refetchInterval: 30000,
        enabled: isOpen,
    });

    const ackMutation = useMutation({
        mutationFn: (alertId) => apiFetch(`/api/alerts/${alertId}/acknowledge/`, { method: "POST" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts-list"] }),
    });

    const resolveMutation = useMutation({
        mutationFn: (alertId) => apiFetch(`/api/alerts/${alertId}/resolve/`, { method: "POST" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts-list"] }),
    });

    if (!isOpen) return null;

    const data = query.data || {};
    const summary = data.summary || { critical: 0, warning: 0, info: 0, active_total: 0 };
    const activeAlerts = data.alerts || [];
    const historyAlerts = data.history || [];

    const filteredAlerts = filterSeverity === "resolved"
        ? historyAlerts
        : activeAlerts.filter((a) => {
            if (filterSeverity === "all" || filterSeverity === "active") return true;
            return a.severity === filterSeverity;
        });

    const getSeverityBadge = (sev) => {
        switch (sev) {
            case "critical":
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900/50">🔴 {t("alerts.severity_critical", "Kritisch")}</span>;
            case "warning":
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-400 border border-amber-200 dark:border-amber-900/50">🟡 {t("alerts.severity_warning", "Warnung")}</span>;
            case "info":
            default:
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900/50">🟢 {t("alerts.severity_info", "Spar-Tipp")}</span>;
        }
    };

    return createPortal(
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/70 backdrop-blur-xs animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div
                className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-800/60">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl sm:text-3xl p-2 sm:p-2.5 bg-white dark:bg-slate-800 rounded-2xl shadow-xs border border-slate-200 dark:border-slate-700">🚨</span>
                        <div>
                            <h2 className="text-lg sm:text-xl font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
                                {t("alerts.modal_title", "Alarm- & Notifikationszentrale")}
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("alerts.modal_subtitle", "Echtzeit-Überwachung von Ertragsausfällen, Akkuzustand, Dauerlasten und Spar-Chancen.")}
                            </p>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="w-9 h-9 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center justify-center text-lg font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Summary & Filters */}
                <div className="px-5 sm:px-6 py-3.5 sm:py-4 border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        <div className="p-2 sm:p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-center">
                            <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">{t("alerts.summary_total", "Aktiv Gesamt")}</div>
                            <div className="text-lg font-black text-slate-800 dark:text-slate-100 font-mono">{summary.active_total}</div>
                        </div>
                        <div className="p-2 sm:p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 text-center">
                            <div className="text-[10px] uppercase font-bold text-rose-600 dark:text-rose-400">🔴 {t("alerts.severity_critical", "Kritisch")}</div>
                            <div className="text-lg font-black text-rose-700 dark:text-rose-300 font-mono">{summary.critical}</div>
                        </div>
                        <div className="p-2 sm:p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 text-center">
                            <div className="text-[10px] uppercase font-bold text-amber-700 dark:text-amber-400">🟡 {t("alerts.severity_warning", "Warnung")}</div>
                            <div className="text-lg font-black text-amber-700 dark:text-amber-300 font-mono">{summary.warning}</div>
                        </div>
                        <div className="p-2 sm:p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 text-center">
                            <div className="text-[10px] uppercase font-bold text-emerald-700 dark:text-emerald-400">🟢 {t("alerts.severity_info", "Spar-Tipp")}</div>
                            <div className="text-lg font-black text-emerald-700 dark:text-emerald-300 font-mono">{summary.info}</div>
                        </div>
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                        <div className="flex flex-wrap gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl text-xs font-semibold">
                            {[
                                { key: "all", label: `${t("alerts.tab_all", "Alle aktiven")} (${activeAlerts.length})` },
                                { key: "critical", label: t("alerts.severity_critical", "Kritisch") },
                                { key: "warning", label: t("alerts.severity_warning", "Warnungen") },
                                { key: "info", label: t("alerts.severity_info", "Spar-Tipps") },
                                { key: "resolved", label: `${t("alerts.tab_history", "Historie")} (${historyAlerts.length})` },
                            ].map((tab) => (
                                <button
                                    key={tab.key}
                                    type="button"
                                    onClick={() => setFilterSeverity(tab.key)}
                                    className={`px-3 py-1 rounded-lg transition cursor-pointer ${filterSeverity === tab.key
                                        ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                                        }`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Alerts List Body */}
                <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-3">
                    {filteredAlerts.length === 0 ? (
                        <div className="py-12 text-center space-y-2">
                            <div className="text-4xl">✨</div>
                            <div className="text-base font-bold text-slate-800 dark:text-slate-200">
                                {filterSeverity === "resolved" ? t("alerts.empty_history", "Keine Einträge in der Historie") : t("alerts.empty_active", "Keine aktiven Alarme")}
                            </div>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {filterSeverity === "resolved"
                                    ? t("alerts.empty_history_desc", "Quittierte oder gelöste Alarme erscheinen hier.")
                                    : t("alerts.empty_active_desc", "Alle überwachten Systeme, Speicher und Erzeugungsanlagen laufen optimal.")}
                            </p>
                        </div>
                    ) : (
                        filteredAlerts.map((alert) => (
                            <div
                                key={alert.id}
                                className={`p-4 rounded-2xl border transition-all ${alert.status === "resolved"
                                    ? "bg-slate-50/60 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700 opacity-70"
                                    : alert.status === "acknowledged"
                                        ? "bg-slate-50/80 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 opacity-80"
                                        : alert.severity === "critical"
                                            ? "bg-rose-50/60 dark:bg-rose-950/40 border-rose-200 dark:border-rose-900/60 shadow-xs"
                                            : alert.severity === "warning"
                                                ? "bg-amber-50/60 dark:bg-amber-950/40 border-amber-200 dark:border-amber-900/60 shadow-xs"
                                                : "bg-emerald-50/60 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900/60 shadow-xs"
                                    }`}
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <div className="space-y-1 flex-1">
                                        <div className="flex flex-wrap items-center gap-2">
                                            {getSeverityBadge(alert.severity)}
                                            {alert.status === "resolved" && (
                                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600">
                                                    ✓ Erledigt
                                                </span>
                                            )}
                                            {alert.status === "acknowledged" && (
                                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                                                    👁️ Quittiert
                                                </span>
                                            )}
                                            <h3 className="font-bold text-sm text-slate-900 dark:text-white">{alert.title}</h3>
                                            <span className="text-[10px] text-slate-400 font-mono">
                                                {new Date(alert.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                            </span>
                                        </div>
                                        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed pt-0.5">{alert.message}</p>

                                        {alert.action_hint && (
                                            <div className="pt-2 flex items-center gap-2">
                                                <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-900/50 px-2.5 py-1 rounded-lg inline-flex items-center gap-1.5">
                                                    <span>👉</span> {alert.action_hint}
                                                </span>
                                            </div>
                                        )}
                                    </div>

                                    {/* Action Buttons */}
                                    {alert.status === "active" && (
                                        <div className="flex flex-col items-end gap-1.5 shrink-0">
                                            <button
                                                type="button"
                                                onClick={() => resolveMutation.mutate(alert.id)}
                                                className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-emerald-50 dark:hover:bg-emerald-950/60 hover:text-emerald-700 dark:hover:text-emerald-300 hover:border-emerald-200 dark:hover:border-emerald-800 transition cursor-pointer"
                                            >
                                                {t("alerts.action_resolve", "✓ Erledigt")}
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => ackMutation.mutate(alert.id)}
                                                className="px-2 py-0.5 rounded-md text-[10px] font-medium text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                                            >
                                                {t("alerts.action_seen", "Quittieren")}
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                    <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> {t("alerts.monitoring_active", "Live-Regelüberwachung aktiv")}
                    </span>
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-1.5 rounded-xl font-bold bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-black dark:hover:bg-slate-100 transition cursor-pointer"
                    >
                        {t("common.close", "Schließen")}
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
}



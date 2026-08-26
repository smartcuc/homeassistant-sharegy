/*
# src/features/alerts/components/AlertCenterModal.jsx
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function AlertCenterModal({ isOpen, onClose }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [filterSeverity, setFilterSeverity] = useState("all");

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
    const activeAlerts = (data.alerts || []).filter(a => a.status !== "resolved");
    const historyAlerts = data.history || (data.alerts || []).filter(a => a.status === "resolved");

    const filteredAlerts = filterSeverity === "resolved"
        ? historyAlerts
        : activeAlerts.filter((a) => {
            if (filterSeverity === "all" || filterSeverity === "active") return true;
            return a.severity === filterSeverity;
        });

    const getSeverityBadge = (sev) => {
        switch (sev) {
            case "critical":
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-700 border border-rose-200">🔴 {t("alerts.severity_critical", "Kritisch")}</span>;
            case "warning":
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">🟡 {t("alerts.severity_warning", "Warnung")}</span>;
            case "info":
            default:
                return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">🟢 {t("alerts.severity_info", "Spar-Tipp")}</span>;
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
            <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-slate-50/70">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl p-2.5 bg-white rounded-2xl shadow-xs border border-gray-200">🚨</span>
                        <div>
                            <h2 className="text-xl font-black text-gray-900 tracking-tight flex items-center gap-2">
                                {t("alerts.modal_title", "Alarm- & Notifikationszentrale")}
                            </h2>
                            <p className="text-xs text-gray-500">
                                {t("alerts.modal_subtitle", "Echtzeit-Überwachung von Ertragsausfällen, Akkuzustand, Dauerlasten und Spar-Chancen.")}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-9 h-9 rounded-full bg-white border border-gray-200 text-gray-400 hover:text-gray-700 hover:bg-gray-100 flex items-center justify-center text-lg font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Summary & Filters */}
                <div className="px-6 py-4 border-b border-gray-100 bg-white space-y-3">
                    <div className="grid grid-cols-4 gap-2">
                        <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-center">
                            <div className="text-[10px] uppercase font-bold text-gray-500">{t("alerts.summary_total", "Aktiv Gesamt")}</div>
                            <div className="text-lg font-black text-slate-800 font-mono">{summary.active_total}</div>
                        </div>
                        <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-center">
                            <div className="text-[10px] uppercase font-bold text-rose-600">🔴 {t("alerts.severity_critical", "Kritisch")}</div>
                            <div className="text-lg font-black text-rose-700 font-mono">{summary.critical}</div>
                        </div>
                        <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-center">
                            <div className="text-[10px] uppercase font-bold text-amber-700">🟡 {t("alerts.severity_warning", "Warnung")}</div>
                            <div className="text-lg font-black text-amber-700 font-mono">{summary.warning}</div>
                        </div>
                        <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-center">
                            <div className="text-[10px] uppercase font-bold text-emerald-700">🟢 {t("alerts.severity_info", "Spar-Tipp")}</div>
                            <div className="text-lg font-black text-emerald-700 font-mono">{summary.info}</div>
                        </div>
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                        <div className="flex flex-wrap gap-1 bg-gray-100 p-1 rounded-xl text-xs font-semibold">
                            {[
                                { key: "all", label: t("alerts.tab_all", "Alle aktiven") },
                                { key: "critical", label: t("alerts.severity_critical", "Kritisch") },
                                { key: "warning", label: t("alerts.severity_warning", "Warnungen") },
                                { key: "info", label: t("alerts.severity_info", "Spar-Tipps") },
                                { key: "resolved", label: t("alerts.tab_history", "Historie") },
                            ].map((tab) => (
                                <button
                                    key={tab.key}
                                    onClick={() => setFilterSeverity(tab.key)}
                                    className={`px-3 py-1 rounded-lg transition cursor-pointer ${filterSeverity === tab.key
                                        ? "bg-white text-gray-900 shadow-xs"
                                        : "text-gray-500 hover:text-gray-900"
                                        }`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Alerts List Body */}
                <div className="flex-1 overflow-y-auto p-6 space-y-3">
                    {filteredAlerts.length === 0 ? (
                        <div className="py-12 text-center space-y-2">
                            <div className="text-4xl">✨</div>
                            <div className="text-base font-bold text-gray-800">
                                {filterSeverity === "resolved" ? t("alerts.empty_history", "Keine gelösten Alarme in der Historie") : t("alerts.empty_active", "Keine aktiven Alarme")}
                            </div>
                            <p className="text-xs text-gray-500">
                                {filterSeverity === "resolved"
                                    ? t("alerts.empty_history_desc", "Es wurden bisher keine Alarme gelöst.")
                                    : t("alerts.empty_active_desc", "Alle überwachten Systeme, Speicher und Erzeugungsanlagen laufen optimal.")}
                            </p>
                        </div>
                    ) : (
                        filteredAlerts.map((alert) => (
                            <div
                                key={alert.id}
                                className={`p-4 rounded-2xl border transition-all ${alert.status === "resolved"
                                    ? "bg-gray-50/60 border-gray-200 opacity-60"
                                    : alert.severity === "critical"
                                        ? "bg-rose-50/50 border-rose-200 shadow-xs"
                                        : alert.severity === "warning"
                                            ? "bg-amber-50/50 border-amber-200 shadow-xs"
                                            : "bg-emerald-50/50 border-emerald-200 shadow-xs"
                                    }`}
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <div className="space-y-1 flex-1">
                                        <div className="flex items-center gap-2">
                                            {getSeverityBadge(alert.severity)}
                                            <h3 className="font-bold text-sm text-gray-900">{alert.title}</h3>
                                            <span className="text-[10px] text-gray-400 font-mono">
                                                {new Date(alert.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-700 leading-relaxed pt-0.5">{alert.message}</p>

                                        {alert.action_hint && (
                                            <div className="pt-2 flex items-center gap-2">
                                                <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2.5 py-1 rounded-lg inline-flex items-center gap-1.5">
                                                    <span>👉</span> {alert.action_hint}
                                                </span>
                                            </div>
                                        )}
                                    </div>

                                    {/* Action Buttons */}
                                    {alert.status !== "resolved" && (
                                        <div className="flex flex-col items-end gap-1.5 shrink-0">
                                            <button
                                                onClick={() => resolveMutation.mutate(alert.id)}
                                                className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-white border border-gray-200 text-gray-700 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 transition cursor-pointer"
                                            >
                                                {t("alerts.action_resolve", "✓ Erledigt")}
                                            </button>
                                            {alert.status === "active" && (
                                                <button
                                                    onClick={() => ackMutation.mutate(alert.id)}
                                                    className="px-2 py-0.5 rounded-md text-[10px] font-medium text-gray-400 hover:text-gray-600 cursor-pointer"
                                                >
                                                    {t("alerts.action_seen", "Gesehen")}
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 bg-slate-50 flex items-center justify-between text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> {t("alerts.monitoring_active", "Live-Regelüberwachung aktiv")}
                    </span>
                    <button
                        onClick={onClose}
                        className="px-4 py-1.5 rounded-xl font-bold bg-gray-900 text-white hover:bg-black transition cursor-pointer"
                    >
                        {t("common.close", "Schließen")}
                    </button>
                </div>
            </div>
        </div>
    );
}


/*
# src/features/alerts/pages/AlertsPage.jsx
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import PushNotificationSettings from "../components/PushNotificationSettings";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

export default function AlertsPage() {
    const { t } = useTranslation();
    const { isPro, proYearlyMonthlyEquiv } = useSubscription();
    const queryClient = useQueryClient();
    const [filterSeverity, setFilterSeverity] = useState("all");
    const [showPushSettings, setShowPushSettings] = useState(false);
    const [proModalOpen, setProModalOpen] = useState(false);

    const query = useQuery({
        queryKey: ["alerts-list"],
        queryFn: () => apiFetch("/api/alerts/"),
        refetchInterval: 30000,
        enabled: isPro,
    });

    const ackMutation = useMutation({
        mutationFn: (alertId) => apiFetch(`/api/alerts/${alertId}/acknowledge/`, { method: "POST" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts-list"] }),
    });

    const resolveMutation = useMutation({
        mutationFn: (alertId) => apiFetch(`/api/alerts/${alertId}/resolve/`, { method: "POST" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts-list"] }),
    });

    const data = query.data || {};
    const summary = data.summary || { critical: 0, warning: 0, info: 0, active_total: 0 };
    const activeAlerts = data.alerts || [];
    const historyAlerts = data.history || [];

    const filteredAlerts = filterSeverity === "resolved"
        ? historyAlerts
        : activeAlerts.filter((a) => {
            if (filterSeverity === "all") return true;
            return a.severity === filterSeverity;
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

    // =========================================================
    // 🛡️ PRO-SPERRSEITE FÜR FREE-NUTZER
    // =========================================================
    if (!isPro) {
        return (
            <div className="p-6 max-w-7xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2.5">
                            <span className="text-2xl">🚨</span> {t("alerts.page_title", "Alarm- & Notifikationszentrale")}
                            <ProBadge size="sm" />
                        </h1>
                        <p className="text-sm text-gray-500 mt-1">
                            {t("alerts.page_subtitle", "Echtzeit-Überwachung von Ertragsausfällen, Akkuzustand, Dauerlasten und Börsenstrom-Chancen.")}
                        </p>
                    </div>
                </div>

                {/* Hero Upgrade Card */}
                <div className="bg-linear-to-br from-slate-900 via-indigo-950 to-slate-950 border border-indigo-500/40 rounded-3xl p-8 sm:p-10 shadow-2xl text-white relative overflow-hidden space-y-8">
                    {/* Background glow */}
                    <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none" />
                    <div className="absolute bottom-0 left-0 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

                    <div className="relative z-10 max-w-3xl space-y-4">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 text-xs font-bold uppercase tracking-wider">
                            <span>⭐</span>
                            <span>Sharegy Pro Exklusiv</span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white leading-tight">
                            Schütze dein Zuhause mit automatischen Echtzeit-Alarmen & Push-Nachrichten
                        </h2>
                        <p className="text-indigo-200/80 text-sm sm:text-base leading-relaxed">
                            Verpasse nie wieder Wechselrichterausfälle, Speicher-Tiefentladungen oder extreme Börsenstrom-Preistiefs. Werde sofort mobil auf deinem Smartphone benachrichtigt.
                        </p>
                    </div>

                    {/* Features Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 relative z-10">
                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">📲</div>
                            <h3 className="text-sm font-bold text-white">Mobile Push-Alarme</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Benachrichtigungen direkt auf dein Android- und iOS-Handy – ohne die App öffnen zu müssen.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">☀️</div>
                            <h3 className="text-sm font-bold text-white">Ertrags- & Ausfallwächter</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Erkennt stillstehende PV-Strings, Netzabschaltungen und unerwartete Leistungsabfälle sofort.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🔋</div>
                            <h3 className="text-sm font-bold text-white">Batterie- & Notstromschutz</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Warnt bei Unterschreitung der Notstromreserve und schützt vor Tiefentladungen im Winter.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">⚡</div>
                            <h3 className="text-sm font-bold text-white">Dynamische Preis-Peaks</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Sofortwarnung vor teuren Verbrauchsspitzen und Hinweis auf negative Börsenstrompreise.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🔌</div>
                            <h3 className="text-sm font-bold text-white">Dauerlast- & Leckage-Finder</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Erkennt vergessene Großverbraucher (z. B. Heizlüfter, Poolpumpe) und hohe Standby-Verbräuche.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">💡</div>
                            <h3 className="text-sm font-bold text-white">KI-Spar-Empfehlungen</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Handlungsanweisungen zur Maximierung deiner Autarkie und Senkung deiner Netzbezugskosten.
                            </p>
                        </div>
                    </div>

                    {/* CTA Actions */}
                    <div className="pt-4 border-t border-indigo-800/40 relative z-10 flex flex-col sm:flex-row items-center justify-between gap-4">
                        <div className="text-xs text-indigo-200/70 text-center sm:text-left">
                            Bereits ab <strong className="text-white font-mono">{proYearlyMonthlyEquiv} €</strong> / Monat (jährliche Zahlweise) · Jederzeit kündbar
                        </div>
                        <div className="flex items-center gap-3 w-full sm:w-auto">
                            <button
                                type="button"
                                onClick={() => setProModalOpen(true)}
                                className="w-full sm:w-auto px-6 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 text-sm font-black rounded-2xl shadow-xl shadow-amber-500/20 transition cursor-pointer flex items-center justify-center gap-2"
                            >
                                <span>⭐</span>
                                <span>Alarmzentrale mit Sharegy Pro freischalten</span>
                            </button>
                        </div>
                    </div>
                </div>

                <ProUpgradeModal
                    open={proModalOpen}
                    onClose={() => setProModalOpen(false)}
                    featureName="Alarmzentrale & Mobile Push-Benachrichtigungen"
                    featureDesc="Schütze deine PV-Anlage, Heimspeicher und Haushaltsgeräte mit automatischen Echtzeit-Alarmen direkt auf dein Smartphone."
                />
            </div>
        );
    }

    // =========================================================
    // ✅ PRO USER VIEW (VOLLE ALARMZENTRALE)
    // =========================================================
    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
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
                        onClick={() => setShowPushSettings(!showPushSettings)}
                        className={`px-3.5 py-2 rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer ${
                            showPushSettings
                                ? "bg-indigo-50 border border-indigo-200 text-indigo-700"
                                : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
                        }`}
                    >
                        <span>📲</span>
                        <span>{showPushSettings ? t("notifications.hide_settings", "Push-Einstellungen schließen") : t("notifications.configure_push", "Push-Alarme einrichten")}</span>
                    </button>
                </div>
            </div>

            {/* PUSH NOTIFICATIONS SETTINGS DRAWER / SECTION */}
            {showPushSettings && (
                <div className="animate-in fade-in duration-200">
                    <PushNotificationSettings />
                </div>
            )}

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
                        { key: "all", label: `${t("common.all", "Alle")} (${activeAlerts.length})` },
                        { key: "critical", label: `🔴 ${t("alerts.critical", "Kritisch")} (${summary.critical})` },
                        { key: "warning", label: `🟡 ${t("alerts.warning", "Warnungen")} (${summary.warning})` },
                        { key: "info", label: `🟢 ${t("alerts.info", "Spar-Tipps")} (${summary.info})` },
                        { key: "resolved", label: `${t("alerts.resolved_history", "Historie")} (${historyAlerts.length})` },
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
                    <div className="bg-white rounded-3xl p-12 border border-gray-200 animate-pulse text-gray-400 text-center space-y-3">
                        <div className="text-3xl">⏳</div>
                        <div className="text-sm font-semibold">{t("common.loading", "Lade Alarme…")}</div>
                    </div>
                ) : filteredAlerts.length === 0 ? (
                    <div className="bg-gradient-to-b from-white to-slate-50/50 rounded-3xl p-10 sm:p-14 border border-slate-200 text-center space-y-6 shadow-sm relative overflow-hidden">
                        <div className="absolute top-0 right-1/2 translate-x-1/2 w-80 h-32 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
                        
                        <div className="relative z-10 w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-700 border border-emerald-200 flex items-center justify-center text-3xl mx-auto shadow-sm">
                            <span>🛡️</span>
                        </div>

                        <div className="relative z-10 space-y-2 max-w-lg mx-auto">
                            <h3 className="text-xl font-black text-slate-900 tracking-tight">
                                {filterSeverity === "resolved" 
                                    ? t("alerts.empty_history", "Keine erledigten Alarme") 
                                    : t("alerts.all_optimal_title", "Alles im grünen Bereich – Keine aktiven Alarme")}
                            </h3>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                {filterSeverity === "resolved"
                                    ? t("alerts.empty_history_desc", "Quittierte oder automatisch gelöste Alarme werden in der Historie archiviert.")
                                    : t("alerts.all_optimal", "Alle überwachten PV-Generatoren, Batteriespeicher, Wechselrichter und Haushaltsverbraucher laufen einwandfrei im optimalen Betriebsbereich.")}
                            </p>
                        </div>

                        {filterSeverity !== "resolved" && (
                            <div className="relative z-10 grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-xl mx-auto pt-2">
                                <div className="p-3 bg-white border border-slate-200 rounded-2xl flex items-center gap-2.5 shadow-2xs">
                                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0 animate-pulse" />
                                    <div className="text-left text-xs">
                                        <div className="font-bold text-slate-800">Solar & Ertrag</div>
                                        <div className="text-[10px] text-slate-400">Normalbetrieb</div>
                                    </div>
                                </div>
                                <div className="p-3 bg-white border border-slate-200 rounded-2xl flex items-center gap-2.5 shadow-2xs">
                                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0 animate-pulse" />
                                    <div className="text-left text-xs">
                                        <div className="font-bold text-slate-800">Speicher & Notstrom</div>
                                        <div className="text-[10px] text-slate-400">Geschützt</div>
                                    </div>
                                </div>
                                <div className="p-3 bg-white border border-slate-200 rounded-2xl flex items-center gap-2.5 shadow-2xs">
                                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0 animate-pulse" />
                                    <div className="text-left text-xs">
                                        <div className="font-bold text-slate-800">Sensoren & Zähler</div>
                                        <div className="text-[10px] text-slate-400">Online</div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    filteredAlerts.map((alert) => (
                        <div
                            key={alert.id}
                            className={`p-5 rounded-2xl border transition-all ${alert.status === "resolved"
                                ? "bg-gray-50/60 border-gray-200 opacity-70"
                                : alert.status === "acknowledged"
                                    ? "bg-slate-50/80 border-slate-200 opacity-80"
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
                                        {alert.status === "resolved" && (
                                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-600 border border-gray-200">
                                                ✓ Erledigt
                                            </span>
                                        )}
                                        {alert.status === "acknowledged" && (
                                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                                                👁️ Quittiert
                                            </span>
                                        )}
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

                                {alert.status === "active" && (
                                    <div className="flex sm:flex-col items-center sm:items-end gap-2 shrink-0">
                                        <button
                                            onClick={() => resolveMutation.mutate(alert.id)}
                                            className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-white border border-gray-200 text-gray-700 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 shadow-2xs transition cursor-pointer"
                                        >
                                            ✓ {t("alerts.mark_resolved", "Erledigt")}
                                        </button>
                                        <button
                                            onClick={() => ackMutation.mutate(alert.id)}
                                            className="px-2.5 py-1 rounded-lg text-[11px] font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-100 cursor-pointer"
                                        >
                                            {t("alerts.mark_seen", "Quittieren")}
                                        </button>
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

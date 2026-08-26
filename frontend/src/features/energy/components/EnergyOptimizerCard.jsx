/*
# src/features/energy/components/EnergyOptimizerCard.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function EnergyOptimizerCard() {
    const { t } = useTranslation();
    const [duration, setDuration] = useState("4h");

    const optimizerQuery = useQuery({
        queryKey: ["energy-optimizer"],
        queryFn: () => apiFetch("/api/energy/optimizer/?horizon=24"),
        refetchInterval: 60000,
    });

    const data = optimizerQuery.data || {};
    const windows = data.windows || {};
    const currentWindow = windows[duration] || null;
    const timeline = data.timeline || [];

    const durationTabs = [
        { key: "1h", label: t("optimizer.duration_1h", "1 Stunde"), icon: "🧺", desc: t("optimizer.duration_1h_desc", "Waschmaschine, Geschirrspüler") },
        { key: "2h", label: t("optimizer.duration_2h", "2 Stunden"), icon: "♨️", desc: t("optimizer.duration_2h_desc", "Wärmepumpe, Wäschetrockner") },
        { key: "4h", label: t("optimizer.duration_4h", "4 Stunden"), icon: "🚗", desc: t("optimizer.duration_4h_desc", "Wallbox (E-Auto), Speicher") },
    ];

    if (optimizerQuery.isLoading) {
        return (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-xs animate-pulse">
                <div className="h-6 w-48 bg-slate-200 rounded-md mb-4" />
                <div className="h-24 bg-slate-100 rounded-xl" />
            </div>
        );
    }

    if (!currentWindow) {
        return null;
    }

    const best = currentWindow.best_overall;
    const bestNight = currentWindow.best_night;
    const worst = currentWindow.worst;
    const deviceInfo = currentWindow.device_info || {};

    const maxTimelinePrice = Math.max(...timeline.map((it) => it.effective_cost_ct || 0), 40.0);

    return (
        <div className="bg-linear-to-br from-slate-900 via-indigo-950 to-slate-900 border border-indigo-900/60 rounded-3xl p-6 shadow-xl text-white space-y-6">
            {/* =========================================================
                HEADER & DURATION SELECTOR
            ========================================================= */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-indigo-800/40 pb-5">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">🧠</span>
                        <h2 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
                            {t("energy.optimizer_title", "Smart Energy Optimizer")}
                        </h2>
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            {t("energy.live_ai_plan", "Live KI-Fahrplan")}
                        </span>
                    </div>
                    <p className="text-xs text-indigo-200/70 mt-1">
                        {t("energy.optimizer_subtitle", "Optimale Lade- und Betriebszeiten berechnet aus PV-Erzeugungsprognose und Börsenstrompreisen.")}
                    </p>
                </div>

                {/* Duration Pills */}
                <div className="inline-flex bg-slate-800/80 p-1.5 rounded-2xl border border-indigo-700/50 shadow-inner self-start sm:self-auto gap-1">
                    {durationTabs.map((tab) => (
                        <button
                            key={tab.key}
                            onClick={() => setDuration(tab.key)}
                            className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${duration === tab.key
                                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/40"
                                : "text-indigo-200/70 hover:text-white hover:bg-slate-700/50"
                                }`}
                        >
                            <span>{tab.icon}</span>
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* =========================================================
                MAIN RECOMMENDATION HERO CARDS
            ========================================================= */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* 1. Best Time Overall (Tag / PV-Spitze) */}
                <div className="p-5 rounded-2xl bg-linear-to-br from-emerald-950/60 to-emerald-900/30 border border-emerald-500/40 space-y-3 relative overflow-hidden">
                    <div className="absolute -right-4 -top-4 w-20 h-20 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />

                    <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1">
                            🏆 {t("energy.best_slot", "Beste Zeit")} ({duration})
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-slate-950">
                            {best.source === "pv_surplus" ? t("optimizer.solar_100", "☀️ 100% Solar") : t("optimizer.market_low", "⚡ Börsentief")}
                        </span>
                    </div>

                    <div>
                        <div className="text-2xl sm:text-3xl font-black font-mono text-white tracking-tight">
                            {best.start_label} – {best.end_label}
                        </div>
                        <div className="text-xs text-emerald-200/80 mt-0.5">
                            {best.date_label} · Ø {best.avg_cost_ct.toFixed(1)} ct/kWh
                        </div>
                    </div>

                    <div className="pt-2 border-t border-emerald-800/40 flex items-center justify-between text-xs">
                        <span className="text-emerald-300/80">{t("optimizer.savings_vs_peak", "Ersparnis vs. Peak:")}</span>
                        <span className="font-mono font-bold text-emerald-300">
                            +{Number(currentWindow.savings_eur || 0).toFixed(2)} €
                        </span>
                    </div>
                </div>

                {/* 2. Best Night Window (Nachtstrom / Pendler) */}
                {bestNight ? (
                    <div className="p-5 rounded-2xl bg-linear-to-br from-indigo-950/60 to-indigo-900/30 border border-indigo-500/30 space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1">
                                🌙 {t("energy.night_slot", "Nacht-Alternative")}
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                                {t("energy.wind_power", "Windstrom")}
                            </span>
                        </div>

                        <div>
                            <div className="text-2xl sm:text-3xl font-black font-mono text-white tracking-tight">
                                {bestNight.start_label} – {bestNight.end_label}
                            </div>
                            <div className="text-xs text-indigo-200/80 mt-0.5">
                                {bestNight.date_label} · Ø {bestNight.avg_cost_ct.toFixed(1)} ct/kWh
                            </div>
                        </div>

                        <div className="pt-2 border-t border-indigo-800/40 text-[11px] text-indigo-300/70">
                            {t("optimizer.night_ideal", "Ideal für automatisches Laden über Nacht bis zur Abfahrt")}
                        </div>
                    </div>
                ) : (
                    <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/50 space-y-3 flex items-center justify-center text-xs text-gray-400">
                        {t("optimizer.night_none", "Kein separates Nachtfenster erforderlich")}
                    </div>
                )}

                {/* 3. Avoid Peak Window */}
                {worst && (
                    <div className="p-5 rounded-2xl bg-linear-to-br from-rose-950/50 to-rose-900/20 border border-rose-500/30 space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1">
                                ⚠️ {t("energy.worst_slot", "Spitzenzeit (Vermeiden)")}
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                                {t("energy.evening_peak", "Abendpeak")}
                            </span>
                        </div>

                        <div>
                            <div className="text-2xl sm:text-3xl font-black font-mono text-rose-200 tracking-tight">
                                {worst.start_label} – {worst.end_label}
                            </div>
                            <div className="text-xs text-rose-300/70 mt-0.5">
                                {worst.date_label} · Ø {worst.avg_cost_ct.toFixed(1)} ct/kWh
                            </div>
                        </div>

                        <div className="pt-2 border-t border-rose-800/40 text-[11px] text-rose-300/70">
                            {t("optimizer.pause_loads", "Flexible Lasten in dieser Zeitspanne pausieren oder sperren")}
                        </div>
                    </div>
                )}
            </div>

            {/* =========================================================
                INTERACTIVE 24H SCHEDULE TIMELINE
            ========================================================= */}
            <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs">
                    <div className="font-bold uppercase tracking-wider text-indigo-200 flex items-center gap-2">
                        <span>📊</span> {t("energy.schedule_timeline", "24h-Stundenplan & Preisprofil")}
                    </div>
                    <div className="flex items-center gap-3 text-[11px] font-medium">
                        <span className="flex items-center gap-1 text-emerald-400">
                            <span className="w-2.5 h-2.5 rounded-xs bg-emerald-400 inline-block" /> {t("optimizer.cheap_solar", "Günstig / Solar")}
                        </span>
                        <span className="flex items-center gap-1 text-amber-400">
                            <span className="w-2.5 h-2.5 rounded-xs bg-amber-400 inline-block" /> {t("energy.acceptable", "Akzeptabel")}
                        </span>
                        <span className="flex items-center gap-1 text-rose-400">
                            <span className="w-2.5 h-2.5 rounded-xs bg-rose-500 inline-block" /> {t("energy.expensive", "Teuer")}
                        </span>
                    </div>
                </div>

                {/* Timeline Visual Columns */}
                <div className="bg-slate-950/60 border border-indigo-900/60 rounded-2xl p-4 pt-6">
                    <div className="h-36 flex items-end justify-between gap-1.5 border-b border-indigo-800/30 pb-2">
                        {timeline.slice(0, 24).map((pt, idx) => {
                            const barHeight = Math.max(15, (pt.effective_cost_ct / maxTimelinePrice) * 100);
                            const isInsideBest = idx >= best.start_idx && idx < (best.start_idx + currentWindow.duration_hours);

                            let barColor = "bg-amber-400 hover:bg-amber-300";
                            if (pt.status === "green") {
                                barColor = "bg-emerald-400 hover:bg-emerald-300";
                            } else if (pt.status === "red") {
                                barColor = "bg-rose-500 hover:bg-rose-400";
                            }

                            return (
                                <div
                                    key={idx}
                                    className={`flex-1 flex flex-col items-center gap-1 h-full justify-end group relative transition-all duration-200 ${isInsideBest ? "scale-105 z-10" : "opacity-85 hover:opacity-100"
                                        }`}
                                >
                                    {/* Best Slot Indicator Top Glow */}
                                    {isInsideBest && (
                                        <div className="absolute -top-3.5 text-[9px] font-black text-emerald-300 bg-emerald-950 border border-emerald-500/60 px-1 rounded-sm shadow-sm animate-bounce">
                                            TOP
                                        </div>
                                    )}

                                    {/* Bar Column */}
                                    <div
                                        className={`w-full max-w-[28px] rounded-t-sm transition-all duration-300 shadow-sm ${barColor} ${isInsideBest ? "ring-2 ring-emerald-300 ring-offset-1 ring-offset-slate-900" : ""
                                            }`}
                                        style={{ height: `${barHeight}%` }}
                                        title={`${pt.time_label} (${pt.date_label}): ${pt.effective_cost_ct} ct/kWh ${pt.pv_kw > 0 ? `| ☀️ ${pt.pv_kw} kW` : ""}`}
                                    />

                                    {/* Hour Label */}
                                    <span
                                        className={`text-[10px] font-mono mt-1 whitespace-nowrap truncate w-full text-center ${isInsideBest ? "font-bold text-emerald-300" : "text-indigo-300/60"
                                            }`}
                                    >
                                        {pt.time_label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>

                    <div className="mt-2.5 flex items-center justify-between text-[11px] text-indigo-300/60 font-medium">
                        <span>{t("energy.now", "Jetzt")} ({timeline[0]?.time_label || "00:00"})</span>
                        <span className="text-emerald-300 font-semibold">
                            {t("optimizer.recommended_window", { duration, start: best.start_label, end: best.end_label, defaultValue: `Empfohlenes ${duration}-Fenster: ${best.start_label} – ${best.end_label}` })}
                        </span>
                        <span>{t("optimizer.in_24h", "In 24 Stunden")}</span>
                    </div>
                </div>
            </div>

            {/* =========================================================
                DEVICE RECOMMENDATION TIP
            ========================================================= */}
            <div className="p-4 bg-indigo-900/30 border border-indigo-700/40 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2.5">
                    <span className="text-2xl p-2 bg-indigo-800/50 rounded-xl">{deviceInfo.icon}</span>
                    <div>
                        <div className="font-bold text-white">{t("optimizer.recommended_for", { duration, defaultValue: `Empfohlenes Einsatzszenario für ${duration}:` })}</div>
                        <div className="text-indigo-200/80">{deviceInfo.device_name} ({t("optimizer.approx_demand", { kwh: currentWindow.total_kwh_typical, defaultValue: `ca. ${currentWindow.total_kwh_typical} kWh Energiebedarf` })})</div>
                    </div>
                </div>

                <div className="text-right self-end sm:self-auto">
                    <div className="text-emerald-300 font-mono font-bold text-sm">
                        {t("optimizer.savings_add", { val: Number(currentWindow.savings_eur || 0).toFixed(2), defaultValue: `+${Number(currentWindow.savings_eur || 0).toFixed(2)} € Ersparnis` })}
                    </div>
                    <div className="text-[10px] text-indigo-300/60">{t("optimizer.per_run", "pro Durchlauf / Ladezyklus")}</div>
                </div>
            </div>
        </div>
    );
}


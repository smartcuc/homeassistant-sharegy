/*
# src/features/energy/components/EnergyOptimizerCard.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

export default function EnergyOptimizerCard() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [duration, setDuration] = useState("1h");
    const [proModalOpen, setProModalOpen] = useState(false);

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
        { key: "2h", label: t("optimizer.duration_2h", "2 Stunden"), icon: "♨️", desc: t("optimizer.duration_2h_desc", "Wärmepumpe, Wäschetrockner"), isProGated: true },
        { key: "4h", label: t("optimizer.duration_4h", "4 Stunden"), icon: "🚗", desc: t("optimizer.duration_4h_desc", "Wallbox (E-Auto), Speicher"), isProGated: true },
    ];

    const handleDurationClick = (tab) => {
        if (tab.isProGated && !isPro) {
            setProModalOpen(true);
            return;
        }
        setDuration(tab.key);
    };

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
                            type="button"
                            onClick={() => handleDurationClick(tab)}
                            className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${duration === tab.key
                                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/40"
                                : "text-indigo-200/70 hover:text-white hover:bg-slate-700/50"
                                }`}
                        >
                            <span>{tab.icon}</span>
                            <span>{tab.label}</span>
                            {tab.isProGated && !isPro && <ProBadge size="xs" />}
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
                        <div className="text-xs text-emerald-300 font-semibold mt-1">
                            {best.effective_cost_ct > 0
                                ? `Effektive Stromkosten: ~${best.effective_cost_ct} ct/kWh`
                                : "0,00 ct/kWh (reiner Solar-Überschuss)"}
                        </div>
                    </div>

                    <div className="text-[11px] text-emerald-200/80 bg-emerald-900/40 border border-emerald-700/50 rounded-xl p-2.5">
                        {best.recommendation_text}
                    </div>
                </div>

                {/* 2. Best Time Night (Nachtfenster) */}
                <div className="p-5 rounded-2xl bg-linear-to-br from-indigo-950/60 to-slate-900/40 border border-indigo-500/40 space-y-3 relative overflow-hidden">
                    <div className="absolute -right-4 -top-4 w-20 h-20 bg-indigo-500/10 rounded-full blur-xl pointer-events-none" />

                    <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1">
                            🌙 {t("energy.best_night_slot", "Günstigstes Nachtfenster")}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500 text-white">
                            {t("energy.market_spot", "Börsenpreis")}
                        </span>
                    </div>

                    <div>
                        <div className="text-2xl sm:text-3xl font-black font-mono text-white tracking-tight">
                            {bestNight.start_label} – {bestNight.end_label}
                        </div>
                        <div className="text-xs text-indigo-300 font-semibold mt-1">
                            {bestNight.effective_cost_ct > 0
                                ? `Effektive Stromkosten: ~${bestNight.effective_cost_ct} ct/kWh`
                                : "0,00 ct/kWh"}
                        </div>
                    </div>

                    <div className="text-[11px] text-indigo-200/80 bg-indigo-900/40 border border-indigo-700/50 rounded-xl p-2.5">
                        {bestNight.recommendation_text}
                    </div>
                </div>

                {/* 3. Worst Time (Spitzenlast & Teuerste Stunde) */}
                <div className="p-5 rounded-2xl bg-linear-to-br from-rose-950/60 to-rose-900/30 border border-rose-500/40 space-y-3 relative overflow-hidden">
                    <div className="absolute -right-4 -top-4 w-20 h-20 bg-rose-500/10 rounded-full blur-xl pointer-events-none" />

                    <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1">
                            🚫 {t("energy.avoid_slot", "Verbrauchsspitze meiden")}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500 text-white">
                            {t("energy.expensive_peak", "Teuer")}
                        </span>
                    </div>

                    <div>
                        <div className="text-2xl sm:text-3xl font-black font-mono text-white tracking-tight">
                            {worst.start_label} – {worst.end_label}
                        </div>
                        <div className="text-xs text-rose-300 font-semibold mt-1">
                            Effektive Stromkosten: ~{worst.effective_cost_ct} ct/kWh
                        </div>
                    </div>

                    <div className="text-[11px] text-rose-200/80 bg-rose-900/40 border border-rose-700/50 rounded-xl p-2.5">
                        {worst.recommendation_text}
                    </div>
                </div>
            </div>

            {/* =========================================================
                TIMELINE HOURLY COST BARS
            ========================================================= */}
            <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs text-indigo-200/80">
                    <span className="font-bold flex items-center gap-1.5">
                        <span>📊</span> {t("energy.timeline_title", "Effektive Kostenkurve & Zeitfenster der nächsten 24h")}
                    </span>
                    <div className="flex items-center gap-3 text-[11px]">
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-400 inline-block" /> {t("energy.legend_free_pv", "0 ct (Solar)")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-sm bg-indigo-400 inline-block" /> {t("energy.legend_market", "Günstiger Börsenstrom")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-sm bg-rose-400 inline-block" /> {t("energy.legend_peak", "Preishoch")}
                        </span>
                    </div>
                </div>

                {/* Timeline Grid */}
                <div className="bg-slate-950/60 border border-indigo-900/50 rounded-2xl p-4 overflow-x-auto">
                    <div className="min-w-[650px] flex items-end gap-1.5 h-28 pt-2">
                        {timeline.map((pt, idx) => {
                            const isInsideBest = pt.hour_idx >= best.start_hour && pt.hour_idx <= best.end_hour;
                            const heightPct = Math.max(8, Math.round((pt.effective_cost_ct / maxTimelinePrice) * 100));

                            return (
                                <div
                                    key={idx}
                                    className={`flex-1 flex flex-col items-center justify-end h-full group relative ${isInsideBest ? "opacity-100" : "opacity-85 hover:opacity-100"
                                        }`}
                                >
                                    {/* Tooltip Hover */}
                                    <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col bg-slate-900 border border-indigo-500/50 rounded-xl p-2 shadow-2xl text-[11px] z-50 whitespace-nowrap pointer-events-none">
                                        <span className="font-bold text-white">{pt.time_label} Uhr</span>
                                        <span className="text-emerald-400">{pt.is_pv_available ? "☀️ Solarüberschuss aktiv" : "⚡ Netzbezug"}</span>
                                        <span className="font-mono text-indigo-300 font-bold">{pt.effective_cost_ct} ct/kWh</span>
                                    </div>

                                    {/* Bar Element */}
                                    <div
                                        className={`w-full rounded-t-sm transition-all duration-200 ${pt.effective_cost_ct === 0
                                            ? "bg-emerald-400 shadow-sm shadow-emerald-400/50"
                                            : pt.is_peak_price
                                                ? "bg-rose-400"
                                                : isInsideBest
                                                    ? "bg-emerald-500 shadow-sm shadow-emerald-500/40"
                                                    : "bg-indigo-500"
                                            }`}
                                        style={{ height: `${heightPct}%` }}
                                    />

                                    {/* Time Label */}
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

            {/* Pro Upgrade Dialog */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Multi-Dauer Smart Energy Optimizer (2h & 4h)"
                featureDesc="Optimiere lange Verbraucher wie Wärmepumpen, Wäschetrockner und E-Auto Wallboxen automatisch mit erweiterten Zeitfenstern und Live Börsenstromdaten."
            />
        </div>
    );
}

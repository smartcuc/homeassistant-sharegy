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
                HEADER & DURATION SELECTOR (ALIGNED WITH ARBITRAGE CARD)
            ========================================================= */}
            <div className="space-y-4 border-b border-indigo-800/40 pb-5">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-xl shadow-2xs shrink-0">
                        🧠
                    </div>
                    <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                            <h2 className="text-base font-bold text-white whitespace-nowrap">
                                {t("energy.optimizer_title", "Smart Energy Optimizer")}
                            </h2>
                            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">
                                {t("energy.live_ai_plan", "Live KI-Fahrplan")}
                            </span>
                        </div>
                        <p className="text-xs text-indigo-200/70 mt-0.5 line-clamp-2 sm:line-clamp-none">
                            {t("energy.optimizer_subtitle", "Optimale Lade- und Betriebszeiten berechnet aus PV-Erzeugungsprognose und Börsenstrompreisen.")}
                        </p>
                    </div>
                </div>

                {/* Duration Pills Toolbar */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                    <span className="text-[11px] font-semibold text-indigo-200/70">
                        Geplante Laufzeit:
                    </span>
                    <div className="flex flex-wrap items-center bg-slate-800/90 p-1 rounded-2xl border border-indigo-700/50 shadow-inner gap-1">
                        {durationTabs.map((tab) => (
                            <button
                                key={tab.key}
                                type="button"
                                onClick={() => handleDurationClick(tab)}
                                className={`px-2.5 sm:px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer shrink-0 ${duration === tab.key
                                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/40"
                                    : "text-indigo-200/70 hover:text-white hover:bg-slate-700/50"
                                    }`}
                            >
                                <span className="text-xs">{tab.icon}</span>
                                <span>{tab.label}</span>
                                {tab.isProGated && !isPro && <ProBadge size="xs" className="shrink-0" />}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* =========================================================
                MAIN RECOMMENDATION HERO CARDS
            ========================================================= */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* 1. Best Time Overall (Tag / PV-Spitze) */}
                <div className="p-4 sm:p-5 rounded-2xl bg-linear-to-br from-emerald-950/60 to-emerald-900/30 border border-emerald-500/40 space-y-3 relative overflow-hidden flex flex-col justify-between">
                    <div className="absolute -right-4 -top-4 w-20 h-20 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />

                    <div className="space-y-3 relative z-10">
                        {/* Header Badge Row */}
                        <div className="flex flex-wrap items-center justify-between gap-1.5 border-b border-emerald-500/20 pb-2.5">
                            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
                                <span>🏆</span>
                                <span>{t("energy.best_slot", "Beste Zeit")} ({duration})</span>
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-slate-950 shrink-0 shadow-2xs">
                                {best.source === "pv_surplus" ? t("optimizer.solar_100", "☀️ 100% Solar") : t("optimizer.market_low", "⚡ Börsentief")}
                            </span>
                        </div>

                        {/* Uhrzeit & Preis */}
                        <div>
                            <div className="text-xl sm:text-2xl font-black font-mono text-white tracking-tight">
                                {best.start_label} – {best.end_label} Uhr
                            </div>
                            <div className="mt-1.5 flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                                <span className="text-sm font-black font-mono text-emerald-400">
                                    {Number(best.avg_cost_ct ?? best.effective_cost_ct ?? 0).toFixed(1)} ct/kWh
                                </span>
                                <span className="text-[11px] text-emerald-300/80 font-medium">
                                    {best.source === "pv_surplus" ? "· Kostenloser Solar-Überschuss" : "· Günstigster Börsenpreis"}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Handlungsempfehlung Box */}
                    <div className="text-[11px] text-emerald-200/90 bg-emerald-900/50 border border-emerald-700/60 rounded-xl p-3 relative z-10 leading-relaxed mt-2">
                        {best.recommendation_text || `⚡ Ideal für energieintensive Geräte (${deviceInfo.device_name || "Haushaltsgeräte"}). Maximale Ersparnis durch Eigenstromnutzung.`}
                    </div>
                </div>

                {/* 2. Best Time Night (Nachtfenster) */}
                <div className="p-4 sm:p-5 rounded-2xl bg-linear-to-br from-indigo-950/60 to-slate-900/40 border border-indigo-500/40 space-y-3 relative overflow-hidden flex flex-col justify-between">
                    <div className="absolute -right-4 -top-4 w-20 h-20 bg-indigo-500/10 rounded-full blur-xl pointer-events-none" />

                    <div className="space-y-3 relative z-10">
                        {/* Header Badge Row */}
                        <div className="flex flex-wrap items-center justify-between gap-1.5 border-b border-indigo-500/20 pb-2.5">
                            <span className="text-xs font-bold uppercase tracking-wider text-indigo-200 flex items-center gap-1.5">
                                <span>🌙</span>
                                <span>{t("energy.best_night_slot", "Günstigstes Nachtfenster")}</span>
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500 text-white shrink-0 shadow-2xs">
                                {t("energy.market_spot", "Börsenpreis")}
                            </span>
                        </div>

                        {/* Uhrzeit & Preis */}
                        <div>
                            <div className="text-xl sm:text-2xl font-black font-mono text-white tracking-tight">
                                {bestNight ? `${bestNight.start_label} – ${bestNight.end_label} Uhr` : "Kein Nachtfenster"}
                            </div>
                            <div className="mt-1.5 flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                                <span className="text-sm font-black font-mono text-indigo-300">
                                    {bestNight ? `${Number(bestNight.avg_cost_ct ?? bestNight.effective_cost_ct ?? 0).toFixed(1)} ct/kWh` : "-"}
                                </span>
                                <span className="text-[11px] text-indigo-200/80 font-medium">
                                    · Niedrigster Spot-Tarif der Nacht
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Handlungsempfehlung Box */}
                    <div className="text-[11px] text-indigo-200/90 bg-indigo-900/50 border border-indigo-700/60 rounded-xl p-3 relative z-10 leading-relaxed mt-2">
                        {bestNight?.recommendation_text || "🌙 Niedrigste Strompreise der Nacht. Optimal für verzögerte Gerätestarts oder Netz-Nachladung des Speichers."}
                    </div>
                </div>

                {/* 3. Worst Time (Spitzenlast & Teuerste Stunde) */}
                <div className="p-4 sm:p-5 rounded-2xl bg-linear-to-br from-rose-950/60 to-rose-900/30 border border-rose-500/40 space-y-3 relative overflow-hidden flex flex-col justify-between">
                    <div className="absolute -right-4 -top-4 w-20 h-20 bg-rose-500/10 rounded-full blur-xl pointer-events-none" />

                    <div className="space-y-3 relative z-10">
                        {/* Header Badge Row */}
                        <div className="flex flex-wrap items-center justify-between gap-1.5 border-b border-rose-500/20 pb-2.5">
                            <span className="text-xs font-bold uppercase tracking-wider text-rose-300 flex items-center gap-1.5">
                                <span>🚫</span>
                                <span>{t("energy.avoid_slot", "Verbrauchsspitze meiden")}</span>
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500 text-white shrink-0 shadow-2xs">
                                {t("energy.expensive_peak", "Teuer")}
                            </span>
                        </div>

                        {/* Uhrzeit & Preis */}
                        <div>
                            <div className="text-xl sm:text-2xl font-black font-mono text-white tracking-tight">
                                {worst ? `${worst.start_label} – ${worst.end_label} Uhr` : "-"}
                            </div>
                            <div className="mt-1.5 flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                                <span className="text-sm font-black font-mono text-rose-400">
                                    {worst ? `${Number(worst.avg_cost_ct ?? worst.effective_cost_ct ?? 0).toFixed(1)} ct/kWh` : "-"}
                                </span>
                                <span className="text-[11px] text-rose-300/80 font-medium">
                                    · Preishoch & Spitzenlast
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Handlungsempfehlung Box */}
                    <div className="text-[11px] text-rose-200/90 bg-rose-900/50 border border-rose-700/60 rounded-xl p-3 relative z-10 leading-relaxed mt-2">
                        {worst?.recommendation_text || "⚠️ Hohe Netzbezugskosten. Schalte flexible Lasten ab und decke den Verbrauch bevorzugt aus dem Batteriespeicher."}
                    </div>
                </div>
            </div>

            {/* =========================================================
                TIMELINE HOURLY COST BARS
            ========================================================= */}
            <div className="space-y-3 pt-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-indigo-200/80">
                    <span className="font-bold flex items-center gap-1.5 text-white">
                        <span>📊</span> {t("energy.timeline_title", "Effektive Kostenkurve & Zeitfenster der nächsten 24h")}
                    </span>
                    <div className="flex flex-wrap items-center gap-3 text-[11px]">
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-400 inline-block" /> {t("energy.legend_free_pv", "0 ct (Solar-Überschuss)")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-sm bg-indigo-400 inline-block" /> {t("energy.legend_market", "Günstiger Börsenstrom")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-sm bg-rose-400 inline-block" /> {t("energy.legend_peak", "Spitzenpreis")}
                        </span>
                    </div>
                </div>

                {/* Timeline Grid */}
                <div className="bg-slate-950/60 border border-indigo-900/50 rounded-2xl p-4 overflow-visible">
                    <div className="min-w-[650px] flex items-end gap-1.5 h-36 pt-8 pb-1 relative">
                        {timeline.map((pt, idx) => {
                            const isInsideBest = (
                                best.start_idx !== undefined &&
                                idx >= best.start_idx &&
                                idx < best.start_idx + currentWindow.duration_hours
                            );
                            const costVal = Number(pt.effective_cost_ct || 0);
                            const isSurplus = Boolean(pt.is_surplus || pt.is_pv_available || costVal <= 8.2);
                            const isPeak = pt.status === "red" || costVal >= 32.0;

                            // Höhe: Minimum 14% für 0 ct Solar, Maximum 100%
                            const heightPct = isSurplus
                                ? 14
                                : Math.min(100, Math.max(14, Math.round((costVal / Math.max(maxTimelinePrice, 35.0)) * 100)));

                            // Dynamische Ausrichtung des Tooltips (linksbündig am Anfang, rechtsbündig am Ende, zentriert in der Mitte)
                            const tooltipPosClass = idx < 3 
                                ? "left-0 translate-x-0" 
                                : idx > timeline.length - 4 
                                    ? "right-0 translate-x-0" 
                                    : "left-1/2 -translate-x-1/2";

                            return (
                                <div
                                    key={idx}
                                    className={`flex-1 flex flex-col items-center justify-end h-full group relative ${
                                        isInsideBest ? "opacity-100" : "opacity-80 hover:opacity-100"
                                    }`}
                                >
                                    {/* Tooltip Hover mit sicherer Positionierung */}
                                    <div className={`absolute bottom-full mb-2 hidden group-hover:flex flex-col bg-slate-900/95 backdrop-blur-md border border-indigo-500/60 rounded-xl p-2.5 shadow-2xl text-[11px] z-50 whitespace-nowrap pointer-events-none ${tooltipPosClass}`}>
                                        <div className="font-bold text-white flex items-center justify-between gap-3">
                                            <span>{pt.time_label} Uhr ({pt.date_label || "Heute"})</span>
                                            <span className="font-mono text-emerald-400 font-bold">{costVal.toFixed(1)} ct/kWh</span>
                                        </div>
                                        <div className="text-[10px] text-slate-300 mt-0.5">
                                            {isSurplus 
                                                ? `☀️ Solarüberschuss (${Number(pt.pv_kw || 0).toFixed(1)} kW PV)` 
                                                : `⚡ Netzbezug (${Number(pt.grid_price_ct || costVal).toFixed(1)} ct)`}
                                        </div>
                                        {isInsideBest && (
                                            <div className="mt-1 text-[9px] font-bold text-emerald-300 uppercase tracking-wider">
                                                ★ Empfohlenes Zeitfenster
                                            </div>
                                        )}
                                    </div>

                                    {/* Bar Element */}
                                    <div
                                        className={`w-full rounded-t-sm transition-all duration-300 ${
                                            isSurplus
                                                ? "bg-emerald-400 shadow-sm shadow-emerald-400/40"
                                                : isPeak
                                                    ? "bg-rose-400 shadow-sm shadow-rose-400/30"
                                                    : isInsideBest
                                                        ? "bg-emerald-500 ring-2 ring-emerald-400 shadow-md shadow-emerald-500/50"
                                                        : "bg-indigo-500"
                                        }`}
                                        style={{ height: `${heightPct}%` }}
                                    />

                                    {/* Time Label */}
                                    <span
                                        className={`text-[10px] font-mono mt-1.5 whitespace-nowrap truncate w-full text-center ${
                                            isInsideBest 
                                                ? "font-bold text-emerald-300 scale-105" 
                                                : "text-indigo-300/60"
                                        }`}
                                    >
                                        {pt.time_label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>

                    <div className="mt-3 pt-2.5 border-t border-indigo-900/40 flex flex-wrap items-center justify-between gap-2 text-[11px] text-indigo-300/70 font-medium">
                        <span>{t("energy.now", "Jetzt")} ({timeline[0]?.time_label || "00:00"} Uhr)</span>
                        <span className="text-emerald-300 font-semibold flex items-center gap-1">
                            <span>★</span>
                            <span>{t("optimizer.recommended_window", { duration, start: best.start_label, end: best.end_label, defaultValue: `Empfohlenes ${duration}-Fenster: ${best.start_label} – ${best.end_label} Uhr` })}</span>
                        </span>
                        <span>{t("optimizer.in_24h", "24-Stunden Prognose")}</span>
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

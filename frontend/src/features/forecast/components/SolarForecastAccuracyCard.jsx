/*
# src/features/forecast/components/SolarForecastAccuracyCard.jsx
*/

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useSolarForecastAccuracy } from "../hooks/useSolarForecastAccuracy";
import { formatNumber } from "../../../utils/format";

export default function SolarForecastAccuracyCard({ stringId = "all" }) {
    const { t } = useTranslation();
    const [period, setPeriod] = useState("today");

    const query = useSolarForecastAccuracy(period, stringId);
    const data = query.data || {};

    const accuracyPct = data.accuracy_percent ?? 0;
    const ratingLabel = data.rating_label || "Gut";
    const ratingDesc = data.rating_desc || "";
    const badgeColor = data.badge_color || "emerald";

    const totalActual = data.total_actual_kwh ?? 0;
    const totalForecast = data.total_forecast_kwh ?? 0;
    const deltaKwh = data.delta_kwh ?? 0;
    const deltaPct = data.delta_percent ?? 0;
    const calibFactor = data.calibration_factor ?? 1.0;
    const points = data.points || [];
    const insights = data.insights || [];

    const maxChartValue = Math.max(
        ...points.map((p) => Math.max(p.actual_kwh || 0, p.forecast_kwh || 0)),
        1.0
    );

    const periods = [
        { key: "today", label: t("forecast.accuracy_today", "Heute (Stündlich)") },
        { key: "7d", label: t("forecast.accuracy_7d", "Letzte 7 Tage") },
        { key: "30d", label: t("forecast.accuracy_30d", "Letzte 30 Tage") },
    ];

    const getBadgeClasses = (color) => {
        switch (color) {
            case "emerald":
                return "bg-emerald-100 text-emerald-800 border-emerald-300";
            case "amber":
                return "bg-amber-100 text-amber-800 border-amber-300";
            case "blue":
            default:
                return "bg-indigo-100 text-indigo-800 border-indigo-300";
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-xs border border-gray-200 overflow-hidden">
            {/* Header */}
            <div className="p-5 sm:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-amber-50/40 via-white to-indigo-50/30">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-xl shadow-2xs">
                        🎯
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                            {t("forecast.accuracy_title", "Solar-Prognosegüte & Ist-vs-Soll-Vergleich")}
                        </h2>
                        <p className="text-xs text-gray-500">
                            {t("forecast.accuracy_subtitle", "Automatischer Abgleich zwischen KI-Wettermodell und gemessener Wechselrichter-Erzeugung.")}
                        </p>
                    </div>
                </div>

                {/* Period Selector Tabs */}
                <div className="inline-flex bg-gray-100 p-1 rounded-xl border border-gray-200 self-start sm:self-auto">
                    {periods.map((p) => (
                        <button
                            key={p.key}
                            onClick={() => setPeriod(p.key)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${period === p.key
                                ? "bg-white text-gray-900 shadow-xs font-bold"
                                : "text-gray-600 hover:text-gray-900"
                                }`}
                        >
                            {p.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content Body */}
            <div className="p-5 sm:p-6 space-y-6">
                {query.isLoading ? (
                    <div className="py-12 text-center text-gray-400 animate-pulse text-sm">
                        {t("common.loading", "Lade Prognosegüte & Ist-vs-Soll Daten...")}
                    </div>
                ) : (
                    <>
                        {/* KPI Metrics Grid */}
                        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
                            {/* Hero Accuracy Score */}
                            <div className="col-span-2 sm:col-span-1 p-4 rounded-2xl bg-gradient-to-br from-slate-900 to-indigo-950 text-white shadow-xs flex flex-col justify-between">
                                <div className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider">
                                    {t("forecast.accuracy_rate", "Prognose-Genauigkeit")}
                                </div>
                                <div className="my-2">
                                    <div className="text-3xl sm:text-4xl font-black font-mono tracking-tight text-white flex items-baseline gap-1">
                                        {formatNumber(accuracyPct, 1)} <span className="text-lg font-bold text-indigo-300">%</span>
                                    </div>
                                    <span className={`inline-block mt-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border ${getBadgeClasses(badgeColor)}`}>
                                        {ratingLabel}
                                    </span>
                                </div>
                                <div className="text-[10px] text-indigo-200/80 leading-tight">
                                    {ratingDesc}
                                </div>
                            </div>

                            {/* Tatsächlich Gemessen */}
                            <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200/80 shadow-2xs flex flex-col justify-between">
                                <div className="text-[11px] font-bold uppercase tracking-wider text-amber-800 flex items-center gap-1.5">
                                    <span>☀️</span> {t("forecast.actual_production", "Ist (Gemessen)")}
                                </div>
                                <div className="text-2xl font-black text-slate-900 font-mono my-2">
                                    {formatNumber(totalActual, 2)} <span className="text-xs font-normal text-gray-500">kWh</span>
                                </div>
                                <div className="text-[11px] text-amber-700/90 font-medium">
                                    Realer Solar-Ertrag
                                </div>
                            </div>

                            {/* Prognostiziert */}
                            <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-200/70 shadow-2xs flex flex-col justify-between">
                                <div className="text-[11px] font-bold uppercase tracking-wider text-indigo-800 flex items-center gap-1.5">
                                    <span>⛅</span> {t("forecast.expected_production", "Soll (Prognose)")}
                                </div>
                                <div className="text-2xl font-black text-slate-900 font-mono my-2">
                                    {formatNumber(totalForecast, 2)} <span className="text-xs font-normal text-gray-500">kWh</span>
                                </div>
                                <div className="text-[11px] text-indigo-700/90 font-medium">
                                    Physik/ML Modell
                                </div>
                            </div>

                            {/* Abweichung Delta */}
                            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 shadow-2xs flex flex-col justify-between">
                                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-700">
                                    Δ {t("forecast.deviation", "Abweichung")}
                                </div>
                                <div className={`text-2xl font-black font-mono my-2 ${deltaKwh >= 0 ? "text-emerald-700" : "text-amber-700"}`}>
                                    {deltaKwh > 0 ? `+${formatNumber(deltaKwh, 2)}` : formatNumber(deltaKwh, 2)} <span className="text-xs font-normal text-gray-500">kWh</span>
                                </div>
                                <div className="text-[11px] text-gray-500 font-medium">
                                    {deltaPct >= 0 ? `+${deltaPct}% Mehrertrag` : `${deltaPct}% Minderertrag`}
                                </div>
                            </div>

                            {/* Kalibrierungs-Faktor */}
                            <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200/70 shadow-2xs flex flex-col justify-between">
                                <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
                                    <span>🤖</span> {t("forecast.calibration_factor", "Kalibrier-Faktor")}
                                </div>
                                <div className="text-2xl font-black text-slate-900 font-mono my-2">
                                    {calibFactor.toFixed(3)}x
                                </div>
                                <div className="text-[11px] text-emerald-700 font-medium">
                                    Adaptive Anpassung
                                </div>
                            </div>
                        </div>

                        {/* =========================================================
                            DUAL-BAR / IST-VS-SOLL TIME SERIES CHART
                        ========================================================= */}
                        <div className="p-4 sm:p-5 rounded-2xl bg-slate-50/80 border border-slate-200 space-y-4">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                <div className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                                    📈 {t("forecast.chart_title", "Stundenvergleich: Erzeugung (Ist) vs. Prognose (Soll)")}
                                </div>
                                <div className="flex items-center gap-4 text-xs font-semibold">
                                    <div className="flex items-center gap-1.5">
                                        <span className="w-3 h-3 rounded-xs bg-amber-500 inline-block shadow-2xs" />
                                        <span className="text-gray-700">{t("forecast.actual", "Ist (Gemessen)")}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <span className="w-3 h-1 rounded-full bg-indigo-500 border border-dashed border-indigo-400 inline-block" />
                                        <span className="text-indigo-700">{t("forecast.forecast", "Soll (Prognose)")}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Chart Bars */}
                            <div className="h-56 sm:h-64 flex items-end gap-1 sm:gap-2 pt-6 pb-2 px-2 overflow-x-auto">
                                {points.map((pt, idx) => {
                                    const actHeight = Math.max(Math.min((pt.actual_kwh / maxChartValue) * 100, 100), pt.actual_kwh > 0 ? 4 : 0);
                                    const fcHeight = Math.max(Math.min((pt.forecast_kwh / maxChartValue) * 100, 100), pt.forecast_kwh > 0 ? 4 : 0);

                                    return (
                                        <div
                                            key={idx}
                                            className="flex-1 min-w-[28px] sm:min-w-[34px] flex flex-col items-center justify-end h-full group relative"
                                        >
                                            {/* Hover Tooltip */}
                                            <div className="absolute -top-12 z-20 hidden group-hover:flex flex-col items-center pointer-events-none transition-all duration-150">
                                                <div className="bg-slate-900 text-white text-[11px] font-semibold py-1 px-2.5 rounded-lg shadow-xl whitespace-nowrap border border-slate-700 flex items-center gap-2">
                                                    <span>⏰ {pt.time_str}</span>
                                                    <span className="text-amber-400">☀️ Ist: {formatNumber(pt.actual_kwh, 2)} kWh</span>
                                                    <span className="text-indigo-300">⛅ Soll: {formatNumber(pt.forecast_kwh, 2)} kWh</span>
                                                    {pt.accuracy_pct !== null && (
                                                        <span className="text-emerald-400 font-bold">🎯 {pt.accuracy_pct}%</span>
                                                    )}
                                                </div>
                                                <div className="w-2 h-2 bg-slate-900 rotate-45 -mt-1" />
                                            </div>

                                            {/* Dual Bars Visualization */}
                                            <div className="w-full h-full flex items-end justify-center gap-0.5 sm:gap-1 px-0.5">
                                                {/* Actual Bar (Amber) */}
                                                <div
                                                    style={{ height: `${actHeight}%` }}
                                                    className="w-1/2 bg-gradient-to-t from-amber-500 to-amber-400 rounded-t-sm transition-all duration-300 hover:brightness-110 shadow-2xs"
                                                />
                                                {/* Forecast Bar (Indigo/Cyan) */}
                                                <div
                                                    style={{ height: `${fcHeight}%` }}
                                                    className="w-1/2 bg-gradient-to-t from-indigo-500/80 to-indigo-400/70 border border-indigo-400/50 rounded-t-sm transition-all duration-300 hover:brightness-110"
                                                />
                                            </div>

                                            {/* X-Axis Label */}
                                            <div className="text-[10px] text-gray-500 mt-1 font-mono tracking-tighter truncate w-full text-center">
                                                {pt.time_str}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Insights & Self-Learning Feedback Loop */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-1">
                            <div className="p-4 rounded-2xl bg-amber-50/50 border border-amber-200/60 text-xs text-amber-950 space-y-2">
                                <div className="font-bold uppercase tracking-wider text-amber-800 text-[11px] flex items-center gap-1.5">
                                    <span>💡</span> {t("forecast.insights_title", "Analyse & Erkenntnisse")}
                                </div>
                                <ul className="space-y-1">
                                    {insights.map((ins, i) => (
                                        <li key={i} className="flex items-start gap-1.5">
                                            <span>•</span>
                                            <span>{ins}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-200/60 text-xs text-indigo-950 space-y-2">
                                <div className="font-bold uppercase tracking-wider text-indigo-800 text-[11px] flex items-center gap-1.5">
                                    <span>🧠</span> {t("forecast.learning_title", "Adaptive Selbstkalibrierung")}
                                </div>
                                <p className="text-gray-600 leading-relaxed">
                                    Das hybride Prognosemodell vergleicht stetig die Abweichungen zu realen Einstrahlungswerten. Systematische Einflüsse wie Teilverschattungen am Nachmittag oder Alterung der Module werden automatisch in zukünftige Vorhersagen eingerechnet.
                                </p>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}


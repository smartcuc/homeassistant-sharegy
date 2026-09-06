/*
# src/features/forecast/components/SolarForecastAccuracyCard.jsx
*/

import { useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { useSolarForecastAccuracy } from "../hooks/useSolarForecastAccuracy";
import { formatNumber } from "../../../utils/format";
import { translateInsight } from "../../../utils/translateInsight";

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

    // =========================================================
    // 📊 ECHARTS OPTION MIT DATAZOOM SLIDER
    // =========================================================
    const echartsOption = useMemo(() => {
        if (!points || points.length === 0) return null;

        const categories = points.map((p) => p.time_str);
        const actualData = points.map((p) => p.actual_kwh ?? 0);
        const forecastData = points.map((p) => p.forecast_kwh ?? 0);

        // Slider bei 30 Tagen oder mehr als 14 Datenpunkten aktivieren
        const showSlider = period === "30d" || points.length > 14;
        const initialEnd = period === "30d" ? 45 : 100;

        return {
            tooltip: {
                trigger: "axis",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                borderColor: "#334155",
                borderRadius: 12,
                padding: [10, 14],
                textStyle: { color: "#fff", fontSize: 12 },
                formatter: (params) => {
                    const idx = params[0]?.dataIndex ?? 0;
                    const pt = points[idx];
                    if (!pt) return "";
                    let accHtml = "";
                    if (pt.accuracy_pct !== null && pt.accuracy_pct !== undefined) {
                        accHtml = `<div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #334155; color: #34d399; font-weight: bold; font-size: 11px;">🎯 Trefferquote: ${pt.accuracy_pct}%</div>`;
                    }
                    return `
                        <div style="font-weight: bold; margin-bottom: 6px; font-size: 12px; color: #cbd5e1;">⏰ ${pt.time_str}</div>
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 2px;">
                            <span style="color: #fbbf24; font-size: 11px;">☀️ Ist (Gemessen):</span>
                            <b>${formatNumber(pt.actual_kwh, 2)} kWh</b>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px;">
                            <span style="color: #818cf8; font-size: 11px;">⛅ Soll (Prognose):</span>
                            <b>${formatNumber(pt.forecast_kwh, 2)} kWh</b>
                        </div>
                        ${accHtml}
                    `;
                },
            },
            legend: {
                show: false,
            },
            grid: {
                top: 25,
                left: 45,
                right: 20,
                bottom: showSlider ? 55 : 30,
            },
            xAxis: {
                type: "category",
                data: categories,
                axisLine: { lineStyle: { color: "#cbd5e1" } },
                axisLabel: {
                    color: "#64748b",
                    fontSize: 11,
                    interval: period === "30d" ? "auto" : 0,
                    hideOverlap: true,
                },
                axisTick: { alignWithLabel: true },
            },
            yAxis: {
                type: "value",
                name: "kWh",
                nameTextStyle: { color: "#94a3b8", fontSize: 10 },
                splitLine: { lineStyle: { color: "#f1f5f9" } },
                axisLabel: {
                    color: "#64748b",
                    fontSize: 11,
                    formatter: (val) => `${val}`,
                },
            },
            dataZoom: showSlider
                ? [
                      {
                          type: "slider",
                          show: true,
                          start: 0,
                          end: initialEnd,
                          height: 24,
                          bottom: 8,
                          borderColor: "transparent",
                          backgroundColor: "#f1f5f9",
                          fillerColor: "rgba(99, 102, 241, 0.18)",
                          handleStyle: {
                              color: "#6366f1",
                              borderColor: "#4f46e5",
                              shadowBlur: 2,
                              shadowColor: "rgba(0, 0, 0, 0.1)",
                          },
                          textStyle: { color: "#64748b", fontSize: 10 },
                      },
                      {
                          type: "inside",
                      },
                  ]
                : [],
            series: [
                {
                    name: "Ist (Gemessen)",
                    type: "bar",
                    data: actualData,
                    itemStyle: {
                        color: "#f59e0b",
                        borderRadius: [4, 4, 0, 0],
                    },
                    barGap: "20%",
                    barCategoryGap: period === "30d" ? "30%" : "40%",
                    maxBarWidth: 32,
                },
                {
                    name: "Soll (Prognose)",
                    type: "bar",
                    data: forecastData,
                    itemStyle: {
                        color: "#6366f1",
                        borderRadius: [4, 4, 0, 0],
                    },
                    maxBarWidth: 32,
                },
            ],
        };
    }, [points, period]);

    return (
        <div className="bg-white rounded-2xl shadow-xs border border-gray-200 overflow-hidden w-full max-w-full min-w-0">
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
                <div className="inline-flex bg-gray-100 p-1 rounded-xl border border-gray-200 self-start sm:self-auto shrink-0">
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
            <div className="p-5 sm:p-6 space-y-6 w-full max-w-full min-w-0 overflow-hidden">
                {query.isLoading ? (
                    <div className="py-12 text-center text-gray-400 animate-pulse text-sm">
                        {t("common.loading", "Lade Prognosegüte & Ist-vs-Soll Daten...")}
                    </div>
                ) : (
                    <>
                        {/* KPI Metrics Grid */}
                        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5 w-full max-w-full min-w-0">
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
                            DUAL-BAR / IST-VS-SOLL TIME SERIES CHART MIT ECHARTS SLIDER
                        ========================================================= */}
                        <div className="p-4 sm:p-5 rounded-2xl bg-slate-50/80 border border-slate-200 space-y-4 w-full max-w-full min-w-0 overflow-hidden">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                <div className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                                    📈 {period === "today"
                                        ? t("forecast.chart_title_hourly", "Stundenvergleich: Erzeugung (Ist) vs. Prognose (Soll)")
                                        : t("forecast.chart_title_daily", "Tagesvergleich: Erzeugung (Ist) vs. Prognose (Soll)")}
                                </div>
                                <div className="flex items-center gap-4 text-xs font-semibold">
                                    <div className="flex items-center gap-1.5">
                                        <span className="w-3 h-3 rounded-xs bg-amber-500 inline-block shadow-2xs" />
                                        <span className="text-gray-700">{t("forecast.actual", "Ist (Gemessen)")}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <span className="w-3 h-3 rounded-xs bg-indigo-500 inline-block shadow-2xs" />
                                        <span className="text-indigo-700">{t("forecast.forecast", "Soll (Prognose)")}</span>
                                    </div>
                                </div>
                            </div>

                            {/* ECharts Dual-Bar Chart mit Zoom Slider */}
                            {!echartsOption ? (
                                <div className="py-12 text-center text-gray-400 text-xs font-medium bg-white/60 rounded-xl border border-dashed border-slate-200">
                                    {t("forecast.no_accuracy_chart_data", "Noch keine Erzeugungs- oder Prognosedaten für diesen Zeitraum erfasst.")}
                                </div>
                            ) : (
                                <div className="w-full h-72 sm:h-80">
                                    <ReactECharts
                                        option={echartsOption}
                                        style={{ height: "100%", width: "100%" }}
                                        notMerge={true}
                                        lazyUpdate={true}
                                    />
                                </div>
                            )}
                        </div>

                        {/* Insights & Self-Learning Feedback Loop */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-1">
                            <div className="p-4 rounded-2xl bg-amber-50/50 border border-amber-200/60 text-xs text-amber-950 space-y-2">
                                <div className="font-bold uppercase tracking-wider text-amber-800 text-[11px] flex items-center gap-1.5">
                                    <span>💡</span> {t("forecast.insights_title", "Analyse & Erkenntnisse")}
                                </div>
                                <ul className="space-y-1">
                                    {insights.map((ins, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                            <span className="text-amber-500 font-bold">•</span>
                                            <span>{translateInsight(ins, t)}</span>
                                        </li>
                                    ))}
                                    {insights.length === 0 && (
                                        <li className="text-gray-400">{t("forecast.no_anomalies", "Keine spezifischen Auffälligkeiten im gewählten Zeitraum.")}</li>
                                    )}
                                </ul>
                            </div>

                            <div className="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-200/60 text-xs text-indigo-950 space-y-2">
                                <div className="font-bold uppercase tracking-wider text-indigo-800 text-[11px] flex items-center gap-1.5">
                                    <span>🧠</span> {t("forecast.learning_loop_title", "Selbstlernendes Korrektur-Modell")}
                                </div>
                                <p className="text-indigo-900/90 leading-relaxed">
                                    Die Sharegy-Engine passt den standortbezogenen Dämpfungsfaktor (Wolkendurchzug, Neigungswinkel, Verschmutzung) kontinuierlich an reale Erträge an.
                                </p>
                                <div className="text-[11px] font-mono text-indigo-700 bg-indigo-100/50 px-2.5 py-1 rounded-lg inline-block">
                                    Kalibrierungs-Multiplikator: {calibFactor.toFixed(3)}x
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

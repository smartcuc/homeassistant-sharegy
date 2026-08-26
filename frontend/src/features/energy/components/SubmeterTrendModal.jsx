/*
# src/features/energy/components/SubmeterTrendModal.jsx
*/

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../../api/client";

export default function SubmeterTrendModal({ meter, isOpen, onClose, defaultPeriod = "30d" }) {
    const { t } = useTranslation();
    const [period, setPeriod] = useState(defaultPeriod);
    const [chartMode, setChartMode] = useState("coverage"); // 'coverage', 'consumption', 'costs'

    const trendQuery = useQuery({
        queryKey: ["submeter-trends", period, meter?.id],
        queryFn: () => apiFetch(`/api/energy/submeters/trends/?period=${period}&meter_id=${meter?.id}`),
        enabled: Boolean(isOpen && meter?.id),
        staleTime: 60_000,
    });

    const data = trendQuery.data;
    const meterMeta = data?.selected_meter || meter;
    const timeseries = data?.selected_timeseries || [];

    const periods = [
        { key: "today", label: t("energy.period_today", "Heute") },
        { key: "7d", label: t("energy.period_7d", "Letzte 7 Tage") },
        { key: "30d", label: t("energy.period_30d", "Letzte 30 Tage") },
        { key: "year", label: t("energy.period_year", "Dieses Jahr") },
    ];

    const chartModes = [
        { key: "coverage", label: t("submeters.mode_coverage", "🟢 Solare Deckung vs. Netz"), icon: "☀️" },
        { key: "consumption", label: t("submeters.mode_consumption", "⚡ Gesamtverbrauch"), icon: "📊" },
        { key: "costs", label: t("submeters.cost_savings_tab", "💶 Kosten & Ersparnis"), icon: "💰" },
    ];

    const chartOption = useMemo(() => {
        const currentTimeseries = data?.selected_timeseries || [];
        const currentMeterMeta = data?.selected_meter || meter;
        if (!currentTimeseries || currentTimeseries.length === 0) return null;

        const dates = currentTimeseries.map((pt) => pt.date);

        if (chartMode === "coverage") {
            return {
                tooltip: {
                    trigger: "axis",
                    axisPointer: { type: "shadow" },
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                    borderColor: "#e2e8f0",
                    textStyle: { color: "#1e293b", fontSize: 12 },
                    extraCssText: "box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-radius: 0.75rem;",
                    formatter: (params) => {
                        if (!params || !params.length) return "";
                        let html = `<div style="font-weight:bold;margin-bottom:4px;">${params[0].name}</div>`;
                        params.forEach((item) => {
                            const val = Number(item.value || 0);
                            html += `<div style="display:flex;justify-content:space-between;gap:12px;font-size:11px;">
                                <span>${item.marker} ${item.seriesName}:</span>
                                <span style="font-weight:bold;font-family:monospace;">${val.toFixed(2)} kWh</span>
                            </div>`;
                        });
                        return html;
                    },
                },
                legend: {
                    data: [t("submeters.solar_self_share", "Solar-Eigenstrom"), t("submeters.grid_share", "Netzbezug")],
                    bottom: 0,
                    textStyle: { fontSize: 11, color: "#64748b" },
                },
                grid: {
                    left: "2%",
                    right: "2%",
                    bottom: "12%",
                    top: "10%",
                    containLabel: true,
                },
                xAxis: {
                    type: "category",
                    data: dates,
                    axisLabel: { fontSize: 11, color: "#94a3b8" },
                    axisLine: { lineStyle: { color: "#cbd5e1" } },
                },
                yAxis: {
                    type: "value",
                    axisLabel: { formatter: "{value} kWh", fontSize: 11, color: "#94a3b8" },
                    splitLine: { lineStyle: { color: "#f1f5f9", type: "dashed" } },
                },
                series: [
                    {
                        name: t("submeters.solar_self_share", "Solar-Eigenstrom"),
                        type: "bar",
                        stack: "coverage",
                        itemStyle: { color: "#10b981" },
                        data: currentTimeseries.map((pt) => Number(pt.solar_kwh || 0)),
                    },
                    {
                        name: t("submeters.grid_share", "Netzbezug"),
                        type: "bar",
                        stack: "coverage",
                        itemStyle: { color: "#64748b" },
                        data: currentTimeseries.map((pt) => Number(pt.grid_kwh || 0)),
                    },
                ],
            };
        }

        if (chartMode === "consumption") {
            return {
                tooltip: {
                    trigger: "axis",
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                    borderColor: "#e2e8f0",
                    textStyle: { color: "#1e293b", fontSize: 12 },
                    extraCssText: "box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-radius: 0.75rem;",
                    formatter: (params) => {
                        const p = params[0];
                        return `<div style="font-weight:bold;">${p.name}</div>
                            <div style="margin-top:2px;font-size:12px;">${t("submeters.consumption_kwh", "Verbrauch")}: <b>${Number(p.value).toFixed(2)} kWh</b></div>`;
                    },
                },
                grid: {
                    left: "2%",
                    right: "2%",
                    bottom: "5%",
                    top: "10%",
                    containLabel: true,
                },
                xAxis: {
                    type: "category",
                    data: dates,
                    axisLabel: { fontSize: 11, color: "#94a3b8" },
                    axisLine: { lineStyle: { color: "#cbd5e1" } },
                },
                yAxis: {
                    type: "value",
                    axisLabel: { formatter: "{value} kWh", fontSize: 11, color: "#94a3b8" },
                    splitLine: { lineStyle: { color: "#f1f5f9", type: "dashed" } },
                },
                series: [
                    {
                        name: t("submeters.consumption_kwh", "Verbrauch"),
                        type: "line",
                        smooth: true,
                        showSymbol: false,
                        itemStyle: { color: currentMeterMeta?.color || "#6366f1" },
                        lineStyle: { width: 3, color: currentMeterMeta?.color || "#6366f1" },
                        areaStyle: {
                            color: {
                                type: "linear",
                                x: 0,
                                y: 0,
                                x2: 0,
                                y2: 1,
                                colorStops: [
                                    { offset: 0, color: currentMeterMeta?.color ? `${currentMeterMeta.color}66` : "rgba(99, 102, 241, 0.4)" },
                                    { offset: 1, color: currentMeterMeta?.color ? `${currentMeterMeta.color}00` : "rgba(99, 102, 241, 0.0)" },
                                ],
                            },
                        },
                        data: currentTimeseries.map((pt) => Number(pt.kwh || 0)),
                    },
                ],
            };
        }

        // Costs Mode
        return {
            tooltip: {
                trigger: "axis",
                axisPointer: { type: "shadow" },
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                borderColor: "#e2e8f0",
                textStyle: { color: "#1e293b", fontSize: 12 },
                extraCssText: "box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-radius: 0.75rem;",
                formatter: (params) => {
                    if (!params || !params.length) return "";
                    let html = `<div style="font-weight:bold;margin-bottom:4px;">${params[0].name}</div>`;
                    params.forEach((item) => {
                        const val = Number(item.value || 0);
                        html += `<div style="display:flex;justify-content:space-between;gap:12px;font-size:11px;">
                            <span>${item.marker} ${item.seriesName}:</span>
                            <span style="font-weight:bold;font-family:monospace;">${val.toFixed(2)} €</span>
                        </div>`;
                    });
                    return html;
                },
            },
            legend: {
                data: [t("submeters.electricity_cost", "Stromkosten (€)"), t("submeters.solar_savings", "Solar-Ersparnis (€)")],
                bottom: 0,
                textStyle: { fontSize: 11, color: "#64748b" },
            },
            grid: {
                left: "2%",
                right: "2%",
                bottom: "12%",
                top: "10%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: dates,
                axisLabel: { fontSize: 11, color: "#94a3b8" },
                axisLine: { lineStyle: { color: "#cbd5e1" } },
            },
            yAxis: {
                type: "value",
                axisLabel: { formatter: "{value} €", fontSize: 11, color: "#94a3b8" },
                splitLine: { lineStyle: { color: "#f1f5f9", type: "dashed" } },
            },
            series: [
                {
                    name: t("submeters.electricity_cost", "Stromkosten (€)"),
                    type: "bar",
                    itemStyle: { color: "#f59e0b" },
                    data: currentTimeseries.map((pt) => Number(pt.cost_eur || 0)),
                },
                {
                    name: t("submeters.solar_savings", "Solar-Ersparnis (€)"),
                    type: "bar",
                    itemStyle: { color: "#10b981" },
                    data: currentTimeseries.map((pt) => Number(pt.savings_eur || 0)),
                },
            ],
        };
    }, [data, chartMode, meter, t]);

    if (!isOpen || !meter) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs transition-opacity animate-fade-in">
            <div className="bg-white border border-gray-200 rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex items-center justify-between gap-4 sticky top-0 bg-white/95 backdrop-blur-xs z-10">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl p-2.5 bg-slate-100 rounded-2xl shrink-0 shadow-2xs">
                            {meterMeta.icon || "🔌"}
                        </span>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-xl font-black text-gray-900 tracking-tight">
                                    {meterMeta.name}
                                </h2>
                                <span
                                    className="px-2.5 py-0.5 rounded-full text-xs font-bold text-white shadow-2xs"
                                    style={{ backgroundColor: meterMeta.color || "#6366f1" }}
                                >
                                    {meterMeta.share_pct || meter.share_pct || 0}% {t("submeters.share", "Anteil")}
                                </span>
                            </div>
                            <p className="text-xs text-gray-400 mt-0.5">
                                {t("submeters.historical_subtitle", "Historische Zeitreihenanalyse & solare Deckungsquote im Zeitverlauf")}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={onClose}
                        className="w-9 h-9 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-gray-900 flex items-center justify-center transition cursor-pointer"
                        title={t("common.close", "Schließen")}
                    >
                        ✕
                    </button>
                </div>

                {/* Content Body */}
                <div className="p-6 space-y-6 flex-1">
                    {/* Period & Mode Filters */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        {/* Mode Toggle */}
                        <div className="inline-flex bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-2xs">
                            {chartModes.map((m) => (
                                <button
                                    key={m.key}
                                    onClick={() => setChartMode(m.key)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 ${chartMode === m.key
                                        ? "bg-white text-indigo-700 shadow-xs font-bold"
                                        : "text-gray-600 hover:text-gray-900"
                                        }`}
                                >
                                    <span>{m.icon}</span>
                                    <span>{m.label}</span>
                                </button>
                            ))}
                        </div>

                        {/* Period Tabs */}
                        <div className="inline-flex bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-2xs">
                            {periods.map((p) => (
                                <button
                                    key={p.key}
                                    onClick={() => setPeriod(p.key)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${period === p.key
                                        ? "bg-white text-indigo-700 shadow-xs font-bold"
                                        : "text-gray-600 hover:text-gray-900"
                                        }`}
                                >
                                    {p.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* KPI Cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
                        <div className="p-4 bg-indigo-50/70 border border-indigo-100 rounded-2xl">
                            <div className="text-[11px] font-bold uppercase tracking-wider text-indigo-700">
                                📊 {t("submeters.total_consumption", "Gesamtverbrauch")}
                            </div>
                            <div className="text-xl font-black text-gray-900 mt-1 font-mono">
                                {Number(meterMeta.total_kwh || meter.consumption_kwh || 0).toLocaleString(undefined, { maximumFractionDigits: 1 })}{" "}
                                <span className="text-xs font-normal text-gray-500">kWh</span>
                            </div>
                            <div className="text-[10px] text-indigo-600 mt-0.5">
                                {t("submeters.daily_avg", { val: meterMeta.avg_daily_kwh || 0, defaultValue: `⌀ ${meterMeta.avg_daily_kwh || 0} kWh / Tag` })}
                            </div>
                        </div>

                        <div className="p-4 bg-emerald-50/70 border border-emerald-100 rounded-2xl">
                            <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">
                                🛡️ {t("submeters.solar_coverage", "Solar-Deckungsgrad")}
                            </div>
                            <div className="text-xl font-black text-emerald-700 mt-1 font-mono">
                                {Number(meterMeta.solar_share_pct || meter.solar_share_pct || 0).toFixed(0)} %
                            </div>
                            <div className="text-[10px] text-emerald-600 mt-0.5">
                                {Number(meterMeta.solar_kwh || 0).toFixed(1)} kWh {t("submeters.by_solar", "durch Eigenstrom")}
                            </div>
                        </div>

                        <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl">
                            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-700">
                                📈 {t("submeters.peak_day", "Peak-Verbrauchstag")}
                            </div>
                            <div className="text-xl font-black text-gray-900 mt-1 font-mono">
                                {Number(meterMeta.peak_day_kwh || 0).toFixed(1)}{" "}
                                <span className="text-xs font-normal text-gray-500">kWh</span>
                            </div>
                            <div className="text-[10px] text-slate-500 mt-0.5 truncate">
                                {t("common.date", "Datum")}: {meterMeta.peak_day_date || "-"}
                            </div>
                        </div>

                        <div className="p-4 bg-amber-50/70 border border-amber-100 rounded-2xl">
                            <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700">
                                {t("submeters.costs_and_savings", "💶 Stromkosten & Ersparnis")}
                            </div>
                            <div className="text-xl font-black text-gray-900 mt-1 font-mono">
                                {Number(meterMeta.cost_eur || meter.cost_eur || 0).toFixed(2)} €
                            </div>
                            <div className="text-[10px] text-emerald-600 font-bold mt-0.5">
                                -{Number(meterMeta.savings_eur || meter.savings_eur || 0).toFixed(2)} € {t("submeters.solar_savings_short", "Solar-Ersparnis")}
                            </div>
                        </div>
                    </div>

                    {/* Main Trend Chart Container */}
                    <div className="bg-slate-50/80 border border-slate-200/80 rounded-2xl p-5 shadow-2xs space-y-3">
                        <div className="flex items-center justify-between text-xs">
                            <span className="font-bold text-gray-700">
                                {t("submeters.trend_label", "Zeitverlauf")} ({data?.period_label || period})
                            </span>
                            <span className="text-gray-400 font-medium">
                                {timeseries.length} {t("submeters.intervals", "Intervalle")}
                            </span>
                        </div>

                        {trendQuery.isLoading ? (
                            <div className="h-64 flex items-center justify-center text-gray-400 text-xs animate-pulse">
                                {t("common.loading", "Lade...")}
                            </div>
                        ) : timeseries.length === 0 || !chartOption ? (
                            <div className="h-64 flex items-center justify-center text-gray-400 text-xs">
                                {t("submeters.no_data", "Keine Messdaten für den gewählten Zeitraum vorhanden.")}
                            </div>
                        ) : (
                            <div className="h-72 w-full">
                                <ReactECharts
                                    option={chartOption}
                                    style={{ height: "100%", width: "100%" }}
                                    notMerge={true}
                                    lazyUpdate={true}
                                />
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between text-xs">
                    <span className="text-gray-400">
                        {t("submeters.data_basis", "Datenbasis: Aggregierte Stundenmessungen & stichtagsgenaue Tarife")}
                    </span>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-xs transition cursor-pointer"
                    >
                        {t("common.finish", "Fertig")}
                    </button>
                </div>
            </div>
        </div>
    );
}


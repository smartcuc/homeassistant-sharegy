/*
# src/features/forecast/components/HouseholdLoadForecastCard.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function HouseholdLoadForecastCard() {
    const { t } = useTranslation();
    const [horizon, setHorizon] = useState(24);

    const query = useQuery({
        queryKey: ["household-load-forecast", horizon],
        queryFn: () => apiFetch(`/api/forecast/load/?horizon=${horizon}`),
        refetchInterval: 60000,
    });

    const data = query.data || {};
    const kpis = data.kpis || {};
    const timeline = data.timeline || [];

    if (query.isLoading) {
        return (
            <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-xs animate-pulse space-y-4">
                <div className="h-6 w-48 bg-slate-200 rounded-md" />
                <div className="h-40 bg-slate-100 rounded-2xl" />
            </div>
        );
    }

    const maxChartKw = Math.max(
        ...timeline.map((pt) => Math.max(pt.total_load_kw || 0, pt.pv_forecast_kw || 0)),
        2.5
    );

    return (
        <div className="bg-white border border-gray-200/80 rounded-3xl p-6 shadow-sm space-y-6">
            {/* =========================================================
                HEADER & HORIZON TOGGLE
            ========================================================= */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-5">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">📈</span>
                        <h2 className="text-xl font-black text-gray-900 tracking-tight flex items-center gap-2">
                            {t("forecast.load_title", "Haushalts- & Verbrauchs-Prognose")}
                        </h2>
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                            {t("load_forecast.weather_load_badge", "Wetter & Lastprofil")}
                        </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                        {t("forecast.load_subtitle", "Vorausschauende 24h/48h Simulation von Grundlast, Wärmepumpen-Bedarf und Netto-Solarüberschuss.")}
                    </p>
                </div>

                {/* Horizon Switcher */}
                <div className="inline-flex bg-gray-100 p-1 rounded-2xl self-start sm:self-auto gap-1">
                    {[
                        { val: 24, label: t("load_forecast.horizon_24h", "24 Stunden") },
                        { val: 48, label: t("load_forecast.horizon_48h", "48 Stunden") },
                    ].map((btn) => (
                        <button
                            key={btn.val}
                            onClick={() => setHorizon(btn.val)}
                            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${horizon === btn.val
                                ? "bg-white text-gray-900 shadow-xs"
                                : "text-gray-500 hover:text-gray-900"
                                }`}
                        >
                            {btn.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* =========================================================
                KPI HIGHLIGHTS
            ========================================================= */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
                {/* 1. Gesamtverbrauch */}
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/70 space-y-1">
                    <div className="text-[11px] font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1">
                        <span>🏠</span> {t("load_forecast.forecast_load", "Prognose-Bedarf")}
                    </div>
                    <div className="text-2xl font-black text-slate-800 font-mono">
                        {Number(kpis.total_load_kwh || 0).toFixed(1)}{" "}
                        <span className="text-xs font-semibold text-gray-400">kWh</span>
                    </div>
                    <div className="text-[10px] text-gray-500">
                        {t("load_forecast.peak_load", "Spitzenlast")}: {kpis.peak_load_kw} kW ({kpis.peak_load_time})
                    </div>
                </div>

                {/* 2. PV-Ertrag */}
                <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200/70 space-y-1">
                    <div className="text-[11px] font-bold text-amber-700 uppercase tracking-wider flex items-center gap-1">
                        <span>☀️</span> {t("energy.pv_short", "Solar-Erzeugung")}
                    </div>
                    <div className="text-2xl font-black text-amber-700 font-mono">
                        {Number(kpis.total_pv_kwh || 0).toFixed(1)}{" "}
                        <span className="text-xs font-semibold text-amber-600/70">kWh</span>
                    </div>
                    <div className="text-[10px] text-amber-800/80">
                        {t("load_forecast.peak_pv", "Spitzenerzeugung")}: {kpis.peak_pv_kw} kW ({kpis.peak_pv_time})
                    </div>
                </div>

                {/* 3. Netto-Solarüberschuss */}
                <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200/80 space-y-1">
                    <div className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1">
                        <span>🟢</span> {t("load_forecast.net_surplus", "Netto-Überschuss")}
                    </div>
                    <div className="text-2xl font-black text-emerald-700 font-mono">
                        {Number(kpis.total_surplus_kwh || 0).toFixed(1)}{" "}
                        <span className="text-xs font-semibold text-emerald-600/70">kWh</span>
                    </div>
                    <div className="text-[10px] text-emerald-800/80">
                        {t("load_forecast.free_for_ev", "Frei für Wallbox / Batterie")}
                    </div>
                </div>

                {/* 4. Erwartete Autarkie */}
                <div className="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200/80 space-y-1">
                    <div className="text-[11px] font-bold text-indigo-800 uppercase tracking-wider flex items-center gap-1">
                        <span>🏆</span> {t("load_forecast.expected_autarky", "Erwartete Autarkie")}
                    </div>
                    <div className="text-2xl font-black text-indigo-700 font-mono">
                        {Number(kpis.autarky_pct || 0).toFixed(0)} %
                    </div>
                    <div className="text-[10px] text-indigo-800/80">
                        {t("load_forecast.grid_import_kwh", { val: Number(kpis.total_grid_import_kwh || 0).toFixed(1), defaultValue: `Netzbezug: ${Number(kpis.total_grid_import_kwh || 0).toFixed(1)} kWh` })}
                    </div>
                </div>
            </div>

            {/* =========================================================
                DUAL-TIMELINE CHART: PV VS LOAD
            ========================================================= */}
            <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs">
                    <div className="font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
                        <span>📊</span> {t("load_forecast.hourly_comparison", { val: horizon, defaultValue: `Stunden-Gegenüberstellung (${horizon}h Horizont)` })}
                    </div>
                    <div className="flex items-center gap-4 text-[11px] font-medium">
                        <span className="flex items-center gap-1.5 text-amber-600">
                            <span className="w-2.5 h-2.5 rounded-xs bg-amber-400 inline-block" /> {t("energy.pv_short", "PV-Ertrag")}
                        </span>
                        <span className="flex items-center gap-1.5 text-blue-600">
                            <span className="w-2.5 h-2.5 rounded-xs bg-blue-500 inline-block" /> {t("energy.load_short", "Hausverbrauch")}
                        </span>
                        <span className="flex items-center gap-1.5 text-emerald-600">
                            <span className="w-2.5 h-2.5 rounded-xs bg-emerald-500 inline-block" /> {t("load_forecast.net_surplus", "Netto-Überschuss")}
                        </span>
                    </div>
                </div>

                {/* Chart Bars */}
                {timeline.length === 0 ? (
                    <div className="bg-slate-50/70 border border-dashed border-slate-200 rounded-3xl p-8 text-center space-y-2">
                        <span className="text-3xl">🏠</span>
                        <div className="font-bold text-gray-800 text-sm">
                            {t("load_forecast.no_devices", "Keine Messgeräte oder Lastprofile vorhanden")}
                        </div>
                        <p className="text-xs text-gray-500 max-w-md mx-auto">
                            {t("load_forecast.no_devices_desc", "Sobald Smart Meter, Wechselrichter oder Verbraucher unter 'Geräte' verknüpft sind, wird hier die 24h/48h Lastprognose berechnet.")}
                        </p>
                    </div>
                ) : (
                    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 pt-8 text-white">
                        <div className="h-44 flex items-end justify-between gap-1 border-b border-slate-700/60 pb-2 overflow-x-auto">
                            {timeline.map((pt, idx) => {
                                const pvHeight = Math.min(100, (pt.pv_forecast_kw / maxChartKw) * 100);
                                const loadHeight = Math.min(100, (pt.total_load_kw / maxChartKw) * 100);
                                const hasSurplus = pt.has_surplus;

                                return (
                                    <div
                                        key={idx}
                                        className="flex-1 min-w-[20px] max-w-[40px] flex flex-col items-center gap-1 h-full justify-end group relative transition"
                                    >
                                        {/* Surplus Indicator Dot */}
                                        {hasSurplus && (
                                            <div className="absolute -top-4 w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-xs shadow-emerald-400/80" />
                                        )}

                                        {/* Dual Side-by-Side Mini Bars */}
                                        <div className="w-full flex items-end justify-center gap-0.5 h-full">
                                            {/* Load Bar */}
                                            <div
                                                className="w-1/2 bg-blue-500/80 group-hover:bg-blue-400 rounded-t-xs transition-all duration-200"
                                                style={{ height: `${Math.max(6, loadHeight)}%` }}
                                                title={`Last: ${pt.total_load_kw} kW (${pt.temperature_c}°C)`}
                                            />
                                            {/* PV Bar */}
                                            <div
                                                className="w-1/2 bg-amber-400/90 group-hover:bg-amber-300 rounded-t-xs transition-all duration-200"
                                                style={{ height: `${Math.max(2, pvHeight)}%` }}
                                                title={`Solar: ${pt.pv_forecast_kw} kW`}
                                            />
                                        </div>

                                        {/* Hour Label */}
                                        <span className="text-[9px] font-mono text-slate-400 truncate w-full text-center mt-1">
                                            {pt.hour % 3 === 0 ? pt.time_label : "·"}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>

                        <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 font-medium">
                            <span>{timeline[0]?.date_label} ({timeline[0]?.time_label})</span>
                            <span className="text-emerald-300 font-semibold">
                                {t("load_forecast.pure_surplus_badge", { val: kpis.total_surplus_kwh, h: horizon, defaultValue: `☀️ ${kpis.total_surplus_kwh} kWh Reiner Solarüberschuss im ${horizon}h-Fenster` })}
                            </span>
                            <span>{timeline[timeline.length - 1]?.date_label}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* =========================================================
                INTELLIGENT SUMMARY CALLOUT
            ========================================================= */}
            <div className="p-4 bg-linear-to-r from-emerald-50 to-teal-50 border border-emerald-200/70 rounded-2xl flex items-center gap-3 text-xs text-emerald-950">
                <span className="text-2xl p-2 bg-emerald-100 rounded-xl">💡</span>
                <div>
                    <span className="font-bold text-emerald-900">{t("load_forecast.insight_title", "Prognose-Erkenntnis:")} </span>
                    {kpis.total_surplus_kwh > 5.0 ? (
                        <span>
                            {t("load_forecast.surplus_rec", { h: horizon, surplus: kpis.total_surplus_kwh, defaultValue: `In den nächsten ${horizon} Stunden werden ${kpis.total_surplus_kwh} kWh ungenutzter Solarüberschuss erwartet. Empfehlung: Ladefahrpläne für Wallbox oder Wärmepumpen-Pufferspeicher aktivieren.` })}
                        </span>
                    ) : (
                        <span>
                            {t("load_forecast.low_surplus_rec", { surplus: kpis.total_surplus_kwh, load: kpis.total_load_kwh, defaultValue: `Geringer Solarüberschuss erwartet (${kpis.total_surplus_kwh} kWh). Der Grundbedarf von ${kpis.total_load_kwh} kWh wird teilweise aus dem Netz bezogen.` })}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}


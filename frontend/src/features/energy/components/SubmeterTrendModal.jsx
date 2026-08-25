/*
# src/features/energy/components/SubmeterTrendModal.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    Legend,
    AreaChart,
    Area,
} from "recharts";
import { apiFetch } from "../../../api/client";

export default function SubmeterTrendModal({ meter, isOpen, onClose, defaultPeriod = "30d" }) {
    const { t } = useTranslation();
    const [period, setPeriod] = useState(defaultPeriod);
    const [chartMode, setChartMode] = useState("coverage"); // 'coverage', 'consumption', 'costs'

    const trendQuery = useQuery({
        queryKey: ["submeter-trends", period, meter?.id],
        queryFn: () => apiFetch(`/api/energy/submeters/trends/?period=${period}&meter_id=${meter?.id}`),
        enabled: Boolean(isOpen && meter?.id),
    });

    if (!isOpen || !meter) return null;

    const data = trendQuery.data || {};
    const meterMeta = data.selected_meter || meter;
    const timeseries = data.selected_timeseries || [];

    const periods = [
        { key: "today", label: t("energy.period_today", "Heute") },
        { key: "7d", label: t("energy.period_7d", "Letzte 7 Tage") },
        { key: "30d", label: t("energy.period_30d", "Letzte 30 Tage") },
        { key: "year", label: t("energy.period_year", "Dieses Jahr") },
    ];

    const chartModes = [
        { key: "coverage", label: "🟢 Solare Deckung vs. Netz", icon: "☀️" },
        { key: "consumption", label: "⚡ Gesamtverbrauch", icon: "📊" },
        { key: "costs", label: "💶 Kosten & Ersparnis", icon: "💰" },
    ];

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
                                    {meterMeta.share_pct || meter.share_pct || 0}% Anteil
                                </span>
                            </div>
                            <p className="text-xs text-gray-400 mt-0.5">
                                Historische Zeitreihenanalyse & solare Deckungsquote im Zeitverlauf
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={onClose}
                        className="w-9 h-9 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-gray-900 flex items-center justify-center transition cursor-pointer"
                        title="Schließen"
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
                                📊 Gesamtverbrauch
                            </div>
                            <div className="text-xl font-black text-gray-900 mt-1 font-mono">
                                {Number(meterMeta.total_kwh || meter.consumption_kwh || 0).toLocaleString("de-DE", { maximumFractionDigits: 1 })}{" "}
                                <span className="text-xs font-normal text-gray-500">kWh</span>
                            </div>
                            <div className="text-[10px] text-indigo-600 mt-0.5">
                                ⌀ {meterMeta.avg_daily_kwh || 0} kWh / Tag
                            </div>
                        </div>

                        <div className="p-4 bg-emerald-50/70 border border-emerald-100 rounded-2xl">
                            <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">
                                🛡️ Solar-Deckungsgrad
                            </div>
                            <div className="text-xl font-black text-emerald-700 mt-1 font-mono">
                                {Number(meterMeta.solar_share_pct || meter.solar_share_pct || 0).toFixed(0)} %
                            </div>
                            <div className="text-[10px] text-emerald-600 mt-0.5">
                                {Number(meterMeta.solar_kwh || 0).toFixed(1)} kWh durch Eigenstrom
                            </div>
                        </div>

                        <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl">
                            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-700">
                                📈 Peak-Verbrauchstag
                            </div>
                            <div className="text-xl font-black text-gray-900 mt-1 font-mono">
                                {Number(meterMeta.peak_day_kwh || 0).toFixed(1)}{" "}
                                <span className="text-xs font-normal text-gray-500">kWh</span>
                            </div>
                            <div className="text-[10px] text-slate-500 mt-0.5 truncate">
                                Datum: {meterMeta.peak_day_date || "-"}
                            </div>
                        </div>

                        <div className="p-4 bg-amber-50/70 border border-amber-100 rounded-2xl">
                            <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700">
                                💶 Stromkosten & Ersparnis
                            </div>
                            <div className="text-xl font-black text-gray-900 mt-1 font-mono">
                                {Number(meterMeta.cost_eur || meter.cost_eur || 0).toFixed(2)} €
                            </div>
                            <div className="text-[10px] text-emerald-600 font-bold mt-0.5">
                                -{Number(meterMeta.savings_eur || meter.savings_eur || 0).toFixed(2)} € Solar-Ersparnis
                            </div>
                        </div>
                    </div>

                    {/* Main Trend Chart Container */}
                    <div className="bg-slate-50/80 border border-slate-200/80 rounded-2xl p-5 shadow-2xs space-y-3">
                        <div className="flex items-center justify-between text-xs">
                            <span className="font-bold text-gray-700">
                                Zeitverlauf ({data.period_label || period})
                            </span>
                            <span className="text-gray-400 font-medium">
                                {timeseries.length} Intervalle
                            </span>
                        </div>

                        {trendQuery.isLoading ? (
                            <div className="h-64 flex items-center justify-center text-gray-400 text-xs animate-pulse">
                                Lade Zeitreihendaten...
                            </div>
                        ) : timeseries.length === 0 ? (
                            <div className="h-64 flex items-center justify-center text-gray-400 text-xs">
                                Keine Messdaten für den gewählten Zeitraum vorhanden.
                            </div>
                        ) : (
                            <div className="h-72 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    {chartMode === "coverage" ? (
                                        <BarChart data={timeseries} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                            <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                                            <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" unit=" kWh" />
                                            <Tooltip
                                                formatter={(value, name) => [
                                                    `${Number(value).toFixed(2)} kWh`,
                                                    name === "solar_kwh" ? "🟢 Solarstrom" : "🔵 Netzstrom",
                                                ]}
                                                contentStyle={{
                                                    borderRadius: "1rem",
                                                    border: "1px solid #e2e8f0",
                                                    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                                                    fontSize: "12px",
                                                }}
                                            />
                                            <Legend
                                                formatter={(val) => (val === "solar_kwh" ? "Solar-Eigenstrom" : "Netzbezug")}
                                                wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
                                            />
                                            <Bar dataKey="solar_kwh" name="solar_kwh" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} />
                                            <Bar dataKey="grid_kwh" name="grid_kwh" stackId="a" fill="#64748b" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    ) : chartMode === "consumption" ? (
                                        <AreaChart data={timeseries} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                            <defs>
                                                <linearGradient id="colorCons" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor={meterMeta.color || "#6366f1"} stopOpacity={0.4} />
                                                    <stop offset="95%" stopColor={meterMeta.color || "#6366f1"} stopOpacity={0.0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                            <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                                            <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" unit=" kWh" />
                                            <Tooltip
                                                formatter={(value) => [`${Number(value).toFixed(2)} kWh`, "Verbrauch"]}
                                                contentStyle={{
                                                    borderRadius: "1rem",
                                                    border: "1px solid #e2e8f0",
                                                    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                                                    fontSize: "12px",
                                                }}
                                            />
                                            <Area
                                                type="monotone"
                                                dataKey="kwh"
                                                stroke={meterMeta.color || "#6366f1"}
                                                strokeWidth={2.5}
                                                fillOpacity={1}
                                                fill="url(#colorCons)"
                                            />
                                        </AreaChart>
                                    ) : (
                                        <BarChart data={timeseries} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                            <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                                            <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" unit=" €" />
                                            <Tooltip
                                                formatter={(value, name) => [
                                                    `${Number(value).toFixed(2)} €`,
                                                    name === "cost_eur" ? "Kosten (Netz)" : "🟢 Vermiedene Kosten (Solar)",
                                                ]}
                                                contentStyle={{
                                                    borderRadius: "1rem",
                                                    border: "1px solid #e2e8f0",
                                                    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                                                    fontSize: "12px",
                                                }}
                                            />
                                            <Legend
                                                formatter={(val) => (val === "cost_eur" ? "Stromkosten (€)" : "Solar-Ersparnis (€)")}
                                                wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
                                            />
                                            <Bar dataKey="cost_eur" name="cost_eur" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                                            <Bar dataKey="savings_eur" name="savings_eur" fill="#10b981" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    )}
                                </ResponsiveContainer>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between text-xs">
                    <span className="text-gray-400">
                        Datenbasis: Aggregierte Stundenmessungen & stichtagsgenaue Tarife
                    </span>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-xs transition cursor-pointer"
                    >
                        Fertig
                    </button>
                </div>
            </div>
        </div>
    );
}


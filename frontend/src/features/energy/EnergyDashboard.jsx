/*
# src/features/energy/EnergyDashboard.jsx
*/

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api/client";

export default function EnergyDashboard() {
    const { t } = useTranslation();
    const [period, setPeriod] = useState("today");

    // Fetch energy balance & submeters
    const balanceQuery = useQuery({
        queryKey: ["energy-balance", period],
        queryFn: () => apiFetch(`/api/energy/balance/?period=${period}`),
        refetchInterval: 10000,
    });

    const data = balanceQuery.data || {};
    const kpis = data.kpis || {};
    const submeters = data.submeters || [];
    const charts = data.charts || {};
    const breakdown = charts.breakdown || [];
    const timeseries = charts.timeseries || [];
    const insights = data.insights || [];

    const periods = [
        { key: "today", label: t("energy.period_today", "Heute") },
        { key: "7d", label: t("energy.period_7d", "Letzte 7 Tage") },
        { key: "30d", label: t("energy.period_30d", "Letzte 30 Tage") },
        { key: "year", label: t("energy.period_year", "Dieses Jahr") },
    ];

    // Pre-calculate SVG donut slices purely and immutably via reduce
    const donutSlices = useMemo(() => {
        const list = balanceQuery.data?.charts?.breakdown || [];
        const total = list.reduce((acc, item) => acc + item.value, 0) || 1;

        return list.reduce(
            (acc, item) => {
                const percentage = item.value / total;
                const strokeDasharray = `${percentage * 251.2} 251.2`;
                const strokeDashoffset = -acc.accumulated * 251.2;
                return {
                    accumulated: acc.accumulated + percentage,
                    items: [
                        ...acc.items,
                        {
                            ...item,
                            strokeDasharray,
                            strokeDashoffset,
                        },
                    ],
                };
            },
            { accumulated: 0, items: [] }
        ).items;
    }, [balanceQuery.data?.charts?.breakdown]);

    // Calculate max value for timeseries scaling
    const maxBarValue = Math.max(
        ...timeseries.map((pt) => Math.max(pt.pv || 0, pt.load || 0)),
        1
    );

    const [isSeeding, setIsSeeding] = useState(false);
    const [seedSuccessMsg, setSeedSuccessMsg] = useState("");

    const handleSeedDemo = async () => {
        try {
            setIsSeeding(true);
            const res = await apiFetch("/api/energy/seed-demo/", { method: "POST" });
            setSeedSuccessMsg(res.message || "Demodaten erfolgreich geladen!");
            balanceQuery.refetch();
            setTimeout(() => setSeedSuccessMsg(""), 4000);
        } catch (err) {
            console.error("Failed to seed demo data", err);
        } finally {
            setIsSeeding(false);
        }
    };

    return (
        <div className="p-6 space-y-6 max-w-7xl">
            {/* =========================================================
                HEADER & TIMEFRAME SELECTOR
            ========================================================= */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <span>⚡</span> {t("energy.title", "Energiebilanz & Analyse")}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        {t("energy.subtitle", "Detaillierte Mengen-, Verbrauchs- und Kostenanalyse nach Zeiträumen.")}
                    </p>
                </div>

                <div className="flex items-center gap-2.5 self-start sm:self-auto">
                    {/* Demo Seed Action */}
                    <button
                        onClick={handleSeedDemo}
                        disabled={isSeeding}
                        className="px-3.5 py-1.5 rounded-xl border border-dashed border-indigo-300 bg-indigo-50/70 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer disabled:opacity-50"
                        title="Vollständige 30-Tage Demodaten und virtuelle Zähler für dieses Konto generieren"
                    >
                        <span>🎲</span>
                        <span>{isSeeding ? "Generiere..." : "Demodaten laden"}</span>
                    </button>

                    {/* Period Selector Tabs */}
                    <div className="inline-flex bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-2xs">
                        {periods.map((p) => (
                            <button
                                key={p.key}
                                onClick={() => setPeriod(p.key)}
                                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${period === p.key
                                    ? "bg-white text-indigo-600 shadow-xs"
                                    : "text-gray-600 hover:text-gray-900"
                                    }`}
                            >
                                {p.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Seed Success Toast */}
            {seedSuccessMsg && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-xl flex items-center gap-2 shadow-xs">
                    <span>✅</span>
                    <span>{seedSuccessMsg}</span>
                </div>
            )}

            {/* =========================================================
                KPI HIGHLIGHTS
            ========================================================= */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
                {/* PV Generation */}
                <div className="p-4 bg-amber-50/70 border border-amber-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700">
                        ☀️ {t("energy.solar_production", "Erzeugung")}
                    </div>
                    <div className="text-2xl font-extrabold text-gray-900 mt-1.5">
                        {Number(kpis.pv_generation_kwh || 0).toLocaleString("de-DE", { maximumFractionDigits: 1 })}{" "}
                        <span className="text-xs font-semibold text-gray-500">kWh</span>
                    </div>
                    <div className="text-[11px] text-amber-800/80 mt-1 font-medium">
                        Direkt: {Number(kpis.direct_consumption_kwh || 0).toFixed(1)} kWh
                    </div>
                </div>

                {/* House Consumption */}
                <div className="p-4 bg-blue-50/70 border border-blue-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-blue-700">
                        🏠 {t("energy.household_load", "Verbrauch")}
                    </div>
                    <div className="text-2xl font-extrabold text-gray-900 mt-1.5">
                        {Number(kpis.house_consumption_kwh || 0).toLocaleString("de-DE", { maximumFractionDigits: 1 })}{" "}
                        <span className="text-xs font-semibold text-gray-500">kWh</span>
                    </div>
                    <div className="text-[11px] text-blue-800/80 mt-1 font-medium">
                        Netzbezug: {Number(kpis.grid_import_kwh || 0).toFixed(1)} kWh
                    </div>
                </div>

                {/* Autarky Rate */}
                <div className="p-4 bg-emerald-50/70 border border-emerald-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">
                        🛡️ {t("energy.autarky", "Autarkiegrad")}
                    </div>
                    <div className="text-2xl font-extrabold text-emerald-700 mt-1.5">
                        {Number(kpis.autarky_rate || 0).toFixed(0)} %
                    </div>
                    <div className="text-[11px] text-emerald-800/80 mt-1 font-medium">
                        Netzunabhängig
                    </div>
                </div>

                {/* Self Consumption Rate */}
                <div className="p-4 bg-purple-50/70 border border-purple-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-purple-700">
                        🔄 {t("energy.self_consumption", "Eigenverbrauch")}
                    </div>
                    <div className="text-2xl font-extrabold text-purple-700 mt-1.5">
                        {Number(kpis.self_consumption_rate || 0).toFixed(0)} %
                    </div>
                    <div className="text-[11px] text-purple-800/80 mt-1 font-medium">
                        PV-Nutzungsgrad
                    </div>
                </div>

                {/* Financial Benefit */}
                <div className="p-4 bg-indigo-50/70 border border-indigo-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-indigo-700">
                        💶 {t("energy.net_benefit", "Finanzvorteil")}
                    </div>
                    <div className="text-2xl font-extrabold text-indigo-900 mt-1.5">
                        {Number(kpis.net_benefit_eur || 0) >= 0 ? "+" : ""}
                        {Number(kpis.net_benefit_eur || 0).toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €
                    </div>
                    <div className="text-[11px] text-indigo-800/80 mt-1 font-medium truncate" title={kpis.tariff_label}>
                        Ersparnis: {Number(kpis.savings_eur || 0).toFixed(2)} € · <span className="font-semibold">{kpis.tariff_label || "Standard"}</span>
                    </div>
                </div>

                {/* CO2 Saved */}
                <div className="p-4 bg-teal-50/70 border border-teal-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-teal-700">
                        🌿 {t("energy.co2_saved", "CO₂ vermieden")}
                    </div>
                    <div className="text-2xl font-extrabold text-teal-900 mt-1.5">
                        {Number(kpis.co2_saved_kg || 0).toLocaleString("de-DE", { maximumFractionDigits: 1 })}{" "}
                        <span className="text-xs font-semibold text-gray-500">kg</span>
                    </div>
                    <div className="text-[11px] text-teal-800/80 mt-1 font-medium">
                        Ökobilanz
                    </div>
                </div>
            </div>

            {/* =========================================================
                ANALYTICS & IMPACT BENCHMARKS
            ========================================================= */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 bg-slate-50/80 border border-slate-200/80 rounded-2xl p-3.5 shadow-2xs">
                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">⚡</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">PV Spitzenleistung</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.peak_pv_kw || 0} kW</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">📈</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">Max. Lastspitze</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.peak_load_kw || 0} kW</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">☀️</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">Ø Erzeugung / Tag</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.daily_avg_generation_kwh || 0} kWh</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">🏠</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">Ø Bedarf / Tag</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.daily_avg_consumption_kwh || 0} kWh</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">🚗</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">Solar-Fahrleistung</div>
                        <div className="text-sm font-black text-emerald-700 font-mono">+{kpis.ev_km_equivalent || 0} km</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">🌳</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">Baum-Kompensation</div>
                        <div className="text-sm font-black text-teal-700 font-mono">{kpis.trees_equivalent || 0} Bäume</div>
                    </div>
                </div>
            </div>

            {/* =========================================================
                INSIGHTS NOTIFICATION
            ========================================================= */}
            {insights.length > 0 && (
                <div className="p-4 bg-linear-to-r from-indigo-50/80 to-purple-50/80 border border-indigo-100 rounded-2xl text-xs text-indigo-950 space-y-1.5 shadow-2xs">
                    {insights.map((text, i) => (
                        <div key={i} className="flex items-center gap-2">
                            <span className="text-indigo-600 text-sm">💡</span>
                            <span className="font-medium">{text}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* =========================================================
                VIRTUELLE ZÄHLER & SUB-METERING
            ========================================================= */}
            <div className="space-y-3">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                            <span>🧮</span> {t("energy.submeters_title", "Virtuelle Zähler & Sub-Metering")}
                        </h2>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("energy.submeters_subtitle", "Aufschlüsselung des gesamten Hausverbrauchs nach Verbrauchern und solarem Deckungsgrad.")}
                        </p>
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-lg">
                        {submeters.length} {submeters.length === 1 ? "Verbraucher" : "Verbraucher"}
                    </span>
                </div>

                {/* Submeters Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {submeters.map((meter) => (
                        <div
                            key={meter.id}
                            className={`p-5 rounded-2xl border transition shadow-2xs ${meter.is_residual
                                ? "bg-slate-50/70 border-dashed border-slate-300"
                                : "bg-white border-gray-200 hover:shadow-xs"
                                }`}
                        >
                            {/* Meter Header */}
                            <div className="flex items-center justify-between gap-2">
                                <div className="flex items-center gap-2.5 min-w-0">
                                    <span className="text-2xl shrink-0 p-2 bg-slate-100 rounded-xl">{meter.icon}</span>
                                    <div className="min-w-0">
                                        <div className="font-bold text-sm text-gray-900 truncate">{meter.name}</div>
                                        <div className="text-[11px] text-gray-400 capitalize">{meter.category}</div>
                                    </div>
                                </div>
                                <span
                                    className="px-2.5 py-1 rounded-full text-xs font-bold text-white shrink-0"
                                    style={{ backgroundColor: meter.color }}
                                >
                                    {meter.share_pct} %
                                </span>
                            </div>

                            {/* Consumption & Costs */}
                            <div className="mt-4 flex items-baseline justify-between border-b pb-3">
                                <div>
                                    <div className="text-2xl font-black text-gray-900 font-mono">
                                        {Number(meter.consumption_kwh).toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}{" "}
                                        <span className="text-xs font-normal text-gray-500">kWh</span>
                                    </div>
                                    <div className="text-[11px] text-gray-400">Verbrauch im Zeitraum</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm font-bold text-gray-800 font-mono">
                                        {Number(meter.cost_eur || 0).toFixed(2)} €
                                    </div>
                                    <div className="text-[11px] text-emerald-600 font-medium">
                                        -{Number(meter.savings_eur || 0).toFixed(2)} € Solar
                                    </div>
                                </div>
                            </div>

                            {/* Solar vs. Grid Coverage Bar */}
                            <div className="mt-3 space-y-1.5">
                                <div className="flex justify-between text-[11px] font-medium">
                                    <span className="text-emerald-700 flex items-center gap-1">
                                        <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                                        {t("energy.solar_share", "Solarstrom")}: {meter.solar_share_pct.toFixed(0)}%
                                    </span>
                                    <span className="text-slate-500 flex items-center gap-1">
                                        <span className="w-2 h-2 rounded-full bg-slate-400 inline-block" />
                                        {t("energy.grid_share", "Netzstrom")}: {(100 - meter.solar_share_pct).toFixed(0)}%
                                    </span>
                                </div>

                                <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden flex">
                                    <div
                                        className="bg-emerald-500 h-full transition-all duration-500"
                                        style={{ width: `${meter.solar_share_pct}%` }}
                                        title={`Solarstrom: ${meter.solar_share_pct}%`}
                                    />
                                    <div
                                        className="bg-slate-400 h-full transition-all duration-500"
                                        style={{ width: `${100 - meter.solar_share_pct}%` }}
                                        title={`Netzstrom: ${100 - meter.solar_share_pct}%`}
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* =========================================================
                CHARTS SECTION: BREAKDOWN (DONUT) & GENERATION VS LOAD
            ========================================================= */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 1. Verbrauchsaufteilung (Donut + Legend) */}
                <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs space-y-4">
                    <h3 className="font-bold text-base text-gray-900 flex items-center gap-2">
                        <span>📊</span> {t("energy.breakdown_title", "Verbrauchsaufteilung")}
                    </h3>

                    <div className="flex flex-col sm:flex-row items-center gap-6">
                        {/* Custom SVG Donut */}
                        <div className="relative w-44 h-44 shrink-0 flex items-center justify-center">
                            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                                {donutSlices.map((item, idx) => (
                                    <circle
                                        key={idx}
                                        cx="50"
                                        cy="50"
                                        r="40"
                                        fill="transparent"
                                        stroke={item.color}
                                        strokeWidth="16"
                                        strokeDasharray={item.strokeDasharray}
                                        strokeDashoffset={item.strokeDashoffset}
                                        className="transition-all duration-500 hover:opacity-80"
                                    />
                                ))}
                            </svg>
                            <div className="absolute text-center">
                                <div className="text-xs text-gray-400 font-semibold uppercase">Gesamt</div>
                                <div className="text-base font-black text-gray-900 font-mono">
                                    {Number(kpis.house_consumption_kwh || 0).toFixed(1)}
                                </div>
                                <div className="text-[10px] text-gray-500">kWh</div>
                            </div>
                        </div>

                        {/* Legend */}
                        <div className="flex-1 w-full space-y-2">
                            {breakdown.map((item, idx) => {
                                const total = breakdown.reduce((acc, b) => acc + b.value, 0) || 1;
                                const pct = ((item.value / total) * 100).toFixed(1);

                                return (
                                    <div key={idx} className="flex items-center justify-between text-xs">
                                        <div className="flex items-center gap-2 truncate">
                                            <span className="w-3 h-3 rounded-md shrink-0" style={{ backgroundColor: item.color }} />
                                            <span className="font-medium text-gray-700 truncate">{item.name}</span>
                                        </div>
                                        <div className="font-mono font-bold text-gray-900 shrink-0 ml-2">
                                            {Number(item.value).toFixed(1)} kWh <span className="text-gray-400 font-normal">({pct}%)</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* 2. Energetische Mengenbilanz (In & Out Flussmatrix) */}
                <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs space-y-4">
                    <h3 className="font-bold text-base text-gray-900 flex items-center gap-2">
                        <span>🔄</span> {t("energy.energy_balance", "Mengenbilanz (kWh)")}
                    </h3>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                        {/* Erzeugung Matrix */}
                        <div className="p-3.5 bg-amber-50/60 border border-amber-100 rounded-xl space-y-2">
                            <div className="font-bold text-amber-900 border-b border-amber-200/60 pb-1">
                                ☀️ PV-Erzeugung ({Number(kpis.pv_generation_kwh || 0).toFixed(1)} kWh)
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🏠 Direktverbrauch:</span>
                                <span className="font-mono font-bold">{Number(kpis.direct_consumption_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔋 In Batterie:</span>
                                <span className="font-mono font-bold">{Number(kpis.battery_charge_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔌 Netzeinspeisung:</span>
                                <span className="font-mono font-bold">{Number(kpis.grid_export_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                        </div>

                        {/* Verbrauch Matrix */}
                        <div className="p-3.5 bg-blue-50/60 border border-blue-100 rounded-xl space-y-2">
                            <div className="font-bold text-blue-900 border-b border-blue-200/60 pb-1">
                                🏠 Hausbedarf ({Number(kpis.house_consumption_kwh || 0).toFixed(1)} kWh)
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>☀️ Aus PV-Direkt:</span>
                                <span className="font-mono font-bold">{Number(kpis.direct_consumption_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔋 Aus Batterie:</span>
                                <span className="font-mono font-bold">{Number(kpis.battery_discharge_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔌 Aus Stromnetz:</span>
                                <span className="font-mono font-bold">{Number(kpis.grid_import_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                        </div>
                    </div>

                    {/* Monetary summary strip */}
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                        <span className="text-gray-600 font-medium">Kostenbilanz im Zeitraum:</span>
                        <div className="flex items-center gap-4 font-mono font-semibold">
                            <span className="text-emerald-700">+{Number(kpis.savings_eur || 0).toFixed(2)} € Ersparnis</span>
                            <span className="text-amber-700">+{Number(kpis.feed_in_revenue_eur || 0).toFixed(2)} € Einspeisung</span>
                            <span className="text-rose-700">-{Number(kpis.grid_costs_eur || 0).toFixed(2)} € Netzkosten</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* =========================================================
                TIMELINE BARS: ERZEUGUNG VS. VERBRAUCH
            ========================================================= */}
            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="font-bold text-base text-gray-900 flex items-center gap-2">
                        <span>📈</span> {t("energy.generation_vs_load", "Erzeugung vs. Verbrauch")} ({data.period_label || period})
                    </h3>
                    <div className="flex items-center gap-4 text-xs font-semibold">
                        <div className="flex items-center gap-1.5 text-amber-700">
                            <span className="w-3 h-3 rounded-xs bg-amber-400" /> ☀️ Erzeugung (kWh)
                        </div>
                        <div className="flex items-center gap-1.5 text-blue-700">
                            <span className="w-3 h-3 rounded-xs bg-blue-500" /> 🏠 Verbrauch (kWh)
                        </div>
                    </div>
                </div>

                {/* Visual Bar Columns */}
                <div className="pt-6 pb-2">
                    <div className="h-48 flex items-end justify-between gap-2 border-b border-gray-200 pb-2">
                        {timeseries.map((pt, idx) => {
                            const pvHeight = (pt.pv / maxBarValue) * 100;
                            const loadHeight = (pt.load / maxBarValue) * 100;

                            return (
                                <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                                    <div className="w-full flex items-end justify-center gap-1 h-full">
                                        {/* PV Bar */}
                                        <div
                                            className="w-1/2 max-w-[24px] bg-amber-400 rounded-t-sm transition-all duration-300 group-hover:bg-amber-500"
                                            style={{ height: `${Math.max(pvHeight, 2)}%` }}
                                            title={`Erzeugung: ${pt.pv} kWh`}
                                        />
                                        {/* Load Bar */}
                                        <div
                                            className="w-1/2 max-w-[24px] bg-blue-500 rounded-t-sm transition-all duration-300 group-hover:bg-blue-600"
                                            style={{ height: `${Math.max(loadHeight, 2)}%` }}
                                            title={`Verbrauch: ${pt.load} kWh`}
                                        />
                                    </div>
                                    <span className="text-[10px] text-gray-400 font-mono mt-1 whitespace-nowrap truncate w-full text-center">
                                        {pt.time}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}

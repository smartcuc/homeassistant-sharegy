/*
# src/features/energy/components/BatteryForecastCard.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function BatteryForecastCard() {
    const { t } = useTranslation();
    const [horizon, setHorizon] = useState(24);

    const query = useQuery({
        queryKey: ["battery-soc-forecast", horizon],
        queryFn: () => apiFetch(`/api/energy/battery-forecast/?horizon=${horizon}`),
        refetchInterval: 60000,
    });

    const data = query.data || {};
    const params = data.parameters || {};
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

    if (!data.has_battery) {
        return null;
    }

    return (
        <div className="bg-linear-to-br from-slate-900 via-slate-950 to-emerald-950/40 border border-emerald-900/50 rounded-3xl p-6 shadow-xl text-white space-y-6">
            {/* =========================================================
                HEADER & HORIZON TOGGLE
            ========================================================= */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-emerald-900/40 pb-5">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">🔋</span>
                        <h2 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
                            {t("energy.battery_forecast_title", "Batterie- & SoC-Prognose")}
                        </h2>
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            {(params.battery_name || "Hausspeicher").toLowerCase().includes("kwh")
                                ? (params.battery_name || "Hausspeicher")
                                : `${params.battery_name || "Hausspeicher"} · ${params.capacity_kwh} kWh`}
                        </span>
                    </div>
                    <p className="text-xs text-emerald-200/70 mt-1">
                        {t("energy.battery_forecast_subtitle", "Vorausschauende 24h/48h Simulation von Speicherladung, Entladung und Nachtautarkie.")}
                    </p>
                </div>

                {/* Horizon Switcher */}
                <div className="inline-flex bg-slate-800/90 p-1.5 rounded-2xl border border-emerald-700/40 shadow-inner self-start sm:self-auto gap-1">
                    {[
                        { val: 24, label: t("load_forecast.horizon_24h", "24 Stunden") },
                        { val: 48, label: t("load_forecast.horizon_48h", "48 Stunden") },
                    ].map((btn) => (
                        <button
                            key={btn.val}
                            onClick={() => setHorizon(btn.val)}
                            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${horizon === btn.val
                                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/40"
                                : "text-emerald-200/70 hover:text-white"
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
                {/* 1. Aktueller Ladestand */}
                <div className="p-4 rounded-2xl bg-emerald-950/50 border border-emerald-500/30 space-y-1">
                    <div className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center justify-between gap-1">
                        <span className="flex items-center gap-1">
                            <span>⚡</span> {t("battery_forecast.start_soc", "Start-Ladestand")}
                        </span>
                        {params.has_live_soc === false && (
                            <span className="text-[9px] px-1.5 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30 normal-case font-semibold">
                                {t("battery_forecast.estimated", "geschätzt")}
                            </span>
                        )}
                    </div>
                    <div className="text-2xl font-black text-white font-mono">
                        {kpis.start_soc_pct} <span className="text-xs font-semibold text-emerald-400/80">%</span>
                    </div>
                    <div className="text-[10px] text-emerald-200/70">
                        {params.has_live_soc === false ? (
                            <span className="text-amber-300/80">{t("battery_forecast.no_sensor_reserve", { reserve: params.min_soc_reserve_pct, defaultValue: `Kein Sensor · Notstromreserve (${params.min_soc_reserve_pct}%)` })}</span>
                        ) : (
                            `${((kpis.start_soc_pct / 100) * params.capacity_kwh).toFixed(1)} / ${params.capacity_kwh} kWh`
                        )}
                    </div>
                </div>

                {/* 2. Voll-Ladezeitpunkt */}
                <div className="p-4 rounded-2xl bg-indigo-950/50 border border-indigo-500/30 space-y-1">
                    <div className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-1">
                        <span>🏆</span> {t("battery_forecast.full_charge_100", "Voll geladen (100%)")}
                    </div>
                    <div className="text-lg font-black text-white truncate">
                        {kpis.full_charge_time}
                    </div>
                    <div className="text-[10px] text-indigo-200/70">
                        +{Number(kpis.total_charged_kwh || 0).toFixed(1)} kWh {t("battery_forecast.pv_charge", "PV-Ladung")}
                    </div>
                </div>

                {/* 3. Nacht-Autarkie */}
                <div className="p-4 rounded-2xl bg-teal-950/50 border border-teal-500/30 space-y-1">
                    <div className="text-[11px] font-bold text-teal-300 uppercase tracking-wider flex items-center gap-1">
                        <span>🌙</span> {t("battery_forecast.night_autarky", "Nacht-Autarkie")}
                    </div>
                    <div className="text-2xl font-black text-teal-300 font-mono">
                        {kpis.night_autarky_pct} %
                    </div>
                    <div className="text-[10px] text-teal-200/70 truncate">
                        {kpis.depleted_time}
                    </div>
                </div>

                {/* 4. Vermiedene Netzkosten */}
                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-700/50 space-y-1">
                    <div className="text-[11px] font-bold text-gray-300 uppercase tracking-wider flex items-center gap-1">
                        <span>💶</span> {t("battery_forecast.avoided_costs", "Vermiedene Netzkosten")}
                    </div>
                    <div className="text-2xl font-black text-emerald-400 font-mono">
                        +{Number(kpis.saved_grid_costs_eur || 0).toFixed(2)} €
                    </div>
                    <div className="text-[10px] text-gray-400">
                        {t("battery_forecast.discharge_amount", { kwh: Number(kpis.total_discharged_kwh || 0).toFixed(1), defaultValue: `durch ${Number(kpis.total_discharged_kwh || 0).toFixed(1)} kWh Entladung` })}
                    </div>
                </div>
            </div>

            {/* =========================================================
                INTERACTIVE SOC SIMULATION TIMELINE
            ========================================================= */}
            <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs">
                    <div className="font-bold uppercase tracking-wider text-emerald-200 flex items-center gap-2">
                        <span>📈</span> {t("battery_forecast.soc_curve", "48h SoC-Verlaufskurve (State of Charge)")}
                    </div>
                    <div className="flex items-center gap-4 text-[11px] font-medium">
                        <span className="flex items-center gap-1.5 text-emerald-400">
                            <span className="w-2.5 h-2.5 rounded-xs bg-emerald-400 inline-block" /> {t("battery_forecast.charging_high", "Laden (>60%)")}
                        </span>
                        <span className="flex items-center gap-1.5 text-amber-400">
                            <span className="w-2.5 h-2.5 rounded-xs bg-amber-400 inline-block" /> {t("battery_forecast.charging_mid", "Mittel (25-60%)")}
                        </span>
                        <span className="flex items-center gap-1.5 text-rose-400">
                            <span className="w-2.5 h-2.5 rounded-xs bg-rose-500 inline-block" /> {t("battery_forecast.charging_low", "Reserve (<25%)")}
                        </span>
                    </div>
                </div>

                {/* Timeline Visual Bars */}
                <div className="bg-slate-950/80 border border-emerald-900/60 rounded-3xl p-5 pt-8">
                    <div className="h-44 flex items-end justify-between gap-1 border-b border-slate-800 pb-2 overflow-x-auto">
                        {timeline.map((pt, idx) => {
                            const barHeight = Math.max(10, pt.soc_pct);

                            let barColor = "bg-amber-400 hover:bg-amber-300";
                            if (pt.soc_pct > 60) {
                                barColor = "bg-emerald-400 hover:bg-emerald-300";
                            } else if (pt.soc_pct < 25) {
                                barColor = "bg-rose-500 hover:bg-rose-400";
                            }

                            const isCharging = pt.bat_flow_kw > 0.1;
                            const isDischarging = pt.bat_flow_kw < -0.1;

                            return (
                                <div
                                    key={idx}
                                    className="flex-1 min-w-[20px] max-w-[36px] flex flex-col items-center gap-1 h-full justify-end group relative transition"
                                >
                                    {/* Flow Arrow Indicator */}
                                    {isCharging && (
                                        <div className="absolute -top-4 text-[9px] font-bold text-emerald-300">
                                            ⬆
                                        </div>
                                    )}
                                    {isDischarging && (
                                        <div className="absolute -top-4 text-[9px] font-bold text-blue-300">
                                            ⬇
                                        </div>
                                    )}

                                    {/* Bar Column */}
                                    <div
                                        className={`w-full rounded-t-xs transition-all duration-300 shadow-sm ${barColor} ${isCharging ? "ring-1 ring-emerald-300" : ""
                                            }`}
                                        style={{ height: `${barHeight}%` }}
                                        title={`${pt.date_label} ${pt.time_label}: SoC ${pt.soc_pct}% (${pt.stored_kwh} kWh) | Fluss: ${pt.bat_flow_kw > 0 ? `+${pt.bat_flow_kw}` : pt.bat_flow_kw} kW`}
                                    />

                                    {/* Hour Label */}
                                    <span className="text-[9px] font-mono text-slate-400 truncate w-full text-center mt-1">
                                        {pt.hour % 3 === 0 ? pt.time_label : "·"}
                                    </span>
                                </div>
                            );
                        })}
                    </div>

                    <div className="mt-3 flex items-center justify-between text-[11px] text-emerald-200/60 font-medium">
                        <span>{timeline[0]?.date_label} ({timeline[0]?.time_label})</span>
                        <span className="text-emerald-300 font-semibold">
                            {t("battery_forecast.reserve_floor", { pct: params.min_soc_reserve_pct, kwh: ((params.min_soc_reserve_pct / 100) * params.capacity_kwh).toFixed(1), defaultValue: `Notstromreserve-Boden: ${params.min_soc_reserve_pct}% (${((params.min_soc_reserve_pct / 100) * params.capacity_kwh).toFixed(1)} kWh)` })}
                        </span>
                        <span>{timeline[timeline.length - 1]?.date_label}</span>
                    </div>
                </div>
            </div>

            {/* =========================================================
                STORAGE SPECS FOOTER
            ========================================================= */}
            <div className="p-4 bg-emerald-950/40 border border-emerald-800/40 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs text-emerald-200/80">
                <div className="flex items-center gap-2">
                    <span className="text-lg">⚙️</span>
                    <span>{t("battery_forecast.specs_title", "Speicherparameter:")}</span>
                </div>
                <div className="flex flex-wrap gap-4 text-xs font-mono items-center">
                    <span>{t("battery_forecast.capacity_label", "Kapazität:")} <strong>{params.capacity_kwh} kWh</strong></span>
                    <span>{t("battery_forecast.max_charge_label", "Max. Ladeleistung:")} <strong>{params.max_charge_kw} kW</strong></span>
                    <span>{t("battery_forecast.efficiency_label", "Wirkungsgrad:")} <strong>{params.roundtrip_efficiency_pct}%</strong></span>
                    <span>{t("battery_forecast.reserve_label", "Notstromreserve:")} <strong>{params.min_soc_reserve_pct}%</strong></span>
                    <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${params.has_live_soc === false ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"}`}>
                        {params.has_live_soc === false ? t("battery_forecast.no_live_sensor", "⚠️ Kein Live-SoC Sensor") : t("battery_forecast.live_sensor_active", "✓ SoC Live-Sensor aktiv")}
                    </span>
                </div>
            </div>
        </div>
    );
}


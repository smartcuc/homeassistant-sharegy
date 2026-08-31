/*
# src/features/energy/components/BatteryForecastCard.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

export default function BatteryForecastCard() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [horizon, setHorizon] = useState(24);
    const [proModalOpen, setProModalOpen] = useState(false);

    const query = useQuery({
        queryKey: ["battery-soc-forecast", horizon],
        queryFn: () => apiFetch(`/api/energy/battery-forecast/?horizon=${horizon}`),
        refetchInterval: 60000,
    });

    const data = query.data || {};
    const params = data.parameters || {};
    const kpis = data.kpis || {};
    const timeline = data.timeline || [];

    const handleHorizonClick = (val) => {
        if (val === 48 && !isPro) {
            setProModalOpen(true);
            return;
        }
        setHorizon(val);
    };

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
                        { val: 48, label: t("load_forecast.horizon_48h", "48 Stunden"), isProGated: true },
                    ].map((btn) => (
                        <button
                            key={btn.val}
                            type="button"
                            onClick={() => handleHorizonClick(btn.val)}
                            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-1.5 ${
                                horizon === btn.val
                                    ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/40"
                                    : "text-emerald-200/70 hover:text-white"
                            }`}
                        >
                            <span>{btn.label}</span>
                            {btn.isProGated && !isPro && <ProBadge size="xs" />}
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
                        {kpis.start_stored_kwh} kWh im Speicher
                    </div>
                </div>

                {/* 2. Erwartete Ladung */}
                <div className="p-4 rounded-2xl bg-emerald-950/50 border border-emerald-500/30 space-y-1">
                    <div className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1">
                        <span>☀️</span> {t("battery_forecast.expected_charge", "Erwartete Ladung")}
                    </div>
                    <div className="text-2xl font-black text-white font-mono">
                        +{kpis.total_charged_kwh} <span className="text-xs font-semibold text-emerald-400/80">kWh</span>
                    </div>
                    <div className="text-[10px] text-emerald-200/70">
                        {kpis.full_charge_time ? `Voll um ${kpis.full_charge_time} Uhr` : "Erreicht keine 100%"}
                    </div>
                </div>

                {/* 3. Erwartete Entladung */}
                <div className="p-4 rounded-2xl bg-emerald-950/50 border border-emerald-500/30 space-y-1">
                    <div className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1">
                        <span>🏠</span> {t("battery_forecast.expected_discharge", "Erwartete Abgabe")}
                    </div>
                    <div className="text-2xl font-black text-white font-mono">
                        -{kpis.total_discharged_kwh} <span className="text-xs font-semibold text-emerald-400/80">kWh</span>
                    </div>
                    <div className="text-[10px] text-emerald-200/70">
                        Deckung für Haushaltslast
                    </div>
                </div>

                {/* 4. Nachtautarkie */}
                <div className="p-4 rounded-2xl bg-emerald-950/50 border border-emerald-500/30 space-y-1">
                    <div className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1">
                        <span>🌙</span> {t("battery_forecast.night_autarky", "Nacht-Autarkie")}
                    </div>
                    <div className="text-2xl font-black text-emerald-400 font-mono">
                        {kpis.night_autarky_pct} <span className="text-xs font-semibold text-emerald-300">%</span>
                    </div>
                    <div className="text-[10px] text-emerald-200/70">
                        {kpis.depleted_time ? `Reserve um ${kpis.depleted_time} Uhr erreicht` : "Reicht komplett über Nacht"}
                    </div>
                </div>
            </div>

            {/* =========================================================
                SIMULATION TIMELINE BAR CHART
            ========================================================= */}
            <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs text-emerald-200/80">
                    <span className="font-bold flex items-center gap-1.5">
                        <span>📈</span> {t("battery_forecast.timeline_title", "Simulierter SoC-Verlauf & Ladefluss")}
                    </span>
                    <div className="flex items-center gap-3 text-[11px]">
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" /> {t("battery_forecast.legend_soc", "SoC %")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" /> {t("battery_forecast.legend_charge", "Laden")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block" /> {t("battery_forecast.legend_discharge", "Entladen")}
                        </span>
                    </div>
                </div>

                {/* Timeline Grid */}
                <div className="bg-slate-950/70 border border-emerald-900/40 rounded-2xl p-4 overflow-x-auto">
                    <div className="min-w-[650px] flex items-end gap-1 h-36 pt-4 pb-1">
                        {timeline.map((slot, idx) => {
                            const socHeight = Math.max(4, Math.round((slot.sim_soc_pct / 100.0) * 100));
                            const isNight = slot.is_night;
                            const isCharging = slot.charge_kw > 0;
                            const isDischarging = slot.discharge_kw > 0;

                            return (
                                <div
                                    key={idx}
                                    className="flex-1 flex flex-col items-center justify-end h-full group relative"
                                >
                                    {/* Tooltip Hover */}
                                    <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col bg-slate-900 border border-emerald-500/50 rounded-xl p-2.5 shadow-2xl text-[11px] z-50 whitespace-nowrap pointer-events-none min-w-[140px]">
                                        <div className="font-bold text-white border-b border-slate-800 pb-1 mb-1">
                                            {slot.hour_label} Uhr {isNight ? "🌙" : "☀️"}
                                        </div>
                                        <div className="flex justify-between text-emerald-300">
                                            <span>SoC:</span>
                                            <span className="font-mono font-bold">{slot.sim_soc_pct}% ({slot.stored_kwh} kWh)</span>
                                        </div>
                                        <div className="flex justify-between text-amber-300">
                                            <span>Solar:</span>
                                            <span className="font-mono font-bold">+{slot.solar_kw} kW</span>
                                        </div>
                                        <div className="flex justify-between text-rose-300">
                                            <span>Haushalt:</span>
                                            <span className="font-mono font-bold">-{slot.load_kw} kW</span>
                                        </div>
                                        {isCharging && (
                                            <div className="flex justify-between text-emerald-400 font-bold pt-1 border-t border-slate-800/80">
                                                <span>Ladung:</span>
                                                <span className="font-mono">+{slot.charge_kw} kW</span>
                                            </div>
                                        )}
                                        {isDischarging && (
                                            <div className="flex justify-between text-cyan-400 font-bold pt-1 border-t border-slate-800/80">
                                                <span>Entladung:</span>
                                                <span className="font-mono">-{slot.discharge_kw} kW</span>
                                            </div>
                                        )}
                                    </div>

                                    {/* SoC Bar */}
                                    <div className="w-full flex items-end justify-center h-28 bg-slate-900/60 rounded-t-sm relative overflow-hidden">
                                        {/* Reserve Indicator Line */}
                                        <div
                                            className="absolute w-full border-t border-dashed border-amber-500/50 pointer-events-none"
                                            style={{ bottom: `${params.min_soc_reserve_pct}%` }}
                                            title={`Notstromreserve: ${params.min_soc_reserve_pct}%`}
                                        />

                                        <div
                                            className={`w-full rounded-t-sm transition-all duration-300 ${
                                                slot.sim_soc_pct <= (params.min_soc_reserve_pct + 1)
                                                    ? "bg-amber-500/80 border-t border-amber-300"
                                                    : isCharging
                                                    ? "bg-gradient-to-t from-emerald-600 via-emerald-500 to-amber-300 shadow-xs shadow-amber-400/20"
                                                    : isDischarging
                                                    ? "bg-gradient-to-t from-emerald-700 via-emerald-500 to-cyan-300 shadow-xs shadow-cyan-400/20"
                                                    : "bg-gradient-to-t from-emerald-600 to-emerald-400"
                                            }`}
                                            style={{ height: `${Math.max(6, socHeight)}%` }}
                                        />
                                    </div>

                                    {/* Hour & Date Label */}
                                    <div className="text-[9px] font-mono text-slate-400 mt-1.5 truncate text-center w-full">
                                        {idx % (horizon === 48 ? 4 : 2) === 0 ? slot.hour_label : "·"}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                    {/* Timeline footer dates */}
                    <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 font-medium px-1 border-t border-slate-800/60 pt-2">
                        <span>{timeline[0]?.date_label} ({timeline[0]?.time_label})</span>
                        <span className="text-emerald-300 font-semibold">
                            🔋 {params.battery_name || "Speicher"} · {kpis.night_autarky_pct || 0}% Nachtautarkie
                        </span>
                        <span>{timeline[timeline.length - 1]?.date_label} ({timeline[timeline.length - 1]?.time_label})</span>
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

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="48-Stunden Speicher- & SoC-Simulation"
                featureDesc="Simuliere den Ladezustand (SoC), Speicherentladungen und deine Nachtautarkie für volle 48 Stunden im Voraus mit Sharegy Pro."
            />
        </div>
    );
}

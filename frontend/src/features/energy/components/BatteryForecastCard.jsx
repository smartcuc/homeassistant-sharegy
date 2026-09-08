import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
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

    const chartOption = useMemo(() => {
        if (!timeline || timeline.length === 0) return {};

        const categories = timeline.map((slot) => {
            return `${slot.time_label}`;
        });

        const socValues = timeline.map((s) => Number(s.soc_pct ?? s.sim_soc_pct ?? 0));
        const solarValues = timeline.map((s) => Number(s.pv_kw ?? s.solar_kw ?? 0));
        const loadValues = timeline.map((s) => Number(s.load_kw ?? 0));
        const chargeValues = timeline.map((s) => {
            const ch = s.charge_kw ?? (s.bat_flow_kw > 0 ? s.bat_flow_kw : 0);
            return Number(ch) > 0 ? Number(ch) : 0;
        });
        const dischargeValues = timeline.map((s) => {
            const dis = s.discharge_kw ?? (s.bat_flow_kw < 0 ? Math.abs(s.bat_flow_kw) : 0);
            return Number(dis) > 0 ? Number(dis) : 0;
        });

        const translateDateLabel = (dl) => {
            if (dl === "Heute") return t("common.today", "Heute");
            if (dl === "Morgen") return t("common.tomorrow", "Morgen");
            return dl || "";
        };

        return {
            backgroundColor: "transparent",
            animation: true,
            tooltip: {
                trigger: "axis",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                borderColor: "rgba(16, 185, 129, 0.4)",
                borderWidth: 1,
                textStyle: { color: "#f8fafc", fontSize: 12 },
                padding: [10, 14],
                formatter: function (items) {
                    if (!items || items.length === 0) return "";
                    const idx = items[0].dataIndex;
                    const slot = timeline[idx];
                    if (!slot) return "";

                    const socVal = Number(slot.soc_pct ?? slot.sim_soc_pct ?? 0).toFixed(1);
                    const storedVal = Number(slot.stored_kwh ?? 0).toFixed(2);
                    const solarVal = Number(slot.pv_kw ?? slot.solar_kw ?? 0).toFixed(2);
                    const loadVal = Number(slot.load_kw ?? 0).toFixed(2);
                    const chargeVal = Number(slot.charge_kw ?? (slot.bat_flow_kw > 0 ? slot.bat_flow_kw : 0));
                    const dischargeVal = Number(slot.discharge_kw ?? (slot.bat_flow_kw < 0 ? Math.abs(slot.bat_flow_kw) : 0));

                    const dateStr = translateDateLabel(slot.date_label);

                    return `
                        <div style="font-weight: bold; margin-bottom: 6px; border-bottom: 1px solid rgba(51, 65, 85, 0.8); padding-bottom: 4px; color: #fff;">
                            ${dateStr} ${slot.time_label} ${slot.is_night ? "🌙" : "☀️"}
                        </div>
                        <div style="display: flex; justify-content: space-between; gap: 16px; margin: 3px 0; color: #34d399;">
                            <span>🔋 ${t("battery_forecast.soc_level", "Ladestand (SoC)")}:</span>
                            <b style="font-family: monospace;">${socVal}% (${storedVal} kWh)</b>
                        </div>
                        <div style="display: flex; justify-content: space-between; gap: 16px; margin: 3px 0; color: #fbbf24;">
                            <span>☀️ ${t("battery_forecast.solar_yield", "Solar-Ertrag")}:</span>
                            <b style="font-family: monospace;">+${solarVal} kW</b>
                        </div>
                        <div style="display: flex; justify-content: space-between; gap: 16px; margin: 3px 0; color: #60a5fa;">
                            <span>🏠 ${t("battery_forecast.house_load", "Hauslast")}:</span>
                            <b style="font-family: monospace;">-${loadVal} kW</b>
                        </div>
                        ${
                            chargeVal > 0.01
                                ? `<div style="display: flex; justify-content: space-between; gap: 16px; margin: 3px 0; color: #4ade80; font-weight: bold; border-top: 1px solid rgba(51, 65, 85, 0.6); padding-top: 3px;">
                                    <span>⚡ ${t("battery_forecast.battery_charge_flow", "Speicher-Ladung")}:</span>
                                    <b style="font-family: monospace;">+${chargeVal.toFixed(2)} kW</b>
                                   </div>`
                                : ""
                        }
                        ${
                            dischargeVal > 0.01
                                ? `<div style="display: flex; justify-content: space-between; gap: 16px; margin: 3px 0; color: #38bdf8; font-weight: bold; border-top: 1px solid rgba(51, 65, 85, 0.6); padding-top: 3px;">
                                    <span>🔄 ${t("battery_forecast.battery_discharge_flow", "Speicher-Entladung")}:</span>
                                    <b style="font-family: monospace;">-${dischargeVal.toFixed(2)} kW</b>
                                   </div>`
                                : ""
                        }
                    `;
                },
            },
            legend: {
                show: false,
            },
            grid: {
                top: 24,
                left: 45,
                right: 45,
                bottom: 32,
            },
            xAxis: {
                type: "category",
                data: categories,
                boundaryGap: false,
                axisLine: { lineStyle: { color: "rgba(110, 231, 183, 0.2)" } },
                axisTick: { show: false },
                axisLabel: {
                    color: "#94a3b8",
                    fontSize: 10,
                    interval: horizon === 48 ? 3 : 1,
                },
            },
            yAxis: [
                {
                    type: "value",
                    name: "SoC %",
                    nameTextStyle: { color: "#34d399", fontSize: 10 },
                    min: 0,
                    max: 100,
                    interval: 25,
                    splitLine: { lineStyle: { color: "rgba(51, 65, 85, 0.35)", type: "dashed" } },
                    axisLabel: {
                        color: "#6ee7b7",
                        fontSize: 10,
                        formatter: "{value}%",
                    },
                },
                {
                    type: "value",
                    name: "kW",
                    nameTextStyle: { color: "#94a3b8", fontSize: 10 },
                    splitLine: { show: false },
                    axisLabel: {
                        color: "#94a3b8",
                        fontSize: 10,
                        formatter: "{value} kW",
                    },
                },
            ],
            series: [
                {
                    name: "SoC (%)",
                    type: "line",
                    yAxisIndex: 0,
                    smooth: 0.35,
                    showSymbol: false,
                    data: socValues,
                    z: 10,
                    lineStyle: {
                        width: 3.5,
                        color: "#10b981",
                        shadowColor: "rgba(16, 185, 129, 0.6)",
                        shadowBlur: 10,
                    },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: "rgba(16, 185, 129, 0.40)" },
                                { offset: 0.8, color: "rgba(6, 182, 212, 0.12)" },
                                { offset: 1, color: "rgba(15, 23, 42, 0.0)" },
                            ],
                        },
                    },
                    markLine: {
                        silent: true,
                        symbol: "none",
                        data: [
                            {
                                yAxis: params.min_soc_reserve_pct || 10,
                                lineStyle: { color: "#f59e0b", type: "dashed", width: 1.5 },
                                label: {
                                    show: true,
                                    position: "end",
                                    formatter: `Reserve ${params.min_soc_reserve_pct || 10}%`,
                                    color: "#fcd34d",
                                    fontSize: 9,
                                },
                            },
                        ],
                    },
                },
                {
                    name: "Solar-Ertrag (kW)",
                    type: "line",
                    yAxisIndex: 1,
                    smooth: 0.35,
                    showSymbol: false,
                    data: solarValues,
                    z: 5,
                    lineStyle: {
                        width: 2,
                        color: "#f59e0b",
                    },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: "rgba(245, 158, 11, 0.25)" },
                                { offset: 1, color: "rgba(245, 158, 11, 0.0)" },
                            ],
                        },
                    },
                },
                {
                    name: "Hauslast (kW)",
                    type: "line",
                    yAxisIndex: 1,
                    smooth: 0.35,
                    showSymbol: false,
                    data: loadValues,
                    z: 6,
                    lineStyle: {
                        width: 2,
                        color: "#60a5fa",
                        type: "dashed",
                    },
                },
            ],
        };
    }, [timeline, horizon, params]);

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
                        {t("battery_forecast.in_storage", "{{kwh}} kWh im Speicher", { kwh: kpis.start_stored_kwh })}
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
                        {kpis.full_charge_time 
                            ? t("battery_forecast.full_at", "Voll um {{time}}", { time: kpis.full_charge_time }) 
                            : t("battery_forecast.not_reaching_full", "Erreicht keine 100%")}
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
                        {t("battery_forecast.load_coverage", "Deckung für Haushaltslast")}
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
                        {kpis.depleted_time 
                            ? t("battery_forecast.reserve_reached_at", "Reserve um {{time}} erreicht", { time: kpis.depleted_time }) 
                            : t("battery_forecast.lasts_all_night", "Reicht durchgehend (kein Leerlaufen)")}
                    </div>
                </div>
            </div>

            {/* =========================================================
                SIMULATION TIMELINE ECHARTS CHART
            ========================================================= */}
            <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs text-emerald-200/80">
                    <span className="font-bold flex items-center gap-1.5">
                        <span>📈</span> {t("battery_forecast.timeline_title", "Simulierter SoC-Verlauf & Ladefluss")}
                    </span>
                    <div className="flex flex-wrap items-center gap-3 text-[11px]">
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block shadow-xs shadow-emerald-400/50" /> {t("battery_forecast.legend_soc", "SoC (%)")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" /> {t("battery_forecast.legend_solar", "Solar (kW)")}
                        </span>
                        <span className="flex items-center gap-1">
                            <span className="w-2.5 h-2.5 rounded-full bg-blue-400 inline-block" /> {t("battery_forecast.legend_load", "Hauslast (kW)")}
                        </span>
                    </div>
                </div>

                {/* ECharts Area Container */}
                <div className="bg-slate-950/80 border border-emerald-900/50 rounded-2xl p-2 pt-3 shadow-inner">
                    <ReactECharts
                        option={chartOption}
                        style={{ height: "280px", width: "100%" }}
                        notMerge={true}
                        lazyUpdate={false}
                        opts={{ renderer: "canvas" }}
                    />

                    {/* Timeline footer dates */}
                    <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400 font-medium px-4 pb-2 border-t border-slate-800/60 pt-2">
                        <span>
                            {timeline[0]?.date_label === "Heute" ? t("common.today", "Heute") : timeline[0]?.date_label === "Morgen" ? t("common.tomorrow", "Morgen") : timeline[0]?.date_label} ({timeline[0]?.time_label})
                        </span>
                        <span className="text-emerald-300 font-semibold">
                            🔋 {params.battery_name || t("battery_forecast.storage", "Speicher")} · {kpis.night_autarky_pct || 0}% {t("battery_forecast.night_autarky", "Nachtautarkie")}
                        </span>
                        <span>
                            {timeline[timeline.length - 1]?.date_label === "Heute" ? t("common.today", "Heute") : timeline[timeline.length - 1]?.date_label === "Morgen" ? t("common.tomorrow", "Morgen") : timeline[timeline.length - 1]?.date_label} ({timeline[timeline.length - 1]?.time_label})
                        </span>
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

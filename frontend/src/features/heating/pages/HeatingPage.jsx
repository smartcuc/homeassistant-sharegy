import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import FloorHeatingLoadCard from "../../control/components/FloorHeatingLoadCard";
import BWWPLoadManagementCard from "../../energy/components/BWWPLoadManagementCard";
import HeatingRodCard from "../../control/components/HeatingRodCard";
import AirConditioningCard from "../../control/components/AirConditioningCard";

export default function HeatingPage() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [activeTab, setActiveTab] = useState("all");

    // Live Floor Heating Status abfragen für Quick-KPIs
    const fbhQuery = useQuery({
        queryKey: ["floor-heating"],
        queryFn: () => apiFetch("/api/energy/floor-heating/"),
        refetchInterval: 5000,
    });

    const fbhData = fbhQuery.data || {};
    const storage = fbhData.storage || {};
    const flow = fbhData.flow_temperature || {};
    const temp = fbhData.temperature || {};
    const signals = fbhData.signals || {};
    const isLive = !fbhQuery.isLoading && !fbhQuery.isError && fbhData.config_id;

    return (
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
            {/* 1. Header: Titel & Beschreibung */}
            <div className="space-y-4 border-b border-slate-200 dark:border-slate-800 pb-5">
                <div className="flex items-start sm:items-center gap-3.5">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-500 to-amber-500 text-white flex items-center justify-center text-2xl shadow-lg shadow-rose-500/20 shrink-0">
                        🌡️
                    </div>
                    <div>
                        <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                            Wärme, Heizung & Raumklima
                        </h1>
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                            Wettergeführte Fußbodenheizung (DIN EN 12831 / MPC), thermische Estrich-Speicherbatterie & Wärmepumpen-Lastmanagement.
                        </p>
                    </div>
                </div>

                {/* 2. Badges & Filter-Tabs unter dem Titel */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                    {/* Status Badges */}
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 flex items-center gap-1.5">
                            <span>🔥</span>
                            <span>Thermische Speicher & MPC</span>
                        </span>

                        {isLive ? (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                <span>Live-Steuerung aktiv ({fbhData.control_mode_display || "Autopilot"})</span>
                            </span>
                        ) : fbhQuery.isLoading ? (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
                                <span>Verbinde mit Heizkreis...</span>
                            </span>
                        ) : (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 flex items-center gap-1.5">
                                <span>⚙️</span>
                                <span>Bereit</span>
                            </span>
                        )}

                        {fbhData.is_preheating_active && (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 flex items-center gap-1.5">
                                <span>⚡</span>
                                <span>Estrich-Vorladeboost aktiv</span>
                            </span>
                        )}
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
                        {[
                            { key: "all", label: "Alle Heizsysteme", icon: "♨️" },
                            { key: "fbh", label: "Fußbodenheizung", icon: "🌡️" },
                            { key: "bwwp", label: "Warmwasser & WP", icon: "🔥" },
                            { key: "ac_rod", label: "Klima & Heizstab", icon: "❄️" },
                        ].map((tab) => (
                            <button
                                key={tab.key}
                                type="button"
                                onClick={() => setActiveTab(tab.key)}
                                className={`px-3.5 py-1.5 rounded-2xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
                                    activeTab === tab.key
                                        ? "bg-rose-600 text-white shadow-md shadow-rose-600/20"
                                        : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                                }`}
                            >
                                <span>{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* 3. Quick Thermal Metrics Overview (Echtdaten) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl shrink-0">
                        🧱
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Estrich-Speichermasse</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {storage.estrich_mass_kg ? (storage.estrich_mass_kg / 1000).toFixed(1) : "—"} <span className="text-xs font-normal text-slate-500">t Beton</span>
                        </div>
                        <div className="text-[11px] text-slate-500">
                            {storage.thermal_capacity_kwh_k ? `${storage.thermal_capacity_kwh_k} kWh/K Kapazität` : "Berechne..."}
                        </div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 flex items-center justify-center text-xl shrink-0">
                        🔥
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Thermischer Ladezustand</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {storage.thermal_soc_pct !== undefined ? `${storage.thermal_soc_pct}%` : "—"} <span className="text-xs font-normal text-slate-500">SoC</span>
                        </div>
                        <div className="text-[11px] text-rose-600 dark:text-rose-400 font-bold">
                            {storage.stored_energy_kwh_th !== undefined ? `${storage.stored_energy_kwh_th} kWh th. geladen` : "Berechne..."}
                        </div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shrink-0">
                        📉
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">MPC Vorlauftemperatur</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {flow.opt_flow_temp_c !== undefined ? `${flow.opt_flow_temp_c}°C` : "—"} <span className="text-xs font-normal text-slate-500">Soll</span>
                        </div>
                        <div className="text-[11px] text-indigo-600 dark:text-indigo-400 font-medium">
                            {flow.solar_offset_k > 0 
                                ? `☀️ -${flow.solar_offset_k} K Sonnengewinn` 
                                : `Heizkurve ${flow.heating_curve_slope || "0.60"}`}
                        </div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xl shrink-0">
                        🛋️
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Raumtemperatur</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {temp.current_c !== undefined ? `${temp.current_c}°C` : "—"} <span className="text-xs font-normal text-slate-500">Ist</span>
                        </div>
                        <div className="text-[11px] text-slate-500">
                            {temp.target_c !== undefined ? `Sollwert: ${temp.target_c}°C` : "Soll: 21.0°C"}
                        </div>
                    </div>
                </div>
            </div>

            {/* 4. Main Cards Layout (Voll interaktiv & scharfgeschaltet) */}
            <div className="space-y-6">
                {/* 🌡️ Fußbodenheizung & Thermische Estrich-Vorladung */}
                {(activeTab === "all" || activeTab === "fbh") && (
                    <div>
                        <FloorHeatingLoadCard />
                    </div>
                )}

                {/* ♨️ BWWP & Wärmepumpen SG-Ready Lastmanagement */}
                {(activeTab === "all" || activeTab === "bwwp") && (
                    <div>
                        <BWWPLoadManagementCard />
                    </div>
                )}

                {/* ❄️ Klimaanlagen & Heizstab Grid */}
                {(activeTab === "all" || activeTab === "ac_rod") && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <HeatingRodCard />
                        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 space-y-4">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-2xl bg-sky-500/10 text-sky-600 flex items-center justify-center text-xl">
                                    ❄️
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Klimaanlage (Pre-Cooling)</h3>
                                    <p className="text-xs text-slate-500">Solares Vorkühlen bei hohen Einstrahlungsspitzen.</p>
                                </div>
                            </div>
                            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 text-xs text-slate-600 dark:text-slate-300">
                                Automatische Aktivierung bei Raumtemperaturen über 24,0°C und vorhandenem Solarüberschuss (&gt; 1.500 W).
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

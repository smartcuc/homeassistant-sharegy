import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function FloorHeatingLoadCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [scheduleDrawerOpen, setScheduleDrawerOpen] = useState(false);
    const [formConfig, setFormConfig] = useState(null);

    // 1. Live Floor Heating Status & Configuration from Backend
    const heatingQuery = useQuery({
        queryKey: ["floor-heating-status"],
        queryFn: () => apiFetch("/api/energy/floor-heating/"),
        refetchInterval: 5000,
    });

    // 2. Devices for optional device binding selection in settings
    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
        enabled: settingsOpen,
    });

    const boostMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/floor-heating/boost/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload || { duration_hours: 2.0 }),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["floor-heating-status"] });
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
        },
    });

    const toggleMutation = useMutation({
        mutationFn: (state) =>
            apiFetch("/api/energy/floor-heating/toggle/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ state }),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["floor-heating-status"] });
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
        },
    });

    const configMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/floor-heating/config/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["floor-heating-status"] });
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            setSettingsOpen(false);
        },
    });

    const data = heatingQuery.data || {};
    const tempInfo = data.temperature || {};
    const flowInfo = data.flow_temperature || {};
    const mpcInfo = data.predictive_mpc || {};
    const storage = data.storage || {};
    const signals = data.signals || {};

    const currentTemp = tempInfo.current_c ?? 21.2;
    const targetTemp = tempInfo.target_c ?? 21.0;
    const boostDelta = tempInfo.boost_delta_k ?? 1.0;
    const boostTarget = tempInfo.boost_target_c ?? 22.0;
    const maxFloorTemp = tempInfo.max_floor_c ?? 24.5;

    const optFlowTemp = flowInfo.opt_flow_temp_c ?? 28.5;
    const baseFlowTemp = flowInfo.base_flow_temp_c ?? 29.0;
    const flowDeltaK = flowInfo.flow_delta_k ?? 0.0;

    const outdoorTemp = signals.outdoor_temp_c ?? 7.5;
    const solarRadiation = signals.solar_radiation_wm2 ?? 380;

    const socPct = storage.thermal_soc_pct ?? 65.0;
    const storedKwhTh = storage.stored_energy_kwh_th ?? 14.2;
    const storedKwhEl = storage.stored_energy_kwh_el ?? 4.1;
    const estrichMassKg = storage.estrich_mass_kg ?? 16800;

    const isPreheating = data.is_preheating_active || false;
    const relayState = data.relay_state || false;
    const controlMode = data.control_mode || "autopilot";
    const decisionReason = data.decision_reason || "Normalbetrieb";

    const timeline = mpcInfo.timeline || [];

    const handleOpenSettings = () => {
        setFormConfig({
            control_mode: controlMode,
            target_room_temp_c: targetTemp,
            boost_delta_k: boostDelta,
            max_floor_temp_c: maxFloorTemp,
            heating_curve_slope: flowInfo.heating_curve_slope ?? 0.60,
            predictive_mpc_enabled: flowInfo.mpc_enabled ?? true,
            solar_gain_compensation: true,
            min_pv_surplus_w: signals.min_pv_surplus_w ?? 1000.0,
            max_spot_price_ct_kwh: signals.max_spot_price_ct_kwh ?? 16.0,
            estrich_area_sqm: 120.0,
            active: data.active ?? true,
            device_id: data.device_id || "",
        });
        setSettingsOpen(true);
    };

    if (heatingQuery.isLoading) {
        return (
            <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xs animate-pulse">
                <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded w-1/3 mb-4"></div>
                <div className="h-28 bg-slate-100 dark:bg-slate-800/60 rounded-2xl"></div>
            </div>
        );
    }

    return (
        <div className="relative overflow-hidden bg-white dark:bg-slate-900/90 rounded-3xl border border-slate-200/80 dark:border-slate-800 p-5 sm:p-6 shadow-xs backdrop-blur-xl transition-all hover:border-amber-500/40">
            {/* Top Row: Title & Action Toggles */}
            <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                    <div className={`w-11 h-11 rounded-2xl flex items-center justify-center text-xl shadow-inner transition-colors ${
                        isPreheating
                            ? "bg-amber-500/20 text-amber-500 ring-2 ring-amber-500/40"
                            : relayState
                            ? "bg-emerald-500/20 text-emerald-500 ring-2 ring-emerald-500/40"
                            : "bg-slate-100 dark:bg-slate-800 text-slate-500"
                    }`}>
                        🌡️
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                {t("control.floor_heating", "Fußbodenheizung & Estrich-Speicher")}
                            </h3>
                            {isPreheating ? (
                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 animate-pulse">
                                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                                    {t("control.preheating_badge", "Thermische Vorladung")}
                                </span>
                            ) : relayState ? (
                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                    {t("control.heating_active", "Heizen aktiv")}
                                </span>
                            ) : (
                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700">
                                    {t("control.standby", "Standby / Passiv")}
                                </span>
                            )}
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            {t("control.floor_heating_desc", "Vorausschauende KI-Wetter Vorlauftemperatur & thermische Bauteilaktivierung")}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={handleOpenSettings}
                        className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title={t("common.settings", "Einstellungen")}
                    >
                        ⚙️
                    </button>
                    <button
                        onClick={() => toggleMutation.mutate(!relayState)}
                        disabled={toggleMutation.isPending}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                            relayState
                                ? "bg-red-500/15 text-red-600 dark:text-red-400 hover:bg-red-500/25 border border-red-500/30"
                                : "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/25 border border-emerald-500/30"
                        }`}
                    >
                        {relayState ? t("common.turn_off", "Pausieren") : t("common.turn_on", "Einschalten")}
                    </button>
                </div>
            </div>

            {/* Thermal Battery Level (SoC Gauge) */}
            <div className="mb-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-3.5 border border-slate-200/60 dark:border-slate-800">
                <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                        <span>🔋</span> {t("control.thermal_battery_soc", "Estrich-Speicherfüllstand")}
                    </span>
                    <span className="font-bold text-amber-600 dark:text-amber-400">
                        {socPct}% · ~{storedKwhTh} kWh <span className="text-[10px] text-slate-400">({storedKwhEl} kWh el)</span>
                    </span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-amber-500 via-orange-500 to-emerald-500 transition-all duration-700 rounded-full"
                        style={{ width: `${socPct}%` }}
                    ></div>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
                    <span>Basis ({targetTemp - 0.5}°C)</span>
                    <span>Speichermasse: ~{(estrichMassKg / 1000).toFixed(1)} t Beton</span>
                    <span>Voll ({boostTarget}°C)</span>
                </div>
            </div>

            {/* Temperatures & Live Metrics Grid (4-Spalten) */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                {/* Raum-Ist */}
                <div className="bg-slate-50/80 dark:bg-slate-800/40 rounded-xl p-2.5 border border-slate-200/60 dark:border-slate-800/60 text-center">
                    <div className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                        {t("control.room_temp", "Raum-Ist")}
                    </div>
                    <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">
                        {currentTemp}°C
                    </div>
                    <div className="text-[10px] text-slate-400">Soll {targetTemp}°C</div>
                </div>

                {/* Vorlauf KI-Soll */}
                <div className="bg-indigo-50/70 dark:bg-indigo-950/30 rounded-xl p-2.5 border border-indigo-200/60 dark:border-indigo-800/60 text-center">
                    <div className="text-[10px] font-medium text-indigo-700 dark:text-indigo-300 flex items-center justify-center gap-1">
                        <span>🧠</span> <span>Vorlauf KI</span>
                    </div>
                    <div className="text-base font-black text-indigo-700 dark:text-indigo-300 mt-0.5">
                        {optFlowTemp}°C
                    </div>
                    <div className="text-[10px] font-semibold text-indigo-500">
                        {flowDeltaK > 0 ? `+${flowDeltaK}K Boost` : flowDeltaK < 0 ? `${flowDeltaK}K Solar` : `Basis ${baseFlowTemp}°C`}
                    </div>
                </div>

                {/* Außentemperatur */}
                <div className="bg-slate-50/80 dark:bg-slate-800/40 rounded-xl p-2.5 border border-slate-200/60 dark:border-slate-800/60 text-center">
                    <div className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                        Außenwetter
                    </div>
                    <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">
                        {outdoorTemp}°C
                    </div>
                    <div className="text-[10px] text-slate-400">{solarRadiation} W/m² Sonne</div>
                </div>

                {/* Vorlade-Ziel */}
                <div className="bg-amber-50/70 dark:bg-amber-950/30 rounded-xl p-2.5 border border-amber-200/60 dark:border-amber-800/60 text-center">
                    <div className="text-[10px] font-medium text-amber-700 dark:text-amber-300">
                        {t("control.boost_target", "Vorlade-Ziel")}
                    </div>
                    <div className="text-base font-black text-amber-600 dark:text-amber-400 mt-0.5">
                        {boostTarget}°C
                    </div>
                    <div className="text-[10px] text-amber-600 dark:text-amber-400">+{boostDelta}K Delta</div>
                </div>
            </div>

            {/* Decision Reason Banner */}
            <div className="text-xs bg-slate-100/70 dark:bg-slate-800/70 text-slate-600 dark:text-slate-300 px-3 py-2 rounded-xl mb-4 flex items-center gap-2 border border-slate-200/50 dark:border-slate-700/50">
                <span className="text-sm">💡</span>
                <span className="truncate">{decisionReason}</span>
            </div>

            {/* 🧠 KI-WETTER & PRÄDIKTIVER FAHRPLAN PREVIEW BUTTON / BANNER */}
            {mpcInfo.ai_recommendation_text && (
                <div className="mb-4 bg-gradient-to-br from-indigo-50/60 via-sky-50/40 to-slate-50 dark:from-indigo-950/40 dark:via-sky-950/20 dark:to-slate-900/50 rounded-2xl p-3.5 border border-indigo-200/60 dark:border-indigo-800/60">
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center gap-2">
                            <span className="text-sm">🧠</span>
                            <span className="text-xs font-bold text-indigo-900 dark:text-indigo-200">
                                {mpcInfo.ai_recommendation_title || "KI-Wetter & Prädiktiver MPC-Fahrplan"}
                            </span>
                        </div>
                        <button
                            onClick={() => setScheduleDrawerOpen(!scheduleDrawerOpen)}
                            className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline cursor-pointer flex items-center gap-1"
                        >
                            <span>{scheduleDrawerOpen ? "Fahrplan schließen" : "24h-Fahrplan anzeigen"}</span>
                            <span>{scheduleDrawerOpen ? "▲" : "▼"}</span>
                        </button>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                        {mpcInfo.ai_recommendation_text}
                    </p>

                    {/* Summary Badges */}
                    <div className="flex flex-wrap items-center gap-2 mt-2.5 pt-2 border-t border-indigo-100 dark:border-indigo-900/50 text-[11px]">
                        <span className="px-2 py-0.5 rounded-md bg-amber-500/15 text-amber-700 dark:text-amber-300 font-medium">
                            ⚡ Vorladen: {mpcInfo.best_preheat_window}
                        </span>
                        <span className="px-2 py-0.5 rounded-md bg-sky-500/15 text-sky-700 dark:text-sky-300 font-medium">
                            🛋️ Entladen: {mpcInfo.best_coast_window}
                        </span>
                        {mpcInfo.estimated_savings_eur > 0 && (
                            <span className="px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-bold ml-auto">
                                💰 ~{mpcInfo.estimated_savings_eur.toFixed(2)} € Ersparnis/Tag
                            </span>
                        )}
                    </div>

                    {/* Expandable 24h Timeline */}
                    {scheduleDrawerOpen && timeline.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-indigo-200/50 dark:border-indigo-800/50 space-y-2">
                            <div className="text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center justify-between">
                                <span>24-Stunden Vorlauf- & Wetterfahrplan:</span>
                                <span className="text-[10px] text-slate-400">Heizkurve vs. Vorlade-Boost</span>
                            </div>
                            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-1.5 max-h-48 overflow-y-auto pr-1">
                                {timeline.slice(0, 16).map((slot, idx) => (
                                    <div
                                        key={idx}
                                        className={`p-2 rounded-xl border text-center transition-all ${
                                            slot.action_mode === "preheat"
                                                ? "bg-amber-500/15 border-amber-500/40 text-amber-900 dark:text-amber-200"
                                                : slot.action_mode === "coast"
                                                ? "bg-sky-500/15 border-sky-500/40 text-sky-900 dark:text-sky-200"
                                                : "bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300"
                                        }`}
                                    >
                                        <div className="text-[10px] font-bold">{slot.hour_label}</div>
                                        <div className="text-xs font-black my-0.5">{slot.opt_flow_temp_c}°C</div>
                                        <div className="text-[9px] opacity-80">{slot.outdoor_temp_c}°C · {slot.solar_radiation_wm2}W</div>
                                        <div className="text-[8px] font-semibold mt-0.5 truncate">{slot.action_badge}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Bottom Actions: Boost & Mode */}
            <div className="flex items-center justify-between gap-3">
                <button
                    onClick={() => boostMutation.mutate({ duration_hours: 2.0 })}
                    disabled={boostMutation.isPending}
                    className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-1.5 ${
                        isPreheating
                            ? "bg-amber-500 text-white hover:bg-amber-600"
                            : "bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:opacity-95"
                    }`}
                >
                    <span>🔥</span>
                    <span>{isPreheating ? t("control.boost_active", "Vorladeboost aktiv (2h)") : t("control.boost_screed", "Estrich vorladen (2h)")}</span>
                </button>

                <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-lg">
                    Modus: <span className="font-bold text-slate-700 dark:text-slate-200 capitalize">{controlMode}</span>
                </div>
            </div>

            {/* Settings Modal */}
            {settingsOpen && formConfig && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-lg shadow-2xl animate-scale-in">
                        <div className="flex items-center justify-between mb-5">
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <span>⚙️</span> {t("control.floor_heating_settings", "Fußbodenheizung & MPC-Parameter")}
                            </h3>
                            <button
                                onClick={() => setSettingsOpen(false)}
                                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl font-bold"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
                            {/* Control Mode */}
                            <div>
                                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                                    {t("control.mode", "Betriebsmodus")}
                                </label>
                                <select
                                    value={formConfig.control_mode}
                                    onChange={(e) => setFormConfig({ ...formConfig, control_mode: e.target.value })}
                                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white"
                                >
                                    <option value="autopilot">🤖 Autopilot (Solar- & Börsenpreis-Vorladung)</option>
                                    <option value="pv_only">☀️ Nur PV-Überschuss</option>
                                    <option value="price_saver">💰 Sparfuchs (Günstigste Börsenstunden)</option>
                                    <option value="comfort">🛋️ Komfortbetrieb (Feste Solltemperatur)</option>
                                    <option value="manual">🛑 Manuell (Automatik pausiert)</option>
                                </select>
                            </div>

                            {/* Target Temperature Slider */}
                            <div>
                                <div className="flex justify-between text-xs font-semibold mb-1">
                                    <span className="text-slate-700 dark:text-slate-300">Raum-Solltemperatur</span>
                                    <span className="text-amber-500 font-bold">{formConfig.target_room_temp_c}°C</span>
                                </div>
                                <input
                                    type="range"
                                    min="18.0"
                                    max="23.0"
                                    step="0.5"
                                    value={formConfig.target_room_temp_c}
                                    onChange={(e) => setFormConfig({ ...formConfig, target_room_temp_c: parseFloat(e.target.value) })}
                                    className="w-full accent-amber-500 cursor-pointer"
                                />
                            </div>

                            {/* Preheating Boost Delta */}
                            <div>
                                <div className="flex justify-between text-xs font-semibold mb-1">
                                    <span className="text-slate-700 dark:text-slate-300">Thermische Vorladung (Delta K)</span>
                                    <span className="text-amber-500 font-bold">+{formConfig.boost_delta_k} K (Ziel: {(parseFloat(formConfig.target_room_temp_c) + parseFloat(formConfig.boost_delta_k)).toFixed(1)}°C)</span>
                                </div>
                                <input
                                    type="range"
                                    min="0.5"
                                    max="2.0"
                                    step="0.1"
                                    value={formConfig.boost_delta_k}
                                    onChange={(e) => setFormConfig({ ...formConfig, boost_delta_k: parseFloat(e.target.value) })}
                                    className="w-full accent-amber-500 cursor-pointer"
                                />
                                <p className="text-[11px] text-slate-400 mt-1">
                                    Hebt die Zieltemperatur bei Solarüberschuss oder Negativpreisen temporär an, um den Estrich vorzuladen.
                                </p>
                            </div>

                            {/* 🧠 Heizkurven-Steilheit (Slope) */}
                            <div>
                                <div className="flex justify-between text-xs font-semibold mb-1">
                                    <span className="text-slate-700 dark:text-slate-300">Heizkurven-Steilheit (Niedertemperatur FBH)</span>
                                    <span className="text-indigo-500 font-bold">{formConfig.heating_curve_slope}</span>
                                </div>
                                <input
                                    type="range"
                                    min="0.30"
                                    max="1.00"
                                    step="0.05"
                                    value={formConfig.heating_curve_slope}
                                    onChange={(e) => setFormConfig({ ...formConfig, heating_curve_slope: parseFloat(e.target.value) })}
                                    className="w-full accent-indigo-500 cursor-pointer"
                                />
                                <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                                    <span>0.30 (Sehr gut gedämmt)</span>
                                    <span>0.60 (Standard FBH)</span>
                                    <span>1.00 (Altbau)</span>
                                </div>
                            </div>

                            {/* Predictive MPC Checkboxes */}
                            <div className="space-y-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/60 dark:border-slate-700/60">
                                <label className="flex items-center gap-2.5 cursor-pointer text-xs font-semibold text-slate-700 dark:text-slate-300">
                                    <input
                                        type="checkbox"
                                        checked={formConfig.predictive_mpc_enabled}
                                        onChange={(e) => setFormConfig({ ...formConfig, predictive_mpc_enabled: e.target.checked })}
                                        className="rounded text-amber-500 focus:ring-amber-400"
                                    />
                                    <span>🧠 Prädiktive KI-Wetter-Optimierung (MPC) aktivieren</span>
                                </label>
                                <label className="flex items-center gap-2.5 cursor-pointer text-xs font-semibold text-slate-700 dark:text-slate-300">
                                    <input
                                        type="checkbox"
                                        checked={formConfig.solar_gain_compensation}
                                        onChange={(e) => setFormConfig({ ...formConfig, solar_gain_compensation: e.target.checked })}
                                        className="rounded text-amber-500 focus:ring-amber-400"
                                    />
                                    <span>☀️ Solares Absenken bei prognostizierter Sonneneinstrahlung</span>
                                </label>
                            </div>

                            {/* Overheating Safety Threshold */}
                            <div>
                                <div className="flex justify-between text-xs font-semibold mb-1">
                                    <span className="text-slate-700 dark:text-slate-300">Überhitzungsschutz (Max-Temperatur)</span>
                                    <span className="text-red-500 font-bold">{formConfig.max_floor_temp_c}°C</span>
                                </div>
                                <input
                                    type="range"
                                    min="23.0"
                                    max="26.0"
                                    step="0.5"
                                    value={formConfig.max_floor_temp_c}
                                    onChange={(e) => setFormConfig({ ...formConfig, max_floor_temp_c: parseFloat(e.target.value) })}
                                    className="w-full accent-red-500 cursor-pointer"
                                />
                            </div>

                            {/* Estrich Area */}
                            <div>
                                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                    Beheizte Estrichfläche (m²)
                                </label>
                                <input
                                    type="number"
                                    min="20"
                                    max="500"
                                    step="5"
                                    value={formConfig.estrich_area_sqm}
                                    onChange={(e) => setFormConfig({ ...formConfig, estrich_area_sqm: parseFloat(e.target.value) || 120.0 })}
                                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white"
                                />
                            </div>

                            {/* Thresholds Grid */}
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                        Min. Solarüberschuss (W)
                                    </label>
                                    <input
                                        type="number"
                                        min="0"
                                        max="5000"
                                        step="100"
                                        value={formConfig.min_pv_surplus_w}
                                        onChange={(e) => setFormConfig({ ...formConfig, min_pv_surplus_w: parseFloat(e.target.value) || 0 })}
                                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                        Max. Börsenpreis (ct/kWh)
                                    </label>
                                    <input
                                        type="number"
                                        min="0"
                                        max="50"
                                        step="0.5"
                                        value={formConfig.max_spot_price_ct_kwh}
                                        onChange={(e) => setFormConfig({ ...formConfig, max_spot_price_ct_kwh: parseFloat(e.target.value) || 0 })}
                                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-slate-200 dark:border-slate-800">
                            <button
                                onClick={() => setSettingsOpen(false)}
                                className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                            >
                                {t("common.cancel", "Abbrechen")}
                            </button>
                            <button
                                onClick={() => configMutation.mutate(formConfig)}
                                disabled={configMutation.isPending}
                                className="px-5 py-2 rounded-xl text-sm font-bold bg-amber-500 hover:bg-amber-600 text-white shadow-xs"
                            >
                                {configMutation.isPending ? t("common.saving", "Speichern...") : t("common.save", "Speichern")}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}


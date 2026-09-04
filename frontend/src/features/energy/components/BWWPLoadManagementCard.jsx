import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function BWWPLoadManagementCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [formConfig, setFormConfig] = useState(null);

    const bwwpQuery = useQuery({
        queryKey: ["bwwp-load-mgmt"],
        queryFn: () => apiFetch("/api/energy/bwwp/"),
        refetchInterval: 12000,
    });

    const switchMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/bwwp/switch/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bwwp-load-mgmt"] });
        },
    });

    const configMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/bwwp/config/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bwwp-load-mgmt"] });
            setSettingsOpen(false);
        },
    });

    const data = bwwpQuery.data || {};
    const telemetry = data.telemetry || {};
    const metrics = data.metrics || {};
    const thresholds = data.thresholds || {};

    const tempC = telemetry.temperature_c ?? metrics.water_temperature_c ?? 48.0;
    const powerW = telemetry.power_w ?? metrics.power_w ?? 0.0;
    const relayState = data.relay_state ?? telemetry.relay_state ?? false;
    const sgState = data.current_sg_state || "2_normal";
    const decisionReason = data.decision_reason || "System im Regelbetrieb.";
    const isProtectionActive = data.protection_active || false;
    const controlMode = data.control_mode || "hybrid";

    const tMin = thresholds.min_temp_c ?? 45.0;
    const tTarget = thresholds.target_temp_c ?? 52.0;
    const tBoost = thresholds.boost_temp_c ?? 60.0;
    const tMax = thresholds.max_safety_temp_c ?? 65.0;
    const minSurplusW = thresholds.min_pv_surplus_w ?? 800.0;
    const availableSurplusW = metrics.available_surplus_w ?? 0.0;
    const gridPriceCt = metrics.grid_price_ct ?? 24.5;

    // Relative Position für Temperatur-Balken (30°C bis 70°C Skala)
    const scaleMin = 30;
    const scaleMax = 70;
    const tempPct = Math.min(100, Math.max(0, ((tempC - scaleMin) / (scaleMax - scaleMin)) * 100));
    const tMinPct = ((tMin - scaleMin) / (scaleMax - scaleMin)) * 100;
    const tTargetPct = ((tTarget - scaleMin) / (scaleMax - scaleMin)) * 100;
    const tBoostPct = ((tBoost - scaleMin) / (scaleMax - scaleMin)) * 100;

    const handleOpenSettings = () => {
        setFormConfig({
            min_temp_c: tMin,
            target_temp_c: tTarget,
            boost_temp_c: tBoost,
            max_safety_temp_c: tMax,
            min_pv_surplus_w: minSurplusW,
            max_price_threshold_ct: thresholds.max_price_threshold_ct ?? 18.0,
            battery_soc_reserve_pct: thresholds.battery_soc_reserve_pct ?? 50.0,
            control_mode: controlMode,
            active: data.status === "active",
        });
        setSettingsOpen(true);
    };

    if (bwwpQuery.isLoading) {
        return (
            <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xs animate-pulse">
                <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded w-1/3 mb-4"></div>
                <div className="h-28 bg-slate-100 dark:bg-slate-800/60 rounded-2xl"></div>
            </div>
        );
    }

    if (data.status === "unconfigured") {
        return null;
    }

    return (
        <div className="p-6 bg-gradient-to-br from-white via-slate-50/70 to-blue-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-blue-950/20 rounded-3xl border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden">
            {/* Background Glow */}
            <div className="absolute top-0 right-0 w-72 h-72 bg-blue-500/5 dark:bg-blue-400/10 rounded-full blur-3xl pointer-events-none" />

            <div className="relative z-10 space-y-5">
                {/* Header */}
                <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3.5">
                        <div className="w-12 h-12 rounded-2xl bg-blue-500/10 dark:bg-blue-400/15 border border-blue-500/20 dark:border-blue-400/30 flex items-center justify-center text-2xl shadow-xs">
                            ♨️
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-slate-900 dark:text-white">
                                    {data.device_name || "Brauchwasserwärmepumpe"}
                                </h2>
                                <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${
                                    sgState === "3_boost"
                                        ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 animate-pulse"
                                        : relayState
                                        ? "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30"
                                        : "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20"
                                }`}>
                                    {sgState === "3_boost"
                                        ? "☀️ SG-Ready Boost"
                                        : relayState
                                        ? "🟢 Normalbetrieb"
                                        : "⚪ Standby"}
                                </span>
                            </div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                Intelligentes Lastmanagement · SG-Ready Schaltung
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={handleOpenSettings}
                            className="p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer border border-slate-200 dark:border-slate-700"
                            title="Parameter & Grenzwerte anpassen"
                        >
                            ⚙️
                        </button>
                    </div>
                </div>

                {/* Primary Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {/* Wassertemperatur */}
                    <div className="p-3.5 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 shadow-2xs">
                        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                            Wassertemperatur
                        </div>
                        <div className="text-xl font-bold font-mono text-slate-900 dark:text-white mt-1 flex items-baseline gap-1">
                            <span>{tempC.toFixed(1)}</span>
                            <span className="text-xs font-normal text-slate-500">°C</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                            Ziel: {tTarget}°C / Boost: {tBoost}°C
                        </div>
                    </div>

                    {/* Leistungsaufnahme */}
                    <div className="p-3.5 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 shadow-2xs">
                        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                            Leistung (Live)
                        </div>
                        <div className="text-xl font-bold font-mono text-slate-900 dark:text-white mt-1 flex items-baseline gap-1">
                            <span>{powerW > 0 ? powerW.toFixed(0) : "0"}</span>
                            <span className="text-xs font-normal text-slate-500">W</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                            Relais: {relayState ? "Geschlossen (AN)" : "Offen (AUS)"}
                        </div>
                    </div>

                    {/* PV-Überschuss */}
                    <div className="p-3.5 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 shadow-2xs">
                        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                            PV-Überschuss
                        </div>
                        <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-1 flex items-baseline gap-1">
                            <span>{availableSurplusW.toFixed(0)}</span>
                            <span className="text-xs font-normal text-slate-500">W</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                            Schwelle: {minSurplusW} W
                        </div>
                    </div>

                    {/* Börsenstrompreis */}
                    <div className="p-3.5 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 shadow-2xs">
                        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                            Strompreis (Effektiv)
                        </div>
                        <div className="text-xl font-bold font-mono text-amber-600 dark:text-amber-400 mt-1 flex items-baseline gap-1">
                            <span>{gridPriceCt.toFixed(1)}</span>
                            <span className="text-xs font-normal text-slate-500">ct/kWh</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                            Modus: {data.control_mode_display || "Hybrid"}
                        </div>
                    </div>
                </div>

                {/* Visual Temperature Scale Bar */}
                <div className="bg-white/80 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-700/50 space-y-2">
                    <div className="flex justify-between items-center text-xs font-medium text-slate-600 dark:text-slate-300">
                        <span>Thermischer Speicherstand ({tempC.toFixed(1)} °C)</span>
                        <span className="text-[11px] text-slate-400 font-mono">30°C – 70°C</span>
                    </div>

                    <div className="relative h-3.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                        {/* Gradient Bar */}
                        <div
                            className="h-full bg-gradient-to-r from-blue-500 via-amber-400 to-emerald-500 rounded-full transition-all duration-700"
                            style={{ width: `${tempPct}%` }}
                        />
                    </div>

                    {/* Marker Labels */}
                    <div className="relative h-4 text-[10px] text-slate-400">
                        <div
                            className="absolute -translate-x-1/2 flex flex-col items-center"
                            style={{ left: `${tMinPct}%` }}
                        >
                            <span className="text-red-500 dark:text-red-400 font-semibold">▲ {tMin}° Min</span>
                        </div>
                        <div
                            className="absolute -translate-x-1/2 flex flex-col items-center"
                            style={{ left: `${tTargetPct}%` }}
                        >
                            <span className="text-blue-500 dark:text-blue-400 font-semibold">▲ {tTarget}° Soll</span>
                        </div>
                        <div
                            className="absolute -translate-x-1/2 flex flex-col items-center"
                            style={{ left: `${tBoostPct}%` }}
                        >
                            <span className="text-emerald-500 dark:text-emerald-400 font-semibold">▲ {tBoost}° Boost</span>
                        </div>
                    </div>
                </div>

                {/* Status & Decision Banner */}
                <div className={`p-3.5 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
                    isProtectionActive
                        ? "bg-amber-500/10 border-amber-500/30 text-amber-800 dark:text-amber-200"
                        : sgState === "3_boost"
                        ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-200"
                        : "bg-slate-100 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300"
                }`}>
                    <div className="flex items-center gap-2.5">
                        <span className="text-base">
                            {isProtectionActive ? "🔒" : sgState === "3_boost" ? "☀️" : "🤖"}
                        </span>
                        <span className="font-medium leading-relaxed">{decisionReason}</span>
                    </div>

                    {/* Quick Manual Actions */}
                    <div className="flex items-center gap-1.5 shrink-0">
                        <button
                            type="button"
                            onClick={() => switchMutation.mutate({ action: "boost", duration_minutes: 60 })}
                            disabled={switchMutation.isPending}
                            className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-xs transition cursor-pointer"
                        >
                            🚀 Boost (1h)
                        </button>
                        <button
                            type="button"
                            onClick={() => switchMutation.mutate({ action: "auto" })}
                            disabled={switchMutation.isPending}
                            className="px-2.5 py-1 bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 rounded-lg text-xs font-semibold transition cursor-pointer"
                        >
                            Auto
                        </button>
                    </div>
                </div>
            </div>

            {/* Settings Modal */}
            {settingsOpen && formConfig && (
                <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 max-w-lg w-full shadow-2xl space-y-4">
                        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <span>⚙️</span>
                                <span>BWWP Lastmanagement Einstellungen</span>
                            </h3>
                            <button
                                type="button"
                                onClick={() => setSettingsOpen(false)}
                                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="space-y-3.5 max-h-[70vh] overflow-y-auto pr-1">
                            {/* Modus */}
                            <div>
                                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    Betriebsmodus
                                </label>
                                <select
                                    value={formConfig.control_mode}
                                    onChange={(e) => setFormConfig({ ...formConfig, control_mode: e.target.value })}
                                    className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-medium"
                                >
                                    <option value="hybrid">🔄 Hybrid (PV-Überschuss + Günstige Börsenstunden)</option>
                                    <option value="pv_surplus">☀️ Nur PV-Überschuss</option>
                                    <option value="spot_price">⚡ Nur Börsenstrompreis (Spotmarkt)</option>
                                    <option value="manual">✋ Manuell (Keine Automatik)</option>
                                </select>
                            </div>

                            {/* Temperaturen Grid */}
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        Mindesttemperatur (°C)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.min_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, min_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono"
                                    />
                                    <span className="text-[10px] text-slate-400">Komfortgrenze (Zwangsheizung)</span>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        Standard-Solltemp. (°C)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.target_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, target_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono"
                                    />
                                    <span className="text-[10px] text-slate-400">Wohlfühltemperatur</span>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        SG-Ready Boost (°C)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.boost_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, boost_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono"
                                    />
                                    <span className="text-[10px] text-slate-400">Thermisches Speichern</span>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        Überhitzungsschutz (°C)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.max_safety_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, max_safety_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono"
                                    />
                                    <span className="text-[10px] text-slate-400">Absoluter Abschaltschutz</span>
                                </div>
                            </div>

                            {/* Schwellenwerte */}
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        Mindest-PV-Überschuss (W)
                                    </label>
                                    <input
                                        type="number"
                                        step="50"
                                        value={formConfig.min_pv_surplus_w}
                                        onChange={(e) => setFormConfig({ ...formConfig, min_pv_surplus_w: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        Max. Preisgrenze (ct/kWh)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.max_price_threshold_ct}
                                        onChange={(e) => setFormConfig({ ...formConfig, max_price_threshold_ct: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                            <button
                                type="button"
                                onClick={() => setSettingsOpen(false)}
                                className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer"
                            >
                                Abbrechen
                            </button>
                            <button
                                type="button"
                                onClick={() => configMutation.mutate(formConfig)}
                                disabled={configMutation.isPending}
                                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md transition cursor-pointer"
                            >
                                {configMutation.isPending ? "Speichern..." : "Einstellungen speichern"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

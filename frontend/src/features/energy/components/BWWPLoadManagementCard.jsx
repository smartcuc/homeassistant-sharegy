import useModalDismiss from "../../../hooks/useModalDismiss";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function BWWPLoadManagementCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [settingsOpen, setSettingsOpen] = useState(false);
    useModalDismiss(settingsOpen, () => setSettingsOpen(false));
    const [formConfig, setFormConfig] = useState(null);

    // 1. Live BWWP Status & Configuration from Backend
    const bwwpQuery = useQuery({
        queryKey: ["bwwp-load-mgmt"],
        queryFn: () => apiFetch("/api/energy/bwwp/"),
        refetchInterval: 5000,
    });

    // 2. Devices for optional device binding selection in settings
    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
        enabled: settingsOpen,
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

    const rawName = data.device_name || "";
    const cleanTitle = (rawName && !rawName.toLowerCase().includes("aircon") && !rawName.toLowerCase().includes("ac_") && !rawName.toLowerCase().includes("bwwp"))
        ? rawName
        : t("control.warmwasser", "Warmwasser");

    const tempC = telemetry.temperature_c ?? metrics.water_temperature_c ?? 48.0;
    const powerW = telemetry.power_w ?? metrics.power_w ?? 0.0;
    const relayState = data.relay_state ?? telemetry.relay_state ?? false;
    const sgState = data.current_sg_state || "2_normal";
    const controlMode = data.control_mode || "hybrid";

    const tMin = thresholds.min_temp_c ?? 45.0;
    const tTarget = thresholds.target_temp_c ?? 52.0;
    const tBoost = thresholds.boost_temp_c ?? 60.0;
    const tMax = thresholds.max_safety_temp_c ?? 65.0;
    const minSurplusW = thresholds.min_pv_surplus_w ?? 800.0;

    const handleOpenSettings = () => {
        setFormConfig({
            device_id: data.device_id || "",
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

    // Unconfigured state
    if (data.status === "unconfigured") {
        return (
            <div className="bg-gradient-to-br from-white via-slate-50/70 to-blue-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-blue-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden flex flex-col justify-between">
                <div className="space-y-4 relative z-10">
                    <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center text-2xl shadow-xs">
                                ♨️
                            </div>
                            <div>
                                <h3 className="font-bold text-base text-slate-900 dark:text-white">
                                    {t("control.warmwasser", "Warmwasser")}
                                </h3>
                                <p className="text-xs text-slate-400 mt-0.5">
                                    {t("bwwp.no_plant_connected", "Keine Warmwasser-Anlage angebunden")}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 text-xs text-slate-500 dark:text-slate-400 text-center">
                        {t("bwwp.unconfigured_desc", "Binde deine Warmwasser-Wärmepumpe oder SG-Ready Relais ein, um Wassertemperatur und PV-Überschuss-Boost zu steuern.")}
                    </div>
                </div>

                <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-end relative z-10">
                    <button
                        type="button"
                        onClick={handleOpenSettings}
                        className="px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer bg-blue-600 hover:bg-blue-700 text-white shadow-blue-600/20 flex items-center gap-1.5"
                    >
                        <span>➕</span>
                        <span>{t("bwwp.setup_btn", "Warmwasser einrichten")}</span>
                    </button>
                </div>
            </div>
        );
    }

    const availableDevices = Array.isArray(devicesQuery.data) ? devicesQuery.data : (devicesQuery.data?.devices || []);

    return (
        <div className="bg-gradient-to-br from-white via-slate-50/70 to-blue-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-blue-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden flex flex-col justify-between">
            {/* Ambient Glow */}
            <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />

            <div className="space-y-4 relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center text-2xl shadow-xs">
                            ♨️
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="font-bold text-base text-slate-900 dark:text-white">
                                    {cleanTitle}
                                </h3>
                                <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full border ${
                                    sgState === "3_boost"
                                        ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 animate-pulse"
                                        : relayState
                                        ? "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30"
                                        : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400 border-slate-200"
                                }`}>
                                    {sgState === "3_boost"
                                        ? `☀️ ${t("bwwp.sg_ready_boost", "SG-Ready Boost")}`
                                        : relayState
                                        ? `● ${t("common.running", "Läuft aktiv")}`
                                        : `⚪ ${t("common.standby", "Standby")}`}
                                </span>
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                {t("bwwp.subtitle", "Intelligente SG-Ready Warmwasser-Steuerung & Speicher-Boost")}
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={handleOpenSettings}
                        className="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer border border-slate-200/80 dark:border-slate-700 shadow-2xs"
                        title={t("bwwp.settings_tooltip", "Schwellwerte & Solltemperaturen anpassen")}
                    >
                        ⚙️
                    </button>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">{t("bwwp.water_temp", "Wassertemperatur")}</div>
                        <div className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 flex items-baseline justify-between">
                            <span>{tempC.toFixed(1)} °C</span>
                            <span className="text-xs font-normal text-slate-400 font-sans">{t("bwwp.target_short", "Soll")}: {tTarget}°C</span>
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">{t("bwwp.heating_power", "Heizleistung (Live)")}</div>
                        <div className="text-lg font-bold font-mono text-blue-600 dark:text-blue-400 mt-0.5">
                            {powerW > 0 ? `${powerW.toFixed(0)} W` : relayState ? "650 W" : "0 W"}
                        </div>
                    </div>
                </div>

                {/* Mode / Strategy Strip */}
                <div className="p-3 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                        <div className="font-bold text-slate-800 dark:text-slate-200 truncate">🔄 {t("bwwp.control_mode_title", "Regelungsmodus")}</div>
                        <div className="text-[11px] text-slate-400 truncate">
                            {controlMode === "pv_surplus" ? t("control.pv_only", "Nur PV-Überschuss") : controlMode === "spot_price" ? t("bwwp.mode_spot_price", "Spotmarkt-Preisführung") : t("bwwp.mode_hybrid", "Hybrid (PV + Günstige Börsenpreise)")}
                        </div>
                    </div>
                    <span className="font-mono text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-1 rounded-xl border border-blue-200 dark:border-blue-800 shrink-0">
                        {t("bwwp.from_pv_threshold", { val: minSurplusW, defaultValue: `ab ${minSurplusW} W PV` })}
                    </span>
                </div>
            </div>

            {/* Actions */}
            <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-3 relative z-10">
                <span className="text-xs text-slate-400">
                    {t("common.status", "Status")}: <strong className="text-blue-600 dark:text-blue-400">{sgState === "3_boost" ? t("bwwp.status_boost_active", "SG-Boost aktiv") : relayState ? t("bwwp.status_heating_normal", "Heizt normal") : t("common.standby", "Standby")}</strong>
                </span>
                <div className="flex items-center gap-2">
                    <button
                        type="button"
                        onClick={() => switchMutation.mutate({ action: sgState === "3_boost" ? "auto" : "boost", duration_minutes: 60 })}
                        disabled={switchMutation.isPending}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer ${
                            sgState === "3_boost"
                                ? "bg-slate-200 hover:bg-slate-300 text-slate-800 dark:bg-slate-800 dark:text-slate-200"
                                : "bg-blue-600 hover:bg-blue-700 text-white shadow-blue-600/20"
                        }`}
                    >
                        {sgState === "3_boost" ? `⏹️ ${t("bwwp.end_boost_btn", "Boost beenden")}` : `🚀 ${t("bwwp.start_boost_btn", "SG-Ready Boost (1h)")}`}
                    </button>
                </div>
            </div>

            {/* Settings Modal */}
            {settingsOpen && formConfig && (
                <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4" onClick={() => setSettingsOpen(false)}>
                    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 max-w-lg w-full shadow-2xl space-y-4 max-h-[90vh] flex flex-col overflow-hidden" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 shrink-0">
                            <div>
                                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>⚙️</span>
                                    <span>{t("bwwp.modal_title", "BWWP Lastmanagement Einstellungen")}</span>
                                </h3>
                                <p className="text-xs text-slate-400 mt-0.5">
                                    {t("bwwp.modal_subtitle", "Definiere Solltemperaturen, PV-Schwellen und Betriebsmodi.")}
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={() => setSettingsOpen(false)}
                                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="space-y-3.5 overflow-y-auto pr-1 flex-1">
                            {/* Gerät / Aktor Zuordnung */}
                            {availableDevices.length > 0 && (
                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        {t("bwwp.linked_device_label", "Verknüpftes Gerät / Aktor")}
                                    </label>
                                    <select
                                        value={formConfig.device_id || ""}
                                        onChange={(e) => setFormConfig({ ...formConfig, device_id: e.target.value })}
                                        className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white"
                                    >
                                        <option value="">{t("bwwp.default_device", "-- Standardgerät --")}</option>
                                        {availableDevices.map((d) => (
                                            <option key={d.id} value={d.id}>
                                                {d.name || d.identifier}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {/* Modus */}
                            <div>
                                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    {t("bwwp.operating_mode_label", "Betriebsmodus")}
                                </label>
                                <select
                                    value={formConfig.control_mode}
                                    onChange={(e) => setFormConfig({ ...formConfig, control_mode: e.target.value })}
                                    className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white"
                                >
                                    <option value="hybrid">🔄 {t("bwwp.opt_hybrid", "Hybrid (PV-Überschuss + Günstige Börsenstunden)")}</option>
                                    <option value="pv_surplus">☀️ {t("bwwp.opt_pv_only", "Nur PV-Überschuss")}</option>
                                    <option value="spot_price">⚡ {t("bwwp.opt_spot_price", "Nur Börsenstrompreis (Spotmarkt)")}</option>
                                    <option value="manual">✋ {t("bwwp.opt_manual", "Manuell (Keine Automatik)")}</option>
                                </select>
                            </div>

                            {/* Temperaturen Grid */}
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        {t("bwwp.min_temp_label", "Mindesttemperatur (°C)")}
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.min_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, min_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                    />
                                    <span className="text-[10px] text-slate-400">{t("bwwp.comfort_limit", "Komfortgrenze (Zwangsheizung)")}</span>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        {t("bwwp.standard_target_temp_label", "Standard-Solltemp. (°C)")}
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.target_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, target_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                    />
                                    <span className="text-[10px] text-slate-400">{t("bwwp.target_feel_good", "Wohlfühltemperatur")}</span>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        {t("bwwp.boost_temp_label", "SG-Ready Boost (°C)")}
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.boost_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, boost_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                    />
                                    <span className="text-[10px] text-slate-400">{t("bwwp.thermal_storage", "Thermisches Speichern")}</span>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        {t("bwwp.max_safety_temp_label", "Überhitzungsschutz (°C)")}
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.max_safety_temp_c}
                                        onChange={(e) => setFormConfig({ ...formConfig, max_safety_temp_c: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                    />
                                    <span className="text-[10px] text-slate-400">{t("bwwp.absolute_cutoff", "Absoluter Abschaltschutz")}</span>
                                </div>
                            </div>

                            {/* Schwellenwerte */}
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        {t("bwwp.min_pv_surplus_label", "Mindest-PV-Überschuss (W)")}
                                    </label>
                                    <input
                                        type="number"
                                        step="50"
                                        value={formConfig.min_pv_surplus_w}
                                        onChange={(e) => setFormConfig({ ...formConfig, min_pv_surplus_w: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                        {t("bwwp.max_price_threshold_label", "Max. Preisgrenze (ct/kWh)")}
                                    </label>
                                    <input
                                        type="number"
                                        step="0.5"
                                        value={formConfig.max_price_threshold_ct}
                                        onChange={(e) => setFormConfig({ ...formConfig, max_price_threshold_ct: parseFloat(e.target.value) })}
                                        className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800 shrink-0">
                            <button
                                type="button"
                                onClick={() => setSettingsOpen(false)}
                                className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer"
                            >
                                {t("common.cancel", "Abbrechen")}
                            </button>
                            <button
                                type="button"
                                onClick={() => configMutation.mutate(formConfig)}
                                disabled={configMutation.isPending}
                                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md transition cursor-pointer"
                            >
                                {configMutation.isPending ? t("common.saving", "Speichern...") : t("common.save_settings", "Einstellungen speichern")}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

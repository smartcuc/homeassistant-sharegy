import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../api/client";
import { useTranslation } from "react-i18next";

export default function DeviceBaselineModal({ device, isOpen, onClose }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [applianceType, setApplianceType] = useState("generic");
    const [standbyPower, setStandbyPower] = useState(30.0);
    const [standbyMax, setStandbyMax] = useState(45.0);
    const [operatingMin, setOperatingMin] = useState(350.0);
    const [operatingMax, setOperatingMax] = useState(750.0);
    const [maxRunHours, setMaxRunHours] = useState(6.0);
    const [isActive, setIsActive] = useState(true);
    const [statusMsg, setStatusMsg] = useState(null);

    // 1. Profil laden
    const { data: profileData, isLoading, refetch } = useQuery({
        queryKey: ["device-baseline-profile", device?.id],
        queryFn: () => apiFetch(`/api/devices/${device.id}/profile/`),
        enabled: Boolean(isOpen && device?.id),
    });

    useEffect(() => {
        if (profileData) {
            setApplianceType(profileData.appliance_type || "generic");
            setStandbyPower(profileData.standby_power_w ?? 30.0);
            setStandbyMax(profileData.standby_max_w ?? 45.0);
            setOperatingMin(profileData.operating_power_min_w ?? 350.0);
            setOperatingMax(profileData.operating_power_max_w ?? 750.0);
            setMaxRunHours(profileData.max_continuous_run_hours ?? 6.0);
            setIsActive(profileData.is_active ?? true);
        }
    }, [profileData]);

    // 2. Preset wählen
    const handlePresetChange = (presetKey) => {
        setApplianceType(presetKey);
        const preset = profileData?.presets?.[presetKey];
        if (preset) {
            setStandbyPower(preset.standby_power_w);
            setStandbyMax(preset.standby_max_w);
            setOperatingMin(preset.operating_power_min_w);
            setOperatingMax(preset.operating_power_max_w);
            setMaxRunHours(preset.max_continuous_run_hours);
            setStatusMsg({ type: "info", text: `Preset "${preset.label}" angewendet.` });
        }
    };

    // 3. Speichern Mutation
    const saveMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch(`/api/devices/${device.id}/profile/`, {
                method: "POST",
                body: JSON.stringify(payload),
            }),
        onSuccess: (res) => {
            queryClient.invalidateQueries(["device-baseline-profile", device.id]);
            queryClient.invalidateQueries(["devices"]);
            queryClient.invalidateQueries(["alerts-list"]);
            setStatusMsg({ type: "success", text: "✅ Baseline-Profil erfolgreich gespeichert!" });
        },
        onError: (err) => {
            setStatusMsg({ type: "error", text: `Fehler beim Speichern: ${err.message}` });
        },
    });

    // 4. Auto-Learning Mutation
    const learnMutation = useMutation({
        mutationFn: () =>
            apiFetch(`/api/devices/${device.id}/profile/learn/`, {
                method: "POST",
                body: JSON.stringify({ days: 7 }),
            }),
        onSuccess: (res) => {
            setStandbyPower(res.standby_power_w);
            setStandbyMax(res.standby_max_w);
            setOperatingMin(res.operating_power_min_w);
            setOperatingMax(res.operating_power_max_w);
            queryClient.invalidateQueries(["device-baseline-profile", device.id]);
            setStatusMsg({ type: "success", text: `🧠 ${res.message}` });
        },
        onError: (err) => {
            setStatusMsg({ type: "error", text: `Fehler beim Lernen: ${err.message}` });
        },
    });

    if (!isOpen || !device) return null;

    const isAnomaly = profileData?.current_health_status === "anomaly";
    const devName = device.config?.custom_name || device.name || device.identifier;

    return (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl shadow-2xl max-w-xl w-full p-6 animate-in fade-in zoom-in-95 space-y-5 max-h-[90vh] overflow-y-auto">
                {/* MODAL HEADER */}
                <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
                    <div className="flex items-center gap-2.5">
                        <span className="text-2xl">🧠</span>
                        <div>
                            <h3 className="font-extrabold text-base text-gray-900 dark:text-white">
                                Geräteprofil & Baseline-Überwachung
                            </h3>
                            <p className="text-xs text-gray-500">{devName}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 text-lg cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* CURRENT HEALTH BANNER */}
                <div className={`p-4 rounded-2xl border text-xs flex items-start gap-3 ${
                    isAnomaly
                        ? "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-900 dark:text-rose-200"
                        : "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200"
                }`}>
                    <span className="text-xl shrink-0">{isAnomaly ? "🚨" : "🟢"}</span>
                    <div className="space-y-1">
                        <div className="font-bold flex items-center gap-2">
                            <span>Status: {isAnomaly ? "Anomalie / Abweichung erkannt!" : "Normal / Baseline eingehalten"}</span>
                        </div>
                        {isAnomaly && profileData?.anomaly_reason && (
                            <p className="opacity-90">{profileData.anomaly_reason}</p>
                        )}
                        {!isAnomaly && (
                            <p className="opacity-80">
                                Gerät arbeitet innerhalb der definierten Toleranz (Standby: {profileData?.standby_power_w ?? 30} W, Obergrenze: {profileData?.standby_max_w ?? 45} W).
                            </p>
                        )}
                    </div>
                </div>

                {statusMsg && (
                    <div className={`p-3 rounded-xl text-xs font-semibold ${
                        statusMsg.type === "success" ? "bg-emerald-100 text-emerald-800" :
                        statusMsg.type === "error" ? "bg-rose-100 text-rose-800" :
                        "bg-indigo-50 text-indigo-800"
                    }`}>
                        {statusMsg.text}
                    </div>
                )}

                {/* PRESET SELECTOR & AUTO LEARN */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <label className="text-xs font-bold text-gray-700 dark:text-gray-300">
                            Gerätetyp / Preset-Vorlage
                        </label>
                        <button
                            type="button"
                            onClick={() => learnMutation.mutate()}
                            disabled={learnMutation.isLoading}
                            className="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1 cursor-pointer"
                        >
                            <span>✨</span>
                            <span>{learnMutation.isLoading ? "Berechne..." : "Aus Daten lernen (7 Tage)"}</span>
                        </button>
                    </div>

                    <select
                        value={applianceType}
                        onChange={(e) => handlePresetChange(e.target.value)}
                        className="w-full text-xs font-semibold p-2.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-200"
                    >
                        <option value="bwwp">🚿 Brauchwasserwärmepumpe (BWWP - Standby 30W, Betrieb 500W)</option>
                        <option value="heatpump">♨️ Heizungs-Wärmepumpe (Standby 45W, Betrieb 600-4000W)</option>
                        <option value="fridge">🧊 Kühlschrank / Gefriertruhe (Standby 2W, Betrieb 40-180W)</option>
                        <option value="circulation_pump">🔄 Zirkulationspumpe (Standby 0.5W, Betrieb 10-50W)</option>
                        <option value="heating_pump">⚡ Umwälz- / Heizungspumpe (Standby 2W, Betrieb 10-60W)</option>
                        <option value="generic">⚙️ Individuelles Gerät / Manuelle Schwellenwerte</option>
                    </select>
                </div>

                {/* THRESHOLD CONTROLS */}
                <div className="grid grid-cols-2 gap-3 pt-2">
                    {/* Standby Power */}
                    <div className="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-xl border border-gray-100 dark:border-slate-800">
                        <label className="block text-[11px] font-bold text-gray-500 uppercase">
                            Ruhe-Baseline (Standby)
                        </label>
                        <div className="flex items-center gap-2 mt-1">
                            <input
                                type="number"
                                step="0.5"
                                value={standbyPower}
                                onChange={(e) => setStandbyPower(parseFloat(e.target.value) || 0)}
                                className="w-full text-xs font-bold p-1.5 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                            />
                            <span className="text-xs font-bold text-gray-400">W</span>
                        </div>
                        <span className="text-[10px] text-gray-400">Soll-Ruhezustand</span>
                    </div>

                    {/* Standby Max Alarm Threshold */}
                    <div className="p-3 bg-rose-50/50 dark:bg-rose-950/20 rounded-xl border border-rose-100 dark:border-rose-900/40">
                        <label className="block text-[11px] font-bold text-rose-700 dark:text-rose-400 uppercase">
                            Standby-Alarm ab
                        </label>
                        <div className="flex items-center gap-2 mt-1">
                            <input
                                type="number"
                                step="0.5"
                                value={standbyMax}
                                onChange={(e) => setStandbyMax(parseFloat(e.target.value) || 0)}
                                className="w-full text-xs font-bold p-1.5 rounded-lg border border-rose-200 dark:border-rose-800 bg-white dark:bg-slate-900 text-rose-700"
                            />
                            <span className="text-xs font-bold text-rose-400">W</span>
                        </div>
                        <span className="text-[10px] text-rose-400">Alarmierung bei Überschreitung</span>
                    </div>

                    {/* Operating Range */}
                    <div className="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-xl border border-gray-100 dark:border-slate-800">
                        <label className="block text-[11px] font-bold text-gray-500 uppercase">
                            Betriebsleistung Min
                        </label>
                        <div className="flex items-center gap-2 mt-1">
                            <input
                                type="number"
                                step="10"
                                value={operatingMin}
                                onChange={(e) => setOperatingMin(parseFloat(e.target.value) || 0)}
                                className="w-full text-xs font-bold p-1.5 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                            />
                            <span className="text-xs font-bold text-gray-400">W</span>
                        </div>
                        <span className="text-[10px] text-gray-400">Kompressor / Pumpe an</span>
                    </div>

                    {/* Max Run Hours */}
                    <div className="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-xl border border-gray-100 dark:border-slate-800">
                        <label className="block text-[11px] font-bold text-gray-500 uppercase">
                            Max. Dauerlaufzeit
                        </label>
                        <div className="flex items-center gap-2 mt-1">
                            <input
                                type="number"
                                step="0.5"
                                value={maxRunHours}
                                onChange={(e) => setMaxRunHours(parseFloat(e.target.value) || 0)}
                                className="w-full text-xs font-bold p-1.5 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                            />
                            <span className="text-xs font-bold text-gray-400">Std.</span>
                        </div>
                        <span className="text-[10px] text-gray-400">Schutz vor Vereisung/Defekt</span>
                    </div>
                </div>

                {/* ACTIVE TOGGLE & ACTION BUTTONS */}
                <div className="pt-3 border-t border-gray-100 dark:border-slate-800 flex items-center justify-between">
                    <label className="flex items-center gap-2 text-xs font-bold text-gray-700 dark:text-gray-300 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={isActive}
                            onChange={(e) => setIsActive(e.target.checked)}
                            className="rounded text-indigo-600 cursor-pointer"
                        />
                        <span>Baseline-Überwachung aktiv</span>
                    </label>

                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-bold text-gray-500 hover:text-gray-700 cursor-pointer"
                        >
                            Schließen
                        </button>
                        <button
                            type="button"
                            onClick={() =>
                                saveMutation.mutate({
                                    appliance_type: applianceType,
                                    standby_power_w: standbyPower,
                                    standby_max_w: standbyMax,
                                    operating_power_min_w: operatingMin,
                                    operating_power_max_w: operatingMax,
                                    max_continuous_run_hours: maxRunHours,
                                    is_active: isActive,
                                })
                            }
                            disabled={saveMutation.isLoading}
                            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition shadow-xs cursor-pointer"
                        >
                            {saveMutation.isLoading ? "Speichere..." : "Baseline aktivieren →"}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

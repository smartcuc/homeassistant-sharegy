import useModalDismiss from "../../../hooks/useModalDismiss";
/*
# src/features/producer/components/StorageSystemModal.jsx
*/

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function StorageSystemModal({ isOpen, onClose, storage, onSaved }) {
    const { t } = useTranslation();
    useModalDismiss(open, onClose);
    const isEdit = Boolean(storage);

    // Auto-Discovery und Geräteliste laden
    const detectQuery = useQuery({
        queryKey: ["storage-detect"],
        queryFn: () => apiFetch("/api/producer/storage/detect/"),
        enabled: isOpen,
    });

    const devices = detectQuery.data?.devices || [];
    const candidates = detectQuery.data?.candidates || [];

    // Mode: "all_in_one" vs "separated"
    const [mode, setMode] = useState("all_in_one");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    const [formData, setFormData] = useState({
        name: "Hausspeicher",
        capacity_kwh: 10.0,
        max_charge_power_kw: 5.0,
        max_discharge_power_kw: 5.0,
        min_soc_reserve_pct: 10.0,
        max_soc_pct: 100.0,
        charge_efficiency_pct: 95.0,
        discharge_efficiency_pct: 95.0,
        primary_device_id: "",
        soc_device_id: "",
        soc_metric_key: "soc",
        power_device_id: "",
        power_metric_key: "power",
        current_device_id: "",
        current_metric_key: "battery_current",
        charge_energy_device_id: "",
        charge_energy_metric_key: "energy_in",
        discharge_energy_device_id: "",
        discharge_energy_metric_key: "energy_out",
        active: true,
        ems_control_enabled: true,
        control_mode: "self_consumption",
        target_charge_power_kw: 3.0,
        price_threshold_ct: 15.0,
    });

    useEffect(() => {
        if (storage) {
            setFormData({
                name: storage.name || "Hausspeicher",
                capacity_kwh: storage.capacity_kwh || 10.0,
                max_charge_power_kw: storage.max_charge_power_kw || 5.0,
                max_discharge_power_kw: storage.max_discharge_power_kw || 5.0,
                min_soc_reserve_pct: storage.min_soc_reserve_pct || 10.0,
                max_soc_pct: storage.max_soc_pct || 100.0,
                charge_efficiency_pct: storage.charge_efficiency_pct || 95.0,
                discharge_efficiency_pct: storage.discharge_efficiency_pct || 95.0,
                primary_device_id: storage.primary_device?.id || storage.primary_device_id || "",
                soc_device_id: storage.soc_device?.id || storage.soc_device_id || "",
                soc_metric_key: storage.soc_metric_key || "soc",
                power_device_id: storage.power_device?.id || storage.power_device_id || "",
                power_metric_key: storage.power_metric_key || "power",
                current_device_id: storage.current_device?.id || storage.current_device_id || "",
                current_metric_key: storage.current_metric_key || "battery_current",
                charge_energy_device_id: storage.charge_energy_device?.id || storage.charge_energy_device_id || "",
                charge_energy_metric_key: storage.charge_energy_metric_key || "energy_in",
                discharge_energy_device_id: storage.discharge_energy_device?.id || storage.discharge_energy_device_id || "",
                discharge_energy_metric_key: storage.discharge_energy_metric_key || "energy_out",
                active: storage.active ?? true,
                ems_control_enabled: storage.ems_control_enabled ?? true,
                control_mode: storage.control_mode || "self_consumption",
                target_charge_power_kw: storage.target_charge_power_kw ?? 3.0,
                price_threshold_ct: storage.price_threshold_ct ?? 15.0,
            });

            if (storage.soc_device_id && storage.power_device_id && storage.soc_device_id !== storage.power_device_id) {
                setMode("separated");
            } else {
                setMode("all_in_one");
            }
        }
    }, [storage, isOpen]);

    if (!isOpen) return null;

    const handleApplyCandidate = (candidate) => {
        setFormData((prev) => ({
            ...prev,
            primary_device_id: candidate.device.id,
            soc_device_id: candidate.device.id,
            power_device_id: candidate.device.id,
            current_device_id: candidate.device.id,
            soc_metric_key: candidate.suggested_soc_metric || "soc",
            power_metric_key: candidate.suggested_power_metric || "power",
            current_metric_key: candidate.suggested_current_metric || "battery_current",
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg("");
        setIsSubmitting(true);

        try {
            const payload = {
                ...formData,
                capacity_kwh: parseFloat(formData.capacity_kwh),
                max_charge_power_kw: parseFloat(formData.max_charge_power_kw),
                max_discharge_power_kw: parseFloat(formData.max_discharge_power_kw),
                min_soc_reserve_pct: parseFloat(formData.min_soc_reserve_pct),
                max_soc_pct: parseFloat(formData.max_soc_pct),
                charge_efficiency_pct: parseFloat(formData.charge_efficiency_pct),
                discharge_efficiency_pct: parseFloat(formData.discharge_efficiency_pct),
                target_charge_power_kw: parseFloat(formData.target_charge_power_kw || 3.0),
                price_threshold_ct: parseFloat(formData.price_threshold_ct || 15.0),
                ems_control_enabled: Boolean(formData.ems_control_enabled),
                control_mode: formData.control_mode || "self_consumption",
            };

            if (mode === "all_in_one" && formData.primary_device_id) {
                payload.soc_device_id = formData.primary_device_id;
                payload.power_device_id = formData.primary_device_id;
            } else if (mode === "separated") {
                payload.primary_device_id = null;
            }

            if (isEdit) {
                await apiFetch(`/api/producer/storage/${storage.id}/`, {
                    method: "PATCH",
                    body: JSON.stringify(payload),
                });
            } else {
                await apiFetch("/api/producer/storage/create/", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });
            }

            if (onSaved) onSaved();
            onClose();
        } catch (err) {
            setErrorMsg(err.message || "Fehler beim Speichern des Speichersystems.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div 
            className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/75 backdrop-blur-xs animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div 
                className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 w-full max-w-2xl max-h-[92vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-800/60 shrink-0">
                    <div className="flex items-center gap-3">
                        <span className="text-xl sm:text-2xl p-2 sm:p-2.5 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 rounded-2xl border border-emerald-200 dark:border-emerald-800/60 shadow-2xs">🔋</span>
                        <div>
                            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                                {isEdit ? t("storage.edit_title", "Batteriespeicher bearbeiten") : t("storage.add_title", "Neuen Batteriespeicher anlegen")}
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("storage.modal_subtitle", "Definiere Kapazität, Ladelimits und ordne Messpunkte flexibel zu.")}
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                        aria-label={t("common.close", "Schließen")}
                    >
                        ✕
                    </button>
                </div>

                {/* Form Body */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-5">
                    {errorMsg && (
                        <div className="p-3.5 bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-rose-700 dark:text-rose-300 text-xs font-semibold rounded-2xl">
                            ⚠️ {errorMsg}
                        </div>
                    )}

                    {/* Auto-Discovery Suggestion Banner */}
                    {!isEdit && candidates.length > 0 && (
                        <div className="p-4 bg-emerald-50/80 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 rounded-2xl space-y-2">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                                    <span>💡</span> {t("storage_system.detected_storage", "Erkannter Speicher aus Plugin / Wechselrichter")}
                                </span>
                                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-200/60 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300">
                                    {t("storage_system.auto_discovery", "Auto-Discovery")}
                                </span>
                            </div>
                            <p className="text-xs text-emerald-800/90 dark:text-emerald-300/80 leading-relaxed">
                                {t("storage_system.detected_desc", { name: candidates[0].device.name, defaultValue: `Es wurde ein Gerät mit Speicher-Metriken (SoC/Leistung) gefunden: ${candidates[0].device.name}.` })}
                            </p>
                            <button
                                type="button"
                                onClick={() => handleApplyCandidate(candidates[0])}
                                className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                            >
                                {t("storage_system.apply_suggestion", "✨ Vorschlag mit 1-Klick übernehmen")}
                            </button>
                        </div>
                    )}

                    {/* Basic Info */}
                    <div className="space-y-3.5">
                        <h3 className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                            {t("storage_system.section_general", "1. Allgemeine Angaben & Kapazität")}
                        </h3>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                            <div>
                                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                                    {t("common.name", "Bezeichnung")} *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                                    {t("storage_system.capacity_kwh", "Nennkapazität (kWh)")} *
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0.5"
                                    max="500"
                                    required
                                    value={formData.capacity_kwh}
                                    onChange={(e) => setFormData({ ...formData, capacity_kwh: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm font-mono font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <div>
                                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    {t("storage_system.max_charge_power_kw", "Max. Laden (kW)")}
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.max_charge_power_kw}
                                    onChange={(e) => setFormData({ ...formData, max_charge_power_kw: e.target.value })}
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    {t("storage_system.max_discharge_power_kw", "Max. Entladen (kW)")}
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.max_discharge_power_kw}
                                    onChange={(e) => setFormData({ ...formData, max_discharge_power_kw: e.target.value })}
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    {t("storage_system.min_soc_pct", "Min. Reserve (%)")}
                                </label>
                                <input
                                    type="number"
                                    step="1"
                                    min="0"
                                    max="100"
                                    value={formData.min_soc_reserve_pct}
                                    onChange={(e) => setFormData({ ...formData, min_soc_reserve_pct: e.target.value })}
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    {t("storage_system.max_soc_pct", "Max. SoC (%)")}
                                </label>
                                <input
                                    type="number"
                                    step="1"
                                    min="50"
                                    max="100"
                                    value={formData.max_soc_pct}
                                    onChange={(e) => setFormData({ ...formData, max_soc_pct: e.target.value })}
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>
                        </div>
                    </div>

                    {/* EMS Control */}
                    <div className="space-y-3.5 pt-4 border-t border-slate-100 dark:border-slate-800">
                        <div className="flex items-center justify-between">
                            <h3 className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                                {t("storage_system.section_control", "2. Intelligente EMS-Steuerung & Fahrplan")}
                            </h3>

                            <label className="flex items-center gap-2 text-xs cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={formData.ems_control_enabled}
                                    onChange={(e) => setFormData({ ...formData, ems_control_enabled: e.target.checked })}
                                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                                />
                                <span className={formData.ems_control_enabled ? "text-emerald-700 dark:text-emerald-400 font-bold" : "text-slate-500"}>
                                    {t("storage_system.control_active", "Steuerung aktiv")}
                                </span>
                            </label>
                        </div>

                        {formData.ems_control_enabled && (
                            <div className="p-4 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 space-y-3">
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                    <div>
                                        <label className="block text-[11px] font-bold text-indigo-950 dark:text-indigo-300 uppercase tracking-wider mb-1">
                                            {t("storage_system.control_mode_label", "Betriebsmodus")}
                                        </label>
                                        <select
                                            value={formData.control_mode}
                                            onChange={(e) => setFormData({ ...formData, control_mode: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 transition"
                                        >
                                            <option value="self_consumption">☀️ {t("storage_system.mode_self_consumption", "PV-Autarkie (Autonom)")}</option>
                                            <option value="price_optimized">💶 {t("storage_system.mode_price_optimized", "Preisgeführt (EPEX Spot / Tibber)")}</option>
                                            <option value="forced_charge">⚡ {t("storage_system.mode_forced_charge", "Manuelle Zwangsladung")}</option>
                                            <option value="idle">💤 {t("storage_system.mode_idle", "Standby / Ladesperre")}</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-indigo-950 dark:text-indigo-300 uppercase tracking-wider mb-1">
                                            {t("storage_system.target_power_label", "Soll-Ladeleistung (kW)")}
                                        </label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            min="0.5"
                                            max={formData.max_charge_power_kw || 15}
                                            value={formData.target_charge_power_kw}
                                            onChange={(e) => setFormData({ ...formData, target_charge_power_kw: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-mono font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 transition"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-indigo-950 dark:text-indigo-300 uppercase tracking-wider mb-1">
                                            {t("storage_system.price_threshold_label", "Preisschwelle (ct/kWh)")}
                                        </label>
                                        <input
                                            type="number"
                                            step="0.5"
                                            value={formData.price_threshold_ct}
                                            onChange={(e) => setFormData({ ...formData, price_threshold_ct: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-mono font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 transition"
                                        />
                                    </div>
                                </div>
                                <p className="text-[11px] text-indigo-800/90 dark:text-indigo-300/80 leading-relaxed">
                                    {t("storage_system.price_mode_hint", "Bei Preisgeführt lädt Sharegy den Batteriespeicher bei dynamischen Tarifen (z. B. Tibber) automatisch aus dem Netz auf, sobald der Börsenstrompreis unter die Preisschwelle fällt.")}
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Signal & Measurement Point Routing */}
                    <div className="space-y-3.5 pt-4 border-t border-slate-100 dark:border-slate-800">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                            <h3 className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                                {t("storage_system.section_sensors", "3. Messpunkt- & Sensor-Zuordnung")}
                            </h3>

                            {/* Mode Toggle */}
                            <div className="inline-flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl text-xs font-semibold">
                                <button
                                    type="button"
                                    onClick={() => setMode("all_in_one")}
                                    className={`px-3 py-1 rounded-lg transition cursor-pointer ${mode === "all_in_one" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold" : "text-slate-500 dark:text-slate-400"}`}
                                >
                                    {t("storage_system.mode_all_in_one", "🎯 All-in-One (Ein Gerät)")}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setMode("separated")}
                                    className={`px-3 py-1 rounded-lg transition cursor-pointer ${mode === "separated" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold" : "text-slate-500 dark:text-slate-400"}`}
                                >
                                    {t("storage_system.mode_separated", "🔀 Getrennte Messpunkte")}
                                </button>
                            </div>
                        </div>

                        {mode === "all_in_one" ? (
                            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-3">
                                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                                    {t("storage_system.select_primary_device", "Hauptgerät auswählen (z. B. Hybrid-Wechselrichter oder All-in-One Speicher)")}
                                </label>
                                <select
                                    value={formData.primary_device_id}
                                    onChange={(e) => setFormData({ ...formData, primary_device_id: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                >
                                    <option value="">{t("storage_system.no_device_manual", "-- Kein Gerät verknüpft (Manuell) --")}</option>
                                    {devices.map((d) => (
                                        <option key={d.id} value={d.id}>
                                            {d.name} {d.has_soc ? t("storage_system.with_soc_sensor", "(mit SoC-Sensor)") : ""}
                                        </option>
                                    ))}
                                </select>
                                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                                    {t("storage_system.all_in_one_hint", "Das ausgewählte Gerät liefert sowohl den aktuellen Ladestand (SoC %) als auch die Lade- und Entladeleistung.")}
                                </p>
                            </div>
                        ) : (
                            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-3.5">
                                {/* SoC Device */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                                            🔋 {t("storage_system.soc_device_label", "Gerät für Ladestand (SoC %)")}
                                        </label>
                                        <select
                                            value={formData.soc_device_id}
                                            onChange={(e) => setFormData({ ...formData, soc_device_id: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                        >
                                            <option value="">{t("common.none", "-- Kein Gerät --")}</option>
                                            {devices.map((d) => (
                                                <option key={d.id} value={d.id}>
                                                    {d.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                                            {t("storage_system.metric_key_label", "Datenpunkt / Metrikschlüssel")}
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="z. B. soc, battery_soc"
                                            value={formData.soc_metric_key}
                                            onChange={(e) => setFormData({ ...formData, soc_metric_key: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                        />
                                    </div>
                                </div>

                                {/* Power Device */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                                            ⚡ {t("storage_system.power_device_label", "Gerät für Ladeleistung (W)")}
                                        </label>
                                        <select
                                            value={formData.power_device_id}
                                            onChange={(e) => setFormData({ ...formData, power_device_id: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                        >
                                            <option value="">{t("common.none", "-- Kein Gerät --")}</option>
                                            {devices.map((d) => (
                                                <option key={d.id} value={d.id}>
                                                    {d.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                                            {t("storage_system.metric_key_label", "Datenpunkt / Metrikschlüssel")}
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="z. B. power, battery_power"
                                            value={formData.power_metric_key}
                                            onChange={(e) => setFormData({ ...formData, power_metric_key: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                        />
                                    </div>
                                </div>

                                {/* Current Device */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-200/60 dark:border-slate-700/60">
                                    <div>
                                        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1 truncate">
                                            🔌 {t("storage_system.current_device_label", "Batteriestrom für Richtung (A) (Opt.)")}
                                        </label>
                                        <select
                                            value={formData.current_device_id}
                                            onChange={(e) => setFormData({ ...formData, current_device_id: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                        >
                                            <option value="">{t("common.none", "-- Optional (Kein Sensor) --")}</option>
                                            {devices.map((d) => (
                                                <option key={d.id} value={d.id}>
                                                    {d.name} {d.has_current ? "(mit Strom-Sensor)" : ""}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1 truncate">
                                            {t("storage_system.current_metric_key_label", "Strom-Datenpunkt (A)")}
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="z. B. battery_current, current"
                                            value={formData.current_metric_key}
                                            onChange={(e) => setFormData({ ...formData, current_metric_key: e.target.value })}
                                            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 transition"
                                        />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Footer Actions */}
                    <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition cursor-pointer"
                        >
                            {t("common.cancel", "Abbrechen")}
                        </button>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="px-5 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs transition cursor-pointer disabled:opacity-50"
                        >
                            {isSubmitting ? t("common.saving", "Speichere...") : isEdit ? t("storage.save_changes", "Änderungen speichern") : t("storage.create", "Speicher anlegen")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

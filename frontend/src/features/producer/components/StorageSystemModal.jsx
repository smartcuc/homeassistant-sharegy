/*
# src/features/producer/components/StorageSystemModal.jsx
*/

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function StorageSystemModal({ isOpen, onClose, storage, onSaved }) {
    const { t } = useTranslation();
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
                primary_device_id: storage.primary_device?.id || "",
                soc_device_id: storage.soc_device?.id || "",
                soc_metric_key: storage.soc_device?.metric_key || "soc",
                power_device_id: storage.power_device?.id || "",
                power_metric_key: storage.power_device?.metric_key || "power",
                current_device_id: storage.current_device?.id || "",
                current_metric_key: storage.current_device?.metric_key || "battery_current",
                charge_energy_device_id: storage.charge_energy_device?.id || "",
                charge_energy_metric_key: storage.charge_energy_device?.metric_key || "energy_in",
                discharge_energy_device_id: storage.discharge_energy_device?.id || "",
                discharge_energy_metric_key: storage.discharge_energy_device?.metric_key || "energy_out",
                active: storage.active ?? true,
            });

            if (!storage.primary_device?.id && (storage.soc_device?.id || storage.power_device?.id || storage.current_device?.id)) {
                setMode("separated");
            } else {
                setMode("all_in_one");
            }
        } else {
            // Reset for Add
            setFormData({
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
            });
            setMode("all_in_one");
        }
    }, [storage, isOpen]);

    if (!isOpen) return null;

    const handleApplyCandidate = (candidate) => {
        setFormData((prev) => ({
            ...prev,
            name: candidate.suggested_name || prev.name,
            primary_device_id: candidate.device.id,
            soc_device_id: candidate.device.id,
            soc_metric_key: candidate.suggested_soc_metric || "soc",
            power_device_id: candidate.device.id,
            power_metric_key: candidate.suggested_power_metric || "power",
            current_device_id: candidate.device.id,
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
            };

            // Im All-in-One Modus werden die Einzelzuordnungen auf das primary_device gesetzt
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
            <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 w-full max-w-2xl max-h-[92vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-slate-50">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl p-2 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-100">🔋</span>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900">
                                {isEdit ? t("storage.edit_title", "Batteriespeicher bearbeiten") : t("storage.add_title", "Neuen Batteriespeicher anlegen")}
                            </h2>
                            <p className="text-xs text-gray-500">
                                {t("storage.modal_subtitle", "Definiere Kapazität, Ladelimits und ordne Messpunkte flexibel zu.")}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-white border border-gray-200 text-gray-400 hover:text-gray-700 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Form Body */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
                    {errorMsg && (
                        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs font-semibold rounded-xl">
                            ⚠️ {errorMsg}
                        </div>
                    )}

                    {/* Auto-Discovery Suggestion Banner */}
                    {!isEdit && candidates.length > 0 && (
                        <div className="p-4 bg-emerald-50/80 border border-emerald-200 rounded-2xl space-y-2">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                                    <span>💡</span> {t("storage_system.detected_storage", "Erkannter Speicher aus Plugin / Wechselrichter")}
                                </span>
                                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-200/60 text-emerald-800">
                                    {t("storage_system.auto_discovery", "Auto-Discovery")}
                                </span>
                            </div>
                            <p className="text-xs text-emerald-800/80">
                                {t("storage_system.detected_desc", { name: candidates[0].device.name, defaultValue: `Es wurde ein Gerät mit Speicher-Metriken (SoC/Leistung) gefunden: ${candidates[0].device.name}.` })}
                            </p>
                            <button
                                type="button"
                                onClick={() => handleApplyCandidate(candidates[0])}
                                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                            >
                                {t("storage_system.apply_suggestion", "✨ Vorschlag mit 1-Klick übernehmen")}
                            </button>
                        </div>
                    )}

                    {/* Basic Info */}
                    <div className="space-y-4">
                        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                            {t("storage_system.section_general", "1. Allgemeine Angaben & Kapazität")}
                        </h3>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    {t("common.name", "Bezeichnung")} *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    {t("storage_system.nominal_capacity", "Nennkapazität (kWh)")} *
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0.5"
                                    max="500"
                                    required
                                    value={formData.capacity_kwh}
                                    onChange={(e) => setFormData({ ...formData, capacity_kwh: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <div>
                                <label className="block text-[11px] font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    {t("storage_system.max_charge_power", "Max. Laden (kW)")}
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.max_charge_power_kw}
                                    onChange={(e) => setFormData({ ...formData, max_charge_power_kw: e.target.value })}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium focus:bg-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    {t("storage_system.max_discharge_power", "Max. Entladen (kW)")}
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.max_discharge_power_kw}
                                    onChange={(e) => setFormData({ ...formData, max_discharge_power_kw: e.target.value })}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium focus:bg-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    {t("storage_system.backup_reserve", "Notstromreserve (%)")}
                                </label>
                                <input
                                    type="number"
                                    step="1"
                                    min="0"
                                    max="50"
                                    value={formData.min_soc_reserve_pct}
                                    onChange={(e) => setFormData({ ...formData, min_soc_reserve_pct: e.target.value })}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium focus:bg-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    {t("storage_system.efficiency", "Wirkungsgrad (%)")}
                                </label>
                                <input
                                    type="number"
                                    step="1"
                                    min="50"
                                    max="100"
                                    value={formData.charge_efficiency_pct}
                                    onChange={(e) => setFormData({
                                        ...formData,
                                        charge_efficiency_pct: e.target.value,
                                        discharge_efficiency_pct: e.target.value,
                                    })}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium focus:bg-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Signal & Measurement Point Routing */}
                    <div className="space-y-4 pt-4 border-t border-gray-100">
                        <div className="flex items-center justify-between">
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                                {t("storage_system.section_sensors", "2. Messpunkt- & Sensor-Zuordnung")}
                            </h3>

                            {/* Mode Toggle */}
                            <div className="inline-flex bg-gray-100 p-1 rounded-xl text-xs font-semibold">
                                <button
                                    type="button"
                                    onClick={() => setMode("all_in_one")}
                                    className={`px-3 py-1 rounded-lg transition ${mode === "all_in_one" ? "bg-white text-gray-900 shadow-xs font-bold" : "text-gray-500"}`}
                                >
                                    {t("storage_system.mode_all_in_one", "🎯 All-in-One (Ein Gerät)")}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setMode("separated")}
                                    className={`px-3 py-1 rounded-lg transition ${mode === "separated" ? "bg-white text-gray-900 shadow-xs font-bold" : "text-gray-500"}`}
                                >
                                    {t("storage_system.mode_separated", "🔀 Getrennte Messpunkte")}
                                </button>
                            </div>
                        </div>

                        {mode === "all_in_one" ? (
                            <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200 space-y-3">
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider">
                                    {t("storage_system.select_primary_device", "Hauptgerät auswählen (z. B. Hybrid-Wechselrichter oder All-in-One Speicher)")}
                                </label>
                                <select
                                    value={formData.primary_device_id}
                                    onChange={(e) => setFormData({ ...formData, primary_device_id: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-white border border-gray-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-emerald-500 transition"
                                >
                                    <option value="">{t("storage_system.no_device_manual", "-- Kein Gerät verknüpft (Manuell) --")}</option>
                                    {devices.map((d) => (
                                        <option key={d.id} value={d.id}>
                                            {d.name} {d.has_soc ? t("storage_system.with_soc_sensor", "(mit SoC-Sensor)") : ""}
                                        </option>
                                    ))}
                                </select>
                                <p className="text-[11px] text-gray-500">
                                    {t("storage_system.all_in_one_hint", "Das ausgewählte Gerät liefert sowohl den aktuellen Ladestand (SoC %) als auch die Lade- und Entladeleistung.")}
                                </p>
                            </div>
                        ) : (
                            <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200 space-y-4">
                                {/* SoC Device */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                            🔋 {t("storage_system.soc_device_label", "Gerät für Ladestand (SoC %)")}
                                        </label>
                                        <select
                                            value={formData.soc_device_id}
                                            onChange={(e) => setFormData({ ...formData, soc_device_id: e.target.value })}
                                            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-emerald-500 transition"
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
                                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                            {t("storage_system.metric_key_label", "Datenpunkt / Metrikschlüssel")}
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="z. B. soc, battery_soc"
                                            value={formData.soc_metric_key}
                                            onChange={(e) => setFormData({ ...formData, soc_metric_key: e.target.value })}
                                            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-mono font-medium focus:ring-2 focus:ring-emerald-500 transition"
                                        />
                                    </div>
                                </div>

                                {/* Power Device */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                            ⚡ {t("storage_system.power_device_label", "Gerät für Ladeleistung (W)")}
                                        </label>
                                        <select
                                            value={formData.power_device_id}
                                            onChange={(e) => setFormData({ ...formData, power_device_id: e.target.value })}
                                            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-emerald-500 transition"
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
                                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                            {t("storage_system.metric_key_label", "Datenpunkt / Metrikschlüssel")}
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="z. B. power, battery_power"
                                            value={formData.power_metric_key}
                                            onChange={(e) => setFormData({ ...formData, power_metric_key: e.target.value })}
                                            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-mono font-medium focus:ring-2 focus:ring-emerald-500 transition"
                                        />
                                    </div>
                                </div>

                                {/* Current Device (Optional for signed direction) */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-gray-200/60">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 truncate" title="Batteriestrom für Richtung (+ Entladen, - Laden)">
                                            🔌 {t("storage_system.current_device_label", "Batteriestrom für Richtung (A) (Opt.)")}
                                        </label>
                                        <select
                                            value={formData.current_device_id}
                                            onChange={(e) => setFormData({ ...formData, current_device_id: e.target.value })}
                                            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-emerald-500 transition"
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
                                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 truncate">
                                            {t("storage_system.current_metric_key_label", "Strom-Datenpunkt (A)")}
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="z. B. battery_current, current"
                                            value={formData.current_metric_key}
                                            onChange={(e) => setFormData({ ...formData, current_metric_key: e.target.value })}
                                            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-mono font-medium focus:ring-2 focus:ring-emerald-500 transition"
                                        />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Footer Actions */}
                    <div className="pt-4 border-t border-gray-100 flex items-center justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-xl transition cursor-pointer"
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


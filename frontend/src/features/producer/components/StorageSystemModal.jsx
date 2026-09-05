/*
# src/features/producer/components/StorageSystemModal.jsx
*/

import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function StorageSystemModal({ isOpen, onClose, storage, onSaved }) {
    const { t } = useTranslation();
    const isEdit = Boolean(storage);

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
                ems_control_enabled: storage.ems_control_enabled ?? true,
                control_mode: storage.control_mode || "self_consumption",
                target_charge_power_kw: storage.target_charge_power_kw ?? 3.0,
                price_threshold_ct: storage.price_threshold_ct ?? 15.0,
            });
        }
    }, [storage, isOpen]);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setErrorMsg("");

        try {
            const payload = {
                name: formData.name,
                capacity_kwh: parseFloat(formData.capacity_kwh),
                max_charge_power_kw: parseFloat(formData.max_charge_power_kw),
                max_discharge_power_kw: parseFloat(formData.max_discharge_power_kw),
                min_soc_reserve_pct: parseFloat(formData.min_soc_reserve_pct),
                max_soc_pct: parseFloat(formData.max_soc_pct),
                charge_efficiency_pct: parseFloat(formData.charge_efficiency_pct),
                discharge_efficiency_pct: parseFloat(formData.discharge_efficiency_pct),
                active: formData.active,
                ems_control_enabled: formData.ems_control_enabled,
                control_mode: formData.control_mode,
                target_charge_power_kw: parseFloat(formData.target_charge_power_kw),
                price_threshold_ct: parseFloat(formData.price_threshold_ct),
                // Preserve device bindings if already configured
                primary_device_id: formData.primary_device_id || null,
                soc_device_id: formData.soc_device_id || null,
                soc_metric_key: formData.soc_metric_key || "soc",
                power_device_id: formData.power_device_id || null,
                power_metric_key: formData.power_metric_key || "power",
                current_device_id: formData.current_device_id || null,
                current_metric_key: formData.current_metric_key || "battery_current",
                charge_energy_device_id: formData.charge_energy_device_id || null,
                charge_energy_metric_key: formData.charge_energy_metric_key || "energy_in",
                discharge_energy_device_id: formData.discharge_energy_device_id || null,
                discharge_energy_metric_key: formData.discharge_energy_metric_key || "energy_out",
            };

            if (isEdit) {
                await apiFetch(`/api/producer/storage/${storage.id}/`, {
                    method: "PATCH",
                    body: JSON.stringify(payload),
                });
            } else {
                await apiFetch("/api/producer/storage/", {
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-fade-in">
            <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 max-w-lg w-full shadow-2xl space-y-4 max-h-[90vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 shrink-0">
                    <div>
                        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>⚙️</span>
                            <span>{isEdit ? t("storage.edit_title", "Batteriespeicher bearbeiten") : t("storage.add_title", "Neuen Batteriespeicher anlegen")}</span>
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">
                            {t("storage.modal_subtitle", "Definiere Kapazität, Ladelimits und Betriebsstrategie.")}
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Form Body */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto space-y-4 pr-1">
                    {errorMsg && (
                        <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs font-semibold rounded-xl">
                            ⚠️ {errorMsg}
                        </div>
                    )}

                    {/* Section 1: Basic Info & Capacity */}
                    <div className="space-y-3">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                            1. Allgemeine Angaben & Kapazität
                        </h4>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    Bezeichnung *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    Nennkapazität (kWh) *
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0.5"
                                    max="500"
                                    required
                                    value={formData.capacity_kwh}
                                    onChange={(e) => setFormData({ ...formData, capacity_kwh: e.target.value })}
                                    className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 transition"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <div>
                                <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    Max. Laden (kW)
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.max_charge_power_kw}
                                    onChange={(e) => setFormData({ ...formData, max_charge_power_kw: e.target.value })}
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    Max. Entladen (kW)
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.max_discharge_power_kw}
                                    onChange={(e) => setFormData({ ...formData, max_discharge_power_kw: e.target.value })}
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    Notstromreserve (%)
                                </label>
                                <input
                                    type="number"
                                    step="1"
                                    min="0"
                                    max="50"
                                    value={formData.min_soc_reserve_pct}
                                    onChange={(e) => setFormData({ ...formData, min_soc_reserve_pct: e.target.value })}
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>

                            <div>
                                <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
                                    Wirkungsgrad (%)
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
                                    className="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Section 2: Active EMS & Smart Charging Control */}
                    <div className="space-y-3 pt-3 border-t border-slate-100 dark:border-slate-800">
                        <div className="flex items-center justify-between">
                            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                                <span>⚡</span> 2. Aktive EMS-Steuerung & Smart-Charging
                            </h4>
                            <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold">
                                <input
                                    type="checkbox"
                                    checked={formData.ems_control_enabled}
                                    onChange={(e) => setFormData({ ...formData, ems_control_enabled: e.target.checked })}
                                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
                                />
                                <span className={formData.ems_control_enabled ? "text-indigo-600 dark:text-indigo-400 font-bold" : "text-slate-400"}>
                                    Steuerung aktiv
                                </span>
                            </label>
                        </div>

                        {formData.ems_control_enabled && (
                            <div className="p-3.5 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-200/60 dark:border-indigo-800/50 space-y-3">
                                <div>
                                    <label className="block text-[11px] font-bold text-indigo-900 dark:text-indigo-300 uppercase tracking-wider mb-1">
                                        Betriebsmodus
                                    </label>
                                    <select
                                        value={formData.control_mode}
                                        onChange={(e) => setFormData({ ...formData, control_mode: e.target.value })}
                                        className="w-full p-2.5 bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 transition"
                                    >
                                        <option value="self_consumption">☀️ PV-Vorrang (Autarkie & Eigenverbrauch)</option>
                                        <option value="price_optimized">💶 Spotmarkt-Arbitrage (Preisgeführt)</option>
                                        <option value="forced_charge">🚀 Manuelle Zwangsladung</option>
                                        <option value="idle">💤 Standby / Ladesperre</option>
                                    </select>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-[11px] font-bold text-indigo-900 dark:text-indigo-300 uppercase tracking-wider mb-1">
                                            Soll-Ladeleistung (kW)
                                        </label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            min="0.5"
                                            max={formData.max_charge_power_kw || 15}
                                            value={formData.target_charge_power_kw}
                                            onChange={(e) => setFormData({ ...formData, target_charge_power_kw: e.target.value })}
                                            className="w-full p-2 bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-indigo-900 dark:text-indigo-300 uppercase tracking-wider mb-1">
                                            Preisschwelle (ct/kWh)
                                        </label>
                                        <input
                                            type="number"
                                            step="0.5"
                                            value={formData.price_threshold_ct}
                                            onChange={(e) => setFormData({ ...formData, price_threshold_ct: e.target.value })}
                                            className="w-full p-2 bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-mono text-slate-900 dark:text-white"
                                        />
                                    </div>
                                </div>

                                <p className="text-[11px] text-indigo-700 dark:text-indigo-300/80 leading-relaxed">
                                    Bei <strong>Spotmarkt-Arbitrage</strong> lädt Sharegy den Batteriespeicher bei dynamischen Tarifen automatisch aus dem Netz auf, sobald der Börsenstrompreis unter die Preisschwelle fällt.
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Footer Actions */}
                    <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-end gap-2 shrink-0">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition cursor-pointer"
                        >
                            {t("common.cancel", "Abbrechen")}
                        </button>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition cursor-pointer disabled:opacity-50"
                        >
                            {isSubmitting ? t("common.saving", "Speichere...") : isEdit ? t("storage.save_changes", "Änderungen speichern") : t("storage.create", "Speicher anlegen")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

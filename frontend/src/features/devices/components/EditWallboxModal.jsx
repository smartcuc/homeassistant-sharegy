import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function EditWallboxModal({ isOpen, onClose, station }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [name, setName] = useState("");
    const [maxCurrentA, setMaxCurrentA] = useState(16);
    const [minCurrentA, setMinCurrentA] = useState(6);
    const [phases, setPhases] = useState(3);
    const [smartMode, setSmartMode] = useState("pv_surplus");
    const [priceThresholdCt, setPriceThresholdCt] = useState(15.0);
    const [minSocTargetPct, setMinSocTargetPct] = useState(50);
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (station) {
            setName(station.name || "Wallbox");
            setMaxCurrentA(station.max_current_a || 16);
            setMinCurrentA(station.min_current_a || 6);
            setPhases(station.phases || 3);
            setSmartMode(station.smart_charging_mode || "pv_surplus");
            setPriceThresholdCt(station.price_threshold_ct !== undefined ? station.price_threshold_ct : 15.0);
            setMinSocTargetPct(station.min_soc_target_pct !== undefined ? station.min_soc_target_pct : 50);
            setError(null);
        }
    }, [station, isOpen]);

    if (!isOpen || !station) return null;

    const host = window.location.hostname || "sharegy.de";
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ocppWsUrl = `${wsProtocol}//${host}/ws/ocpp/${station.charge_point_id}`;

    const updateMutation = useMutation({
        mutationFn: async (payload) => {
            return apiFetch(`/api/energy/wallboxes/${station.id}/`, {
                method: "PATCH",
                body: JSON.stringify(payload),
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
            onClose();
        },
        onError: (err) => {
            setError(err.message || t("wallbox.save_error", "Fehler beim Speichern der Einstellungen."));
        },
    });

    const handleCopyUrl = async () => {
        try {
            await navigator.clipboard.writeText(ocppWsUrl);
            setCopied(true);
            setTimeout(() => setCopied(false), 3000);
        } catch (e) {
            // Fallback
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);
        updateMutation.mutate({
            name: name.trim(),
            max_current_a: Number(maxCurrentA),
            min_current_a: Number(minCurrentA),
            phases: Number(phases),
            smart_charging_mode: smartMode,
            price_threshold_ct: Number(priceThresholdCt),
            min_soc_target_pct: Number(minSocTargetPct),
        });
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs animate-fade-in">
            <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-lg w-full overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-gradient-to-r from-slate-50 to-white dark:from-slate-900 dark:to-slate-850">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl">
                            ⚙️
                        </div>
                        <div>
                            <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                                {t("wallbox.edit_title", "Wallbox-Einstellungen bearbeiten")}
                            </h3>
                            <p className="text-xs text-slate-400">
                                {station.vendor ? `${station.vendor} · ` : ""}{station.charge_point_id}
                            </p>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 flex items-center justify-center text-xs font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Form Body */}
                <form onSubmit={handleSubmit} className="p-5 sm:p-6 space-y-4 overflow-y-auto flex-1 text-xs">
                    {error && (
                        <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 rounded-2xl text-red-700 dark:text-red-300 font-medium">
                            {error}
                        </div>
                    )}

                    {/* Name */}
                    <div>
                        <label className="block text-slate-700 dark:text-slate-300 font-bold mb-1.5">
                            {t("wallbox.name_label", "Bezeichnung / Name")}
                        </label>
                        <input
                            type="text"
                            required
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder={t("wallbox.name_placeholder", "z. B. Garage Links")}
                            className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium outline-none focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 transition"
                        />
                    </div>

                    {/* Phasen & Strom */}
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-slate-700 dark:text-slate-300 font-bold mb-1.5">
                                {t("wallbox.phases_label", "Phasenanzahl")}
                            </label>
                            <select
                                value={phases}
                                onChange={(e) => setPhases(Number(e.target.value))}
                                className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium outline-none focus:border-indigo-500 transition cursor-pointer"
                            >
                                <option value={3}>{t("wallbox.phase_3", "3-phasig (400V - z. B. 11 kW / 22 kW)")}</option>
                                <option value={1}>{t("wallbox.phase_1", "1-phasig (230V - z. B. 3.7 kW)")}</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-slate-700 dark:text-slate-300 font-bold mb-1.5">
                                {t("wallbox.max_current_label", "Max. Ladestrom")}
                            </label>
                            <select
                                value={maxCurrentA}
                                onChange={(e) => setMaxCurrentA(Number(e.target.value))}
                                className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium outline-none focus:border-indigo-500 transition cursor-pointer"
                            >
                                <option value={10}>10 A ({phases === 3 ? "6.9 kW" : "2.3 kW"})</option>
                                <option value={13}>13 A ({phases === 3 ? "9.0 kW" : "3.0 kW"})</option>
                                <option value={16}>16 A ({phases === 3 ? "11.0 kW" : "3.7 kW"} - {t("wallbox.standard_hint", "Standard")})</option>
                                <option value={20}>20 A ({phases === 3 ? "13.8 kW" : "4.6 kW"})</option>
                                <option value={24}>24 A ({phases === 3 ? "16.5 kW" : "5.5 kW"})</option>
                                <option value={32}>32 A ({phases === 3 ? "22.0 kW" : "7.4 kW"})</option>
                            </select>
                        </div>
                    </div>

                    {/* Min Strom & Börsenpreis-Schwelle */}
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-slate-700 dark:text-slate-300 font-bold mb-1.5">
                                {t("wallbox.min_current_label", "Min. Ladestrom (IEC)")}
                            </label>
                            <select
                                value={minCurrentA}
                                onChange={(e) => setMinCurrentA(Number(e.target.value))}
                                className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium outline-none focus:border-indigo-500 transition cursor-pointer"
                            >
                                <option value={6}>6 A (1.4 kW / 4.1 kW - {t("wallbox.standard_hint", "Standard")})</option>
                                <option value={8}>8 A (1.8 kW / 5.5 kW)</option>
                                <option value={10}>10 A (2.3 kW / 6.9 kW)</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-slate-700 dark:text-slate-300 font-bold mb-1.5">
                                {t("wallbox.price_threshold_label", "Börsenpreis-Grenze")}
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    step="0.1"
                                    value={priceThresholdCt}
                                    onChange={(e) => setPriceThresholdCt(e.target.value)}
                                    className="w-full px-3.5 py-2.5 pr-14 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium outline-none focus:border-indigo-500 transition"
                                />
                                <span className="absolute right-3.5 top-2.5 font-bold text-slate-400">ct/kWh</span>
                            </div>
                        </div>
                    </div>

                    {/* Standard-Lademodus & Ziel-SoC */}
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-slate-700 dark:text-slate-300 font-bold mb-1.5">
                                {t("wallbox.mode_label", "Aktiver Lademodus")}
                            </label>
                            <select
                                value={smartMode}
                                onChange={(e) => setSmartMode(e.target.value)}
                                className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium outline-none focus:border-indigo-500 transition cursor-pointer"
                            >
                                <option value="pv_surplus">{t("wallbox.mode_pv_surplus", "☀️ Nur Solarüberschuss")}</option>
                                <option value="min_pv">{t("wallbox.mode_min_pv", "⛅ Min + PV-Überschuss")}</option>
                                <option value="spot_price">{t("wallbox.mode_spot_price", "💶 Börsenpreisgeführt")}</option>
                                <option value="instant">{t("wallbox.mode_instant", "⚡ Sofortladen (Max. Power)")}</option>
                                <option value="off">{t("wallbox.mode_off", "🛑 Gesperrt / Pausiert")}</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-slate-700 dark:text-slate-300 font-bold mb-1.5">
                                {t("wallbox.target_soc_label", "Mindest-Ziel-SoC")}
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    min="20"
                                    max="100"
                                    step="5"
                                    value={minSocTargetPct}
                                    onChange={(e) => setMinSocTargetPct(e.target.value)}
                                    className="w-full px-3.5 py-2.5 pr-8 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium outline-none focus:border-indigo-500 transition"
                                />
                                <span className="absolute right-3.5 top-2.5 font-bold text-slate-400">%</span>
                            </div>
                        </div>
                    </div>

                    {/* OCPP Backend Verbindungs-URL Infobox */}
                    <div className="p-3.5 bg-slate-50 dark:bg-slate-850 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-1.5">
                        <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-700 dark:text-slate-300">
                                {t("wallbox.ocpp_url_label", "OCPP 1.6-J Server URL")}
                            </span>
                            <button
                                type="button"
                                onClick={handleCopyUrl}
                                className="text-indigo-600 dark:text-indigo-400 hover:underline font-bold"
                            >
                                {copied ? t("wallbox.copied", "✓ Kopiert") : t("wallbox.copy", "Kopieren")}
                            </button>
                        </div>
                        <div className="font-mono text-[11px] text-slate-600 dark:text-slate-400 select-all break-all bg-white dark:bg-slate-900 p-2 rounded-xl border border-slate-200/80 dark:border-slate-800">
                            {ocppWsUrl}
                        </div>
                    </div>

                    {/* Submit Buttons */}
                    <div className="pt-2 flex items-center justify-end gap-2.5 border-t border-slate-100 dark:border-slate-800">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2.5 rounded-2xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-bold transition cursor-pointer"
                        >
                            {t("wallbox.cancel", "Abbrechen")}
                        </button>
                        <button
                            type="submit"
                            disabled={updateMutation.isPending}
                            className="px-5 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer flex items-center gap-1.5"
                        >
                            {updateMutation.isPending ? t("wallbox.saving", "Speichere...") : t("wallbox.save", "Änderungen speichern")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

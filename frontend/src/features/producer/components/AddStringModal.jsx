import useModalDismiss from "../../../hooks/useModalDismiss";
/*
# src/features/producer/components/AddStringModal.jsx
*/

import { useState, useEffect } from "react";
import { apiFetch } from "../../../api/client";
import { useQuery } from "@tanstack/react-query";
import { getOrientations } from "../api";
import { useTranslation } from "react-i18next";

export default function AddStringModal({
    open,
    onClose,
    generatorId,
    onCreated,
    string = null,
}) {
    const { t } = useTranslation();
    useModalDismiss(open, onClose);

    const [name, setName] = useState("");
    const [modules, setModules] = useState("");
    const [power, setPower] = useState("");
    const [orientationId, setOrientationId] = useState("");
    const [tilt, setTilt] = useState(35);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const isEdit = !!string;

    const { data: orientations = [] } =
        useQuery({
            queryKey: ["orientations"],
            queryFn: getOrientations,
        });

    useEffect(() => {
        if (!string) {
            return;
        }

        setName(string.name ?? "");
        setModules(string.module_count ?? "");
        setPower(string.peak_power_kwp ?? "");
        setOrientationId(string.orientation_id ?? "");
        setTilt(string.tilt_deg ?? 35);
    }, [string]);

    async function handleSave() {
        setIsSubmitting(true);
        try {
            const payload = {
                name,
                module_count: Number(modules),
                peak_power_kwp: String(power).replace(",", "."),
                orientation_id: orientationId,
                tilt_deg: Number(tilt),
            };

            if (isEdit) {
                await apiFetch(`/api/producer/string/${string.id}/`, {
                    method: "PATCH",
                    body: JSON.stringify(payload),
                });
            } else {
                await apiFetch("/api/producer/string/create/", {
                    method: "POST",
                    body: JSON.stringify({
                        generator_id: generatorId,
                        ...payload,
                    }),
                });
            }

            onCreated();
            onClose();
        } finally {
            setIsSubmitting(false);
        }
    }

    if (!open) {
        return null;
    }

    return (
        <div
            className="fixed inset-0 bg-slate-950/75 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div
                className="bg-white dark:bg-slate-900 rounded-3xl p-5 sm:p-6 w-full max-w-lg shadow-2xl border border-slate-200 dark:border-slate-800 animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100 dark:border-slate-800">
                    <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>☀️</span>
                        <span>
                            {isEdit
                                ? t("producers.modal_edit_string", "String bearbeiten")
                                : t("producers.modal_add_string", "String hinzufügen")}
                        </span>
                    </h2>
                    <button
                        type="button"
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                <div className="space-y-3.5">
                    <div>
                        <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1 block">
                            {t("producers.string_name_placeholder", "Name des Strings")}
                        </label>
                        <input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="z. B. Dach Süd oder Garage Ost"
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-2.5 text-xs sm:text-sm font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 transition"
                        />
                    </div>

                    <div>
                        <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1 block">
                            {t("producers.orientation_select", "Ausrichtung auswählen")}
                        </label>
                        <select
                            value={orientationId}
                            onChange={(e) => setOrientationId(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-2.5 text-xs sm:text-sm font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 transition"
                        >
                            <option value="">
                                {t("producers.orientation_select", "Ausrichtung auswählen")}
                            </option>
                            {orientations.map((orientation) => (
                                <option key={orientation.id} value={orientation.id}>
                                    {t(`orientations.${orientation.key}`, orientation.name)}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-3 gap-2 sm:gap-3">
                        <div>
                            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1 block truncate">
                                {t("producers.modules", "Module")}
                            </label>
                            <input
                                value={modules}
                                onChange={(e) => setModules(e.target.value)}
                                placeholder="z. B. 12"
                                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-2 sm:p-2.5 text-xs sm:text-sm font-mono text-slate-900 dark:text-white"
                            />
                        </div>

                        <div>
                            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1 block truncate">
                                {t("producers.power", "Leistung")} (kWp)
                            </label>
                            <input
                                value={power}
                                onChange={(e) => setPower(e.target.value)}
                                placeholder="z. B. 5.2"
                                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-2 sm:p-2.5 text-xs sm:text-sm font-mono text-slate-900 dark:text-white"
                            />
                        </div>

                        <div>
                            <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1 block truncate">
                                {t("producers.tilt_placeholder", "Neigung (°)")}
                            </label>
                            <input
                                value={tilt}
                                onChange={(e) => setTilt(e.target.value)}
                                placeholder="35"
                                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-2 sm:p-2.5 text-xs sm:text-sm font-mono text-slate-900 dark:text-white"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex justify-end gap-2.5 mt-6 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition cursor-pointer"
                    >
                        {t("common.cancel", "Abbrechen")}
                    </button>

                    <button
                        type="button"
                        onClick={handleSave}
                        disabled={isSubmitting}
                        className="px-5 py-2 text-xs font-bold bg-amber-500 hover:bg-amber-600 text-white rounded-xl shadow-xs transition cursor-pointer disabled:opacity-50"
                    >
                        {isSubmitting ? t("common.saving", "Speichere...") : t("common.save", "Speichern")}
                    </button>
                </div>
            </div>
        </div>
    );
}

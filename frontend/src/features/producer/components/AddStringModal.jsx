/*
# src/features/producer/components/AddStringModal.jsx
*/

import { useState, useEffect } from "react";
import { apiFetch } from "../../../api/client";
import { useQuery } from "@tanstack/react-query";
import { getOrientations } from "../api";
import { useTranslation } from "react-i18next";

function normalizeDecimal(value) {
    return value
        ?.toString()
        .replace(",", ".");
}

export default function AddStringModal({
    open,
    onClose,
    generatorId,
    onCreated,
    string = null,
}) {
    const { t } = useTranslation();

    const [name, setName] = useState("");
    const [modules, setModules] = useState("");
    const [power, setPower] = useState("");
    const [orientationId, setOrientationId] = useState("");
    const [tilt, setTilt] = useState(35);

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
    }

    if (!open) {
        return null;
    }

    return (
        <div
            className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl p-6 w-full max-w-lg shadow-xl"
                onClick={(e) => e.stopPropagation()}
            >
                <h2 className="text-lg font-bold text-gray-900 mb-4">
                    {isEdit
                        ? t("producers.modal_edit_string", "String bearbeiten")
                        : t("producers.modal_add_string", "String hinzufügen")}
                </h2>

                <div className="space-y-3">
                    <div>
                        <label className="text-xs font-semibold text-gray-500 mb-1 block">
                            {t("producers.string_name_placeholder", "Name des Strings")}
                        </label>
                        <input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="z. B. Dach Süd oder Garage Ost"
                            className="w-full border rounded-xl p-2.5 text-sm"
                        />
                    </div>

                    <div>
                        <label className="text-xs font-semibold text-gray-500 mb-1 block">
                            {t("producers.orientation_select", "Ausrichtung auswählen")}
                        </label>
                        <select
                            value={orientationId}
                            onChange={(e) => setOrientationId(e.target.value)}
                            className="w-full border rounded-xl p-2.5 text-sm bg-white"
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

                    <div className="grid grid-cols-3 gap-2">
                        <div>
                            <label className="text-[11px] font-semibold text-gray-500 mb-1 block truncate">
                                {t("producers.modules", "Module")}
                            </label>
                            <input
                                value={modules}
                                onChange={(e) => setModules(e.target.value)}
                                placeholder="z. B. 12"
                                className="w-full border rounded-xl p-2.5 text-sm"
                            />
                        </div>

                        <div>
                            <label className="text-[11px] font-semibold text-gray-500 mb-1 block truncate">
                                {t("producers.power", "Leistung")} (kWp)
                            </label>
                            <input
                                value={power}
                                onChange={(e) => setPower(e.target.value)}
                                placeholder="z. B. 5.2"
                                className="w-full border rounded-xl p-2.5 text-sm"
                            />
                        </div>

                        <div>
                            <label className="text-[11px] font-semibold text-gray-500 mb-1 block truncate">
                                {t("producers.tilt_placeholder", "Neigung (°)")}
                            </label>
                            <input
                                value={tilt}
                                onChange={(e) => setTilt(e.target.value)}
                                placeholder="35"
                                className="w-full border rounded-xl p-2.5 text-sm"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex justify-end gap-2 mt-6">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm border border-gray-200 hover:bg-gray-50 rounded-xl transition"
                    >
                        {t("common.cancel", "Abbrechen")}
                    </button>

                    <button
                        onClick={handleSave}
                        className="px-5 py-2 text-sm font-semibold bg-amber-500 hover:bg-amber-600 text-white rounded-xl shadow-xs transition"
                    >
                        {t("common.save", "Speichern")}
                    </button>
                </div>
            </div>
        </div>
    );
}

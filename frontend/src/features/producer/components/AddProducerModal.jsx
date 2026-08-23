/*
# src/features/producer/components/AddProducerModal.jsx
*/

import { useEffect, useState } from "react";
import { apiFetch } from "../../../api/client";
import { useQuery } from "@tanstack/react-query";
import { getGeneratorTypes } from "../api";
import { useTranslation } from "react-i18next";

function normalizeDecimal(value) {
    return value
        ?.toString()
        .replace(",", ".");
}

export default function AddProducerModal({
    open,
    onClose,
    onCreated,
    producer = null,
}) {
    const { t } = useTranslation();

    const { data: generatorTypes = [] } =
        useQuery({
            queryKey: ["generator-types"],
            queryFn: getGeneratorTypes,
        });

    const [generatorType, setGeneratorType] = useState("");
    const [name, setName] = useState("");
    const [peakPower, setPeakPower] = useState("");
    const [inverterPower, setInverterPower] = useState("");
    const [batteryCapacity, setBatteryCapacity] = useState("");

    const isEdit = !!producer;

    useEffect(() => {
        if (!producer) {
            return;
        }

        setName(producer.name ?? "");
        setPeakPower(producer.peak_power_kw ?? "");
        setInverterPower(producer.inverter_power_kw ?? "");
        setBatteryCapacity(producer.battery_capacity_kwh ?? "");
        setGeneratorType(producer.generator_type_id ?? "");
    }, [producer]);

    async function handleSave() {
        const payload = {
            name,
            generator_type: generatorType,
            peak_power_kw: normalizeDecimal(peakPower),
            inverter_power_kw: normalizeDecimal(inverterPower),
            battery_capacity_kwh: normalizeDecimal(batteryCapacity),
        };

        if (isEdit) {
            await apiFetch(`/api/producer/${producer.id}/`, {
                method: "PATCH",
                body: JSON.stringify(payload),
            });
        } else {
            await apiFetch("/api/producer/create/", {
                method: "POST",
                body: JSON.stringify(payload),
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
                        ? t("producers.modal_edit_title", "☀️ Erzeuger bearbeiten")
                        : t("producers.modal_add_title", "☀️ Erzeuger anlegen")}
                </h2>

                <div className="space-y-3">
                    <div>
                        <label className="text-xs font-semibold text-gray-500 mb-1 block">
                            {t("producers.producer_name_placeholder", "Name des Erzeugers")}
                        </label>
                        <input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder={t("producers.producer_name_placeholder", "Name des Erzeugers")}
                            className="w-full border rounded-xl p-2.5 text-sm"
                        />
                    </div>

                    <div>
                        <label className="text-xs font-semibold text-gray-500 mb-1 block">
                            {t("producers.producer_type_select", "Typ auswählen")}
                        </label>
                        <select
                            value={generatorType}
                            onChange={(e) => setGeneratorType(e.target.value)}
                            className="w-full border rounded-xl p-2.5 text-sm bg-white"
                        >
                            <option value="">
                                {t("producers.producer_type_select", "Typ auswählen")}
                            </option>
                            {generatorTypes.map((type) => (
                                <option key={type.id} value={type.id}>
                                    {t(`generator_types.${type.key}`, type.name)}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-3 gap-2">
                        <div>
                            <label className="text-[11px] font-semibold text-gray-500 mb-1 block truncate">
                                {t("producers.power", "Leistung")} (kWp)
                            </label>
                            <input
                                value={peakPower}
                                onChange={(e) => setPeakPower(e.target.value)}
                                placeholder="z. B. 9.8"
                                className="w-full border rounded-xl p-2.5 text-sm"
                            />
                        </div>

                        <div>
                            <label className="text-[11px] font-semibold text-gray-500 mb-1 block truncate">
                                {t("producers.inverter", "WR")} (kW)
                            </label>
                            <input
                                value={inverterPower}
                                onChange={(e) => setInverterPower(e.target.value)}
                                placeholder="z. B. 8.0"
                                className="w-full border rounded-xl p-2.5 text-sm"
                            />
                        </div>

                        <div>
                            <label className="text-[11px] font-semibold text-gray-500 mb-1 block truncate">
                                {t("producers.battery", "Speicher")} (kWh)
                            </label>
                            <input
                                value={batteryCapacity}
                                onChange={(e) => setBatteryCapacity(e.target.value)}
                                placeholder="z. B. 10.0"
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

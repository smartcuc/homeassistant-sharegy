/*
# src/features/producer/pages/ProducerPage.jsx
*/

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import AddProducerModal from "../components/AddProducerModal";
import AddStringModal from "../components/AddStringModal";


export default function ProducerPage() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const { data = [] } = useQuery({
        queryKey: ["producers"],
        queryFn: () => apiFetch("/api/producer/"),
    });

    const [openAdd, setOpenAdd] = useState(false);
    const [editProducer, setEditProducer] = useState(null);
    const [openEditProducer, setOpenEditProducer] = useState(false);

    const [selectedGenerator, setSelectedGenerator] = useState(null);
    const [openString, setOpenString] = useState(false);
    const [editString, setEditString] = useState(null);
    const [openEditString, setOpenEditString] = useState(false);

    return (
        <div className="p-6">

            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
                        {t("producers.title", "☀️ Erzeuger")}
                    </h1>

                    <p className="text-sm text-gray-500 mt-1">
                        {t("producers.subtitle", "Verwalte Photovoltaik, Brennstoffzellen, BHKW und weitere Erzeugersysteme.")}
                    </p>
                </div>

                <button
                    onClick={() => setOpenAdd(true)}
                    className="px-4 py-2 rounded-lg bg-amber-500 text-white font-medium shadow-sm hover:bg-amber-600 transition-colors"
                >
                    {t("producers.add_producer", "+ Erzeuger")}
                </button>
            </div>

            {data.length === 0 && (
                <div className="bg-white border rounded-xl p-6 text-center text-gray-500">
                    {t("producers.empty", "Noch keine Erzeugersysteme vorhanden.")}
                </div>
            )}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                {data.map((producer) => (
                    <div
                        key={producer.id}
                        className="bg-white rounded-xl border border-gray-200 shadow-sm p-4"
                    >
                        <div className="flex items-start justify-between">
                            <div>
                                <div className="text-lg font-semibold text-gray-900">
                                    {producer.name}
                                </div>
                                <div className="text-sm text-gray-500">
                                    {producer.type ? t(`generator_types.${producer.type}`, producer.type_label || producer.type) : "-"}
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => {
                                        setEditProducer(producer);
                                        setOpenEditProducer(true);
                                    }}
                                    className="px-2 py-1 text-xs rounded bg-slate-100 text-slate-700 hover:bg-slate-200"
                                    title={t("common.edit", "Bearbeiten")}
                                >
                                    ✏️
                                </button>

                                <button
                                    onClick={async () => {
                                        if (!window.confirm(t("producers.delete_confirm", { name: producer.name, defaultValue: `Erzeuger "${producer.name}" wirklich löschen?` }))) {
                                            return;
                                        }

                                        await apiFetch(`/api/producer/${producer.id}/delete/`, {
                                            method: "DELETE",
                                        });

                                        queryClient.invalidateQueries({
                                            queryKey: ["producers"],
                                        });
                                    }}
                                    className="px-2 py-1 text-xs rounded bg-zinc-100 text-zinc-700 hover:bg-zinc-200"
                                    title={t("common.delete", "Löschen")}
                                >
                                    🗑️
                                </button>

                                <button
                                    onClick={() => {
                                        setSelectedGenerator(producer.id);
                                        setOpenString(true);
                                    }}
                                    className="px-3 py-1 text-xs rounded-lg bg-amber-500 text-white hover:bg-amber-600 font-medium"
                                >
                                    {t("producers.add_string", "+ String")}
                                </button>
                            </div>
                        </div>

                        <div className="mt-4 grid grid-cols-2 gap-3">
                            <div>
                                <div className="text-xs text-gray-500">
                                    {t("producers.power", "Leistung")}
                                </div>
                                <div className="font-semibold text-gray-900">
                                    {producer.peak_power_kw} kWp
                                </div>
                            </div>

                            <div>
                                <div className="text-xs text-gray-500">
                                    {t("producers.strings", "Strings")}
                                </div>
                                <div className="font-semibold text-gray-900">
                                    {producer.string_count}
                                </div>
                            </div>

                            <div>
                                <div className="text-xs text-gray-500">
                                    {t("producers.inverter", "Wechselrichter")}
                                </div>
                                <div className="font-semibold text-gray-900">
                                    {producer.inverter_power_kw ?? "-"} kW
                                </div>
                            </div>

                            <div>
                                <div className="text-xs text-gray-500">
                                    {t("producers.battery", "Speicher")}
                                </div>
                                <div className="font-semibold text-gray-900">
                                    {producer.battery_capacity_kwh ?? "-"} kWh
                                </div>
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t">
                            <div className="text-sm text-gray-500">
                                {t("producers.total_string_power", "String-Gesamtleistung")}
                            </div>
                            <div className="font-semibold text-gray-900">
                                {producer.total_string_power_kwp} kWp
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t">
                            <div className="space-y-2">
                                <div className="text-sm font-medium text-gray-700">
                                    {t("producers.strings", "Strings")}
                                </div>

                                <div className="space-y-2">
                                    {producer.strings?.map((string) => (
                                        <div
                                            key={string.id}
                                            className="flex items-center justify-between border rounded-lg p-2.5 bg-slate-50"
                                        >
                                            <div>
                                                <div className="font-medium text-gray-900 text-sm">
                                                    {string.name}
                                                </div>
                                                <div className="text-xs text-gray-500">
                                                    {t(`orientations.${string.orientation_key || string.orientation}`, string.orientation)}
                                                    {" • "}
                                                    {string.tilt_deg}°
                                                    {" • "}
                                                    {string.module_count} {t("producers.modules", "Module")}
                                                    {" • "}
                                                    {t("producers.shading", "Verschattung")} {string.shading_percent}%
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                <div className="text-sm font-semibold text-amber-600">
                                                    {string.peak_power_kwp} kWp
                                                </div>

                                                <button
                                                    onClick={() => {
                                                        setEditString(string);
                                                        setOpenEditString(true);
                                                    }}
                                                    className="px-2 py-1 text-xs rounded bg-slate-100 text-slate-700 hover:bg-slate-200"
                                                    title={t("common.edit", "Bearbeiten")}
                                                >
                                                    ✏️
                                                </button>

                                                <button
                                                    onClick={async () => {
                                                        if (!window.confirm(t("producers.delete_string_confirm", { name: string.name, defaultValue: `String "${string.name}" wirklich löschen?` }))) {
                                                            return;
                                                        }

                                                        await apiFetch(`/api/producer/string/${string.id}/delete/`, {
                                                            method: "DELETE",
                                                        });

                                                        queryClient.invalidateQueries({
                                                            queryKey: ["producers"],
                                                        });
                                                    }}
                                                    className="px-2 py-1 text-xs rounded bg-zinc-100 text-zinc-700 hover:bg-zinc-200"
                                                    title={t("common.delete", "Löschen")}
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <AddProducerModal
                open={openAdd}
                onClose={() => setOpenAdd(false)}
                onCreated={() => queryClient.invalidateQueries({ queryKey: ["producers"] })}
            />
            <AddProducerModal
                open={openEditProducer}
                producer={editProducer}
                onClose={() => {
                    setOpenEditProducer(false);
                    setEditProducer(null);
                }}
                onCreated={() => queryClient.invalidateQueries({ queryKey: ["producers"] })}
            />

            <AddStringModal
                open={openString}
                generatorId={selectedGenerator}
                onClose={() => setOpenString(false)}
                onCreated={() => queryClient.invalidateQueries({ queryKey: ["producers"] })}
            />

            <AddStringModal
                open={openEditString}
                string={editString}
                generatorId={selectedGenerator}
                onClose={() => {
                    setOpenEditString(false);
                    setEditString(null);
                }}
                onCreated={() => queryClient.invalidateQueries({ queryKey: ["producers"] })}
            />

        </div>
    );
}

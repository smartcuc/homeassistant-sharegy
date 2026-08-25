/*
# src/features/producer/pages/ProducerPage.jsx
*/

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import AddProducerModal from "../components/AddProducerModal";
import AddStringModal from "../components/AddStringModal";
import StorageSystemCard from "../components/StorageSystemCard";
import StorageSystemModal from "../components/StorageSystemModal";

export default function ProducerPage() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [activeTab, setActiveTab] = useState("generators"); // "generators" | "storage"

    // 1. Erzeugeranlagen
    const { data: producers = [] } = useQuery({
        queryKey: ["producers"],
        queryFn: () => apiFetch("/api/producer/"),
    });

    // 2. Speichersysteme
    const { data: storages = [] } = useQuery({
        queryKey: ["storages"],
        queryFn: () => apiFetch("/api/producer/storage/"),
    });

    // Modal States: Erzeuger & Strings
    const [openAdd, setOpenAdd] = useState(false);
    const [editProducer, setEditProducer] = useState(null);
    const [openEditProducer, setOpenEditProducer] = useState(false);

    const [selectedGenerator, setSelectedGenerator] = useState(null);
    const [openString, setOpenString] = useState(false);
    const [editString, setEditString] = useState(null);
    const [openEditString, setOpenEditString] = useState(false);

    // Modal States: Speichersysteme
    const [openStorageModal, setOpenStorageModal] = useState(false);
    const [editingStorage, setEditingStorage] = useState(null);

    const handleDeleteStorage = async (id, name) => {
        if (!window.confirm(t("storage.delete_confirm", { name, defaultValue: `Batteriespeicher "${name}" wirklich löschen?` }))) {
            return;
        }

        await apiFetch(`/api/producer/storage/${id}/delete/`, {
            method: "DELETE",
        });

        queryClient.invalidateQueries({ queryKey: ["storages"] });
        queryClient.invalidateQueries({ queryKey: ["battery-soc-forecast"] });
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <span>☀️</span> {t("producers.page_title", "Erzeuger- & Speicheranlagen")}
                    </h1>

                    <p className="text-xs text-gray-500 mt-1">
                        {t("producers.page_subtitle", "Verwalte Photovoltaik, Strings, Ausrichtungen und bündele Messpunkte für Batteriespeicher.")}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    {activeTab === "generators" ? (
                        <button
                            onClick={() => setOpenAdd(true)}
                            className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold shadow-xs transition cursor-pointer flex items-center gap-1.5"
                        >
                            <span>+</span> {t("producers.add_producer", "Erzeuger anlegen")}
                        </button>
                    ) : (
                        <button
                            onClick={() => {
                                setEditingStorage(null);
                                setOpenStorageModal(true);
                            }}
                            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-xs transition cursor-pointer flex items-center gap-1.5"
                        >
                            <span>+</span> {t("storage.add_btn", "Batteriespeicher anlegen")}
                        </button>
                    )}
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex items-center gap-2 border-b border-gray-200">
                <button
                    onClick={() => setActiveTab("generators")}
                    className={`pb-3 px-3 text-xs font-bold transition flex items-center gap-2 border-b-2 cursor-pointer ${activeTab === "generators"
                        ? "border-amber-500 text-amber-600"
                        : "border-transparent text-gray-500 hover:text-gray-900"
                        }`}
                >
                    <span>☀️</span>
                    <span>{t("producers.tab_pv", "Photovoltaik & Erzeuger")}</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] bg-amber-100 text-amber-800">
                        {producers.length}
                    </span>
                </button>

                <button
                    onClick={() => setActiveTab("storage")}
                    className={`pb-3 px-3 text-xs font-bold transition flex items-center gap-2 border-b-2 cursor-pointer ${activeTab === "storage"
                        ? "border-emerald-600 text-emerald-700"
                        : "border-transparent text-gray-500 hover:text-gray-900"
                        }`}
                >
                    <span>🔋</span>
                    <span>{t("storage.tab_storage", "Batteriespeicher & Messpunkte")}</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-800">
                        {storages.length}
                    </span>
                </button>
            </div>

            {/* =========================================================
                TAB 1: ERZEUGER & STRINGS (PV)
            ========================================================= */}
            {activeTab === "generators" && (
                <div className="space-y-4">
                    {producers.length === 0 && (
                        <div className="bg-white border border-gray-200 rounded-3xl p-12 text-center text-gray-500 space-y-3">
                            <div className="text-4xl">☀️</div>
                            <div className="font-bold text-gray-900">{t("producers.empty", "Noch keine Erzeugersysteme vorhanden.")}</div>
                            <p className="text-xs text-gray-400 max-w-sm mx-auto">
                                Lege deine PV-Anlage oder BHKW an, um Strings, Modulausrichtungen und Neigungen zu erfassen.
                            </p>
                        </div>
                    )}

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        {producers.map((producer) => (
                            <div
                                key={producer.id}
                                className="bg-white rounded-2xl border border-gray-200 shadow-xs p-5 space-y-4"
                            >
                                <div className="flex items-start justify-between">
                                    <div>
                                        <div className="text-base font-bold text-gray-900">
                                            {producer.name}
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            {producer.type ? t(`generator_types.${producer.type}`, producer.type_label || producer.type) : "-"}
                                        </div>
                                    </div>

                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => {
                                                setEditProducer(producer);
                                                setOpenEditProducer(true);
                                            }}
                                            className="px-2.5 py-1 text-xs rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-semibold transition cursor-pointer"
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

                                                queryClient.invalidateQueries({ queryKey: ["producers"] });
                                            }}
                                            className="px-2.5 py-1 text-xs rounded-xl bg-red-50 text-red-700 hover:bg-red-100 font-semibold transition cursor-pointer"
                                            title={t("common.delete", "Löschen")}
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-3 gap-3 text-xs bg-slate-50 p-3 rounded-xl border border-slate-100">
                                    <div>
                                        <div className="text-[10px] text-gray-400 uppercase font-semibold">Gesamtleistung</div>
                                        <div className="font-bold text-gray-900 font-mono">
                                            {producer.peak_power_kw ? `${producer.peak_power_kw} kWp` : "-"}
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-[10px] text-gray-400 uppercase font-semibold">Wechselrichter</div>
                                        <div className="font-bold text-gray-900 font-mono">
                                            {producer.inverter_power_kw ? `${producer.inverter_power_kw} kW` : "-"}
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-[10px] text-gray-400 uppercase font-semibold">Strings</div>
                                        <div className="font-bold text-gray-900 font-mono">
                                            {producer.string_count} Strings ({producer.total_string_power_kwp} kWp)
                                        </div>
                                    </div>
                                </div>

                                {/* Strings List */}
                                <div className="space-y-2 pt-2 border-t border-gray-100">
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs font-bold text-gray-700">PV-Strings & Ausrichtung</span>
                                        <button
                                            onClick={() => {
                                                setSelectedGenerator(producer.id);
                                                setOpenString(true);
                                            }}
                                            className="text-[11px] font-bold text-amber-600 hover:underline cursor-pointer"
                                        >
                                            + String hinzufügen
                                        </button>
                                    </div>

                                    <div className="space-y-1.5">
                                        {producer.strings.map((str) => (
                                            <div
                                                key={str.id}
                                                className="p-2.5 bg-gray-50 rounded-xl border border-gray-200/60 flex items-center justify-between text-xs"
                                            >
                                                <div>
                                                    <span className="font-bold text-gray-800">{str.name}</span>
                                                    <span className="text-gray-500 ml-2">
                                                        {str.peak_power_kwp} kWp · {str.orientation} · {str.tilt_deg}° Neigung
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-1">
                                                    <button
                                                        onClick={() => {
                                                            setSelectedGenerator(producer.id);
                                                            setEditString(str);
                                                            setOpenEditString(true);
                                                        }}
                                                        className="px-2 py-0.5 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 text-[10px]"
                                                    >
                                                        ✏️
                                                    </button>
                                                    <button
                                                        onClick={async () => {
                                                            if (!window.confirm(`String "${str.name}" wirklich löschen?`)) return;
                                                            await apiFetch(`/api/producer/string/${str.id}/delete/`, { method: "DELETE" });
                                                            queryClient.invalidateQueries({ queryKey: ["producers"] });
                                                        }}
                                                        className="px-2 py-0.5 bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100 text-[10px]"
                                                    >
                                                        🗑️
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* =========================================================
                TAB 2: BATTERIESPEICHER & MESSBÜNDELUNG
            ========================================================= */}
            {activeTab === "storage" && (
                <div className="space-y-4">
                    {storages.length === 0 && (
                        <div className="bg-white border border-gray-200 rounded-3xl p-12 text-center text-gray-500 space-y-3">
                            <div className="text-4xl">🔋</div>
                            <div className="font-bold text-gray-900">{t("storage.empty_title", "Keine Batteriespeicher angelegt")}</div>
                            <p className="text-xs text-gray-400 max-w-md mx-auto">
                                Lege deinen Hausspeicher an und ordne flexibel zu, welches Gerät den Ladestand (SoC %) und die Ladeleistung liefert (All-in-One Wechselrichter oder getrennte Sensoren).
                            </p>
                            <button
                                onClick={() => {
                                    setEditingStorage(null);
                                    setOpenStorageModal(true);
                                }}
                                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                            >
                                + Batteriespeicher hinzufügen
                            </button>
                        </div>
                    )}

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        {storages.map((storage) => (
                            <StorageSystemCard
                                key={storage.id}
                                storage={storage}
                                onEdit={(st) => {
                                    setEditingStorage(st);
                                    setOpenStorageModal(true);
                                }}
                                onDelete={handleDeleteStorage}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Modals */}
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

            {/* Storage Modal */}
            <StorageSystemModal
                isOpen={openStorageModal}
                storage={editingStorage}
                onClose={() => {
                    setOpenStorageModal(false);
                    setEditingStorage(null);
                }}
                onSaved={() => {
                    queryClient.invalidateQueries({ queryKey: ["storages"] });
                    queryClient.invalidateQueries({ queryKey: ["battery-soc-forecast"] });
                }}
            />
        </div>
    );
}
